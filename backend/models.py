from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Boolean
from sqlalchemy.sql import func
from database import Base
import enum

class AddressType(enum.Enum):
    RESIDENTIAL = "Residential"
    BUSINESS = "Business"
    PO_BOX = "PO Box"

class OnboardingStatus(enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class OffboardingStatus(enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class ScriptStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RUNNING = "RUNNING"

class Onboarding(Base):
    __tablename__ = "onboarding"

    id = Column(Integer, primary_key=True, index=True)
    
    # Company Information
    company = Column(String(255), nullable=False, default="Americor")
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=False)
    personal_email = Column(String(255), nullable=False)
    company_email = Column(String(255), nullable=True, unique=True)
    phone_number = Column(String(20), nullable=True)
    
    # Work Information
    title = Column(String(200), nullable=False)
    manager = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    location_first_day = Column(String(255), nullable=True)
    
    # Address Information
    address_type = Column(Enum(AddressType), nullable=False)
    street_name = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(10), nullable=False)
    zip_code = Column(String(20), nullable=False)
    
    # System Information
    username = Column(String(100), nullable=True)
    department_ou = Column(String(200), nullable=True)
    hostname = Column(String(100), nullable=True)
    password = Column(String(255), nullable=True)
    credit9_alias = Column(String(255), nullable=True)
    advantageteam_alias = Column(String(255), nullable=True)
    
    # Access/Telephony
    zoom = Column(Boolean, default=False)
    five9 = Column(Boolean, default=False)
    extension = Column(String(20), nullable=True)

    # Status and Tracking
    status = Column(Enum(OnboardingStatus), default=OnboardingStatus.PENDING)
    ticket_number = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    extra_details = Column(Text, nullable=True)
    
    # Account Creation Status
    jumpcloud_status = Column(Enum(ScriptStatus), nullable=True)  # JumpCloud account creation status
    jumpcloud_created_at = Column(DateTime(timezone=True), nullable=True)  # When JumpCloud account was created
    jumpcloud_error = Column(Text, nullable=True)  # Error message if JumpCloud creation failed
    
    google_status = Column(Enum(ScriptStatus), nullable=True)  # Google Workspace account creation status
    google_created_at = Column(DateTime(timezone=True), nullable=True)  # When Google account was created
    google_error = Column(Text, nullable=True)  # Error message if Google creation failed
    
    # Record Management
    created_by = Column(String(255), nullable=True)  # Email of user who created record, or 'freshdesk-sync' for automated
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class Offboarding(Base):
    __tablename__ = "offboarding"

    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company_email = Column(String(255), nullable=False)
    
    # System Information
    hostname = Column(String(100), nullable=True)
    
    # Request Information
    requested_by = Column(String(255), nullable=False)
    created_by = Column(String(255), nullable=False)  # User who created the offboarding record
    
    # Security Information
    password = Column(String(16), nullable=True)  # 16-character generated password
    
    # Status and Tracking
    status = Column(Enum(OffboardingStatus), default=OffboardingStatus.PENDING)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class DepartmentMapping(Base):
    __tablename__ = "department_mappings"

    id = Column(Integer, primary_key=True, index=True)
    department = Column(String(100), nullable=False, unique=True)
    department_ou = Column(String(200), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    user_email = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScriptLog(Base):
    __tablename__ = "script_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Reference to onboarding user - can be NULL for system operations
    script_type = Column(String(50), nullable=False)  # 'jumpcloud', 'google', 'freshservice_sync', etc.
    script_name = Column(String(100), nullable=False)  # 'create_user', 'bind_machine', 'sync_onboarding', etc.
    status = Column(Enum(ScriptStatus), nullable=False)
    output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    executed_by = Column(String(255), nullable=False)  # Email of user who ran the script or 'system_scheduler'
    execution_time_seconds = Column(Integer, nullable=True)
    additional_params = Column(Text, nullable=True)  # JSON string of additional parameters
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class OffboardingScriptLog(Base):
    __tablename__ = "offboarding_script_logs"

    id = Column(Integer, primary_key=True, index=True)
    offboarding_id = Column(Integer, nullable=False)  # Reference to offboarding record ID
    script_type = Column(String(50), nullable=False)  # 'offboarding'
    script_name = Column(String(100), nullable=False)  # 'terminate_user_jumpcloud', 'terminate_user_google', 'remove_automox_agent'
    status = Column(Enum(ScriptStatus), nullable=False)
    output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    executed_by = Column(String(255), nullable=False)  # Email of user who ran the script
    execution_time_seconds = Column(Integer, nullable=True)
    additional_params = Column(Text, nullable=True)  # JSON string of additional parameters
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    sync_type = Column(String(50), nullable=False)  # e.g., 'freshservice'
    sync_source = Column(String(100), nullable=True)  # e.g., 'Freshservice API'
    status = Column(String(20), nullable=False)  # 'running', 'success', 'failed'
    triggered_by = Column(String(50), nullable=True)  # 'manual_trigger', 'automated_scheduler'
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time_seconds = Column(Integer, nullable=True)
    tickets_processed = Column(Integer, nullable=True)
    users_created = Column(Integer, nullable=True)
    users_skipped = Column(Integer, nullable=True)
    output_message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    additional_data = Column(Text, nullable=True)  # JSON string for extra context
