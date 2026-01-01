"""
Django settings for UserService.

Educational Note: This service is the JWT token issuer.
It generates RSA key pairs and signs tokens with the private key.
Other services verify tokens using the public key.
"""

import os
from pathlib import Path
from datetime import timedelta
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']  # In production, specify exact hosts

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'corsheaders',
    'django_otp',
    'django_otp.plugins.otp_totp',
    
    # Local apps
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS must be before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',  # For 2FA
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'user_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'user_service.wsgi.application'

# Database
# Educational Note: Each service has its own database (service isolation)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
# Educational Note: In production, specify exact origins
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# Redis Cache Configuration
# Educational Note: Redis provides fast in-memory caching for:
# - Session storage (faster than database)
# - API response caching
# - Rate limiting
# - Temporary data storage
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'user_service',
        'TIMEOUT': 300,  # Default timeout: 5 minutes
    }
}

# ============================================================================
# Session Configuration for 2FA
# Educational Note: Sessions are needed to store temporary 2FA setup data
# Using Redis for session storage provides better performance
# ============================================================================

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_NAME = 'user_sessionid'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False

# ============================================================================
# TOTP (Time-based One-Time Password) Configuration
# Educational Note: Critical settings for 2FA token verification
# ============================================================================

# OTP_TOTP_TOLERANCE: Number of 30-second windows to check before/after current time
# Educational Note: Why tolerance is needed:
# - Network latency (1-2 seconds)
# - User typing delay (2-5 seconds)
# - Clock drift between server and phone (up to 30 seconds)
# - Processing time
#
# Tolerance of 1 = checks 3 windows: [previous, current, next]
# This gives a 90-second acceptance window (30s * 3)
#
# Security vs Usability:
# - Tolerance 0: Most secure, but high failure rate (NOT RECOMMENDED)
# - Tolerance 1: Good balance (RECOMMENDED for production)
# - Tolerance 2: More forgiving, slightly less secure
#
# Industry standards:
# - Google Authenticator: Uses tolerance of 1
# - RFC 6238 (TOTP spec): Recommends tolerance of 1
# - Most enterprise systems: Use tolerance of 1-2
OTP_TOTP_TOLERANCE = 1  # Accept tokens from 1 window before/after current

# OTP_TOTP_SYNC: Enable time drift compensation
# If a user's token is consistently off by 1 window, the system learns this
OTP_TOTP_SYNC = True

# ============================================================================
# RSA Key Generation for JWT
# Educational Note: This is the core of our RSA-based JWT authentication
# ============================================================================

def get_or_create_rsa_keys():
    """
    Generate or load RSA 4096-bit key pair for JWT signing.
    
    Educational Note:
    - Private key: Used to SIGN JWT tokens (only UserService has this)
    - Public key: Used to VERIFY JWT tokens (shared with all services)
    - RS256 algorithm: RSA signature with SHA-256 hash
    
    Why RSA over HMAC (HS256)?
    - Better security: Private key never leaves UserService
    - Better performance: Services verify locally without calling UserService
    - Better scalability: No bottleneck on UserService for validation
    - Industry standard: OAuth2/OpenID Connect use RS256
    """
    private_key_path = os.getenv('JWT_PRIVATE_KEY_PATH', str(BASE_DIR / 'keys' / 'jwt_private.pem'))
    public_key_path = os.getenv('JWT_PUBLIC_KEY_PATH', str(BASE_DIR / 'keys' / 'jwt_public.pem'))
    
    # Create keys directory if it doesn't exist
    os.makedirs(os.path.dirname(private_key_path), exist_ok=True)
    
    if os.path.exists(private_key_path) and os.path.exists(public_key_path):
        # Load existing keys
        print("Loading existing RSA keys for JWT...")
        with open(private_key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        with open(public_key_path, 'rb') as f:
            public_key_pem = f.read()
    else:
        # Generate new RSA 4096-bit key pair
        print("Generating new RSA 4096-bit key pair for JWT...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,  # Professional-grade security (150+ years protection)
            backend=default_backend()
        )
        
        # Serialize and save private key
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # In production, use password
        )
        with open(private_key_path, 'wb') as f:
            f.write(private_key_pem)
        
        # Serialize and save public key
        public_key = private_key.public_key()
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(public_key_path, 'wb') as f:
            f.write(public_key_pem)
        
        print(f"RSA keys generated and saved:")
        print(f"  Private key: {private_key_path}")
        print(f"  Public key: {public_key_path}")
    
    return private_key, public_key_pem

# Generate or load RSA keys
JWT_PRIVATE_KEY, JWT_PUBLIC_KEY_PEM = get_or_create_rsa_keys()

# ============================================================================
# Django REST Framework Configuration
# ============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ============================================================================
# JWT Configuration with RS256 (RSA)
# Educational Note: This is where we configure simplejwt to use RSA keys
# ============================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # Reduced from 7 days for better security
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    # Educational Note: RS256 uses RSA keys (asymmetric)
    # - SIGNING_KEY: Private key for signing tokens (only UserService)
    # - VERIFYING_KEY: Public key for verifying tokens (all services)
    'ALGORITHM': 'RS256',
    'SIGNING_KEY': JWT_PRIVATE_KEY,  # Private key for signing
    'VERIFYING_KEY': JWT_PUBLIC_KEY_PEM,  # Public key for verification
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
}

# ============================================================================
# API Documentation (Swagger/OpenAPI)
# ============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'UserService API',
    'DESCRIPTION': 'User management, authentication, and 2FA service',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# ============================================================================
# Field Encryption Configuration
# Educational Note: For encrypting sensitive database fields
# ============================================================================

FIELD_ENCRYPTION_KEY = os.getenv('FIELD_ENCRYPTION_KEY', 'dev-encryption-key-change-in-production')

# ============================================================================
# Logging Configuration
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
