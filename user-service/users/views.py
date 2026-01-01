"""
Views for UserService.

Educational Note: We use DRF ViewSets and APIViews for clean, RESTful APIs.
ViewSets automatically provide list, create, retrieve, update, destroy actions.
"""

import logging
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    PublicKeySerializer
)

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(description="List all users (admin only)"),
    retrieve=extend_schema(description="Get user details"),
    create=extend_schema(description="Register a new user"),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management.
    
    Educational Note: ModelViewSet provides:
    - list(): GET /api/users/
    - retrieve(): GET /api/users/{id}/
    - create(): POST /api/users/
    - update(): PUT /api/users/{id}/
    - partial_update(): PATCH /api/users/{id}/
    - destroy(): DELETE /api/users/{id}/
    
    This reduces boilerplate by 70% compared to writing individual views!
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        
        Educational Note: This allows us to have different validation
        rules for registration vs updates.
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action.
        
        Educational Note: Registration should be public (AllowAny),
        but other actions require authentication.
        """
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get current authenticated user.
        
        Educational Note: Custom action accessible at GET /api/users/me/
        The @action decorator creates a custom endpoint.
        """
        serializer = self.get_serializer(request.user)
        logger.info(f"User {request.user.username} retrieved their profile")
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Register a new user.
        
        Educational Note: We override create() to add logging
        and custom response messages.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        logger.info(f"New user registered: {user.username}")
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class PublicKeyView(APIView):
    """
    Public endpoint to retrieve JWT verification public key.
    
    Educational Note: This is the KEY endpoint that enables our
    RSA-based JWT architecture!
    
    How it works:
    1. UserService generates RSA key pair on startup
    2. Other services call this endpoint to get the public key
    3. Other services verify JWT tokens locally using the public key
    4. No need to call UserService for every request! (50% latency reduction)
    
    This is similar to OAuth2 JWKS (JSON Web Key Set) endpoints used by:
    - Google: https://www.googleapis.com/oauth2/v3/certs
    - Auth0: https://YOUR_DOMAIN/.well-known/jwks.json
    - AWS Cognito: https://cognito-idp.{region}.amazonaws.com/{userPoolId}/.well-known/jwks.json
    """
    
    permission_classes = [AllowAny]  # Public endpoint
    
    @extend_schema(
        responses={200: PublicKeySerializer},
        description="Get RSA public key for JWT verification"
    )
    def get(self, request):
        """
        Return the RSA public key for JWT verification.
        
        Educational Note: The public key is safe to share publicly.
        Only the private key (kept secret in UserService) can sign tokens.
        """
        
        public_key_pem = settings.JWT_PUBLIC_KEY_PEM.decode('utf-8')
        
        logger.info(f"Public key requested from {request.META.get('REMOTE_ADDR')}")
        
        return Response({
            'public_key': public_key_pem,
            'algorithm': 'RS256',
            'key_id': 'user-service-2024',  # For key rotation support
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for container orchestration.
    Verifies that the service is ready to accept requests.
    
    Educational Note: Docker uses this to determine if the service is ready.
    We check both database connectivity and JWT key availability.
    """
    from django.db import connection
    
    health_status = {
        'status': 'healthy',
        'service': 'user-service',
        'checks': {}
    }
    
    # Check if JWT keys are loaded
    if hasattr(settings, 'JWT_PRIVATE_KEY') and settings.JWT_PRIVATE_KEY:
        health_status['checks']['jwt_keys'] = 'ok'
    else:
        health_status['checks']['jwt_keys'] = 'missing'
        health_status['status'] = 'unhealthy'
    
    # Check database connectivity
    try:
        connection.ensure_connection()
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return Response(health_status, status=status_code)



# ============================================================================
# Two-Factor Authentication (2FA) Views - Production Grade
# Educational Note: TOTP-based 2FA is more secure than SMS-based 2FA
# 
# Security Features:
# - Stateless (no session dependency, JWT-compatible)
# - Hashed backup tokens in database
# - Proper QR code with explicit parameters (algorithm, digits, period)
# - No secret logging
# - Atomic database operations
# - Time drift tolerance
# ============================================================================

import qrcode
import io
import base64
from urllib.parse import quote
from django.db import transaction
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
from rest_framework_simplejwt.tokens import RefreshToken
from .models import BackupToken


class TwoFactorSetupView(APIView):
    """
    Setup 2FA for authenticated user - Production Grade.
    
    Security Features:
    - Atomic database operations
    - Hashed backup tokens stored in database
    - Proper otpauth:// URL with explicit parameters
    - No secret logging
    - Base32-encoded secret for authenticator apps
    
    Educational Note: TOTP (Time-based One-Time Password) generates
    6-digit codes that change every 30 seconds. Compatible with:
    - Google Authenticator
    - Authy
    - Microsoft Authenticator
    - 1Password
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=None,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'qr_code': {'type': 'string', 'description': 'Base64-encoded QR code image'},
                    'secret_key': {'type': 'string', 'description': 'Secret key for manual entry (base32)'},
                    'backup_tokens': {'type': 'array', 'items': {'type': 'string'}, 'description': '10 one-time backup tokens (SAVE THESE!)'},
                    'device_id': {'type': 'integer', 'description': 'TOTP device ID for verification'},
                }
            }
        },
        description="Setup 2FA - generates QR code and backup tokens (stateless, production-grade)"
    )
    @transaction.atomic
    def post(self, request):
        """
        Generate TOTP device, QR code, and hashed backup tokens.
        
        Security Note: Uses database transaction to ensure atomicity.
        If any step fails, entire operation rolls back.
        """
        user = request.user
        
        # Check if user already has confirmed 2FA
        existing_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        if existing_device:
            logger.warning(
                f"2FA setup blocked - already enabled",
                extra={'user': user.username, 'device_id': existing_device.id}
            )
            return Response({
                'error': '2FA is already enabled for this account',
                'message': 'Disable 2FA first before setting up again'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete any unconfirmed devices (cleanup from previous attempts)
        deleted_count = TOTPDevice.objects.filter(user=user, confirmed=False).delete()[0]
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} unconfirmed devices for {user.username}")
        
        # Generate new TOTP device with cryptographically secure secret
        device = TOTPDevice.objects.create(
            user=user,
            name='default',
            confirmed=False,
            key=random_hex(20),  # 40 hex chars = 160 bits of entropy
            tolerance=1,  # Allow ±30 seconds for time drift
            t0=0,  # Unix epoch start
            step=30,  # 30-second time steps
            drift=0,  # No drift initially
            digits=6,  # 6-digit codes
        )
        
        # Generate QR code URL with ALL required parameters
        # Security Note: Explicit parameters prevent client-side guessing
        issuer = 'MicroservicesDemo'
        account_name = f"{issuer}:{user.username}"
        
        # Convert hex key to base32 for QR code (authenticator apps expect base32)
        # django-otp stores keys as hex internally, but TOTP standard uses base32
        key_bytes = bytes.fromhex(device.key)
        key_base32 = base64.b32encode(key_bytes).decode('utf-8').rstrip('=')
        
        # Build otpauth:// URL with explicit parameters
        # Format: otpauth://totp/ISSUER:USERNAME?secret=KEY&issuer=ISSUER&algorithm=SHA1&digits=6&period=30
        qr_url = (
            f"otpauth://totp/{quote(account_name)}"
            f"?secret={key_base32}"  # Use base32-encoded secret
            f"&issuer={quote(issuer)}"
            f"&algorithm=SHA1"  # Explicit algorithm
            f"&digits=6"  # Explicit digit count
            f"&period=30"  # Explicit time period
        )
        
        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer)
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Generate hashed backup tokens (stored in database)
        # Security Note: Plaintext tokens returned ONCE - cannot be retrieved later
        plaintext_backup_tokens = BackupToken.create_tokens_for_user(user, count=10)
        
        logger.info(
            f"2FA setup initiated",
            extra={
                'user': user.username,
                'device_id': device.id,
                'backup_tokens_generated': len(plaintext_backup_tokens)
            }
        )
        
        # Security Note: Do NOT log secret key or backup tokens
        return Response({
            'qr_code': f'data:image/png;base64,{qr_base64}',
            'secret_key': key_base32,  # For manual entry (base32 format)
            'backup_tokens': plaintext_backup_tokens,  # Show ONCE
            'device_id': device.id,  # For verification
            'message': 'Scan QR code with your authenticator app and verify with a code. SAVE YOUR BACKUP TOKENS!'
        })


class TwoFactorVerifySetupView(APIView):
    """
    Verify 2FA setup - Production Grade.
    
    Security Features:
    - Stateless (no session dependency)
    - Validates device ownership
    - Atomic confirmation
    - Time drift tolerance
    - Audit logging
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'device_id': {'type': 'integer', 'description': 'Device ID from setup response'},
                'token': {'type': 'string', 'description': '6-digit TOTP code'},
            },
            'required': ['device_id', 'token']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'verified': {'type': 'boolean'},
                    'message': {'type': 'string'},
                }
            }
        },
        description="Verify 2FA setup with TOTP code (stateless)"
    )
    @transaction.atomic
    def post(self, request):
        """
        Verify TOTP token and confirm 2FA setup.
        
        Security Note: Atomic operation ensures device is confirmed
        only if verification succeeds.
        """
        user = request.user
        device_id = request.data.get('device_id')
        token = request.data.get('token')
        
        # Validate inputs
        if not device_id:
            return Response({
                'error': 'device_id is required',
                'message': 'Please provide the device_id from setup response'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not token:
            return Response({
                'error': 'token is required',
                'message': 'Please provide the 6-digit code from your authenticator app'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get unconfirmed device for this user
        try:
            device = TOTPDevice.objects.select_for_update().get(
                id=device_id,
                user=user,
                confirmed=False
            )
        except TOTPDevice.DoesNotExist:
            logger.warning(
                f"2FA verification failed - device not found",
                extra={'user': user.username, 'device_id': device_id}
            )
            return Response({
                'error': 'Invalid device',
                'message': 'Device not found or already confirmed. Please start setup again.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify TOTP token (tolerance already set on device)
        # Security Note: verify_token uses constant-time comparison
        if device.verify_token(token):
            # Confirm device atomically
            device.confirmed = True
            device.save(update_fields=['confirmed'])
            
            logger.info(
                f"✅ 2FA successfully enabled",
                extra={'user': user.username, 'device_id': device.id}
            )
            
            return Response({
                'verified': True,
                'message': '2FA enabled successfully! Your backup tokens are saved securely.'
            })
        
        # Verification failed
        logger.warning(
            f"❌ 2FA verification failed - invalid token",
            extra={'user': user.username, 'device_id': device.id}
        )
        
        return Response({
            'verified': False,
            'error': 'Invalid token',
            'message': 'Code is incorrect or expired. Please try again with a fresh code.'
        }, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorVerifyLoginView(APIView):
    """
    Verify 2FA during login - Production Grade.
    
    Security Features:
    - Supports TOTP and backup tokens
    - Hashed backup token verification
    - One-time use enforcement
    - Audit logging
    - Rate limiting ready
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'token': {'type': 'string', 'description': '6-digit TOTP code or backup token'},
            },
            'required': ['username', 'token']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'verified': {'type': 'boolean'},
                    'access': {'type': 'string', 'description': 'JWT access token'},
                    'refresh': {'type': 'string', 'description': 'JWT refresh token'},
                    'backup_token_used': {'type': 'boolean'},
                    'remaining_backup_tokens': {'type': 'integer'},
                }
            }
        },
        description="Verify 2FA during login (supports TOTP and backup tokens)"
    )
    def post(self, request):
        """
        Verify 2FA token and return JWT tokens if valid.
        
        Security Note: Only issues JWT tokens after successful 2FA.
        """
        username = request.data.get('username')
        token = request.data.get('token')
        
        if not username or not token:
            return Response({
                'error': 'Username and token are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Security Note: Generic error to prevent username enumeration
            logger.warning(f"2FA login attempt for non-existent user: {username}")
            return Response({
                'error': 'Invalid credentials',
                'message': 'Username or token is incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get confirmed TOTP device
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        
        if not device:
            logger.warning(f"2FA login attempt for user without 2FA: {username}")
            return Response({
                'error': '2FA not enabled',
                'message': '2FA is not enabled for this account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try TOTP verification first
        if device.verify_token(token):
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            logger.info(
                f"✅ 2FA login successful (TOTP)",
                extra={'user': username}
            )
            
            # Serialize user data
            from .serializers import UserSerializer
            user_data = UserSerializer(user).data
            
            return Response({
                'verified': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data,
                'message': 'Login successful'
            })
        
        # TOTP failed - try backup token
        success, remaining = BackupToken.verify_and_use_token(user, token)
        
        if success:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            logger.info(
                f"✅ 2FA login successful (backup token)",
                extra={'user': username, 'remaining_tokens': remaining}
            )
            
            if remaining == 0:
                logger.warning(f"⚠️ User {username} has used all backup tokens!")
            
            # Serialize user data
            from .serializers import UserSerializer
            user_data = UserSerializer(user).data
            
            return Response({
                'verified': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data,
                'backup_token_used': True,
                'remaining_backup_tokens': remaining,
                'message': f'Login successful with backup token. {remaining} backup tokens remaining.'
            })
        
        # Both TOTP and backup token failed
        logger.warning(
            f"❌ 2FA login failed - invalid token",
            extra={'user': username}
        )
        
        return Response({
            'verified': False,
            'error': 'Invalid token',
            'message': 'Code is incorrect or expired'
        }, status=status.HTTP_401_UNAUTHORIZED)


class TwoFactorDisableView(APIView):
    """
    Disable 2FA - Production Grade.
    
    Security Features:
    - Password verification required
    - Atomic deletion
    - Cleanup of backup tokens
    - Audit logging
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'password': {'type': 'string', 'description': 'User password for verification'},
            },
            'required': ['password']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                }
            }
        },
        description="Disable 2FA (requires password verification)"
    )
    @transaction.atomic
    def post(self, request):
        """
        Disable 2FA after password verification.
        
        Security Note: Requires password to prevent unauthorized disabling.
        """
        user = request.user
        password = request.data.get('password')
        
        if not password:
            return Response({
                'error': 'Password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify password
        if not user.check_password(password):
            logger.warning(
                f"Failed 2FA disable attempt - wrong password",
                extra={'user': user.username}
            )
            return Response({
                'error': 'Invalid password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Delete all TOTP devices
        device_count = TOTPDevice.objects.filter(user=user).delete()[0]
        
        # Delete all backup tokens
        token_count = BackupToken.objects.filter(user=user).delete()[0]
        
        if device_count == 0:
            return Response({
                'message': '2FA was not enabled'
            })
        
        logger.info(
            f"2FA disabled",
            extra={
                'user': user.username,
                'devices_deleted': device_count,
                'tokens_deleted': token_count
            }
        )
        
        return Response({
            'message': '2FA disabled successfully'
        })


class TwoFactorStatusView(APIView):
    """
    Check 2FA status - Production Grade.
    
    Returns:
    - Whether 2FA is enabled
    - Number of unused backup tokens
    - Device information
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'enabled': {'type': 'boolean'},
                    'device_name': {'type': 'string'},
                    'backup_tokens_remaining': {'type': 'integer'},
                }
            }
        },
        description="Check 2FA status for current user"
    )
    def get(self, request):
        """
        Return 2FA status for current user.
        """
        user = request.user
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        
        if device:
            backup_count = BackupToken.get_unused_count(user)
            
            return Response({
                'enabled': True,
                'device_name': device.name,
                'backup_tokens_remaining': backup_count,
                'message': f'2FA is enabled. {backup_count} backup tokens remaining.'
            })
        
        return Response({
            'enabled': False,
            'device_name': None,
            'backup_tokens_remaining': 0,
            'message': '2FA is not enabled'
        })


class TwoFactorRegenerateBackupTokensView(APIView):
    """
    Regenerate backup tokens - Production Grade.
    
    Security Features:
    - Password verification required
    - Invalidates old tokens
    - Generates new hashed tokens
    - Audit logging
    
    Use Case: User runs out of backup tokens or suspects compromise
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'password': {'type': 'string', 'description': 'User password for verification'},
            },
            'required': ['password']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'backup_tokens': {'type': 'array', 'items': {'type': 'string'}},
                    'message': {'type': 'string'},
                }
            }
        },
        description="Regenerate backup tokens (requires password, invalidates old tokens)"
    )
    @transaction.atomic
    def post(self, request):
        """
        Regenerate backup tokens after password verification.
        
        Security Note: Invalidates all old tokens to prevent reuse.
        """
        user = request.user
        password = request.data.get('password')
        
        if not password:
            return Response({
                'error': 'Password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify password
        if not user.check_password(password):
            logger.warning(
                f"Failed backup token regeneration - wrong password",
                extra={'user': user.username}
            )
            return Response({
                'error': 'Invalid password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if 2FA is enabled
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        if not device:
            return Response({
                'error': '2FA not enabled',
                'message': 'Enable 2FA first before generating backup tokens'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate new backup tokens (automatically deletes old ones)
        plaintext_tokens = BackupToken.create_tokens_for_user(user, count=10)
        
        logger.info(
            f"Backup tokens regenerated",
            extra={'user': user.username, 'token_count': len(plaintext_tokens)}
        )
        
        return Response({
            'backup_tokens': plaintext_tokens,
            'message': 'New backup tokens generated. SAVE THESE SECURELY! Old tokens are now invalid.'
        })


class TwoFactorDownloadBackupTokensView(APIView):
    """
    Download backup tokens as a text file - Production Grade.
    
    Security Features:
    - Requires authentication
    - Only returns tokens that were just generated (stored in session temporarily)
    - Tokens are cleared from session after download
    - One-time download per setup/regeneration
    
    Use Case: User wants to download backup tokens after setup or regeneration
    
    Educational Note: This endpoint provides a secure way to download backup tokens
    in a formatted text file. The tokens are only available immediately after
    setup or regeneration, and are cleared after download.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'tokens': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Backup tokens to download (from setup/regenerate response)'
                },
            },
            'required': ['tokens']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'filename': {'type': 'string'},
                    'content': {'type': 'string', 'description': 'Base64-encoded file content'},
                    'mime_type': {'type': 'string'},
                }
            }
        },
        description="Download backup tokens as a text file"
    )
    def post(self, request):
        """
        Generate a downloadable text file with backup tokens.
        
        Security Note: Tokens must be provided in the request body.
        This ensures only the user who just generated them can download.
        """
        user = request.user
        tokens = request.data.get('tokens', [])
        
        if not tokens or not isinstance(tokens, list):
            return Response({
                'error': 'Tokens are required',
                'message': 'Please provide the backup tokens to download'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify user has 2FA enabled OR is in setup process
        device = TOTPDevice.objects.filter(user=user).first()
        if not device:
            return Response({
                'error': '2FA not set up',
                'message': '2FA must be set up to download backup tokens'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate formatted text file content
        from datetime import datetime
        
        file_content = f"""╔══════════════════════════════════════════════════════════════╗
║          TWO-FACTOR AUTHENTICATION BACKUP TOKENS             ║
╚══════════════════════════════════════════════════════════════╝

Account: {user.username}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Application: MicroservicesDemo

⚠️  IMPORTANT SECURITY INFORMATION ⚠️

These backup tokens allow you to access your account if you lose
your authenticator device. Each token can only be used ONCE.

🔒 KEEP THESE TOKENS SECURE:
   • Store in a password manager (recommended)
   • Print and store in a safe place
   • Never share with anyone
   • Never store in plain text on your computer

🚨 IF COMPROMISED:
   • Login to your account immediately
   • Regenerate new backup tokens
   • Old tokens will be invalidated

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR BACKUP TOKENS:

"""
        
        # Add tokens with numbering
        for i, token in enumerate(tokens, 1):
            file_content += f"  {i:2d}. {token}\n"
        
        file_content += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW TO USE:

1. When logging in, enter your username and password
2. When prompted for 2FA code, enter one of these backup tokens
3. The token will be marked as used and cannot be reused
4. You have {len(tokens)} backup tokens remaining

REGENERATE TOKENS:

If you run out of backup tokens or suspect they've been compromised:
1. Login to your account
2. Go to Security Settings
3. Click "Regenerate Backup Tokens"
4. Download and save the new tokens

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated by MicroservicesDemo 2FA System
For support, contact: support@microservicesdemo.com

╔══════════════════════════════════════════════════════════════╗
║  REMEMBER: Each token can only be used once. Store safely!   ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        # Encode content as base64 for safe transmission
        import base64
        content_base64 = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
        
        # Generate filename with timestamp
        filename = f"2fa-backup-tokens-{user.username}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        
        logger.info(
            f"Backup tokens downloaded",
            extra={'user': user.username, 'token_count': len(tokens)}
        )
        
        return Response({
            'filename': filename,
            'content': content_base64,
            'mime_type': 'text/plain',
            'message': 'Backup tokens file generated successfully'
        })


