"""
URL configuration for users app.

Educational Note: We use DRF routers for automatic URL generation.
Routers create standard REST URLs for ViewSets.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Educational Note: DefaultRouter automatically creates URLs:
# - GET /api/users/ → list users
# - POST /api/users/ → create user
# - GET /api/users/{id}/ → retrieve user
# - PUT /api/users/{id}/ → update user
# - PATCH /api/users/{id}/ → partial update user
# - DELETE /api/users/{id}/ → delete user
# - GET /api/users/me/ → get current user (custom action)
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    # Two-Factor Authentication endpoints (must come BEFORE router to avoid conflicts)
    # Educational Note: Production-grade TOTP-based 2FA with hashed backup tokens
    # These are under /api/users/2fa/ to match frontend expectations
    path('users/2fa/setup/', views.TwoFactorSetupView.as_view(), name='2fa-setup'),
    path('users/2fa/verify-setup/', views.TwoFactorVerifySetupView.as_view(), name='2fa-verify-setup'),
    path('users/2fa/verify-login/', views.TwoFactorVerifyLoginView.as_view(), name='2fa-verify-login'),
    path('users/2fa/disable/', views.TwoFactorDisableView.as_view(), name='2fa-disable'),
    path('users/2fa/status/', views.TwoFactorStatusView.as_view(), name='2fa-status'),
    path('users/2fa/regenerate-backup-tokens/', views.TwoFactorRegenerateBackupTokensView.as_view(), name='2fa-regenerate-tokens'),
    path('users/2fa/download-backup-tokens/', views.TwoFactorDownloadBackupTokensView.as_view(), name='2fa-download-tokens'),
    
    # Public key endpoint for other services
    # Educational Note: This is the KEY endpoint for RSA JWT architecture!
    path('users/auth/public-key/', views.PublicKeyView.as_view(), name='public-key'),
    
    # Health check endpoint (at root level)
    path('health/', views.health_check, name='health'),
    
    # Router URLs (includes /users/ prefix) - MUST come last
    path('', include(router.urls)),
]
