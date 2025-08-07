#!/bin/bash

# Enhanced Production Backup Script for Helpdesk CRM
# Backs up database, application data, and configuration files

set -euo pipefail

# Configuration
BACKUP_BASE_DIR="/opt/backups"
APP_DIR="/opt/helpdesk-crm"
LOG_FILE="/var/log/helpdesk-backup.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$BACKUP_BASE_DIR/$TIMESTAMP"
RETENTION_DAYS=30

# AWS S3 Configuration (optional)
S3_BUCKET="${BACKUP_S3_BUCKET:-}"
AWS_REGION="${AWS_REGION:-us-west-2}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking backup prerequisites..."
    
    # Check if running as proper user
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root"
        exit 1
    fi
    
    # Check disk space (need at least 5GB free)
    local available_space=$(df "$BACKUP_BASE_DIR" | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 5242880 ]]; then
        error "Insufficient disk space for backup. Need at least 5GB."
        exit 1
    fi
    
    # Check if application directory exists
    if [[ ! -d "$APP_DIR" ]]; then
        error "Application directory not found: $APP_DIR"
        exit 1
    fi
    
    # Load environment variables
    if [[ -f "$APP_DIR/.env" ]]; then
        source "$APP_DIR/.env"
    else
        error "Environment file not found: $APP_DIR/.env"
        exit 1
    fi
    
    # Check required tools
    local missing_tools=()
    command -v mysqldump >/dev/null || missing_tools+=("mysqldump")
    command -v docker >/dev/null || missing_tools+=("docker")
    command -v tar >/dev/null || missing_tools+=("tar")
    command -v gzip >/dev/null || missing_tools+=("gzip")
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi
}

# Create backup directory structure
setup_backup_directory() {
    log "Setting up backup directory: $BACKUP_DIR"
    
    mkdir -p "$BACKUP_DIR"/{database,application,logs,config}
    chmod 755 "$BACKUP_DIR"
}

# Backup database
backup_database() {
    log "Starting database backup..."
    
    local db_backup_file="$BACKUP_DIR/database/helpdesk_crm_${TIMESTAMP}.sql"
    
    # Get database credentials from environment or secrets
    local db_host="${DB_HOST:-localhost}"
    local db_port="${DB_PORT:-3306}"
    local db_name="${DB_NAME:-helpdesk_crm}"
    local db_user="${DB_USER:-admin}"
    local db_password=""
    
    # Get password from AWS Secrets Manager if enabled
    if [[ "${SECRETS_MANAGER_ENABLED:-false}" == "true" ]]; then
        local secret_name="${DB_PASSWORD_SECRET_NAME:-helpdesk-crm/db-password}"
        db_password=$(aws secretsmanager get-secret-value 
            --secret-id "$secret_name" 
            --region "$AWS_REGION" 
            --query SecretString 
            --output text 2>/dev/null || echo "")
        
        if [[ -z "$db_password" ]]; then
            error "Failed to retrieve database password from Secrets Manager"
            return 1
        fi
    else
        db_password="${DB_PASSWORD:-}"
        if [[ -z "$db_password" ]]; then
            error "Database password not configured"
            return 1
        fi
    fi
    
    # Create database backup
    if mysqldump 
        --host="$db_host" 
        --port="$db_port" 
        --user="$db_user" 
        --password="$db_password" 
        --single-transaction 
        --routines 
        --triggers 
        --add-drop-table 
        --add-locks 
        --create-options 
        --quick 
        --lock-tables=false 
        "$db_name" > "$db_backup_file" 2>/dev/null; then
        
        # Compress the backup
        gzip "$db_backup_file"
        local compressed_size=$(du -h "${db_backup_file}.gz" | cut -f1)
        log "✅ Database backup completed: ${compressed_size}"
        
        # Create backup metadata
        cat > "$BACKUP_DIR/database/metadata.json" <<EOF
{
    "timestamp": "$TIMESTAMP",
    "database_host": "$db_host",
    "database_name": "$db_name",
    "backup_size": "$compressed_size",
    "backup_method": "mysqldump",
    "compression": "gzip"
}
EOF
        
        return 0
    else
        error "Database backup failed"
        return 1
    fi
}

# Backup application files
backup_application() {
    log "Starting application backup..."
    
    cd "$APP_DIR"
    
    # Create application backup
    local app_backup_file="$BACKUP_DIR/application/helpdesk_app_${TIMESTAMP}.tar.gz"
    
    # Exclude unnecessary files and directories
    local exclude_patterns=(
        "--exclude=.git"
        "--exclude=node_modules"
        "--exclude=__pycache__"
        "--exclude=*.pyc"
        "--exclude=.env.local"
        "--exclude=.env.development"
        "--exclude=logs/*"
        "--exclude=.docker"
        "--exclude=*.log"
    )
    
    if tar czf "$app_backup_file" "${exclude_patterns[@]}" . 2>/dev/null; then
        local app_size=$(du -h "$app_backup_file" | cut -f1)
        log "✅ Application backup completed: ${app_size}"
        
        # Create application metadata
        local git_commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
        local git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        
        cat > "$BACKUP_DIR/application/metadata.json" <<EOF
{
    "timestamp": "$TIMESTAMP",
    "backup_size": "$app_size",
    "git_commit": "$git_commit",
    "git_branch": "$git_branch",
    "backup_method": "tar+gzip"
}
EOF
        
        return 0
    else
        error "Application backup failed"
        return 1
    fi
}

# Backup configuration files
backup_configuration() {
    log "Starting configuration backup..."
    
    local config_dir="$BACKUP_DIR/config"
    
    # Backup environment configuration (without sensitive data)
    if [[ -f "$APP_DIR/.env" ]]; then
        # Create sanitized environment file
        grep -v -E "(PASSWORD|SECRET|KEY)" "$APP_DIR/.env" > "$config_dir/env_sanitized.txt" || true
        log "Environment configuration backed up (sanitized)"
    fi
    
    # Backup Docker Compose configuration
    if [[ -f "$APP_DIR/docker-compose.prod.yml" ]]; then
        cp "$APP_DIR/docker-compose.prod.yml" "$config_dir/"
        log "Docker Compose configuration backed up"
    fi
    
    # Backup Nginx configuration
    if [[ -f "$APP_DIR/nginx/nginx.prod.conf" ]]; then
        cp "$APP_DIR/nginx/nginx.prod.conf" "$config_dir/"
        log "Nginx configuration backed up"
    fi
    
    # Backup Terraform configuration (if exists)
    if [[ -d "$APP_DIR/terraform" ]]; then
        tar czf "$config_dir/terraform_config.tar.gz" -C "$APP_DIR" terraform/
        log "Terraform configuration backed up"
    fi
    
    # Create configuration metadata
    cat > "$config_dir/metadata.json" <<EOF
{
    "timestamp": "$TIMESTAMP",
    "hostname": "$(hostname)",
    "backup_contents": [
        "environment_config",
        "docker_compose_config",
        "nginx_config",
        "terraform_config"
    ]
}
EOF
    
    log "✅ Configuration backup completed"
}

# Backup application logs
backup_logs() {
    log "Starting logs backup..."
    
    local logs_backup_file="$BACKUP_DIR/logs/application_logs_${TIMESTAMP}.tar.gz"
    
    # Backup application logs
    if [[ -d "$APP_DIR/logs" ]] && [[ -n "$(ls -A "$APP_DIR/logs" 2>/dev/null)" ]]; then
        tar czf "$logs_backup_file" -C "$APP_DIR" logs/
        local logs_size=$(du -h "$logs_backup_file" | cut -f1)
        log "✅ Application logs backup completed: ${logs_size}"
    else
        warn "No application logs found to backup"
    fi
    
    # Backup system logs related to the application
    local system_logs_file="$BACKUP_DIR/logs/system_logs_${TIMESTAMP}.tar.gz"
    local log_files=()
    
    [[ -f "/var/log/helpdesk-deploy.log" ]] && log_files+=("/var/log/helpdesk-deploy.log")
    [[ -f "/var/log/helpdesk-backup.log" ]] && log_files+=("/var/log/helpdesk-backup.log")
    [[ -f "/var/log/helpdesk-monitor.log" ]] && log_files+=("/var/log/helpdesk-monitor.log")
    
    if [[ ${#log_files[@]} -gt 0 ]]; then
        tar czf "$system_logs_file" "${log_files[@]}" 2>/dev/null || true
        log "System logs backup completed"
    fi
}

# Upload to S3 (if configured)
upload_to_s3() {
    if [[ -z "$S3_BUCKET" ]]; then
        info "S3 backup not configured, skipping upload"
        return 0
    fi
    
    log "Starting S3 upload to bucket: $S3_BUCKET"
    
    # Create compressed backup archive
    local full_backup_file="/tmp/helpdesk_backup_${TIMESTAMP}.tar.gz"
    tar czf "$full_backup_file" -C "$BACKUP_BASE_DIR" "$TIMESTAMP"
    
    # Upload to S3
    if aws s3 cp "$full_backup_file" "s3://$S3_BUCKET/backups/helpdesk-crm/" 
        --region "$AWS_REGION" 
        --storage-class STANDARD_IA 
        --metadata "timestamp=$TIMESTAMP,hostname=$(hostname)" 2>/dev/null; then
        
        local backup_size=$(du -h "$full_backup_file" | cut -f1)
        log "✅ S3 upload completed: ${backup_size}"
        
        # Clean up temporary file
        rm -f "$full_backup_file"
        
        return 0
    else
        error "S3 upload failed"
        rm -f "$full_backup_file"
        return 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    # Clean up local backups
    find "$BACKUP_BASE_DIR" -maxdepth 1 -type d -name "????????_??????" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    # Clean up old log entries (keep last 1000 lines)
    if [[ -f "$LOG_FILE" ]]; then
        tail -1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
    
    # Clean up S3 backups (if configured)
    if [[ -n "$S3_BUCKET" ]]; then
        local cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%Y%m%d)
        aws s3 ls "s3://$S3_BUCKET/backups/helpdesk-crm/" 2>/dev/null | 
        awk -v cutoff="$cutoff_date" '$4 ~ /^helpdesk_backup_[0-9]{8}_/ && $4 < "helpdesk_backup_"cutoff {print $4}' | 
        while read -r backup_file; do
            aws s3 rm "s3://$S3_BUCKET/backups/helpdesk-crm/$backup_file" 2>/dev/null || true
        done
    fi
    
    log "Cleanup completed"
}

# Generate backup report
generate_backup_report() {
    local backup_status="$1"
    local backup_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "unknown")
    
    cat > "$BACKUP_DIR/backup_report.json" <<EOF
{
    "backup_id": "$TIMESTAMP",
    "timestamp": "$(date -Iseconds)",
    "hostname": "$(hostname)",
    "status": "$backup_status",
    "total_size": "$backup_size",
    "retention_days": $RETENTION_DAYS,
    "s3_enabled": $([ -n "$S3_BUCKET" ] && echo "true" || echo "false"),
    "components": {
        "database": $([ -f "$BACKUP_DIR/database/helpdesk_crm_${TIMESTAMP}.sql.gz" ] && echo "true" || echo "false"),
        "application": $([ -f "$BACKUP_DIR/application/helpdesk_app_${TIMESTAMP}.tar.gz" ] && echo "true" || echo "false"),
        "configuration": $([ -f "$BACKUP_DIR/config/metadata.json" ] && echo "true" || echo "false"),
        "logs": $([ -f "$BACKUP_DIR/logs/application_logs_${TIMESTAMP}.tar.gz" ] && echo "true" || echo "false")
    }
}
EOF

    log "Backup report generated: $BACKUP_DIR/backup_report.json"
}

# Send backup notification (if configured)
send_notification() {
    local status="$1"
    local message="$2"
    
    # Email notification (if configured)
    if command -v mail >/dev/null 2>&1 && [[ -n "${ADMIN_EMAIL:-}" ]] && [[ "$ADMIN_EMAIL" != "admin@localhost" ]]; then
        echo "$message" | mail -s "Helpdesk CRM Backup $status" "$ADMIN_EMAIL" 2>/dev/null || true
    fi
    
    # Slack notification (if webhook configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' 
            --data "{"text":"Helpdesk CRM Backup $status: $message"}" 
            "$SLACK_WEBHOOK_URL" 2>/dev/null || true
    fi
}

# Main backup function
main() {
    local backup_start_time=$(date +%s)
    local backup_status="FAILED"
    local errors=()
    
    log "🚀 Starting Helpdesk CRM backup - ID: $TIMESTAMP"
    
    # Run backup steps
    check_prerequisites || { errors+=("Prerequisites check failed"); }
    setup_backup_directory || { errors+=("Backup directory setup failed"); }
    
    backup_database || { errors+=("Database backup failed"); }
    backup_application || { errors+=("Application backup failed"); }
    backup_configuration || { errors+=("Configuration backup failed"); }
    backup_logs || { errors+=("Logs backup failed"); }
    
    # Optional S3 upload
    if [[ ${#errors[@]} -eq 0 ]]; then
        upload_to_s3 || { errors+=("S3 upload failed"); }
    fi
    
    # Cleanup regardless of backup status
    cleanup_old_backups
    
    # Determine final status
    if [[ ${#errors[@]} -eq 0 ]]; then
        backup_status="SUCCESS"
    fi
    
    # Generate report
    generate_backup_report "$backup_status"
    
    # Calculate backup duration
    local backup_end_time=$(date +%s)
    local backup_duration=$((backup_end_time - backup_start_time))
    local backup_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "unknown")
    
    # Log final status
    if [[ "$backup_status" == "SUCCESS" ]]; then
        log "✅ Backup completed successfully in ${backup_duration}s - Size: $backup_size"
        send_notification "Success" "Backup completed successfully. Size: $backup_size, Duration: ${backup_duration}s"
    else
        local error_list=$(IFS=', '; echo "${errors[*]}")
        error "❌ Backup completed with errors: $error_list"
        send_notification "Failed" "Backup failed with errors: $error_list"
    fi
    
    # Exit with appropriate code
    [[ "$backup_status" == "SUCCESS" ]] && exit 0 || exit 1
}

# Handle script interruption
trap 'error "Backup interrupted"; exit 1' INT TERM

# Run main function
main "$@"
