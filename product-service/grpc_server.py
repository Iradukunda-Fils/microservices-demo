"""
gRPC server for ProductService.

Educational Note: This server handles inter-service communication.
OrderService calls these methods to validate products and check inventory.
"""

import os
import sys
import logging
import grpc
from concurrent import futures
import time
from decimal import Decimal

# Add Django project to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_service.settings')
import django
django.setup()

from products.models import Product
from grpc_generated import product_pb2, product_pb2_grpc

logger = logging.getLogger(__name__)

# Shared secret for service-to-service authentication
SERVICE_SECRET = os.getenv('SERVICE_SECRET', 'shared-secret-key-change-in-production')


class ProductServiceServicer(product_pb2_grpc.ProductServiceServicer):
    """
    Implementation of ProductService gRPC API.
    
    Educational Note: This provides product validation and inventory checks
    for OrderService without exposing the database directly.
    """
    
    def GetProductInfo(self, request, context):
        """
        Get product information including price and availability.
        
        Educational Note: OrderService calls this to get product details
        when creating orders. This ensures OrderService never accesses
        ProductService's database directly (service isolation).
        
        Args:
            request: ProductInfoRequest with product_id
            context: gRPC context
        
        Returns:
            ProductInfoResponse with product details
        """
        
        # Verify service authentication
        metadata = dict(context.invocation_metadata())
        auth_token = metadata.get('authorization', '')
        
        if auth_token != f'Bearer {SERVICE_SECRET}':
            logger.warning(f"Unauthorized gRPC call from {request.requesting_service}")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid service credentials')
            return product_pb2.ProductInfoResponse(
                exists=False,
                error_message='Unauthorized'
            )
        
        product_id = request.product_id
        requesting_service = request.requesting_service
        
        logger.info(f"gRPC GetProductInfo called by {requesting_service} for product_id={product_id}")
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Educational Note: Convert Decimal to string to avoid precision issues
            # Protocol Buffers don't have a native Decimal type
            product_info = product_pb2.ProductInfo(
                id=product.id,
                name=product.name,
                description=product.description,
                price=str(product.price),  # Decimal → string
                inventory_count=product.inventory_count,
                is_available=product.is_available
            )
            
            logger.info(f"Product {product_id} info returned to {requesting_service}")
            
            return product_pb2.ProductInfoResponse(
                exists=True,
                product_info=product_info
            )
            
        except Product.DoesNotExist:
            logger.warning(f"Product {product_id} not found (requested by {requesting_service})")
            
            return product_pb2.ProductInfoResponse(
                exists=False,
                error_message=f'Product with id {product_id} not found'
            )
            
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            
            return product_pb2.ProductInfoResponse(
                exists=False,
                error_message='Internal server error'
            )
    
    def CheckAvailability(self, request, context):
        """
        Check if sufficient inventory exists for a quantity.
        
        Educational Note: OrderService calls this before creating orders
        to ensure products are in stock. This prevents overselling.
        
        Args:
            request: AvailabilityRequest with product_id and quantity
            context: gRPC context
        
        Returns:
            AvailabilityResponse with availability status
        """
        
        # Verify service authentication
        metadata = dict(context.invocation_metadata())
        auth_token = metadata.get('authorization', '')
        
        if auth_token != f'Bearer {SERVICE_SECRET}':
            logger.warning(f"Unauthorized gRPC call from {request.requesting_service}")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid service credentials')
            return product_pb2.AvailabilityResponse(
                available=False,
                available_quantity=0,
                error_message='Unauthorized'
            )
        
        product_id = request.product_id
        quantity = request.quantity
        requesting_service = request.requesting_service
        
        logger.info(f"gRPC CheckAvailability called by {requesting_service} for product_id={product_id}, quantity={quantity}")
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Check if sufficient inventory exists
            available = product.check_availability(quantity)
            
            logger.info(f"Product {product_id} availability check: requested={quantity}, available={product.inventory_count}, result={available}")
            
            return product_pb2.AvailabilityResponse(
                available=available,
                available_quantity=product.inventory_count,
                error_message='' if available else f'Insufficient inventory. Available: {product.inventory_count}, Requested: {quantity}'
            )
            
        except Product.DoesNotExist:
            logger.warning(f"Product {product_id} not found (requested by {requesting_service})")
            
            return product_pb2.AvailabilityResponse(
                available=False,
                available_quantity=0,
                error_message=f'Product with id {product_id} not found'
            )
            
        except Exception as e:
            logger.error(f"Error checking availability for product {product_id}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            
            return product_pb2.AvailabilityResponse(
                available=False,
                available_quantity=0,
                error_message='Internal server error'
            )


def serve():
    """
    Start the gRPC server.
    
    Educational Note: This server runs alongside Django HTTP server.
    - HTTP: For frontend communication (port 8000)
    - gRPC: For inter-service communication (port 50052)
    """
    
    port = os.getenv('GRPC_PORT', '50052')
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register our service implementation
    product_pb2_grpc.add_ProductServiceServicer_to_server(
        ProductServiceServicer(), server
    )
    
    # Bind to port
    server.add_insecure_port(f'[::]:{port}')
    
    # Start server
    server.start()
    
    logger.info(f"✓ gRPC server started on port {port}")
    logger.info(f"  Service: ProductService")
    logger.info(f"  Methods: GetProductInfo, CheckAvailability")
    logger.info(f"  Protocol: gRPC (HTTP/2 + Protocol Buffers)")
    logger.info(f"")
    logger.info(f"Educational Note:")
    logger.info(f"  - This server handles inter-service communication")
    logger.info(f"  - OrderService calls these methods to validate products")
    logger.info(f"  - 7-10x faster than REST (binary vs JSON)")
    logger.info(f"  - Type-safe (Protocol Buffers)")
    
    try:
        # Keep server running
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        server.stop(0)


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    serve()
