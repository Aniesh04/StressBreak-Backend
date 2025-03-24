import os
import json
from typing import Dict, Any
from pathlib import Path

class Config:
    """
    Configuration class that loads settings from a JSON file.
    Default settings can be overridden with environment variables.
    """
    
    # Default configuration
    _default_config = {
        "database": {
            "driver": "postgresql",
            "host": "ep-wispy-voice-a5r5q0qj-pooler.us-east-2.aws.neon.tech",
            "port": 5432,
            "username": "neondb_owner",
            "password": "npg_sM63LwzWUuZY",
            "database": "stressbreak",
            "sslmode": "require"
        }
    }
    
    _config: Dict[str, Any] = {}
    
    @classmethod
    def load_config(cls, config_path: str = "config.json") -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file.
        """
        # Start with default configuration
        cls._config = cls._default_config.copy()
        
        # Try to load from config file
        config_file = Path(config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                
                # Deep merge the configurations
                cls._deep_merge(cls._config, file_config)
            except Exception as e:
                print(f"Error loading config file: {e}")
        
        # Override with environment variables
        cls._load_from_env()
    
    @classmethod
    def _deep_merge(cls, target: Dict, source: Dict) -> None:
        """Recursively merge nested dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                cls._deep_merge(target[key], value)
            else:
                target[key] = value
    
    @classmethod
    def _load_from_env(cls) -> None:
        """Override configuration with environment variables."""
        # Database settings from the DATABASE_URL environment variable
        if os.environ.get('DATABASE_URL'):
            # Parse the DATABASE_URL if it's provided
            # Format: postgresql://username:password@host:port/database?sslmode=require
            try:
                db_url = os.environ.get('DATABASE_URL')
                print(f"Using database URL from environment: {db_url}")
            except Exception as e:
                print(f"Error parsing DATABASE_URL: {e}")
        
        # Individual database environment variables
        if os.environ.get('PGHOST'):
            cls._config['database']['host'] = os.environ.get('PGHOST')
        if os.environ.get('PGPORT'):
            cls._config['database']['port'] = int(os.environ.get('PGPORT', '5432'))
        if os.environ.get('PGUSER'):
            cls._config['database']['username'] = os.environ.get('PGUSER')
        if os.environ.get('PGPASSWORD'):
            cls._config['database']['password'] = os.environ.get('PGPASSWORD')
        if os.environ.get('PGDATABASE'):
            cls._config['database']['database'] = os.environ.get('PGDATABASE')
        
        # Application settings
        if os.environ.get('APP_DEBUG'):
            cls._config['application']['debug'] = os.environ.get('APP_DEBUG').lower() == 'true'
        if os.environ.get('SECRET_KEY'):
            cls._config['application']['secret_key'] = os.environ.get('SECRET_KEY')
    
    @classmethod
    def get(cls, key: str = None):
        """
        Get configuration value.
        
        Args:
            key: Dot-separated path to configuration value, e.g. 'database.host'.
                 If None, returns all configuration.
        
        Returns:
            Configuration value or entire configuration if key is None.
        """
        if not cls._config:
            cls.load_config()
        
        if key is None:
            return cls._config
        
        parts = key.split('.')
        value = cls._config
        for part in parts:
            if part not in value:
                return None
            value = value[part]
        
        return value

# Load configuration on module import
Config.load_config()

# Database connection string
def get_database_url() -> str:
    """Generate SQLAlchemy database URL from configuration."""
    db_config = Config.get('database')
    
    # Include SSL mode parameter if available
    ssl_param = ""
    if db_config.get('sslmode'):
        ssl_param = f"?sslmode={db_config['sslmode']}"
    
    return f"{db_config['driver']}://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}{ssl_param}"
