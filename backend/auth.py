# User Authentication and Role Management

from enum import Enum
from typing import Optional, List
import json

class UserRole(Enum):
    ADMIN = "admin"
    IT = "it"
    USER = "user"

class UserPermission(Enum):
    # User Management
    CREATE_USER = "create_user"
    EDIT_USER = "edit_user"
    DELETE_USER = "delete_user"
    VIEW_USER = "view_user"
    
    # Bulk Operations
    BULK_ONBOARD = "bulk_onboard"
    BULK_OFFBOARD = "bulk_offboard"
    
    # Script Execution
    EXECUTE_SCRIPTS = "execute_scripts"
    VIEW_SCRIPT_LOGS = "view_script_logs"
    
    # System Administration
    MANAGE_SETTINGS = "manage_settings"
    VIEW_AUDIT_LOGS = "view_audit_logs"

# Role to Permission Mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        UserPermission.CREATE_USER,
        UserPermission.EDIT_USER,
        UserPermission.DELETE_USER,
        UserPermission.VIEW_USER,
        UserPermission.BULK_ONBOARD,
        UserPermission.BULK_OFFBOARD,
        UserPermission.EXECUTE_SCRIPTS,
        UserPermission.VIEW_SCRIPT_LOGS,
        UserPermission.MANAGE_SETTINGS,
        UserPermission.VIEW_AUDIT_LOGS,
    ],
    UserRole.IT: [
        UserPermission.CREATE_USER,
        UserPermission.EDIT_USER,
        UserPermission.VIEW_USER,
        UserPermission.BULK_ONBOARD,
        UserPermission.BULK_OFFBOARD,
        UserPermission.EXECUTE_SCRIPTS,
        UserPermission.VIEW_SCRIPT_LOGS,
        UserPermission.MANAGE_SETTINGS,  # Added settings access for IT
    ],
    UserRole.USER: [
        UserPermission.VIEW_USER,
    ]
}

# Admin Users - can be configured via environment or JumpCloud groups
ADMIN_USERS = [
    "cristian.rodriguez@americor.com",
]

class AuthenticatedUser:
    def __init__(self, email: str, name: str, groups: List[str] = None):
        self.email = email
        self.name = name
        self.groups = groups or []
        self.role = self._determine_role()
        self.permissions = self._get_permissions()
    
    def _determine_role(self) -> UserRole:
        """Determine user role based on email and JumpCloud groups/attributes"""
        
        # Check if user is in admin list (fallback)
        if self.email in ADMIN_USERS:
            return UserRole.ADMIN
        
        # Check JumpCloud Role attribute and groups
        for group_or_role in self.groups:
            group_lower = group_or_role.lower()
            
            # Check for exact role matches from SAML Role attribute
            if group_lower == "help desk management tool - admin" or group_lower == "admin":
                return UserRole.ADMIN
            elif group_lower == "help desk management tool - it" or group_lower == "it":
                return UserRole.IT
            
            # Check for partial matches (legacy support)
            elif "admin" in group_lower:
                return UserRole.ADMIN
            elif "it" in group_lower or "information technology" in group_lower:
                return UserRole.IT
        
        # Default to USER role
        return UserRole.USER
    
    def _get_permissions(self) -> List[UserPermission]:
        """Get permissions based on role"""
        return ROLE_PERMISSIONS.get(self.role, [])
    
    def has_permission(self, permission: UserPermission) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN

def parse_user_from_sso_claims(claims: dict) -> AuthenticatedUser:
    """Parse SSO claims into AuthenticatedUser object"""
    
    # Get email from claims
    email = claims.get('email') or claims.get('preferred_username')
    if not email:
        raise ValueError("No email found in SSO claims")
    
    # If email is just username, construct full email
    if isinstance(email, str) and '@' not in email:
        email = f"{email}@americor.com"
    
    # Get name from claims
    name = claims.get('name')
    if not name:
        given_name = claims.get('given_name', '')
        family_name = claims.get('family_name', '')
        name = f"{given_name} {family_name}".strip() or email.split('@')[0]
    
    # Get groups/roles from JumpCloud claims
    groups = claims.get('groups', [])
    if isinstance(groups, str):
        groups = [groups]
    
    # Get Role attribute from SAML (this is what you're using)
    role_attribute = claims.get('Role') or claims.get('role')
    if role_attribute:
        if isinstance(role_attribute, list):
            groups.extend(role_attribute)
        else:
            groups.append(role_attribute)
    
    # Debug logging
    print(f"SSO Claims - Email: {email}, Name: {name}, Groups/Roles: {groups}")
    
    return AuthenticatedUser(email=email, name=name, groups=groups)

def get_current_user_from_session(session_storage_data: str) -> Optional[AuthenticatedUser]:
    """Extract current user from session storage data"""
    try:
        claims = json.loads(session_storage_data)
        return parse_user_from_sso_claims(claims)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing SSO claims: {e}")
        return None
