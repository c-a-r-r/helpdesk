#!/usr/bin/env python3
"""
JumpCloud User Creation Script  
Creates a new user in JumpCloud directory
"""
import sys
import os
import json
import time
import requests
import string
import secrets
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # Add backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add scripts directory

from base_script import BaseUserScript
from aws_secrets import get_jumpcloud_api_key
from typing import Dict, Any

class CreateJumpCloudUser(BaseUserScript):
    """Creates a user in JumpCloud directory"""

    def get_jumpcloud_api_key(self) -> str:
        """Retrieve JumpCloud API key using the centralized secrets manager"""
        try:
            api_key = get_jumpcloud_api_key()
            self.log_info("Retrieved JumpCloud API key successfully")
            return api_key
        except Exception as e:
            raise Exception(f"Error retrieving JumpCloud API key: {e}")

    def validate_user_data(self) -> bool:
        """Validate required fields for JumpCloud user creation"""
        required_fields = ["display_name", "display_last_name", "company_email", "username"]
        for field in required_fields:
            if not self.user_data.get(field):
                self.log_error(f"Missing required field: {field}")
                return False

        if "@" not in self.user_data.get("company_email", ""):
            self.log_error("Invalid email format")
            return False

        return True

    def execute(self) -> Dict[str, Any]:
        """Execute JumpCloud user creation"""
        username = self.user_data["username"]
        email = self.user_data["company_email"]

        self.log_info(f"Creating JumpCloud user: {email}")

        try:
            api_key = self.get_jumpcloud_api_key()

            jumpcloud_user = {
                "username": username,
                "email": email,
                "firstname": self.user_data["display_name"],
                "lastname": self.user_data["display_last_name"],
                "displayname": f"{self.user_data['display_name']} {self.user_data['display_last_name']}",
                "department": self.user_data.get("department", ""),
                "company": self.user_data.get("company", "Americor"),
                "jobTitle": self.user_data.get("title", ""),
                "password": self.user_data.get("password", ""),
                "activated": True,
                "password_expired": True,
                "enable_mfa": True,
                "sudo": False
            }

            headers = {"Content-Type": "application/json", "x-api-key": api_key}
            response = requests.post(
                "https://console.jumpcloud.com/api/systemusers",
                headers=headers,
                json=jumpcloud_user,
                timeout=30,
            )

            self.log_info(f"JumpCloud API response status: {response.status_code}")
            response.raise_for_status()
            jc_response = response.json()

            return {
                "jumpcloud_user_id": jc_response.get("id"),
                "username": username,
                "email": email,
                "status": "created",
                "message": f"JumpCloud user {username} created successfully",
                "created_at": jc_response.get("created"),
                "display_name": jc_response.get("displayname"),
                "mfa_enabled": jc_response.get("enable_mfa", True),
                "password_expired": jc_response.get("password_expired", True),
                "activated": jc_response.get("activated", True),
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"JumpCloud API request failed: {str(e)}"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_msg += f" - {e.response.json()}"
                except:
                    error_msg += f" - HTTP {e.response.status_code}"

            self.log_error(error_msg)
            return {"status": "failed", "error": error_msg, "message": f"Failed to create JumpCloud user {username}"}

        except Exception as e:
            error_msg = f"Failed to create JumpCloud user: {str(e)}"
            self.log_error(error_msg)
            return {"status": "failed", "error": error_msg, "message": f"Failed to create JumpCloud user {username}"}


def main():
    script = CreateJumpCloudUser()
    script.run()


if __name__ == "__main__":
    main()