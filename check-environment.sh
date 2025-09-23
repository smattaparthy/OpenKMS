#!/bin/bash

# OpenKMS Environment Check Script
# This script checks if the development environment is properly configured

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

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
is_port_available() {
    ! nc -z localhost "$1" >/dev/null 2>&1
}

# Function to check if Docker is running
is_docker_running() {
    docker info >/dev/null 2>&1
}

# Function to check Docker containers
check_containers() {
    local containers=("openkms-postgres" "openkms-redis" "openkms-backend" "openkms-frontend")
    local all_running=true

    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "$container"; then
            print_status "$container is running"
        else
            print_error "$container is not running"
            all_running=false
        fi
    done

    if [ "$all_running" = false ]; then
        print_warning "Some containers are not running. Run './scripts/dev-commands.sh start' to start them."
    fi
}

# Main check process
main() {
    echo "🔍 OpenKMS Environment Check"
    echo "============================="
    echo

    # Check prerequisites
    print_info "Checking prerequisites..."

    # Check Docker
    if command_exists docker; then
        print_status "Docker is installed"

        # Check Docker version
        docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_info "   Docker version: $docker_version"
    else
        print_error "Docker is not installed"
        echo "   Install Docker: https://docs.docker.com/get-docker/"
    fi

    # Check Docker Compose
    if command_exists docker-compose; then
        print_status "Docker Compose is installed"

        # Check Docker Compose version
        compose_version=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        print_info "   Docker Compose version: $compose_version"
    else
        print_error "Docker Compose is not installed"
        echo "   Install Docker Compose: https://docs.docker.com/compose/install/"
    fi

    # Check if Docker is running
    if is_docker_running; then
        print_status "Docker is running"
    else
        print_error "Docker is not running"
        echo "   Start Docker Desktop or Docker service"
    fi

    # Check Git
    if command_exists git; then
        print_status "Git is installed"

        # Check Git version
        git_version=$(git --version | cut -d' ' -f3)
        print_info "   Git version: $git_version"
    else
        print_error "Git is not installed"
        echo "   Install Git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git"
    fi

    # Check OpenSSL
    if command_exists openssl; then
        print_status "OpenSSL is installed"

        # Check OpenSSL version
        openssl_version=$(openssl version | cut -d' ' -f2)
        print_info "   OpenSSL version: $openssl_version"
    else
        print_warning "OpenSSL is not installed. Some features may not work."
    fi

    echo

    # Check required ports
    print_info "Checking port availability..."

    local ports=(5432 6379 8000 8080)
    for port in "${ports[@]}"; do
        if is_port_available "$port"; then
            print_status "Port $port is available"
        else
            print_warning "Port $port is in use"
        fi
    done

    echo

    # Check environment file
    print_info "Checking environment configuration..."

    if [ -f .env ]; then
        print_status "Environment file (.env) exists"

        # Check required environment variables
        local required_vars=("POSTGRES_PASSWORD" "SECRET_KEY" "DATABASE_URL" "REDIS_URL")
        for var in "${required_vars[@]}"; do
            if grep -q "^$var=" .env; then
                print_status "   $var is set"
            else
                print_error "   $var is not set"
            fi
        done
    else
        print_error "Environment file (.env) does not exist"
        echo "   Run './scripts/dev-setup.sh' to create it"
    fi

    echo

    # Check Docker containers (if Docker is running)
    if is_docker_running; then
        print_info "Checking Docker containers..."
        check_containers
    fi

    echo

    # Check services health (if containers are running)
    if docker ps --format "table {{.Names}}" | grep -q "openkms-backend"; then
        print_info "Checking service health..."

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
    fi

    echo

    # Print summary
    print_info "Environment Check Summary:"
    echo "=========================="
    echo ""

    # Count issues
    local issue_count=0

    if ! command_exists docker; then
        echo "❌ Docker is not installed"
        ((issue_count++))
    fi

    if ! command_exists docker-compose; then
        echo "❌ Docker Compose is not installed"
        ((issue_count++))
    fi

    if ! is_docker_running; then
        echo "❌ Docker is not running"
        ((issue_count++))
    fi

    if [ ! -f .env ]; then
        echo "❌ Environment file does not exist"
        ((issue_count++))
    fi

    if [ $issue_count -eq 0 ]; then
        print_status "✅ All checks passed! Environment is ready."
        echo ""
        echo "Next steps:"
        echo "1. Run './scripts/dev-setup.sh' to set up the environment (first time)"
        echo "2. Run './scripts/dev-commands.sh start' to start services"
        echo "3. Access the application at http://localhost:8080"
    else
        print_warning "⚠️  Found $issue_count issue(s). Please fix them before proceeding."
        echo ""
        echo "To fix issues:"
        echo "1. Install missing dependencies"
        echo "2. Start Docker"
        echo "3. Run './scripts/dev-setup.sh' to set up the environment"
        echo "4. Run './scripts/dev-commands.sh start' to start services"
    fi
}

# Run main function
main "$@"