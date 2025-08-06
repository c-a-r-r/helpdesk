"""
Script Manager for User Management Tools
Handles execution of various user management scripts with database logging
"""
import os
import subprocess
import json
import logging
import time
from typing import Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

logger = logging.getLogger(__name__)

class ScriptManager:
    """Manages execution of user management scripts"""
    
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.jumpcloud_dir = self.scripts_dir / "jumpcloud"
        self.google_dir = self.scripts_dir / "google_workspace"
        self.freshservice_dir = self.scripts_dir / "freshservice"
        self.offboarding_dir = self.scripts_dir / "offboarding"
    
    async def execute_script(self, 
                           script_type: str, 
                           script_name: str, 
                           user_data: Dict[str, Any],
                           db: Session,
                           executed_by: str,
                           user_id: int,
                           additional_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a user management script with database logging
        
        Args:
            script_type: 'jumpcloud', 'google', or 'freshservice'
            script_name: Name of the script to execute
            user_data: User data to pass to the script
            db: Database session for logging
            executed_by: Email of user executing the script
            user_id: ID of the user this script is being run for
            additional_params: Additional parameters for the script
            
        Returns:
            Dictionary with execution results
        """
        # Import here to avoid circular imports
        from crud import ScriptLogCRUD
        from schemas import ScriptLogCreate
        from models import ScriptStatus
        
        # Create initial log entry
        log_data = ScriptLogCreate(
            user_id=user_id,
            script_type=script_type,
            script_name=script_name,
            status=ScriptStatus.RUNNING,
            executed_by=executed_by,
            additional_params=json.dumps(additional_params) if additional_params else None
        )
        
        script_log = ScriptLogCRUD.create(db, log_data)
        start_time = time.time()
        
        try:
            script_path = self._get_script_path(script_type, script_name)
            if not script_path.exists():
                error_msg = f"Script not found: {script_path}"
                
                # Update log with error
                ScriptLogCRUD.update_completion(
                    db, script_log.id, ScriptStatus.FAILED.value, 
                    error_message=error_msg,
                    execution_time_seconds=int(time.time() - start_time)
                )
                
                return {
                    "success": False,
                    "error": error_msg,
                    "output": "",
                    "script_type": script_type,
                    "script_name": script_name,
                    "executed_by": executed_by,
                    "executed_at": datetime.now()
                }
            
            # Merge user data with additional params
            script_input = {**user_data}
            if additional_params:
                script_input.update(additional_params)
            
            # Prepare command
            cmd = ["python", str(script_path)]
            
            # Set up environment to ensure scripts can import aws_secrets module and base_script
            backend_root = str(Path(__file__).parent.parent)
            scripts_dir = str(Path(__file__).parent)
            env = {
                **dict(os.environ),  # Inherit current environment
                "PYTHONPATH": f"{backend_root}:{scripts_dir}"  # Add both backend root and scripts directory
            }
            
            # Execute script with user data as JSON input
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=str(Path(__file__).parent.parent)  # Set working directory to backend root
            )
            
            stdout, stderr = process.communicate(input=json.dumps(script_input))
            execution_time = int(time.time() - start_time)
            
            success = process.returncode == 0
            status = ScriptStatus.SUCCESS if success else ScriptStatus.FAILED
            
            # Update log with completion
            ScriptLogCRUD.update_completion(
                db, script_log.id, status.value,
                output=stdout if success else None,
                error_message=stderr if not success else None,
                execution_time_seconds=execution_time
            )
            
            return {
                "success": success,
                "output": stdout,
                "error": stderr if not success else None,
                "script_type": script_type,
                "script_name": script_name,
                "executed_by": executed_by,
                "executed_at": datetime.now()
            }
            
        except Exception as e:
            execution_time = int(time.time() - start_time)
            error_msg = str(e)
            
            logger.error(f"Error executing script {script_type}/{script_name}: {error_msg}")
            
            # Update log with error
            ScriptLogCRUD.update_completion(
                db, script_log.id, ScriptStatus.FAILED.value,
                error_message=error_msg,
                execution_time_seconds=execution_time
            )
            
            return {
                "success": False,
                "error": error_msg,
                "output": "",
                "script_type": script_type,
                "script_name": script_name,
                "executed_by": executed_by,
                "executed_at": datetime.now()
            }
    
    def _get_script_path(self, script_type: str, script_name: str) -> Path:
        """Get the full path to a script"""
        if script_type == "jumpcloud":
            return self.jumpcloud_dir / f"{script_name}.py"
        elif script_type == "google":
            return self.google_dir / f"{script_name}.py"
        elif script_type == "freshservice":
            return self.freshservice_dir / f"{script_name}.py"
        elif script_type == "offboarding":
            return self.offboarding_dir / f"{script_name}.py"
        else:
            raise ValueError(f"Unknown script type: {script_type}")
    
    def get_available_scripts(self) -> Dict[str, list]:
        """Get list of available scripts by type"""
        return {
            "jumpcloud": self._get_scripts_in_dir(self.jumpcloud_dir),
            "google": self._get_scripts_in_dir(self.google_dir),
            "freshservice": self._get_scripts_in_dir(self.freshservice_dir),
            "offboarding": self._get_scripts_in_dir(self.offboarding_dir)
        }
    
    def _get_scripts_in_dir(self, directory: Path) -> list:
        """Get list of Python scripts in a directory"""
        if not directory.exists():
            return []
        
        scripts = []
        for script_file in directory.glob("*.py"):
            if script_file.name != "__init__.py":
                scripts.append(script_file.stem)
        
        return scripts

# Global script manager instance
script_manager = ScriptManager()
