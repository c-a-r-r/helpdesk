#!/bin/bash
"""
Setup script for Freshservice Sync Cron Job
This script sets up a reliable cron job that runs independently of your web application
"""

SCRIPT_DIR="/Users/cristian.rodriguez/Documents/helpdesk-crm/backend"
PYTHON_PATH="/usr/bin/python3"  # Adjust this to your Python path
LOG_FILE="/tmp/freshservice_sync.log"

echo "🔧 Setting up Freshservice Sync Cron Job"
echo "=========================================="

# Function to detect Python path
detect_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_PATH=$(which python3)
    elif command -v python &> /dev/null; then
        PYTHON_PATH=$(which python)
    else
        echo "❌ Python not found. Please install Python 3."
        exit 1
    fi
    echo "🐍 Using Python: $PYTHON_PATH"
}

# Function to test the script
test_script() {
    echo "🧪 Testing the sync script..."
    cd "$SCRIPT_DIR"
    $PYTHON_PATH cron_freshservice_sync.py
    if [ $? -eq 0 ]; then
        echo "✅ Script test successful!"
    else
        echo "❌ Script test failed. Check the error above."
        exit 1
    fi
}

# Function to setup cron job
setup_cron() {
    echo "⏰ Setting up cron job..."
    
    # Create the cron job entry
    CRON_JOB="*/5 * * * * cd $SCRIPT_DIR && $PYTHON_PATH cron_freshservice_sync.py >> $LOG_FILE 2>&1"
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    
    echo "✅ Cron job added!"
    echo "📋 Job details:"
    echo "   Schedule: Every 5 minutes"
    echo "   Command: $CRON_JOB"
    echo "   Log file: $LOG_FILE"
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Current Status:"
    echo "=================="
    echo "📄 Current crontab:"
    crontab -l | grep -E "(freshservice|sync)" || echo "   No sync jobs found"
    
    echo ""
    echo "📝 Recent log entries:"
    if [ -f "$LOG_FILE" ]; then
        tail -n 10 "$LOG_FILE"
    else
        echo "   No log file found yet"
    fi
}

# Function to remove cron job
remove_cron() {
    echo "🗑️  Removing Freshservice sync cron job..."
    crontab -l | grep -v "cron_freshservice_sync.py" | crontab -
    echo "✅ Cron job removed!"
}

# Main menu
case "${1:-setup}" in
    "setup")
        detect_python
        test_script
        setup_cron
        show_status
        echo ""
        echo "🎉 Setup complete!"
        echo "💡 Tips:"
        echo "   - Monitor logs: tail -f $LOG_FILE"
        echo "   - Check status: $0 status"
        echo "   - Remove job: $0 remove"
        ;;
    "test")
        detect_python
        test_script
        ;;
    "status")
        show_status
        ;;
    "remove")
        remove_cron
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [setup|test|status|remove|help]"
        echo ""
        echo "Commands:"
        echo "  setup   - Set up the cron job (default)"
        echo "  test    - Test the sync script"
        echo "  status  - Show current status and logs"
        echo "  remove  - Remove the cron job"
        echo "  help    - Show this help"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
