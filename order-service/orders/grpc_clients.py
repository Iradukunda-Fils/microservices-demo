"""
gRPC client utilities with resilience patterns.

Educational Note: This module demonstrates professional microservices patterns:
1. Retry logic with exponential backoff (tenacity)
2. Circuit breaker pattern (pybreaker)
3. Comprehensive error handling and logging
4. Type-safe gRPC communication

Why these patterns matter:
- Retry: Handles transient failures (network blips, temporary overload)
- Circuit Breaker: Prevents cascade failures (stops calling failing services)
- Logging: Essential for debugging distributed systems
"""

import grpc
import logging
import sys
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from pybreaker import CircuitBreaker, CircuitBreakerError
from django.conf import settings

# Import generated gRPC code
# Educational Note: We use absolute imports to avoid relative import issues
try:
    from orders.grpc_generated import user_pb2, user_pb2_grpc
    from orders.grpc_generated import product_pb2, product_pb2_grpc
    
    # Verify imports succeeded
    if user_pb2 is None or user_pb2_grpc is None:
        raise ImportError("gRPC modules imported but are None")
    if product_pb2 is None or product_pb2_grpc is None:
        raise ImportError("gRPC modules imported but are None")
        
except ImportError as e:
    print(f"CRITICAL ERROR: Failed to import gRPC modules: {e}", file=sys.stderr)
    print("This will cause order creation to fail!", file=sys.stderr)
    print("Solution: Run 'docker compose exec order-service python manage.py shell' and check imports", file=sys.stderr)
    # Re-raise to make the error visible
    raise ImportError(
        f"Failed to import gRPC modules. "
        f"Make sure generate_grpc.sh has been run and generated files exist. "
        f"Original error: {e}"
    )

logger = logging.getLogger(__name__)


# Educational Note: Circuit Breaker Pattern
# A circuit breaker prevents calling a failing service repeatedly.
# It has three states:
# 1. CLOSED: Normal operation, requests pass through
# 2. OPEN: Service is failing, requests fail immediately (no call made)
# 3. HALF_OPEN: Testing if service recovered, limited requests allowed
#
# Benefits:
# - Prevents cascade failures (one failing service doesn't bring down others)
# - Gives failing service time to recover
# - Fails fast instead of waiting for timeouts
# - Used by: Netflix (Hystrix), AWS, Google Cloud

user_service_breaker = CircuitBreaker(
    fail_max=settings.CIRCUIT_BREAKER_FAIL_MAX,
    reset_timeout=settings.CIRCUIT_BREAKER_TIMEOUT,
    name='UserService'
)

product_service_breaker = CircuitBreaker(
    fail_max=settings.CIRCUIT_BREAKER_FAIL_MAX,
    reset_timeout=settings.CIRCUIT_BREAKER_TIMEOUT,
    name='ProductService'
)


class GRPCClientError(Exception):
    """Base exception for gRPC client errors."""
    pass


class UserServiceClient:
    """
    Client for UserService gRPC API with resilience patterns.
    
    Educational Note: This client demonstrates:
    - Retry logic with exponential backoff
    - Circuit breaker for fault tolerance
    - Proper gRPC channel management
    - Comprehensive error handling
    """
    
    def __init__(self):
        self.url = settings.USER_SERVICE_GRPC_URL
        self.channel = None
        self.stub = None
    
    def _get_stub(self):
        """Get or create gRPC stub."""
        if self.stub is None:
            # Educational Note: gRPC channels are expensive to create
            # We reuse the same channel for multiple requests
            self.channel = grpc.insecure_channel(self.url)
            self.stub = user_pb2_grpc.UserServiceStub(self.channel)
        return self.stub
    
    def _get_metadata(self):
        """
        Get gRPC metadata with service authentication.
        
        Educational Note: gRPC metadata is similar to HTTP headers.
        We use it to pass the SERVICE_SECRET for service-to-service authentication.
        
        In production, use mutual TLS or service mesh (Istio) instead.
        """
        service_secret = settings.SERVICE_SECRET
        return [
            ('authorization', f'Bearer {service_secret}'),
        ]
    
    @retry(
        # Educational Note: Retry Configuration
        # stop_after_attempt: Maximum number of retry attempts
        # wait_exponential: Wait time doubles after each failure (1s, 2s, 4s, 8s...)
        # retry_if_exception_type: Only retry on gRPC errors (not business logic errors)
        # before_sleep_log: Log before each retry attempt
        #
        # Why exponential backoff?
        # - Gives service time to recover
        # - Prevents overwhelming a struggling service
        # - Standard pattern used by AWS, Google Cloud, Azure
        stop=stop_after_attempt(settings.RETRY_ATTEMPTS),
        wait=wait_exponential(
            min=settings.RETRY_MIN_WAIT,
            max=settings.RETRY_MAX_WAIT
        ),
        retry=retry_if_exception_type(grpc.RpcError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    @user_service_breaker
    def validate_user(self, user_id: int) -> dict:
        """
        Validate if a user exists and is active.
        
        Args:
            user_id: User ID to validate
            
        Returns:
            dict with keys: valid, user_info, error_message
            
        Raises:
            GRPCClientError: If gRPC call fails after retries
            CircuitBreakerError: If circuit breaker is open
            
        Educational Note: This method is decorated with:
        1. @retry: Automatically retries on transient failures
        2. @user_service_breaker: Circuit breaker prevents repeated calls to failing service
        
        The decorators work together:
        - First, retry handles transient failures (network blips)
        - If retries fail repeatedly, circuit breaker opens
        - When circuit is open, calls fail immediately (no retry)
        """
        try:
            stub = self._get_stub()
            
            # Create request
            request = user_pb2.ValidateUserRequest(
                user_id=user_id,
                requesting_service='order-service'
            )
            
            # Make gRPC call with authentication metadata
            logger.info(f"🔍 Validating user {user_id} via gRPC")
            response = stub.ValidateUser(request, metadata=self._get_metadata())
            
            # Convert protobuf response to dict
            result = {
                'valid': response.valid,
                'error_message': response.error_message,
            }
            
            if response.valid:
                result['user_info'] = {
                    'id': response.user_info.id,
                    'username': response.user_info.username,
                    'email': response.user_info.email,
                    'is_active': response.user_info.is_active,
                }
                logger.info(f"✅ User {user_id} validated successfully")
            else:
                logger.warning(f"❌ User {user_id} validation failed: {response.error_message}")
            
            return result
            
        except grpc.RpcError as e:
            logger.error(f"❌ gRPC error validating user {user_id}: {e.code()} - {e.details()}")
            raise GRPCClientError(f"Failed to validate user: {e.details()}")
        except CircuitBreakerError:
            logger.error(f"⚡ Circuit breaker OPEN for UserService - failing fast")
            raise
    
    def close(self):
        """Close gRPC channel."""
        if self.channel:
            self.channel.close()


class ProductServiceClient:
    """
    Client for ProductService gRPC API with resilience patterns.
    """
    
    def __init__(self):
        self.url = settings.PRODUCT_SERVICE_GRPC_URL
        self.channel = None
        self.stub = None
    
    def _get_stub(self):
        """Get or create gRPC stub."""
        if self.stub is None:
            self.channel = grpc.insecure_channel(self.url)
            self.stub = product_pb2_grpc.ProductServiceStub(self.channel)
        return self.stub
    
    def _get_metadata(self):
        """
        Get gRPC metadata with service authentication.
        
        Educational Note: gRPC metadata is similar to HTTP headers.
        We use it to pass the SERVICE_SECRET for service-to-service authentication.
        """
        service_secret = settings.SERVICE_SECRET
        return [
            ('authorization', f'Bearer {service_secret}'),
        ]
    
    @retry(
        stop=stop_after_attempt(settings.RETRY_ATTEMPTS),
        wait=wait_exponential(
            min=settings.RETRY_MIN_WAIT,
            max=settings.RETRY_MAX_WAIT
        ),
        retry=retry_if_exception_type(grpc.RpcError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    @product_service_breaker
    def get_product_info(self, product_id: int) -> dict:
        """
        Get product information including price and availability.
        
        Args:
            product_id: Product ID to query
            
        Returns:
            dict with keys: exists, product_info, error_message
            
        Raises:
            GRPCClientError: If gRPC call fails after retries
            CircuitBreakerError: If circuit breaker is open
        """
        try:
            stub = self._get_stub()
            
            request = product_pb2.ProductInfoRequest(
                product_id=product_id,
                requesting_service='order-service'
            )
            
            logger.info(f"🔍 Getting product info for {product_id} via gRPC")
            response = stub.GetProductInfo(request, metadata=self._get_metadata())
            
            result = {
                'exists': response.exists,
                'error_message': response.error_message,
            }
            
            if response.exists:
                result['product_info'] = {
                    'id': response.product_info.id,
                    'name': response.product_info.name,
                    'description': response.product_info.description,
                    'price': response.product_info.price,
                    'inventory_count': response.product_info.inventory_count,
                    'is_available': response.product_info.is_available,
                }
                logger.info(f"✅ Product {product_id} info retrieved successfully")
            else:
                logger.warning(f"❌ Product {product_id} not found: {response.error_message}")
            
            return result
            
        except grpc.RpcError as e:
            logger.error(f"❌ gRPC error getting product {product_id}: {e.code()} - {e.details()}")
            raise GRPCClientError(f"Failed to get product info: {e.details()}")
        except CircuitBreakerError:
            logger.error(f"⚡ Circuit breaker OPEN for ProductService - failing fast")
            raise
    
    @retry(
        stop=stop_after_attempt(settings.RETRY_ATTEMPTS),
        wait=wait_exponential(
            min=settings.RETRY_MIN_WAIT,
            max=settings.RETRY_MAX_WAIT
        ),
        retry=retry_if_exception_type(grpc.RpcError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    @product_service_breaker
    def check_availability(self, product_id: int, quantity: int) -> dict:
        """
        Check if sufficient inventory exists for a quantity.
        
        Args:
            product_id: Product ID to check
            quantity: Requested quantity
            
        Returns:
            dict with keys: available, available_quantity, error_message
            
        Raises:
            GRPCClientError: If gRPC call fails after retries
            CircuitBreakerError: If circuit breaker is open
        """
        try:
            stub = self._get_stub()
            
            request = product_pb2.AvailabilityRequest(
                product_id=product_id,
                quantity=quantity,
                requesting_service='order-service'
            )
            
            logger.info(f"🔍 Checking availability for product {product_id} (qty: {quantity}) via gRPC")
            response = stub.CheckAvailability(request, metadata=self._get_metadata())
            
            result = {
                'available': response.available,
                'available_quantity': response.available_quantity,
                'error_message': response.error_message,
            }
            
            if response.available:
                logger.info(f"✅ Product {product_id} available (qty: {quantity})")
            else:
                logger.warning(f"❌ Product {product_id} not available: {response.error_message}")
            
            return result
            
        except grpc.RpcError as e:
            logger.error(f"❌ gRPC error checking availability for {product_id}: {e.code()} - {e.details()}")
            raise GRPCClientError(f"Failed to check availability: {e.details()}")
        except CircuitBreakerError:
            logger.error(f"⚡ Circuit breaker OPEN for ProductService - failing fast")
            raise
    
    def close(self):
        """Close gRPC channel."""
        if self.channel:
            self.channel.close()


# Singleton instances
# Educational Note: We create singleton instances to reuse gRPC channels
# Creating new channels for each request is expensive and inefficient
_user_service_client = None
_product_service_client = None


def get_user_service_client() -> UserServiceClient:
    """Get singleton UserServiceClient instance."""
    global _user_service_client
    if _user_service_client is None:
        _user_service_client = UserServiceClient()
    return _user_service_client


def get_product_service_client() -> ProductServiceClient:
    """Get singleton ProductServiceClient instance."""
    global _product_service_client
    if _product_service_client is None:
        _product_service_client = ProductServiceClient()
    return _product_service_client
