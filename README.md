# Microservices Demo - Educational Project

An educational microservices demonstration project showcasing production-ready patterns for distributed systems.

## 🎯 Learning Goals

This project teaches:
- **Microservices Architecture**: Service isolation, independent deployment, and scaling
- **gRPC Communication**: High-performance inter-service communication with Protocol Buffers
- **Security**: RSA-based JWT authentication, 2FA with TOTP, field-level encryption
- **Resilience**: Retry patterns, circuit breakers, fault tolerance
- **Modern Tools**: Django REST Framework, React, Docker Compose, and industry-standard libraries

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

### Getting Started
- **[Quick Start Guide](docs/getting-started/QUICK_START.md)** - Get up and running in 5 minutes

### Features
- **[Feature Overview](docs/FEATURES.md)** - Complete list of all features

### Architecture & Design
- **[API Gateway](docs/architecture/API_GATEWAY.md)** - Nginx routing and configuration

### Security
- **[Security Overview](docs/security/SECURITY_OVERVIEW.md)** - Comprehensive security guide
- **[JWT Best Practices](docs/security/JWT_BEST_PRACTICES.md)** - RSA-based JWT authentication
- **[gRPC Security](docs/security/GRPC_SECURITY.md)** - Secure inter-service communication

### Deployment
- **[Production Deployment](docs/deployment/PRODUCTION_DEPLOYMENT.md)** - Deploy to production
- **[Redis Cache Configuration](docs/deployment/REDIS_CACHE.md)** - Redis setup and usage

## 🏗️ Architecture

```
                    ┌─────────────────────────────────┐
                    │      API Gateway (Nginx)        │
                    │         Port 80                 │
                    └─────────────┬───────────────────┘
                                  │
                    ┌─────────────┴───────────────────┐
                    │                                 │
        ┌───────────▼──────────┐        ┌────────────▼─────────┐
        │   Frontend (React)   │        │  Backend Services    │
        │   - Vite + Tailwind  │        │  - UserService       │
        │   - JWT Auth + 2FA   │        │  - ProductService    │
        │   - Responsive UI    │        │  - OrderService      │
        └──────────────────────┘        └──────────┬───────────┘
                                                   │
                                        ┌──────────┴──────────┐
                                        │   gRPC Communication │
                                        │   - ValidateUser     │
                                        │   - GetProductInfo   │
                                        │   - CheckAvailability│
                                        └──────────┬───────────┘
                                                   │
                                        ┌──────────┴──────────┐
                                        │   Data Layer        │
                                        │   - User DB         │
                                        │   - Product DB      │
                                        │   - Order DB        │
                                        │   - Redis Cache     │
                                        └─────────────────────┘
```

### Architecture Highlights

- **API Gateway**: Single entry point (port 80) for all services
- **Service Isolation**: Each service has its own database
- **Dual Communication**: REST for frontend, gRPC for inter-service
- **Security**: JWT verification at each service, no shared secrets
- **Resilience**: Retry logic and circuit breakers for fault tolerance
- **Caching**: Redis for session storage and API response caching

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Run the Project

```bash
# Clone the repository
git clone <repository-url>
cd microservices-demo

# Start all services
docker-compose up

# Wait for services to start (30-60 seconds)
# Databases will seed automatically with sample data
```

### Access the Application

**Main Application:**
- Frontend: http://localhost/
- API Gateway: http://localhost/

**API Documentation (Swagger):**
- UserService: http://localhost/docs/user
- ProductService: http://localhost/docs/product
- OrderService: http://localhost/docs/order

**Health Checks:**
- All Services: http://localhost/health
- UserService: http://localhost/health/user
- ProductService: http://localhost/health/product
- OrderService: http://localhost/health/order

**Demo Credentials:**
```
Username: user0
Password: password123

Or register your own account!
```

### Sample Data

The application automatically seeds with:
- **10 users** (admin, staff, user0-user9)
- **20 products** (laptops, accessories, tech items)
- **30 orders** (various statuses)



## 📚 Services

### UserService
**Responsibilities:**
- User registration and authentication
- JWT token generation with RS256 (RSA signatures)
- Two-Factor Authentication (TOTP + backup tokens)
- Public key distribution for other services
- User profile management

**REST API Endpoints:**
- `POST /api/users/register/` - Register new user
- `POST /api/token/` - Login and get JWT tokens
- `POST /api/token/refresh/` - Refresh access token
- `GET /api/auth/public-key/` - Get public key for JWT verification
- `GET /api/users/me/` - Get authenticated user profile
- `POST /api/users/2fa/setup/` - Setup 2FA with QR code
- `POST /api/users/2fa/verify-setup/` - Verify 2FA setup
- `POST /api/users/2fa/verify-login/` - Verify 2FA code during login
- `POST /api/users/2fa/disable/` - Disable 2FA
- `GET /api/users/2fa/status/` - Check 2FA status

**gRPC Methods:**
- `ValidateUser(user_id)` - Validate user exists and is active

**Key Technologies:**
- Django REST Framework
- djangorestframework-simplejwt (RS256)
- django-two-factor-auth
- grpcio (server on port 50051)

**Access:** http://localhost/api/users (via API Gateway)

---

### ProductService
**Responsibilities:**
- Product catalog management
- Inventory tracking
- Product search and filtering
- JWT verification with public key (no UserService call needed!)

**REST API Endpoints:**
- `GET /api/products/` - List products (with pagination, search, filters)
- `POST /api/products/` - Create product (admin only)
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product (admin only)
- `PATCH /api/products/{id}/` - Partial update (admin only)
- `DELETE /api/products/{id}/` - Delete product (admin only)

**gRPC Methods:**
- `GetProductInfo(product_id)` - Get product details
- `CheckAvailability(product_id, quantity)` - Check inventory

**Key Technologies:**
- Django REST Framework
- JWT verification (RS256 with public key)
- grpcio (server on port 50052)
- DRF filters and pagination

**Access:** http://localhost/api/products (via API Gateway)

---

### OrderService
**Responsibilities:**
- Order creation and management
- Cross-service validation (User + Product)
- Encrypted sensitive data storage
- Resilience patterns (retry + circuit breaker)
- Order history tracking

**REST API Endpoints:**
- `POST /api/orders/` - Create new order
- `GET /api/orders/{id}/` - Get order details
- `GET /api/orders/user/{user_id}/` - Get user's order history
- `GET /api/orders/` - List all orders (admin only)

**gRPC Clients:**
- Calls UserService: `ValidateUser` (with retry + circuit breaker)
- Calls ProductService: `GetProductInfo`, `CheckAvailability` (with retry + circuit breaker)

**Key Technologies:**
- Django REST Framework
- JWT verification (RS256 with public key)
- grpcio (client)
- tenacity (retry logic with exponential backoff)
- pybreaker (circuit breaker for fault tolerance)
- django-encrypted-model-fields (AES-256 encryption)

**Access:** http://localhost/api/orders (via API Gateway)

---

### Frontend
**Responsibilities:**
- User interface for all features
- Product browsing and search
- Shopping cart management
- Order creation (checkout)
- User authentication with 2FA
- Order history display

**Pages:**
- `/` - Home page
- `/login` - Login with 2FA support
- `/register` - User registration
- `/products` - Product listing with cart
- `/orders` - Order history
- `/2fa-setup` - Two-factor authentication setup

**Key Technologies:**
- React 18 with hooks
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (HTTP client with JWT interceptors)
- React Router (navigation)
- React Hook Form (form validation)
- qrcode.react (QR code display)

**Access:** http://localhost/ (via API Gateway)

---

### API Gateway
**Responsibilities:**
- Single entry point for all services
- Request routing to backend services
- CORS handling
- Health check aggregation
- Load balancing ready
- SSL/TLS termination ready

**Routes:**
- `/` → Frontend
- `/api/users/*` → UserService
- `/api/products/*` → ProductService
- `/api/orders/*` → OrderService
- `/docs/user` → UserService Swagger
- `/docs/product` → ProductService Swagger
- `/docs/order` → OrderService Swagger
- `/health` → All services health check

**Key Technologies:**
- Nginx (Alpine Linux)
- Reverse proxy configuration
- Custom routing rules

**Access:** http://localhost/ (port 80)

---

### Redis
**Responsibilities:**
- Session storage for 2FA and user sessions
- API response caching
- Rate limiting (future)
- Temporary data storage

**Key Features:**
- In-memory data store (sub-millisecond latency)
- Separate databases for each service (0, 1, 2)
- Persistent storage with AOF (Append-Only File)
- Password authentication in production

**Key Technologies:**
- Redis 7 (Alpine Linux)
- redis-py (Python client)
- django-redis (Django integration)

**Configuration:**
- UserService: Database 0 (sessions + cache)
- OrderService: Database 1 (cache)
- ProductService: Database 2 (cache)

**Documentation**: [Redis Cache Configuration](docs/deployment/REDIS_CACHE.md)

**Access:** redis://redis:6379 (internal only)

## 🔐 Security Features

### 1. RSA-Based JWT Authentication (Identity Provider Pattern)
- **UserService** acts as Identity Provider
  - Owns RSA private key (4096-bit) - signs tokens
  - Distributes public key to services
- **All services** verify tokens locally with public key
  - No network calls to UserService (50% latency reduction)
  - Scalable and secure architecture
- Industry standard (OAuth 2.0, OpenID Connect pattern)

**Documentation**: [JWT Best Practices](docs/security/JWT_BEST_PRACTICES.md)

### 2. Two-Factor Authentication (2FA)
- TOTP-based (Google Authenticator, Authy, Microsoft Authenticator)
- 6-digit codes that change every 30 seconds
- 10 hashed backup tokens for account recovery
- One-time use enforcement
- More secure than SMS-based 2FA (no SIM swapping)

**Documentation**: [Two-Factor Authentication](docs/features/TWO_FACTOR_AUTH.md)

### 3. gRPC Security
- **Development**: Shared secret authentication
- **Production**: Mutual TLS (mTLS) recommended
  - Both client and server authenticate
  - All traffic encrypted (TLS 1.3)
  - Certificate-based access control

**Documentation**: [gRPC Security](docs/security/GRPC_SECURITY.md)

### 4. Data Encryption
- **Field-level encryption**: Sensitive database fields (AES-256)
- **Password hashing**: PBKDF2-SHA256
- **Backup token hashing**: PBKDF2-SHA256
- **Secure cookies**: httpOnly, secure, samesite attributes

**Documentation**: [Security Overview](docs/security/SECURITY_OVERVIEW.md)

### 5. Resilience Patterns
- **Retry logic**: Exponential backoff with jitter (tenacity)
- **Circuit breaker**: Prevents cascading failures (pybreaker)
- **Graceful degradation**: Services continue working when dependencies fail
- **Rate limiting**: Prevent abuse (production)

**Documentation**: [Resilience Patterns](docs/patterns/RESILIENCE_PATTERNS.md)

## 📖 Key Concepts Explained

### Why Microservices?
**Benefits:**
- **Independent scaling**: Scale ProductService during high traffic without scaling UserService
- **Independent deployment**: Update OrderService without touching UserService
- **Technology flexibility**: Use different languages/frameworks per service
- **Fault isolation**: One service failure doesn't crash entire system
- **Team autonomy**: Different teams can own different services

**Trade-offs:**
- **Increased complexity**: Distributed debugging, network latency
- **Data consistency challenges**: No ACID transactions across services
- **Operational overhead**: Multiple deployments, monitoring
- **Network overhead**: Inter-service calls add latency

**When to use:** Large applications with multiple teams, need for independent scaling

---

### Why gRPC over REST for Inter-Service Communication?
**Benefits:**
- **7-10x faster** than REST (binary Protocol Buffers vs JSON)
- **Type safety**: Strongly typed contracts prevent errors at compile time
- **HTTP/2**: Multiplexing, bi-directional streaming, header compression
- **Code generation**: Auto-generate client/server code from .proto files
- **Industry standard**: Used by Google, Netflix, Uber, Square

**Trade-offs:**
- **Learning curve**: Protocol Buffers syntax
- **Browser support**: Limited (use REST for frontend)
- **Debugging**: Binary format harder to inspect than JSON

**When to use:** High-performance inter-service communication

---

### Why RS256 (RSA) over HS256 (HMAC) for JWT?
**Benefits:**
- **Better security**: Private key only in UserService, public key distributed
- **Better performance**: Services verify tokens locally without calling UserService (50% latency reduction)
- **Better scalability**: No bottleneck on UserService for token verification
- **Industry standard**: OAuth2/OpenID Connect pattern

**How it works:**
1. UserService signs JWT with RSA private key (RS256)
2. UserService exposes public key at `/api/auth/public-key/`
3. ProductService and OrderService fetch public key on startup
4. Services verify JWT signatures locally using public key
5. No network call to UserService for every request!

**Trade-offs:**
- **Complexity**: Key distribution and management
- **Key rotation**: Need strategy for rotating keys

**When to use:** Microservices with multiple services verifying tokens

---

### Why API Gateway?
**Benefits:**
- **Single entry point**: Clients only need to know one URL
- **Centralized concerns**: CORS, SSL/TLS, rate limiting, authentication
- **Service abstraction**: Change backend services without affecting clients
- **Load balancing**: Distribute traffic across service instances
- **Monitoring**: Centralized logging and metrics

**Trade-offs:**
- **Single point of failure**: Gateway down = entire system down (mitigate with HA)
- **Bottleneck**: All traffic goes through gateway (mitigate with horizontal scaling)
- **Complexity**: Additional component to manage

**When to use:** Always in production microservices

---

### Why Circuit Breaker Pattern?
**Benefits:**
- **Prevents cascading failures**: Stop calling failing service
- **Fast failure**: Return error immediately instead of waiting for timeout
- **Automatic recovery**: Periodically test if service recovered
- **Resource protection**: Don't waste threads on failing calls

**How it works:**
1. **Closed state**: Normal operation, calls go through
2. **Open state**: Service failing, calls fail immediately (no network call)
3. **Half-open state**: Test if service recovered with limited calls

**Configuration in this project:**
- `fail_max=5`: Open circuit after 5 failures
- `timeout=30s`: Try recovery after 30 seconds

**When to use:** Any inter-service communication

---

### Why Retry with Exponential Backoff?
**Benefits:**
- **Handles transient failures**: Network blips, temporary overload
- **Reduces load**: Exponential backoff prevents thundering herd
- **Automatic recovery**: No manual intervention needed

**How it works:**
1. First retry: Wait 1 second
2. Second retry: Wait 2 seconds
3. Third retry: Wait 4 seconds
4. Add jitter: Random delay to prevent synchronized retries

**Configuration in this project:**
- `max_attempts=3`: Try up to 3 times
- `wait_exponential_multiplier=1000`: Start at 1 second
- `wait_exponential_max=10000`: Max 10 seconds

**When to use:** Any network call that might fail transiently

---

### Why Two-Factor Authentication (2FA)?
**Benefits:**
- **Better security**: Requires something you know (password) + something you have (phone)
- **Prevents account takeover**: Even if password leaked, attacker needs 2FA device
- **TOTP better than SMS**: Not vulnerable to SIM swapping attacks
- **Backup tokens**: Account recovery if device lost

**How it works:**
1. User enables 2FA and scans QR code with authenticator app
2. App generates 6-digit codes that change every 30 seconds
3. User enters code during login
4. Server validates code using shared secret
5. If device lost, user can use one-time backup tokens

**When to use:** Any application with sensitive data or financial transactions

## 🛠️ Third-Party Libraries Used

### Why Use Third-Party Libraries?
**Benefits:**
- **Faster development**: 70-80% less code to write
- **Battle-tested**: Used by thousands of projects, bugs already found
- **Best practices**: Implement industry standards correctly
- **Security**: Security experts maintain the code
- **Documentation**: Comprehensive guides and examples

**Trade-offs:**
- **Dependencies**: Need to keep libraries updated
- **Learning curve**: Need to learn library APIs
- **Less control**: Can't customize everything

**Philosophy**: Use libraries for complex, security-critical, or standardized functionality. Write custom code for business logic.

---

### Backend (Python/Django)

#### Django REST Framework (DRF)
**Purpose**: REST API framework  
**Why**: 70% less boilerplate than vanilla Django, automatic serialization, built-in authentication  
**Alternatives**: Flask-RESTful, FastAPI

#### djangorestframework-simplejwt
**Purpose**: JWT authentication with RS256 support  
**Why**: Industry-standard JWT implementation, supports RSA keys, automatic token refresh  
**Alternatives**: PyJWT (lower-level), django-rest-framework-jwt (deprecated)

#### django-two-factor-auth
**Purpose**: Complete 2FA solution with TOTP and backup tokens  
**Why**: Includes QR code generation, backup tokens, device management, battle-tested  
**Alternatives**: django-otp (lower-level), custom implementation (risky)

#### grpcio
**Purpose**: Production-grade gRPC implementation  
**Why**: Official Google implementation, 7-10x faster than REST, type-safe  
**Alternatives**: REST (slower), Thrift (less popular)

#### tenacity
**Purpose**: Retry logic with exponential backoff  
**Why**: Declarative retry policies, supports multiple strategies, well-tested  
**Alternatives**: Custom retry loops (error-prone), backoff library

#### pybreaker
**Purpose**: Circuit breaker pattern  
**Why**: Simple API, configurable states, production-ready  
**Alternatives**: Custom implementation (complex), Netflix Hystrix (Java)

#### django-encrypted-model-fields
**Purpose**: Transparent field-level encryption  
**Why**: Automatic encryption/decryption, AES-256, works with Django ORM  
**Alternatives**: Manual encryption (error-prone), database-level encryption

#### drf-spectacular
**Purpose**: Auto-generated Swagger/OpenAPI documentation  
**Why**: Automatic from DRF serializers, interactive UI, OpenAPI 3.0 standard  
**Alternatives**: drf-yasg (older), manual documentation

#### redis & django-redis
**Purpose**: In-memory caching and session storage  
**Why**: Sub-millisecond response times, reduces database load, scales horizontally  
**Alternatives**: Memcached (less features), database caching (slower)

#### factory-boy
**Purpose**: Test fixture generation  
**Why**: Realistic test data, reduces boilerplate, integrates with Django ORM  
**Alternatives**: Django fixtures (static), manual creation

#### Hypothesis
**Purpose**: Property-based testing  
**Why**: Finds edge cases automatically, generates test data, complements unit tests  
**Alternatives**: Manual test cases (miss edge cases), QuickCheck (Haskell)

---

### Frontend (JavaScript/React)

#### React 18
**Purpose**: UI library with hooks  
**Why**: Component-based, virtual DOM, huge ecosystem, industry standard  
**Alternatives**: Vue, Angular, Svelte

#### Vite
**Purpose**: Fast build tool  
**Why**: 10-100x faster than Webpack, hot module replacement, modern  
**Alternatives**: Create React App (slower), Webpack (complex)

#### Tailwind CSS
**Purpose**: Utility-first CSS framework  
**Why**: Rapid development, consistent design, no CSS files, responsive utilities  
**Alternatives**: Bootstrap, Material-UI, custom CSS

#### Axios
**Purpose**: HTTP client  
**Why**: Interceptors for JWT, automatic JSON parsing, better error handling than fetch  
**Alternatives**: fetch (no interceptors), jQuery (outdated)

#### React Router
**Purpose**: Client-side routing  
**Why**: Standard for React SPAs, declarative routing, protected routes  
**Alternatives**: Reach Router (merged), custom routing

#### React Hook Form
**Purpose**: Performant form validation  
**Why**: Minimal re-renders, built-in validation, easy API  
**Alternatives**: Formik (more re-renders), manual state

#### qrcode.react
**Purpose**: QR code generation  
**Why**: React component, customizable, works with 2FA  
**Alternatives**: qrcode.js (vanilla), manual canvas

---

### Infrastructure

#### Docker
**Purpose**: Containerization  
**Why**: Consistent environments, easy deployment, service isolation  
**Alternatives**: Virtual machines (heavier), bare metal (inconsistent)

#### Docker Compose
**Purpose**: Multi-container orchestration  
**Why**: Simple YAML config, service dependencies, networking  
**Alternatives**: Kubernetes (overkill for dev), manual docker commands

#### Nginx
**Purpose**: API Gateway and reverse proxy  
**Why**: High performance, battle-tested, simple config, industry standard  

#### Redis
**Purpose**: In-memory data store for caching and sessions  
**Why**: Sub-millisecond latency, pub/sub messaging, persistence options, widely adopted  
**Alternatives**: Memcached (simpler, no persistence), database caching (slower)

---

## 🔍 Exploring the Code

### Key Implementations to Study

#### 1. RSA-Based JWT Authentication
**Location**: `user-service/users/views.py`

```python
# UserService generates RSA key pair and signs tokens
from cryptography.hazmat.primitives.asymmetric import rsa
private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)

# Other services verify tokens with public key only
# Location: product-service/product_service/settings.py
SIMPLE_JWT = {
    'ALGORITHM': 'RS256',
    'VERIFYING_KEY': public_key,  # No private key needed!
}
```

**Why this matters**: Services verify tokens locally without calling UserService, reducing latency by 50%.

---

#### 2. Two-Factor Authentication with Backup Tokens
**Location**: `user-service/users/views.py`

```python
# Setup 2FA: Generate TOTP device and 10 backup tokens
device = TOTPDevice.objects.create(user=user, name='default')
backup_tokens = [StaticToken.random_token() for _ in range(10)]

# Verify login: Support both TOTP and backup tokens
if device.verify_token(token):
    # TOTP code valid
elif StaticToken.objects.filter(user=user, token=token).exists():
    # Backup token valid (one-time use)
```

**Why this matters**: Backup tokens prevent account lockout if device is lost.

---

#### 3. gRPC Server Implementation
**Location**: `user-service/grpc_server.py`

```python
# Define service in user.proto
service UserService {
    rpc ValidateUser(ValidateUserRequest) returns (ValidateUserResponse);
}

# Implement in Python
class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    def ValidateUser(self, request, context):
        user = User.objects.get(id=request.user_id)
        return user_pb2.ValidateUserResponse(
            user_id=user.id,
            username=user.username,
            is_active=user.is_active
        )
```

**Why this matters**: gRPC is 7-10x faster than REST for inter-service calls.

---

#### 4. gRPC Client with Retry and Circuit Breaker
**Location**: `order-service/orders/grpc_clients.py`

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from pybreaker import CircuitBreaker

# Retry with exponential backoff
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def validate_user_with_retry(user_id):
    return user_client.ValidateUser(user_id)

# Circuit breaker prevents cascading failures
user_breaker = CircuitBreaker(fail_max=5, timeout_duration=30)

@user_breaker
def validate_user_with_circuit_breaker(user_id):
    return validate_user_with_retry(user_id)
```

**Why this matters**: Resilience patterns prevent cascading failures and handle transient errors.

---

#### 5. Field-Level Encryption
**Location**: `order-service/orders/models.py`

```python
from encrypted_model_fields.fields import EncryptedCharField

class Order(models.Model):
    user_id = EncryptedCharField(max_length=255)  # Encrypted at rest
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
# Automatic encryption/decryption
order = Order.objects.create(user_id="123")  # Encrypted in database
print(order.user_id)  # "123" - Automatically decrypted
```

**Why this matters**: Sensitive data encrypted at rest, even if database is compromised.

---

#### 6. API Gateway Routing
**Location**: `api-gateway/nginx.conf`

```nginx
# Route to UserService
location /api/users {
    proxy_pass http://user-service:8001;
}

# Route to ProductService
location /api/products {
    proxy_pass http://product-service:8002;
}

# Route to OrderService
location /api/orders {
    proxy_pass http://order-service:8003;
}
```

**Why this matters**: Single entry point simplifies client configuration and enables centralized concerns.

---

#### 7. React Authentication Context
**Location**: `frontend/src/context/AuthContext.jsx`

```javascript
// Global authentication state
const AuthContext = createContext();

// JWT interceptor for automatic token refresh
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Token expired, refresh it
      const newToken = await refreshToken();
      // Retry original request
      return axios(originalRequest);
    }
  }
);
```

**Why this matters**: Automatic token refresh provides seamless user experience.

---

#### 8. Database Seeding with Factory-Boy
**Location**: `user-service/users/factories.py`

```python
import factory
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    
# Generate 10 users
users = UserFactory.create_batch(10)
```

**Why this matters**: Realistic test data without manual SQL or fixtures.

---

#### 9. Docker Compose Orchestration
**Location**: `docker-compose.yml`

```yaml
services:
  user-service:
    build: ./user-service
    volumes:
      - jwt-keys:/app/keys  # Shared volume for RSA keys
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      
  product-service:
    depends_on:
      user-service:
        condition: service_healthy  # Wait for UserService
    volumes:
      - jwt-keys:/app/keys:ro  # Read-only access to public key
```

**Why this matters**: Service dependencies and health checks ensure proper startup order.

---

#### 10. Cross-Service Validation
**Location**: `order-service/orders/views.py`

```python
def create_order(request):
    # Validate user via gRPC
    user = validate_user_with_circuit_breaker(user_id)
    
    # Validate products via gRPC
    for item in items:
        product = get_product_info(item['product_id'])
        check_availability(item['product_id'], item['quantity'])
    
    # Create order only if all validations pass
    order = Order.objects.create(...)
```

**Why this matters**: Cross-service validation ensures data consistency without shared database.

## 🧪 Testing

The project includes comprehensive testing:
- **Unit tests**: Specific scenarios and edge cases
- **Property-based tests**: Universal properties with Hypothesis
- **Integration tests**: End-to-end flows

```bash
# Run tests for a service
cd user-service
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## 🎓 Exercises for Learners

### Beginner Level

#### 1. Add Product Categories
**Goal**: Extend ProductService with categories

**Tasks**:
- Add `category` field to Product model
- Update ProductSerializer
- Add category filter to product list endpoint
- Update frontend to show categories

**Learning**: Django models, DRF serializers, filtering

---

#### 2. Add Order Status Updates
**Goal**: Allow updating order status

**Tasks**:
- Add `PATCH /api/orders/{id}/status/` endpoint
- Restrict to admin users only
- Update frontend to show status changes
- Add email notification on status change

**Learning**: DRF permissions, PATCH requests, email integration

---

#### 3. Add User Profile Page
**Goal**: Display and edit user information

**Tasks**:
- Create profile page in frontend
- Add `PATCH /api/users/me/` endpoint
- Allow updating email, name
- Show 2FA status

**Learning**: React forms, PATCH requests, user management

---

### Intermediate Level

#### 4. Add Product Reviews
**Goal**: Allow users to review products

**Tasks**:
- Add Review model (user, product, rating, comment)
- Add review endpoints (create, list, update, delete)
- Update frontend to show reviews
- Add average rating to products
- Prevent duplicate reviews per user

**Learning**: Model relationships, aggregations, permissions

---

#### 5. Add Saga Pattern for Order Creation
**Goal**: Implement distributed transaction with compensation

**Tasks**:
- Create order saga coordinator
- Implement compensation logic (rollback on failure)
- Reserve inventory before creating order
- Release inventory if payment fails
- Add saga state tracking

**Learning**: Distributed transactions, saga pattern, compensation logic

---

#### 6. Add API Rate Limiting
**Goal**: Prevent API abuse

**Tasks**:
- Add rate limiting to API Gateway (Nginx)
- Or use django-ratelimit in services
- Different limits for authenticated vs anonymous
- Return 429 Too Many Requests
- Add rate limit headers

**Learning**: Rate limiting, API security, Nginx configuration

---

#### 7. Add Product Search with Elasticsearch
**Goal**: Full-text search for products

**Tasks**:
- Add Elasticsearch service to docker-compose.yml
- Install django-elasticsearch-dsl
- Index products in Elasticsearch
- Add search endpoint with relevance scoring
- Update frontend with search suggestions

**Learning**: Full-text search, Elasticsearch, indexing

---

### Advanced Level

#### 8. Add Kubernetes Deployment
**Goal**: Deploy to Kubernetes instead of Docker Compose

**Tasks**:
- Create Kubernetes manifests (Deployments, Services, ConfigMaps)
- Set up Ingress for API Gateway
- Configure persistent volumes for databases
- Add horizontal pod autoscaling
- Deploy to Minikube or cloud provider

**Learning**: Kubernetes, container orchestration, cloud deployment

---

#### 9. Add Distributed Tracing
**Goal**: Trace requests across services

**Tasks**:
- Add Jaeger service to docker-compose.yml
- Install opentelemetry libraries
- Add tracing to all services
- Trace gRPC calls
- Visualize request flow in Jaeger UI

**Learning**: Distributed tracing, observability, OpenTelemetry

---

#### 10. Add Monitoring and Alerting
**Goal**: Monitor service health and performance

**Tasks**:
- Add Prometheus for metrics collection
- Add Grafana for visualization
- Expose metrics endpoints in all services
- Create dashboards (request rate, latency, errors)
- Set up alerts (high error rate, service down)

**Learning**: Monitoring, metrics, alerting, Prometheus, Grafana

---

#### 11. Add Event-Driven Architecture
**Goal**: Use message queue for async communication

**Tasks**:
- Add RabbitMQ or Kafka to docker-compose.yml
- Publish events (OrderCreated, ProductUpdated)
- Subscribe to events in other services
- Implement eventual consistency
- Add dead letter queue for failed messages

**Learning**: Event-driven architecture, message queues, eventual consistency

---

#### 12. Add GraphQL API
**Goal**: Alternative to REST API

**Tasks**:
- Install graphene-django
- Create GraphQL schema for products and orders
- Add GraphQL endpoint
- Implement queries and mutations
- Update frontend to use GraphQL

**Learning**: GraphQL, schema design, queries vs mutations

---

#### 13. Add Multi-Tenancy
**Goal**: Support multiple organizations

**Tasks**:
- Add Organization model
- Add tenant_id to all models
- Filter queries by tenant
- Add tenant middleware
- Update JWT to include tenant_id

**Learning**: Multi-tenancy, data isolation, middleware

---

#### 14. Add SMS-Based 2FA
**Goal**: Alternative to TOTP

**Tasks**:
- Integrate Twilio or similar SMS service
- Add phone number to User model
- Send SMS code during login
- Verify SMS code
- Allow choosing between TOTP and SMS

**Learning**: SMS integration, third-party APIs, multiple auth methods

---

#### 15. Add Payment Integration
**Goal**: Process payments for orders

**Tasks**:
- Integrate Stripe or PayPal
- Add payment endpoint
- Handle payment success/failure
- Update order status based on payment
- Add webhook for payment notifications

**Learning**: Payment processing, webhooks, financial transactions

---

### Expert Level

#### 16. Add Service Mesh
**Goal**: Use Istio or Linkerd for service communication

**Tasks**:
- Deploy services to Kubernetes
- Install Istio or Linkerd
- Configure service mesh
- Add traffic management (canary deployments)
- Add mutual TLS between services

**Learning**: Service mesh, traffic management, mTLS

---

#### 17. Add CQRS Pattern
**Goal**: Separate read and write models

**Tasks**:
- Create separate read and write databases
- Implement command handlers (write)
- Implement query handlers (read)
- Sync data between databases
- Optimize read model for queries

**Learning**: CQRS, event sourcing, read/write separation

---

#### 18. Add Machine Learning Recommendations
**Goal**: Recommend products to users

**Tasks**:
- Collect user behavior data (views, purchases)
- Train recommendation model (collaborative filtering)
- Add recommendation endpoint
- Display recommendations in frontend
- Update model periodically

**Learning**: Machine learning, recommendation systems, data pipelines

## 🐛 Troubleshooting

### Services Won't Start

**Problem**: Docker containers fail to start

**Solutions**:
```bash
# Check logs for specific service
docker-compose logs user-service
docker-compose logs product-service
docker-compose logs order-service

# Check all logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose up --build

# Remove volumes and rebuild (WARNING: deletes data)
docker-compose down -v
docker-compose up --build
```

**Common causes**:
- Port conflicts (port 80 already in use)
- Missing dependencies (run `docker-compose build`)
- Database corruption (remove volumes with `-v`)

---

### JWT Verification Fails

**Problem**: ProductService or OrderService can't verify JWT tokens

**Solutions**:
```bash
# Check public key is accessible
curl http://localhost/api/users/auth/public-key/

# Check UserService is running
curl http://localhost/health/user

# Check service logs for JWT errors
docker-compose logs product-service | grep -i jwt
docker-compose logs order-service | grep -i jwt

# Restart services to re-fetch public key
docker-compose restart product-service order-service
```

**Common causes**:
- UserService not started yet (check `depends_on` in docker-compose.yml)
- Public key not generated (check UserService logs)
- Clock skew between containers (JWT has expiration time)

---

### 2FA Setup Issues

**Problem**: QR code won't scan or codes don't work

**Solutions**:
```bash
# Check time synchronization
# TOTP requires accurate time (within 30 seconds)
docker exec user-service date
# Compare with your system time

# Check 2FA status
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/api/users/2fa/status/

# Use backup tokens if TOTP fails
# Backup tokens are displayed during setup
```

**Common causes**:
- Time not synchronized between server and authenticator app
- QR code not scanned correctly (try manual entry of secret)
- Using old code (codes change every 30 seconds)

**Backup token usage**:
- Each backup token can only be used once
- Save backup tokens securely during setup
- Use backup token if device is lost

---

### Circuit Breaker Issues

**Problem**: OrderService returns "Circuit breaker is open" error

**Solutions**:
```bash
# Check if UserService or ProductService is down
curl http://localhost/health/user
curl http://localhost/health/product

# Check circuit breaker state in logs
docker-compose logs order-service | grep -i circuit

# Wait for circuit breaker to reset (30 seconds by default)
# Or restart OrderService to reset circuit breaker
docker-compose restart order-service
```

**Circuit breaker states**:
- **Closed**: Normal operation, calls go through
- **Open**: Service failing, calls fail immediately (no network call)
- **Half-open**: Testing if service recovered

**Configuration**:
- `fail_max=5`: Opens after 5 consecutive failures
- `timeout_duration=30`: Tries recovery after 30 seconds

---

### gRPC Connection Errors

**Problem**: OrderService can't connect to UserService or ProductService via gRPC

**Solutions**:
```bash
# Check gRPC servers are running
docker-compose logs user-service | grep -i grpc
docker-compose logs product-service | grep -i grpc

# Check network connectivity
docker-compose exec order-service ping user-service
docker-compose exec order-service ping product-service

# Check gRPC ports are exposed
docker-compose ps

# Restart services
docker-compose restart user-service product-service order-service
```

**Common causes**:
- gRPC server not started (check startup scripts)
- Network issues (check Docker network)
- Port conflicts (gRPC uses 50051, 50052)

---

### Database Issues

**Problem**: Database errors or data not persisting

**Solutions**:
```bash
# Check database files exist
docker-compose exec user-service ls -la db.sqlite3
docker-compose exec product-service ls -la db.sqlite3
docker-compose exec order-service ls -la db.sqlite3

# Run migrations manually
docker-compose exec user-service python manage.py migrate
docker-compose exec product-service python manage.py migrate
docker-compose exec order-service python manage.py migrate

# Seed database manually
docker-compose exec user-service python manage.py seed_data
docker-compose exec product-service python manage.py seed_data
docker-compose exec order-service python manage.py seed_data

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up
```

---

### Frontend Issues

**Problem**: Frontend not loading or API calls failing

**Solutions**:
```bash
# Check frontend is running
curl http://localhost/

# Check API Gateway is routing correctly
curl http://localhost/health

# Check browser console for errors
# Open DevTools (F12) and check Console tab

# Check network requests
# Open DevTools (F12) → Network tab → Check failed requests

# Clear browser cache and reload
# Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

# Check frontend logs
docker-compose logs frontend
```

**Common causes**:
- API Gateway not routing correctly (check nginx.conf)
- CORS issues (check nginx CORS headers)
- JWT token expired (should auto-refresh)

---

### Port Conflicts

**Problem**: Port 80 already in use

**Solutions**:
```bash
# Check what's using port 80
# Windows:
netstat -ano | findstr :80

# Linux/Mac:
lsof -i :80

# Option 1: Stop conflicting service
# Windows: Stop IIS or other web server
# Linux/Mac: sudo systemctl stop apache2

# Option 2: Change port in docker-compose.yml
# Edit api-gateway ports: "8080:80"
# Access at http://localhost:8080
```

---

### Encryption Issues

**Problem**: Encrypted fields not working

**Solutions**:
```bash
# Check encryption key is set
docker-compose exec order-service env | grep FIELD_ENCRYPTION_KEY

# Check encrypted fields in database
docker-compose exec order-service python manage.py dbshell
# SELECT user_id FROM orders_order LIMIT 1;
# Should see encrypted data (not plaintext)

# Regenerate encryption key (WARNING: can't decrypt old data)
# Edit docker-compose.yml and change FIELD_ENCRYPTION_KEY
```

---

### Performance Issues

**Problem**: Slow response times

**Solutions**:
```bash
# Check service health
curl http://localhost/health

# Check logs for slow queries
docker-compose logs | grep -i slow

# Check retry attempts (might indicate service issues)
docker-compose logs order-service | grep -i retry

# Check circuit breaker state
docker-compose logs order-service | grep -i circuit

# Monitor resource usage
docker stats
```

**Common causes**:
- Retry logic triggering (check service health)
- Circuit breaker open (wait for recovery)
- Database not indexed (add indexes for large datasets)

---

### Getting Help

If you're still stuck:

1. **Check logs**: `docker-compose logs [service-name]`
2. **Check health**: `curl http://localhost/health`
3. **Check documentation**: See docs in `.kiro/specs/microservices-demo/`
4. **Check Swagger**: Interactive API docs at `/docs/user`, `/docs/product`, `/docs/order`
5. **Reset everything**: `docker-compose down -v && docker-compose up --build`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**TL;DR**: You can use, modify, and distribute this project freely. No warranty provided.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick start:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

**Ways to contribute:**
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit code changes
- 💬 Help others in discussions

## 🔒 Security

Found a security vulnerability? Please see [SECURITY.md](SECURITY.md) for responsible disclosure guidelines.

**Do NOT open public issues for security vulnerabilities.**

## 📚 Further Reading

### Microservices Architecture
- [Microservices Patterns](https://microservices.io/patterns/index.html) - Comprehensive pattern catalog
- [Building Microservices](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/) - Sam Newman's book
- [Microservices.io](https://microservices.io/) - Chris Richardson's site

### gRPC and Protocol Buffers
- [gRPC Documentation](https://grpc.io/docs/) - Official docs
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers) - Google's guide
- [gRPC vs REST](https://cloud.google.com/blog/products/api-management/understanding-grpc-openapi-and-rest) - Comparison

### JWT and Authentication
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725) - RFC 8725
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749) - RFC 6749
- [OpenID Connect](https://openid.net/connect/) - Identity layer on OAuth 2.0
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

### Two-Factor Authentication
- [TOTP RFC](https://tools.ietf.org/html/rfc6238) - RFC 6238
- [Google Authenticator](https://github.com/google/google-authenticator) - Open source implementation
- [OWASP 2FA Guide](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)

### Resilience Patterns
- [Release It!](https://pragprog.com/titles/mnee2/release-it-second-edition/) - Michael Nygard's book
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html) - Martin Fowler
- [Retry Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry) - Microsoft Azure docs

### Django and DRF
- [Django Documentation](https://docs.djangoproject.com/) - Official Django docs
- [Django REST Framework](https://www.django-rest-framework.org/) - Official DRF docs
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x) - Best practices book

### React and Frontend
- [React Documentation](https://react.dev/) - Official React docs
- [React Router](https://reactrouter.com/) - Official router docs
- [Tailwind CSS](https://tailwindcss.com/) - Official Tailwind docs

### Docker and Kubernetes
- [Docker Documentation](https://docs.docker.com/) - Official Docker docs
- [Docker Compose](https://docs.docker.com/compose/) - Compose docs
- [Kubernetes Documentation](https://kubernetes.io/docs/) - Official K8s docs

### Security
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Top security risks
- [Cryptography Best Practices](https://www.keylength.com/) - Key length recommendations
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) - Security framework

### Testing
- [Property-Based Testing](https://hypothesis.works/articles/what-is-property-based-testing/) - Introduction
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/) - Python PBT library
- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) - Martin Fowler

### Distributed Systems
- [Designing Data-Intensive Applications](https://dataintensive.net/) - Martin Kleppmann's book
- [Distributed Systems Patterns](https://www.microsoft.com/en-us/research/publication/distributed-systems-patterns/) - Microsoft Research
- [CAP Theorem](https://en.wikipedia.org/wiki/CAP_theorem) - Consistency, Availability, Partition tolerance

## 📄 License

MIT License - Educational purposes

## 🤝 Contributing

This is an educational project. Feel free to fork and experiment!

---

**Built with ❤️ for learning microservices architecture**
# microservices-demo
