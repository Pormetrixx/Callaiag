#!/usr/bin/env python3
"""
Configuration management for the Callaiag agent
"""

import os
import sys
import yaml
from pathlib import Path
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the Callaiag agent"""
    
    DEFAULT_CONFIG_PATHS = [
        './config.yaml',
        '~/.config/callaiag/config.yaml',
        '/etc/callaiag/config.yaml'
    ]
    
    DEFAULT_CONFIG = {
        'general': {
            'debug': False,
            'log_level': 'INFO',
            'language': 'de-DE',  # German language default
        },
        'database': {
            'type': 'sqlite',  # sqlite, mysql, postgresql
            'path': './data/callaiag.db',  # For SQLite
            'host': 'localhost',  # For MySQL/PostgreSQL
            'port': 3306,  # MySQL default port
            'name': 'callaiag',
            'user': 'callaiag',
            'password': 'change_me',  # Should be overridden in actual config
        },
        'asterisk': {
            'enabled': True,
            'host': 'localhost',
            'port': 5038,
            'username': 'callaiag',
            'password': 'change_me',  # Should be overridden in actual config
            'context': 'outbound',
            'extension': 's',
            'priority': 1,
            'channel_type': 'SIP',
            'caller_id': 'Callaiag <1000>',
            'trunk': 'trunk',
        },
        'speech': {
            'stt': {
                'engine': 'whisper',  # whisper
                'whisper_model': 'medium',  # tiny, base, small, medium, large
                'language': 'de',  # de, en, etc.
                'device': 'cpu',  # cpu, cuda
            },
            'tts': {
                'engine': 'mimic3',  # mimic3, coqui
                'voice': 'de_DE/thorsten-emotional',
                'rate': 1.0,
                'pitch': 0.0,
                'volume': 1.0,
            },
            'audio': {
                'input_device': None,  # None for default
                'output_device': None,  # None for default
                'sample_rate': 16000,
                'channels': 1,
                'format': 'wav',
                'temp_dir': './temp',
            },
        },
        'conversation': {
            'default_script': 'default',
            'timeout': 10.0,  # seconds
            'max_duration': 300,  # seconds (5 minutes)
            'emotion_threshold': 0.7,  # confidence threshold for emotion detection
            'scripts_dir': './scripts',
            'faqs_dir': './faqs',
        },
        'dashboard': {
            'enabled': True,
            'port': 8080,
            'host': '0.0.0.0',  # Listen on all interfaces
            'admin_user': 'admin',
            'admin_password': 'admin123',  # Should be overridden in actual config
            'session_timeout': 3600,  # seconds (1 hour)
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Optional path to a configuration file
        """
        self.config_data = {}
        
        # Find config file
        self.config_path = self._find_config(config_path)
        
        # Load configuration
        self._load_config()
        
        # Override with environment variables
        self._load_env_vars()
        
        logger.debug(f"Configuration loaded from {self.config_path}")
        
    def _find_config(self, config_path: Optional[str]) -> str:
        """
        Find the configuration file
        
        Args:
            config_path: Optional path to a configuration file
            
        Returns:
            The path to the configuration file
        """
        if config_path:
            if os.path.isfile(config_path):
                return config_path
            else:
                logger.warning(f"Config file not found at {config_path}, using defaults")
                return None
        
        # Try default locations
        for path in self.DEFAULT_CONFIG_PATHS:
            expanded_path = os.path.expanduser(path)
            if os.path.isfile(expanded_path):
                return expanded_path
                
        logger.warning("No config file found, using defaults")
        return None
    
    def _load_config(self):
        """Load configuration from file"""
        # Start with defaults
        self.config_data = self.DEFAULT_CONFIG.copy()
        
        # Load from file if available
        if self.config_path and os.path.isfile(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                
                if file_config:
                    # Update configuration with file values
                    self._update_config(self.config_data, file_config)
            except Exception as e:
                logger.error(f"Error loading config from {self.config_path}: {e}")
                
    def _update_config(self, base_config: Dict[str, Any], new_config: Dict[str, Any]):
        """
        Update configuration recursively
        
        Args:
            base_config: Base configuration dictionary
            new_config: New configuration dictionary to merge in
        """
        for key, value in new_config.items():
            if key in base_config:
                if isinstance(value, dict) and isinstance(base_config[key], dict):
                    # Recursively update nested dictionaries
                    self._update_config(base_config[key], value)
                else:
                    # Replace value
                    base_config[key] = value
            else:
                # Add new key
                base_config[key] = value
    
    def _load_env_vars(self):
        """Override configuration with environment variables"""
        for key in os.environ:
            if key.startswith('CALLAIAG_'):
                # Convert CALLAIAG_DATABASE_HOST to ['database', 'host']
                path = key[9:].lower().split('_')
                
                # Navigate to the correct section of the config
                config_section = self.config_data
                for section in path[:-1]:
                    if section not in config_section:
                        config_section[section] = {}
                    config_section = config_section[section]
                
                # Set the value
                config_section[path[-1]] = self._convert_env_value(os.environ[key])
    
    def _convert_env_value(self, value: str) -> Any:
        """
        Convert environment variable string to appropriate type
        
        Args:
            value: String value from environment variable
            
        Returns:
            Converted value
        """
        # Try to convert to appropriate type
        if value.lower() in ('true', 'yes', 'y', '1'):
            return True
        elif value.lower() in ('false', 'no', 'n', '0'):
            return False
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
            return float(value)
        else:
            return value
    
    def get(self, *keys, default=None) -> Any:
        """Get a configuration value
        
        Args:
            *keys: Keys to navigate the configuration
            default: Default value if not found
            
        Returns:
            The configuration value
        """
        value = self.config_data
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def create_default_config(self):
        """Create a default configuration file"""
        # Determine target path
        if self.config_path:
            target_path = self.config_path
        else:
            target_path = os.path.expanduser(self.DEFAULT_CONFIG_PATHS[0])
            
        # Create directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
        
        # Write default config
        with open(target_path, 'w') as f:
            yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
        
        self.config_path = target_path
        return target_path
