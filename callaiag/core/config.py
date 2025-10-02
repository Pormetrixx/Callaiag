#!/usr/bin/env python3
"""
Configuration management for the Callaiag agent.

This module provides a centralized configuration system with support for
multiple configuration sources (files, environment variables) and sensible defaults.
"""

import os
import yaml
from pathlib import Path
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the Callaiag agent"""
    
    DEFAULT_CONFIG_PATHS = [
        './config.yaml',
        './config/default_config.yml',
        '~/.config/callaiag/config.yaml',
        '/etc/callaiag/config.yaml'
    ]
    
    DEFAULT_CONFIG = {
        'general': {
            'debug': False,
            'log_level': 'INFO',
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
        },
        'dashboard': {
            'enabled': True,
            'port': 8080,
            'host': '0.0.0.0',
            'admin_user': 'admin',
            'admin_password': 'admin123',
            'session_timeout': 3600,
        },
        'emotion': {
            'enabled': True,
            'model_path': './models/emotion',
            'confidence_threshold': 0.6,
        },
        'training': {
            'enabled': True,
            'min_calls_for_training': 100,
            'auto_retrain': False,
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = self._find_config(config_path)
        self.config_data = {}
        self._load_config()
        self._load_env_vars()
    
    def _find_config(self, config_path: Optional[str]) -> Optional[str]:
        """Find configuration file from various locations."""
        if config_path and os.path.isfile(config_path):
            return config_path
        
        for path in self.DEFAULT_CONFIG_PATHS:
            expanded_path = os.path.expanduser(path)
            if os.path.isfile(expanded_path):
                logger.info(f"Found configuration file at {expanded_path}")
                return expanded_path
        
        logger.warning("No configuration file found, using defaults")
        return None
    
    def _load_config(self):
        """Load configuration from file"""
        self.config_data = self.DEFAULT_CONFIG.copy()
        
        if self.config_path and os.path.isfile(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                
                if file_config:
                    self._update_config(self.config_data, file_config)
                    logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading config from {self.config_path}: {e}")
    
    def _update_config(self, base_config: Dict[str, Any], new_config: Dict[str, Any]):
        """Update configuration recursively"""
        for key, value in new_config.items():
            if key in base_config:
                if isinstance(value, dict) and isinstance(base_config[key], dict):
                    self._update_config(base_config[key], value)
                else:
                    base_config[key] = value
            else:
                base_config[key] = value
    
    def _load_env_vars(self):
        """Override configuration with environment variables"""
        env_prefix = "CALLAIAG_"
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                self.config_data[config_key] = self._convert_env_value(value)
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        elif value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value
    
    def get(self, *keys, default=None) -> Any:
        """
        Get configuration value by key path.
        
        Args:
            *keys: Configuration key path (e.g., 'database', 'host')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        value = self.config_data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def create_default_config(self, output_path: str = './config/default_config.yml'):
        """
        Create a default configuration file.
        
        Args:
            output_path: Path where to save the configuration file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Default configuration created at {output_path}")
