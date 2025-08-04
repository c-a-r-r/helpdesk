#!/usr/bin/env python3
"""
Google Workspace Add Email Aliases Script
Adds email aliases to an existing Google Workspace user
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # Add backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add scripts directory

from base_script import BaseUserScript
from aws_secrets import get_google_credentials
from typing import Dict, Any, List

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

class AddGoogleWorkspaceAliases(BaseUserScript):
    """Adds email aliases to a Google Workspace user"""
    
    def __init__(self):
        super().__init__()
        self.service = None
    
    def setup_google_credentials(self) -> bool:
        """Set up Google Workspace API credentials using centralized secrets manager"""
        try:
            # Get Google credentials using centralized secrets manager
            self.log_info("Retrieving Google service account credentials")
            
            secret_data = get_google_credentials()
            if not secret_data:
                self.log_error("Failed to retrieve Google service account credentials")
                return False
            
            self.log_info("Credentials retrieved successfully, creating service account...")
            
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
            
        except Exception as e:
            self.log_error(f"Failed to setup Google credentials: {str(e)}")
            self.log_error(f"Error type: {type(e).__name__}")
            return False
    
    def validate_user_data(self) -> bool:
        """Validate required fields for adding aliases"""
        if not self.user_data.get('company_email'):
            self.log_error("Missing required field: company_email")
            return False
        
        # Validate email format for primary email
        email = self.user_data.get('company_email', '')
        if '@' not in email:
            self.log_error("Invalid primary email format")
            return False
        
        # Check if any aliases are specified
        credit9_alias = self.user_data.get('credit9_alias', '').strip()
        advantageteam_alias = self.user_data.get('advantageteam_alias', '').strip()
        general_aliases = self.user_data.get('aliases', '')
        
        has_aliases = bool(credit9_alias or advantageteam_alias or general_aliases)
        
        if not has_aliases:
            self.log_error("No aliases specified")
            return False
        
        # Validate alias formats
        aliases_to_validate = []
        
        if credit9_alias:
            aliases_to_validate.append(credit9_alias)
        if advantageteam_alias:
            aliases_to_validate.append(advantageteam_alias)
        
        if general_aliases:
            if isinstance(general_aliases, str):
                additional_aliases = [alias.strip() for alias in general_aliases.split(',') if alias.strip()]
                aliases_to_validate.extend(additional_aliases)
            elif isinstance(general_aliases, list):
                aliases_to_validate.extend(general_aliases)
        
        for alias in aliases_to_validate:
            if '@' not in alias:
                self.log_error(f"Invalid alias format: {alias}")
                return False
        
        return True
    
    def is_alias_exist(self, user_key: str, alias: str) -> bool:
        """Check if alias already exists for the user (matching Google Apps Script pattern)"""
        try:
            aliases_response = self.service.users().aliases().list(userKey=user_key).execute()
            aliases = aliases_response.get('aliases', [])
            
            for existing_alias in aliases:
                if existing_alias.get('alias') == alias:
                    return True
            
            return False
            
        except HttpError as e:
            if e.resp.status == 404:
                # User not found or no aliases
                return False
            else:
                self.log_error(f"Error checking if alias exists: {e}")
                return False
        except Exception as e:
            self.log_error(f"Error checking if alias exists: {e}")
            return False
    
    def execute(self) -> Dict[str, Any]:
        """Execute adding aliases to Google Workspace user (matching Google Apps Script pattern)"""
        email = self.user_data['company_email']
        
        # Get aliases from different possible fields (matching your form structure)
        aliases = []
        
        # Check for individual alias fields (like alias1, alias2 in Google Apps Script)
        credit9_alias = self.user_data.get('credit9_alias', '').strip()
        advantageteam_alias = self.user_data.get('advantageteam_alias', '').strip()
        
        if credit9_alias:
            aliases.append(credit9_alias)
        if advantageteam_alias:
            aliases.append(advantageteam_alias)
        
        # Also check for a general aliases field (comma-separated)
        general_aliases = self.user_data.get('aliases', '')
        if general_aliases:
            if isinstance(general_aliases, str):
                additional_aliases = [alias.strip() for alias in general_aliases.split(',') if alias.strip()]
                aliases.extend(additional_aliases)
            elif isinstance(general_aliases, list):
                aliases.extend(general_aliases)
        
        # Remove duplicates while preserving order
        aliases = list(dict.fromkeys(aliases))
        
        self.log_info(f"Adding aliases to Google Workspace user: {email}")
        self.log_info(f"Aliases to process: {aliases}")
        
        if not aliases:
            return {
                "status": "skipped",
                "message": "No aliases specified",
                "user_email": email,
                "added_aliases": [],
                "failed_aliases": [],
                "total_requested": 0,
                "total_added": 0
            }
        
        if not GOOGLE_API_AVAILABLE:
            self.log_error("Google API libraries not available")
            return {
                "status": "failed",
                "error": "Google API libraries not installed",
                "message": f"Cannot add aliases to {email} - missing dependencies"
            }
        
        if not self.setup_google_credentials():
            return {
                "status": "failed", 
                "error": "Failed to setup Google credentials",
                "message": f"Cannot add aliases to {email} - credential error"
            }
        
        try:
            added_aliases = []
            failed_aliases = []
            status_details = []
            
            for alias in aliases:
                if not alias:  # Skip empty aliases
                    status_details.append(f"Alias is empty - skipped")
                    continue
                
                # Check if alias already exists (matching Google Apps Script pattern)
                if self.is_alias_exist(email, alias):
                    self.log_info(f"Alias {alias} already exists")
                    added_aliases.append(alias)
                    status_details.append(f"Alias {alias} already exists")
                else:
                    try:
                        # Create alias (matching Google Apps Script pattern)
                        alias_body = {
                            "alias": alias
                        }
                        result = self.service.users().aliases().insert(
                            userKey=email,
                            body=alias_body
                        ).execute()
                        
                        added_aliases.append(alias)
                        self.log_info(f"Successfully created alias: {alias}")
                        status_details.append(f"Alias {alias} created")
                        
                    except HttpError as e:
                        error_msg = str(e)
                        self.log_error(f"Failed to create alias {alias}: {error_msg}")
                        failed_aliases.append({"alias": alias, "error": error_msg})
                        status_details.append(f"Error creating alias {alias}")
            
            # Determine overall status
            if not failed_aliases:
                status = "completed" if added_aliases else "skipped"
            else:
                status = "partial" if added_aliases else "failed"
            
            status_summary = " | ".join(status_details)
            
            self.log_info(f"Alias operation completed. Status: {status_summary}")
            
            return {
                "status": status,
                "message": f"Processed {len(aliases)} aliases for {email}. Added: {len(added_aliases)}, Failed: {len(failed_aliases)}",
                "user_email": email,
                "added_aliases": added_aliases,
                "failed_aliases": failed_aliases,
                "total_requested": len(aliases),
                "total_added": len(added_aliases),
                "status_details": status_summary,
                "credit9_alias": credit9_alias if credit9_alias else "Not specified",
                "advantageteam_alias": advantageteam_alias if advantageteam_alias else "Not specified"
            }
            
        except Exception as e:
            error_msg = f"Failed to add aliases: {str(e)}"
            self.log_error(error_msg)
            return {
                "status": "failed",
                "error": error_msg,
                "message": f"Failed to add aliases to {email}"
            }

def main():
    script = AddGoogleWorkspaceAliases()
    script.run()

if __name__ == "__main__":
    main()
