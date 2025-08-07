#!/bin/bash

# Health Check and Monitoring Script for Helpdesk CRM
# This script performs comprehensive health checks and reports system status

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/helpdesk-crm"
LOG_FILE="/var/log/helpdesk-monitor.log"
ALERT_EMAIL="${ADMIN_EMAIL:-admin@localhost}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Health check endpoints
HEALTH_ENDPOINTS=(
    "http://localhost/health"
    "http://localhost/api/v1/health"
)

# Critical services to monitor
SERVICES=(
    "helpdesk-backend-prod"
    "helpdesk-frontend-prod"
    "helpdesk-nginx-prod"
)

# Logging functions
log() {
    echo -e "${GREEN}[$TIMESTAMP] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$TIMESTAMP] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$TIMESTAMP] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$TIMESTAMP] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Check if docker is running
check_docker() {
    if ! systemctl is-active --quiet docker; then
        error "Docker service is not running"
        return 1
    fi
    return 0
}

# Check container health
check_containers() {
    local failed=0
    
    info "Checking container health..."
    
    cd "$APP_DIR" 2>/dev/null || {
        error "Cannot access application directory: $APP_DIR"
        return 1
    }
    
    for service in "${SERVICES[@]}"; do
        local status=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "unknown")
        local running=$(docker inspect --format='{{.State.Running}}' "$service" 2>/dev/null || echo "false")
        
        if [[ "$running" != "true" ]]; then
            error "Container $service is not running"
            failed=1
        elif [[ "$status" == "unhealthy" ]]; then
            error "Container $service is unhealthy"
            failed=1
        elif [[ "$status" == "healthy" ]]; then
            log "✅ Container $service is healthy"
        else
            warn "Container $service health status: $status"
        fi
    done
    
    return $failed
}

# Check HTTP endpoints
check_endpoints() {
    local failed=0
    
    info "Checking HTTP endpoints..."
    
    for endpoint in "${HEALTH_ENDPOINTS[@]}"; do
        local response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$endpoint" 2>/dev/null || echo "000")
        
        if [[ "$response_code" == "200" ]]; then
            log "✅ $endpoint responded with $response_code"
        else
            error "❌ $endpoint responded with $response_code"
            failed=1
        fi
    done
    
    return $failed
}

# Check system resources
check_resources() {
    local warnings=0
    
    info "Checking system resources..."
    
    # Check memory usage
    local mem_used=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
    local mem_used_int=${mem_used%.*}
    
    if [[ $mem_used_int -gt 90 ]]; then
        error "Memory usage critical: ${mem_used}%"
        warnings=1
    elif [[ $mem_used_int -gt 80 ]]; then
        warn "Memory usage high: ${mem_used}%"
    else
        log "Memory usage normal: ${mem_used}%"
    fi
    
    # Check disk usage
    local disk_used=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
    
    if [[ $disk_used -gt 90 ]]; then
        error "Disk usage critical: ${disk_used}%"
        warnings=1
    elif [[ $disk_used -gt 80 ]]; then
        warn "Disk usage high: ${disk_used}%"
    else
        log "Disk usage normal: ${disk_used}%"
    fi
    
    # Check CPU load
    local cpu_load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    local cpu_cores=$(nproc)
    local cpu_percentage=$(echo "scale=1; $cpu_load * 100 / $cpu_cores" | bc -l 2>/dev/null || echo "0")
    local cpu_percentage_int=${cpu_percentage%.*}
    
    if [[ $cpu_percentage_int -gt 90 ]]; then
        error "CPU load critical: ${cpu_percentage}% (load: $cpu_load)"
        warnings=1
    elif [[ $cpu_percentage_int -gt 80 ]]; then
        warn "CPU load high: ${cpu_percentage}% (load: $cpu_load)"
    else
        log "CPU load normal: ${cpu_percentage}% (load: $cpu_load)"
    fi
    
    return $warnings
}

# Check database connectivity
check_database() {
    info "Checking database connectivity..."
    
    cd "$APP_DIR" 2>/dev/null || return 1
    
    # Load environment variables
    if [[ -f .env ]]; then
        source .env
    else
        warn "Environment file not found"
        return 1
    fi
    
    # Test database connection through backend container
    local db_test=$(docker-compose -f docker-compose.prod.yml exec -T backend python -c "
from database import engine
try:
    with engine.connect() as conn:
        print('SUCCESS')
except Exception as e:
    print(f'FAILED: {e}')
" 2>/dev/null || echo "FAILED: Container not accessible")
    
    if [[ "$db_test" == "SUCCESS" ]]; then
        log "✅ Database connection successful"
        return 0
    else
        error "❌ Database connection failed: $db_test"
        return 1
    fi
}

# Check SSL certificate expiry (if HTTPS is configured)
check_ssl_certificate() {
    info "Checking SSL certificate..."
    
    # Get domain from environment
    local domain=""
    if [[ -f "$APP_DIR/.env" ]]; then
        domain=$(grep -E "^CORS_ORIGINS=" "$APP_DIR/.env" | cut -d'=' -f2 | cut -d',' -f1 | sed 's/https:\/\///')
    fi
    
    if [[ -z "$domain" ]]; then
        info "No domain configured for SSL check"
        return 0
    fi
    
    # Check certificate expiry
    local cert_expiry=$(echo | openssl s_client -servername "$domain" -connect "${domain}:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d'=' -f2 || echo "")
    
    if [[ -n "$cert_expiry" ]]; then
        local expiry_epoch=$(date -d "$cert_expiry" +%s 2>/dev/null || echo "0")
        local current_epoch=$(date +%s)
        local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        if [[ $days_until_expiry -lt 7 ]]; then
            error "SSL certificate expires in $days_until_expiry days"
            return 1
        elif [[ $days_until_expiry -lt 30 ]]; then
            warn "SSL certificate expires in $days_until_expiry days"
        else
            log "SSL certificate valid for $days_until_expiry days"
        fi
    else
        warn "Could not check SSL certificate for $domain"
    fi
    
    return 0
}

# Check application logs for errors
check_logs() {
    info "Checking application logs for recent errors..."
    
    cd "$APP_DIR" 2>/dev/null || return 1
    
    # Check for errors in the last 10 minutes
    local error_count=$(docker-compose -f docker-compose.prod.yml logs --since=10m 2>/dev/null | grep -i error | wc -l)
    
    if [[ $error_count -gt 0 ]]; then
        warn "Found $error_count error(s) in recent logs"
        return 1
    else
        log "No recent errors found in logs"
        return 0
    fi
}

# Auto-restart unhealthy services
auto_restart() {
    info "Attempting to restart unhealthy services..."
    
    cd "$APP_DIR" 2>/dev/null || return 1
    
    # Restart unhealthy containers
    for service in "${SERVICES[@]}"; do
        local status=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "unknown")
        
        if [[ "$status" == "unhealthy" ]] || [[ "$status" == "unknown" ]]; then
            warn "Restarting unhealthy service: $service"
            docker-compose -f docker-compose.prod.yml restart "${service#helpdesk-}" || error "Failed to restart $service"
        fi
    done
}

# Send alert email
send_alert() {
    local subject="$1"
    local message="$2"
    
    # Only send email if configured and mail command is available
    if command -v mail >/dev/null 2>&1 && [[ "$ALERT_EMAIL" != "admin@localhost" ]]; then
        echo "$message" | mail -s "$subject" "$ALERT_EMAIL" || warn "Failed to send alert email"
    fi
}

# Generate report
generate_report() {
    local overall_status="$1"
    
    cat << EOF

=== HELPDESK CRM HEALTH REPORT ===
Timestamp: $TIMESTAMP
Overall Status: $overall_status

=== SYSTEM INFORMATION ===
Hostname: $(hostname)
Uptime: $(uptime -p)
Load Average: $(uptime | awk -F'load average:' '{print $2}')

=== RESOURCE USAGE ===
Memory: $(free -h | awk 'NR==2{printf "%s/%s (%.1f%%)", $3, $2, $3*100/$2}')
Disk Usage: $(df -h / | awk 'NR==2{printf "%s/%s (%s)", $3, $2, $5}')
CPU Cores: $(nproc)

=== CONTAINER STATUS ===
$(cd "$APP_DIR" 2>/dev/null && docker-compose -f docker-compose.prod.yml ps || echo "Cannot access containers")

=== RECENT LOGS ===
$(cd "$APP_DIR" 2>/dev/null && docker-compose -f docker-compose.prod.yml logs --tail=5 2>/dev/null || echo "Cannot access logs")

EOF
}

# Main health check function
main() {
    local exit_code=0
    local issues=()
    
    log "Starting health check..."
    
    # Perform all health checks
    check_docker || { issues+=("Docker service"); exit_code=1; }
    check_containers || { issues+=("Container health"); exit_code=1; }
    check_endpoints || { issues+=("HTTP endpoints"); exit_code=1; }
    check_resources || { issues+=("System resources"); exit_code=1; }
    check_database || { issues+=("Database connectivity"); exit_code=1; }
    check_ssl_certificate || { issues+=("SSL certificate"); exit_code=1; }
    check_logs || { issues+=("Application logs"); }
    
    # Determine overall status
    local status="HEALTHY"
    if [[ $exit_code -ne 0 ]]; then
        status="UNHEALTHY"
        
        # Attempt auto-restart if enabled
        if [[ "${AUTO_RESTART:-true}" == "true" ]]; then
            auto_restart
        fi
        
        # Send alert
        local issue_list=$(IFS=', '; echo "${issues[*]}")
        send_alert "Helpdesk CRM Health Alert" "Issues detected: $issue_list"
    fi
    
    # Generate and display report
    local report=$(generate_report "$status")
    echo "$report"
    echo "$report" >> "$LOG_FILE"
    
    if [[ $exit_code -eq 0 ]]; then
        log "Health check completed successfully - All systems healthy"
    else
        error "Health check completed with issues - Status: $status"
    fi
    
    exit $exit_code
}

# Handle script arguments
case "${1:-check}" in
    "check")
        main
        ;;
    "monitor")
        # Continuous monitoring mode
        while true; do
            main
            sleep 300  # Check every 5 minutes
        done
        ;;
    "report")
        # Generate report only
        generate_report "REPORT"
        ;;
    *)
        echo "Usage: $0 [check|monitor|report]"
        echo "  check   - Run health check once (default)"
        echo "  monitor - Run continuous monitoring"
        echo "  report  - Generate system report only"
        exit 1
        ;;
esac
