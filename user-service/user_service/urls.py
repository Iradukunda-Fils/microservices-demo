"""
URL configuration for UserService.

Educational Note: This service exposes:
1. REST API endpoints for user management
2. JWT token endpoints (obtain, refresh)
3. Public key endpoint for other services
4. Swagger/OpenAPI documentation
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users import views
from users.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that returns user data along with tokens.
    
    Educational Note: This allows the frontend to get user information
    during login without making an additional API call.
    """
    serializer_class = CustomTokenObtainPairSerializer


urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health check endpoint (at root for Docker healthcheck)
    path('health/', views.health_check, name='health'),
    
    # API endpoints (includes users app URLs)
    # This will make /api/users/, /api/users/2fa/, etc. available
    path('api/', include('users.urls')),
    
    # JWT token endpoints
    # Educational Note: These endpoints use RS256 (RSA) for signing tokens
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API documentation (Swagger UI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
