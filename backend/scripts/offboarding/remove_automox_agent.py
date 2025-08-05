#!/usr/bin/env python3
"""
Automox Agent Removal Script
Removes the Automox agent from a specified device
"""
import os
import sys
import requests
from pathlib import Path

# Add the parent directory to the path to import base_script
sys.path.append(str(Path(__file__).parent.parent))
from base_script import BaseUserScript

class AutomoxRemoveAgent(BaseUserScript):
    """Script to remove Automox agent from a device"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('AUTOMOX_API_KEY')
        self.base_url = "https://console.automox.com/api"
    
    def validate_user_data(self) -> bool:
        """Validate that we have the required user data"""
        if not self.user_data:
            self.log_error("No user data provided")
            return False
        
        # We need either hostname or company_email to find the device
        if not self.user_data.get('hostname') and not self.user_data.get('company_email'):
            self.log_error("Either hostname or company_email is required")
            return False
        
        if not self.api_key:
            self.log_error("AUTOMOX_API_KEY environment variable not set")
            return False
        
        return True
    
    def execute(self):
        """Execute the Automox agent removal"""
        try:
            self.log_info("Starting Automox agent removal process")
            
            # Find devices associated with the user
            devices = self.find_user_devices()
            if not devices:
                return {"status": "warning", "message": "No Automox devices found for user"}
            
            removed_devices = []
            failed_devices = []
            
            for device in devices:
                device_id = device.get('id')
                device_name = device.get('name', 'Unknown')
                
                self.log_info(f"Processing device: {device_name} (ID: {device_id})")
                
                # Remove the agent from the device
                if self.remove_agent(device_id, device_name):
                    removed_devices.append({
                        'id': device_id,
                        'name': device_name
                    })
                else:
                    failed_devices.append({
                        'id': device_id,
                        'name': device_name
                    })
            
            if removed_devices:
                self.log_info(f"✅ Successfully removed Automox agent from {len(removed_devices)} device(s)")
            
            if failed_devices:
                self.log_warning(f"⚠️ Failed to remove agent from {len(failed_devices)} device(s)")
            
            return {
                "status": "success" if removed_devices and not failed_devices else "partial" if removed_devices else "failed",
                "message": f"Processed {len(devices)} device(s)",
                "details": {
                    "removed_devices": removed_devices,
                    "failed_devices": failed_devices,
                    "total_processed": len(devices)
                }
            }
            
        except Exception as e:
            self.log_error(f"Automox agent removal failed: {str(e)}")
            return {"status": "failed", "message": str(e)}
    
    def find_user_devices(self):
        """Find devices associated with the user"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Get all organizations first
            orgs_url = f"{self.base_url}/orgs"
            response = requests.get(orgs_url, headers=headers)
            
            if response.status_code != 200:
                self.log_error(f"Failed to get organizations: {response.status_code}")
                return []
            
            orgs = response.json()
            all_devices = []
            
            # Search devices in each organization
            for org in orgs:
                org_id = org.get('id')
                self.log_info(f"Searching devices in organization: {org.get('name', org_id)}")
                
                devices_url = f"{self.base_url}/servers"
                params = {'o': org_id}
                
                devices_response = requests.get(devices_url, headers=headers, params=params)
                
                if devices_response.status_code == 200:
                    devices = devices_response.json()
                    
                    # Filter devices by hostname or user email
                    hostname = self.user_data.get('hostname', '').lower()
                    company_email = self.user_data.get('company_email', '').lower()
                    username = self.user_data.get('username', '').lower()
                    
                    for device in devices:
                        device_name = device.get('name', '').lower()
                        
                        # Check if device matches user criteria
                        match = False
                        
                        if hostname and hostname in device_name:
                            match = True
                            self.log_info(f"Found device by hostname match: {device.get('name')}")
                        
                        elif company_email:
                            # Check if device has user info that matches email
                            if company_email.split('@')[0] in device_name:
                                match = True
                                self.log_info(f"Found device by email match: {device.get('name')}")
                        
                        elif username and username in device_name:
                            match = True
                            self.log_info(f"Found device by username match: {device.get('name')}")
                        
                        if match:
                            all_devices.append(device)
            
            self.log_info(f"Found {len(all_devices)} matching device(s)")
            return all_devices
            
        except Exception as e:
            self.log_error(f"Error finding devices: {str(e)}")
            return []
    
    def remove_agent(self, device_id, device_name):
        """Remove Automox agent from a specific device"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Delete the device from Automox (this removes the agent)
            url = f"{self.base_url}/servers/{device_id}"
            
            self.log_info(f"Removing device from Automox: {device_name}")
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
                self.log_info(f"✅ Successfully removed device: {device_name}")
                return True
            elif response.status_code == 404:
                self.log_warning(f"Device not found (may already be removed): {device_name}")
                return True  # Consider this a success since device is gone
            else:
                self.log_error(f"Failed to remove device {device_name}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Error removing device {device_name}: {str(e)}")
            return False
    
    def get_device_info(self, device_id):
        """Get detailed information about a device"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/servers/{device_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log_warning(f"Could not get device info: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_error(f"Error getting device info: {str(e)}")
            return None

if __name__ == "__main__":
    script = AutomoxRemoveAgent()
    script.run()
