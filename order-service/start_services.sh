#!/bin/bash

# Startup script for OrderService
# Educational Note: This script:
# 1. Waits for public key from UserService
# 2. Generates gRPC client code
# 3. Runs database migrations
# 4. Starts Django HTTP server

echo "🚀 Starting OrderService..."

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

# Generate gRPC client code
echo "🔧 Generating gRPC client code..."
chmod +x generate_grpc.sh
./generate_grpc.sh

# Run database migrations
echo "📊 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if needed (for development)
echo "👤 Creating superuser (if needed)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('ℹ️ Superuser already exists')
EOF

# Seed database with sample data (only if empty)
echo "📊 Checking if database needs seeding..."
python manage.py shell -c "
from orders.models import Order

if Order.objects.count() == 0:
    print('🌱 Database is empty, seeding with sample data...')
    print('⚠️  Note: This assumes UserService and ProductService are already seeded!')
    import subprocess
    result = subprocess.run(['python', 'manage.py', 'seed_data', '--orders', '30'])
    if result.returncode == 0:
        print('✅ Database seeded successfully')
else:
    print(f'✓ Database already has {Order.objects.count()} orders, skipping seeding')
" 2>/dev/null
echo ""

# Start Django HTTP server
echo "🌐 Starting Django HTTP server on port 8000..."
python manage.py runserver 0.0.0.0:8000
