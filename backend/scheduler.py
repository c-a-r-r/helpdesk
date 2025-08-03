"""
Background Scheduler for Automated Tasks
Handles automated execution of scripts like Freshservice onboarding sync
"""
import asyncio
import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
import traceback
import json

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReliableBackgroundScheduler:
    """Enhanced scheduler with better reliability and logging"""
    
    def __init__(self):
        self.running = False
        self.scheduler_thread = None
        self.last_sync_attempt = None
        self.last_sync_success = None
        self.sync_failures = 0
        self.max_consecutive_failures = 5
        
    def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
            
        logger.info("Starting enhanced background scheduler...")
        self.running = True
        
        # Clear any existing jobs
        schedule.clear()
        
        # Schedule the Freshservice sync every 5 minutes for testing
        job = schedule.every(5).minutes.do(self._run_freshservice_sync_with_error_handling)
        logger.info(f"Scheduled Freshservice sync every 5 minutes: {job}")
        
        # Also schedule every hour for production
        hourly_job = schedule.every().hour.do(self._run_freshservice_sync_with_error_handling)
        logger.info(f"Scheduled Freshservice sync every hour: {hourly_job}")
        
        # Schedule a heartbeat log every 10 minutes to confirm scheduler is alive
        heartbeat_job = schedule.every(10).minutes.do(self._log_heartbeat)
        logger.info(f"Scheduled heartbeat every 10 minutes: {heartbeat_job}")
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info(f"Enhanced scheduler started with {len(schedule.jobs)} jobs")
        
        # Log immediate status
        self._log_scheduler_status()
    
    def stop(self):
        """Stop the background scheduler"""
        logger.info("Stopping enhanced background scheduler...")
        self.running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=10)
            
        logger.info("Enhanced background scheduler stopped")
    
    def _run_scheduler(self):
        """Enhanced scheduler loop with better error handling"""
        logger.info("Enhanced scheduler loop started")
        self._log_heartbeat()  # Initial heartbeat
        
        while self.running:
            try:
                # Log pending jobs for debugging
                pending_jobs = [job for job in schedule.jobs if job.should_run]
                if pending_jobs:
                    logger.info(f"Running {len(pending_jobs)} pending jobs")
                    for job in pending_jobs:
                        logger.info(f"  - Job: {job.job_func.__name__} | Next run was: {job.next_run}")
                
                # Run pending jobs
                schedule.run_pending()
                
                # Sleep for 30 seconds (more frequent checking)
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Critical error in scheduler loop: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                time.sleep(60)  # Wait longer on error
    
    def _log_heartbeat(self):
        """Log heartbeat to confirm scheduler is running"""
        logger.info("📡 Scheduler heartbeat - System is running")
        logger.info(f"Next sync attempt scheduled for: {self._get_next_sync_time()}")
        logger.info(f"Last sync attempt: {self.last_sync_attempt}")
        logger.info(f"Last successful sync: {self.last_sync_success}")
        logger.info(f"Consecutive failures: {self.sync_failures}")
    
    def _get_next_sync_time(self) -> Optional[str]:
        """Get the next scheduled sync time"""
        sync_jobs = [job for job in schedule.jobs if 'freshservice_sync' in job.job_func.__name__]
        if sync_jobs:
            next_run = min(job.next_run for job in sync_jobs if job.next_run)
            return next_run.strftime("%Y-%m-%d %H:%M:%S") if next_run else None
        return None
    
    def _run_freshservice_sync_with_error_handling(self):
        """Wrapper for Freshservice sync with comprehensive error handling"""
        self.last_sync_attempt = datetime.now()
        
        try:
            logger.info("🔄 Starting automated Freshservice onboarding sync...")
            logger.info(f"Sync attempt at: {self.last_sync_attempt}")
            
            result = self._run_freshservice_sync()
            
            if result and result.get("status") == "success":
                self.last_sync_success = datetime.now()
                self.sync_failures = 0
                logger.info("✅ Scheduled sync completed successfully")
            else:
                self.sync_failures += 1
                logger.error(f"❌ Scheduled sync failed. Consecutive failures: {self.sync_failures}")
                
                if self.sync_failures >= self.max_consecutive_failures:
                    logger.critical(f"🚨 CRITICAL: {self.sync_failures} consecutive sync failures! Manual intervention required.")
                    
        except Exception as e:
            self.sync_failures += 1
            logger.error(f"❌ Critical error in sync wrapper: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error(f"Consecutive failures: {self.sync_failures}")
    
    def _run_freshservice_sync(self) -> Dict[str, Any]:
        """Enhanced Freshservice sync with detailed logging"""
        db = None
        script_log = None
        start_time = time.time()
        
        try:
            # Import here to avoid circular imports
            from scripts.freshservice.sync_onboarding import FreshserviceOnboardingSync
            from database import SessionLocal
            from sqlalchemy import text
            from datetime import datetime
            
            # Create database session
            db = SessionLocal()
            
            # Insert directly into sync_logs table
            started_at = datetime.now()
            
            # Insert initial log entry
            db.execute(text("""
                INSERT INTO sync_logs (sync_type, sync_source, status, triggered_by, started_at, additional_data)
                VALUES (:sync_type, :sync_source, :status, :triggered_by, :started_at, :additional_data)
            """), {
                'sync_type': 'freshservice',
                'sync_source': 'Freshservice API',
                'status': 'running',
                'triggered_by': 'automated_scheduler',
                'started_at': started_at,
                'additional_data': json.dumps({
                    "hours_back": 1, 
                    "automated": True,
                    "sync_attempt": self.last_sync_attempt.isoformat() if self.last_sync_attempt else None,
                    "consecutive_failures": self.sync_failures
                })
            })
            db.commit()
            
            # Get the inserted log ID
            result_proxy = db.execute(text("SELECT LAST_INSERT_ID()"))
            log_id = result_proxy.fetchone()[0]
            
            logger.info(f"Created sync log entry with ID: {log_id}")
            
            # Execute the sync script
            sync_script = FreshserviceOnboardingSync()
            sync_script.user_data = {"hours_back": 1}  # Only check last hour for automated runs
            
            logger.info("Executing Freshservice sync script...")
            result = sync_script.execute()
            
            execution_time = int(time.time() - start_time)
            
            # Process results
            tickets_processed = result.get('tickets_processed', 0)
            users_created = result.get('users_created', 0)
            users_skipped = result.get('users_skipped', 0)
            
            # Determine status
            if result.get("status") == "completed":
                status = "success"
                output = f"✅ Automated sync completed successfully:\n" \
                        f"  • Tickets processed: {tickets_processed}\n" \
                        f"  • Users created: {users_created}\n" \
                        f"  • Users skipped: {users_skipped}\n" \
                        f"  • Execution time: {execution_time}s"
                        
                logger.info(output.replace('\n', ' | '))
                
                # Log creation details if any users were created
                if users_created > 0:
                    logger.info(f"🎉 Created {users_created} new onboarding records from Freshservice!")
                    if result.get('created_tickets'):
                        for ticket in result.get('created_tickets', []):
                            logger.info(f"  • Ticket {ticket.get('ticket_id')}: {ticket.get('name')} ({ticket.get('email')})")
                else:
                    logger.info("📋 No new onboarding records found in Freshservice")
            else:
                status = "failed"
                error_msg = result.get("error", "Unknown error occurred")
                output = f"❌ Automated sync failed: {error_msg}"
                logger.error(output)
            
            # Update sync_logs with results
            completed_at = datetime.now()
            if status == "success":
                db.execute(text("""
                    UPDATE sync_logs 
                    SET status = :status, completed_at = :completed_at, 
                        execution_time_seconds = :execution_time,
                        tickets_processed = :tickets_processed,
                        users_created = :users_created,
                        users_skipped = :users_skipped,
                        output_message = :output_message
                    WHERE id = :log_id
                """), {
                    'status': status,
                    'completed_at': completed_at,
                    'execution_time': execution_time,
                    'tickets_processed': result.get('tickets_processed', 0),
                    'users_created': result.get('users_created', 0),
                    'users_skipped': result.get('users_skipped', 0),
                    'output_message': output,
                    'log_id': log_id
                })
            else:
                db.execute(text("""
                    UPDATE sync_logs 
                    SET status = :status, completed_at = :completed_at,
                        execution_time_seconds = :execution_time,
                        error_message = :error_message,
                        output_message = :output_message
                    WHERE id = :log_id
                """), {
                    'status': status,
                    'completed_at': completed_at,
                    'execution_time': execution_time,
                    'error_message': error_msg,
                    'output_message': output,
                    'log_id': log_id
                })
            
            db.commit()
            
            return {"status": status, "result": result}
            
        except Exception as e:
            # Handle critical errors
            execution_time = int(time.time() - start_time)
            error_msg = f"Critical error in scheduled sync: {str(e)}"
            
            logger.error(error_msg)
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Update sync_logs with error if we have a log entry
            if log_id and db:
                try:
                    completed_at = datetime.now()
                    db.execute(text("""
                        UPDATE sync_logs 
                        SET status = :status, completed_at = :completed_at,
                            execution_time_seconds = :execution_time,
                            error_message = :error_message,
                            output_message = :output_message
                        WHERE id = :log_id
                    """), {
                        'status': 'failed',
                        'completed_at': completed_at,
                        'execution_time': execution_time,
                        'error_message': error_msg,
                        'output_message': f"❌ Critical scheduler error: {error_msg}",
                        'log_id': log_id
                    })
                    db.commit()
                except Exception as log_error:
                    logger.error(f"Failed to update sync log: {log_error}")
            
            return {"status": "failed", "error": error_msg}
            
        finally:
            if db:
                try:
                    db.close()
                except Exception as e:
                    logger.error(f"Error closing database connection: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get enhanced scheduler status"""
        next_runs = []
        for job in schedule.jobs:
            next_runs.append({
                "job": job.job_func.__name__,
                "next_run": job.next_run.isoformat() if job.next_run else None,
                "interval": str(job.interval),
                "unit": job.unit
            })
        
        return {
            "running": self.running,
            "jobs_count": len(schedule.jobs),
            "next_runs": next_runs,
            "current_time": datetime.now().isoformat(),
            "last_sync_attempt": self.last_sync_attempt.isoformat() if self.last_sync_attempt else None,
            "last_sync_success": self.last_sync_success.isoformat() if self.last_sync_success else None,
            "consecutive_failures": self.sync_failures,
            "next_sync_time": self._get_next_sync_time()
        }
    
    def _log_scheduler_status(self):
        """Log comprehensive scheduler status"""
        status = self.get_status()
        logger.info("📊 Enhanced Scheduler Status Report:")
        logger.info(f"  • Running: {status['running']}")
        logger.info(f"  • Active Jobs: {status['jobs_count']}")
        logger.info(f"  • Last Sync Attempt: {status['last_sync_attempt']}")
        logger.info(f"  • Last Successful Sync: {status['last_sync_success']}")
        logger.info(f"  • Consecutive Failures: {status['consecutive_failures']}")
        logger.info(f"  • Next Sync: {status['next_sync_time']}")
        
        for job_info in status['next_runs']:
            logger.info(f"  • Job: {job_info['job']} | Every {job_info['interval']} {job_info['unit']} | Next: {job_info['next_run']}")

# Global scheduler instance
background_scheduler = ReliableBackgroundScheduler()
@asynccontextmanager
async def scheduler_lifespan():
    """Context manager for scheduler lifecycle"""
    try:
        background_scheduler.start()
        yield
    finally:
        background_scheduler.stop()
