# API Gateway - Nginx Configuration

## Overview

The API Gateway serves as the single entry point for all client requests, routing them to the appropriate backend services. It's implemented using Nginx as a reverse proxy.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client (Browser/App)                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    API Gateway (Nginx)                       │
│                         Port 80                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Routing Rules                           │  │
│  │  /                    → Frontend (React)             │  │
│  │  /api/users/*         → UserService:8000             │  │
│  │  /api/products/*      → ProductService:8000          │  │
│  │  /api/orders/*        → OrderService:8000            │  │
│  │  /api/token/*         → UserService:8000             │  │
│  │  /docs/user           → UserService Swagger          │  │
│  │  /docs/product        → ProductService Swagger       │  │
│  │  /docs/order          → OrderService Swagger         │  │
│  │  /health              → Gateway Health Check         │  │
│  │  /health/user         → UserService Health           │  │
│  │  /health/product      → ProductService Health        │  │
│  │  /health/order        → OrderService Health          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  UserService   │  │ ProductService  │  │  OrderService  │
│    :8000       │  │     :8000       │  │     :8000      │
└────────────────┘  └─────────────────┘  └────────────────┘
```

## Routing Configuration

### Frontend Routes

```nginx
location / {
    proxy_pass http://frontend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

**Purpose**: Serves the React application and handles client-side routing.

**Features**:
- WebSocket support for hot module replacement (HMR) in development
- Cache bypass for dynamic content
- Preserves original host header

### UserService Routes

```nginx
# User management endpoints
location /api/users {
    proxy_pass http://user_service/api/users;
    # ... headers ...
}

# JWT token endpoints
location /api/token {
    proxy_pass http://user_service/api/token;
    # ... headers ...
}

# Public key endpoint
location /api/auth {
    proxy_pass http://user_service/api/auth;
    # ... headers ...
}
```

**Endpoints**:
- `/api/users/` - User CRUD operations
- `/api/users/me/` - Current user profile
- `/api/users/2fa/*` - Two-factor authentication
- `/api/token/` - JWT token obtain
- `/api/token/refresh/` - JWT token refresh
- `/api/auth/public-key/` - RSA public key for JWT verification

### ProductService Routes

```nginx
location /api/products {
    proxy_pass http://product_service/api/products;
    # ... headers ...
}
```

**Endpoints**:
- `/api/products/` - Product listing (with pagination, search, filters)
- `/api/products/{id}/` - Product details
- `/api/products/` (POST) - Create product (admin only)
- `/api/products/{id}/` (PUT/PATCH) - Update product (admin only)
- `/api/products/{id}/` (DELETE) - Delete product (admin only)

### OrderService Routes

```nginx
location /api/orders {
    proxy_pass http://order_service/api/orders;
    # ... headers ...
}
```

**Endpoints**:
- `/api/orders/` - Create order (POST) or list orders (GET, admin only)
- `/api/orders/{id}/` - Order details
- `/api/orders/user/{user_id}/` - User's order history

### Health Check Routes

```nginx
# Gateway health
location /health {
    access_log off;
    return 200 "API Gateway is healthy\n";
    add_header Content-Type text/plain;
}

# Service health checks
location /health/user {
    proxy_pass http://user_service/health/;
}

location /health/product {
    proxy_pass http://product_service/health/;
}

location /health/order {
    proxy_pass http://order_service/health/;
}
```

**Purpose**: Monitor service availability for Docker health checks and load balancers.

### API Documentation Routes

```nginx
location /docs/user {
    proxy_pass http://user_service/api/docs/;
}

location /docs/product {
    proxy_pass http://product_service/api/docs/;
}

location /docs/order {
    proxy_pass http://order_service/api/docs/;
}
```

**Purpose**: Interactive Swagger UI for API exploration and testing.

## CORS Configuration

```nginx
# CORS headers
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, PATCH, DELETE, OPTIONS' always;
add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type, Accept' always;
add_header 'Access-Control-Max-Age' 1728000 always;

# Handle preflight requests
if ($request_method = 'OPTIONS') {
    return 204;
}
```

**Purpose**: Allow frontend (running on different origin in development) to make API requests.

**Production Note**: In production, replace `'*'` with specific allowed origins for better security.

## Proxy Headers

All backend routes include these headers:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

**Purpose**:
- `Host`: Preserve original host header
- `X-Real-IP`: Client's real IP address
- `X-Forwarded-For`: Chain of proxy IPs
- `X-Forwarded-Proto`: Original protocol (http/https)

**Use Case**: Backend services can log client IP and detect HTTPS connections.

## Timeout Configuration

```nginx
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
```

**Purpose**: Prevent hanging connections and provide reasonable timeout for long-running requests.

**Tuning**:
- Increase for long-running operations (file uploads, reports)
- Decrease for fast APIs to fail fast

## Buffer Configuration

```nginx
client_max_body_size 10M;
proxy_buffer_size 128k;
proxy_buffers 4 256k;
proxy_busy_buffers_size 256k;
```

**Purpose**:
- `client_max_body_size`: Maximum request body size (file uploads)
- `proxy_buffer_size`: Buffer for response headers
- `proxy_buffers`: Buffers for response body
- `proxy_busy_buffers_size`: Maximum busy buffer size

**Tuning**:
- Increase `client_max_body_size` for large file uploads
- Increase buffers for large API responses

## Upstream Configuration

```nginx
upstream user_service {
    server user-service:8000;
}

upstream product_service {
    server product-service:8000;
}

upstream order_service {
    server order-service:8000;
}

upstream frontend {
    server frontend:3000;
}
```

**Purpose**: Define backend service locations.

**Load Balancing**: Add multiple servers for load balancing:

```nginx
upstream user_service {
    server user-service-1:8000;
    server user-service-2:8000;
    server user-service-3:8000;
}
```

**Health Checks**: Nginx Plus supports active health checks:

```nginx
upstream user_service {
    server user-service:8000 max_fails=3 fail_timeout=30s;
}
```

## Static Files (Django Admin)

```nginx
location /static/user/ {
    alias /var/www/static/user/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

**Purpose**: Serve Django admin static files (CSS, JS) efficiently.

**Caching**: 30-day cache for static assets with immutable flag.

## Security Considerations

### Current Configuration (Development)

```nginx
add_header 'Access-Control-Allow-Origin' '*' always;
```

**Risk**: Allows requests from any origin.

### Production Configuration

```nginx
# Only allow specific origins
add_header 'Access-Control-Allow-Origin' 'https://yourdomain.com' always;

# Or use variables for multiple origins
map $http_origin $cors_origin {
    default "";
    "https://yourdomain.com" $http_origin;
    "https://app.yourdomain.com" $http_origin;
}

add_header 'Access-Control-Allow-Origin' $cors_origin always;
```

### SSL/TLS Configuration (Production)

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... rest of configuration ...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Rate Limiting (Production)

```nginx
# Define rate limit zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# Apply to API endpoints
location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    # ... rest of configuration ...
}
```

**Configuration**:
- `rate=10r/s`: 10 requests per second per IP
- `burst=20`: Allow bursts up to 20 requests
- `nodelay`: Don't delay burst requests

## Monitoring and Logging

### Access Logs

```nginx
access_log /var/log/nginx/access.log;
```

**Format**: Combined log format with timestamp, IP, method, URL, status, size.

**Analysis**: Use tools like GoAccess or AWStats for log analysis.

### Error Logs

```nginx
error_log /var/log/nginx/error.log;
```

**Levels**: debug, info, notice, warn, error, crit, alert, emerg.

**Production**: Set to `warn` or `error` to reduce noise.

### Custom Log Format

```nginx
log_format api_log '$remote_addr - $remote_user [$time_local] '
                   '"$request" $status $body_bytes_sent '
                   '"$http_referer" "$http_user_agent" '
                   'rt=$request_time uct="$upstream_connect_time" '
                   'uht="$upstream_header_time" urt="$upstream_response_time"';

access_log /var/log/nginx/api_access.log api_log;
```

**Metrics**:
- `request_time`: Total request time
- `upstream_connect_time`: Time to connect to backend
- `upstream_header_time`: Time to receive response headers
- `upstream_response_time`: Time to receive full response

## Testing the Gateway

### Health Check

```bash
curl http://localhost/health
# Expected: "API Gateway is healthy"
```

### Service Health Checks

```bash
curl http://localhost/health/user
curl http://localhost/health/product
curl http://localhost/health/order
```

### API Endpoints

```bash
# UserService
curl http://localhost/api/users/

# ProductService
curl http://localhost/api/products/

# OrderService (requires authentication)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/api/orders/
```

### Swagger Documentation

```bash
# Open in browser
http://localhost/docs/user
http://localhost/docs/product
http://localhost/docs/order
```

## Troubleshooting

### 502 Bad Gateway

**Cause**: Backend service is down or not responding.

**Solution**:
```bash
# Check service health
docker-compose ps
docker-compose logs user-service
docker-compose logs product-service
docker-compose logs order-service

# Restart services
docker-compose restart user-service
```

### 504 Gateway Timeout

**Cause**: Backend service taking too long to respond.

**Solution**:
- Increase timeout values in nginx.conf
- Optimize backend service performance
- Check for slow database queries

### CORS Errors

**Cause**: CORS headers not configured correctly.

**Solution**:
- Check browser console for specific error
- Verify CORS headers in nginx.conf
- Test with curl to isolate issue

### Static Files Not Loading

**Cause**: Static file paths not configured correctly.

**Solution**:
```bash
# Check static files exist
docker-compose exec api-gateway ls -la /var/www/static/user/

# Check volume mounts in docker-compose.yml
docker-compose config | grep -A 5 volumes
```

## Performance Optimization

### Enable Gzip Compression

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript 
           application/json application/javascript application/xml+rss;
```

### Enable HTTP/2

```nginx
listen 443 ssl http2;
```

### Connection Pooling

```nginx
upstream user_service {
    server user-service:8000;
    keepalive 32;
}

location /api/users {
    proxy_pass http://user_service;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
}
```

### Caching

```nginx
# Cache zone
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

# Cache GET requests
location /api/products {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
    add_header X-Cache-Status $upstream_cache_status;
    
    proxy_pass http://product_service/api/products;
}
```

## Best Practices

1. **Use Upstream Blocks**: Define upstreams for better organization and load balancing
2. **Set Timeouts**: Prevent hanging connections
3. **Enable Logging**: Monitor traffic and errors
4. **Use HTTPS in Production**: Encrypt all traffic
5. **Implement Rate Limiting**: Prevent abuse
6. **Enable Compression**: Reduce bandwidth
7. **Cache Static Content**: Improve performance
8. **Monitor Health Checks**: Detect service failures
9. **Use HTTP/2**: Better performance
10. **Restrict CORS**: Only allow trusted origins

## Further Reading

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Nginx Load Balancing](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)
- [Nginx Security](https://www.nginx.com/blog/mitigating-ddos-attacks-with-nginx-and-nginx-plus/)

---

**Last Updated**: 2026-01-01
