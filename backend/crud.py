from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from models import Onboarding, Offboarding, DepartmentMapping, AuditLog, ScriptLog, OffboardingScriptLog
from schemas import OnboardingCreate, OnboardingUpdate, OffboardingCreate, OffboardingUpdate, DepartmentMappingCreate, DepartmentMappingUpdate, ScriptLogCreate, OffboardingScriptLogCreate
from typing import List, Optional
import json
import string
import secrets

class OnboardingCRUD:
    @staticmethod
    def create(db: Session, onboarding: OnboardingCreate, user_email: str) -> Onboarding:
        db_onboarding = Onboarding(**onboarding.dict())
        # Set created_by field - use user_email if provided, otherwise it's from sync
        db_onboarding.created_by = user_email if user_email else 'freshdesk-sync'
        db.add(db_onboarding)
        db.commit()
        db.refresh(db_onboarding)
        
        # Create audit log
        OnboardingCRUD._create_audit_log(
            db, "onboarding", db_onboarding.id, "CREATE", 
            None, onboarding.dict(), user_email
        )
        
        return db_onboarding

    @staticmethod
    def get(db: Session, onboarding_id: int) -> Optional[Onboarding]:
        return db.query(Onboarding).filter(Onboarding.id == onboarding_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Onboarding]:
        return db.query(Onboarding).filter(
            or_(Onboarding.personal_email == email, Onboarding.company_email == email)
        ).first()

    @staticmethod
    def get_by_personal_email(db: Session, email: str) -> Optional[Onboarding]:
        return db.query(Onboarding).filter(Onboarding.personal_email == email).first()

    @staticmethod
    def get_by_company_email(db: Session, email: str) -> Optional[Onboarding]:
        return db.query(Onboarding).filter(Onboarding.company_email == email).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Onboarding]:
        return db.query(Onboarding).offset(skip).limit(limit).all()

    @staticmethod
    def search(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Onboarding]:
        search_filter = or_(
            Onboarding.legal_name.ilike(f"%{query}%"),
            Onboarding.display_name.ilike(f"%{query}%"),
            Onboarding.display_last_name.ilike(f"%{query}%"),
            Onboarding.personal_email.ilike(f"%{query}%"),
            Onboarding.company_email.ilike(f"%{query}%"),
            Onboarding.department.ilike(f"%{query}%"),
            Onboarding.ticket_number.ilike(f"%{query}%")
        )
        return db.query(Onboarding).filter(search_filter).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, onboarding_id: int, onboarding_update: OnboardingUpdate, user_email: str) -> Optional[Onboarding]:
        db_onboarding = OnboardingCRUD.get(db, onboarding_id)
        if not db_onboarding:
            return None
        
        # Store old values for audit
        old_values = {
            "legal_name": db_onboarding.legal_name,
            "display_name": db_onboarding.display_name,
            "display_last_name": db_onboarding.display_last_name,
            "personal_email": db_onboarding.personal_email,
            "company_email": db_onboarding.company_email,
            "department": db_onboarding.department,
            "status": db_onboarding.status.value if db_onboarding.status else None
        }
        
        # Update fields
        update_data = onboarding_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_onboarding, field, value)
        
        db.commit()
        db.refresh(db_onboarding)
        
        # Create audit log
        OnboardingCRUD._create_audit_log(
            db, "onboarding", onboarding_id, "UPDATE", 
            old_values, update_data, user_email
        )
        
        return db_onboarding

    @staticmethod
    def delete(db: Session, onboarding_id: int, user_email: str) -> bool:
        db_onboarding = OnboardingCRUD.get(db, onboarding_id)
        if not db_onboarding:
            return False
        
        # Store values for audit
        old_values = {
            "legal_name": db_onboarding.legal_name,
            "display_name": db_onboarding.display_name,
            "display_last_name": db_onboarding.display_last_name,
            "personal_email": db_onboarding.personal_email,
            "company_email": db_onboarding.company_email
        }
        
        db.delete(db_onboarding)
        db.commit()
        
        # Create audit log
        OnboardingCRUD._create_audit_log(
            db, "onboarding", onboarding_id, "DELETE", 
            old_values, None, user_email
        )
        
        return True

    @staticmethod
    def _create_audit_log(db: Session, table_name: str, record_id: int, action: str, 
                         old_values: dict, new_values: dict, user_email: str):
        import json
        from datetime import datetime
        import enum
        
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, enum.Enum):
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        audit_log = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=json.dumps(old_values, default=serialize_datetime) if old_values else None,
            new_values=json.dumps(new_values, default=serialize_datetime) if new_values else None,
            user_email=user_email
        )
        db.add(audit_log)
        db.commit()

class DepartmentMappingCRUD:
    @staticmethod
    def create(db: Session, dept_mapping: DepartmentMappingCreate) -> DepartmentMapping:
        db_mapping = DepartmentMapping(**dept_mapping.dict())
        db.add(db_mapping)
        db.commit()
        db.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def get(db: Session, mapping_id: int) -> Optional[DepartmentMapping]:
        return db.query(DepartmentMapping).filter(DepartmentMapping.id == mapping_id).first()

    @staticmethod
    def get_by_department(db: Session, department: str) -> Optional[DepartmentMapping]:
        return db.query(DepartmentMapping).filter(DepartmentMapping.department == department).first()

    @staticmethod
    def get_all(db: Session) -> List[DepartmentMapping]:
        return db.query(DepartmentMapping).order_by(DepartmentMapping.department).all()

    @staticmethod
    def update(db: Session, mapping_id: int, dept_mapping_update: DepartmentMappingUpdate) -> Optional[DepartmentMapping]:
        db_mapping = DepartmentMappingCRUD.get(db, mapping_id)
        if not db_mapping:
            return None
        
        update_data = dept_mapping_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_mapping, field, value)
        
        db.commit()
        db.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def delete(db: Session, mapping_id: int) -> bool:
        db_mapping = DepartmentMappingCRUD.get(db, mapping_id)
        if not db_mapping:
            return False
        
        db.delete(db_mapping)
        db.commit()
        return True

class ScriptLogCRUD:
    @staticmethod
    def create(db: Session, script_log: ScriptLogCreate) -> ScriptLog:
        db_script_log = ScriptLog(**script_log.dict())
        db.add(db_script_log)
        db.commit()
        db.refresh(db_script_log)
        return db_script_log

    @staticmethod
    def get(db: Session, log_id: int) -> Optional[ScriptLog]:
        return db.query(ScriptLog).filter(ScriptLog.id == log_id).first()

    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[ScriptLog]:
        return db.query(ScriptLog)\
            .filter(ScriptLog.user_id == user_id)\
            .order_by(desc(ScriptLog.started_at))\
            .offset(skip).limit(limit).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ScriptLog]:
        return db.query(ScriptLog)\
            .order_by(desc(ScriptLog.started_at))\
            .offset(skip).limit(limit).all()

    @staticmethod
    def get_by_script_type(db: Session, script_type: str, limit: int = 10) -> List[ScriptLog]:
        return db.query(ScriptLog)\
            .filter(ScriptLog.script_type == script_type)\
            .order_by(desc(ScriptLog.started_at))\
            .limit(limit).all()

    @staticmethod
    def update_completion(db: Session, log_id: int, status: str, output: str = None, error_message: str = None, execution_time_seconds: int = None) -> Optional[ScriptLog]:
        try:
            db_log = ScriptLogCRUD.get(db, log_id)
            if not db_log:
                return None
            
            from datetime import datetime
            from models import ScriptStatus
            import re
            
            # Clean error message to remove emojis and problematic characters
            if error_message:
                # Remove emoji and other 4-byte UTF-8 characters
                emoji_pattern = re.compile("["
                                          u"\U0001F600-\U0001F64F"  # emoticons
                                          u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                          u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                          u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                          u"\U00002702-\U000027B0"
                                          u"\U000024C2-\U0001F251"
                                          "]+", flags=re.UNICODE)
                error_message = emoji_pattern.sub('', error_message)
                error_message = error_message.encode('utf-8', 'ignore').decode('utf-8')
                # Truncate if too long (typical MySQL TEXT limit)
                error_message = error_message[:65535] if len(error_message) > 65535 else error_message
            
            db_log.status = ScriptStatus(status)
            db_log.completed_at = datetime.now()
            if output:
                db_log.output = output
            if error_message:
                db_log.error_message = error_message
            if execution_time_seconds:
                db_log.execution_time_seconds = execution_time_seconds
            
            db.commit()
            db.refresh(db_log)
            return db_log
            
        except Exception as e:
            # Rollback the session on any error
            db.rollback()
            print(f"Error updating script log completion: {str(e)}")
            raise

def generate_password(length: int = 16) -> str:
    """Generate a secure random password of specified length."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class OffboardingCRUD:
    @staticmethod
    def create(db: Session, offboarding: OffboardingCreate, user_email: str) -> Offboarding:
        # Create a copy of the data and generate password if not provided
        offboarding_data = offboarding.dict()
        if not offboarding_data.get('password'):
            offboarding_data['password'] = generate_password(16)
        
        # Set created_by field if not provided
        if not offboarding_data.get('created_by'):
            offboarding_data['created_by'] = user_email
        
        db_offboarding = Offboarding(**offboarding_data)
        db.add(db_offboarding)
        db.commit()
        db.refresh(db_offboarding)
        
        # Create audit log
        OffboardingCRUD._create_audit_log(
            db, "offboarding", db_offboarding.id, "CREATE", 
            None, offboarding_data, user_email
        )
        
        return db_offboarding

    @staticmethod
    def get(db: Session, offboarding_id: int) -> Optional[Offboarding]:
        return db.query(Offboarding).filter(Offboarding.id == offboarding_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Offboarding]:
        return db.query(Offboarding).filter(Offboarding.company_email == email).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Offboarding]:
        return db.query(Offboarding).order_by(desc(Offboarding.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def search(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Offboarding]:
        search_filter = or_(
            Offboarding.first_name.ilike(f"%{query}%"),
            Offboarding.last_name.ilike(f"%{query}%"),
            Offboarding.company_email.ilike(f"%{query}%"),
            Offboarding.hostname.ilike(f"%{query}%"),
            Offboarding.requested_by.ilike(f"%{query}%")
        )
        return db.query(Offboarding).filter(search_filter).order_by(desc(Offboarding.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, offboarding_id: int, offboarding_update: OffboardingUpdate, user_email: str) -> Optional[Offboarding]:
        db_offboarding = OffboardingCRUD.get(db, offboarding_id)
        if not db_offboarding:
            return None
        
        # Store old values for audit log
        old_values = {
            column.name: getattr(db_offboarding, column.name)
            for column in db_offboarding.__table__.columns
        }
        
        # Update only provided fields
        update_data = offboarding_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_offboarding, field, value)
        
        db.commit()
        db.refresh(db_offboarding)
        
        # Create audit log
        new_values = {
            column.name: getattr(db_offboarding, column.name)
            for column in db_offboarding.__table__.columns
        }
        OffboardingCRUD._create_audit_log(
            db, "offboarding", offboarding_id, "UPDATE", 
            old_values, new_values, user_email
        )
        
        return db_offboarding

    @staticmethod
    def delete(db: Session, offboarding_id: int, user_email: str) -> bool:
        db_offboarding = OffboardingCRUD.get(db, offboarding_id)
        if not db_offboarding:
            return False
        
        # Store old values for audit log
        old_values = {
            column.name: getattr(db_offboarding, column.name)
            for column in db_offboarding.__table__.columns
        }
        
        db.delete(db_offboarding)
        db.commit()
        
        # Create audit log
        OffboardingCRUD._create_audit_log(
            db, "offboarding", offboarding_id, "DELETE", 
            old_values, None, user_email
        )
        
        return True

    @staticmethod
    def _create_audit_log(db: Session, table_name: str, record_id: int, action: str, old_values: dict, new_values: dict, user_email: str):
        audit_log = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=json.dumps(old_values, default=str) if old_values else None,
            new_values=json.dumps(new_values, default=str) if new_values else None,
            user_email=user_email
        )
        db.add(audit_log)
        db.commit()

class OffboardingScriptLogCRUD:
    @staticmethod
    def create(db: Session, log_data) -> 'OffboardingScriptLog':
        """Create a new offboarding script log entry"""
        from models import OffboardingScriptLog
        import json
        
        # Convert schema object to dict
        if hasattr(log_data, 'model_dump'):
            data = log_data.model_dump()
        else:
            data = log_data
        
        # Convert additional_params dict to JSON string if needed
        if data.get('additional_params') and isinstance(data['additional_params'], dict):
            data['additional_params'] = json.dumps(data['additional_params'])
        
        db_log = OffboardingScriptLog(**data)
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    @staticmethod
    def update_completion(db: Session, log_id: int, status: str, output: str = None, error_message: str = None, execution_time_seconds: int = None):
        """Update log with completion details"""
        try:
            from models import OffboardingScriptLog, ScriptStatus
            from datetime import datetime
            import re
            
            log = db.query(OffboardingScriptLog).filter(OffboardingScriptLog.id == log_id).first()
            if log:
                # Clean error message to remove emojis and problematic characters
                if error_message:
                    # Remove emoji and other 4-byte UTF-8 characters
                    emoji_pattern = re.compile("["
                                              u"\U0001F600-\U0001F64F"  # emoticons
                                              u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                              u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                              u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                              u"\U00002702-\U000027B0"
                                              u"\U000024C2-\U0001F251"
                                              "]+", flags=re.UNICODE)
                    error_message = emoji_pattern.sub('', error_message)
                    error_message = error_message.encode('utf-8', 'ignore').decode('utf-8')
                    # Truncate if too long (typical MySQL TEXT limit)
                    error_message = error_message[:65535] if len(error_message) > 65535 else error_message
                
                # Map status string to enum - handle both string formats
                if status.lower() in ["completed", "success"]:
                    log.status = ScriptStatus.SUCCESS
                elif status.lower() in ["failed", "error"]:
                    log.status = ScriptStatus.FAILED
                else:
                    log.status = ScriptStatus.RUNNING
                    
                log.output = output
                log.error_message = error_message
                log.execution_time_seconds = execution_time_seconds
                log.completed_at = datetime.now()
                db.commit()
                db.refresh(log)
            return log
            
        except Exception as e:
            # Rollback the session on any error
            db.rollback()
            print(f"Error updating offboarding script log completion: {str(e)}")
            raise

    @staticmethod
    def get_by_offboarding_id(db: Session, offboarding_id: int, limit: int = 20):
        """Get all script logs for a specific offboarding record"""
        from models import OffboardingScriptLog
        
        return db.query(OffboardingScriptLog).filter(
            OffboardingScriptLog.offboarding_id == offboarding_id
        ).order_by(desc(OffboardingScriptLog.started_at)).limit(limit).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        """Get all offboarding script logs"""
        from models import OffboardingScriptLog
        
        return db.query(OffboardingScriptLog).order_by(
            desc(OffboardingScriptLog.started_at)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get(db: Session, log_id: int):
        """Get a specific offboarding script log by ID"""
        from models import OffboardingScriptLog
        
        return db.query(OffboardingScriptLog).filter(OffboardingScriptLog.id == log_id).first()
