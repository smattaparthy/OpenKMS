# OpenKMS Deployment Guide

This comprehensive guide covers all aspects of deploying OpenKMS in various environments.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Start](#quick-start)
3. [Development Setup](#development-setup)
4. [Production Deployment](#production-deployment)
5. [Docker Compose Configuration](#docker-compose-configuration)
6. [Environment Configuration](#environment-configuration)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Database Setup](#database-setup)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Backup and Recovery](#backup-and-recovery)
11. [Troubleshooting](#troubleshooting)
12. [Security Considerations](#security-considerations)

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **Memory**: 4GB RAM
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04 LTS / macOS 10.15+ / Docker-capable Linux

### Recommended Requirements (Production)
- **CPU**: 4+ cores
- **Memory**: 8GB+ RAM
- **Storage**: 50GB+ SSD
- **Network**: 100+ Mbps bandwidth
- **OS**: Ubuntu 22.04 LTS / RHEL 8+

### Software Dependencies
- Docker 20.10+
- Docker Compose 2.0+
- Git
- OpenSSL (for SSL certificate generation)

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/openkms.git
cd openkms
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Development Environment
```bash
docker-compose up -d
```

### 4. Access the Application
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development Setup

### Prerequisites
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Development Environment Setup

1. **Clone and Setup**
```bash
git clone https://github.com/your-org/openkms.git
cd openkms
cp .env.example .env
```

2. **Configure Development Environment**
```bash
# Edit .env for development
cat > .env << EOF
DEBUG=True
LOG_LEVEL=DEBUG
SECRET_KEY=development-secret-key
POSTGRES_PASSWORD=dev_password
DATABASE_URL=postgresql://openkms:dev_password@postgres:5432/openkms
REDIS_URL=redis://redis:6379/0
FRONTEND_URL=http://localhost:8080
ALLOWED_HOSTS=localhost,127.0.0.1
BACKEND_URL=http://localhost:8000
EOF
```

3. **Start Services**
```bash
# Start all services
docker-compose up -d

# Start with development overrides
docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Development Tools

#### Backend Development
```bash
# Access backend container
docker-compose exec backend bash

# Run tests
docker-compose exec backend pytest

# Check logs
docker-compose logs -f backend
```

#### Frontend Development
```bash
# Access frontend container
docker-compose exec frontend bash

# Run tests
docker-compose exec frontend dotnet test

# Check logs
docker-compose logs -f frontend
```

### Hot Reload

Both backend and frontend support hot reload in development mode:

```bash
# Backend code changes auto-reload (uvicorn --reload)
# Frontend changes require container restart
docker-compose restart frontend
```

## Production Deployment

### Production Environment Setup

1. **Prepare Production Environment**
```bash
# Production server setup
sudo apt update
sudo apt upgrade -y
sudo apt install -y docker.io docker-compose git nginx certbot python3-certbot-nginx

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

2. **Clone and Configure**
```bash
git clone https://github.com/your-org/openkms.git /opt/openkms
cd /opt/openkms
cp .env.example .env
```

3. **Configure Production Environment**
```bash
# Edit .env for production
cat > .env << EOF
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=your-very-secure-secret-key-change-this-in-production
POSTGRES_PASSWORD=your-secure-database-password
DATABASE_URL=postgresql://openkms:your-secure-database-password@postgres:5432/openkms
REDIS_URL=redis://redis:6379/0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080
DOMAIN_NAME=your-domain.com
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://your-domain.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@your-domain.com
EOF
```

4. **Setup SSL Certificates**
```bash
sudo mkdir -p /opt/openkms/nginx/ssl
sudo cp your-cert.pem /opt/openkms/nginx/ssl/cert.pem
sudo cp your-key.pem /opt/openkms/nginx/ssl/key.pem
sudo cp your-chain.pem /opt/openkms/nginx/ssl/chain.pem
sudo chmod 600 /opt/openkms/nginx/ssl/key.pem
```

5. **Start Production Services**
```bash
# Start production services with nginx proxy
docker-compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml --profile proxy up -d
```

### Production Deployment Strategies

#### Single Server Deployment
```bash
# Stop existing services
docker-compose down

# Pull latest images
docker-compose pull

# Start production services
docker-compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml --profile proxy up -d

# Run database migrations
docker-compose exec backend alembic upgrade head
```

#### Multi-Server Deployment (Recommended for Scale)

1. **Database Server**
```bash
# On database server
sudo apt install postgresql-15 redis-server
sudo systemctl start postgresql redis
```

2. **Application Server**
```bash
# On application server
docker run -d \
  --name openkms-backend \
  -e DATABASE_URL="postgresql://openkms:password@db-server:5432/openkms" \
  -e REDIS_URL="redis://redis-server:6379/0" \
  openkms-backend:latest
```

3. **Load Balancer**
```bash
# Configure nginx as load balancer
upstream backend_servers {
    server app1:8000;
    server app2:8000;
}
```

## Docker Compose Configuration

### Available Configuration Files

- `docker-compose.yml` - Base configuration
- `docker-compose.override.yml` - Development overrides
- `docker-compose.prod.yml` - Production configuration

### Service Configuration

#### Backend (FastAPI)
```yaml
backend:
  build: ./openkms-backend
  environment:
    - DATABASE_URL=postgresql://openkms:${POSTGRES_PASSWORD}@postgres/openkms
    - REDIS_URL=redis://redis:6379/0
  ports:
    - "8000:8000"
  depends_on:
    - postgres
    - redis
```

#### Frontend (Blazor)
```yaml
frontend:
  build: ./openkms-frontend
  environment:
    - ASPNETCORE_ENVIRONMENT=Production
    - ApiSettings__BaseUrl=https://${DOMAIN_NAME}
  ports:
    - "8080:8080"
  depends_on:
    - backend
```

#### Database (PostgreSQL)
```yaml
postgres:
  image: postgres:15-bullseye
  environment:
    - POSTGRES_USER=openkms
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    - POSTGRES_DB=openkms
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
```

#### Cache (Redis)
```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data
  ports:
    - "6379:6379"
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect openkms_postgres_data

# Backup volume
docker run --rm -v openkms_postgres_data:/volume -v $(pwd):/backup alpine tar cvf /backup/postgres-backup.tar /volume

# Restore volume
docker run --rm -v openkms_postgres_data:/volume -v $(pwd):/backup alpine tar xvf /backup/postgres-backup.tar -C /volume --strip 1
```

## Environment Configuration

### Required Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes | - |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `DATABASE_URL` | Database connection string | Yes | - |
| `REDIS_URL` | Redis connection string | Yes | - |
| `DEBUG` | Debug mode | No | `False` |
| `LOG_LEVEL` | Logging level | No | `INFO` |
| `DOMAIN_NAME` | Production domain name | No | - |
| `FRONTEND_URL` | Frontend URL for CORS | No | `http://localhost:8080` |

### Environment Files

#### `.env` (Production)
```bash
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=your-secure-secret-key
POSTGRES_PASSWORD=your-database-password
DATABASE_URL=postgresql://openkms:your-database-password@postgres:5432/openkms
REDIS_URL=redis://redis:6379/0
DOMAIN_NAME=your-domain.com
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
FRONTEND_URL=https://your-domain.com
```

#### `.env.development`
```bash
DEBUG=True
LOG_LEVEL=DEBUG
SECRET_KEY=development-secret-key
POSTGRES_PASSWORD=dev_password
DATABASE_URL=postgresql://openkms:dev_password@postgres:5432/openkms
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:8080
```

### Security Configuration

#### Generate Secure Secret Key
```bash
# Generate secure JWT secret
openssl rand -hex 32
```

#### Database Security
```bash
# Use strong passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Use SSL for database connections in production
DATABASE_URL=postgresql://openkms:password@postgres:5432/openkms?sslmode=require
```

## SSL/TLS Configuration

### Let's Encrypt Setup

1. **Install Certbot**
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Generate Certificate**
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

3. **Auto-renewal**
```bash
sudo certbot renew --dry-run
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Self-Signed Certificate (Development)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_trusted_certificate /etc/nginx/ssl/chain.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:50m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
}
```

## Database Setup

### Database Migration

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Downgrade migration
docker-compose exec backend alembic downgrade -1
```

### Database Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U openkms openkms > backup.sql

# Backup with compression
docker-compose exec postgres pg_dump -U openkms openkms | gzip > backup.sql.gz

# Scheduled backup (cron)
0 2 * * * docker-compose exec postgres pg_dump -U openkms openkms | gzip > /backups/openkms-$(date +\%Y\%m\%d).sql.gz
```

### Database Restore

```bash
# Restore database
docker-compose exec -T postgres psql -U openkms openkms < backup.sql

# Restore from compressed backup
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U openkms openkms
```

### Database Maintenance

```bash
# Vacuum and analyze
docker-compose exec postgres psql -U openkms openkms -c "VACUUM ANALYZE;"

# Reindex database
docker-compose exec postgres psql -U openkms openkms -c "REINDEX DATABASE openkms;"

# Check database size
docker-compose exec postgres psql -U openkms openkms -c "SELECT pg_size_pretty(pg_database_size('openkms'));"
```

## Monitoring and Logging

### Health Checks

```bash
# Check all services health
docker-compose ps

# Backend health check
curl http://localhost:8000/api/v1/health

# Frontend health check
curl http://localhost:8080/health
```

### Log Management

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View logs from last hour
docker-compose logs --since 1h -f backend

# Export logs
docker-compose logs backend > backend.log
```

### Monitoring Setup

#### Prometheus Integration
```yaml
# Add to docker-compose.prod.yml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'

grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

#### Application Metrics

Backend exposes metrics at `/metrics` endpoint:
```bash
curl http://localhost:8000/metrics
```

### Performance Monitoring

```bash
# Monitor resource usage
docker stats

# Monitor specific container
docker stats openkms-backend

# Monitor network usage
docker network inspect openkms_openkms-network
```

## Backup and Recovery

### Full System Backup

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/openkms-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup database
docker-compose exec postgres pg_dump -U openkms openkms > "$BACKUP_DIR/database.sql"

# Backup uploads
docker cp openkms-data:/app/uploads "$BACKUP_DIR/uploads"

# Backup configuration
cp .env "$BACKUP_DIR/"

# Compress backup
tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"
rm -rf "$BACKUP_DIR"
```

### System Recovery

```bash
#!/bin/bash
# restore.sh
BACKUP_FILE="$1"

# Extract backup
tar -xzf "$BACKUP_FILE"
BACKUP_DIR="${BACKUP_FILE%.tar.gz}"

# Restore database
docker-compose exec -T postgres psql -U openkms openkms < "$BACKUP_DIR/database.sql"

# Restore uploads
docker cp "$BACKUP_DIR/uploads" openkms-data:/app/

# Restore configuration
cp "$BACKUP_DIR/.env" ./

# Restart services
docker-compose restart
```

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check port usage
sudo lsof -i :8000
sudo lsof -i :8080
sudo lsof -i :5432
sudo lsof -i :6379

# Kill conflicting processes
sudo kill -9 <PID>
```

#### Container Issues
```bash
# Rebuild containers
docker-compose build --no-cache

# Clean restart
docker-compose down
docker-compose up -d

# Clear container logs
docker-compose logs -f backend --tail=0
```

#### Database Connection Issues
```bash
# Check database connectivity
docker-compose exec postgres psql -U openkms openkms -c "SELECT 1;"

# Check database logs
docker-compose logs postgres

# Reset database connection
docker-compose restart postgres
```

#### Memory Issues
```bash
# Check memory usage
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}"

# Increase memory limits (docker-compose.prod.yml)
deploy:
  resources:
    limits:
      memory: 2G
```

### Debug Commands

```bash
# Access container shell
docker-compose exec backend bash
docker-compose exec frontend bash
docker-compose exec postgres bash

# Check container configuration
docker-compose config

# Check network configuration
docker network inspect openkms_openkms-network

# Check volume configuration
docker volume inspect openkms_postgres_data
```

### Performance Issues

```bash
# Monitor database performance
docker-compose exec postgres psql -U openkms openkms -c "SELECT * FROM pg_stat_activity;"

# Check slow queries
docker-compose exec postgres psql -U openkms openkms -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Monitor backend performance
curl http://localhost:8000/metrics
```

## Security Considerations

### Container Security

```bash
# Regular security updates
docker-compose pull
docker-compose up -d --force-recreate

# Scan images for vulnerabilities
docker scan openkms-backend
docker scan openkms-frontend

# Use non-root users in containers
# Already configured in Dockerfiles
```

### Network Security

```bash
# Firewall configuration
sudo ufw enable
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# Network isolation
docker network create --internal openkms-internal
```

### Application Security

```bash
# Regular secret rotation
openssl rand -hex 32  # Generate new secret key

# Security headers audit
curl -I https://your-domain.com

# CORS configuration validation
curl -X OPTIONS https://your-domain.com/api/v1/auth/login -H "Origin: https://your-domain.com"
```

### Database Security

```bash
# Regular password updates
docker-compose exec postgres psql -U openkms openkms -c "ALTER USER openkms PASSWORD 'new-password';"

# Database encryption
# Use TLS for database connections
DATABASE_URL=postgresql://openkms:password@postgres:5432/openkms?sslmode=require

# Regular database backups
# Setup automated backups as described in Backup section
```

### Security Auditing

```bash
# Audit container images
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# Audit running containers
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# Audit network connections
docker network ls
docker network inspect openkms_openkms-network
```

## Conclusion

This deployment guide provides a comprehensive overview of deploying and managing OpenKMS in various environments. Remember to:

1. Always use secure passwords and keys in production
2. Regularly update containers and dependencies
3. Implement proper backup and recovery procedures
4. Monitor system performance and security
5. Follow security best practices

For additional support or questions, please refer to the project documentation or contact the development team.