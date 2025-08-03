#!/usr/bin/env python3
"""
Standalone Freshservice Sync Script for Cron
This script can be run independently by cron without requiring the web app to be running
"""
import sys
import os
import logging
import time
import json
import traceback
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/freshservice_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_sync():
    """Run the Freshservice sync independently"""
    logger.info("🔄 Starting cron-based Freshservice sync...")
    
    db = None
    script_log = None
    start_time = time.time()
    
    try:
        # Import here to ensure all dependencies are available
        from scripts.freshservice.sync_onboarding import FreshserviceOnboardingSync
        from database import SessionLocal
        from crud import ScriptLogCRUD
        from schemas import ScriptLogCreate
        from models import ScriptStatus
        
        # Create database session
        db = SessionLocal()
        
        # Create log entry
        log_data = ScriptLogCreate(
            user_id=None,
            script_type="freshservice",
            script_name="sync_onboarding",
            status=ScriptStatus.RUNNING,
            executed_by="cron_job",
            additional_params=json.dumps({
                "hours_back": 1,
                "automated": True,
                "trigger": "cron",
                "timestamp": datetime.now().isoformat()
            })
        )
        
        script_log = ScriptLogCRUD.create(db, log_data)
        logger.info(f"Created script log entry with ID: {script_log.id}")
        
        # Execute sync
        sync_script = FreshserviceOnboardingSync()
        sync_script.user_data = {"hours_back": 1}
        
        result = sync_script.execute()
        execution_time = int(time.time() - start_time)
        
        # Process results
        tickets_processed = result.get('tickets_processed', 0)
        users_created = result.get('users_created', 0)
        users_skipped = result.get('users_skipped', 0)
        
        if result.get("status") == "completed":
            status = "success"
            output = f"✅ Cron sync completed successfully:\n" \
                    f"  • Tickets processed: {tickets_processed}\n" \
                    f"  • Users created: {users_created}\n" \
                    f"  • Users skipped: {users_skipped}\n" \
                    f"  • Execution time: {execution_time}s"
            
            if users_created > 0:
                logger.info(f"🎉 Created {users_created} new onboarding records!")
                if result.get('created_tickets'):
                    for ticket in result.get('created_tickets', []):
                        logger.info(f"  • Ticket {ticket.get('ticket_id')}: {ticket.get('name')} ({ticket.get('email')})")
            else:
                logger.info("📋 No new onboarding records found")
        else:
            status = "failed"
            error_msg = result.get("error", "Unknown error")
            output = f"❌ Cron sync failed: {error_msg}"
        
        # Update log
        ScriptLogCRUD.update_completion(
            db, script_log.id, status,
            output=output,
            error_message=result.get("error") if status == "failed" else None,
            execution_time_seconds=execution_time
        )
        
        logger.info(output.replace('\n', ' | '))
        
        # Exit with appropriate code
        sys.exit(0 if status == "success" else 1)
        
    except Exception as e:
        error_msg = f"Critical error in cron sync: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Update log if possible
        if script_log and db:
            try:
                execution_time = int(time.time() - start_time)
                ScriptLogCRUD.update_completion(
                    db, script_log.id, "failed",
                    error_message=error_msg,
                    execution_time_seconds=execution_time
                )
            except Exception as log_error:
                logger.error(f"Failed to update log: {log_error}")
        
        sys.exit(1)
        
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database: {e}")

if __name__ == "__main__":
    run_sync()
