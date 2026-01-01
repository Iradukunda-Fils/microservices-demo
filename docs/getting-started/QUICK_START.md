# Quick Start Guide

Get the Microservices Demo up and running in 5 minutes!

## Prerequisites

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git**
- **8GB RAM** minimum
- **10GB disk space**

### Install Docker

**Windows/Mac**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop)

**Linux**:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Verify installation:
```bash
docker --version
docker-compose --version
```

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd microservices-demo
```

## Step 2: Start All Services

```bash
docker-compose up
```

**What happens**:
1. Builds Docker images for all services (first time: 5-10 minutes)
2. Starts 5 containers: API Gateway, UserService, ProductService, OrderService, Frontend
3. Generates RSA keys for JWT authentication
4. Runs database migrations
5. Seeds databases with sample data
6. Services become healthy (30-60 seconds)

**Watch for**:
```
user-service     | ✅ Database migrations complete
user-service     | ✅ Sample data seeded
product-service  | ✅ Database migrations complete
product-service  | ✅ Sample data seeded
order-service    | ✅ Database migrations complete
order-service    | ✅ Sample data seeded
api-gateway      | ✅ API Gateway is healthy
```

## Step 3: Access the Application

Open your browser and navigate to:

**Main Application**: http://localhost/

**API Documentation**:
- UserService: http://localhost/docs/user
- ProductService: http://localhost/docs/product
- OrderService: http://localhost/docs/order

**Health Checks**:
- All Services: http://localhost/health
- UserService: http://localhost/health/user
- ProductService: http://localhost/health/product
- OrderService: http://localhost/health/order

## Step 4: Login

Use one of the pre-seeded accounts:

```
Username: user0
Password: password123
```

Or register a new account!

## Step 5: Explore Features

### Browse Products
1. Click "Products" in the navigation
2. View 20 pre-seeded products
3. Use search and filters
4. Click a product to see details

### Create an Order
1. Go to product details
2. Select quantity
3. Click "Order Now"
4. Confirm order
5. View in "My Orders"

### Enable Two-Factor Authentication
1. Click your username → "2FA Setup"
2. Click "Enable 2FA"
3. Scan QR code with Google Authenticator or Authy
4. Save backup tokens
5. Enter 6-digit code to verify
6. Logout and login again to test 2FA

## What's Running?

```
┌─────────────────────────────────────────────────────────┐
│                  http://localhost/                       │
│                   API Gateway (Nginx)                    │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼─────┐ ┌───────▼────────┐
│  UserService   │ │ Product  │ │  OrderService  │
│   Port 8000    │ │ Service  │ │   Port 8000    │
│   gRPC 50051   │ │ Port 8000│ │                │
└────────────────┘ │ gRPC 50052│ └────────────────┘
                   └───────────┘
```

**Services**:
- **API Gateway**: Routes requests to services (port 80)
- **UserService**: Authentication, 2FA, user management
- **ProductService**: Product catalog, inventory
- **OrderService**: Order creation, cross-service validation
- **Frontend**: React application

**Databases**:
- Each service has its own SQLite database
- Data persists in Docker volumes

## Sample Data

The system automatically seeds with:

**Users** (10 total):
- `admin` / `admin123` (superuser)
- `staff` / `staff123` (staff user)
- `user0` to `user9` / `password123` (regular users)

**Products** (20 total):
- Laptops, accessories, tech items
- Prices: $99 - $2,499
- Inventory: 5-50 units each

**Orders** (30 total):
- Various statuses: pending, processing, shipped, delivered
- Assigned to different users

See [Database Seeding Guide](../development/DATABASE_SEEDING.md) for details.

## Common Commands

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs user-service
docker-compose logs product-service
docker-compose logs order-service
docker-compose logs frontend

# Follow logs (real-time)
docker-compose logs -f user-service
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart user-service
```

### Stop Services

```bash
# Stop (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

### Rebuild Services

```bash
# Rebuild all
docker-compose up --build

# Rebuild specific service
docker-compose up --build user-service
```

### Access Service Shell

```bash
# Django shell
docker-compose exec user-service python manage.py shell

# Bash shell
docker-compose exec user-service bash
```

### Run Database Migrations

```bash
docker-compose exec user-service python manage.py migrate
docker-compose exec product-service python manage.py migrate
docker-compose exec order-service python manage.py migrate
```

### Seed Database Manually

```bash
docker-compose exec user-service python manage.py seed_data
docker-compose exec product-service python manage.py seed_data
docker-compose exec order-service python manage.py seed_data
```

## Troubleshooting

### Services Won't Start

**Problem**: Containers fail to start or exit immediately.

**Solution**:
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Port 80 Already in Use

**Problem**: Another service is using port 80.

**Solution**:

**Option 1**: Stop the conflicting service
```bash
# Windows: Stop IIS
net stop w3svc

# Linux/Mac: Stop Apache
sudo systemctl stop apache2
```

**Option 2**: Change the port
```yaml
# Edit docker-compose.yml
api-gateway:
  ports:
    - "8080:80"  # Change to port 8080
```

Then access at http://localhost:8080/

### Frontend Not Loading

**Problem**: Blank page or loading forever.

**Solution**:
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up --build frontend

# Clear browser cache
# Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

### JWT Verification Fails

**Problem**: "Invalid token" or "Token verification failed" errors.

**Solution**:
```bash
# Check UserService is running
curl http://localhost/health/user

# Restart services to regenerate keys
docker-compose restart user-service product-service order-service

# Check public key is accessible
curl http://localhost/api/auth/public-key/
```

### Database Errors

**Problem**: "Database is locked" or "No such table" errors.

**Solution**:
```bash
# Run migrations
docker-compose exec user-service python manage.py migrate
docker-compose exec product-service python manage.py migrate
docker-compose exec order-service python manage.py migrate

# If still failing, reset database
docker-compose down -v
docker-compose up
```

### 2FA Not Working

**Problem**: QR code won't scan or codes don't work.

**Solution**:
1. **Check time synchronization**: TOTP requires accurate time
   ```bash
   docker exec user-service date
   # Compare with your system time
   ```

2. **Use manual entry**: Copy the secret key and enter manually in authenticator app

3. **Use backup tokens**: If you saved them during setup

4. **Disable and re-enable 2FA**: Login without 2FA, go to 2FA Setup, disable, then enable again

See [Troubleshooting Guide](TROUBLESHOOTING.md) for more issues.

## Next Steps

### Learn the Architecture
- Read [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)
- Understand [Service Communication](../architecture/SERVICE_COMMUNICATION.md)
- Study [API Gateway](../architecture/API_GATEWAY.md)

### Explore the Code
- Review [UserService](../services/USER_SERVICE.md)
- Study [ProductService](../services/PRODUCT_SERVICE.md)
- Understand [OrderService](../services/ORDER_SERVICE.md)

### Try the Tutorials
- [Adding a New Service](../tutorials/ADDING_NEW_SERVICE.md)
- [Implementing 2FA](../tutorials/IMPLEMENTING_2FA.md)
- [gRPC Communication](../tutorials/GRPC_TUTORIAL.md)

### Set Up Development Environment
- Follow [Development Setup](../development/DEVELOPMENT_SETUP.md)
- Learn [Testing Strategies](../development/TESTING.md)
- Explore [API Documentation](../development/API_DOCUMENTATION.md)

## Getting Help

- **Documentation**: Check the [docs/](../) directory
- **API Docs**: Interactive Swagger UI at `/docs/user`, `/docs/product`, `/docs/order`
- **Logs**: `docker-compose logs [service-name]`
- **Health Checks**: http://localhost/health
- **Troubleshooting**: [Troubleshooting Guide](TROUBLESHOOTING.md)

## Clean Up

When you're done:

```bash
# Stop services (keeps data)
docker-compose down

# Remove everything including data
docker-compose down -v

# Remove Docker images
docker-compose down --rmi all -v
```

---

**Congratulations!** You now have a fully functional microservices application running locally. Happy learning! 🎉

---

**Last Updated**: 2026-01-01
