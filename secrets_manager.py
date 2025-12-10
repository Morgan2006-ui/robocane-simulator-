import boto3
import os
import json
from botocore.exceptions import ClientError

class SecretsManager:
    def __init__(self):
        self.client = boto3.client('secretsmanager', region_name='ap-northeast-1')
        # Get environment from environment variable (demo, stg, or prod)
        self.environment = os.environ.get('ENVIRONMENT', 'demo')
        
    def get_secret(self, secret_name):
        """Retrieve a secret from AWS Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            # Check if secret is string or JSON
            if 'SecretString' in response:
                secret = response['SecretString']
                # Try to parse as JSON, if fails return as string
                try:
                    return json.loads(secret)
                except json.JSONDecodeError:
                    return secret
            else:
                # Binary secret
                return response['SecretBinary']
        except ClientError as e:
            print(f"Error retrieving secret {secret_name}: {e}")
            raise
    
    def get_google_maps_api_key(self):
        """Get Google Maps API key for current environment"""
        secret_name = f"api/google-maps/robocane-{self.environment}"
        return self.get_secret(secret_name)
    
    def get_stripe_publishable_key(self):
        """Get Stripe publishable key for current environment"""
        secret_name = f"api/stripe-publishable/robocane-{self.environment}"
        return self.get_secret(secret_name)
    
    def get_stripe_secret_key(self):
        """Get Stripe secret key for current environment"""
        secret_name = f"api/stripe-secret/robocane-{self.environment}"
        return self.get_secret(secret_name)
    
    def get_openai_api_key(self):
        """Get OpenAI API key for current environment"""
        secret_name = f"api/openai/robocane-{self.environment}"
        return self.get_secret(secret_name)
    
    def get_anthropic_api_key(self):
        """Get Anthropic API key for current environment"""
        secret_name = f"api/anthropic/robocane-{self.environment}"
        return self.get_secret(secret_name)
    
    def get_serp_api_key(self):
        """Get SerpAPI key for current environment"""
        secret_name = f"api/serp-api/robocane-{self.environment}"
        return self.get_secret(secret_name)
    
    def get_n8n_api_key(self):
        """Get n8n API key for current environment"""
        secret_name = f"api/n8n.cloud/robocane-{self.environment}"
        return self.get_secret(secret_name)

# Create a global instance
secrets_manager = SecretsManager()
            
        
           
            
       


       
    
  
