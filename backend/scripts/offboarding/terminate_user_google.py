#!/usr/bin/env python3
"""
Google Workspace User Termination Script
Comprehensive user termination with dynamic progress updates
"""
import sys
import os
import json
import time
import string
import secrets
import datetime
import asyncio
from typing import Dict, Any, List, Optional
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # Add backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add scripts directory

from base_script import BaseUserScript
from aws_secrets import get_google_credentials

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

# Google Workspace configuration
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.datatransfer'
]
ADMIN_EMAIL = 'it.vault@americor.com'

class TerminateGoogleWorkspaceUser(BaseUserScript):
    """Comprehensive Google Workspace user termination with dynamic progress updates"""
    
    def __init__(self):
        super().__init__()
        self.admin_email = "it.vault@americor.com"
        self.scopes = ["https://www.googleapis.com/auth/admin.directory.user"]
        self.google_user_management_url = "https://admin.googleapis.com/admin/directory/v1/users"
        self.session = None
        self.domain = "americor.com"
        self.progress_steps = [
            "Checking user existence",
            "Changing password",
            "Removing recovery email",
            "Removing recovery phone",
            "Disabling 2-Step Verification",
            "Updating security settings",
            "Hiding from Global Address List",
            "Updating user profile",
            "Signing out from all sessions",
            "Removing from all groups",
            "Finalizing termination"
        ]
        self.current_step = 0
    
    def log_progress(self, message: str, success: bool = True):
        """Log progress with dynamic updates"""
        status_icon = "[SUCCESS]" if success else "[FAILED]"
        self.log_info(f"{status_icon} {message}")
        
        # Update progress
        if self.current_step < len(self.progress_steps):
            self.current_step += 1
            if self.current_step < len(self.progress_steps):
                next_step = self.progress_steps[self.current_step]
                self.log_info(f"[NEXT] {next_step}")
    
    async def setup_google_session(self) -> bool:
        """Setup Google Workspace authenticated session"""
        try:
            self.log_info("Setting up Google Workspace authentication...")
            
            # Get Google service account credentials from AWS Secrets Manager
            google_credentials = self.get_google_credentials()
            if not google_credentials:
                self.log_error("Failed to retrieve Google credentials from AWS Secrets Manager")
                return False
                
            # Parse the service account info
            if isinstance(google_credentials, str):
                service_account_info = json.loads(google_credentials)
            else:
                service_account_info = google_credentials
                
            # Create credentials with domain-wide delegation
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=self.scopes
            )
            
            # Create delegated credentials to impersonate admin user
            delegated_credentials = credentials.with_subject(self.admin_email)
            
            # Create authenticated session
            self.session = AuthorizedSession(delegated_credentials)
            
            self.log_info("Google Workspace authentication successful")
            return True
            
        except Exception as e:
            self.log_error(f"Error setting up Google authentication: {str(e)}")
            return False
    
    async def find_user(self, user_email: str) -> Dict[str, Any]:
        """Find user in Google Workspace using the working pattern"""
        try:
            self.log_info(f"Searching for user: {user_email}")
            
            # Try direct user lookup first (same as working script)
            try:
                url = f"{self.google_user_management_url}/{user_email}"
                self.log_info(f"Direct lookup URL: {url}")
                
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    self.log_info(f"Found user directly: {user_data.get('primaryEmail')}")
                    return {
                        "found": True,
                        "user": user_data,
                        "method": "direct_lookup"
                    }
                else:
                    self.log_info(f"Direct lookup failed with status: {response.status_code}")
                    if response.status_code != 404:
                        self.log_info(f"Response: {response.text}")
                        
            except Exception as direct_error:
                self.log_info(f"Direct lookup exception: {str(direct_error)}")
                
            # Try listing users with domain (fallback)
            try:
                self.log_info(f"Trying user list in domain: {self.domain}")
                list_url = f"{self.google_user_management_url}?domain={self.domain}&maxResults=500"
                
                response = self.session.get(list_url, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    users = result.get('users', [])
                    self.log_info(f"Found {len(users)} users in domain")
                    
                    # Search for our specific user
                    for user in users:
                        if user.get('primaryEmail', '').lower() == user_email.lower():
                            self.log_info(f"Found user via list: {user.get('primaryEmail')}")
                            return {
                                "found": True,
                                "user": user,
                                "method": "list_search"
                            }
                    
                    # Log sample of users for debugging
                    self.log_info(f"Sample users in domain {self.domain}:")
                    for i, user in enumerate(users[:5]):
                        self.log_info(f"  - {user.get('primaryEmail')}")
                        if i >= 4:
                            break
                else:
                    self.log_info(f"List query failed with status: {response.status_code}")
                    self.log_info(f"Response: {response.text}")
                    
            except Exception as list_error:
                self.log_info(f"List search exception: {str(list_error)}")
            
            return {
                "found": False,
                "user": None,
                "method": "not_found"
            }
            
        except Exception as e:
            self.log_error(f"Error in find_user: {str(e)}")
            return {
                "found": False,
                "user": None,
                "method": "error",
                "error": str(e)
            }
    
    async def move_to_terminated_ou(self, user_email: str) -> bool:
        """Move user to terminated OU"""
        try:
            self.log_info(f"Moving user to terminated OU...")
            
            current_date = datetime.datetime.utcnow()
            org_unit = f"/zz-Terminated Users/Term month - {current_date.strftime('%Y-%m')}"
            
            url = f"{self.google_user_management_url}/{user_email}"
            payload = {"orgUnitPath": org_unit}
            
            self.log_info(f"Moving to OU: {org_unit}")
            response = self.session.patch(url, json=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                self.log_info(f"Successfully moved to OU: {org_unit}")
                return True
            else:
                self.log_error(f"Failed to move to OU. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Error moving to OU: {str(e)}")
            return False
    
    async def apply_termination_settings(self, user_email: str) -> bool:
        """Apply all termination settings (same as working script)"""
        try:
            self.log_info(f"Applying termination settings...")
            
            # Generate new random password
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*()") for _ in range(14))
            
            url = f"{self.google_user_management_url}/{user_email}"
            
            # Same payload as working script
            deactivation_payload = {
                "password": new_password,
                "recoveryEmail": "",
                "recoveryPhone": "",
                "isEnrolledIn2Sv": False,
                "changePasswordAtNextLogin": False,
                "includeInGlobalAddressList": False,
                "suspended": True,
            }
            
            self.log_info(f"Applying: password reset, removing recovery info, disabling 2SV, suspending...")
            response = self.session.patch(url, json=deactivation_payload, timeout=10)
            
            if response.status_code in [200, 204]:
                self.log_info(f"Successfully applied termination settings")
                return True
            else:
                self.log_error(f"Failed to apply settings. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Error applying termination settings: {str(e)}")
            return False
    
    async def verify_termination(self, user_email: str, expected_ou: str) -> Dict[str, Any]:
        """Verify the termination was successful"""
        try:
            self.log_info(f"Verifying termination status...")
            
            url = f"{self.google_user_management_url}/{user_email}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                
                current_ou = user_data.get("orgUnitPath", "")
                is_suspended = user_data.get("suspended", False)
                is_in_gal = user_data.get("includeInGlobalAddressList", True)
                
                verification = {
                    "ou_correct": current_ou == expected_ou,
                    "is_suspended": is_suspended,
                    "hidden_from_gal": not is_in_gal,
                    "current_ou": current_ou,
                    "expected_ou": expected_ou
                }
                
                if verification["ou_correct"] and verification["is_suspended"] and verification["hidden_from_gal"]:
                    self.log_info(f"Termination verification successful")
                    return {"verified": True, "details": verification}
                else:
                    self.log_info(f"Termination completed but verification found issues: {verification}")
                    return {"verified": False, "details": verification}
            else:
                self.log_error(f"Failed to verify termination. Status: {response.status_code}")
                return {"verified": False, "error": f"Verification failed: {response.status_code}"}
                
        except Exception as e:
            self.log_error(f"Error verifying termination: {str(e)}")
            return {"verified": False, "error": str(e)}
    
    def execute(self) -> Dict[str, Any]:
        """Execute the complete Google Workspace termination process"""
        # Run async code in sync context
        return asyncio.run(self.async_execute())
    
    async def async_execute(self) -> Dict[str, Any]:
        """Execute the complete Google Workspace termination process (async implementation)"""
        start_time = datetime.datetime.now()
        user_email = self.user_data.get("company_email")
        
        if not user_email:
            return {
                "success": False,
                "error": "User email is required",
                "status": "failed"
            }
        
        self.log_info(f"Starting Google Workspace termination for: {user_email}")
        
        try:
            # Step 1: Setup authentication
            if not await self.setup_google_session():
                return {
                    "success": False,
                    "error": "Failed to authenticate with Google Workspace",
                    "status": "failed"
                }
            
            # Step 2: Find the user
            self.log_info(f"Step 1/4: Finding user in Google Workspace...")
            user_search = await self.find_user(user_email)
            
            if not user_search["found"]:
                error_msg = f"User {user_email} not found in Google Workspace"
                if "error" in user_search:
                    error_msg += f": {user_search['error']}"
                    
                return {
                    "success": True,  # Consider this success since user doesn't exist
                    "result": {
                        "status": "not_found",
                        "message": error_msg,
                        "search_method": user_search.get("method", "unknown")
                    }
                }
            
            self.log_info(f"Found user via {user_search['method']}")
            
            # Step 3: Move to terminated OU
            self.log_info(f"Step 2/4: Moving to terminated OU...")
            current_date = datetime.datetime.utcnow()
            expected_ou = f"/zz-Terminated Users/Term month - {current_date.strftime('%Y-%m')}"
            
            ou_success = await self.move_to_terminated_ou(user_email)
            
            # Step 4: Apply termination settings
            self.log_info(f"Step 3/4: Applying termination settings...")
            settings_success = await self.apply_termination_settings(user_email)
            
            # Step 5: Verify termination
            self.log_info(f"Step 4/4: Verifying termination...")
            verification = await self.verify_termination(user_email, expected_ou)
            
            # Calculate execution time
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            
            # Prepare result
            result = {
                "status": "completed",
                "email": user_email,
                "ou_moved": ou_success,
                "settings_applied": settings_success,
                "verification": verification,
                "terminated_at": datetime.datetime.utcnow().isoformat(),
                "execution_time_seconds": round(execution_time, 2),
                "message": f"Google Workspace user {user_email} terminated successfully"
            }
            
            overall_success = ou_success and settings_success
            
            if overall_success:
                self.log_info(f"Google Workspace termination completed successfully for {user_email}")
            else:
                self.log_error(f"Google Workspace termination completed with issues for {user_email}")
            
            return {
                "success": overall_success,
                "result": result
            }
            
        except Exception as e:
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            error_msg = f"Error during Google Workspace termination: {str(e)}"
            self.log_error(f"{error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "status": "failed",
                "execution_time_seconds": round(execution_time, 2)
            }
    
    def validate_user_data(self) -> bool:
        """Validate required user data"""
        if not self.user_data.get("company_email"):
            self.log_error("Company email is required")
            return False
        return True
    
    def get_google_credentials(self):
        """Get Google credentials from AWS Secrets Manager"""
        try:
            return get_google_credentials()
        except Exception as e:
            self.log_error(f"Error getting Google credentials: {str(e)}")
            return None

# Main execution function for direct script execution
if __name__ == "__main__":
    script = TerminateGoogleWorkspaceUser()
    script.run()
