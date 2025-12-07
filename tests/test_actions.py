"""
Tests for action handlers
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess

from actions import ActionHandler


class TestActionHandler:
    """Test action handler functionality"""
    
    @patch('subprocess.run')
    def test_lock_screen_loginctl(self, mock_run):
        """Test screen locking with loginctl"""
        mock_run.return_value = Mock(returncode=0)
        
        result = ActionHandler.lock_screen()
        
        assert result is True
        mock_run.assert_called_once()
        assert 'loginctl' in mock_run.call_args[0][0]
    
    @patch('subprocess.run')
    def test_lock_screen_fallback(self, mock_run):
        """Test screen locking fallback methods"""
        # First call fails (loginctl), second succeeds (gnome-screensaver)
        mock_run.side_effect = [
            Mock(returncode=1),  # loginctl fails
            Mock(returncode=0),  # gnome-screensaver succeeds
        ]
        
        result = ActionHandler.lock_screen()
        
        assert result is True
        assert mock_run.call_count == 2
    
    @patch('subprocess.run')
    def test_lock_screen_all_fail(self, mock_run):
        """Test screen locking when all methods fail"""
        mock_run.return_value = Mock(returncode=1)
        
        result = ActionHandler.lock_screen()
        
        assert result is False
    
    @patch('subprocess.run')
    def test_suspend(self, mock_run):
        """Test system suspend"""
        mock_run.return_value = Mock(returncode=0)
        
        result = ActionHandler.suspend()
        
        assert result is True
        mock_run.assert_called_once()
        assert 'systemctl' in mock_run.call_args[0][0]
        assert 'suspend' in mock_run.call_args[0][0]
    
    @patch('subprocess.run')
    def test_suspend_failure(self, mock_run):
        """Test system suspend failure"""
        mock_run.return_value = Mock(returncode=1, stderr=b'Error')
        
        result = ActionHandler.suspend()
        
        assert result is False
    
    @patch('subprocess.run')
    def test_hibernate(self, mock_run):
        """Test system hibernate"""
        mock_run.return_value = Mock(returncode=0)
        
        result = ActionHandler.hibernate()
        
        assert result is True
        mock_run.assert_called_once()
        assert 'systemctl' in mock_run.call_args[0][0]
        assert 'hibernate' in mock_run.call_args[0][0]
    
    @patch('subprocess.run')
    def test_send_notification(self, mock_run):
        """Test sending desktop notification"""
        mock_run.return_value = Mock(returncode=0)
        
        result = ActionHandler.send_notification('Test Title', 'Test Message')
        
        assert result is True
        mock_run.assert_called_once()
        assert 'notify-send' in mock_run.call_args[0][0]
    
    @patch('subprocess.run')
    def test_send_notification_with_urgency(self, mock_run):
        """Test sending notification with urgency level"""
        mock_run.return_value = Mock(returncode=0)
        
        result = ActionHandler.send_notification(
            'Critical Alert', 
            'Important message', 
            urgency='critical'
        )
        
        assert result is True
        call_args = mock_run.call_args[0][0]
        assert 'notify-send' in call_args
        assert 'critical' in call_args
    
    def test_run_custom_script_nonexistent(self, temp_dir):
        """Test running non-existent script"""
        script_path = temp_dir / "nonexistent.sh"
        
        result = ActionHandler.run_custom_script(str(script_path))
        
        assert result is False
    
    @patch('subprocess.run')
    def test_run_custom_script_success(self, mock_run, temp_dir):
        """Test running custom script successfully"""
        # Create a test script
        script_path = temp_dir / "test_script.sh"
        script_path.write_text("#!/bin/bash\necho 'test'")
        script_path.chmod(0o755)
        
        mock_run.return_value = Mock(returncode=0, stdout=b'test')
        
        result = ActionHandler.run_custom_script(str(script_path))
        
        assert result is True
    
    @patch('subprocess.run')
    def test_run_custom_script_with_event_data(self, mock_run, temp_dir):
        """Test running custom script with event data"""
        script_path = temp_dir / "test_script.sh"
        script_path.write_text("#!/bin/bash\necho $FACE_AUTH_USERNAME")
        script_path.chmod(0o755)
        
        mock_run.return_value = Mock(returncode=0, stdout=b'testuser')
        
        event_data = {'username': 'testuser', 'confidence': 0.95}
        result = ActionHandler.run_custom_script(str(script_path), event_data)
        
        assert result is True
        # Check environment was passed
        env = mock_run.call_args[1]['env']
        assert 'FACE_AUTH_USERNAME' in env
        assert env['FACE_AUTH_USERNAME'] == 'testuser'
    
    def test_execute_action_lock_screen(self):
        """Test executing lock_screen action"""
        with patch.object(ActionHandler, 'lock_screen', return_value=True) as mock_lock:
            result = ActionHandler.execute_action('lock_screen')
            
            assert result is True
            mock_lock.assert_called_once()
    
    def test_execute_action_suspend(self):
        """Test executing suspend action"""
        with patch.object(ActionHandler, 'suspend', return_value=True) as mock_suspend:
            result = ActionHandler.execute_action('suspend')
            
            assert result is True
            mock_suspend.assert_called_once()
    
    def test_execute_action_log(self):
        """Test executing log action"""
        result = ActionHandler.execute_action('log', {'event': 'test'})
        
        assert result is True
    
    def test_execute_action_custom_script(self, temp_dir):
        """Test executing custom script action"""
        script_path = temp_dir / "test.sh"
        script_path.write_text("#!/bin/bash\necho 'test'")
        script_path.chmod(0o755)
        
        with patch.object(ActionHandler, 'run_custom_script', return_value=True) as mock_script:
            result = ActionHandler.execute_action(f'custom_script:{script_path}')
            
            assert result is True
            mock_script.assert_called_once()
    
    def test_execute_action_notify(self):
        """Test executing notify action"""
        with patch.object(ActionHandler, 'send_notification', return_value=True) as mock_notify:
            result = ActionHandler.execute_action('notify:Test message', {'event': 'test'})
            
            assert result is True
            mock_notify.assert_called_once()
    
    def test_execute_action_unknown(self):
        """Test executing unknown action"""
        result = ActionHandler.execute_action('unknown_action')
        
        assert result is False
    
    def test_execute_actions_multiple(self):
        """Test executing multiple actions"""
        with patch.object(ActionHandler, 'execute_action', return_value=True) as mock_execute:
            actions = ['log', 'notify:Test', 'lock_screen']
            ActionHandler.execute_actions(actions, {'event': 'test'})
            
            assert mock_execute.call_count == 3
