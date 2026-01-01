"""
URL configuration for ProductService.

Educational Note: This service provides REST API for product management.
JWT tokens are verified locally using the public key from UserService.
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from products import views

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health check endpoint (at root for Docker healthcheck)
    path('health/', views.health_check, name='health'),
    
    # API endpoints
    path('api/', include('products.urls')),
    
    # API documentation (Swagger UI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
