# ============================================================================
# API Gateway Dockerfile - Production-Ready Nginx Configuration
# Educational Note: Uses official Nginx Alpine image for minimal size (~25MB)
# Alpine Linux is security-focused and lightweight
# ============================================================================

FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create log directory
RUN mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx

# Expose port 80
EXPOSE 80

# Health check
# Educational Note: Health checks ensure the gateway is responding
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Educational Note: Nginx will start automatically with the default CMD
# The configuration routes requests to appropriate backend services
# In production, add SSL/TLS configuration and certificates
