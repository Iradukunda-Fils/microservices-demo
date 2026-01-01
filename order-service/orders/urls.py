"""
URL configuration for orders app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

# Educational Note: DRF routers automatically generate URLs for ViewSets
# This creates:
# - GET /api/orders/ - List orders
# - POST /api/orders/ - Create order
# - GET /api/orders/{id}/ - Get order detail
# - PUT /api/orders/{id}/ - Update order
# - PATCH /api/orders/{id}/ - Partial update
# - DELETE /api/orders/{id}/ - Delete order
# - GET /api/orders/user/{user_id}/ - Custom action for user orders

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
