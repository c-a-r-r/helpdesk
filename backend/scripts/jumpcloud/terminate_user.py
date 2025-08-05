#!/usr/bin/env python3
"""
JumpCloud User Termination Script  
Terminates a user in JumpCloud directory - suspends user and logs associated systems
Based on Google Apps Script functionality
"""
import sys
import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # Add backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add scripts directory

from base_script import BaseUserScript
from aws_secrets import get_jumpcloud_api_key

class TerminateJumpCloudUser(BaseUserScript):
    """Terminates a user in JumpCloud directory"""

    def __init__(self):
        super().__init__()
        self.api_key = None
        self.base_url = "https://console.jumpcloud.com/api"
        
    def get_jumpcloud_api_key(self) -> str:
        """Retrieve JumpCloud API key using the centralized secrets manager"""
        try:
            if not self.api_key:
                self.api_key = get_jumpcloud_api_key()
                self.log_info("Retrieved JumpCloud API key successfully")
            return self.api_key
        except Exception as e:
            raise Exception(f"Error retrieving JumpCloud API key: {e}")

    def get_headers(self) -> Dict[str, str]:
        """Get common headers for JumpCloud API requests"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json", 
            "x-api-key": self.get_jumpcloud_api_key()
        }

    def get_user_id_by_email(self, email: str) -> Optional[str]:
        """Get JumpCloud user ID by email address"""
        try:
            url = f"{self.base_url}/systemusers"
            params = {
                "limit": 1,
                "filter": f"email:{email}"
            }
            
            response = requests.get(url, headers=self.get_headers(), params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            users = data.get("results", [])
            
            if users:
                user_id = users[0].get("_id")
                self.log_info(f"Found JumpCloud user ID: {user_id} for email: {email}")
                return user_id
            else:
                self.log_warning(f"No JumpCloud user found for email: {email}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.log_error(f"Failed to get user ID for {email}: {str(e)}")
            return None

    def get_user_system_associations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get systems associated with the user (DirectBind)"""
        try:
            url = f"{self.base_url}/v2/users/{user_id}/associations"
            params = {"targets": "system"}
            
            response = requests.get(url, headers=self.get_headers(), params=params, timeout=30)
            response.raise_for_status()
            
            associations = response.json()
            self.log_info(f"Found {len(associations)} system associations for user {user_id}")
            return associations
            
        except requests.exceptions.RequestException as e:
            self.log_error(f"Failed to get system associations for user {user_id}: {str(e)}")
            return []

    def get_system_display_name(self, system_id: str) -> Optional[str]:
        """Get system display name by system ID"""
        try:
            url = f"{self.base_url}/systems/{system_id}"
            
            response = requests.get(url, headers=self.get_headers(), timeout=30)
            response.raise_for_status()
            
            system_data = response.json()
            display_name = system_data.get("displayName")
            self.log_info(f"System {system_id} display name: {display_name}")
            return display_name
            
        except requests.exceptions.RequestException as e:
            self.log_error(f"Failed to get system display name for {system_id}: {str(e)}")
            return None

    def suspend_user(self, user_id: str) -> bool:
        """Suspend the user in JumpCloud"""
        try:
            url = f"{self.base_url}/systemusers/{user_id}"
            payload = {
                "state": "SUSPENDED",
                "suspended": True
            }
            
            response = requests.put(url, headers=self.get_headers(), json=payload, timeout=30)
            response.raise_for_status()
            
            self.log_info(f"User {user_id} suspended successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_error(f"Failed to suspend user {user_id}: {str(e)}")
            return False

    def validate_user_data(self) -> bool:
        """Validate required fields for JumpCloud user termination"""
        if not self.user_data.get("company_email"):
            self.log_error("Missing required field: company_email")
            return False

        if "@" not in self.user_data.get("company_email", ""):
            self.log_error("Invalid email format")
            return False

        return True

    def execute(self) -> Dict[str, Any]:
        """Execute JumpCloud user termination"""
        email = self.user_data.get("company_email")
        
        self.log_info(f"Starting JumpCloud user termination for: {email}")

        try:
            # Step 1: Get user ID by email
            user_id = self.get_user_id_by_email(email)
            if not user_id:
                return {
                    "status": "failed",
                    "error": f"User not found in JumpCloud",
                    "message": f"No JumpCloud user found for email: {email}"
                }

            # Step 2: Get system associations
            associations = self.get_user_system_associations(user_id)
            associated_systems = []
            
            for association in associations:
                if association.get("to", {}).get("id"):
                    system_id = association["to"]["id"]
                    display_name = self.get_system_display_name(system_id)
                    if display_name:
                        associated_systems.append({
                            "system_id": system_id,
                            "display_name": display_name
                        })

            # Step 3: Suspend the user
            suspend_success = self.suspend_user(user_id)
            
            # Step 4: Prepare result
            result = {
                "jumpcloud_user_id": user_id,
                "email": email,
                "status": "completed" if suspend_success else "partial",
                "user_suspended": suspend_success,
                "associated_systems": associated_systems,
                "systems_count": len(associated_systems),
                "terminated_at": datetime.now().isoformat(),
                "message": f"JumpCloud user {email} {'terminated' if suspend_success else 'partially terminated'}"
            }

            if suspend_success:
                if associated_systems:
                    self.log_info(f"User {email} suspended successfully. Found {len(associated_systems)} associated systems.")
                    for system in associated_systems:
                        self.log_info(f"  - System: {system['display_name']} (ID: {system['system_id']})")
                else:
                    self.log_info(f"User {email} suspended successfully. No associated systems found.")
            else:
                result["error"] = "Failed to suspend user in JumpCloud"

            return result

        except Exception as e:
            error_msg = f"JumpCloud user termination failed: {str(e)}"
            self.log_error(error_msg)
            return {
                "status": "failed", 
                "error": error_msg, 
                "message": f"Failed to terminate JumpCloud user {email}"
            }


def main():
    script = TerminateJumpCloudUser()
    script.run()


if __name__ == "__main__":
    main()
