#!/usr/bin/env python3
"""
Google Workspace User Creation Script
Creates a new user in Google Workspace
"""
import sys
import os
import json
import time
import string
import secrets
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # Add backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add scripts directory

from base_script import BaseUserScript
from aws_secrets import get_google_credentials
from typing import Dict, Any

try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

# Google Workspace configuration
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group'
]
ADMIN_EMAIL = 'it.vault@americor.com'

class CreateGoogleWorkspaceUser(BaseUserScript):
    """Creates a user in Google Workspace"""
    
    def __init__(self):
        super().__init__()
        self.service = None
    
    def get_google_credentials(self) -> bool:
        """Get Google Workspace credentials using the centralized secrets manager"""
        try:
            self.log_info("Retrieving Google service account credentials...")
            
            # Use the centralized secrets manager
            credentials_data = get_google_credentials()
            
            # If no Google credentials are configured (development mode), return False gracefully
            if not credentials_data:
                self.log_error("Google Workspace credentials not configured for this environment")
                return False
            
            # Validate secret data structure
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in credentials_data]
            if missing_fields:
                self.log_error(f"Missing required fields in service account JSON: {missing_fields}")
                return False
            
            self.log_info(f"Service account email: {credentials_data.get('client_email', 'unknown')}")
            
            # Create credentials with service account delegation
            credentials = service_account.Credentials.from_service_account_info(
                credentials_data,
                scopes=GOOGLE_SCOPES,
                subject=ADMIN_EMAIL  # Delegate to admin email for directory operations
            )
            
            self.log_info(f"Credentials created with delegation to: {ADMIN_EMAIL}")
            
            # Build the service
            self.service = build('admin', 'directory_v1', credentials=credentials)
            
            self.log_info("Google Workspace credentials configured successfully")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to setup Google credentials: {str(e)}")
            self.log_error(f"Error type: {type(e).__name__}")
            return False

    def check_user_exists(self, email: str) -> bool:
        """Check if user already exists in Google Workspace"""
        try:
            self.service.users().get(userKey=email).execute()
            return True
        except HttpError as e:
            if e.resp.status == 404:
                return False
            # Re-raise other errors
            raise
        except Exception as e:
            self.log_error(f"Error checking if user exists: {str(e)}")
            return False

    def get_org_unit_path(self) -> str:
        """Get organizational unit path based on department_ou field or default"""
        department_ou = self.user_data.get('department_ou', '') or ''
        department = self.user_data.get('department', '') or ''
        
        # Safely strip strings, handling None values
        department_ou = department_ou.strip() if department_ou else ''
        department = department.lower().strip() if department else ''
        
        # Valid Google Workspace OU paths (update this based on your actual OUs)
        valid_ous = {
            "/Legal": "/Legal",
            "/External Contractors/Kipi": "/External Contractors/Kipi", 
            "/Accounting": "/Accounting",
            "/Human Resources": "/Human Resources",
            "/Mission Loans": "/Mission Loans",
            "/Compliance": "/Compliance",
            # Map legacy/invalid OUs to valid ones
            "IT-OU": "/",  # Map IT-OU to root since it's not a valid OU path
            "/IT-OU": "/",  # Also handle if it has slash
            "IT": "/",     # Map IT department to root
            "/IT": "/"
        }
        
        # Use department_ou if provided and valid
        if department_ou:
            # Check if it's a valid OU directly
            if department_ou in valid_ous:
                mapped_ou = valid_ous[department_ou]
                self.log_info(f"Using mapped organizational unit: {mapped_ou} (from {department_ou})")
                return mapped_ou
            
            # If it starts with /, check if it's valid
            if department_ou.startswith('/'):
                if department_ou in valid_ous:
                    self.log_info(f"Using specified organizational unit: {department_ou}")
                    return department_ou
                else:
                    self.log_warning(f"Invalid OU path '{department_ou}', falling back to root (/)")
                    return "/"
            else:
                # Try adding slash and check again
                with_slash = f"/{department_ou}"
                if with_slash in valid_ous:
                    mapped_ou = valid_ous[with_slash]
                    self.log_info(f"Using mapped organizational unit: {mapped_ou} (from {department_ou})")
                    return mapped_ou
                else:
                    self.log_warning(f"Invalid OU '{department_ou}' not found in valid OUs, falling back to root (/)")
                    return "/"
        
        # Fallback based on department name
        department_mappings = {
            'legal': '/Legal',
            'accounting': '/Accounting', 
            'hr': '/Human Resources',
            'human resources': '/Human Resources',
            'compliance': '/Compliance',
            'mission loans': '/Mission Loans'
        }
        
        if department and department in department_mappings:
            mapped_ou = department_mappings[department]
            self.log_info(f"Using department-based OU mapping: {mapped_ou} for department '{department}'")
            return mapped_ou
        
        # Final fallback to root OU
        self.log_info(f"No valid OU found for department '{department}', using root organizational unit (/)")
        return "/"
    
    def generate_random_password(self, length=14):
        """Generate a secure random password"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*()"
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password
    
    def sanitize_user_data(self, user_data):
        """Sanitize user data by trimming strings and handling None values"""
        sanitized_data = {}
        for key, value in user_data.items():
            if isinstance(value, str):
                sanitized_data[key] = value.strip()
            elif value is None:
                sanitized_data[key] = ""  # Convert None to empty string
            else:
                sanitized_data[key] = value
        return sanitized_data
    
    def validate_user_data(self) -> bool:
        """Validate required fields for Google Workspace user creation"""
        required_fields = ['display_name', 'display_last_name', 'company_email', 'username']
        
        for field in required_fields:
            if not self.user_data.get(field):
                self.log_error(f"Missing required field: {field}")
                return False
        
        # Validate email format
        email = self.user_data.get('company_email', '')
        if '@' not in email:
            self.log_error("Invalid email format")
            return False
        
        # Check if email domain is valid for Google Workspace
        domain = email.split('@')[1]
        valid_domains = ['americor.com', 'credit9.com']  # Add your domains
        if domain not in valid_domains:
            self.log_error(f"Email domain {domain} not configured for Google Workspace")
            return False
        
        return True
    
    def execute(self) -> Dict[str, Any]:
        """Execute Google Workspace user creation"""
        username = self.user_data['username']
        email = self.user_data['company_email']
        
        self.log_info(f"Creating Google Workspace user: {email}")
        
        # Sanitize user data
        self.user_data = self.sanitize_user_data(self.user_data)
        
        # Check if Google API is available
        if not GOOGLE_API_AVAILABLE:
            self.log_error("Google API libraries not available. Install with: pip install google-api-python-client google-auth")
            return {
                "status": "failed",
                "error": "Google API libraries not installed",
                "message": f"Cannot create Google Workspace user {email} - missing dependencies"
            }
        
        # Setup Google credentials
        if not self.get_google_credentials():
            return {
                "status": "failed", 
                "error": "Failed to setup Google credentials",
                "message": f"Cannot create Google Workspace user {email} - credential error"
            }
        
        try:
            # Check if user already exists
            if self.check_user_exists(email):
                self.log_info(f"User {email} already exists in Google Workspace")
                return {
                    "status": "already_exists",
                    "message": f"User {email} already exists in Google Workspace",
                    "google_user_id": email,
                    "primary_email": email
                }
            
            # Use password from form data or generate one if not provided
            password = self.user_data.get('password')
            if password:
                self.log_info("Using password provided in form data")
            else:
                password = self.generate_random_password()
                self.log_info("Generated random password for user")
            
            # Prepare user data for Google Workspace (matching your Lambda pattern)
            google_user = {
                "primaryEmail": email,
                "name": {
                    "givenName": self.user_data['display_name'],
                    "familyName": self.user_data['display_last_name']
                },
                "password": password,
                "orgUnitPath": self.get_org_unit_path(),
                "organizations": [{
                    "title": self.user_data.get('title', ''),
                    "department": self.user_data.get('department', '')
                }],
                "changePasswordAtNextLogin": True,
                "agreedToTerms": True,
                "suspended": False,
                "includeInGlobalAddressList": True
            }
            
            # Add manager relationship if provided
            if self.user_data.get('manager'):
                google_user["relations"] = [{
                    "value": self.user_data['manager'],
                    "type": "manager"
                }]
            
            # Create the user
            self.log_info(f"Creating user with data: {json.dumps({k: v for k, v in google_user.items() if k != 'password'}, indent=2)}")
            result = self.service.users().insert(body=google_user).execute()
            
            pacific_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            
            self.log_info(f"Google Workspace user created successfully: {result.get('id', email)}")
            
            return {
                "status": "created",
                "message": f"User created successfully on {pacific_time}",
                "google_user_id": result.get("id", email),
                "primary_email": email,
                "username": username,
                "password": password,  # Include generated password in response
                "org_unit": google_user["orgUnitPath"],
                "password_change_required": True,
                "suspended": False,
                "created_at": result.get("creationTime", pacific_time),
                "department": self.user_data.get('department', ''),
                "title": self.user_data.get('title', ''),
                "manager": self.user_data.get('manager', ''),
                "firstname": self.user_data['display_name'],
                "lastname": self.user_data['display_last_name']
            }
            
        except HttpError as e:
            error_msg = f"Google API error: {e.resp.status} - {e.content.decode()}"
            self.log_error(error_msg)
            return {
                "status": "failed",
                "error": error_msg,
                "message": f"Failed to create Google Workspace user {email}"
            }
        except Exception as e:
            error_msg = f"Failed to create Google Workspace user: {str(e)}"
            self.log_error(error_msg)
            return {
                "status": "failed",
                "error": error_msg,
                "message": f"Failed to create Google Workspace user {email}"
            }
    
    def build_custom_schemas(self) -> Dict[str, Any]:
        """Build custom schemas for additional user attributes"""
        custom_schemas = {}
        
        # Employee information schema
        employee_info = {}
        
        if self.user_data.get('employee_id'):
            employee_info['employeeId'] = self.user_data['employee_id']
        
        if self.user_data.get('title'):
            employee_info['jobTitle'] = self.user_data['title']
        
        if self.user_data.get('department'):
            employee_info['department'] = self.user_data['department']
        
        if self.user_data.get('manager'):
            employee_info['manager'] = self.user_data['manager']
        
        if self.user_data.get('start_date'):
            employee_info['startDate'] = str(self.user_data['start_date'])
        
        if self.user_data.get('phone'):
            employee_info['workPhone'] = self.user_data['phone']
        
        if self.user_data.get('location'):
            employee_info['location'] = self.user_data['location']
        
        if employee_info:
            custom_schemas['EmployeeInfo'] = employee_info
        
        return custom_schemas

def main():
    script = CreateGoogleWorkspaceUser()
    script.run()

if __name__ == "__main__":
    main()
