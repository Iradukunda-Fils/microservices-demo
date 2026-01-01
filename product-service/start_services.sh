#!/bin/bash
# Startup script for ProductService
# Runs both Django HTTP server and gRPC server

echo "Starting ProductService..."
echo ""

# Wait for public key from UserService
echo "⏳ Waiting for JWT public key from UserService..."
MAX_WAIT=30
WAIT_COUNT=0
while [ ! -f /app/keys/jwt_public.pem ] && [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    if [ $((WAIT_COUNT % 5)) -eq 0 ]; then
        echo "   Still waiting... (${WAIT_COUNT}s/${MAX_WAIT}s)"
    fi
done

if [ -f /app/keys/jwt_public.pem ]; then
    echo "✅ JWT public key found"
else
    echo "⚠️  JWT public key not found after ${MAX_WAIT}s"
    echo "   Will attempt to fetch via HTTP from UserService..."
fi
echo ""

# Always generate gRPC code to ensure it's up to date
echo "Generating gRPC code from Protocol Buffers..."
bash generate_grpc.sh
echo ""

# Make Django migrations
echo "creating database migrations..."
python manage.py makemigrations
echo ""

# Run Django migrations
echo "Running database migrations..."
python manage.py migrate --noinput
echo ""

# Create superuser if it doesn't exist (for development)
echo "Creating superuser (if not exists)..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✓ Superuser created: admin / admin123')
else:
    print('✓ Superuser already exists')
" 2>/dev/null
echo ""

# Create sample products (for development)
echo "Checking if database needs seeding..."
python manage.py shell -c "
from products.models import Product

if Product.objects.count() == 0:
    print('🌱 Database is empty, seeding with sample data...')
    import subprocess
    result = subprocess.run(['python', 'manage.py', 'seed_data', '--products', '20'])
    if result.returncode == 0:
        print('✅ Database seeded successfully')
else:
    print(f'✓ Database already has {Product.objects.count()} products, skipping seeding')
" 2>/dev/null
echo ""

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput > /dev/null 2>&1
echo "✓ Static files collected"
echo ""

# Start gRPC server in background
echo "Starting gRPC server (port 50052)..."
python grpc_server.py &
GRPC_PID=$!
echo "✓ gRPC server started (PID: $GRPC_PID)"
echo ""

# Start Django HTTP server
echo "Starting Django HTTP server (port 8000)..."
echo "✓ REST API: http://0.0.0.0:8000"
echo "✓ Swagger UI: http://0.0.0.0:8000/api/docs/"
echo "✓ Admin: http://0.0.0.0:8000/admin/"
echo ""
python manage.py runserver 0.0.0.0:8000

# Cleanup on exit
trap "kill $GRPC_PID" EXIT
