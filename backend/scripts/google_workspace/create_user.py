#!/usr/bin/env python3
"""
Google Workspace User Creation Script
Creates a new user in Google Workspace
"""
import sys
import os
import json
import time
import boto3
import string
import secrets
from datetime import datetime
from botocore.exceptions import ClientError
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_script import BaseUserScript
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
        """Get Google Workspace credentials from AWS Secrets Manager"""
        try:
            # Use existing AWS secret ARN
            secret_arn = "arn:aws:secretsmanager:us-west-2:134308154914:secret:google-service-account-signature-secret-KHaS4K"
            
            self.log_info(f"Retrieving Google service account credentials from AWS")
            self.log_info(f"Secret ARN: {secret_arn}")
            
            # Get AWS credentials
            session = boto3.Session()
            secrets_client = session.client('secretsmanager', region_name='us-west-2')
            
            self.log_info("AWS session created, attempting to retrieve secret...")
            
            # Retrieve the secret
            response = secrets_client.get_secret_value(SecretId=secret_arn)
            secret_data = json.loads(response['SecretString'])
            
            self.log_info("Secret retrieved successfully, creating service account credentials...")
            
            # Validate secret data structure
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in secret_data]
            if missing_fields:
                self.log_error(f"Missing required fields in service account JSON: {missing_fields}")
                return False
            
            self.log_info(f"Service account email: {secret_data.get('client_email', 'unknown')}")
            
            # Create credentials with service account delegation
            credentials = service_account.Credentials.from_service_account_info(
                secret_data,
                scopes=GOOGLE_SCOPES,
                subject=ADMIN_EMAIL  # Delegate to admin email for directory operations
            )
            
            self.log_info(f"Credentials created with delegation to: {ADMIN_EMAIL}")
            
            # Build the service
            self.service = build('admin', 'directory_v1', credentials=credentials)
            
            self.log_info("Google Workspace credentials configured successfully")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            self.log_error(f"AWS Secrets Manager error ({error_code}): {error_msg}")
            
            if error_code == 'AccessDeniedException':
                self.log_error("The Docker container doesn't have permission to access AWS Secrets Manager")
                self.log_error("Make sure AWS credentials are properly configured in the container")
            elif error_code == 'ResourceNotFoundException':
                self.log_error(f"Secret not found: {secret_arn}")
            
            return False
        except json.JSONDecodeError as e:
            self.log_error(f"Failed to parse secret as JSON: {str(e)}")
            return False
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
        department_ou = self.user_data.get('department_ou', '').strip()
        department = self.user_data.get('department', '').lower()
        
        # Use department_ou if provided (this is the actual OU path)
        if department_ou:
            # Ensure it starts with / if not already
            if not department_ou.startswith('/'):
                department_ou = f"/{department_ou}"
            self.log_info(f"Using specified organizational unit: {department_ou}")
            return department_ou
        
        # Fallback to root OU if no department_ou specified
        self.log_info(f"No department_ou specified, using root organizational unit (/) for department: {department}")
        return "/"
    
    def generate_random_password(self, length=14):
        """Generate a secure random password"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*()"
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password
    
    def sanitize_user_data(self, user_data):
        """Sanitize user data by trimming strings"""
        sanitized_data = {}
        for key, value in user_data.items():
            if isinstance(value, str):
                sanitized_data[key] = value.strip()
            else:
                sanitized_data[key] = value
        return sanitized_data
    
    def validate_user_data(self) -> bool:
        """Validate required fields for Google Workspace user creation"""
        required_fields = ['first_name', 'last_name', 'company_email', 'username']
        
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
                    "givenName": self.user_data['first_name'],
                    "familyName": self.user_data['last_name']
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
                "firstname": self.user_data['first_name'],
                "lastname": self.user_data['last_name']
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
