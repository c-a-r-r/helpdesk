from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import schedule
from database import get_db
from schemas import (
    OnboardingCreate, OnboardingUpdate, OnboardingResponse,
    DepartmentMappingCreate, DepartmentMappingUpdate, DepartmentMappingResponse,
    ScriptExecutionRequest, ScriptExecutionResponse, ScriptLogResponse
)
from crud import OnboardingCRUD, DepartmentMappingCRUD, ScriptLogCRUD
from models import OnboardingStatus
from scripts.script_manager import script_manager
from scripts.freshservice.sync_onboarding import FreshserviceOnboardingSync
from auth import parse_user_from_sso_claims, UserPermission

router = APIRouter()

# Onboarding endpoints
@router.post("/onboarding/", response_model=OnboardingResponse)
def create_onboarding(
    onboarding: OnboardingCreate,
    user_email: str = Query(..., description="Email of the user creating the record"),
    db: Session = Depends(get_db)
):
    """Create a new onboarding record"""
    # Check if zoom and five9 are both true, which is not allowed
    if onboarding.zoom and onboarding.five9:
        raise HTTPException(status_code=400, detail="A user cannot have both zoom and five9 enabled at the same time")
    
    # Check if personal email already exists
    existing_personal = OnboardingCRUD.get_by_personal_email(db, onboarding.personal_email)
    if existing_personal:
        raise HTTPException(status_code=400, detail="Personal email already exists")
    
    # Check if company email already exists (will be auto-generated based on username)
    if onboarding.company_email:
        existing_company = OnboardingCRUD.get_by_company_email(db, onboarding.company_email)
        if existing_company:
            raise HTTPException(status_code=400, detail="Company email already exists")
    
    return OnboardingCRUD.create(db, onboarding, user_email)

@router.get("/onboarding/{onboarding_id}", response_model=OnboardingResponse)
def get_onboarding(onboarding_id: int, db: Session = Depends(get_db)):
    """Get a specific onboarding record"""
    onboarding = OnboardingCRUD.get(db, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding record not found")
    return onboarding

@router.get("/onboarding/", response_model=List[OnboardingResponse])
def get_all_onboarding(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search in name, email, department, or ticket number"),
    status: Optional[OnboardingStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get all onboarding records with optional search and filtering"""
    if search:
        onboardings = OnboardingCRUD.search(db, search, skip, limit)
    else:
        onboardings = OnboardingCRUD.get_all(db, skip, limit)
    
    # Filter by status if provided
    if status:
        onboardings = [o for o in onboardings if o.status == status]
    
    return onboardings

@router.put("/onboarding/{onboarding_id}", response_model=OnboardingResponse)
def update_onboarding(
    onboarding_id: int,
    onboarding_update: OnboardingUpdate,
    user_email: str = Query(..., description="Email of the user updating the record"),
    db: Session = Depends(get_db)
):
    """Update an onboarding record"""
    # Check if zoom and five9 are both true, which is not allowed
    if onboarding_update.zoom and onboarding_update.five9:
        raise HTTPException(status_code=400, detail="A user cannot have both zoom and five9 enabled at the same time")
    onboarding = OnboardingCRUD.update(db, onboarding_id, onboarding_update, user_email)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding record not found")
    return onboarding

@router.delete("/onboarding/{onboarding_id}")
def delete_onboarding(
    onboarding_id: int,
    user_email: str = Query(..., description="Email of the user deleting the record"),
    db: Session = Depends(get_db)
):
    """Delete an onboarding record"""
    success = OnboardingCRUD.delete(db, onboarding_id, user_email)
    if not success:
        raise HTTPException(status_code=404, detail="Onboarding record not found")
    return {"message": "Onboarding record deleted successfully"}

# Bulk onboarding
@router.post("/onboarding/bulk/", response_model=List[OnboardingResponse])
def create_bulk_onboarding(
    onboardings: List[OnboardingCreate],
    user_email: str = Query(..., description="Email of the user creating the records"),
    db: Session = Depends(get_db)
):
    """Create multiple onboarding records"""
    created_records = []
    errors = []
    
    for i, onboarding in enumerate(onboardings):
        try:
            # Check if personal email already exists
            existing_personal = OnboardingCRUD.get_by_personal_email(db, onboarding.personal_email)
            if existing_personal:
                errors.append(f"Record {i+1}: Personal email {onboarding.personal_email} already exists")
                continue
                
            # Check if company email already exists 
            if onboarding.company_email:
                existing_company = OnboardingCRUD.get_by_company_email(db, onboarding.company_email)
                if existing_company:
                    errors.append(f"Record {i+1}: Company email {onboarding.company_email} already exists")
                    continue
            
            created = OnboardingCRUD.create(db, onboarding, user_email)
            created_records.append(created)
        except Exception as e:
            errors.append(f"Record {i+1}: {str(e)}")
    
    if errors and not created_records:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return created_records

# Department mapping endpoints
@router.post("/department-mappings/", response_model=DepartmentMappingResponse)
def create_department_mapping(
    dept_mapping: DepartmentMappingCreate,
    db: Session = Depends(get_db)
):
    """Create a new department mapping"""
    # Check if department already exists
    existing = DepartmentMappingCRUD.get_by_department(db, dept_mapping.department)
    if existing:
        raise HTTPException(status_code=400, detail="Department mapping already exists")
    
    return DepartmentMappingCRUD.create(db, dept_mapping)

@router.get("/department-mappings/", response_model=List[DepartmentMappingResponse])
def get_all_department_mappings(db: Session = Depends(get_db)):
    """Get all department mappings"""
    return DepartmentMappingCRUD.get_all(db)

@router.get("/department-mappings/{department}")
def get_department_ou(department: str, db: Session = Depends(get_db)):
    """Get OU for a specific department"""
    mapping = DepartmentMappingCRUD.get_by_department(db, department)
    if not mapping:
        raise HTTPException(status_code=404, detail="Department mapping not found")
    return {"department": department, "department_ou": mapping.department_ou}

@router.put("/department-mappings/{mapping_id}", response_model=DepartmentMappingResponse)
def update_department_mapping(
    mapping_id: int,
    dept_mapping_update: DepartmentMappingUpdate,
    db: Session = Depends(get_db)
):
    """Update a department mapping"""
    mapping = DepartmentMappingCRUD.update(db, mapping_id, dept_mapping_update)
    if not mapping:
        raise HTTPException(status_code=404, detail="Department mapping not found")
    return mapping

@router.delete("/department-mappings/{mapping_id}")
def delete_department_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """Delete a department mapping"""
    success = DepartmentMappingCRUD.delete(db, mapping_id)
    if not success:
        raise HTTPException(status_code=404, detail="Department mapping not found")

# Script execution endpoints
@router.post("/scripts/execute", response_model=ScriptExecutionResponse)
async def execute_script(
    request: ScriptExecutionRequest,
    user_email: str = Query(..., description="Email of the user executing the script"),
    user_claims: Optional[str] = Query(None, description="SSO claims JSON for permission checking"),
    db: Session = Depends(get_db)
):
    """Execute a user management script with database logging"""
    try:
        # Check user permissions for script execution
        if user_claims:
            try:
                import json
                claims = json.loads(user_claims)
                authenticated_user = parse_user_from_sso_claims(claims)
                
                if not authenticated_user.has_permission(UserPermission.EXECUTE_SCRIPTS):
                    raise HTTPException(
                        status_code=403, 
                        detail=f"User {user_email} does not have permission to execute scripts. Required role: ADMIN or IT"
                    )
                    
                print(f"Permission check passed for {user_email} with role {authenticated_user.role}")
                
            except json.JSONDecodeError:
                print(f"Warning: Invalid SSO claims provided for {user_email}, skipping permission check")
            except Exception as e:
                print(f"Warning: Permission check failed for {user_email}: {e}, skipping permission check")
        else:
            # For development/testing, allow admin email without claims
            admin_emails = ["cristian.rodriguez@americor.com", "admin@americor.com"]
            if user_email not in admin_emails:
                print(f"Warning: No SSO claims provided for {user_email}, skipping permission check in development mode")
        
        # Get user data if user_id is provided
        if request.user_id:
            user_data = OnboardingCRUD.get(db, request.user_id)
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Convert user data to dict for script execution
            script_input = {
                "id": user_data.id,
                "company": user_data.company,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "display_name": user_data.display_name,
                "personal_email": user_data.personal_email,
                "company_email": user_data.company_email,
                "phone_number": user_data.phone_number,
                "title": user_data.title,
                "manager": user_data.manager,
                "department": user_data.department,
                "start_date": user_data.start_date.isoformat() if user_data.start_date else None,
                "location_first_day": user_data.location_first_day,
                "address_type": user_data.address_type.value if user_data.address_type else None,
                "street_name": user_data.street_name,
                "city": user_data.city,
                "state": user_data.state,
                "zip_code": user_data.zip_code,
                "username": user_data.username,
                "department_ou": user_data.department_ou,
                "hostname": user_data.hostname,
                "password": user_data.password,
                "credit9_alias": user_data.credit9_alias,
                "advantageteam_alias": user_data.advantageteam_alias,
                "status": user_data.status.value if user_data.status else None,
                "ticket_number": user_data.ticket_number,
                "notes": user_data.notes,
                "extra_details": user_data.extra_details
            }
        else:
            # Use only additional params if no user_id provided
            script_input = {}
            if not request.additional_params:
                raise HTTPException(status_code=400, detail="Either user_id or additional_params must be provided")
        
        # Execute the script with database logging
        result = await script_manager.execute_script(
            script_type=request.script_type,
            script_name=request.script_name,
            user_data=script_input,
            db=db,
            executed_by=user_email,
            user_id=request.user_id or 0,  # Use 0 if no specific user
            additional_params=request.additional_params
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Script execution failed: {str(e)}")

@router.get("/scripts/available")
def get_available_scripts():
    """Get list of available scripts"""
    return script_manager.get_available_scripts()

@router.get("/scripts/logs", response_model=List[ScriptLogResponse])
def get_script_logs(
    user_id: Optional[int] = Query(None, description="Filter logs by user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get script execution logs"""
    if user_id:
        return ScriptLogCRUD.get_by_user(db, user_id, skip, limit)
    else:
        return ScriptLogCRUD.get_all(db, skip, limit)

@router.get("/scripts/logs/{log_id}", response_model=ScriptLogResponse)
def get_script_log(log_id: int, db: Session = Depends(get_db)):
    """Get a specific script log"""
    log = ScriptLogCRUD.get(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Script log not found")
    return log

# Dashboard endpoints
@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    from sqlalchemy import func, case
    from models import Onboarding, OnboardingStatus
    
    # Get total counts by status
    stats = db.query(
        func.count(Onboarding.id).label('total'),
        func.sum(case((Onboarding.status == OnboardingStatus.COMPLETED, 1), else_=0)).label('completed'),
        func.sum(case((Onboarding.status == OnboardingStatus.PENDING, 1), else_=0)).label('pending'),
        func.sum(case((Onboarding.status == OnboardingStatus.IN_PROGRESS, 1), else_=0)).label('in_progress'),
        func.sum(case((Onboarding.status == OnboardingStatus.FAILED, 1), else_=0)).label('failed')
    ).first()
    
    return {
        "totalUsers": stats.total or 0,
        "completedUsers": stats.completed or 0,
        "pendingUsers": stats.pending or 0,
        "inProgressUsers": stats.in_progress or 0,
        "offboardedUsers": stats.failed or 0  # Map failed to offboarded for frontend
    }

@router.get("/dashboard/recent-activity")
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get recent activity for dashboard"""
    # For now, return a simple response with placeholder data
    # since we need to get the endpoint working first
    
    activities = [
        {
            "id": "activity-1",
            "type": "status_change",
            "icon": "⏳",
            "title": "Recent Onboarding Activity",
            "description": "Onboarding activities are being tracked",
            "timestamp": "2025-01-01T12:00:00",
            "user": "System",
            "updatedBy": "System"
        }
    ]
    
    return activities[:limit]


# Admin & Settings Endpoints for Automation
@router.post("/admin/sync/freshservice/manual")
async def trigger_manual_freshservice_sync(db: Session = Depends(get_db)):
    """Trigger a manual Freshservice onboarding sync"""
    try:
        script = FreshserviceOnboardingSync()
        result = script.execute()
        
        if result.get("status") == "completed":
            return {
                "success": True,
                "message": f"Manual Freshservice sync completed successfully",
                "result": result
            }
        else:
            return {
                "success": False,
                "message": "Manual Freshservice sync failed",
                "error": result.get("error", "Unknown error")
            }
    except Exception as e:
        return {
            "success": False,
            "message": "Manual Freshservice sync failed",
            "error": str(e)
        }


@router.get("/admin/scheduler/status")
async def get_scheduler_status():
    """Get current status of the background scheduler"""
    try:
        from scheduler import background_scheduler
        
        # Check if scheduler exists and is running
        is_running = background_scheduler and hasattr(background_scheduler, 'running') and background_scheduler.running
        
        # Get next run time for freshservice sync if scheduler is running
        next_run = None
        if is_running:
            # Get jobs from the schedule library
            jobs = schedule.jobs
            for job in jobs:
                # Check if this is a freshservice job by looking at the job's function
                if hasattr(job, 'job_func') and 'freshservice' in str(job.job_func):
                    next_run = job.next_run.isoformat() if job.next_run else None
                    break
        
        return {
            "scheduler_running": is_running,
            "next_freshservice_sync": next_run,
            "automation_enabled": True,
            "total_scheduled_jobs": len(schedule.jobs) if is_running else 0
        }
    except Exception as e:
        return {
            "scheduler_running": False,
            "next_freshservice_sync": None,
            "automation_enabled": False,
            "total_scheduled_jobs": 0,
            "error": str(e)
        }


@router.get("/admin/sync/freshservice/history")
async def get_freshservice_sync_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent Freshservice sync execution history"""
    try:
        # Get recent freshservice sync logs
        logs = ScriptLogCRUD.get_by_script_type(db, "freshservice", limit=limit)
        
        history = []
        for log in logs:
            history.append({
                "id": log.id,
                "started_at": log.started_at.isoformat(),
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "script_type": log.script_type,
                "script_name": log.script_name,
                "status": log.status.value,
                "executed_by": log.executed_by,
                "execution_time_seconds": log.execution_time_seconds,
                "output": log.output,
                "error_message": log.error_message
            })
        
        return {
            "success": True,
            "history": history,
            "total_records": len(history)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "history": []
        }


@router.get("/api/v1/admin/scheduler/status")
async def get_scheduler_status():
    """Get current status of the background scheduler"""
    try:
        from scheduler import background_scheduler
        
        # Check if scheduler exists and is running
        is_running = background_scheduler and background_scheduler.running
        
        # Get next run time for freshservice sync if scheduler is running
        next_run = None
        if is_running and background_scheduler.scheduler:
            jobs = background_scheduler.scheduler.jobs
            for job in jobs:
                if 'freshservice' in str(job.func):
                    next_run = job.next_run_time.isoformat() if job.next_run_time else None
                    break
        
        return {
            "scheduler_running": is_running,
            "next_freshservice_sync": next_run,
            "automation_enabled": True
        }
    except Exception as e:
        return {
            "scheduler_running": False,
            "next_freshservice_sync": None,
            "automation_enabled": False,
            "error": str(e)
        }


@router.get("/api/v1/admin/sync/freshservice/history")
async def get_freshservice_sync_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent Freshservice sync execution history"""
    try:
        # Get recent freshservice sync logs
        logs = ScriptLogCRUD.get_by_script_type(db, "freshservice_sync", limit=limit)
        
        history = []
        for log in logs:
            history.append({
                "id": log.id,
                "started_at": log.started_at.isoformat(),
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "script_type": log.script_type,
                "script_name": log.script_name,
                "status": log.status.value,
                "executed_by": log.executed_by,
                "execution_time_seconds": log.execution_time_seconds,
                "output": log.output,
                "error_message": log.error_message
            })
        
        return history
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "history": []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "history": []
        }
