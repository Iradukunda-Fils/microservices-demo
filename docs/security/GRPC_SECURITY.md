# gRPC Security Best Practices

## Overview

This document outlines security considerations and best practices for gRPC communication in microservices architecture.

## Current Implementation Status

### ⚠️ Development Configuration (INSECURE)

The current implementation uses **insecure gRPC channels** with a **shared secret** for authentication. This is acceptable for development but **NOT production-ready**.

```python
# Current (Development Only)
channel = grpc.insecure_channel(self.url)
metadata = [('authorization', f'Bearer {SERVICE_SECRET}')]
```

**Security Issues**:
- ❌ No encryption (plaintext communication)
- ❌ No certificate validation
- ❌ Shared secret can be intercepted
- ❌ No mutual authentication
- ❌ Vulnerable to man-in-the-middle attacks

## Production Security Recommendations

### 1. Mutual TLS (mTLS) - RECOMMENDED

Mutual TLS provides the strongest security for service-to-service communication.

#### Benefits
- ✅ **Encryption**: All traffic encrypted with TLS 1.3
- ✅ **Authentication**: Both client and server verify each other's identity
- ✅ **Authorization**: Certificate-based access control
- ✅ **Integrity**: Prevents tampering
- ✅ **Industry Standard**: Used by Google, Netflix, Uber

#### Implementation

**Step 1: Generate Certificates**

```bash
# Create Certificate Authority (CA)
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -days 365 -key ca-key.pem -out ca-cert.pem \
  -subj "/CN=MicroservicesCA"

# Generate server certificate (UserService)
openssl genrsa -out user-service-key.pem 4096
openssl req -new -key user-service-key.pem -out user-service.csr \
  -subj "/CN=user-service"
openssl x509 -req -days 365 -in user-service.csr \
  -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial \
  -out user-service-cert.pem

# Generate client certificate (OrderService)
openssl genrsa -out order-service-key.pem 4096
openssl req -new -key order-service-key.pem -out order-service.csr \
  -subj "/CN=order-service"
openssl x509 -req -days 365 -in order-service.csr \
  -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial \
  -out order-service-cert.pem
```

**Step 2: Server Configuration (UserService)**

```python
import grpc
from concurrent import futures

def serve():
    # Load server credentials
    with open('certs/user-service-key.pem', 'rb') as f:
        private_key = f.read()
    with open('certs/user-service-cert.pem', 'rb') as f:
        certificate_chain = f.read()
    with open('certs/ca-cert.pem', 'rb') as f:
        root_certificates = f.read()
    
    # Create server credentials with mutual TLS
    server_credentials = grpc.ssl_server_credentials(
        [(private_key, certificate_chain)],
        root_certificates=root_certificates,
        require_client_auth=True  # Require client certificate
    )
    
    # Create secure server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserServiceServicer(), server
    )
    
    # Use secure port
    server.add_secure_port('[::]:50051', server_credentials)
    server.start()
```

**Step 3: Client Configuration (OrderService)**

```python
import grpc

class UserServiceClient:
    def __init__(self):
        # Load client credentials
        with open('certs/order-service-key.pem', 'rb') as f:
            private_key = f.read()
        with open('certs/order-service-cert.pem', 'rb') as f:
            certificate_chain = f.read()
        with open('certs/ca-cert.pem', 'rb') as f:
            root_certificates = f.read()
        
        # Create client credentials
        credentials = grpc.ssl_channel_credentials(
            root_certificates=root_certificates,
            private_key=private_key,
            certificate_chain=certificate_chain
        )
        
        # Create secure channel
        self.channel = grpc.secure_channel(
            'user-service:50051',
            credentials,
            options=[
                ('grpc.ssl_target_name_override', 'user-service'),
            ]
        )
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)
```

**Step 4: Docker Configuration**

```yaml
# docker-compose.yml
services:
  user-service:
    volumes:
      - ./certs:/app/certs:ro  # Read-only certificates
    environment:
      - GRPC_SSL_ENABLED=true
      - GRPC_CERT_PATH=/app/certs/user-service-cert.pem
      - GRPC_KEY_PATH=/app/certs/user-service-key.pem
      - GRPC_CA_PATH=/app/certs/ca-cert.pem
  
  order-service:
    volumes:
      - ./certs:/app/certs:ro
    environment:
      - GRPC_SSL_ENABLED=true
      - GRPC_CERT_PATH=/app/certs/order-service-cert.pem
      - GRPC_KEY_PATH=/app/certs/order-service-key.pem
      - GRPC_CA_PATH=/app/certs/ca-cert.pem
```

#### Certificate Management

**Rotation Strategy**:
1. Generate new certificates before expiry
2. Deploy new certificates to all services
3. Restart services with new certificates
4. Revoke old certificates

**Storage**:
- ✅ Store in Kubernetes Secrets or HashiCorp Vault
- ✅ Use read-only file permissions (400)
- ❌ Never commit certificates to Git
- ❌ Never hardcode in source code

### 2. Service Mesh (Istio/Linkerd) - ENTERPRISE

Service meshes provide automatic mTLS and advanced traffic management.

#### Benefits
- ✅ **Automatic mTLS**: No code changes required
- ✅ **Certificate Rotation**: Automatic certificate management
- ✅ **Traffic Management**: Canary deployments, A/B testing
- ✅ **Observability**: Distributed tracing, metrics
- ✅ **Policy Enforcement**: Fine-grained access control

#### Istio Example

```yaml
# Enable mTLS for all services
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT  # Require mTLS for all traffic

---
# Authorization policy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: order-to-user
  namespace: default
spec:
  selector:
    matchLabels:
      app: user-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/order-service"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/user.UserService/ValidateUser"]
```

**When to Use**:
- Large-scale deployments (10+ services)
- Need for advanced traffic management
- Compliance requirements (SOC 2, PCI-DSS)
- Enterprise environments

### 3. JWT-Based Authentication (Alternative)

Use JWT tokens for service-to-service authentication.

#### Implementation

**Server Side (UserService)**:

```python
import jwt
from functools import wraps

def require_service_auth(f):
    """Decorator to require JWT authentication for gRPC methods."""
    @wraps(f)
    def wrapper(self, request, context):
        # Extract JWT from metadata
        metadata = dict(context.invocation_metadata())
        auth_header = metadata.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Missing or invalid authorization header')
            return None
        
        token = auth_header[7:]  # Remove 'Bearer '
        
        try:
            # Verify JWT with public key
            payload = jwt.decode(
                token,
                settings.JWT_PUBLIC_KEY,
                algorithms=['RS256'],
                audience='microservices',
                issuer='user-service'
            )
            
            # Check service identity
            if payload.get('service') != request.requesting_service:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details('Service identity mismatch')
                return None
            
            # Call original method
            return f(self, request, context)
            
        except jwt.ExpiredSignatureError:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Token expired')
            return None
        except jwt.InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(f'Invalid token: {str(e)}')
            return None
    
    return wrapper

class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    @require_service_auth
    def ValidateUser(self, request, context):
        # Method implementation
        pass
```

**Client Side (OrderService)**:

```python
import jwt
import time

class UserServiceClient:
    def _get_service_token(self):
        """Generate JWT for service authentication."""
        payload = {
            'service': 'order-service',
            'iat': int(time.time()),
            'exp': int(time.time()) + 300,  # 5 minutes
            'aud': 'microservices',
            'iss': 'user-service'
        }
        
        token = jwt.encode(
            payload,
            settings.SERVICE_PRIVATE_KEY,
            algorithm='RS256'
        )
        
        return token
    
    def _get_metadata(self):
        """Get gRPC metadata with JWT token."""
        token = self._get_service_token()
        return [('authorization', f'Bearer {token}')]
```

## Security Best Practices

### 1. Network Segmentation

Isolate gRPC traffic from public internet.

```yaml
# docker-compose.yml
networks:
  # Public network (API Gateway only)
  public:
    driver: bridge
  
  # Private network (services only)
  private:
    driver: bridge
    internal: true  # No external access

services:
  api-gateway:
    networks:
      - public
      - private
  
  user-service:
    networks:
      - private  # Not exposed to public
    expose:
      - "50051"  # Only within private network
```

### 2. Rate Limiting

Prevent abuse and DoS attacks.

```python
from collections import defaultdict
from time import time

class RateLimiter:
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id):
        now = time()
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        self.requests[client_id].append(now)
        return True

rate_limiter = RateLimiter(max_requests=100, window=60)

class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    def ValidateUser(self, request, context):
        # Get client identity
        metadata = dict(context.invocation_metadata())
        client_id = metadata.get('client-id', 'unknown')
        
        # Check rate limit
        if not rate_limiter.is_allowed(client_id):
            context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
            context.set_details('Rate limit exceeded')
            return user_pb2.ValidateUserResponse(
                valid=False,
                error_message='Rate limit exceeded'
            )
        
        # Process request
        # ...
```

### 3. Input Validation

Validate all inputs to prevent injection attacks.

```python
class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    def ValidateUser(self, request, context):
        # Validate user_id
        if request.user_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Invalid user_id: must be positive')
            return user_pb2.ValidateUserResponse(
                valid=False,
                error_message='Invalid user_id'
            )
        
        # Validate requesting_service
        allowed_services = ['order-service', 'notification-service']
        if request.requesting_service not in allowed_services:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details(f'Unknown service: {request.requesting_service}')
            return user_pb2.ValidateUserResponse(
                valid=False,
                error_message='Unauthorized service'
            )
        
        # Process request
        # ...
```

### 4. Logging and Monitoring

Log all gRPC calls for security auditing.

```python
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_grpc_call(f):
    """Decorator to log gRPC method calls."""
    @wraps(f)
    def wrapper(self, request, context):
        # Extract metadata
        metadata = dict(context.invocation_metadata())
        client_ip = metadata.get('x-forwarded-for', 'unknown')
        
        # Log request
        logger.info(
            f"gRPC call: {f.__name__}",
            extra={
                'method': f.__name__,
                'client_ip': client_ip,
                'requesting_service': request.requesting_service,
                'user_id': getattr(request, 'user_id', None),
                'product_id': getattr(request, 'product_id', None),
            }
        )
        
        # Call method
        try:
            response = f(self, request, context)
            
            # Log success
            logger.info(
                f"gRPC call successful: {f.__name__}",
                extra={'method': f.__name__}
            )
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(
                f"gRPC call failed: {f.__name__}",
                extra={
                    'method': f.__name__,
                    'error': str(e)
                },
                exc_info=True
            )
            raise
    
    return wrapper

class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    @log_grpc_call
    def ValidateUser(self, request, context):
        # Method implementation
        pass
```

### 5. Timeout Configuration

Set appropriate timeouts to prevent resource exhaustion.

```python
# Server-side timeout
server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10),
    options=[
        ('grpc.max_receive_message_length', 4 * 1024 * 1024),  # 4MB
        ('grpc.max_send_message_length', 4 * 1024 * 1024),
        ('grpc.keepalive_time_ms', 10000),  # 10 seconds
        ('grpc.keepalive_timeout_ms', 5000),  # 5 seconds
        ('grpc.http2.max_pings_without_data', 0),
        ('grpc.keepalive_permit_without_calls', 1),
    ]
)

# Client-side timeout
response = stub.ValidateUser(
    request,
    timeout=5.0,  # 5 second timeout
    metadata=self._get_metadata()
)
```

## Security Checklist

### Development
- [x] Use shared secret for authentication
- [x] Log all gRPC calls
- [x] Validate inputs
- [x] Handle errors gracefully
- [ ] Use mTLS (recommended for production)

### Production
- [ ] **Enable mTLS** (mutual TLS)
- [ ] **Certificate rotation** strategy
- [ ] **Network segmentation** (private network for gRPC)
- [ ] **Rate limiting** per service
- [ ] **Input validation** on all methods
- [ ] **Comprehensive logging** and monitoring
- [ ] **Timeout configuration** on all calls
- [ ] **Circuit breakers** for resilience
- [ ] **Health checks** for all gRPC servers
- [ ] **Secrets management** (Vault, Kubernetes Secrets)

## Migration Path

### Phase 1: Current (Development)
- Insecure channels with shared secret
- Suitable for local development only

### Phase 2: TLS (Staging)
- Enable TLS encryption
- Server-side certificates
- Validates server identity

### Phase 3: mTLS (Production)
- Mutual TLS with client certificates
- Both client and server authenticate
- Industry-standard security

### Phase 4: Service Mesh (Enterprise)
- Automatic mTLS with Istio/Linkerd
- Advanced traffic management
- Comprehensive observability

## Further Reading

- [gRPC Authentication Guide](https://grpc.io/docs/guides/auth/)
- [gRPC Security Best Practices](https://github.com/grpc/grpc/blob/master/SECURITY.md)
- [Mutual TLS in Microservices](https://www.nginx.com/blog/microservices-reference-architecture-nginx-security/)
- [Istio Security](https://istio.io/latest/docs/concepts/security/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)

---

**Last Updated**: 2026-01-01
**Status**: Development configuration - requires mTLS for production
