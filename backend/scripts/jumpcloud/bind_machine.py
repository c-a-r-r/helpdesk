#!/usr/bin/env python3
"""
JumpCloud Machine Binding Script
Binds a machine to a user in JumpCloud
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # Add backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add scripts directory

from base_script import BaseUserScript
from aws_secrets import get_jumpcloud_api_key
from typing import Dict, Any
import json
import requests

class JumpCloudBinder:
    def __init__(self, region="us-west-2", logger=None):
        self.logger = logger
        self.api_key = self.get_jumpcloud_api_key()

    def log_info(self, message):
        if self.logger:
            self.logger.log_info(message)
        else:
            print(f"ℹ️ {message}")

    def log_error(self, message):
        if self.logger:
            self.logger.log_error(message)
        else:
            print(f"❌ {message}")

    def get_jumpcloud_api_key(self):
        """Retrieve API key using the centralized secrets manager"""
        try:
            api_key = get_jumpcloud_api_key()
            self.log_info("Retrieved JumpCloud API key successfully")
            return api_key
        except Exception as e:
            raise Exception(f"Error retrieving JumpCloud API key: {e}")

    def find_user_id_by_email(self, email):
        """Get JumpCloud user ID by email"""
        url = f"https://console.jumpcloud.com/api/systemusers?limit=1&filter=email:{email}"
        headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
        
        try:
            resp = requests.get(url, headers=headers, timeout=20)

            if resp.status_code == 200:
                data = resp.json().get("results", [])
                return data[0]["_id"] if data else None
            else:
                self.log_error(f"Failed to get user ID for {email}: {resp.text}")
                return None
        except Exception as e:
            self.log_error(f"Error finding user {email}: {str(e)}")
            return None

    def get_system_id_by_hostname(self, hostname):
        """Get JumpCloud system ID by hostname"""
        url = "https://console.jumpcloud.com/api/search/systems"
        headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}

        payload = {
            "searchFilter": {"searchTerm": hostname, "fields": ["hostname", "displayName"]},
            "fields": "os hostname displayName",
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)

            if resp.status_code == 200:
                results = resp.json().get("results", [])
                return results[0]["_id"] if results else None
            else:
                self.log_error(f"Failed to get system ID for {hostname}: {resp.text}")
                return None
        except Exception as e:
            self.log_error(f"Error finding system {hostname}: {str(e)}")
            return None

    def bind_system_to_user(self, hostname, email):
        """Bind a JumpCloud system to a user"""
        self.log_info(f"Attempting to bind system {hostname} to user {email}")
        
        system_id = self.get_system_id_by_hostname(hostname)
        if not system_id:
            self.log_error(f"System not found for hostname: {hostname}")
            return False

        user_id = self.find_user_id_by_email(email)
        if not user_id:
            self.log_error(f"User not found for email: {email}")
            return False

        url = f"https://console.jumpcloud.com/api/v2/systems/{system_id}/associations"
        headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "attributes": {"sudo": {"enabled": False, "withoutPassword": False}},
            "op": "add",
            "type": "user",
            "id": user_id,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)

            if resp.status_code == 204:
                self.log_info(f"Device {hostname} successfully bound to {email}")
                return True
            else:
                self.log_error(f"Failed to bind device {hostname} to {email}: {resp.text}")
                return False
        except Exception as e:
            self.log_error(f"Error binding system to user: {str(e)}")
            return False

class BindMachineToUser(BaseUserScript):
    """Binds a machine to a user in JumpCloud"""
    
    def validate_user_data(self) -> bool:
        """Validate required fields for machine binding"""
        required_fields = ['company_email', 'hostname']
        
        for field in required_fields:
            if not self.user_data.get(field):
                self.log_error(f"Missing required field: {field}")
                return False
        
        return True
    
    def execute(self) -> Dict[str, Any]:
        """Execute machine binding to user"""
        email = self.user_data['company_email']
        hostname = self.user_data['hostname']
        
        self.log_info(f"Binding machine {hostname} to user {email}")
        
        try:
            # Initialize JumpCloud binder with logger
            binder = JumpCloudBinder(logger=self)
            
            # Perform the binding
            success = binder.bind_system_to_user(hostname, email)
            
            if success:
                self.log_info("Machine binding completed successfully")
                return {
                    "user": email,
                    "machine": hostname,
                    "status": "bound",
                    "message": f"Machine {hostname} successfully bound to user {email}",
                    "binding_id": f"binding_{email}_{hostname}".replace("@", "_").replace(".", "_")
                }
            else:
                raise Exception("Machine binding failed")
            
        except Exception as e:
            self.log_error(f"Failed to bind machine to user: {str(e)}")
            raise

if __name__ == "__main__":
    script = BindMachineToUser()
    script.run()