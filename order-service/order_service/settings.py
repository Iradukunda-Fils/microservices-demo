"""
Django settings for order_service project.

Educational Note: OrderService is the orchestrator that coordinates UserService
and ProductService to create orders. It demonstrates:
1. JWT verification using public key (no private key needed)
2. gRPC client calls to other services
3. Resilience patterns (retry, circuit breaker)
4. Field-level encryption for sensitive data
"""

from pathlib import Path
import os
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-order-service-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'order_service.urls'

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

WSGI_APPLICATION = 'order_service.wsgi.application'

# Database
# Educational Note: Each microservice has its own database (service isolation)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# Redis Cache Configuration
# Educational Note: Redis provides fast in-memory caching for:
# - API response caching
# - Rate limiting
# - Temporary data storage
# - Session management
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'order_service',
        'TIMEOUT': 300,  # Default timeout: 5 minutes
    }
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # For development only

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Educational Note: JWT Configuration for OrderService
# OrderService ONLY VERIFIES tokens (does not sign them)
# It uses the PUBLIC KEY from UserService to verify token signatures
# This is the RS256 (RSA) pattern used in OAuth2/OpenID Connect
#
# Why RS256 instead of HS256?
# 1. Security: Public key can be shared safely, private key stays in UserService
# 2. Performance: No need to call UserService for every request (50% latency reduction)
# 3. Scalability: Multiple services can verify tokens independently
# 4. Standard: Used by Auth0, Okta, AWS Cognito, Google Identity Platform

def load_jwt_public_key():
    """
    Load JWT public key with fallback strategies.
    
    Strategy:
    1. Try to read from shared volume (fastest)
    2. Fetch from UserService HTTP endpoint with retry (fallback)
    3. Return None if all attempts fail (degraded mode)
    """
    import time
    import requests
    
    public_key_path = os.getenv('JWT_PUBLIC_KEY_PATH', '/app/keys/jwt_public.pem')
    user_service_url = os.getenv('USER_SERVICE_URL', 'http://user-service:8000')
    
    # Strategy 1: Try to read from shared volume
    if os.path.exists(public_key_path):
        try:
            with open(public_key_path, 'r') as f:
                public_key = f.read()
            logging.info(f"✅ JWT public key loaded from shared volume: {public_key_path}")
            return public_key
        except Exception as e:
            logging.warning(f"⚠️  Failed to read public key from volume: {e}")
    
    # Strategy 2: Fetch from UserService HTTP endpoint with retry
    max_retries = 5
    retry_delay = 2  # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"🔄 Fetching public key from UserService (attempt {attempt}/{max_retries})...")
            response = requests.get(
                f'{user_service_url}/api/users/public-key/',
                timeout=5
            )
            response.raise_for_status()
            
            public_key = response.json()['public_key']
            
            # Save to local file for future use
            try:
                os.makedirs(os.path.dirname(public_key_path), exist_ok=True)
                with open(public_key_path, 'w') as f:
                    f.write(public_key)
                logging.info(f"✅ JWT public key fetched and saved to {public_key_path}")
            except Exception as e:
                logging.warning(f"⚠️  Could not save public key to file: {e}")
            
            return public_key
            
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                logging.info(f"   Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logging.error(f"❌ Failed to fetch public key after {max_retries} attempts")
    
    # Strategy 3: Return None and log warning
    logging.warning("⚠️  WARNING: Could not load JWT public key!")
    logging.warning("   Authentication will not work until key is available.")
    logging.warning("   Service will start in degraded mode.")
    return None

# Load public key on startup
JWT_PUBLIC_KEY = load_jwt_public_key()

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'RS256',  # RSA algorithm (asymmetric)
    'VERIFYING_KEY': JWT_PUBLIC_KEY,  # Public key for verification
    # Note: No SIGNING_KEY - OrderService doesn't sign tokens!
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Educational Note: Field-level encryption configuration
# django-encrypted-model-fields encrypts data at the application layer
# before storing in the database. This provides defense-in-depth:
# - Database compromise doesn't expose sensitive data
# - Encrypted data in backups
# - Compliance with data protection regulations (GDPR, HIPAA)
#
# Uses AES-256 encryption (symmetric) for field encryption
# Different from JWT (which uses RSA for signing, not encryption)
FIELD_ENCRYPTION_KEY = os.getenv(
    'FIELD_ENCRYPTION_KEY',
    'your-32-byte-encryption-key-change-in-production!!'  # Must be 32 bytes for AES-256
)

# gRPC service endpoints
# Educational Note: These are internal service URLs using Docker DNS
# Docker Compose creates a network where services can reach each other by name
USER_SERVICE_GRPC_URL = os.getenv('USER_SERVICE_GRPC_URL', 'user-service:50051')
PRODUCT_SERVICE_GRPC_URL = os.getenv('PRODUCT_SERVICE_GRPC_URL', 'product-service:50052')

# Service-to-service authentication
# Educational Note: Shared secret for gRPC service authentication
# In production, use mutual TLS or service mesh (Istio) instead
SERVICE_SECRET = os.getenv('SERVICE_SECRET', 'shared-secret-key-change-in-production')

# Resilience configuration
# Educational Note: These settings control retry and circuit breaker behavior
# Retry: Automatically retry failed requests (handles transient failures)
# Circuit Breaker: Stop calling failing services (prevents cascade failures)

# Tenacity retry configuration
RETRY_ATTEMPTS = 3  # Number of retry attempts
RETRY_MIN_WAIT = 1  # Minimum wait time between retries (seconds)
RETRY_MAX_WAIT = 10  # Maximum wait time between retries (seconds)

# PyBreaker circuit breaker configuration
CIRCUIT_BREAKER_FAIL_MAX = 5  # Open circuit after 5 failures
CIRCUIT_BREAKER_TIMEOUT = 30  # Try again after 30 seconds

# Logging configuration
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
        'orders': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Spectacular settings for API documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'OrderService API',
    'DESCRIPTION': 'Order management and orchestration service',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
