"""
Configuration management for Callaiag.

This module handles loading, validating, and managing configuration from various sources.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class Config:
    """
    Configuration manager for the Callaiag agent.
    
    Handles loading configuration from YAML files and environment variables,
    with validation and default values.
    
    Attributes:
        config_path: Path to the configuration file
        config_data: Dictionary containing all configuration values
        
    Example:
        >>> config = Config("config.yaml")
        >>> db_host = config.get("database", "host", default="localhost")
    """
    
    DEFAULT_CONFIG_PATHS: List[str] = [
        './config.yaml',
        './config/default_config.yml',
        '~/.config/callaiag/config.yaml',
        '/etc/callaiag/config.yaml'
    ]
    
    DEFAULT_CONFIG: Dict[str, Any] = {
        'general': {
            'debug': False,
            'log_level': 'INFO',
            'log_file': 'callaiag.log',
            'log_dir': './logs',
            'language': 'de-DE',
        },
        'database': {
            'type': 'sqlite',
            'path': './data/callaiag.db',
            'host': 'localhost',
            'port': 3306,
            'name': 'callaiag',
            'user': 'callaiag',
            'password': 'change_me',
        },
        'asterisk': {
            'enabled': True,
            'host': 'localhost',
            'port': 5038,
            'username': 'callaiag',
            'password': 'change_me',
            'context': 'outbound',
            'extension': 's',
            'priority': 1,
            'channel_type': 'SIP',
            'caller_id': 'Callaiag <1000>',
            'trunk': 'trunk',
        },
        'speech': {
            'stt': {
                'engine': 'whisper',
                'whisper_model': 'medium',
                'language': 'de',
                'device': 'cpu',
            },
            'tts': {
                'engine': 'mimic3',
                'voice': 'de_DE/thorsten-emotional',
                'rate': 1.0,
                'pitch': 0.0,
                'volume': 1.0,
            },
            'audio': {
                'input_device': None,
                'output_device': None,
                'sample_rate': 16000,
                'channels': 1,
                'format': 'wav',
                'temp_dir': './temp',
            },
        },
        'conversation': {
            'default_script': 'default',
            'timeout': 10.0,
            'max_duration': 300,
            'emotion_threshold': 0.7,
            'scripts_dir': './scripts',
            'faqs_dir': './faqs',
            'response_delay_min': 0.5,
            'response_delay_max': 2.0,
        },
        'human_simulation': {
            'natural_delays': True,
            'use_fillers': True,
            'filler_frequency': 0.15,
            'hesitation_frequency': 0.10,
            'typing_speed_wpm': 40,
        },
        'dashboard': {
            'enabled': True,
            'port': 8080,
            'host': '0.0.0.0',
            'admin_user': 'admin',
            'admin_password': 'admin123',
        },
    }
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Optional path to a configuration file
            
        Raises:
            ConfigValidationError: If configuration validation fails
        """
        self.config_data: Dict[str, Any] = {}
        self.config_path: Optional[str] = self._find_config(config_path)
        
        # Load configuration
        self._load_config()
        
        # Override with environment variables
        self._load_env_vars()
        
        # Validate configuration
        self.validate()
        
        logger.debug(f"Configuration loaded from {self.config_path or 'defaults'}")
    
    def _find_config(self, config_path: Optional[str]) -> Optional[str]:
        """
        Find the configuration file.
        
        Args:
            config_path: Optional path to a configuration file
            
        Returns:
            The path to the configuration file or None if not found
        """
        if config_path:
            expanded = os.path.expanduser(config_path)
            if os.path.isfile(expanded):
                return expanded
            else:
                logger.warning(f"Config file not found at {config_path}, using defaults")
                return None
        
        # Try default locations
        for path in self.DEFAULT_CONFIG_PATHS:
            expanded_path = os.path.expanduser(path)
            if os.path.isfile(expanded_path):
                return expanded_path
                
        logger.info("No config file found, using defaults")
        return None
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        # Start with defaults
        self.config_data = self._deep_copy(self.DEFAULT_CONFIG)
        
        # Load from file if available
        if self.config_path and os.path.isfile(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                
                if file_config:
                    self._update_config(self.config_data, file_config)
                    logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading config from {self.config_path}: {e}")
                raise ConfigValidationError(f"Failed to load config: {e}")
    
    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        # Map environment variables to config keys
        env_mappings = {
            'CALLAIAG_DEBUG': ('general', 'debug'),
            'CALLAIAG_LOG_LEVEL': ('general', 'log_level'),
            'CALLAIAG_DB_TYPE': ('database', 'type'),
            'CALLAIAG_DB_HOST': ('database', 'host'),
            'CALLAIAG_DB_PORT': ('database', 'port'),
            'CALLAIAG_DB_NAME': ('database', 'name'),
            'CALLAIAG_DB_USER': ('database', 'user'),
            'CALLAIAG_DB_PASSWORD': ('database', 'password'),
        }
        
        for env_var, config_keys in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                self._set_nested_value(self.config_data, config_keys, value)
    
    def _update_config(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """
        Recursively update base configuration with values from update.
        
        Args:
            base: Base configuration dictionary
            update: Update configuration dictionary
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._update_config(base[key], value)
            else:
                base[key] = value
    
    def _deep_copy(self, obj: Any) -> Any:
        """Create a deep copy of the object."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
    
    def _set_nested_value(self, data: Dict[str, Any], keys: tuple, value: Any) -> None:
        """Set a nested value in the configuration."""
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            *keys: Keys to navigate the configuration
            default: Default value if not found
            
        Returns:
            The configuration value or default
            
        Example:
            >>> config.get("database", "host", default="localhost")
            'localhost'
        """
        value = self.config_data
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, *keys: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            *keys: Keys to navigate the configuration
            value: Value to set
            
        Example:
            >>> config.set("database", "host", value="192.168.1.100")
        """
        self._set_nested_value(self.config_data, keys, value)
    
    def validate(self) -> None:
        """
        Validate the configuration.
        
        Raises:
            ConfigValidationError: If validation fails
        """
        # Validate required fields
        required_fields = [
            ('general', 'log_level'),
            ('speech', 'stt', 'engine'),
            ('speech', 'tts', 'engine'),
        ]
        
        for keys in required_fields:
            value = self.get(*keys)
            if value is None:
                raise ConfigValidationError(f"Required config field missing: {'.'.join(keys)}")
        
        # Validate log level
        log_level = self.get('general', 'log_level', default='INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level.upper() not in valid_levels:
            raise ConfigValidationError(f"Invalid log level: {log_level}")
        
        logger.debug("Configuration validation successful")
    
    def create_default_config(self, target_path: Optional[str] = None) -> str:
        """
        Create a default configuration file.
        
        Args:
            target_path: Optional target path for the config file
            
        Returns:
            Path to the created configuration file
        """
        if target_path:
            config_path = os.path.expanduser(target_path)
        elif self.config_path:
            config_path = self.config_path
        else:
            config_path = os.path.expanduser(self.DEFAULT_CONFIG_PATHS[0])
        
        # Create directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        # Write default config
        with open(config_path, 'w') as f:
            yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
        
        self.config_path = config_path
        logger.info(f"Default configuration created at {config_path}")
        return config_path
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get the entire configuration as a dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._deep_copy(self.config_data)
