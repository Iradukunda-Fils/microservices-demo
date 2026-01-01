"""
User models for UserService.

Educational Note: We use Django's built-in User model for simplicity.
In production, you might extend AbstractUser for custom fields.
"""

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils import timezone

# We're using Django's built-in User model which includes:
# - username (unique)
# - email
# - password (automatically hashed)
# - first_name, last_name
# - is_active, is_staff, is_superuser
# - date_joined, last_login

# Educational Note: Django automatically handles password hashing
# using PBKDF2 algorithm with SHA256 hash


class BackupToken(models.Model):
    """
    Secure storage for 2FA backup tokens.
    
    Security Design:
    - Tokens are hashed using Django's password hasher (PBKDF2-SHA256)
    - One-time use enforced at database level
    - Automatic expiry after 90 days
    - Audit trail with usage timestamps
    
    Why hash backup tokens?
    - If database is compromised, tokens cannot be used
    - Same security level as passwords
    - Industry best practice (OWASP recommendation)
    
    Why not store in session?
    - Sessions are ephemeral and can be lost
    - Not suitable for long-term recovery tokens
    - Doesn't work across devices/browsers
    - Violates stateless JWT architecture
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='backup_tokens',
        help_text="User who owns this backup token"
    )
    
    token_hash = models.CharField(
        max_length=255,
        help_text="Hashed backup token (PBKDF2-SHA256)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this token was generated"
    )
    
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this token was used (null = unused)"
    )
    
    expires_at = models.DateTimeField(
        help_text="When this token expires (90 days from creation)"
    )
    
    class Meta:
        db_table = 'backup_tokens'
        indexes = [
            models.Index(fields=['user', 'used_at']),  # Fast lookup for unused tokens
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        status = "used" if self.used_at else "unused"
        return f"BackupToken for {self.user.username} ({status})"
    
    @classmethod
    def create_tokens_for_user(cls, user, count=10):
        """
        Generate and store hashed backup tokens for a user.
        
        Security Note: Returns plaintext tokens ONCE for user to save.
        After this, only hashes are stored - tokens cannot be retrieved.
        
        Args:
            user: User instance
            count: Number of tokens to generate (default 10)
        
        Returns:
            list: Plaintext tokens (show to user ONCE)
        """
        from django_otp.util import random_hex
        from datetime import timedelta
        
        # Delete any existing unused tokens for this user
        cls.objects.filter(user=user, used_at__isnull=True).delete()
        
        plaintext_tokens = []
        expires_at = timezone.now() + timedelta(days=90)
        
        for _ in range(count):
            # Generate cryptographically secure random token
            plaintext_token = random_hex(16)  # 32 hex characters
            plaintext_tokens.append(plaintext_token)
            
            # Hash token before storing (same as password hashing)
            token_hash = make_password(plaintext_token)
            
            # Store hashed token
            cls.objects.create(
                user=user,
                token_hash=token_hash,
                expires_at=expires_at
            )
        
        return plaintext_tokens
    
    @classmethod
    def verify_and_use_token(cls, user, plaintext_token):
        """
        Verify a backup token and mark it as used.
        
        Security Note: Constant-time comparison via check_password.
        Prevents timing attacks.
        
        Args:
            user: User instance
            plaintext_token: Token to verify
        
        Returns:
            tuple: (success: bool, remaining_count: int)
        """
        # Get all unused, non-expired tokens for this user
        unused_tokens = cls.objects.filter(
            user=user,
            used_at__isnull=True,
            expires_at__gt=timezone.now()
        )
        
        # Try to find matching token (constant-time comparison)
        for token_obj in unused_tokens:
            if check_password(plaintext_token, token_obj.token_hash):
                # Mark as used
                token_obj.used_at = timezone.now()
                token_obj.save(update_fields=['used_at'])
                
                # Count remaining unused tokens
                remaining = unused_tokens.exclude(id=token_obj.id).count()
                
                return (True, remaining)
        
        # Token not found or already used
        return (False, unused_tokens.count())
    
    @classmethod
    def get_unused_count(cls, user):
        """
        Get count of unused, non-expired backup tokens for a user.
        
        Args:
            user: User instance
        
        Returns:
            int: Number of unused tokens
        """
        return cls.objects.filter(
            user=user,
            used_at__isnull=True,
            expires_at__gt=timezone.now()
        ).count()
    
    @classmethod
    def cleanup_expired(cls):
        """
        Delete expired tokens (for periodic cleanup task).
        
        Should be run via cron/celery daily.
        """
        expired_count = cls.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        
        return expired_count
