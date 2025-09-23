#!/bin/bash

# OpenKMS Development Commands Script
# Convenience script for common development tasks

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_command() {
    echo -e "${CYAN}🔧 $1${NC}"
}

# Function to show help
show_help() {
    echo "OpenKMS Development Commands"
    echo "=============================="
    echo
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "┌─────────────────┬─────────────────────────────────────────────────────────────┐"
    echo "│ Command         │ Description                                                 │"
    echo "├─────────────────┼─────────────────────────────────────────────────────────────┤"
    echo "│ setup           │ Set up development environment (first time setup)           │"
    echo "│ start           │ Start all services                                         │"
    echo "│ stop            │ Stop all services                                          │"
    echo "│ restart         │ Restart all services                                       │"
    echo "│ status          │ Show service status                                        │"
    echo "│ logs            │ Show logs for all services                                 │"
    echo "│ logs-backend    │ Show backend logs only                                     │"
    echo "│ logs-frontend   │ Show frontend logs only                                    │"
    echo "│ logs-db         │ Show database logs only                                    │"
    echo "│ shell-backend   │ Access backend shell                                       │"
    echo "│ shell-frontend  │ Access frontend shell                                      │"
    echo "│ shell-db        │ Access database shell                                      │"
    echo "│ test-backend    │ Run backend tests                                          │"
    echo "│ test-frontend   │ Run frontend tests                                         │"
    echo "│ test-all        │ Run all tests                                              │"
    echo "│ migrate         │ Run database migrations                                    │"
    echo "│ migrate-new     │ Create new database migration                              │"
    echo "│ backup          │ Backup database and uploads                                │"
    echo "│ restore         │ Restore from backup                                       │"
    echo "│ clean           │ Clean up containers and volumes                           │"
    echo "│ rebuild         │ Rebuild all containers                                    │"
    echo "│ update          │ Update dependencies and rebuild                           │"
    echo "│ help            │ Show this help message                                    │"
    echo "└─────────────────┴─────────────────────────────────────────────────────────────┘"
    echo
    echo "Examples:"
    echo "  $0 logs-backend    # Show backend logs"
    echo "  $0 test-backend    # Run backend tests"
    echo "  $0 migrate         # Run database migrations"
    echo
}

# Function to setup environment
setup_environment() {
    print_info "Setting up development environment..."
    ./scripts/dev-setup.sh
}

# Function to start services
start_services() {
    print_info "Starting all services..."
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml up -d
    print_status "Services started successfully"
}

# Function to stop services
stop_services() {
    print_info "Stopping all services..."
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml down
    print_status "Services stopped successfully"
}

# Function to restart services
restart_services() {
    print_info "Restarting all services..."
    stop_services
    sleep 3
    start_services
}

# Function to show service status
show_status() {
    print_info "Service Status:"
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml ps
}

# Function to show logs
show_logs() {
    local service="$1"
    case "$service" in
        "backend")
            print_info "Showing backend logs..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml logs -f backend
            ;;
        "frontend")
            print_info "Showing frontend logs..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml logs -f frontend
            ;;
        "db")
            print_info "Showing database logs..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml logs -f postgres
            ;;
        *)
            print_info "Showing all logs..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml logs -f
            ;;
    esac
}

# Function to access shell
access_shell() {
    local service="$1"
    case "$service" in
        "backend")
            print_info "Accessing backend shell..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec backend bash
            ;;
        "frontend")
            print_info "Accessing frontend shell..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec frontend bash
            ;;
        "db")
            print_info "Accessing database shell..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec postgres psql -U openkms openkms
            ;;
        *)
            print_error "Invalid service. Use: backend, frontend, or db"
            exit 1
            ;;
    esac
}

# Function to run tests
run_tests() {
    local service="$1"
    case "$service" in
        "backend")
            print_info "Running backend tests..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec backend pytest -v
            ;;
        "frontend")
            print_info "Running frontend tests..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec frontend dotnet test --verbosity normal
            ;;
        "all")
            print_info "Running all tests..."
            echo "Running backend tests..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec backend pytest -v
            echo "Running frontend tests..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec frontend dotnet test --verbosity normal
            ;;
        *)
            print_error "Invalid service. Use: backend, frontend, or all"
            exit 1
            ;;
    esac
}

# Function to run database migrations
run_migrations() {
    local action="$1"
    case "$action" in
        "up")
            print_info "Running database migrations..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec backend alembic upgrade head
            ;;
        "down")
            print_info "Rolling back database migrations..."
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec backend alembic downgrade -1
            ;;
        "new")
            print_info "Creating new database migration..."
            echo "Enter migration description:"
            read -r description
            docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec backend alembic revision --autogenerate -m "$description"
            ;;
        *)
            print_error "Invalid action. Use: up, down, or new"
            exit 1
            ;;
    esac
}

# Function to backup database
backup_data() {
    print_info "Creating backup..."
    local backup_dir="./backups"
    mkdir -p "$backup_dir"
    local backup_file="$backup_dir/openkms-backup-$(date +%Y%m%d_%H%M%S).sql"

    # Backup database
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec -T postgres pg_dump -U openkms openkms > "$backup_file"

    # Backup uploads
    local uploads_backup="$backup_dir/uploads-$(date +%Y%m%d_%H%M%S)"
    docker cp openkms-backend:/app/uploads "$uploads_backup"

    print_status "Backup created successfully"
    print_info "Database backup: $backup_file"
    print_info "Uploads backup: $uploads_backup"
}

# Function to restore from backup
restore_data() {
    if [ -z "$1" ]; then
        print_error "Please provide backup file path"
        exit 1
    fi

    local backup_file="$1"
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi

    print_warning "This will restore the database from backup. All current data will be lost."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi

    print_info "Restoring from backup: $backup_file"
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec -T postgres psql -U openkms openkms < "$backup_file"
    print_status "Database restored successfully"
}

# Function to clean up
cleanup() {
    print_warning "This will stop all containers and remove all volumes. All data will be lost."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi

    print_info "Cleaning up..."
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml down -v
    docker system prune -f
    print_status "Cleanup completed"
}

# Function to rebuild containers
rebuild_containers() {
    print_info "Rebuilding all containers..."
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml down
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml build --no-cache
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml up -d
    print_status "Containers rebuilt successfully"
}

# Function to update dependencies
update_dependencies() {
    print_info "Updating dependencies..."

    # Update backend dependencies
    print_info "Updating backend dependencies..."
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec backend pip install --upgrade -r requirements.txt

    # Update frontend dependencies
    print_info "Updating frontend dependencies..."
    docker-compose --env-file .env -f docker-compose.yml -f docker-compose.override.yml exec frontend dotnet restore

    # Rebuild containers
    rebuild_containers
}

# Main script logic
case "$1" in
    setup)
        setup_environment
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    logs-backend)
        show_logs "backend"
        ;;
    logs-frontend)
        show_logs "frontend"
        ;;
    logs-db)
        show_logs "db"
        ;;
    shell-backend)
        access_shell "backend"
        ;;
    shell-frontend)
        access_shell "frontend"
        ;;
    shell-db)
        access_shell "db"
        ;;
    test-backend)
        run_tests "backend"
        ;;
    test-frontend)
        run_tests "frontend"
        ;;
    test-all)
        run_tests "all"
        ;;
    migrate)
        run_migrations "up"
        ;;
    migrate-down)
        run_migrations "down"
        ;;
    migrate-new)
        run_migrations "new"
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data "$2"
        ;;
    clean)
        cleanup
        ;;
    rebuild)
        rebuild_containers
        ;;
    update)
        update_dependencies
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac