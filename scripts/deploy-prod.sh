#!/bin/bash
# Production Deployment Script - Sync files and deploy

set -euo pipefail

# Configuration
LOCAL_DIR="/Users/cristian.rodriguez/Documents/helpdesk-crm"
REMOTE_HOST="ec2-44-245-190-156.us-west-2.compute.amazonaws.com"
REMOTE_USER="ec2-user"
REMOTE_DIR="helpdesk-crm"
SSH_KEY="/Users/cristian.rodriguez/Documents/my-keys/dms-test.pem"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Function to sync files with exclusions
sync_files() {
    log "🚀 Syncing files to production server..."
    
    # Rsync with exclusions
    rsync -avz --delete \
        --exclude='terraform/' \
        --exclude='docs/' \
        --exclude='.git/' \
        --exclude='node_modules/' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        --exclude='*.log' \
        --exclude='*.tmp' \
        --exclude='.env.local' \
        --exclude='.vscode/' \
        -e "ssh -i $SSH_KEY" \
        "$LOCAL_DIR/" \
        "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/" || error "Failed to sync files"
    
    log "✅ Files synced successfully"
}

# Function to deploy containers
deploy_containers() {
    log "🏗️ Deploying containers on production server..."
    
    ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" << 'EOF'
        set -euo pipefail
        cd helpdesk-crm
        
        # Copy SSL certificates
        echo "🔐 Copying SSL certificates..."
        ./scripts/copy-ssl-certs.sh || echo "Warning: SSL certificate copy failed"
        
        # Stop existing containers
        echo "⏹️ Stopping existing containers..."
        docker-compose -f docker-compose.prod.yml down --timeout 30 || true
        
        # Build and start containers
        echo "🚀 Building and starting containers..."
        docker-compose -f docker-compose.prod.yml up -d --build
        
        # Wait for health checks
        echo "⏳ Waiting for services to be healthy..."
        sleep 10
        
        # Check container status
        echo "📊 Container status:"
        docker-compose -f docker-compose.prod.yml ps
        
        # Test health endpoint
        echo "🔍 Testing health endpoint..."
        sleep 5
        curl -f http://localhost/health || echo "Warning: Health check failed"
        
        echo "✅ Deployment completed!"
EOF
    
    if [ $? -eq 0 ]; then
        log "✅ Deployment completed successfully!"
        log "🌐 Application URL: https://helpdesk.amer.biz"
    else
        error "❌ Deployment failed!"
    fi
}

# Function to show deployment summary
show_summary() {
    echo ""
    log "=== DEPLOYMENT SUMMARY ==="
    echo "🌐 Application: https://helpdesk.amer.biz"
    echo "🔍 Health Check: https://helpdesk.amer.biz/health"
    echo "📚 API Docs: https://helpdesk.amer.biz/docs"
    echo ""
    echo "📋 Excluded from sync:"
    echo "   - terraform/ (infrastructure code)"
    echo "   - docs/ (documentation)"
    echo "   - .git/ (version control)"
    echo "   - node_modules/ (dependencies)"
    echo "   - __pycache__/ (Python cache)"
    echo ""
    echo "🔧 To monitor:"
    echo "   ssh -i $SSH_KEY $REMOTE_USER@$REMOTE_HOST"
    echo "   cd $REMOTE_DIR && docker-compose -f docker-compose.prod.yml logs -f"
}

# Main execution
main() {
    log "🚀 Starting production deployment..."
    
    # Check if local directory exists
    if [[ ! -d "$LOCAL_DIR" ]]; then
        error "Local directory not found: $LOCAL_DIR"
    fi
    
    # Check if SSH key exists
    if [[ ! -f "$SSH_KEY" ]]; then
        error "SSH key not found: $SSH_KEY"
    fi
    
    # Sync files
    sync_files
    
    # Deploy containers
    deploy_containers
    
    # Show summary
    show_summary
}

# Run main function
main "$@"
