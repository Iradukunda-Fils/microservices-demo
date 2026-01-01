"""
Serializers for UserService.

Educational Note: DRF serializers handle:
1. Validation of input data
2. Serialization (Python objects → JSON)
3. Deserialization (JSON → Python objects)
"""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Educational Note: ModelSerializer automatically creates fields
    based on the model definition, reducing boilerplate code.
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Educational Note: This serializer includes validation for:
    - Unique username and email
    - Password strength (Django's built-in validators)
    - Password confirmation matching
    """
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        """
        Validate that passwords match.
        
        Educational Note: This is a field-level validation method.
        It's called after individual field validators.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create and return a new user with hashed password.
        
        Educational Note: We use create_user() instead of create()
        to ensure the password is properly hashed.
        """
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        
        # Create user with hashed password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that includes user data in the response.
    
    Educational Note: The default TokenObtainPairSerializer only returns
    access and refresh tokens. We customize it to:
    1. Check if user has 2FA enabled
    2. If 2FA enabled, return requires_2fa flag instead of tokens
    3. If 2FA disabled, return tokens + user data as normal
    
    This implements a two-step login flow:
    - Step 1: POST /api/token/ with username/password
      - If 2FA disabled: Returns tokens immediately
      - If 2FA enabled: Returns requires_2fa=true
    - Step 2: POST /api/users/2fa/verify-login/ with username/token
      - Returns tokens after successful 2FA verification
    """
    
    def validate(self, attrs):
        # First, authenticate the user with username/password
        # This calls Django's authenticate() and validates credentials
        from django.contrib.auth import authenticate
        from django_otp.plugins.otp_totp.models import TOTPDevice
        
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Invalid credentials
            from rest_framework_simplejwt.exceptions import AuthenticationFailed
            raise AuthenticationFailed('No active account found with the given credentials')
        
        # Check if user has 2FA enabled
        has_2fa = TOTPDevice.objects.filter(user=user, confirmed=True).exists()
        
        if has_2fa:
            # User has 2FA enabled - don't issue tokens yet
            # Frontend should redirect to 2FA verification page
            return {
                'requires_2fa': True,
                'username': username,
                'message': 'Please enter your 2FA code to complete login'
            }
        
        # No 2FA - proceed with normal token generation
        data = super().validate(attrs)
        
        # Add user data to the response
        data['user'] = UserSerializer(self.user).data
        data['requires_2fa'] = False
        
        return data


class PublicKeySerializer(serializers.Serializer):
    """
    Serializer for public key distribution.
    
    Educational Note: This endpoint allows other services to fetch
    the public key for JWT verification without calling UserService
    for every request.
    """
    
    public_key = serializers.CharField(
        help_text="RSA public key in PEM format for JWT verification"
    )
    algorithm = serializers.CharField(
        help_text="JWT signing algorithm (RS256)"
    )
    key_id = serializers.CharField(
        help_text="Key identifier for key rotation support"
    )
