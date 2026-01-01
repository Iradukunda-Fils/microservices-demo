"""
gRPC server for UserService.

Educational Note: This server runs alongside the Django HTTP server.
- HTTP/REST: For frontend communication (port 8000)
- gRPC: For inter-service communication (port 50051)

Why separate servers?
- REST is better for client-server (browsers, mobile apps)
- gRPC is better for service-to-service (faster, type-safe)
"""

import os
import sys
import logging
import grpc
from concurrent import futures
import time

# Add Django project to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')
import django
django.setup()

from django.contrib.auth.models import User
from grpc_generated import user_pb2, user_pb2_grpc

logger = logging.getLogger(__name__)

# Educational Note: Shared secret for service-to-service authentication
# In production, use mutual TLS or service mesh (Istio) instead
SERVICE_SECRET = os.getenv('SERVICE_SECRET', 'shared-secret-key-change-in-production')


class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    """
    Implementation of UserService gRPC API.
    
    Educational Note: This class implements the service defined in user.proto.
    The grpcio-tools compiler generates the base class (UserServiceServicer)
    and we implement the actual logic.
    """
    
    def ValidateUser(self, request, context):
        """
        Validate if a user exists and return basic info.
        
        Educational Note: This is called by OrderService before creating orders.
        Instead of OrderService accessing UserService's database directly,
        it makes a gRPC call to this method.
        
        Benefits:
        - Service isolation (no direct database access)
        - Encapsulation (UserService controls its data)
        - Type safety (Protocol Buffers)
        - Performance (binary protocol, 7-10x faster than REST)
        
        Args:
            request: ValidateUserRequest with user_id and requesting_service
            context: gRPC context (metadata, authentication, etc.)
        
        Returns:
            ValidateUserResponse with validation result and user info
        """
        
        # Educational Note: Extract metadata for authentication
        # In production, use mutual TLS or service mesh
        metadata = dict(context.invocation_metadata())
        auth_token = metadata.get('authorization', '')
        
        # Verify service authentication
        if auth_token != f'Bearer {SERVICE_SECRET}':
            logger.warning(f"Unauthorized gRPC call from {request.requesting_service}")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid service credentials')
            return user_pb2.ValidateUserResponse(
                valid=False,
                error_message='Unauthorized'
            )
        
        user_id = request.user_id
        requesting_service = request.requesting_service
        
        logger.info(f"gRPC ValidateUser called by {requesting_service} for user_id={user_id}")
        
        try:
            # Query user from database
            user = User.objects.get(id=user_id, is_active=True)
            
            # Educational Note: We only return necessary fields
            # This minimizes data transfer and protects sensitive information
            user_info = user_pb2.UserInfo(
                id=user.id,
                username=user.username,
                email=user.email,  # In production, consider encrypting
                is_active=user.is_active
            )
            
            logger.info(f"User {user_id} validated successfully for {requesting_service}")
            
            return user_pb2.ValidateUserResponse(
                valid=True,
                user_info=user_info
            )
            
        except User.DoesNotExist:
            logger.warning(f"User {user_id} not found (requested by {requesting_service})")
            
            return user_pb2.ValidateUserResponse(
                valid=False,
                error_message=f'User with id {user_id} not found or inactive'
            )
            
        except Exception as e:
            logger.error(f"Error validating user {user_id}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            
            return user_pb2.ValidateUserResponse(
                valid=False,
                error_message='Internal server error'
            )


def serve():
    """
    Start the gRPC server.
    
    Educational Note: This server runs in a separate process from Django.
    In production, you might use:
    - Supervisor to manage both processes
    - Docker Compose to run separate containers
    - Kubernetes to orchestrate services
    """
    
    port = os.getenv('GRPC_PORT', '50051')
    
    # Educational Note: ThreadPoolExecutor handles concurrent requests
    # max_workers=10 means up to 10 concurrent gRPC calls
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register our service implementation
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserServiceServicer(), server
    )
    
    # Bind to port
    server.add_insecure_port(f'[::]:{port}')
    
    # Start server
    server.start()
    
    logger.info(f"✓ gRPC server started on port {port}")
    logger.info(f"  Service: UserService")
    logger.info(f"  Methods: ValidateUser")
    logger.info(f"  Protocol: gRPC (HTTP/2 + Protocol Buffers)")
    logger.info(f"")
    logger.info(f"Educational Note:")
    logger.info(f"  - This server handles inter-service communication")
    logger.info(f"  - 7-10x faster than REST (binary vs JSON)")
    logger.info(f"  - Type-safe (Protocol Buffers)")
    logger.info(f"  - Used by OrderService to validate users")
    
    try:
        # Keep server running
        while True:
            time.sleep(86400)  # Sleep for a day
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
