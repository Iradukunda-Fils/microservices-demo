"""
Order views with cross-service validation and resilience patterns.

Educational Note: This demonstrates the orchestration pattern in microservices.
OrderService coordinates UserService and ProductService to create orders.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from decimal import Decimal
import logging

from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderListSerializer,
)
from .grpc_clients import (
    get_user_service_client,
    get_product_service_client,
    GRPCClientError,
)
from pybreaker import CircuitBreakerError

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order management with cross-service validation.
    
    Educational Note: This ViewSet demonstrates:
    1. Cross-service validation via gRPC
    2. Resilience patterns (retry, circuit breaker)
    3. Transaction management for data consistency
    4. Comprehensive error handling
    5. RESTful API design with JWT authentication
    
    Security: All endpoints use request.user.id from JWT token.
    Users can only access their own orders.
    
    Endpoints:
    - POST /api/orders/ - Create order for authenticated user
    - GET /api/orders/ - List authenticated user's orders
    - GET /api/orders/{id}/ - Get order detail (if owned by user)
    """
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return orders for the authenticated user only.
        
        Educational Note: This ensures users can only see their own orders.
        The queryset is automatically filtered by user_id from JWT token.
        """
        if not self.request.user or not self.request.user.is_authenticated:
            return Order.objects.none()
        
        # Filter by authenticated user's ID
        user_id = str(self.request.user.id)
        return Order.objects.filter(user_id=user_id)
    
    def get_serializer_class(self):
        """
        Return different serializers for different actions.
        
        Educational Note: Performance optimization pattern.
        - List view: Lightweight serializer (no nested items)
        - Detail view: Full serializer (with nested items)
        - Create view: Custom validation serializer
        """
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new order with cross-service validation.
        
        Educational Note: This method demonstrates the orchestration pattern:
        1. Get user_id from authenticated JWT token (request.user)
        2. Validate input data (items)
        3. Validate user exists (UserService via gRPC)
        4. Validate products exist (ProductService via gRPC)
        5. Check inventory availability (ProductService via gRPC)
        6. Calculate total amount
        7. Create order and order items in a transaction
        
        Security: user_id comes from JWT token, not client input.
        This prevents users from creating orders for other users.
        
        Resilience patterns:
        - Retry logic handles transient failures
        - Circuit breaker prevents cascade failures
        - Comprehensive error handling
        """
        # Step 1: Get user_id from JWT token
        if not request.user or not request.user.is_authenticated:
            logger.error(f"❌ Unauthenticated request")
            return Response(
                {
                    'error': 'Authentication required',
                    'detail': 'You must be logged in to create an order'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Extract user_id from JWT token payload
        user_id = request.user.id
        
        logger.info(f"📥 Received order creation request from user {user_id}")
        logger.info(f"📥 Request data: {request.data}")
        
        # Step 2: Validate input data
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"❌ Validation failed: {serializer.errors}")
            return Response(
                {
                    'error': 'Validation failed',
                    'detail': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items_data = serializer.validated_data['items']
        
        logger.info(f"📦 Creating order for user {user_id} with {len(items_data)} items")
        
        try:
            # Step 3: Validate user exists via gRPC
            # Educational Note: This is a synchronous gRPC call to UserService
            # The @retry decorator handles transient failures automatically
            # The @circuit_breaker decorator prevents repeated calls to failing service
            user_client = get_user_service_client()
            user_result = user_client.validate_user(user_id)
            
            if not user_result['valid']:
                logger.warning(f"❌ User validation failed: {user_result['error_message']}")
                return Response(
                    {
                        'error': 'User validation failed',
                        'detail': user_result['error_message']
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"✅ User {user_id} validated")
            
            # Step 4 & 5: Validate products and check availability
            product_client = get_product_service_client()
            validated_items = []
            total_amount = Decimal('0.00')
            
            for item_data in items_data:
                product_id = int(item_data['product_id'])
                quantity = int(item_data['quantity'])
                
                # Get product info
                product_result = product_client.get_product_info(product_id)
                
                if not product_result['exists']:
                    logger.warning(f"❌ Product {product_id} not found")
                    return Response(
                        {
                            'error': 'Product validation failed',
                            'detail': f"Product {product_id} not found"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                product_info = product_result['product_info']
                
                # Check availability
                availability_result = product_client.check_availability(product_id, quantity)
                
                if not availability_result['available']:
                    logger.warning(f"❌ Product {product_id} not available in requested quantity")
                    return Response(
                        {
                            'error': 'Insufficient inventory',
                            'detail': f"Product {product_id} only has {availability_result['available_quantity']} units available"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calculate item total
                price = Decimal(product_info['price'])
                item_total = price * quantity
                total_amount += item_total
                
                validated_items.append({
                    'product_id': str(product_id),
                    'quantity': quantity,
                    'price_at_purchase': price,
                })
                
                logger.info(f"✅ Product {product_id} validated (qty: {quantity}, price: {price})")
            
            # Step 6: Create order and order items in a transaction
            # Educational Note: Database transaction ensures atomicity
            # Either all records are created, or none are (no partial orders)
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    user_id=str(user_id),  # Will be encrypted automatically
                    total_amount=total_amount,
                    status='pending'
                )
                
                # Create order items
                for item_data in validated_items:
                    OrderItem.objects.create(
                        order=order,
                        **item_data
                    )
                
                logger.info(f"✅ Order {order.id} created successfully (total: ${total_amount})")
            
            # Return created order
            response_serializer = OrderSerializer(order)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except CircuitBreakerError as e:
            # Educational Note: Circuit breaker is open - service is failing
            # We fail fast instead of waiting for timeouts
            logger.error(f"⚡ Circuit breaker open: {e}")
            return Response(
                {
                    'error': 'Service temporarily unavailable',
                    'detail': 'One or more services are experiencing issues. Please try again later.'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        except GRPCClientError as e:
            # Educational Note: gRPC call failed after retries
            logger.error(f"❌ gRPC client error: {e}")
            return Response(
                {
                    'error': 'Service communication error',
                    'detail': str(e)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        except Exception as e:
            # Educational Note: Catch-all for unexpected errors
            logger.error(f"❌ Unexpected error creating order: {e}", exc_info=True)
            return Response(
                {
                    'error': 'Internal server error',
                    'detail': 'An unexpected error occurred while creating the order'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
