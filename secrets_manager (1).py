"""
AWS Secrets Manager Integration for RoboKen
Retrieves API keys and credentials from AWS Secrets Manager
"""

import boto3
import json
from typing import Dict, Any
import os

class SecretsManager:
    def __init__(self, region_name: str = "ap-northeast-1"):
        """Initialize Secrets Manager client"""
        self.client = boto3.client('secretsmanager', region_name=region_name)
        self.cache = {}
    
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """
        Retrieve a secret from AWS Secrets Manager
        
        Args:
            secret_name: Name of the secret in Secrets Manager
            
        Returns:
            Dictionary containing the secret values
        """
        # Check cache first
        if secret_name in self.cache:
            return self.cache[secret_name]
        
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            
            # Parse the secret string
            if 'SecretString' in response:
                secret = json.loads(response['SecretString'])
            else:
                # Binary secret (shouldn't happen for API keys)
                secret = response['SecretBinary']
            
            # Cache the result
            self.cache[secret_name] = secret
            return secret
            
        except Exception as e:
            print(f"Error retrieving secret {secret_name}: {str(e)}")
            raise
    
    def get_api_keys(self, environment: str = "prod") -> Dict[str, str]:
        """
        Retrieve all API keys for the specified environment
        
        Args:
            environment: Environment name (prod, stg, demo)
            
        Returns:
            Dictionary with all API keys
        """
        api_keys = {}
        
        # Based on Ms. Kobayashi's naming convention
        # Adjust these paths based on actual secret names in Secrets Manager
        secret_mappings = {
            'openai': f'api/openai/robocane-{environment}',
            'claude': f'api/claude/robocane-{environment}',
            'stripe': f'api/stripe/roboken-{environment}',
            'n8n': f'api/n8n/roboken-{environment}',
            'google_maps': f'api/google-maps/roboken-{environment}',
            'serpapi': f'api/serpapi/roboken-{environment}',
        }
        
        for key_name, secret_name in secret_mappings.items():
            try:
                secret = self.get_secret(secret_name)
                # Assume the secret contains an 'api_key' field
                api_keys[key_name] = secret.get('api_key', secret.get('key', ''))
            except Exception as e:
                print(f"Warning: Could not retrieve {key_name}: {str(e)}")
                api_keys[key_name] = None
        
        return api_keys
    
    def get_email_credentials(self, environment: str = "prod") -> Dict[str, str]:
        """
        Retrieve roboken.ai email credentials
        
        Args:
            environment: Environment name
            
        Returns:
            Dictionary with email and password
        """
        try:
            secret_name = f'email/roboken-{environment}'
            secret = self.get_secret(secret_name)
            return {
                'email': secret.get('email', ''),
                'password': secret.get('password', ''),
                'smtp_host': secret.get('smtp_host', 'smtp.xserver.jp'),
                'smtp_port': secret.get('smtp_port', 587)
            }
        except Exception as e:
            print(f"Warning: Could not retrieve email credentials: {str(e)}")
            return {}


# Singleton instance
_secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    """Get or create the Secrets Manager singleton"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


# Convenience functions
def get_api_keys(environment: str = None) -> Dict[str, str]:
    """Get all API keys for the current environment"""
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'prod')
    
    # Map environment names
    env_map = {
        'production': 'prod',
        'staging': 'stg',
        'demo': 'demo',
        'development': 'dev'
    }
    environment = env_map.get(environment, environment)
    
    sm = get_secrets_manager()
    return sm.get_api_keys(environment)


def get_email_credentials(environment: str = None) -> Dict[str, str]:
    """Get email credentials for the current environment"""
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'prod')
    
    sm = get_secrets_manager()
    return sm.get_email_credentials(environment)


if __name__ == "__main__":
    # Test the secrets manager
    import sys
    
    env = sys.argv[1] if len(sys.argv) > 1 else 'stg'
    
    print(f"Testing Secrets Manager for environment: {env}")
    print("=" * 50)
    
    try:
        api_keys = get_api_keys(env)
        print("\nAPI Keys Retrieved:")
        for key, value in api_keys.items():
            if value:
                print(f"  {key}: {'*' * 20} (hidden)")
            else:
                print(f"  {key}: NOT FOUND")
        
        email_creds = get_email_credentials(env)
        print("\nEmail Credentials:")
        if email_creds:
            print(f"  Email: {email_creds.get('email', 'NOT FOUND')}")
            print(f"  Password: {'*' * 20} (hidden)")
            print(f"  SMTP Host: {email_creds.get('smtp_host', 'NOT FOUND')}")
        else:
            print("  NOT FOUND")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
