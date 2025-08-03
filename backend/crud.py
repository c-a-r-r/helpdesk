from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from models import Onboarding, DepartmentMapping, AuditLog, ScriptLog
from schemas import OnboardingCreate, OnboardingUpdate, DepartmentMappingCreate, DepartmentMappingUpdate, ScriptLogCreate
from typing import List, Optional
import json

class OnboardingCRUD:
    @staticmethod
    def create(db: Session, onboarding: OnboardingCreate, user_email: str) -> Onboarding:
        db_onboarding = Onboarding(**onboarding.dict())
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
            Onboarding.first_name.ilike(f"%{query}%"),
            Onboarding.last_name.ilike(f"%{query}%"),
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
            "first_name": db_onboarding.first_name,
            "last_name": db_onboarding.last_name,
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
            "first_name": db_onboarding.first_name,
            "last_name": db_onboarding.last_name,
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
        db_log = ScriptLogCRUD.get(db, log_id)
        if not db_log:
            return None
        
        from datetime import datetime
        from models import ScriptStatus
        
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
