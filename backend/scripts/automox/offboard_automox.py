"""
Automox integration for offboarding scripts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scripts.automox.remove_agent import execute_script as remove_automox_agent
from scripts.base_script import BaseScript


class AutomoxOffboardingScript(BaseScript):
    """Script to remove Automox agent during offboarding"""
    
    def __init__(self):
        super().__init__(
            name="Automox Agent Removal",
            description="Remove Automox agent by hostname during offboarding"
        )
    
    def execute(self, **params) -> dict:
        """
        Execute Automox agent removal
        
        Required params:
            hostname: The hostname of the device to remove from Automox
        
        Optional params:
            dry_run: If True, don't actually delete (default: False)
            environment: PROD or TEST (default: PROD)
        """
        hostname = params.get('hostname')
        if not hostname:
            return {
                'success': False,
                'message': 'Hostname parameter is required for Automox removal'
            }
        
        dry_run = params.get('dry_run', False)
        environment = params.get('environment', 'PROD')
        
        self.log(f"Removing Automox agent for hostname: {hostname}")
        
        try:
            result = remove_automox_agent(
                hostname=hostname,
                dry_run=dry_run,
                environment=environment
            )
            
            if result['success']:
                self.log(f"Successfully removed Automox agent: {result['message']}")
            else:
                self.log(f"Failed to remove Automox agent: {result['message']}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in Automox removal script: {str(e)}"
            self.log(error_msg)
            return {
                'success': False,
                'message': error_msg
            }


# For direct script manager integration
def get_script_instance():
    """Return script instance for the script manager"""
    return AutomoxOffboardingScript()


if __name__ == "__main__":
    # Command line testing
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Automox offboarding script')
    parser.add_argument('hostname', help='Hostname to remove from Automox')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--env', choices=['PROD', 'TEST'], default='PROD', help='Environment')
    
    args = parser.parse_args()
    
    script = AutomoxOffboardingScript()
    result = script.execute(
        hostname=args.hostname,
        dry_run=args.dry_run,
        environment=args.env
    )
    
    print(f"Result: {result}")
    sys.exit(0 if result['success'] else 1)
