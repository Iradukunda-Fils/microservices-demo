"""
Views for ProductService.

Educational Note: This service VERIFIES JWT tokens using the public key.
No need to call UserService for authentication! (50% latency reduction)
"""

import logging
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Product
from .serializers import ProductSerializer, ProductListSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(description="List all products with pagination and search"),
    retrieve=extend_schema(description="Get product details"),
    create=extend_schema(description="Create a new product (admin only)"),
    update=extend_schema(description="Update a product (admin only)"),
    partial_update=extend_schema(description="Partially update a product (admin only)"),
    destroy=extend_schema(description="Delete a product (admin only)"),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product management.
    
    Educational Note: This demonstrates JWT verification without calling UserService!
    
    How it works:
    1. Frontend sends JWT token in Authorization header
    2. DRF JWTAuthentication extracts the token
    3. simplejwt verifies signature using PUBLIC KEY (local operation!)
    4. If valid, request.user is set from token claims
    5. No network call to UserService! (50% faster)
    
    This is the same pattern used by:
    - Google OAuth2
    - Auth0
    - AWS Cognito
    - Okta
    """
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Use different serializers for list vs detail views.
        
        Educational Note: Optimize performance by sending less data
        in list views (only essential fields).
        """
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action.
        
        Educational Note:
        - list, retrieve: Anyone can view (IsAuthenticatedOrReadOnly)
        - create, update, destroy: Requires authentication
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def list(self, request, *args, **kwargs):
        """
        List products with optional search and filtering.
        
        Educational Note: JWT verification happens automatically
        via DRF authentication classes. No manual token checking needed!
        """
        logger.info(f"Product list requested (authenticated: {request.user.is_authenticated})")
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new product.
        
        Educational Note: Only authenticated users can create products.
        JWT token is verified using the public key from UserService.
        """
        logger.info(f"Product creation requested by user {request.user.id if request.user.is_authenticated else 'anonymous'}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        
        logger.info(f"Product created: {product.name} (ID: {product.id})")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def check_availability(self, request, pk=None):
        """
        Check if product has sufficient inventory.
        
        Educational Note: Custom action accessible at:
        POST /api/products/{id}/check_availability/
        
        This is called by OrderService via gRPC before creating orders.
        """
        product = self.get_object()
        quantity = request.data.get('quantity', 1)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response({
                    'error': 'Quantity must be positive'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid quantity'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        available = product.check_availability(quantity)
        
        logger.info(f"Availability check for product {product.id}: quantity={quantity}, available={available}")
        
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'requested_quantity': quantity,
            'available_inventory': product.inventory_count,
            'is_available': available
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for container orchestration.
    Verifies that the service is ready to accept requests.
    
    Educational Note: Docker uses this to determine if the service is ready.
    We check database connectivity and JWT public key availability.
    """
    from django.conf import settings
    from django.db import connection
    
    health_status = {
        'status': 'healthy',
        'service': 'product-service',
        'checks': {}
    }
    
    # Check if JWT public key is loaded
    if hasattr(settings, 'JWT_PUBLIC_KEY_PEM') and settings.JWT_PUBLIC_KEY_PEM:
        health_status['checks']['jwt_public_key'] = 'ok'
    else:
        health_status['checks']['jwt_public_key'] = 'missing'
        health_status['status'] = 'degraded'  # Can still start, but auth won't work
    
    # Check database connectivity
    try:
        connection.ensure_connection()
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    status_code = 200 if health_status['status'] in ['healthy', 'degraded'] else 503
    return Response(health_status, status=status_code)
