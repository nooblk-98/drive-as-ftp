"""
Configuration module for Google Drive FTP Server
"""

import os
from dotenv import load_dotenv


class Config:
    """Application configuration"""
    
    def __init__(self, env_file='.env'):
        """Initialize configuration from environment file"""
        load_dotenv(env_file)
        
        # FTP Server Settings
        self.ftp_host = os.getenv('FTP_HOST', '0.0.0.0')
        self.ftp_port = int(os.getenv('FTP_PORT', '2121'))
        self.ftp_username = os.getenv('FTP_USERNAME', 'admin')
        self.ftp_password = os.getenv('FTP_PASSWORD', 'admin123')
        self.ftp_max_connections = int(os.getenv('FTP_MAX_CONNECTIONS', '256'))
        self.ftp_max_connections_per_ip = int(os.getenv('FTP_MAX_CONNECTIONS_PER_IP', '5'))
        self.ftp_root_path = os.getenv('FTP_ROOT_PATH', '/').strip()
        self.ftp_passive_address = os.getenv('FTP_PASSIVE_ADDRESS', '').strip() or None
        self.ftp_passive_ports = self._parse_passive_ports(
            os.getenv('FTP_PASSIVE_PORTS', '').strip()
        )
        
        # Google Drive Settings
        self.credentials_file = os.getenv('CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('TOKEN_FILE', 'token.json')
        
        # Logging Settings
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/ftp_server.log')
        
        # Performance Settings
        self.cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        self.cache_timeout = int(os.getenv('CACHE_TIMEOUT', '60'))

    def _parse_passive_ports(self, value):
        """Parse passive port range like '30000-30100'."""
        if not value:
            return None
        parts = value.split('-', 1)
        if len(parts) != 2:
            return None
        try:
            start = int(parts[0])
            end = int(parts[1])
        except ValueError:
            return None
        if start < 1 or end > 65535 or start > end:
            return None
        return range(start, end + 1)
    
    def validate(self):
        """Validate configuration"""
        errors = []
        
        if not os.path.exists(self.credentials_file):
            errors.append(f"Credentials file '{self.credentials_file}' not found")
        
        if not (1 <= self.ftp_port <= 65535):
            errors.append(f"Invalid FTP port: {self.ftp_port}")
        
        if not self.ftp_username or not self.ftp_password:
            errors.append("FTP username and password must be set")
        
        return errors
    
    def display(self):
        """Display current configuration"""
        print(f"FTP Configuration:")
        print(f"  Host: {self.ftp_host}")
        print(f"  Port: {self.ftp_port}")
        print(f"  Username: {self.ftp_username}")
        print(f"  Root Path: {self.ftp_root_path}")
        print(f"  Max Connections: {self.ftp_max_connections}")
        print(f"  Max Connections Per IP: {self.ftp_max_connections_per_ip}")
        if self.ftp_passive_address:
            print(f"  Passive Address: {self.ftp_passive_address}")
        if self.ftp_passive_ports:
            print(f"  Passive Ports: {self.ftp_passive_ports.start}-{self.ftp_passive_ports.stop - 1}")
        print(f"\nGoogle Drive Configuration:")
        print(f"  Credentials File: {self.credentials_file}")
        print(f"  Token File: {self.token_file}")
        print(f"\nLogging Configuration:")
        print(f"  Log Level: {self.log_level}")
        print(f"  Log File: {self.log_file}")
        print(f"\nPerformance Configuration:")
        print(f"  Cache Enabled: {self.cache_enabled}")
        print(f"  Cache Timeout: {self.cache_timeout}s")
