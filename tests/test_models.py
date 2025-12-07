"""
Tests for database models
"""

import pytest
from datetime import datetime
import numpy as np
from pathlib import Path

from models import Database, User


class TestDatabase:
    """Test database operations"""
    
    def test_create_database(self, test_data_dir):
        """Test database creation"""
        db_path = test_data_dir / "test.db"
        db = Database(str(db_path))
        
        assert db_path.exists()
        assert db.get_session() is not None
    
    def test_add_user(self, test_data_dir, mock_face_encoding):
        """Test adding a new user"""
        db_path = test_data_dir / "test.db"
        db = Database(str(db_path))
        
        # add_user expects a list of encodings
        user = db.add_user("testuser", [mock_face_encoding])
        assert user is not None
        assert user.username == "testuser"
        
        # Verify user exists
        user = db.get_user("testuser")
        assert user is not None
        assert user.username == "testuser"
    
    def test_add_duplicate_user(self, test_data_dir, mock_face_encoding):
        """Test adding duplicate user"""
        db_path = test_data_dir / "test.db"
        db = Database(str(db_path))
        
        db.add_user("testuser", [mock_face_encoding])
        
        # Try to add same user again - should raise exception
        with pytest.raises(Exception):  # IntegrityError
            db.add_user("testuser", [mock_face_encoding])
    
    def test_get_user(self, test_data_dir, mock_face_encoding):
        """Test retrieving a user"""
        db_path = test_data_dir / "test.db"
        db = Database(str(db_path))
        
        db.add_user("testuser", [mock_face_encoding])
        
        user = db.get_user("testuser")
        assert user is not None
        assert user.username == "testuser"
        # face_encodings is stored as encrypted text
        assert user.face_encodings is not None
    
    def test_get_nonexistent_user(self, test_data_dir):
        """Test retrieving non-existent user"""
        db_path = test_data_dir / "test.db"
        db = Database(str(db_path))
        
        user = db.get_user("nonexistent")
        assert user is None
    
    def test_get_all_users(self, test_data_dir, mock_face_encoding):
        """Test retrieving all users"""
        db_path = test_data_dir / "test.db"
        db = Database(str(db_path))
        
        # Add multiple users
        db.add_user("user1", [mock_face_encoding])
        db.add_user("user2", [mock_face_encoding])
        db.add_user("user3", [mock_face_encoding])
        
        users = db.get_all_users()
        assert len(users) == 3
        assert {u.username for u in users} == {"user1", "user2", "user3"}
    
    def test_remove_user(self, test_data_dir, mock_face_encoding):
        """Test removing a user"""
        db_path = test_data_dir / "test.db"
        db = Database(str(db_path))
        
        db.add_user("testuser", [mock_face_encoding])
        
        success = db.remove_user("testuser")
        assert success is True
        
        # Verify user is removed
        user = db.get_user("testuser")
        assert user is None
    
    def test_remove_nonexistent_user(self, test_data_dir):
        """Test removing non-existent user"""
        db_path = test_data_dir / "test.db"
        db = Database(str(db_path))
        
        success = db.remove_user("nonexistent")
        assert success is False
    
    def test_update_last_seen(self, test_data_dir, mock_face_encoding):
        """Test updating user's last seen timestamp"""
        db_path = test_data_dir / "test.db"
        db = Database(str(db_path))
        
        db.add_user("testuser", [mock_face_encoding])
        
        # Update last seen
        db.update_last_seen("testuser")
        
        # Verify timestamp is updated
        user = db.get_user("testuser")
        assert user.last_seen is not None
        assert isinstance(user.last_seen, datetime)
    
    def test_face_encoding_storage(self, test_data_dir):
        """Test face encoding storage and retrieval"""
        db_path = test_data_dir / "test.db"
        db = Database(str(db_path))
        
        # Create specific encodings
        encoding1 = np.array([0.1, 0.2, 0.3, 0.4, 0.5] * 25 + [0.1, 0.2, 0.3])  # 128 elements
        encoding2 = np.array([0.2, 0.3, 0.4, 0.5, 0.6] * 25 + [0.2, 0.3, 0.4])  # 128 elements
        
        db.add_user("testuser", [encoding1, encoding2])
        
        # Retrieve and verify
        user = db.get_user("testuser")
        retrieved_encodings = db.decrypt_encodings(user.face_encodings)
        
        assert isinstance(retrieved_encodings, list)
        assert len(retrieved_encodings) == 2
        np.testing.assert_array_almost_equal(encoding1, retrieved_encodings[0])
        np.testing.assert_array_almost_equal(encoding2, retrieved_encodings[1])


class TestUser:
    """Test User model"""
    
    def test_user_creation(self):
        """Test creating a user object"""
        # User is created via Database.add_user, not directly
        # This test verifies the User model structure
        user = User()
        user.username = "testuser"
        user.face_encodings = "encrypted_data"
        
        assert user.username == "testuser"
        assert user.face_encodings == "encrypted_data"
    
    def test_user_timestamps(self):
        """Test user timestamp fields"""
        user = User()
        user.username = "testuser"
        user.face_encodings = "encrypted_data"
        user.enrolled_at = datetime.utcnow()
        
        assert isinstance(user.enrolled_at, datetime)
        
        # Set last seen
        user.last_seen = datetime.utcnow()
        assert isinstance(user.last_seen, datetime)

