"""
Dedicated API endpoints for sync logs management
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/admin/sync/logs")
async def get_sync_logs(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get sync logs from the dedicated sync_logs table"""
    try:
        query = text("""
            SELECT id, sync_type, sync_source, status, triggered_by,
                   started_at, completed_at, execution_time_seconds,
                   tickets_processed, users_created, users_skipped,
                   output_message, error_message
            FROM sync_logs 
            ORDER BY started_at DESC 
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": limit})
        logs = []
        
        for row in result:
            logs.append({
                "id": row.id,
                "sync_type": row.sync_type,
                "sync_source": row.sync_source,
                "status": row.status,
                "triggered_by": row.triggered_by,
                "started_at": row.started_at.isoformat() if row.started_at else None,
                "completed_at": row.completed_at.isoformat() if row.completed_at else None,
                "execution_time_seconds": row.execution_time_seconds,
                "tickets_processed": row.tickets_processed or 0,
                "users_created": row.users_created or 0,
                "users_skipped": row.users_skipped or 0,
                "output_message": row.output_message,
                "error_message": row.error_message
            })
        
        return {"success": True, "logs": logs}
        
    except Exception as e:
        logger.error(f"Error fetching sync logs: {e}")
        return {"success": False, "error": str(e), "logs": []}

@router.post("/admin/sync/logs")
async def create_sync_log(
    sync_type: str = "freshservice",
    triggered_by: str = "manual",
    tickets_processed: int = 0,
    users_created: int = 0,
    users_skipped: int = 0,
    output_message: str = "",
    error_message: str = "",
    execution_time_seconds: int = 0,
    status: str = "success",
    db: Session = Depends(get_db)
):
    """Create a new sync log entry"""
    try:
        from datetime import datetime
        
        query = text("""
            INSERT INTO sync_logs 
            (sync_type, sync_source, status, triggered_by, started_at, completed_at, 
             execution_time_seconds, tickets_processed, users_created, users_skipped, 
             output_message, error_message)
            VALUES 
            (:sync_type, 'Freshservice Onboarding API', :status, :triggered_by, 
             NOW(), NOW(), :execution_time, :tickets_processed, :users_created, 
             :users_skipped, :output_message, :error_message)
        """)
        
        db.execute(query, {
            "sync_type": sync_type,
            "status": status,
            "triggered_by": triggered_by,
            "execution_time": execution_time_seconds,
            "tickets_processed": tickets_processed,
            "users_created": users_created,
            "users_skipped": users_skipped,
            "output_message": output_message,
            "error_message": error_message
        })
        
        db.commit()
        
        return {"success": True, "message": "Sync log created successfully"}
        
    except Exception as e:
        logger.error(f"Error creating sync log: {e}")
        db.rollback()
        return {"success": False, "error": str(e)}
