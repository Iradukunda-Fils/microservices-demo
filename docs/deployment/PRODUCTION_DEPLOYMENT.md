# Production Deployment Guide

## Overview

This guide covers deploying the Microservices Demo to production using Docker Compose with security hardening.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Domain name with DNS configured
- SSL/TLS certificates
- 8GB RAM minimum
- 50GB disk space

## Architecture Differences

### Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| Database | SQLite | PostgreSQL |
| Cache | None | Redis |
| HTTPS | No | Yes (required) |
| gRPC Security | Shared secret | mTLS |
| Secrets | Environment vars | Secrets manager |
| Logging | DEBUG | INFO/WARNING |
| Volume mounts | Yes (hot reload) | No (immutable) |
| Resource limits | No | Yes |
| Networks | Single | Public + Private |

## Step 1: Server Setup

### 1.1 Provision Server

**Minimum Requirements**:
- 4 CPU cores
- 8GB RAM
- 50GB SSD
- Ubuntu 22.04 LTS or similar

**Recommended**:
- 8 CPU cores
- 16GB RAM
- 100GB SSD

### 1.2 Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 1.3 Configure Firewall

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Step 2: SSL/TLS Certificates

### Option 1: Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be at:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Copy to project
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./certs/nginx-cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./certs/nginx-key.pem
sudo chown $USER:$USER ./certs/*.pem
```

### Option 2: Self-Signed (Testing Only)

```bash
# Create certs directory
mkdir -p certs

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout certs/nginx-key.pem \
  -out certs/nginx-cert.pem \
  -subj "/CN=yourdomain.com"
```

## Step 3: Generate mTLS Certificates for gRPC

```bash
# Create Certificate Authority
openssl genrsa -out certs/ca-key.pem 4096
openssl req -new -x509 -days 365 -key certs/ca-key.pem -out certs/ca-cert.pem \
  -subj "/CN=MicroservicesCA"

# Generate server certificates
for service in user-service product-service; do
  openssl genrsa -out certs/${service}-key.pem 4096
  openssl req -new -key certs/${service}-key.pem -out certs/${service}.csr \
    -subj "/CN=${service}"
  openssl x509 -req -days 365 -in certs/${service}.csr \
    -CA certs/ca-cert.pem -CAkey certs/ca-key.pem -CAcreateserial \
    -out certs/${service}-cert.pem
done

# Generate client certificate (OrderService)
openssl genrsa -out certs/order-service-key.pem 4096
openssl req -new -key certs/order-service-key.pem -out certs/order-service.csr \
  -subj "/CN=order-service"
openssl x509 -req -days 365 -in certs/order-service.csr \
  -CA certs/ca-cert.pem -CAkey certs/ca-key.pem -CAcreateserial \
  -out certs/order-service-cert.pem

# Set permissions
chmod 400 certs/*-key.pem
chmod 444 certs/*-cert.pem
```

## Step 4: Configure Environment Variables

```bash
# Copy example file
cp .env.production.example .env.production

# Generate secrets
echo "USER_SERVICE_SECRET_KEY=$(openssl rand -hex 32)" >> .env.production
echo "PRODUCT_SERVICE_SECRET_KEY=$(openssl rand -hex 32)" >> .env.production
echo "ORDER_SERVICE_SECRET_KEY=$(openssl rand -hex 32)" >> .env.production
echo "SERVICE_SECRET=$(openssl rand -hex 32)" >> .env.production

# Generate encryption key
python3 -c "from cryptography.fernet import Fernet; print('FIELD_ENCRYPTION_KEY=' + Fernet.generate_key().decode())" >> .env.production

# Edit file and fill in remaining values
nano .env.production
```

**Required Values**:
- `DOMAIN_NAME`: Your domain name
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: Strong PostgreSQL password
- `REDIS_PASSWORD`: Strong Redis password

## Step 5: Update Nginx Configuration for HTTPS

Create `api-gateway/nginx-prod.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/certs/nginx-cert.pem;
    ssl_certificate_key /etc/nginx/certs/nginx-key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # ... rest of configuration from nginx.conf ...
}
```

## Step 6: Deploy

```bash
# Clone repository
git clone <repository-url>
cd microservices-demo

# Load environment variables
export $(cat .env.production | xargs)

# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Step 7: Initialize Database

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec user-service python manage.py migrate
docker-compose -f docker-compose.prod.yml exec product-service python manage.py migrate
docker-compose -f docker-compose.prod.yml exec order-service python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec user-service python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec user-service python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml exec product-service python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml exec order-service python manage.py collectstatic --noinput

# Seed data (optional)
docker-compose -f docker-compose.prod.yml exec user-service python manage.py seed_data
docker-compose -f docker-compose.prod.yml exec product-service python manage.py seed_data
docker-compose -f docker-compose.prod.yml exec order-service python manage.py seed_data
```

## Step 8: Verify Deployment

```bash
# Check health endpoints
curl https://yourdomain.com/health
curl https://yourdomain.com/health/user
curl https://yourdomain.com/health/product
curl https://yourdomain.com/health/order

# Test API
curl https://yourdomain.com/api/products/

# Check SSL
curl -vI https://yourdomain.com
```

## Step 9: Configure Monitoring

### 9.1 Set Up Log Aggregation

```bash
# Install Promtail (for Loki)
docker run -d --name promtail \
  -v /var/log:/var/log \
  -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
  grafana/promtail:latest \
  -config.file=/etc/promtail/config.yml
```

### 9.2 Set Up Metrics

```bash
# Add Prometheus exporter to services
# See docs/deployment/MONITORING.md for details
```

## Step 10: Backup Strategy

### 10.1 Database Backups

```bash
# Create backup script
cat > /usr/local/bin/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/backups/postgres
DATE=$(date +%Y%m%d_%H%M%S)

docker-compose -f /path/to/docker-compose.prod.yml exec -T postgres \
  pg_dumpall -U microservices_user | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup-db.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /usr/local/bin/backup-db.sh" | crontab -
```

### 10.2 Volume Backups

```bash
# Backup Docker volumes
docker run --rm \
  -v jwt-keys:/data \
  -v /backups:/backup \
  alpine tar czf /backup/jwt-keys-$(date +%Y%m%d).tar.gz /data
```

## Step 11: SSL Certificate Renewal

```bash
# Auto-renewal with Certbot
sudo certbot renew --dry-run

# Add to crontab (check daily)
echo "0 0 * * * certbot renew --quiet && docker-compose -f /path/to/docker-compose.prod.yml restart api-gateway" | sudo crontab -
```

## Maintenance

### Update Services

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec user-service python manage.py migrate
docker-compose -f docker-compose.prod.yml exec product-service python manage.py migrate
docker-compose -f docker-compose.prod.yml exec order-service python manage.py migrate
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f user-service

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Scale Services

```bash
# Scale ProductService to 3 instances
docker-compose -f docker-compose.prod.yml up -d --scale product-service=3

# Update nginx upstream for load balancing
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check resource usage
docker stats

# Check disk space
df -h
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U microservices_user -d userservice
```

### SSL Certificate Issues

```bash
# Verify certificate
openssl x509 -in certs/nginx-cert.pem -text -noout

# Test SSL
curl -vI https://yourdomain.com
```

## Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] mTLS configured for gRPC
- [ ] Strong passwords for all services
- [ ] Secrets stored in secrets manager
- [ ] Firewall configured
- [ ] SSH key-based authentication only
- [ ] Regular security updates
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured
- [ ] Log aggregation set up
- [ ] Rate limiting enabled
- [ ] CORS restricted to specific origins
- [ ] Security headers configured
- [ ] Database access restricted
- [ ] Regular penetration testing

## Further Reading

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Nginx Security](https://www.nginx.com/blog/mitigating-ddos-attacks-with-nginx-and-nginx-plus/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [Let's Encrypt](https://letsencrypt.org/getting-started/)

---

**Last Updated**: 2026-01-01
