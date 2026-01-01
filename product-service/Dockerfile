# Development Dockerfile for ProductService
# Educational Note: This is optimized for development with hot-reload
# For production, use a multi-stage build with gunicorn

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    libpq-dev \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/keys /app/data /app/staticfiles

# Expose ports
# 8000: HTTP/REST API
# 50052: gRPC server
EXPOSE 8000 50052

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Default command (can be overridden by docker-compose)
CMD ["bash", "start_services.sh"]
