from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import schedule
import logging
from database import get_db
from schemas import (
    OnboardingCreate, OnboardingUpdate, OnboardingResponse,
    OffboardingCreate, OffboardingUpdate, OffboardingResponse,
    DepartmentMappingCreate, DepartmentMappingUpdate, DepartmentMappingResponse,
    ScriptExecutionRequest, ScriptExecutionResponse, ScriptLogResponse,
    OffboardingScriptLogResponse
)
from crud import OnboardingCRUD, OffboardingCRUD, DepartmentMappingCRUD, ScriptLogCRUD, OffboardingScriptLogCRUD
from models import OnboardingStatus
from scripts.script_manager import script_manager
from auth import parse_user_from_sso_claims, UserPermission
from sqlalchemy import text

logger = logging.getLogger(__name__)
router = APIRouter()

def check_user_permission(user_email: str, required_permission: UserPermission, user_claims: Optional[str] = None):
    """Check if user has required permission"""
    if user_claims:
        try:
            authenticated_user = parse_user_from_sso_claims(json.loads(user_claims))
            if not authenticated_user.has_permission(required_permission):
                raise HTTPException(
                    status_code=403, 
                    detail=f"User {user_email} does not have permission {required_permission.value}. Required role: ADMIN or higher"
                )
            print(f"Permission check passed for {user_email} with role {authenticated_user.role}")
        except json.JSONDecodeError:
            print(f"Warning: Invalid SSO claims provided for {user_email}, allowing in development mode")
        except Exception as e:
            print(f"Warning: Permission check failed for {user_email}: {e}, allowing in development mode")
    else:
        print(f"Warning: No SSO claims provided for {user_email}, allowing in development mode")

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
    user_claims: Optional[str] = Query(None, description="SSO claims JSON for permission checking"),
    db: Session = Depends(get_db)
):
    """Delete an onboarding record - Admin only"""
    check_user_permission(user_email, UserPermission.DELETE_USER, user_claims)
    
    success = OnboardingCRUD.delete(db, onboarding_id, user_email)
    if not success:
        raise HTTPException(status_code=404, detail="Onboarding record not found")
    return {"message": "Onboarding record deleted successfully"}

# Bulk onboarding
@router.post("/onboarding/bulk/", response_model=List[OnboardingResponse])
def create_bulk_onboarding(
    onboardings: List[OnboardingCreate],
    user_email: str = Query(..., description="Email of the user creating the records"),
    user_claims: Optional[str] = Query(None, description="SSO claims JSON for permission checking"),
    db: Session = Depends(get_db)
):
    """Create multiple onboarding records - Admin and IT roles"""
    check_user_permission(user_email, UserPermission.BULK_ONBOARD, user_claims)
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
    user_email: str = Query(..., description="Email of the user creating the mapping"),
    user_claims: Optional[str] = Query(None, description="SSO claims JSON for permission checking"),
    db: Session = Depends(get_db)
):
    """Create a new department mapping - Admin and IT roles"""
    check_user_permission(user_email, UserPermission.MANAGE_SETTINGS, user_claims)
    
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
    user_email: str = Query(..., description="Email of the user updating the mapping"),
    user_claims: Optional[str] = Query(None, description="SSO claims JSON for permission checking"),
    db: Session = Depends(get_db)
):
    """Update a department mapping - Admin and IT roles"""
    check_user_permission(user_email, UserPermission.MANAGE_SETTINGS, user_claims)
    
    mapping = DepartmentMappingCRUD.update(db, mapping_id, dept_mapping_update)
    if not mapping:
        raise HTTPException(status_code=404, detail="Department mapping not found")
    return mapping

@router.delete("/department-mappings/{mapping_id}")
def delete_department_mapping(
    mapping_id: int, 
    user_email: str = Query(..., description="Email of the user deleting the mapping"),
    user_claims: Optional[str] = Query(None, description="SSO claims JSON for permission checking"),
    db: Session = Depends(get_db)
):
    """Delete a department mapping - Admin and IT roles"""
    check_user_permission(user_email, UserPermission.MANAGE_SETTINGS, user_claims)
    
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
            # Generate company email if missing
            company_email = user_data.company_email
            if not company_email:
                if user_data.username:
                    company_email = f"{user_data.username}@americor.com"
                elif user_data.display_name and user_data.display_last_name:
                    # Generate username from name if missing
                    username = f"{user_data.display_name.lower()}.{user_data.display_last_name.lower()}"
                    company_email = f"{username}@americor.com"
                else:
                    company_email = None
            
            script_input = {
                "id": user_data.id,
                "company": user_data.company,
                "legal_name": user_data.legal_name,
                "display_name": user_data.display_name,
                "display_last_name": user_data.display_last_name,
                "personal_email": user_data.personal_email,
                "company_email": company_email,
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
                "username": user_data.username or (f"{user_data.display_name.lower()}.{user_data.display_last_name.lower()}" if user_data.display_name and user_data.display_last_name else None),
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
        
        # Update onboarding status fields based on script execution results
        if request.user_id and result:
            user_data = OnboardingCRUD.get(db, request.user_id)
            if user_data:
                from models import ScriptStatus
                from datetime import datetime
                
                # Determine which status field to update based on script type and name
                status_value = ScriptStatus.SUCCESS if result.get("success") else ScriptStatus.FAILED
                current_time = datetime.now()
                
                update_data = {}
                
                if request.script_type == "jumpcloud" and request.script_name == "create_user":
                    update_data["jumpcloud_status"] = status_value
                    if result.get("success"):
                        update_data["jumpcloud_created_at"] = current_time
                        update_data["jumpcloud_error"] = None  # Clear any previous error
                    else:
                        update_data["jumpcloud_error"] = result.get("error", "Unknown error")
                        
                elif request.script_type == "jumpcloud" and request.script_name == "bind_machine":
                    update_data["bind_machine_status"] = status_value
                        
                elif request.script_type == "google" and request.script_name == "create_user":
                    update_data["google_status"] = status_value
                    if result.get("success"):
                        update_data["google_created_at"] = current_time
                        update_data["google_error"] = None  # Clear any previous error
                    else:
                        update_data["google_error"] = result.get("error", "Unknown error")
                        
                elif request.script_type == "google" and request.script_name == "add_aliases":
                    update_data["add_alias_status"] = status_value
                    
                elif request.script_type == "google" and request.script_name == "force_password_change":
                    update_data["force_pwd_change_status"] = status_value
                
                # Update the onboarding record if we have status updates
                if update_data:
                    for field, value in update_data.items():
                        setattr(user_data, field, value)
                    
                    db.commit()
                    db.refresh(user_data)
        
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

# Bulk operation endpoints
@router.post("/scripts/jumpcloud/create-user")
async def bulk_create_jumpcloud_user(
    request: ScriptExecutionRequest,
    user_email: str = Query(..., description="Email of the user executing the script"),
    db: Session = Depends(get_db)
):
    """Create JumpCloud account for a user"""
    if not request.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    script_request = ScriptExecutionRequest(
        script_type="jumpcloud",
        script_name="create_user",
        user_id=request.user_id,
        additional_params=request.additional_params
    )
    
    # Execute script and get result
    result = await execute_script(script_request, user_email, None, db)
    
    # Update onboarding record with JumpCloud status
    try:
        import json
        from crud import OnboardingCRUD
        from models import ScriptStatus
        from schemas import OnboardingUpdate
        from datetime import datetime
        
        user_data = OnboardingCRUD.get(db, request.user_id)
        if user_data:
            # Parse the nested result structure from execute_script
            script_result = {}
            if result.get("success") and result.get("output"):
                try:
                    output_data = json.loads(result["output"])
                    script_result = output_data.get("result", {})
                except json.JSONDecodeError:
                    script_result = {}
            
            # Check the actual status returned by the script
            script_status = script_result.get("status", "failed")
            is_success = script_status in ["created", "already_exists"]
            
            # Create OnboardingUpdate object with the status fields
            update_data = OnboardingUpdate(
                jumpcloud_status=ScriptStatus.SUCCESS if is_success else ScriptStatus.FAILED,
                jumpcloud_created_at=datetime.now() if is_success else None,
                jumpcloud_error=script_result.get("error") if not is_success else None
            )
            
            OnboardingCRUD.update(db, request.user_id, update_data, user_email)
            logger.info(f"Updated JumpCloud status for user {request.user_id}: {script_status} -> {update_data.jumpcloud_status}")
            
    except Exception as e:
        logger.error(f"Failed to update JumpCloud status for user {request.user_id}: {e}")
    
    return result

@router.post("/scripts/google/create-user")
async def bulk_create_google_user(
    request: ScriptExecutionRequest,
    user_email: str = Query(..., description="Email of the user executing the script"),
    db: Session = Depends(get_db)
):
    """Create Google Workspace account for a user"""
    if not request.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    script_request = ScriptExecutionRequest(
        script_type="google",
        script_name="create_user",
        user_id=request.user_id,
        additional_params=request.additional_params
    )
    
    # Execute script and get result
    result = await execute_script(script_request, user_email, None, db)
    
    # Update onboarding record with Google Workspace status
    try:
        import json
        from crud import OnboardingCRUD
        from models import ScriptStatus
        from schemas import OnboardingUpdate
        from datetime import datetime
        
        user_data = OnboardingCRUD.get(db, request.user_id)
        if user_data:
            # Parse the nested result structure from execute_script
            script_result = {}
            if result.get("success") and result.get("output"):
                try:
                    output_data = json.loads(result["output"])
                    script_result = output_data.get("result", {})
                except json.JSONDecodeError:
                    script_result = {}
            
            # Check the actual status returned by the script
            script_status = script_result.get("status", "failed")
            is_success = script_status in ["created", "already_exists"]
            
            # Create OnboardingUpdate object with the status fields
            update_data = OnboardingUpdate(
                google_status=ScriptStatus.SUCCESS if is_success else ScriptStatus.FAILED,
                google_created_at=datetime.now() if is_success else None,
                google_error=script_result.get("error") if not is_success else None
            )
            
            OnboardingCRUD.update(db, request.user_id, update_data, user_email)
            logger.info(f"Updated Google Workspace status for user {request.user_id}: {script_status} -> {update_data.google_status}")
            
    except Exception as e:
        logger.error(f"Failed to update Google Workspace status for user {request.user_id}: {e}")
    
    return result

# Dashboard endpoints
@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    from sqlalchemy import func, case, and_
    from models import Onboarding, OnboardingStatus, Offboarding, OffboardingStatus, ScriptStatus, ScriptLog
    from datetime import datetime, timedelta
    
    # Get total users count
    total_users = db.query(func.count(Onboarding.id)).scalar() or 0
    
    # Get JumpCloud accounts created (users with successful JumpCloud status)
    jumpcloud_accounts = db.query(func.count(Onboarding.id)).filter(
        Onboarding.jumpcloud_status == ScriptStatus.SUCCESS
    ).scalar() or 0
    
    # Get Google Workspace accounts created (users with successful Google status)
    google_accounts = db.query(func.count(Onboarding.id)).filter(
        Onboarding.google_status == ScriptStatus.SUCCESS
    ).scalar() or 0
    
    # Get recent script executions (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_scripts = db.query(func.count(ScriptLog.id)).filter(
        ScriptLog.started_at >= seven_days_ago
    ).scalar() or 0
    
    # Get offboarding counts
    offboarding_count = db.query(func.count(Offboarding.id)).scalar() or 0
    
    return {
        "totalUsers": total_users,
        "jumpcloudAccounts": jumpcloud_accounts,
        "googleAccounts": google_accounts,
        "recentScripts": recent_scripts,
        "offboardedUsers": offboarding_count
    }

@router.get("/dashboard/recent-activity")
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get recent activity for dashboard - including sync logs"""
    try:
        # Get recent script logs for sync activity
        recent_logs = db.query(ScriptLogCRUD.model).filter(
            ScriptLogCRUD.model.script_name == "sync_onboarding"
        ).order_by(ScriptLogCRUD.model.created_at.desc()).limit(limit).all()
        
        activities = []
        
        for log in recent_logs:
            # Determine activity type and icon based on log data
            if log.executed_by in ["automated_scheduler", "system_scheduler"]:
                activity_type = "sync_auto"
                icon = "AUTO"
                title = "Automated Freshservice Sync"
            else:
                activity_type = "sync_manual"
                icon = "MANUAL"
                title = "Manual Freshservice Sync"
            
            # Parse additional params for more details
            try:
                import json
                params = json.loads(log.additional_params or '{}')
                hours_back = params.get('hours_back', 'N/A')
                automated = params.get('automated', False)
            except:
                hours_back = 'N/A'
                automated = False
            
            # Create description based on status and output
            if log.status.value == "success":
                # Try to extract numbers from output
                output = log.output or ""
                if "Users created:" in output:
                    import re
                    created_match = re.search(r'Users created: (\d+)', output)
                    processed_match = re.search(r'Tickets processed: (\d+)', output)
                    created = created_match.group(1) if created_match else "0"
                    processed = processed_match.group(1) if processed_match else "0"
                    description = f"Processed {processed} tickets, created {created} new users"
                else:
                    description = "Sync completed successfully"
                icon = "SUCCESS"
            elif log.status.value == "failed":
                description = f"Sync failed: {log.error_message or 'Unknown error'}"
                icon = "FAILED"
            elif log.status.value == "running":
                description = "Sync currently in progress..."
                icon = "RUNNING"
            else:
                description = "Sync status unknown"
                icon = "UNKNOWN"
            
            activity = {
                "id": f"script-log-{log.id}",
                "type": activity_type,
                "icon": icon,
                "title": title,
                "description": description,
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "user": "Freshservice Sync",
                "executedBy": log.executed_by or "Unknown",
                "status": log.status.value,
                "execution_time": f"{log.execution_time_seconds}s" if log.execution_time_seconds else None
            }
            activities.append(activity)
        
        # If no sync logs, add a placeholder
        if not activities:
            activities.append({
                "id": "no-activity",
                "type": "info",
                "icon": "NOTE",
                "title": "No Recent Sync Activity",
                "description": "No Freshservice sync activities found yet. Sync runs every 5 minutes automatically.",
                "timestamp": "2025-08-03T12:00:00",
                "user": "System",
                "executedBy": "System"
            })
        
        return activities
        
    except Exception as e:
        # Fallback to basic response if there's an error
        logger.error(f"Error fetching recent activity: {e}")
        return [{
            "id": "error-activity",
            "type": "error",
            "icon": "ERROR",
            "title": "Activity Error",
            "description": f"Error loading recent activity: {str(e)}",
            "timestamp": "2025-08-03T12:00:00",
            "user": "System",
            "executedBy": "System"
        }]

@router.get("/dashboard/scheduler-status")
def get_scheduler_status(db: Session = Depends(get_db)):
    """Get scheduler status for monitoring"""
    try:
        from scheduler import background_scheduler
        scheduler_status = background_scheduler.get_status()
        
        # Get last manual sync information from sync_logs
        last_manual_sync = None
        try:
            last_manual_query = db.execute(text("""
                SELECT started_at, status, tickets_processed, users_created, users_skipped
                FROM sync_logs 
                WHERE triggered_by = 'manual_trigger' 
                ORDER BY started_at DESC 
                LIMIT 1
            """))
            last_manual_result = last_manual_query.fetchone()
            
            if last_manual_result:
                last_manual_sync = {
                    "timestamp": last_manual_result[0].isoformat() if last_manual_result[0] else None,
                    "result": {
                        "status": last_manual_result[1],
                        "tickets_processed": last_manual_result[2] or 0,
                        "users_created": last_manual_result[3] or 0,
                        "users_skipped": last_manual_result[4] or 0
                    }
                }
            
        except Exception as db_error:
            logger.warning(f"Could not fetch last manual sync: {db_error}")
        
        # Create the final response with last_manual_sync included
        final_status = dict(scheduler_status)
        final_status["last_manual_sync"] = last_manual_sync
        
        return {
            "success": True,
            "status": final_status
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": {
                "running": False,
                "error": "Scheduler not available",
                "last_manual_sync": None
            }
        }


# Admin & Settings Endpoints for Automation
@router.post("/admin/sync/freshservice/manual")
async def trigger_manual_freshservice_sync(db: Session = Depends(get_db)):
    """Trigger a manual Freshservice onboarding sync"""
    try:
        import time
        import json
        from datetime import datetime
        
        # Insert directly into sync_logs table
        start_time = time.time()
        started_at = datetime.now()
        
        # Insert initial log entry
        db.execute(text("""
            INSERT INTO sync_logs (sync_type, sync_source, status, triggered_by, started_at, additional_data)
            VALUES (:sync_type, :sync_source, :status, :triggered_by, :started_at, :additional_data)
        """), {
            'sync_type': 'freshservice',
            'sync_source': 'Freshservice API',
            'status': 'running',
            'triggered_by': 'manual_trigger',
            'started_at': started_at,
            'additional_data': json.dumps({
                "hours_back": 24,
                "automated": False,
                "manual_trigger": True
            })
        })
        db.commit()
        
        # Get the inserted log ID in a DB-agnostic way
        try:
            dialect = db.bind.dialect.name if getattr(db, 'bind', None) else 'unknown'
            if dialect == 'sqlite':
                result_proxy = db.execute(text("SELECT last_insert_rowid()"))
                log_id = result_proxy.scalar()
            elif dialect in ('mysql', 'mariadb'):
                result_proxy = db.execute(text("SELECT LAST_INSERT_ID()"))
                log_id = result_proxy.scalar()
            else:
                # Fallback: find by timestamp and trigger
                result_proxy = db.execute(text("""
                    SELECT id FROM sync_logs 
                    WHERE triggered_by = :triggered_by AND started_at = :started_at
                    ORDER BY id DESC LIMIT 1
                """), { 'triggered_by': 'manual_trigger', 'started_at': started_at })
                row = result_proxy.fetchone()
                log_id = row[0] if row else None
        except Exception as id_err:
            logger.warning(f"Could not get last insert id: {id_err}. Falling back to MAX(id)")
            result_proxy = db.execute(text("SELECT MAX(id) FROM sync_logs"))
            log_id = result_proxy.scalar()
        
        # Execute the actual Freshservice sync script
        from scripts.freshservice.sync_onboarding import FreshserviceOnboardingSync
        
        sync_script = FreshserviceOnboardingSync()
        sync_script.user_data = {"hours_back": 24}  # Look back 24 hours for manual sync
        
        result = sync_script.execute()
        
        execution_time = int(time.time() - start_time)
        completed_at = datetime.now()
        
        # Process real results
        status = "success" if result.get("status") == "completed" else "failed"
        tickets_processed = result.get('tickets_processed', 0)
        users_created = result.get('users_created', 0)
        users_skipped = result.get('users_skipped', 0)
        execution_logs = result.get('execution_logs', '')
        
        # Create detailed output message with execution logs (no emojis for DB compatibility)
        summary = f"Manual sync completed: {tickets_processed} tickets processed, {users_created} users created, {users_skipped} users skipped. Execution time: {execution_time}s"
        output = f"{summary}\n\nDetailed Execution Log:\n{execution_logs}" if execution_logs else summary
        error_message = result.get('error', '') if status == "failed" else None
        
        db.execute(text("""
            UPDATE sync_logs 
            SET status = :status, completed_at = :completed_at, 
                execution_time_seconds = :execution_time,
                tickets_processed = :tickets_processed,
                users_created = :users_created,
                users_skipped = :users_skipped,
                output_message = :output_message,
                error_message = :error_message
            WHERE id = :log_id
        """), {
            'status': status,
            'completed_at': completed_at,
            'execution_time': execution_time,
            'tickets_processed': tickets_processed,
            'users_created': users_created,
            'users_skipped': users_skipped,
            'output_message': output,
            'error_message': error_message,
            'log_id': log_id
        })
        
        db.commit()
        
        return {
            "success": status == "success",
            "message": output,
            "result": {
                "status": status,
                "tickets_processed": tickets_processed,
                "users_created": users_created,
                "users_skipped": users_skipped,
                "execution_time": execution_time
            },
            "log_id": log_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Manual Freshservice sync failed: {str(e)}",
            "error": str(e)
        }


@router.post("/admin/test-sync")
async def test_sync_endpoint(db: Session = Depends(get_db)):
    """Test sync endpoint to isolate the issue"""
    try:
        return {
            "success": True,
            "message": "Test endpoint working perfectly!",
            "timestamp": "2025-08-03T17:25:00Z"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Test failed: {str(e)}",
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


# Dedicated Sync Logs Endpoint 
@router.get("/admin/sync/logs")
async def get_sync_logs(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get sync logs from the dedicated sync_logs table"""
    try:
        # Execute query with proper session handling
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
        rows = result.fetchall()
        logs = []
        
        for row in rows:
            logs.append({
                "id": row[0],
                "sync_type": row[1],
                "sync_source": row[2],
                "status": row[3],
                "triggered_by": row[4],
                "started_at": row[5].isoformat() if row[5] else None,
                "completed_at": row[6].isoformat() if row[6] else None,
                "execution_time_seconds": row[7],
                "tickets_processed": row[8] or 0,
                "users_created": row[9] or 0,
                "users_skipped": row[10] or 0,
                "output_message": row[11],
                "error_message": row[12]
            })
        
        db.commit()  # Explicitly commit the transaction
        logger.info(f"Successfully returning {len(logs)} sync logs")
        
        return {"success": True, "logs": logs, "total_count": len(logs)}
        
    except Exception as e:
        db.rollback()  # Rollback on error
        logger.error(f"Error fetching sync logs: {e}")
        return {"success": False, "error": str(e), "logs": []}

# Offboarding endpoints
@router.post("/offboarding/", response_model=OffboardingResponse)
def create_offboarding(
    offboarding: OffboardingCreate,
    user_email: str = Query(..., description="Email of the user creating the record"),
    db: Session = Depends(get_db)
):
    """Create a new offboarding record"""
    # Check if company email already exists
    existing = OffboardingCRUD.get_by_email(db, offboarding.company_email)
    if existing:
        raise HTTPException(status_code=400, detail="Offboarding record for this email already exists")
    
    # Set the created_by field from the authenticated user
    if not offboarding.created_by:
        offboarding.created_by = user_email
    
    return OffboardingCRUD.create(db, offboarding, user_email)

@router.get("/offboarding/{offboarding_id}", response_model=OffboardingResponse)
def get_offboarding(offboarding_id: int, db: Session = Depends(get_db)):
    """Get a specific offboarding record"""
    offboarding = OffboardingCRUD.get(db, offboarding_id)
    if not offboarding:
        raise HTTPException(status_code=404, detail="Offboarding record not found")
    return offboarding

@router.get("/offboarding/", response_model=List[OffboardingResponse])
def get_all_offboarding(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all offboarding records with optional search"""
    if search:
        return OffboardingCRUD.search(db, search, skip, limit)
    return OffboardingCRUD.get_all(db, skip, limit)

@router.put("/offboarding/{offboarding_id}", response_model=OffboardingResponse)
def update_offboarding(
    offboarding_id: int,
    offboarding_update: OffboardingUpdate,
    user_email: str = Query(..., description="Email of the user updating the record"),
    db: Session = Depends(get_db)
):
    """Update an offboarding record"""
    offboarding = OffboardingCRUD.update(db, offboarding_id, offboarding_update, user_email)
    if not offboarding:
        raise HTTPException(status_code=404, detail="Offboarding record not found")
    return offboarding

@router.delete("/offboarding/{offboarding_id}")
def delete_offboarding(
    offboarding_id: int,
    user_email: str = Query(..., description="Email of the user deleting the record"),
    user_claims: Optional[str] = Query(None, description="SSO claims JSON for permission checking"),
    db: Session = Depends(get_db)
):
    """Delete an offboarding record - Admin only"""
    check_user_permission(user_email, UserPermission.DELETE_USER, user_claims)
    
    success = OffboardingCRUD.delete(db, offboarding_id, user_email)
    if not success:
        raise HTTPException(status_code=404, detail="Offboarding record not found")
    return {"message": "Offboarding record deleted successfully"}

# Offboarding Script Log endpoints
@router.get("/offboarding/{offboarding_id}/script-logs", response_model=List[OffboardingScriptLogResponse])
def get_offboarding_script_logs(
    offboarding_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get script logs for a specific offboarding record"""
    logs = OffboardingScriptLogCRUD.get_by_offboarding_id(db, offboarding_id, limit)
    return logs

@router.get("/offboarding/script-logs", response_model=List[OffboardingScriptLogResponse])
def get_all_offboarding_script_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all offboarding script logs"""
    logs = OffboardingScriptLogCRUD.get_all(db, skip, limit)
    return logs

@router.get("/offboarding/script-logs/{log_id}", response_model=OffboardingScriptLogResponse)
def get_offboarding_script_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific offboarding script log"""
    log = OffboardingScriptLogCRUD.get(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Script log not found")
    return log

@router.post("/offboarding/{offboarding_id}/execute-script", response_model=ScriptExecutionResponse)
async def execute_offboarding_script(
    offboarding_id: int,
    request: ScriptExecutionRequest,
    user_email: str = Query(..., description="Email of the user executing the script"),
    user_claims: Optional[str] = Query(None, description="SSO claims JSON for permission checking"),
    db: Session = Depends(get_db)
):
    """Execute an offboarding script with specialized logging"""
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

        # Get offboarding data
        offboarding_data = OffboardingCRUD.get(db, offboarding_id)
        if not offboarding_data:
            raise HTTPException(status_code=404, detail="Offboarding record not found")

        # Create log entry for the script execution
        from schemas import OffboardingScriptLogCreate
        log_data = OffboardingScriptLogCreate(
            offboarding_id=offboarding_id,
            script_type=request.script_type,
            script_name=request.script_name,
            executed_by=user_email,
            additional_params=request.additional_params
        )
        script_log = OffboardingScriptLogCRUD.create(db, log_data)

        # Convert offboarding data to dict for script execution
        # Include essential fields and hostname for Automox scripts
        script_input = {
            "id": offboarding_data.id,
            "first_name": offboarding_data.first_name,
            "last_name": offboarding_data.last_name,
            "company_email": offboarding_data.company_email,
            "hostname": getattr(offboarding_data, 'hostname', None),
            # Optional fields that may be useful for logging/context
            "requested_by": getattr(offboarding_data, 'requested_by', None),
            "notes": getattr(offboarding_data, 'notes', None)
        }
        
        try:
            # Execute the script using the script manager
            from scripts.script_manager import script_manager
            import time
            
            start_time = time.time()
            
            print(f"🔍 DEBUG: About to execute script: {request.script_type}/{request.script_name}")
            
            # Execute the script
            result = await script_manager.execute_script(
                script_type=request.script_type,
                script_name=request.script_name,
                user_data=script_input,
                db=db,
                executed_by=user_email,
                user_id=offboarding_id,
                additional_params=request.additional_params
            )
            
            print(f"🔍 DEBUG: Script execution completed")
            
            end_time = time.time()
            execution_time = int(end_time - start_time)
            
            # Update the log with results - map warning to SUCCESS with special output
            from models import ScriptStatus
            script_status = ScriptStatus.FAILED  # default
            output_data = result.get("output", "")
            
            # Debug logging
            print(f"🔍 DEBUG: Script result: {result}")
            print(f"🔍 DEBUG: result.get('success'): {result.get('success', False)}")
            print(f"🔍 DEBUG: result.get('result'): {result.get('result', {})}")
            
            # Determine the script status for logging
            script_execution_status = None
            if result.get("success", False):
                print("🔍 DEBUG: Entered success branch")
                # Check if there's parsed output with more specific status
                parsed_output = result.get("parsed_output", {})
                print(f"🔍 DEBUG: parsed_output: {parsed_output}")
                
                nested_result = {}
                if isinstance(parsed_output, dict):
                    # Get the nested result from parsed output
                    nested_result = parsed_output.get("result", {})
                    print(f"🔍 DEBUG: nested_result from parsed_output: {nested_result}")
                    
                    # Handle double-nested result structure (result.result.result)
                    if "result" in nested_result and isinstance(nested_result["result"], dict):
                        print(f"🔍 DEBUG: Found double-nested result: {nested_result['result']}")
                        nested_result = nested_result["result"]
                    
                    # First check for status field
                    if "status" in nested_result:
                        nested_status = nested_result["status"].lower()
                        print(f"🔍 DEBUG: nested_status: {nested_status}")
                        if nested_status in ["success", "completed"]:
                            print("🔍 DEBUG: Status is success/completed - setting SUCCESS")
                            script_status = ScriptStatus.SUCCESS
                            # Always use clean, short status messages for database storage
                            if request.script_type.lower() == "automox":
                                script_execution_status = "AGENT REMOVED"
                            elif request.script_type.lower() == "jumpcloud":
                                script_execution_status = "USER TERMINATED"
                            elif request.script_type.lower() in ["google", "offboarding"]:
                                script_execution_status = "USER TERMINATED"
                        elif nested_status == "warning":
                            # Store as SUCCESS but preserve the warning info in output
                            script_status = ScriptStatus.SUCCESS
                            # Always use clean, short warning status messages
                            if request.script_type.lower() == "automox":
                                script_execution_status = "AGENT NOT FOUND"
                            elif request.script_type.lower() == "jumpcloud":
                                script_execution_status = "USER NOT FOUND"
                            elif request.script_type.lower() in ["google", "offboarding"]:
                                script_execution_status = "USER NOT FOUND"
                            # Add a marker to the output so frontend can detect warnings
                            if isinstance(result.get("output"), str) and '{"success": true, "result":' in result.get("output", ""):
                                # Output already contains the JSON with warning status
                                pass
                            else:
                                # Ensure the output contains the warning marker
                                output_data = f"WARNING_STATUS: {output_data}"
                        elif nested_status == "failed":
                            script_status = ScriptStatus.FAILED
                            # Use message if available, otherwise use default failure messages
                            if "message" in nested_result:
                                script_execution_status = nested_result["message"]
                            else:
                                # Map to user-friendly failure status
                                if request.script_type.lower() == "automox":
                                    script_execution_status = "REMOVAL FAILED"
                                elif request.script_type.lower() == "jumpcloud":
                                    script_execution_status = "TERMINATION FAILED"
                                elif request.script_type.lower() in ["google", "offboarding"]:
                                    script_execution_status = "TERMINATION FAILED"
                    elif "message" in nested_result:
                        # Determine success/failure based on the message content and use clean status
                        message_lower = nested_result["message"].lower()
                        if "failed" in message_lower or "error" in message_lower:
                            script_status = ScriptStatus.FAILED
                            # Use clean failure messages
                            if request.script_type.lower() == "automox":
                                script_execution_status = "REMOVAL FAILED"
                            elif request.script_type.lower() == "jumpcloud":
                                script_execution_status = "TERMINATION FAILED"
                            elif request.script_type.lower() in ["google", "offboarding"]:
                                script_execution_status = "TERMINATION FAILED"
                        elif "not found" in message_lower or "unknown" in message_lower:
                            script_status = ScriptStatus.SUCCESS  # These are valid responses, not failures
                            # Use clean warning messages
                            if request.script_type.lower() == "automox":
                                script_execution_status = "AGENT NOT FOUND"
                            elif request.script_type.lower() == "jumpcloud":
                                script_execution_status = "USER NOT FOUND"
                            elif request.script_type.lower() in ["google", "offboarding"]:
                                script_execution_status = "USER NOT FOUND"
                        else:
                            script_status = ScriptStatus.SUCCESS
                            # Use clean success messages
                            if request.script_type.lower() == "automox":
                                script_execution_status = "AGENT REMOVED"
                            elif request.script_type.lower() == "jumpcloud":
                                script_execution_status = "USER TERMINATED"
                            elif request.script_type.lower() in ["google", "offboarding"]:
                                script_execution_status = "USER TERMINATED"
                else:
                    # No nested result, use top-level success
                    script_status = ScriptStatus.SUCCESS
                    if request.script_type.lower() == "automox":
                        script_execution_status = "AGENT REMOVED"
                    elif request.script_type.lower() == "jumpcloud":
                        script_execution_status = "USER TERMINATED"
                    elif request.script_type.lower() in ["google", "offboarding"]:
                        script_execution_status = "USER TERMINATED"
            else:
                # Failed execution
                if request.script_type.lower() == "automox":
                    script_execution_status = "REMOVAL FAILED"
                elif request.script_type.lower() == "jumpcloud":
                    script_execution_status = "TERMINATION FAILED"
                elif request.script_type.lower() in ["google", "offboarding"]:
                    script_execution_status = "TERMINATION FAILED"
            
            # Update the script status in the offboarding record
            print(f"🔍 DEBUG: script_execution_status = {script_execution_status}")
            print(f"🔍 DEBUG: script_status = {script_status}")
            if script_execution_status:
                update_data = {}
                
                # Extract hostname information for JumpCloud scripts
                if request.script_type.lower() == "jumpcloud" and result.get("parsed_output"):
                    parsed_output = result.get("parsed_output", {})
                    if isinstance(parsed_output, dict):
                        nested_result = parsed_output.get("result", {})
                        if isinstance(nested_result, dict) and nested_result.get("hostnames"):
                            update_data["hostname"] = nested_result["hostnames"]
                            print(f"🔍 DEBUG: Extracted hostnames for database: {nested_result['hostnames']}")
                
                # Set status fields
                if request.script_type.lower() == "automox":
                    update_data["automox_status"] = script_execution_status
                elif request.script_type.lower() == "jumpcloud":
                    update_data["jumpcloud_status"] = script_execution_status
                elif request.script_type.lower() in ["google", "offboarding"]:
                    update_data["google_status"] = script_execution_status
                
                print(f"🔍 DEBUG: update_data = {update_data}")
                if update_data:
                    offboarding_update = OffboardingUpdate(**update_data)
                    print(f"🔍 DEBUG: About to update database with: {update_data}")
                    OffboardingCRUD.update(db, offboarding_id, offboarding_update, offboarding_data.company_email)
                    print(f"🔍 DEBUG: Database update completed")
            
            # If no specific status was set, check the script log status and use a default message
            if not script_execution_status:
                # Fallback: use the script log status to determine a basic status message
                if script_status == ScriptStatus.SUCCESS:
                    fallback_status = "COMPLETED"
                elif script_status == ScriptStatus.FAILED:
                    fallback_status = "FAILED"
                else:
                    fallback_status = "UNKNOWN"
                
                update_data = {}
                if request.script_type.lower() == "automox":
                    update_data["automox_status"] = fallback_status
                elif request.script_type.lower() == "jumpcloud":
                    update_data["jumpcloud_status"] = fallback_status
                elif request.script_type.lower() in ["google", "offboarding"]:
                    update_data["google_status"] = fallback_status
                
                if update_data:
                    offboarding_update = OffboardingUpdate(**update_data)
                    OffboardingCRUD.update(db, offboarding_id, offboarding_update, offboarding_data.company_email)
            
            # Update the offboarding script log with completion details
            OffboardingScriptLogCRUD.update_completion(
                db, 
                script_log.id,
                status=script_status.value,  # Convert enum to string
                output=output_data,
                error_message=result.get("error") if script_status == ScriptStatus.FAILED else None,
                execution_time_seconds=execution_time
            )
            
            return result
            
        except Exception as script_error:
            # Update log with error - handle potential database rollback
            try:
                OffboardingScriptLogCRUD.update_completion(
                    db,
                    script_log.id,
                    status="failed",
                    error_message=str(script_error)
                )
            except Exception as db_error:
                print(f"Database error while updating script log: {str(db_error)}")
                # Continue with the original script error
            raise
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Offboarding script execution failed: {str(e)}")

