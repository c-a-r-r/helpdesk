from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import datetime
from typing import Optional, Dict, Any
from models import AddressType, OnboardingStatus, ScriptStatus

class OnboardingBase(BaseModel):
    company: str = "Americor"
    first_name: str
    last_name: str
    display_name: str
    personal_email: EmailStr
    company_email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    title: str
    manager: EmailStr
    department: str
    start_date: datetime
    location_first_day: Optional[str] = None
    address_type: AddressType
    street_name: str
    city: str
    state: str
    zip_code: str
    username: Optional[str] = None
    department_ou: Optional[str] = None
    hostname: Optional[str] = None
    password: Optional[str] = None
    credit9_alias: Optional[str] = None
    advantageteam_alias: Optional[str] = None
    ticket_number: Optional[str] = None
    zoom: Optional[bool] = False
    five9: Optional[bool] = False
    extension: Optional[str] = None
    notes: Optional[str] = None
    extra_details: Optional[str] = None

    @field_validator('display_name', mode='before')
    @classmethod
    def generate_display_name(cls, v, info):
        if not v and info.data:
            first_name = info.data.get('first_name')
            last_name = info.data.get('last_name')
            if first_name and last_name:
                return f"{first_name} {last_name}"
        return v

    @field_validator('username', mode='before')
    @classmethod
    def generate_username(cls, v, info):
        if not v and info.data:
            first_name = info.data.get('first_name')
            last_name = info.data.get('last_name')
            if first_name and last_name:
                return f"{first_name.lower()}.{last_name.lower()}"
        return v

    @model_validator(mode='before')
    @classmethod
    def validate_zoom_five9_exclusive(cls, values):
        """Ensure that zoom and five9 cannot both be true at the same time"""
        if isinstance(values, dict):
            zoom = values.get('zoom', False)
            five9 = values.get('five9', False)
            
            if zoom and five9:
                raise ValueError('zoom and five9 cannot both be enabled for the same user')
        
        return values

    @field_validator('company_email', mode='before')
    @classmethod
    def generate_company_email(cls, v, info):
        if not v and info.data:
            username = info.data.get('username')
            if username:
                return f"{username}@americor.com"
            
            first_name = info.data.get('first_name')
            last_name = info.data.get('last_name')
            if first_name and last_name:
                username = f"{first_name.lower()}.{last_name.lower()}"
                return f"{username}@americor.com"
        return v

    @field_validator('credit9_alias', mode='before')
    @classmethod
    def generate_credit9_alias(cls, v, info):
        if not v and info.data:
            username = info.data.get('username')
            if username:
                return f"{username}@credit9.com"
            
            first_name = info.data.get('first_name')
            last_name = info.data.get('last_name')
            if first_name and last_name:
                username = f"{first_name.lower()}.{last_name.lower()}"
                return f"{username}@credit9.com"
        return v

    @field_validator('advantageteam_alias', mode='before')
    @classmethod
    def generate_advantageteam_alias(cls, v, info):
        if not v and info.data:
            username = info.data.get('username')
            if username:
                return f"{username}@advantageteam.law"
            
            first_name = info.data.get('first_name')
            last_name = info.data.get('last_name')
            if first_name and last_name:
                username = f"{first_name.lower()}.{last_name.lower()}"
                return f"{username}@advantageteam.law"
        return v

class OnboardingCreate(OnboardingBase):
    pass

class OnboardingUpdate(BaseModel):
    company: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    personal_email: Optional[EmailStr] = None
    company_email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    title: Optional[str] = None
    manager: Optional[EmailStr] = None
    department: Optional[str] = None
    start_date: Optional[datetime] = None
    location_first_day: Optional[str] = None
    address_type: Optional[AddressType] = None
    street_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    username: Optional[str] = None
    department_ou: Optional[str] = None
    hostname: Optional[str] = None
    password: Optional[str] = None
    credit9_alias: Optional[str] = None
    advantageteam_alias: Optional[str] = None
    status: Optional[OnboardingStatus] = None
    ticket_number: Optional[str] = None
    zoom: Optional[bool] = None
    five9: Optional[bool] = None
    extension: Optional[str] = None
    notes: Optional[str] = None
    extra_details: Optional[str] = None

class OnboardingResponse(OnboardingBase):
    id: int
    status: OnboardingStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DepartmentMappingBase(BaseModel):
    department: str
    department_ou: str

class DepartmentMappingCreate(DepartmentMappingBase):
    pass

class DepartmentMappingUpdate(BaseModel):
    department: Optional[str] = None
    department_ou: Optional[str] = None

class DepartmentMappingResponse(DepartmentMappingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Script execution schemas
class ScriptExecutionRequest(BaseModel):
    script_type: str  # 'jumpcloud' or 'google'
    script_name: str  # 'create_user', 'bind_machine', etc.
    user_id: Optional[int] = None  # If executing on a specific user
    additional_params: Dict[str, Any] = {}  # Additional parameters for the script

class ScriptExecutionResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    executed_by: str
    executed_at: datetime = datetime.now()
    script_type: str
    script_name: str
    user_id: Optional[int] = None

# Script log schemas
class ScriptLogBase(BaseModel):
    user_id: int
    script_type: str
    script_name: str
    status: ScriptStatus
    output: Optional[str] = None
    error_message: Optional[str] = None
    executed_by: str
    execution_time_seconds: Optional[int] = None
    additional_params: Optional[str] = None

class ScriptLogCreate(ScriptLogBase):
    pass

class ScriptLogResponse(ScriptLogBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
