"""
Unit tests for core.config module.

Tests configuration loading, validation, and management.
"""

import pytest
import tempfile
import os
from pathlib import Path

from callaiag.core.config import Config, ConfigValidationError


class TestConfig:
    """Test suite for Config class."""
    
    def test_config_initialization(self):
        """Test basic configuration initialization."""
        config = Config()
        assert config is not None
        assert config.config_data is not None
    
    def test_config_get_default(self):
        """Test getting configuration with defaults."""
        config = Config()
        log_level = config.get('general', 'log_level', default='INFO')
        assert log_level == 'INFO'
    
    def test_config_get_nested(self):
        """Test getting nested configuration values."""
        config = Config()
        stt_engine = config.get('speech', 'stt', 'engine')
        assert stt_engine == 'whisper'
    
    def test_config_set_value(self):
        """Test setting configuration values."""
        config = Config()
        config.set('test', 'key', value='test_value')
        assert config.get('test', 'key') == 'test_value'
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        # Should not raise any exception
        config.validate()
    
    def test_config_invalid_log_level(self):
        """Test validation with invalid log level."""
        config = Config()
        config.set('general', 'log_level', value='INVALID')
        
        with pytest.raises(ConfigValidationError):
            config.validate()
    
    def test_create_default_config(self):
        """Test creating default configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, 'test_config.yaml')
            config = Config()
            result_path = config.create_default_config(config_path)
            
            assert os.path.exists(result_path)
            assert result_path == config_path
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'general' in config_dict
        assert 'speech' in config_dict
