"""
Mock utilities for testing face authentication
"""

import numpy as np
from unittest.mock import Mock, MagicMock
import cv2


class MockCamera:
    """Mock camera for testing"""
    
    def __init__(self, device_id=0):
        self.device_id = device_id
        self.is_opened = False
        self.frame_count = 0
        
    def isOpened(self):
        """Check if camera is opened"""
        return self.is_opened
    
    def open(self, device_id):
        """Open camera"""
        self.is_opened = True
        return True
    
    def release(self):
        """Release camera"""
        self.is_opened = False
    
    def read(self):
        """Read a frame from camera"""
        if not self.is_opened:
            return False, None
        
        # Generate a random frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        self.frame_count += 1
        return True, frame
    
    def set(self, prop, value):
        """Set camera property"""
        return True
    
    def get(self, prop):
        """Get camera property"""
        if prop == cv2.CAP_PROP_FRAME_WIDTH:
            return 640
        elif prop == cv2.CAP_PROP_FRAME_HEIGHT:
            return 480
        return 0


class MockFaceRecognition:
    """Mock face recognition for testing"""
    
    @staticmethod
    def face_locations(image, model='hog'):
        """Mock face location detection"""
        # Return a single face location
        return [(100, 400, 300, 200)]  # (top, right, bottom, left)
    
    @staticmethod
    def face_encodings(image, known_face_locations=None, num_jitters=1):
        """Mock face encoding generation"""
        # Return a random 128-dimensional encoding
        return [np.random.rand(128).astype(np.float64)]
    
    @staticmethod
    def compare_faces(known_encodings, face_encoding, tolerance=0.6):
        """Mock face comparison"""
        # Return True for first encoding, False for others
        return [True] + [False] * (len(known_encodings) - 1)
    
    @staticmethod
    def face_distance(known_encodings, face_encoding):
        """Mock face distance calculation"""
        # Return distances (lower = more similar)
        distances = []
        for i in range(len(known_encodings)):
            if i == 0:
                distances.append(0.3)  # Close match
            else:
                distances.append(0.8)  # Poor match
        return np.array(distances)


def create_mock_face_image(width=640, height=480):
    """Create a mock face image"""
    return np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)


def create_mock_face_encoding():
    """Create a mock face encoding"""
    return np.random.rand(128).astype(np.float64)


def create_mock_face_location():
    """Create a mock face location"""
    return (100, 400, 300, 200)  # (top, right, bottom, left)


def create_similar_encoding(base_encoding, similarity=0.95):
    """
    Create an encoding similar to the base encoding
    
    Args:
        base_encoding: Base face encoding
        similarity: Similarity level (0.0-1.0)
    
    Returns:
        Similar face encoding
    """
    noise = np.random.rand(128).astype(np.float64) * (1 - similarity)
    return base_encoding * similarity + noise * (1 - similarity)


def create_different_encoding(base_encoding):
    """
    Create an encoding different from the base encoding
    
    Args:
        base_encoding: Base face encoding
    
    Returns:
        Different face encoding
    """
    return np.random.rand(128).astype(np.float64)
