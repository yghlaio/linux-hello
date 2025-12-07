"""
Tests for configuration module
"""

import pytest
from pathlib import Path
import yaml

from config import Config


class TestConfig:
    """Test configuration management"""
    
    def test_load_config(self, test_config_file, test_data_dir):
        """Test loading configuration from file"""
        config = Config(test_config_file)
        
        assert config.get('camera.device_id') == 0
        assert config.get('recognition.tolerance') == 0.6
        assert config.get('recognition.model') == 'hog'
    
    def test_get_nested_value(self, test_config_file):
        """Test getting nested configuration values"""
        config = Config(test_config_file)
        
        assert config.get('camera.device_id') == 0
        assert config.get('monitoring.check_interval') == 2.0
        assert config.get('enrollment.num_samples') == 3
    
    def test_get_with_default(self, test_config_file):
        """Test getting value with default"""
        config = Config(test_config_file)
        
        # Existing value
        assert config.get('camera.device_id', 999) == 0
        
        # Non-existing value
        assert config.get('nonexistent.key', 'default') == 'default'
    
    def test_set_value(self, test_config_file):
        """Test setting configuration values"""
        config = Config(test_config_file)
        
        config.set('camera.device_id', 1)
        assert config.get('camera.device_id') == 1
        
        config.set('new.nested.value', 'test')
        assert config.get('new.nested.value') == 'test'
    
    def test_save_config(self, test_config_file):
        """Test saving configuration"""
        config = Config(test_config_file)
        
        config.set('camera.device_id', 2)
        config.save()
        
        # Load again and verify
        config2 = Config(test_config_file)
        assert config2.get('camera.device_id') == 2
    
    def test_ensure_directories(self, test_config_file, test_data_dir):
        """Test directory creation"""
        config = Config(test_config_file)
        
        # Update paths to use test directory
        config.set('database.path', str(test_data_dir / 'face_auth.db'))
        config.set('logging.file', str(test_data_dir / 'face_auth.log'))
        
        config.ensure_directories()
        
        # Verify directories exist
        assert test_data_dir.exists()
    
    def test_get_camera_settings(self, test_config_file):
        """Test getting camera settings"""
        config = Config(test_config_file)
        
        assert config.get('camera.device_id') == 0
        assert config.get('camera.width') == 640
        assert config.get('camera.height') == 480
    
    def test_get_recognition_settings(self, test_config_file):
        """Test getting recognition settings"""
        config = Config(test_config_file)
        
        assert config.get('recognition.tolerance') == 0.6
        assert config.get('recognition.model') == 'hog'
        assert config.get('recognition.num_jitters') == 1
    
    def test_get_monitoring_settings(self, test_config_file):
        """Test getting monitoring settings"""
        config = Config(test_config_file)
        
        assert config.get('monitoring.enabled') is True
        assert config.get('monitoring.check_interval') == 2.0
        assert config.get('monitoring.absence_timeout') == 10.0
    
    def test_get_actions(self, test_config_file):
        """Test getting action configurations"""
        config = Config(test_config_file)
        
        on_absence = config.get('actions.on_absence', [])
        assert 'log' in on_absence
        
        on_presence = config.get('actions.on_presence', [])
        assert 'log' in on_presence
