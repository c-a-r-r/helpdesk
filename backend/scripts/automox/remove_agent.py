#!/usr/bin/env python3
"""
Automox Agent Removal Script for Offboarding
Finds and deletes Automox agents by hostname during user offboarding
"""

import boto3
import json
import requests
import os
import sys
from typing import Optional, Dict, Any


class AutomoxManager:
    def __init__(self, environment: str = "PROD"):
        """Initialize Automox manager with credentials from AWS Secrets Manager"""
        self.environment = environment
        self.base_url = "https://console.automox.com/api"
        
        # Get credentials from AWS Secrets Manager
        self._load_credentials()
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _load_credentials(self):
        """Load API credentials from AWS Secrets Manager"""
        try:
            # Use the production secret ARN
            secret_arn = os.getenv(
                "AUTOMOX_SECRET_ARN", 
                "arn:aws:secretsmanager:us-west-2:134308154914:secret:helpdesk-crm/automox-credentials"
            )
            
            client = boto3.client("secretsmanager", region_name="us-west-2")
            response = client.get_secret_value(SecretId=secret_arn)
            secrets = json.loads(response["SecretString"])
            
            # Get environment-specific credentials
            self.api_key = secrets.get(f"AUTOMOX_API_KEY_{self.environment}")
            self.org_id = secrets.get(f"AUTOMOX_ORG_ID_{self.environment}")
            
            if not self.api_key or not self.org_id:
                raise ValueError(f"Missing Automox credentials for environment: {self.environment}")
                
        except Exception as e:
            print(f"Error loading Automox credentials: {e}")
            raise
    
    def get_all_devices(self) -> list:
        """Retrieve all devices from Automox"""
        print("Retrieving all Automox devices...")
        all_devices = []
        page = 0
        limit = 500
        
        while True:
            params = {
                "o": self.org_id,
                "limit": str(limit),
                "page": str(page)
            }
            
            try:
                response = requests.get(
                    f"{self.base_url}/servers",
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"Error retrieving devices on page {page}: {response.status_code} - {response.text}")
                    break
                
                batch = response.json()
                if not batch:
                    break
                
                all_devices.extend(batch)
                print(f"Retrieved page {page} ({len(batch)} devices)")
                page += 1
                
            except requests.RequestException as e:
                print(f"Network error on page {page}: {e}")
                break
        
        print(f"Total devices retrieved: {len(all_devices)}")
        return all_devices
    
    def find_device_by_hostname(self, hostname: str) -> Optional[Dict[Any, Any]]:
        """Find a device by hostname (display_name)"""
        if not hostname:
            print("No hostname provided")
            return None
        
        print(f"Searching for device with hostname: '{hostname}'")
        
        # Get all devices
        devices = self.get_all_devices()
        
        # Search for exact match first
        target_device = next(
            (device for device in devices if device.get("display_name") == hostname),
            None
        )
        
        if target_device:
            print(f"Found exact match: Device '{hostname}' with ID: {target_device['id']}")
            return target_device
        
        # Search for partial matches (case-insensitive)
        hostname_lower = hostname.lower()
        partial_matches = [
            device for device in devices 
            if hostname_lower in device.get("display_name", "").lower()
        ]
        
        if partial_matches:
            print(f"Found {len(partial_matches)} partial matches:")
            for device in partial_matches[:5]:  # Show first 5 matches
                print(f"  - {device.get('display_name')} (ID: {device['id']})")
            
            if len(partial_matches) == 1:
                print("Using the only partial match")
                return partial_matches[0]
            else:
                print("Multiple partial matches found. Please use exact hostname.")
                return None
        
        print(f"No device found with hostname containing: '{hostname}'")
        return None
    
    def delete_device(self, device_id: str, dry_run: bool = False) -> bool:
        """Delete a device from Automox"""
        if dry_run:
            print(f"DRY RUN: Would delete device with ID: {device_id}")
            return True
        
        try:
            delete_url = f"{self.base_url}/servers/{device_id}"
            delete_params = {"o": self.org_id}
            
            response = requests.delete(
                delete_url,
                headers=self.headers,
                params=delete_params,
                timeout=30
            )
            
            if response.status_code == 204:
                print(f"Device with ID {device_id} successfully deleted from Automox")
                return True
            else:
                print(f"Failed to delete device: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"Network error during deletion: {e}")
            return False
    
    def remove_agent_by_hostname(self, hostname: str, dry_run: bool = False) -> Dict[str, Any]:
        """Main method to find and remove Automox agent by hostname"""
        result = {
            "success": False,
            "message": "",
            "device_id": None,
            "hostname": hostname
        }
        
        try:
            # Find the device
            device = self.find_device_by_hostname(hostname)
            
            if not device:
                result["message"] = f"No Automox device found with hostname: {hostname}"
                return result
            
            device_id = device["id"]
            result["device_id"] = device_id
            
            # Delete the device
            if self.delete_device(device_id, dry_run):
                result["success"] = True
                action = "Would be deleted" if dry_run else "Deleted"
                result["message"] = f"{action} Automox device '{hostname}' (ID: {device_id})"
            else:
                result["message"] = f"Failed to delete Automox device '{hostname}' (ID: {device_id})"
            
        except Exception as e:
            result["message"] = f"Error removing Automox agent: {str(e)}"
        
        return result


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python remove_automox_agent.py <hostname> [--dry-run] [--env PROD|TEST]")
        print("Example: python remove_automox_agent.py A-10V13Z3")
        sys.exit(1)
    
    hostname = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    
    # Get environment
    environment = "PROD"
    if "--env" in sys.argv:
        env_index = sys.argv.index("--env")
        if env_index + 1 < len(sys.argv):
            environment = sys.argv[env_index + 1].upper()
    
    print(f"🤖 Automox Agent Removal - Environment: {environment}")
    print(f"Target hostname: {hostname}")
    if dry_run:
        print("🧪 DRY RUN MODE - No actual deletions will be performed")
    print("-" * 50)
    
    try:
        automox = AutomoxManager(environment=environment)
        result = automox.remove_agent_by_hostname(hostname, dry_run=dry_run)
        
        print(f"Result: {result['message']}")
        
        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


# For integration with the script manager
def execute_script(hostname: str, dry_run: bool = False, environment: str = "PROD") -> Dict[str, Any]:
    """
    Execute Automox agent removal for integration with the helpdesk system
    
    Args:
        hostname: The hostname of the device to remove
        dry_run: If True, don't actually delete anything
        environment: PROD or TEST
    
    Returns:
        Dict with success status and message
    """
    try:
        automox = AutomoxManager(environment=environment)
        return automox.remove_agent_by_hostname(hostname, dry_run=dry_run)
    except Exception as e:
        return {
            "success": False,
            "message": f"Error executing Automox removal: {str(e)}",
            "device_id": None,
            "hostname": hostname
        }


if __name__ == "__main__":
    main()
