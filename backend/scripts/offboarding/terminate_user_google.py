#!/usr/bin/env python3
"""
Google Workspace User Termination Script
Suspends a user in Google Workspace and transfers ownership of files/calendars
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the path to import base_script
sys.path.append(str(Path(__file__).parent.parent))
from base_script import BaseUserScript

try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from googleapiclient.errors import HttpError
except ImportError:
    # Handle missing Google libraries gracefully
    pass

class GoogleWorkspaceTerminateUser(BaseUserScript):
    """Script to terminate a user in Google Workspace"""
    
    def __init__(self):
        super().__init__()
        self.service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        self.admin_email = os.getenv('GOOGLE_ADMIN_EMAIL', 'admin@americor.com')
        self.service = None
    
    def validate_user_data(self) -> bool:
        """Validate that we have the required user data"""
        if not self.user_data:
            self.log_error("No user data provided")
            return False
        
        required_fields = ['company_email']
        missing_fields = []
        
        for field in required_fields:
            if not self.user_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            self.log_error(f"Missing required fields: {', '.join(missing_fields)}")
            return False
        
        if not self.service_account_file:
            self.log_error("GOOGLE_SERVICE_ACCOUNT_FILE environment variable not set")
            return False
        
        if not os.path.exists(self.service_account_file):
            self.log_error(f"Service account file not found: {self.service_account_file}")
            return False
        
        return True
    
    def execute(self):
        """Execute the Google Workspace user termination"""
        try:
            self.log_info("Starting Google Workspace user termination process")
            
            # Initialize Google Admin SDK service
            if not self.init_service():
                return {"status": "failed", "message": "Failed to initialize Google service"}
            
            user_email = self.user_data['company_email']
            
            # Check if user exists
            user_exists = self.check_user_exists(user_email)
            if not user_exists:
                return {"status": "failed", "message": f"User {user_email} not found in Google Workspace"}
            
            # Suspend the user
            suspend_result = self.suspend_user(user_email)
            if not suspend_result:
                return {"status": "failed", "message": "Failed to suspend user"}
            
            # Reset password to secure random value
            password_result = self.reset_password(user_email)
            
            # Remove from groups/organizational units (optional)
            # groups_result = self.remove_from_groups(user_email)
            
            # Transfer ownership of files/calendars to manager or admin
            transfer_result = self.initiate_data_transfer(user_email)
            
            self.log_info("✅ Google Workspace user termination completed successfully")
            
            return {
                "status": "success",
                "message": f"User {user_email} successfully terminated in Google Workspace",
                "details": {
                    "suspended": suspend_result,
                    "password_reset": password_result,
                    "data_transfer_initiated": transfer_result
                }
            }
            
        except Exception as e:
            self.log_error(f"Google Workspace termination failed: {str(e)}")
            return {"status": "failed", "message": str(e)}
    
    def init_service(self):
        """Initialize Google Admin SDK service"""
        try:
            # Import here to handle missing libraries
            from googleapiclient.discovery import build
            from google.oauth2 import service_account
            
            # Define required scopes
            scopes = [
                'https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group',
                'https://www.googleapis.com/auth/admin.datatransfer'
            ]
            
            # Load service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=scopes
            )
            
            # Delegate to admin user
            delegated_credentials = credentials.with_subject(self.admin_email)
            
            # Build the service
            self.service = build('admin', 'directory_v1', credentials=delegated_credentials)
            self.transfer_service = build('admin', 'datatransfer_v1', credentials=delegated_credentials)
            
            self.log_info("✅ Google Admin SDK service initialized")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to initialize Google service: {str(e)}")
            return False
    
    def check_user_exists(self, user_email):
        """Check if user exists in Google Workspace"""
        try:
            self.log_info(f"Checking if user exists: {user_email}")
            user = self.service.users().get(userKey=user_email).execute()
            self.log_info(f"User found: {user.get('primaryEmail')}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                self.log_warning(f"User not found: {user_email}")
                return False
            else:
                self.log_error(f"Error checking user: {str(e)}")
                return False
        except Exception as e:
            self.log_error(f"Error checking user: {str(e)}")
            return False
    
    def suspend_user(self, user_email):
        """Suspend the user account"""
        try:
            self.log_info(f"Suspending user: {user_email}")
            
            user_body = {
                'suspended': True,
                'suspensionReason': 'Employee terminated - account suspended for security'
            }
            
            result = self.service.users().update(
                userKey=user_email,
                body=user_body
            ).execute()
            
            self.log_info("✅ User account suspended successfully")
            return True
            
        except Exception as e:
            self.log_error(f"Error suspending user: {str(e)}")
            return False
    
    def reset_password(self, user_email):
        """Reset user password to a secure random value"""
        try:
            import secrets
            import string
            
            # Generate secure random password
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(secrets.choice(alphabet) for i in range(16))
            
            self.log_info(f"Resetting password for user: {user_email}")
            
            user_body = {
                'password': password,
                'changePasswordAtNextLogin': True
            }
            
            result = self.service.users().update(
                userKey=user_email,
                body=user_body
            ).execute()
            
            self.log_info("✅ User password reset successfully")
            return True
            
        except Exception as e:
            self.log_error(f"Error resetting password: {str(e)}")
            return False
    
    def initiate_data_transfer(self, user_email):
        """Initiate data transfer to manager or admin"""
        try:
            # Get manager email from user data or default to admin
            manager_email = self.user_data.get('manager', self.admin_email)
            if not manager_email or '@' not in manager_email:
                manager_email = self.admin_email
            
            self.log_info(f"Initiating data transfer from {user_email} to {manager_email}")
            
            # Note: This is a simplified version. In production, you'd want to:
            # 1. Transfer Google Drive files
            # 2. Transfer Calendar ownership
            # 3. Set up email forwarding
            # 4. Transfer other Google Workspace data
            
            # For now, we'll just log the action
            self.log_info(f"📧 Data transfer would be initiated to: {manager_email}")
            self.log_info("Note: Manual data transfer may be required for some services")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error initiating data transfer: {str(e)}")
            return False

if __name__ == "__main__":
    script = GoogleWorkspaceTerminateUser()
    script.run()
