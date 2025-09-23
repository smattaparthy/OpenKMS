#!/bin/bash

# OpenKMS Development Setup Script
# This script sets up a complete development environment for OpenKMS

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Docker is running
is_docker_running() {
    docker info >/dev/null 2>&1
}

# Function to create .env file from template
create_env_file() {
    if [ ! -f .env ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env

        # Generate random passwords and secrets
        DB_PASSWORD=$(openssl rand -base64 32 | tr -d '/')
        SECRET_KEY=$(openssl rand -hex 32)

        # Update .env with generated values
        sed -i.bak "s/your-secure-database-password-here/${DB_PASSWORD}/g" .env
        sed -i.bak "s/your-very-secure-secret-key-change-this-in-production/${SECRET_KEY}/g" .env

        # Set development values
        sed -i.bak 's/DEBUG=False/DEBUG=True/g' .env
        sed -i.bak 's/LOG_LEVEL=INFO/LOG_LEVEL=DEBUG/g' .env
        sed -i.bak 's/your-domain.com/localhost/g' .env

        rm .env.bak
        print_status "Environment file created successfully"
    else
        print_warning ".env file already exists"
    fi
}

# Main setup process
main() {
    echo "🚀 OpenKMS Development Environment Setup"
    echo "=========================================="
    echo

    # Check prerequisites
    print_info "Checking prerequisites..."

    # Check Docker
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_status "Docker is installed"

    # Check Docker Compose
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_status "Docker Compose is installed"

    # Check if Docker is running
    if ! is_docker_running; then
        print_error "Docker is not running. Please start Docker Desktop or Docker service."
        exit 1
    fi
    print_status "Docker is running"

    # Check Git
    if ! command_exists git; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    print_status "Git is installed"

    # Check OpenSSL
    if ! command_exists openssl; then
        print_warning "OpenSSL is not installed. Some features may not work."
    else
        print_status "OpenSSL is installed"
    fi

    echo

    # Create environment file
    create_env_file

    echo

    # Create necessary directories
    print_info "Creating necessary directories..."
    mkdir -p logs uploads nginx/ssl
    print_status "Directories created"

    echo

    # Build and start containers
    print_info "Building and starting containers..."
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml down
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml build --no-cache
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml up -d

    # Wait for services to be ready
    print_info "Waiting for services to be ready..."
    sleep 30

    # Run database migrations
    print_info "Running database migrations..."
    docker-compose exec -T backend alembic upgrade head || {
        print_warning "Database migration failed, but continuing..."
    }

    echo

    # Health checks
    print_info "Performing health checks..."

    # Check backend health
    if curl -f http://localhost:8000/api/v1/health >/dev/null 2>&1; then
        print_status "Backend is healthy"
    else
        print_error "Backend is not responding"
    fi

    # Check frontend health
    if curl -f http://localhost:8080/health >/dev/null 2>&1; then
        print_status "Frontend is healthy"
    else
        print_error "Frontend is not responding"
    fi

    # Check database health
    if docker-compose exec -T postgres pg_isready -U openkms >/dev/null 2>&1; then
        print_status "Database is healthy"
    else
        print_error "Database is not responding"
    fi

    # Check Redis health
    if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        print_status "Redis is healthy"
    else
        print_error "Redis is not responding"
    fi

    echo

    # Display access information
    print_info "🎉 Development environment setup completed!"
    echo
    echo "Access URLs:"
    echo "┌─────────────────────┬─────────────────────────────────┐"
    echo "│ Service            │ URL                             │"
    echo "├─────────────────────┼─────────────────────────────────┤"
    echo "│ Frontend           │ http://localhost:8080           │"
    echo "│ Backend API        │ http://localhost:8000           │"
    echo "│ API Docs           │ http://localhost:8000/docs      │"
    echo "│ Admin Docs         │ http://localhost:8000/redoc     │"
    echo "└─────────────────────┴─────────────────────────────────┘"
    echo
    echo "Default Login Credentials:"
    echo "┌─────────────┬──────────────────┬─────────────┐"
    echo "│ Username    │ Password         │ Role        │"
    echo "├─────────────┼──────────────────┼─────────────┤"
    echo "│ admin       │ password123      │ Admin       │"
    echo "│ michael     │ password123      │ Manager     │"
    echo "│ emma       │ password123      │ Employee    │"
    echo "└─────────────┴──────────────────┴─────────────┘"
    echo
    echo "Development Commands:"
    echo "┌─────────────────────────────────┬─────────────────────────────────┐"
    echo "│ Command                         │ Description                     │"
    echo "├─────────────────────────────────┼─────────────────────────────────┤"
    echo "│ docker-compose up -d            │ Start all services              │"
    echo "│ docker-compose down             │ Stop all services               │"
    echo "│ docker-compose logs -f backend  │ View backend logs                │"
    echo "│ docker-compose logs -f frontend │ View frontend logs               │"
    echo "│ docker-compose exec backend bash│ Access backend shell            │"
    echo "│ docker-compose exec frontend bash│ Access frontend shell           │"
    echo "│ docker-compose restart backend  │ Restart backend service         │"
    echo "│ docker-compose restart frontend │ Restart frontend service        │"
    echo "└─────────────────────────────────┴─────────────────────────────────┘"
    echo
    print_warning "Note: This setup is for development purposes only. Do not use in production!"
    print_status "Setup completed successfully! 🚀"
}

# Run main function
main "$@"