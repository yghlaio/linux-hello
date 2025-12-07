"""
Simplified CLI tests without face recognition dependencies
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path


class TestCLIBasics:
    """Test basic CLI functionality"""
    
    def test_cmd_config_get(self, test_config_file):
        """Test getting configuration value"""
        from cli import cmd_config
        
        args = Mock()
        args.edit = False
        args.set = None
        args.get = 'camera.device_id'
        
        with patch('cli.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.config_path = test_config_file
            mock_config.get.return_value = 0
            mock_get_config.return_value = mock_config
            
            result = cmd_config(args)
        
        assert result == 0
        mock_config.get.assert_called_once_with('camera.device_id')
    
    def test_cmd_config_set(self, test_config_file):
        """Test setting configuration value"""
        from cli import cmd_config
        
        args = Mock()
        args.edit = False
        args.set = 'camera.device_id=1'
        args.get = None
        
        with patch('cli.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.config_path = test_config_file
            mock_get_config.return_value = mock_config
            
            result = cmd_config(args)
        
        assert result == 0
        mock_config.set.assert_called_once_with('camera.device_id', 1)
        mock_config.save.assert_called_once()
    
    def test_cmd_list_empty(self, test_config_file, test_data_dir):
        """Test listing users when none enrolled"""
        from cli import cmd_list
        
        args = Mock()
        
        with patch('cli.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get.return_value = str(test_data_dir / 'test.db')
            mock_get_config.return_value = mock_config
            
            result = cmd_list(args)
        
        assert result == 0
    
    def test_cmd_remove_nonexistent(self, test_config_file, test_data_dir):
        """Test removing non-existent user"""
        from cli import cmd_remove
        
        args = Mock()
        args.username = 'nonexistent'
        
        with patch('cli.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get.return_value = str(test_data_dir / 'test.db')
            mock_get_config.return_value = mock_config
            
            result = cmd_remove(args)
        
        assert result == 1
    
    @patch('subprocess.run')
    def test_cmd_stop_monitor_not_running(self, mock_run):
        """Test stopping monitor when not running"""
        from cli import cmd_stop_monitor
        
        mock_run.return_value = Mock(returncode=1)
        
        args = Mock()
        result = cmd_stop_monitor(args)
        
        assert result == 1
