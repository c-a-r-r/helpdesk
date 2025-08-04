"""
Base script template for user management operations
All scripts should inherit from this base class
"""
import json
import sys
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseUserScript(ABC):
    """Base class for all user management scripts"""
    
    def __init__(self):
        self.user_data = None
        self.execution_logs = []  # Capture logs for database storage
    
    def run(self):
        """Main entry point for script execution"""
        try:
            # Read user data from stdin
            input_data = sys.stdin.read()
            self.user_data = json.loads(input_data)
            
            # Validate required fields
            if not self.validate_user_data():
                self.output_error("Invalid user data provided")
                return
            
            # Execute the main script logic
            result = self.execute()
            
            # Output success result
            self.output_success(result)
            
        except json.JSONDecodeError as e:
            self.output_error(f"Invalid JSON input: {str(e)}")
        except Exception as e:
            self.output_error(f"Script execution failed: {str(e)}")
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """
        Main script logic - must be implemented by subclasses
        Returns: Dictionary with execution results
        """
        pass
    
    @abstractmethod
    def validate_user_data(self) -> bool:
        """
        Validate user data - must be implemented by subclasses
        Returns: True if data is valid, False otherwise
        """
        pass
    
    def output_success(self, result: Dict[str, Any]):
        """Output successful result"""
        output = {
            "success": True,
            "result": result
        }
        print(json.dumps(output))
    
    def output_error(self, error_message: str):
        """Output error result"""
        output = {
            "success": False,
            "error": error_message
        }
        print(json.dumps(output), file=sys.stderr)
        sys.exit(1)
    
    def log_info(self, message: str):
        """Log info message"""
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}]"
        formatted_message = f"{timestamp} [INFO] {message}"
        logger.info(f"[{self.__class__.__name__}] {message}")
        self.execution_logs.append(formatted_message)
    
    def log_error(self, message: str):
        """Log error message"""
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}]"
        formatted_message = f"{timestamp} [ERROR] {message}"
        logger.error(f"[{self.__class__.__name__}] {message}")
        self.execution_logs.append(formatted_message)
    
    def log_warning(self, message: str):
        """Log warning message"""
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}]"
        formatted_message = f"{timestamp} [WARNING] {message}"
        logger.warning(f"[{self.__class__.__name__}] {message}")
        self.execution_logs.append(formatted_message)
    
    def get_execution_logs(self) -> str:
        """Get all execution logs as a single string"""
        return "\n".join(self.execution_logs)

if __name__ == "__main__":
    # This should be overridden in actual script files
    print("This is a base template - should not be executed directly")
    sys.exit(1)
