"""
Simplified integration tests for core functionality
Tests basic configuration, database, and action handling without camera/face recognition
"""

import pytest
from pathlib import Path

from config import Config
from models import Database
from actions import ActionHandler


class TestConfigIntegration:
    """Integration tests for configuration"""
    
    def test_config_lifecycle(self, test_config_file, test_data_dir):
        """Test complete config lifecycle"""
        config = Config(test_config_file)
        
        # Read values
        assert config.get('camera.device_id') == 0
        
        # Modify values
        config.set('camera.device_id', 1)
        config.set('recognition.tolerance', 0.7)
        
        # Save
        config.save()
        
        # Reload and verify
        config2 = Config(test_config_file)
        assert config2.get('camera.device_id') == 1
        assert config2.get('recognition.tolerance') == 0.7


class TestDatabaseIntegration:
    """Integration tests for database"""
    
    def test_database_user_workflow(self, test_data_dir, mock_face_encoding):
        """Test complete user workflow"""
        db_path = test_data_dir / 'test.db'
        db = Database(str(db_path))
        
        # Add users (face_encodings expects a list)
        alice_user = db.add_user('alice', [mock_face_encoding])
        bob_user = db.add_user('bob', [mock_face_encoding])
        
        assert alice_user is not None
        assert bob_user is not None
        
        # List users
        users = db.get_all_users()
        assert len(users) == 2
        
        # Update last seen
        db.update_last_seen('alice')
        
        # Verify update
        alice = db.get_user('alice')
        assert alice.last_seen is not None
        
        # Remove user
        assert db.remove_user('alice') is True
        
        # Verify removal
        users = db.get_all_users()
        assert len(users) == 1
        assert users[0].username == 'bob'


class TestActionIntegration:
    """Integration tests for actions"""
    
    def test_action_execution_flow(self, temp_dir):
        """Test action execution with event data"""
        # Create test script
        script_path = temp_dir / "test_action.sh"
        script_path.write_text("#!/bin/bash\necho \"Event: $FACE_AUTH_EVENT\"")
        script_path.chmod(0o755)
        
        # Execute action
        event_data = {
            'event': 'on_presence',
            'username': 'testuser',
            'confidence': 0.95
        }
        
        # Test log action (always works)
        result = ActionHandler.execute_action('log', event_data)
        assert result is True
