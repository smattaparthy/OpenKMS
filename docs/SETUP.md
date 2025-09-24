# OpenKMS Quick Setup Guide

## 🚀 Overview

This guide provides step-by-step instructions to get OpenKMS up and running quickly. Whether you're setting up for development, testing, or production, this guide will help you get started efficiently.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Memory**: Minimum 4GB RAM, 8GB+ recommended
- **Storage**: Minimum 20GB free space
- **Network**: Internet connection for downloading dependencies

### Required Software
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: Version 2.0 or higher
- **Curl**: For API testing (optional)

### Verification Commands
```bash
# Check Docker installation
docker --version
docker-compose --version

# Check Git installation
git --version

# Verify Docker is running
docker info
```

---

## 🛠️ Quick Start Guide

### Step 1: Clone Repository
```bash
# Clone the repository
git clone https://github.com/your-org/openkms.git

# Navigate to project directory
cd openkms

# Verify project structure
ls -la
```

#### Expected Directory Structure
```
openkms/
├── README.md                    # Main project documentation
├── README.DEVELOPMENT.md        # Development guide
├── DEPLOYMENT.md               # Deployment guide
├── docker-compose.yml         # Development configuration
├── docker-compose.prod.yml    # Production configuration
├── .env.example               # Environment variables template
├── scripts/                   # Setup and management scripts
├── openkms-backend/           # Python FastAPI backend
├── openkms-frontend/          # .NET Blazor frontend
├── nginx/                     # Nginx configuration
└── docs/                      # Documentation
```

### Step 2: Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables (optional for development)
# nano .env  # or your preferred editor
```

#### Environment Variables
```bash
# .env file - Development configuration
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql+asyncpg://openkms:your_secure_password@postgres:5432/openkms
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-super-secret-jwt-key-change-in-production
FRONTEND_URL=http://localhost:8080
BACKEND_URL=http://localhost:8000
```

### Step 3: Initial Setup
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Check system compatibility
./scripts/check-environment.sh

# If checks pass, run initial setup
./scripts/dev-setup.sh
```

#### Environment Check Script Output
```
✓ Docker version 20.10+ found
✓ Docker Compose version 2.0+ found
✓ Git version 2.0+ found
✓ Port 5432 (PostgreSQL) is available
✓ Port 6379 (Redis) is available
✓ Port 8000 (Backend) is available
✓ Port 8080 (Frontend) is available
✓ System meets all requirements
```

### Step 4: Start Application
```bash
# Start all services
./scripts/dev-commands.sh start

# Or use Docker Compose directly
docker-compose up -d
```

#### Service Startup Sequence
```
Starting OpenKMS services...
✓ Starting PostgreSQL database...
✓ Starting Redis cache...
✓ Starting Backend API...
✓ Starting Frontend application...
✓ Starting Nginx reverse proxy...
All services started successfully!
```

### Step 5: Verify Installation
```bash
# Check service status
./scripts/dev-commands.sh status

# Check service health
curl -f http://localhost:8080 && echo "✓ Frontend is running"
curl -f http://localhost:8000 && echo "✓ Backend is running"
curl -f http://localhost:8000/health && echo "✓ Backend health check passed"
```

#### Expected Output
```
OpenKMS Service Status:
┌─────────────────┬──────────────────┬─────────────────┐
│    Service      │     Status       │      Ports      │
├─────────────────┼──────────────────┼─────────────────┤
│      postgres    │      healthy     │     5432        │
│       redis      │      healthy     │     6379        │
│      backend     │      healthy     │     8000        │
│     frontend     │      healthy     │     8080        │
│      nginx       │      healthy     │ 80, 443        │
└─────────────────┴──────────────────┴─────────────────┘
```

### Step 6: Access Application
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Alternative Docs**: http://localhost:8000/redoc

---

## 🔧 Development Setup

### Development Environment
```bash
# Start development environment with hot reload
./scripts/dev-commands.sh start

# View live logs
./scripts/dev-commands.sh logs
./scripts/dev-commands.sh logs-backend
./scripts/dev-commands.sh logs-frontend

# Restart specific services
./scripts/dev-commands.sh restart backend
./scripts/dev-commands.sh restart frontend
```

### Development Tools
```bash
# Access service shells
./scripts/dev-commands.sh shell-backend    # Python shell
./scripts/dev-commands.sh shell-frontend   # .NET shell
./scripts/dev-commands.sh shell-db         # PostgreSQL shell

# Database operations
./scripts/dev-commands.sh migrate          # Run migrations
./scripts/dev-commands.sh migrate-new      # Create new migration
./scripts/dev-commands.sh backup           # Create backup
./scripts/dev-commands.sh restore          # Restore backup

# Testing
./scripts/dev-commands.sh test-backend
./scripts/dev-commands.sh test-frontend
```

### IDE Setup
#### Visual Studio Code
```bash
# Recommended VS Code extensions
- Docker
- Python
- C#
- PostgreSQL
- Redis
- Remote - Containers
```

#### VS Code Workspace Configuration
Create `.vscode/settings.json`:
```json
{
    "docker.composeFile": "docker-compose.yml",
    "python.autoComplete.extraPaths": [
        "./openkms-backend/app"
    ],
    "python.analysis.extraPaths": [
        "./openkms-backend/app"
    ],
    "omnisharp.path": "./openkms-frontend",
    "dotnet.server.useOmnisharp": true
}
```

---

## 🚀 Production Setup

### Production Preparation
```bash
# 1. Prepare production environment variables
cp .env.example .env.production
# Edit production values in .env.production

# 2. Use production docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### Production Configuration
```bash
# .env.production
POSTGRES_PASSWORD=your_production_secure_password
DATABASE_URL=postgresql+asyncpg://openkms:your_prod_password@postgres:5432/openkms
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-production-super-secret-key-min-32-chars
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://api.your-domain.com
DEBUG=False
LOG_LEVEL=INFO
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### Production Deployment
```bash
# Deploy with production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

### SSL/TLS Setup
```bash
# Generate SSL certificates (Let's Encrypt)
./scripts/setup-ssl.sh your-domain.com

# Or manually configure SSL in nginx/ssl/
# Place your certificate files:
# - nginx/ssl/cert.pem
# - nginx/ssl/key.pem

# Enable SSL profile
docker-compose --profile proxy up -d
```

---

## 🐛 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check port usage
lsof -i :8000  # Backend port
lsof -i :8080  # Frontend port
lsof -i :5432  # PostgreSQL port
lsof -i :6379  # Redis port

# Kill conflicting processes
kill -9 <PID>

# Or modify ports in .env file
```

#### Docker Issues
```bash
# Clean up Docker system
docker system prune -a
docker volume prune

# Rebuild containers
./scripts/dev-commands.sh rebuild

# Reset to clean state
./scripts/dev-commands.sh clean
./scripts/dev-commands.sh start
```

#### Database Issues
```bash
# Reset database connection
./scripts/dev-commands.sh restart db

# Check database logs
./scripts/dev-commands.sh logs-db

# Manual database reset (WARNING: destroys data)
docker-compose down -v
docker-compose up -d
```

#### Build Issues
```bash
# Clear build cache
docker builder prune

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Check build logs
docker-compose logs --tail=50 backend
docker-compose logs --tail=50 frontend
```

### Health Checks

#### Service Health Commands
```bash
# Overall service status
docker-compose ps

# Individual service health
docker exec openkms-backend curl -f http://localhost:8000/health
docker exec openkms-postgres pg_isready -U openkms
docker exec openkms-redis redis-cli ping

# Container resource usage
docker stats
```

#### Database Health
```bash
# Access database shell
./scripts/dev-commands.sh shell-db

# Check database connections
SELECT count(*) FROM pg_stat_activity;

# Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### Application Logs
```bash
# Backend logs
docker-compose logs --tail=100 backend
docker-compose logs --follow backend

# Frontend logs
docker-compose logs --tail=100 frontend
docker-compose logs --follow frontend

# Database logs
docker-compose logs --tail=50 postgres

# All services logs
docker-compose logs --tail=50
```

---

## 🔄 Maintenance

### Regular Maintenance Tasks
```bash
# Daily: Check service health
./scripts/dev-commands.sh status

# Weekly: Create database backup
./scripts/dev-commands.sh backup

# Monthly: Clean up logs and temporary files
docker system prune -f
docker volume prune -f

# Quarterly: Update dependencies
./scripts/update-dependencies.sh
```

### Database Maintenance
```bash
# Create backup
./scripts/dev-commands.sh backup

# Restore backup
./scripts/dev-commands.sh restore /path/to/backup.sql

# Database migrations
./scripts/dev-commands.sh migrate

# Run custom maintenance queries
./scripts/dev-commands.sh shell-db
# Then execute SQL queries
```

### Service Updates
```bash
# Update Docker images
docker-compose pull

# Update specific service
docker-compose pull backend frontend

# Rebuild and restart
docker-compose up -d --force-recreate

# Clean up old images
docker image prune -f
```

---

## 📊 Monitoring

### Basic Monitoring
```bash
# Service monitoring
docker stats

# Resource usage
docker exec openkms-backend top
docker exec openkms-frontend top

# Application metrics
curl http://localhost:8000/metrics

# Health check endpoint
curl http://localhost:8000/health
```

### Log Analysis
```bash
# Tail all logs
docker-compose logs --tail=100

# Filter by service
docker-compose logs --tail=50 backend

# Search logs (requires external tools)
docker-compose logs | grep "ERROR"

# Export logs for analysis
docker-compose logs > application-logs-$(date +%Y%m%d).log
```

---

## 🔒 Security Setup

### Initial Security Configuration
```bash
# 1. Generate secure secrets
openssl rand -hex 32  # For JWT secret key
openssl rand -hex 16  # For database password

# 2. Set strong passwords in .env
POSTGRES_PASSWORD=your-very-secure-random-password
SECRET_KEY=your-very-secure-32-character-jwt-secret-key

# 3. Restart services with secure configuration
./scripts/dev-commands.sh restart
```

### SSL/TLS Configuration
```bash
# Generate self-signed certificate (for development)
openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes

# Or use Let's Encrypt for production
./scripts/setup-letsencrypt.sh your-domain.com
```

### Firewall Configuration
```bash
# Linux example with ufw
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

---

## 🚀 Performance Optimization

### Development Performance
```bash
# Increase Docker memory allocation (macOS/Windows)
# Docker Desktop settings → Resources → Memory → 4GB+

# Use volume mounts for hot reload
docker-compose up --build

# Optimize Docker build cache
docker-compose build --no-cache
```

### Production Performance
```bash
# Scale services
docker-compose up -d --scale backend=3 --scale frontend=2

# Optimized Docker Compose for production
docker-compose -f docker-compose.prod.yml up -d

# Monitor performance
docker stats
```

---

## 📝 Quick Reference

### Essential Commands
```bash
# Start/Stop
./scripts/dev-commands.sh start    # Start all services
./scripts/dev-commands.sh stop     # Stop all services
./scripts/dev-commands.sh restart  # Restart all services
./scripts/dev-commands.sh status   # Check service status

# Development
./scripts/dev-commands.sh logs     # View all logs
./scripts/dev-commands.sh shell-backend  # Access backend
./scripts/dev-commands.sh shell-frontend # Access frontend

# Database
./scripts/dev-commands.sh migrate  # Run migrations
./scripts/dev-commands.sh backup   # Create backup
./scripts/dev-commands.sh restore  # Restore backup
```

### File Locations
```bash
# Configuration files
.env                    # Environment variables
docker-compose.yml      # Dev configuration
docker-compose.prod.yml # Production configuration

# Application code
openkms-backend/        # Python backend
openkms-frontend/       # .NET frontend

# Documentation
README.md               # Project overview
docs/                   # Complete documentation
```

### URLs and Ports
```bash
# Local development
Frontend:     http://localhost:8080
Backend API:  http://localhost:8000
API Docs:     http://localhost:8000/docs
Database:     localhost:5432
Redis:        localhost:6379

# Production (with SSL)
Frontend:     https://your-domain.com
Backend API:  https://api.your-domain.com
API Docs:     https://api.your-domain.com/docs
```

---

## 🆘 Getting Help

### Documentation Resources
- **Main Documentation**: [README.md](../README.md)
- **Development Guide**: [README.DEVELOPMENT.md](../README.DEVELOPMENT.md)
- **Deployment Guide**: [DEPLOYMENT.md](../DEPLOYMENT.md)
- **API Documentation**: [docs/API.md](docs/API.md)
- **Component Docs**: [docs/COMPONENTS.md](docs/COMPONENTS.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

### Troubleshooting Resources
- **Common Issues**: See Troubleshooting section above
- **Service Logs**: `docker-compose logs <service>`
- **Health Checks**: `docker-compose ps`, `curl /health`
- **Community**: [GitHub Discussions](https://github.com/your-org/openkms/discussions)
- **Issues**: [GitHub Issues](https://github.com/your-org/openkms/issues)

### Support Contact
- **Documentation Issues**: Submit GitHub issue with `documentation` label
- **Bug Reports**: Submit GitHub issue with `bug` label
- **Feature Requests**: Submit GitHub issue with `enhancement` label
- **Enterprise Support**: contact@openkms.com

---

## 🎉 Success!

You now have OpenKMS up and running! Here's what to do next:

### First Steps
1. **Access the Application**: Visit http://localhost:8080
2. **Explore the API**: Browse http://localhost:8000/docs
3. **Create an Account**: Use the registration form
4. **Try Admin Features**: Create admin user and explore dashboard

### Learning Resources
- **API Integration**: Read [API Documentation](docs/API.md)
- **Component Development**: See [Component Documentation](docs/COMPONENTS.md)
- **System Architecture**: Review [Architecture Guide](docs/ARCHITECTURE.md)
- **Development Workflow**: Follow [Development Guide](README.DEVELOPMENT.md)

### Next Steps
- **Customization**: Modify components and add features
- **Integration**: Connect to your existing systems
- **Deployment**: Prepare for production deployment
- **Monitoring**: Set up monitoring and alerting

---

*Happy coding! 🚀*

**Last updated**: December 1, 2023