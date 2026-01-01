#!/bin/bash
# Startup script for UserService
# Runs both Django HTTP server and gRPC server
#
# Educational Note: In production, use a process manager like:
# - Supervisor
# - systemd
# - Docker Compose (separate containers)
# - Kubernetes (separate pods)

echo "Starting UserService..."
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

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput > /dev/null 2>&1
echo "✓ Static files collected"
echo ""

# Seed database with sample data (only if empty)
echo "Checking if database needs seeding..."
python manage.py shell -c "
from users.models import User
if User.objects.count() <= 1:  # Only superuser exists
    print('🌱 Database is empty, seeding with sample data...')
    import subprocess
    result = subprocess.run(['python', 'manage.py', 'seed_data', '--users', '10'])
    if result.returncode == 0:
        print('✅ Database seeded successfully')
else:
    print('✓ Database already has data, skipping seeding')
" 2>/dev/null
echo ""

# Start gRPC server in background
echo "Starting gRPC server (port 50051)..."
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
