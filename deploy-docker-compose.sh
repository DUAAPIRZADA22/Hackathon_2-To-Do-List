#!/bin/bash

# ActionMindAI Docker Compose Deployment Script
# Cloud-native production deployment with health checks

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
REQUIRED_VARS=("DATABASE_URL" "OPENAI_API_KEY" "BETTER_AUTH_SECRET")

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    fi
    log_success "Docker is installed: $(docker --version)"

    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please update Docker Desktop."
        exit 1
    fi
    log_success "Docker Compose is available: $(docker compose version)"

    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker Desktop."
        exit 1
    fi
    log_success "Docker daemon is running"

    # Check available disk space
    local available_space=$(df -h . | tail -1 | awk '{print $4}')
    log_info "Available disk space: $available_space"
}

check_environment() {
    log_info "Checking environment configuration..."

    if [ ! -f "$ENV_FILE" ]; then
        log_warning ".env file not found. Creating from template..."
        if [ -f ".env.production" ]; then
            cp .env.production .env
            log_warning "Please edit .env with your actual values before deploying."
            log_warning "Required variables: DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET"
            read -p "Press Enter to open .env file in your editor..."
            ${EDITOR:-nano} .env
        else
            log_error ".env.production template not found. Cannot create .env file."
            exit 1
        fi
    fi

    # Source the .env file
    source .env

    # Check required variables
    local missing_vars=()
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var:-}" ] || [[ "${!var}" == *"your_"* ]] || [[ "${!var}" == *"CHANGE_THIS"* ]]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Missing or invalid environment variables:"
        printf '  - %s\n' "${missing_vars[@]}"
        log_error "Please edit .env file and set all required values."
        exit 1
    fi

    log_success "All required environment variables are configured"
}

check_images() {
    log_info "Checking Docker images..."

    local images_missing=false

    if ! docker image inspect ActionMindAI/frontend:1.0.0 &> /dev/null; then
        log_warning "Frontend image not found. Building..."
        docker build -t ActionMindAI/frontend:1.0.0 -f frontend/Dockerfile frontend/
        if [ $? -eq 0 ]; then
            log_success "Frontend image built successfully"
        else
            log_error "Failed to build frontend image"
            images_missing=true
        fi
    else
        log_success "Frontend image exists: ActionMindAI/frontend:1.0.0"
    fi

    if ! docker image inspect ActionMindAI/backend:1.0.0 &> /dev/null; then
        log_warning "Backend image not found. Building..."
        docker build -t ActionMindAI/backend:1.0.0 -f backend/Dockerfile backend/
        if [ $? -eq 0 ]; then
            log_success "Backend image built successfully"
        else
            log_error "Failed to build backend image"
            images_missing=true
        fi
    else
        log_success "Backend image exists: ActionMindAI/backend:1.0.0"
    fi

    if [ "$images_missing" = true ]; then
        exit 1
    fi
}

deploy_services() {
    log_info "Deploying services with Docker Compose..."

    docker compose -f "$COMPOSE_FILE" up -d

    if [ $? -eq 0 ]; then
        log_success "Services deployed successfully"
    else
        log_error "Failed to deploy services"
        exit 1
    fi
}

wait_for_health() {
    log_info "Waiting for services to become healthy..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts..."

        # Check backend health
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log_success "Backend is healthy"
        else
            log_warning "Backend not yet healthy..."
        fi

        # Check frontend health
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            log_success "Frontend is healthy"
        else
            log_warning "Frontend not yet healthy..."
        fi

        # Check if both are healthy
        if curl -s http://localhost:8000/health > /dev/null 2>&1 && curl -s http://localhost:3000 > /dev/null 2>&1; then
            log_success "All services are healthy!"
            return 0
        fi

        sleep 5
        ((attempt++))
    done

    log_warning "Health check timed out. Services may need more time."
    log_info "Check logs with: docker compose logs -f"
}

show_status() {
    log_info "Deployment status:"
    echo ""
    docker compose ps
    echo ""
    log_success "Access the application at:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    log_info "View logs with: docker compose logs -f"
    log_info "Stop services with: docker compose down"
}

# Main deployment flow
main() {
    echo ""
    echo "=========================================="
    echo "  ActionMindAI Docker Compose Deployment"
    echo "=========================================="
    echo ""

    check_prerequisites
    check_environment
    check_images
    deploy_services
    wait_for_health
    show_status

    echo ""
    log_success "Deployment complete! 🚀"
    echo ""
}

# Run main function
main "$@"
