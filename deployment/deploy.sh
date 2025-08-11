#!/bin/bash

# Enhanced Production Deployment Script for AWS EC2
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/home/ec2-user/helpdesk-crm"
BACKUP_DIR="/home/ec2-user/backups"
LOG_FILE="/home/ec2-user/helpdesk-deploy.log"
DEPLOY_DATE=$(date +"%Y%m%d_%H%M%S")

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Check if running as root
check_user() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as ec2-user or similar."
    fi
}

# Check system requirements
check_requirements() {
    log "🔍 Checking system requirements..."
    
    # Check available disk space (minimum 5GB)
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    if [[ $AVAILABLE_SPACE -lt 5242880 ]]; then
        error "Insufficient disk space. At least 5GB required."
    fi
    
    # Check memory (minimum 2GB)
    AVAILABLE_MEMORY=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [[ $AVAILABLE_MEMORY -lt 1024 ]]; then
        warn "Low available memory ($AVAILABLE_MEMORY MB). Recommended: 2GB+"
    fi
}

# Install system dependencies
install_dependencies() {
    log "📦 Installing system dependencies..."
    
    # Update system packages
    sudo yum update -y || error "Failed to update system packages"
    
    # Install essential packages
    sudo yum install -y git curl wget unzip htop || error "Failed to install essential packages"
    
    # Install Docker if not present
    if ! command -v docker &> /dev/null; then
        log "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh || error "Failed to install Docker"
        sudo usermod -aG docker $USER
        sudo systemctl start docker
        sudo systemctl enable docker
        rm -f get-docker.sh
        
        # Test Docker installation
        sudo docker run hello-world || error "Docker installation verification failed"
    else
        log "Docker is already installed"
    fi
    
    # Install Docker Compose if not present
    if ! command -v docker-compose &> /dev/null; then
        log "Installing Docker Compose..."
        DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*?(?=")')
        sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        
        # Test Docker Compose installation
        docker-compose --version || error "Docker Compose installation verification failed"
    else
        log "Docker Compose is already installed"
    fi
    
    # Install AWS CLI v2 if not present
    if ! command -v aws &> /dev/null; then
        log "Installing AWS CLI v2..."
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip -q awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
        
        # Verify AWS CLI installation
        aws --version || error "AWS CLI installation verification failed"
    else
        log "AWS CLI is already installed"
    fi
}

# Setup application directory
setup_app_directory() {
    log "📁 Setting up application directory..."
    
    # Create directories with proper permissions (no sudo needed for home directory)
    mkdir -p "$BACKUP_DIR" 
    chmod 755 "$BACKUP_DIR"
    
    # Application directory should already exist from rsync deployment
    if [[ ! -d "$APP_DIR" ]]; then
        error "Application directory not found: $APP_DIR. Please deploy code first via rsync."
    fi
    
    # Ensure proper ownership (should already be correct)
    if [[ ! -w "$APP_DIR" ]]; then
        error "No write permission to $APP_DIR"
    fi
}

# Clone or update application code
deploy_application_code() {
    log "📥 Deploying application code..."
    
    if [[ -d "$APP_DIR/.git" ]]; then
        log "Updating existing application code..."
        cd "$APP_DIR"
        
        # Backup current state
        cp -r . "$BACKUP_DIR/backup_$DEPLOY_DATE" || warn "Failed to create backup"
        
        # Stash any local changes and pull updates
        git stash push -m "Auto-stash before deployment $DEPLOY_DATE" || true
        git pull origin main || error "Failed to update application code"
    else
        log "Application directory exists but not a git repository..."
        log "Using existing files (deployed via rsync)"
        
        # Ensure we're in the right directory
        cd "$APP_DIR" || error "Application directory not found: $APP_DIR"
        
        # Create backup if directory has content
        if [[ "$(ls -A .)" ]]; then
            mkdir -p "$BACKUP_DIR"
            cp -r . "$BACKUP_DIR/backup_$DEPLOY_DATE" || warn "Failed to create backup"
        fi
    fi
    
    # Ensure script permissions
    find . -name "*.sh" -exec chmod +x {} \;
}

# Configure environment
configure_environment() {
    log "⚙️  Configuring production environment..."
    
    cd "$APP_DIR"
    
    # Copy production environment template if .env doesn't exist
    if [[ ! -f .env ]]; then
        if [[ -f .env.production.template ]]; then
            cp .env.production.template .env
            log "Created .env from template. Please customize it."
        else
            error ".env file not found and no template available"
        fi
    fi
    
    # Validate critical environment variables
    if [[ -f .env ]]; then
        source .env
    else
        error ".env file not found"
    fi
    
    local missing_vars=()
    [[ -z "${DB_HOST:-}" ]] && missing_vars+=("DB_HOST")
    [[ -z "${CORS_ORIGINS:-}" ]] && missing_vars+=("CORS_ORIGINS")
    [[ -z "${REDIRECT_URI:-}" ]] && missing_vars+=("REDIRECT_URI")
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        warn "Missing recommended environment variables: ${missing_vars[*]}"
    fi
    
    # Test RDS connectivity (if configured)
    if [[ -n "${DB_HOST:-}" ]]; then
        log "Testing database connectivity..."
        timeout 10 bash -c "</dev/tcp/${DB_HOST}/3306" || warn "Cannot connect to database. Please verify RDS configuration."
    fi
}

# Copy SSL certificates for nginx container
copy_ssl_certificates() {
    log "🔐 Copying SSL certificates..."
    
    local domain="helpdesk.amer.biz"
    local ssl_dir="./nginx/ssl"
    
    # Create SSL directory if it doesn't exist
    mkdir -p "$ssl_dir"
    
    # Check if Let's Encrypt certificates exist
    if [[ -f "/etc/letsencrypt/live/$domain/fullchain.pem" ]]; then
        log "Found Let's Encrypt certificates for $domain"
        
        # Copy actual certificate files (not symlinks)
        sudo cp "/etc/letsencrypt/live/$domain/fullchain.pem" "$ssl_dir/"
        sudo cp "/etc/letsencrypt/live/$domain/privkey.pem" "$ssl_dir/"
        
        # Set proper ownership
        sudo chown $USER:$USER "$ssl_dir"/*.pem
        
        # Set proper permissions
        chmod 644 "$ssl_dir/fullchain.pem"
        chmod 600 "$ssl_dir/privkey.pem"
        
        log "SSL certificates copied successfully!"
        ls -la "$ssl_dir"
    else
        warn "SSL certificates not found for $domain"
        warn "Make sure to run 'sudo certbot certonly --nginx -d $domain' first"
        warn "Continuing without SSL certificates - HTTPS will not work"
        
        # Create placeholder files to prevent nginx errors
        touch "$ssl_dir/fullchain.pem"
        touch "$ssl_dir/privkey.pem"
        chown $USER:$USER "$ssl_dir"/*.pem
    fi
}

# Build and deploy containers
deploy_containers() {
    log "🏗️  Building and deploying containers..."
    
    cd "$APP_DIR"
    
    # Stop existing containers gracefully
    if docker-compose ps | grep -q "Up"; then
        log "Stopping existing containers..."
        docker-compose down --timeout 30
    fi
    
    # Copy SSL certificates before building containers
    copy_ssl_certificates
    
    # Build containers with no cache for production
    log "Building containers..."
    docker-compose -f docker-compose.prod.yml build --no-cache --parallel || error "Failed to build containers"
    
    # Start containers
    log "Starting containers..."
    docker-compose -f docker-compose.prod.yml up -d || error "Failed to start containers"
    
    # Wait for services to be healthy
    log "⏳ Waiting for services to become healthy..."
    local timeout=120
    local elapsed=0
    
    while [[ $elapsed -lt $timeout ]]; do
        if docker-compose -f docker-compose.prod.yml ps | grep -q "healthy"; then
            local healthy_count=$(docker-compose -f docker-compose.prod.yml ps | grep -c "healthy" || echo "0")
            local total_services=3  # backend, frontend, nginx
            
            if [[ $healthy_count -eq $total_services ]]; then
                log "All services are healthy!"
                break
            fi
        fi
        
        sleep 5
        elapsed=$((elapsed + 5))
        info "Waiting for services... ($elapsed/${timeout}s)"
    done
    
    if [[ $elapsed -ge $timeout ]]; then
        error "Services failed to become healthy within ${timeout}s"
    fi
}

# Setup monitoring and logging
setup_monitoring() {
    log "� Setting up monitoring and logging..."
    
    # Setup log rotation
    sudo tee /etc/logrotate.d/helpdesk-crm > /dev/null <<EOF
$APP_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $USER $USER
    postrotate
        cd $APP_DIR && docker-compose -f docker-compose.prod.yml restart backend nginx
    endscript
}
EOF

    # Install and configure CloudWatch agent if available
    if command -v amazon-cloudwatch-agent-ctl &> /dev/null; then
        log "Configuring CloudWatch agent..."
        # CloudWatch configuration is handled by user-data script
    else
        warn "CloudWatch agent not found. Install it for better monitoring."
    fi
    
    # Create monitoring script
    tee "$APP_DIR/scripts/monitor.sh" > /dev/null <<'EOF'
#!/bin/bash
# Basic monitoring script
APP_DIR="/home/ec2-user/helpdesk-crm"
cd "$APP_DIR"

echo "=== Container Status ==="
docker-compose -f docker-compose.prod.yml ps

echo -e "\n=== Container Health ==="
curl -s http://localhost/health || echo "Health check failed"

echo -e "\n=== System Resources ==="
echo "Memory Usage:"
free -h
echo "Disk Usage:"
df -h /

echo -e "\n=== Recent Logs ==="
docker-compose -f docker-compose.prod.yml logs --tail=10
EOF
    chmod +x "$APP_DIR/scripts/monitor.sh"
}

# Setup backup system
setup_backups() {
    log "💾 Setting up backup system..."
    
    # Ensure backup script is executable
    if [[ -f "$APP_DIR/backup/backup.sh" ]]; then
        chmod +x "$APP_DIR/backup/backup.sh"
        
        # Setup daily backup cron job
        (crontab -l 2>/dev/null | grep -v "backup.sh"; echo "0 2 * * * $APP_DIR/backup/backup.sh") | crontab -
        log "Backup cron job configured for 2 AM daily"
    else
        warn "Backup script not found. Please create backup/backup.sh"
    fi
}

# Setup systemd service
setup_systemd_service() {
    log "🔧 Setting up systemd service..."
    
    sudo tee /etc/systemd/system/helpdesk-crm.service > /dev/null <<EOF
[Unit]
Description=Helpdesk CRM Application
Requires=docker.service
After=docker.service
StartLimitIntervalSec=0

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down --timeout 30
ExecReload=/usr/local/bin/docker-compose -f docker-compose.prod.yml restart
TimeoutStartSec=300
TimeoutStopSec=120
Restart=on-failure
RestartSec=30
User=ec2-user
Group=ec2-user

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable helpdesk-crm.service
    log "Systemd service configured and enabled"
}

# Verify deployment
verify_deployment() {
    log "🔍 Verifying deployment..."
    
    cd "$APP_DIR"
    
    # Check container status
    info "Container status:"
    docker-compose -f docker-compose.prod.yml ps
    
    # Test health endpoints
    local health_tests=(
        "http://localhost/health"
        "http://localhost/api/health"
    )
    
    for endpoint in "${health_tests[@]}"; do
        if curl -sf "$endpoint" > /dev/null; then
            log "✅ $endpoint - OK"
        else
            error "❌ $endpoint - FAILED"
        fi
    done
    
    # Check logs for errors
    local error_count=$(docker-compose -f docker-compose.prod.yml logs --tail=50 | grep -i error | wc -l)
    if [[ $error_count -gt 0 ]]; then
        warn "Found $error_count error(s) in recent logs. Please review."
    fi
    
    # Display resource usage
    info "System resource usage:"
    echo "Memory: $(free -h | awk 'NR==2{printf "%.1f/%.1fGB (%.1f%%)", $3/1024/1024, $2/1024/1024, $3*100/$2}')"
    echo "Disk: $(df -h / | awk 'NR==2{printf "%s/%s (%s)", $3, $2, $5}')"
    echo "CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
}

# Main deployment function
main() {
    log "🚀 Starting Helpdesk CRM Production Deployment"
    log "Deployment ID: $DEPLOY_DATE"
    
    check_user
    check_requirements
    install_dependencies
    setup_app_directory
    deploy_application_code
    configure_environment
    deploy_containers
    setup_monitoring
    setup_backups
    setup_systemd_service
    verify_deployment
    
    log "✅ Deployment completed successfully!"
    echo ""
    echo -e "${GREEN}=== DEPLOYMENT SUMMARY ===${NC}"
    echo "🌐 Application URL: http://$(curl -s http://checkip.amazonaws.com)"
    echo "📊 Monitor status: $APP_DIR/scripts/monitor.sh"
    echo "📄 View logs: docker-compose -f $APP_DIR/docker-compose.prod.yml logs -f"
    echo "🔄 Restart services: sudo systemctl restart helpdesk-crm"
    echo ""
    echo -e "${YELLOW}🔧 Next steps:${NC}"
    echo "   1. Configure your domain DNS to point to this server"
    echo "   2. Set up SSL certificate with Let's Encrypt or ACM"
    echo "   3. Configure AWS Application Load Balancer (if using)"
    echo "   4. Set up monitoring alerts in CloudWatch"
    echo "   5. Perform user acceptance testing"
    echo ""
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo "   - Production Guide: $APP_DIR/PRODUCTION-README.md"
    echo "   - API Docs: http://$(curl -s http://checkip.amazonaws.com)/api/v1/docs"
    echo "   - Health Check: http://$(curl -s http://checkip.amazonaws.com)/health"
}

# Handle script interruption
trap 'error "Deployment interrupted"' INT TERM

# Run main function
main "$@"
