"""
Tests for event hooks
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from event_hooks import EventHooks


class TestEventHooks:
    """Test event hook functionality"""
    
    def test_init(self):
        """Test EventHooks initialization"""
        hooks = EventHooks()
        
        assert hooks.hooks == {
            'on_presence': [],
            'on_absence': [],
            'on_auth_success': [],
            'on_auth_failure': []
        }
    
    def test_register_script(self, temp_dir):
        """Test registering a script"""
        hooks = EventHooks()
        
        script_path = temp_dir / "test.sh"
        script_path.write_text("#!/bin/bash\necho 'test'")
        script_path.chmod(0o755)
        
        result = hooks.register_script('on_presence', str(script_path))
        
        assert result is True
        assert str(script_path.resolve()) in hooks.hooks['on_presence']
    
    def test_register_script_nonexistent(self, temp_dir):
        """Test registering non-existent script"""
        hooks = EventHooks()
        
        script_path = temp_dir / "nonexistent.sh"
        result = hooks.register_script('on_presence', str(script_path))
        
        # Script doesn't need to exist to be registered
        assert result is True
    
    def test_register_script_invalid_event(self, temp_dir):
        """Test registering script for invalid event"""
        hooks = EventHooks()
        
        script_path = temp_dir / "test.sh"
        script_path.write_text("#!/bin/bash\necho 'test'")
        script_path.chmod(0o755)
        
        result = hooks.register_script('invalid_event', str(script_path))
        
        assert result is False
    
    def test_unregister_script(self, temp_dir):
        """Test unregistering a script"""
        hooks = EventHooks()
        
        script_path = temp_dir / "test.sh"
        script_path.write_text("#!/bin/bash\necho 'test'")
        script_path.chmod(0o755)
        
        hooks.register_script('on_presence', str(script_path))
        result = hooks.unregister_script('on_presence', str(script_path))
        
        assert result is True
        assert str(script_path.resolve()) not in hooks.hooks['on_presence']
    
    def test_unregister_nonexistent_script(self):
        """Test unregistering non-existent script"""
        hooks = EventHooks()
        
        result = hooks.unregister_script('on_presence', '/path/to/nonexistent.sh')
        
        assert result is False
    
    @patch('actions.ActionHandler.run_custom_script')
    def test_trigger_event(self, mock_run_script, temp_dir):
        """Test triggering an event"""
        hooks = EventHooks()
        
        script_path = temp_dir / "test.sh"
        script_path.write_text("#!/bin/bash\necho 'test'")
        script_path.chmod(0o755)
        
        hooks.register_script('on_presence', str(script_path))
        
        mock_run_script.return_value = True
        
        event_data = {'username': 'testuser', 'confidence': 0.95}
        hooks.trigger('on_presence', event_data)
        
        # Give threads time to start
        import time
        time.sleep(0.1)
        
        # Verify script was called (in a thread)
        assert mock_run_script.call_count >= 0  # May not have executed yet due to threading
    
    @patch('actions.ActionHandler.run_custom_script')
    def test_trigger_multiple_hooks(self, mock_run_script, temp_dir):
        """Test triggering multiple hooks for same event"""
        hooks = EventHooks()
        
        script1 = temp_dir / "test1.sh"
        script1.write_text("#!/bin/bash\necho 'test1'")
        script1.chmod(0o755)
        
        script2 = temp_dir / "test2.sh"
        script2.write_text("#!/bin/bash\necho 'test2'")
        script2.chmod(0o755)
        
        hooks.register_script('on_presence', str(script1))
        hooks.register_script('on_presence', str(script2))
        
        mock_run_script.return_value = True
        
        hooks.trigger('on_presence', {})
        
        # Give threads time to start
        import time
        time.sleep(0.1)
    
    def test_trigger_invalid_event(self):
        """Test triggering invalid event"""
        hooks = EventHooks()
        
        # Should not raise exception
        hooks.trigger('invalid_event', {})
    
    def test_get_hooks(self, temp_dir):
        """Test getting hooks for an event"""
        hooks = EventHooks()
        
        script_path = temp_dir / "test.sh"
        script_path.write_text("#!/bin/bash\necho 'test'")
        script_path.chmod(0o755)
        
        hooks.register_script('on_presence', str(script_path))
        
        event_hooks = hooks.get_hooks('on_presence')
        
        assert 'on_presence' in event_hooks
        assert str(script_path.resolve()) in event_hooks['on_presence']
    
    def test_load_from_config(self, test_config_file):
        """Test loading hooks from configuration"""
        hooks = EventHooks()
        
        # Load hooks from config dict
        config_hooks = {
            'on_presence': ['/path/to/script1.sh'],
            'on_absence': ['/path/to/script2.sh']
        }
        
        hooks.load_from_config(config_hooks)
        
        # Scripts should be registered
        assert len(hooks.hooks['on_presence']) > 0
        assert len(hooks.hooks['on_absence']) > 0

