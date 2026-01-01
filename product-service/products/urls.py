"""
URL configuration for products app.

Educational Note: DRF routers automatically generate RESTful URLs.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Educational Note: DefaultRouter creates standard REST URLs:
# - GET /api/products/ → list products
# - POST /api/products/ → create product
# - GET /api/products/{id}/ → retrieve product
# - PUT /api/products/{id}/ → update product
# - PATCH /api/products/{id}/ → partial update product
# - DELETE /api/products/{id}/ → delete product
# - POST /api/products/{id}/check_availability/ → check availability (custom action)
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
]

# Health check endpoint
urlpatterns += [
    path('health/', views.health_check, name='health'),
]
