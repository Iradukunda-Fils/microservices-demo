# ============================================================================
# Multi-Stage Build for Production-Ready React Application
# Educational Note: Multi-stage builds reduce final image size by 90%+
# Development: ~1.2GB, Production: ~25MB
# Stage 1: Build - Install dependencies and build static files
# Stage 2: Production - Serve with Nginx
# ============================================================================

# Stage 1: Builder - Build React application
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
# Educational Note: npm ci is faster and more reliable than npm install for CI/CD
RUN npm ci --only=production

# Copy application code
COPY . .

# Build production-ready static files
# Educational Note: Vite optimizes and minifies code for production
RUN npm run build

# ============================================================================
# Stage 2: Production - Serve with Nginx
# Educational Note: Nginx is lightweight and efficient for serving static files
# ============================================================================
FROM nginx:alpine

# Copy custom nginx configuration for SPA routing
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built static files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Educational Note: Nginx starts automatically with default CMD
# The configuration handles SPA routing (all routes → index.html)
