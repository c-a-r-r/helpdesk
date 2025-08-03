"""
Background Scheduler for Automated Tasks
Handles automated execution of scripts like Freshservice onboarding sync
"""
import asyncio
import logging
import schedule
import time
import threading
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundScheduler:
    """Handles background scheduled tasks"""
    
    def __init__(self):
        self.running = False
        self.scheduler_thread = None
        
    def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
            
        logger.info("Starting background scheduler...")
        self.running = True
        
        # Schedule the Freshservice sync every hour
        job = schedule.every().hour.do(self._run_freshservice_sync)
        logger.info(f"Scheduled job: {job}")
        
        # For testing, also schedule every 5 minutes to see if it works
        test_job = schedule.every(5).minutes.do(self._run_freshservice_sync)
        logger.info(f"Test job scheduled every 5 minutes: {test_job}")
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info(f"Background scheduler started successfully with {len(schedule.jobs)} jobs")
        logger.info(f"Jobs: {[str(job) for job in schedule.jobs]}")
    
    def stop(self):
        """Stop the background scheduler"""
        logger.info("Stopping background scheduler...")
        self.running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
            
        logger.info("Background scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        while self.running:
            try:
                # Log pending jobs count
                pending_jobs = len([job for job in schedule.jobs if job.should_run])
                if pending_jobs > 0:
                    logger.info(f"Found {pending_jobs} pending jobs to run")
                
                # Run pending jobs
                schedule.run_pending()
                
                # Log current status every 10 minutes
                current_time = time.time()
                if not hasattr(self, '_last_status_log'):
                    self._last_status_log = current_time
                elif current_time - self._last_status_log >= 600:  # 10 minutes
                    self._log_scheduler_status()
                    self._last_status_log = current_time
                
                time.sleep(60)  # Check every minute for pending jobs
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue running even if there's an error
    
    def _run_freshservice_sync(self):
        """Run the Freshservice onboarding sync"""
        try:
            logger.info("Running scheduled Freshservice onboarding sync...")
            
            # Import here to avoid circular imports
            from scripts.freshservice.sync_onboarding import FreshserviceOnboardingSync
            from database import SessionLocal
            from crud import ScriptLogCRUD
            from schemas import ScriptLogCreate
            from models import ScriptStatus
            
            # Create database session
            db = SessionLocal()
            
            try:
                # Create log entry for scheduled sync
                log_data = ScriptLogCreate(
                    user_id=None,  # System-initiated
                    script_type="freshservice",
                    script_name="sync_onboarding",
                    status=ScriptStatus.RUNNING,
                    executed_by="system_scheduler",
                    additional_params='{"hours_back": 1, "automated": true}'
                )
                
                script_log = ScriptLogCRUD.create(db, log_data)
                start_time = time.time()
                
                # Execute the sync script
                sync_script = FreshserviceOnboardingSync()
                sync_script.user_data = {"hours_back": 1}  # Only check last hour
                
                result = sync_script.execute()
                execution_time = int(time.time() - start_time)
                
                # Update log with results
                status = "success" if result.get("status") == "completed" else "failed"
                output = f"Processed {result.get('tickets_processed', 0)} tickets, " \
                        f"Created {result.get('users_created', 0)} users, " \
                        f"Skipped {result.get('users_skipped', 0)} users"
                
                ScriptLogCRUD.update_completion(
                    db, script_log.id, status,
                    output=output,
                    error_message=result.get("error") if status == "failed" else None,
                    execution_time_seconds=execution_time
                )
                
                logger.info(f"Scheduled sync completed: {output}")
                
            except Exception as e:
                # Update log with error
                execution_time = int(time.time() - start_time) if 'start_time' in locals() else 0
                error_msg = str(e)
                
                if 'script_log' in locals():
                    ScriptLogCRUD.update_completion(
                        db, script_log.id, "failed",
                        error_message=error_msg,
                        execution_time_seconds=execution_time
                    )
                
                logger.error(f"Error in scheduled Freshservice sync: {error_msg}")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Critical error in scheduled sync: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        next_runs = []
        for job in schedule.jobs:
            next_runs.append({
                "job": str(job.job_func),
                "next_run": job.next_run.isoformat() if job.next_run else None
            })
        
        return {
            "running": self.running,
            "jobs_count": len(schedule.jobs),
            "next_runs": next_runs,
            "current_time": datetime.now().isoformat()
        }
    
    def _log_scheduler_status(self):
        """Log current scheduler status"""
        status = self.get_status()
        logger.info(f"Scheduler Status: Running={status['running']}, Jobs={status['jobs_count']}")
        for job_info in status['next_runs']:
            logger.info(f"  - {job_info['job']} | Next run: {job_info['next_run']}")

# Global scheduler instance
background_scheduler = BackgroundScheduler()

@asynccontextmanager
async def scheduler_lifespan():
    """Context manager for scheduler lifecycle"""
    try:
        background_scheduler.start()
        yield
    finally:
        background_scheduler.stop()
