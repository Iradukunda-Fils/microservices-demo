# OrderService Testing Guide

This guide shows how to test the OrderService implementation.

## Prerequisites

1. Start all services:
```bash
docker-compose up
```

2. Wait for all services to be healthy (check logs)

## Test Flow

### Step 1: Register a User (UserService)

```bash
curl -X POST http://localhost:8001/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### Step 2: Login and Get JWT Token

```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

Save the `access` token from the response.

### Step 3: List Products (ProductService)

```bash
curl -X GET http://localhost:8002/api/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Note the product IDs (should be 1-5 from sample data).

### Step 4: Create an Order (OrderService) ⭐

```bash
curl -X POST http://localhost:8003/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "user_id": 1,
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      },
      {
        "product_id": 2,
        "quantity": 1
      }
    ]
  }'
```

**What happens behind the scenes:**
1. OrderService validates JWT token using public key (no call to UserService!)
2. OrderService calls UserService gRPC to validate user exists
3. OrderService calls ProductService gRPC to get product info
4. OrderService calls ProductService gRPC to check inventory
5. OrderService calculates total amount
6. OrderService creates order with encrypted user_id
7. OrderService creates order items

**Resilience patterns in action:**
- If a service is slow, tenacity retries with exponential backoff
- If a service fails repeatedly, circuit breaker opens
- All errors are logged comprehensively

### Step 5: Get Order Details

```bash
curl -X GET http://localhost:8003/api/orders/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Step 6: Get User's Order History

```bash
curl -X GET http://localhost:8003/api/orders/user/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Testing Resilience Patterns

### Test Retry Logic

1. Stop ProductService:
```bash
docker stop product-service
```

2. Try to create an order - you'll see retry attempts in logs

3. Restart ProductService:
```bash
docker start product-service
```

### Test Circuit Breaker

1. Stop UserService:
```bash
docker stop user-service
```

2. Try to create multiple orders - after 5 failures, circuit breaker opens

3. Subsequent requests fail immediately (no retry)

4. After 30 seconds, circuit breaker enters half-open state

## Verify Encryption

Check that user_id is encrypted in the database:

```bash
docker exec -it order-service sqlite3 db.sqlite3 "SELECT * FROM orders_order;"
```

You should see encrypted user_id values, not plaintext!

## Check Swagger Documentation

Visit: http://localhost:8003/api/docs/

## Monitor Logs

Watch OrderService logs to see:
- gRPC calls
- Retry attempts
- Circuit breaker state changes
- Validation steps

```bash
docker logs -f order-service
```

## Expected Log Output

```
🔍 Validating user 1 via gRPC
✅ User 1 validated successfully
🔍 Getting product info for 1 via gRPC
✅ Product 1 info retrieved successfully
🔍 Checking availability for product 1 (qty: 2) via gRPC
✅ Product 1 available (qty: 2)
📦 Creating order for user 1 with 2 items
✅ Order 1 created successfully (total: $2199.98)
```

## Troubleshooting

### "Circuit breaker OPEN"
- A service has failed repeatedly
- Wait 30 seconds for circuit breaker to reset
- Check service health: `docker ps`

### "Failed to validate user"
- User doesn't exist
- Check user_id is correct
- Verify UserService is running

### "Insufficient inventory"
- Product doesn't have enough stock
- Check product inventory: `GET /api/products/{id}/`
- Reduce quantity in order

### "JWT token invalid"
- Token expired (60 minutes)
- Get a new token: `POST /api/token/`
- Check token format: `Bearer YOUR_TOKEN`
