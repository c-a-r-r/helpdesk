#!/usr/bin/env python3
"""
JumpCloud User Termination Script
Terminates a user in JumpCloud by suspending their account and removing from groups
"""
import os
import sys
import requests
from pathlib import Path

# Add the parent directory to the path to import base_script
sys.path.append(str(Path(__file__).parent.parent))
from base_script import BaseUserScript

class JumpCloudTerminateUser(BaseUserScript):
    """Script to terminate a user in JumpCloud"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('JUMPCLOUD_API_KEY')
        self.base_url = "https://console.jumpcloud.com/api"
    
    def validate_user_data(self) -> bool:
        """Validate that we have the required user data"""
        if not self.user_data:
            self.log_error("No user data provided")
            return False
        
        required_fields = ['company_email', 'username']
        missing_fields = []
        
        for field in required_fields:
            if not self.user_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            self.log_error(f"Missing required fields: {', '.join(missing_fields)}")
            return False
        
        if not self.api_key:
            self.log_error("JUMPCLOUD_API_KEY environment variable not set")
            return False
        
        return True
    
    def execute(self):
        """Execute the JumpCloud user termination"""
        try:
            self.log_info("Starting JumpCloud user termination process")
            
            # Find the user by email or username
            user_id = self.find_user()
            if not user_id:
                return {"status": "failed", "message": "User not found in JumpCloud"}
            
            self.log_info(f"Found user with ID: {user_id}")
            
            # Suspend the user account
            suspend_result = self.suspend_user(user_id)
            if not suspend_result:
                return {"status": "failed", "message": "Failed to suspend user account"}
            
            # Remove user from all groups
            groups_result = self.remove_from_groups(user_id)
            
            # Unbind user from systems (optional - might want to keep for audit)
            # systems_result = self.unbind_systems(user_id)
            
            self.log_info("JumpCloud user termination completed successfully")
            
            return {
                "status": "success",
                "message": f"User {self.user_data['company_email']} successfully terminated in JumpCloud",
                "details": {
                    "user_id": user_id,
                    "suspended": suspend_result,
                    "groups_removed": groups_result.get('removed_count', 0)
                }
            }
            
        except Exception as e:
            self.log_error(f"JumpCloud termination failed: {str(e)}")
            return {"status": "failed", "message": str(e)}
    
    def find_user(self):
        """Find user in JumpCloud by email or username"""
        try:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'x-api-key': self.api_key
            }
            
            # Search by email first
            email = self.user_data.get('company_email', '')
            username = self.user_data.get('username', '')
            
            # Try searching by email
            url = f"{self.base_url}/systemusers"
            params = {'filter': f'email:eq:{email}'}
            
            self.log_info(f"Searching for user by email: {email}")
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                users = response.json().get('results', [])
                if users:
                    self.log_info(f"Found user by email: {users[0]['id']}")
                    return users[0]['id']
            
            # If not found by email, try by username
            if username:
                params = {'filter': f'username:eq:{username}'}
                self.log_info(f"Searching for user by username: {username}")
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    users = response.json().get('results', [])
                    if users:
                        self.log_info(f"Found user by username: {users[0]['id']}")
                        return users[0]['id']
            
            self.log_warning(f"User not found with email {email} or username {username}")
            return None
            
        except Exception as e:
            self.log_error(f"Error finding user: {str(e)}")
            return None
    
    def suspend_user(self, user_id):
        """Suspend the user account"""
        try:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'x-api-key': self.api_key
            }
            
            url = f"{self.base_url}/systemusers/{user_id}"
            data = {
                'suspended': True,
                'password_expired': True  # Force password expiration
            }
            
            self.log_info(f"Suspending user account: {user_id}")
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code == 200:
                self.log_info("User account suspended successfully")
                return True
            else:
                self.log_error(f"Failed to suspend user: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Error suspending user: {str(e)}")
            return False
    
    def remove_from_groups(self, user_id):
        """Remove user from all JumpCloud groups"""
        try:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'x-api-key': self.api_key
            }
            
            # Get user's current groups
            url = f"{self.base_url}/systemusers/{user_id}/memberof"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                self.log_warning("Could not retrieve user groups")
                return {"removed_count": 0}
            
            groups = response.json()
            removed_count = 0
            
            for group in groups:
                if group.get('type') == 'user_group':
                    group_id = group.get('id')
                    # Remove user from group
                    remove_url = f"{self.base_url}/usergroups/{group_id}/members"
                    remove_data = {
                        'op': 'remove',
                        'type': 'user',
                        'id': user_id
                    }
                    
                    remove_response = requests.post(remove_url, headers=headers, json=remove_data)
                    if remove_response.status_code == 204:
                        self.log_info(f"Removed user from group: {group.get('name', group_id)}")
                        removed_count += 1
                    else:
                        self.log_warning(f"Failed to remove from group {group.get('name', group_id)}")
            
            self.log_info(f"Removed user from {removed_count} groups")
            return {"removed_count": removed_count}
            
        except Exception as e:
            self.log_error(f"Error removing from groups: {str(e)}")
            return {"removed_count": 0}

if __name__ == "__main__":
    script = JumpCloudTerminateUser()
    script.run()
