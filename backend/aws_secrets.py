"""
AWS Secrets Manager and Environment Variable Handler
Provides a unified interface for retrieving secrets from either AWS Secrets Manager or environment variables
"""
import os
import json
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SecretsManager:
    """Handles retrieving secrets from AWS Secrets Manager or environment variables"""
    
    def __init__(self):
        self.use_aws_secrets = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"
        self.region = os.getenv("AWS_REGION", "us-west-2")
        self.secret_arn = os.getenv("AWS_SECRET_ARN", "arn:aws:secretsmanager:us-west-2:134308154914:secret:helpdesk-crm/prod-zUcloT")
        
    def get_jumpcloud_api_key(self) -> str:
        """Get JumpCloud API key from AWS Secrets Manager"""
        if self.use_aws_secrets:
            try:
                # Get JumpCloud API key from the main secrets
                secret_data = self._get_from_aws_secrets_dict()
                api_key = secret_data.get("jumpcloud_api_key", "")
                
                if not api_key:
                    raise ValueError("JumpCloud API key not found in AWS Secrets Manager")
                
                logger.info("Retrieved JumpCloud API key from AWS Secrets Manager")
                return api_key
                
            except Exception as e:
                logger.error(f"Failed to retrieve JumpCloud API key from AWS Secrets Manager: {e}")
                raise ValueError(f"Error retrieving JumpCloud API key from AWS Secrets: {e}")
        else:
            # Fallback to environment variable for development
            api_key = os.getenv("JUMPCLOUD_API_KEY")
            if not api_key:
                raise ValueError("JumpCloud API key not found. Either set JUMPCLOUD_API_KEY environment variable or enable AWS Secrets Manager")
            logger.info("Retrieved JumpCloud API key from environment variable")
            return api_key
    
    def get_google_credentials(self) -> Dict[str, Any]:
        """Get Google Workspace credentials from AWS Secrets Manager"""
        if self.use_aws_secrets:
            try:
                session = boto3.session.Session()
                client = session.client(service_name="secretsmanager", region_name=self.region)
                
                # First try to get Google credentials from the main helpdesk secret
                try:
                    logger.info(f"Trying to retrieve Google credentials from main secret: {self.secret_arn}")
                    response = client.get_secret_value(SecretId=self.secret_arn)
                    secret_data = json.loads(response["SecretString"])
                    
                    # Look for google credentials in the main secret
                    if "google_service_account" in secret_data:
                        logger.info("Found Google service account credentials in main secret")
                        google_creds = secret_data["google_service_account"]
                        if isinstance(google_creds, str):
                            return json.loads(google_creds)
                        return google_creds
                        
                except Exception as main_secret_error:
                    logger.info(f"Could not get Google credentials from main secret: {main_secret_error}")
                
                # Fallback: try the dedicated Google secret
                google_secret_arn = "arn:aws:secretsmanager:us-west-2:134308154914:secret:google-service-account-signature-secret-KHaS4K"
                logger.info(f"Trying dedicated Google secret: {google_secret_arn}")
                
                response = client.get_secret_value(SecretId=google_secret_arn)
                secret_data = json.loads(response["SecretString"])
                
                logger.info("Successfully retrieved Google service account credentials from dedicated secret")
                return secret_data
                    
            except ClientError as e:
                error_code = e.response['Error']['Code']
                logger.error(f"AWS Secrets Manager error retrieving Google credentials ({error_code}): {e.response['Error']['Message']}")
                return {}
            except Exception as e:
                logger.error(f"Failed to retrieve Google credentials from AWS Secrets Manager: {e}")
                return {}
        else:
            # For development, return empty dict to indicate credentials not available
            logger.warning("Google credentials not configured for development environment (AWS Secrets disabled)")
            return {}
    
    def get_freshdesk_credentials(self) -> Dict[str, str]:
        """Get Freshdesk credentials from AWS Secrets or environment variables"""
        if self.use_aws_secrets:
            secret_data = self._get_from_aws_secrets_dict()
            return {
                "api_key": secret_data.get("freshdesk_api_key", ""),
                "domain": secret_data.get("freshdesk_domain", "")
            }
        else:
            api_key = os.getenv("FRESHDESK_API_KEY", "")
            domain = os.getenv("FRESHDESK_DOMAIN", "")
            if not api_key or not domain:
                logger.warning("Freshdesk credentials not fully configured in environment variables")
            return {
                "api_key": api_key,
                "domain": domain
            }
    
    def _get_from_aws_secrets(self, key: str) -> str:
        """Retrieve a specific key from AWS Secrets Manager"""
        secret_data = self._get_from_aws_secrets_dict()
        value = secret_data.get(key)
        if not value:
            raise ValueError(f"{key} not found in AWS Secrets Manager")
        logger.info(f"Retrieved {key} from AWS Secrets Manager")
        return value
    
    def _get_from_aws_secrets_dict(self) -> Dict[str, Any]:
        """Retrieve all secrets from AWS Secrets Manager as a dictionary"""
        try:
            session = boto3.session.Session()
            client = session.client(service_name="secretsmanager", region_name=self.region)
            
            response = client.get_secret_value(SecretId=self.secret_arn)
            secret_data = json.loads(response["SecretString"])
            
            return secret_data
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'DecryptionFailureException':
                raise Exception("Secrets Manager can't decrypt the protected secret text using the provided KMS key")
            elif error_code == 'InternalServiceErrorException':
                raise Exception("An error occurred on the server side")
            elif error_code == 'InvalidParameterException':
                raise Exception("Invalid parameter provided to Secrets Manager")
            elif error_code == 'InvalidRequestException':
                raise Exception("Invalid request to Secrets Manager")
            elif error_code == 'ResourceNotFoundException':
                raise Exception("The requested secret was not found")
            else:
                raise Exception(f"AWS Secrets Manager error: {e}")
        except Exception as e:
            raise Exception(f"Error retrieving secrets from AWS: {e}")

# Global instance
secrets_manager = SecretsManager()

# Convenience functions for backward compatibility
def get_jumpcloud_api_key() -> str:
    """Get JumpCloud API key"""
    return secrets_manager.get_jumpcloud_api_key()

def get_google_credentials() -> Dict[str, Any]:
    """Get Google Workspace credentials"""
    return secrets_manager.get_google_credentials()

def get_freshdesk_credentials() -> Dict[str, str]:
    """Get Freshdesk credentials"""
    return secrets_manager.get_freshdesk_credentials()
