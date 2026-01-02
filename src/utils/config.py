"""
Configuration module for Google Drive SFTP Server
"""

import os
from dotenv import load_dotenv


class Config:
    """Application configuration"""
    
    def __init__(self, env_file='.env'):
        """Initialize configuration from environment file"""
        load_dotenv(env_file)
        
        # SFTP Server Settings (fallback to FTP_* for backward compatibility)
        self.sftp_host = os.getenv('SFTP_HOST') or os.getenv('FTP_HOST', '0.0.0.0')
        self.sftp_port = int(os.getenv('SFTP_PORT') or os.getenv('FTP_PORT', '2121'))
        self.sftp_username = os.getenv('SFTP_USERNAME') or os.getenv('FTP_USERNAME', 'admin')
        self.sftp_password = os.getenv('SFTP_PASSWORD') or os.getenv('FTP_PASSWORD', 'admin123')
        self.sftp_root_path = (os.getenv('SFTP_ROOT_PATH') or os.getenv('FTP_ROOT_PATH', '/')).strip()
        self.sftp_host_key = os.getenv('SFTP_HOST_KEY', 'config/sftp_host_key')
        
        # Google Drive Settings
        self.credentials_file = os.getenv('CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('TOKEN_FILE', 'token.json')
        
        # Logging Settings
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/sftp_server.log')
        
        # Performance Settings
        self.cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        self.cache_timeout = int(os.getenv('CACHE_TIMEOUT', '60'))

    def validate(self):
        """Validate configuration"""
        errors = []
        
        if not os.path.exists(self.credentials_file):
            errors.append(f"Credentials file '{self.credentials_file}' not found")
        
        if not (1 <= self.sftp_port <= 65535):
            errors.append(f"Invalid SFTP port: {self.sftp_port}")
        
        if not self.sftp_username or not self.sftp_password:
            errors.append("SFTP username and password must be set")
        
        return errors
    
    def display(self):
        """Display current configuration"""
        print(f"SFTP Configuration:")
        print(f"  Host: {self.sftp_host}")
        print(f"  Port: {self.sftp_port}")
        print(f"  Username: {self.sftp_username}")
        print(f"  Root Path: {self.sftp_root_path}")
        print(f"  Host Key: {self.sftp_host_key}")
        print(f"\nGoogle Drive Configuration:")
        print(f"  Credentials File: {self.credentials_file}")
        print(f"  Token File: {self.token_file}")
        print(f"\nLogging Configuration:")
        print(f"  Log Level: {self.log_level}")
        print(f"  Log File: {self.log_file}")
        print(f"\nPerformance Configuration:")
        print(f"  Cache Enabled: {self.cache_enabled}")
        print(f"  Cache Timeout: {self.cache_timeout}s")
