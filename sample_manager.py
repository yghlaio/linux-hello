#!/usr/bin/env python3
"""
Sample management utility for Face Authentication System
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional
import logging

from models import Database
from face_auth import FaceAuthenticator

logger = logging.getLogger(__name__)


class SampleManager:
    """Manage face samples for users"""
    
    def __init__(self, db: Optional[Database] = None):
        """Initialize sample manager"""
        from config import get_config
        self.config = get_config()
        self.db = db or Database(self.config.get('database.path'))
        self.authenticator = FaceAuthenticator(self.db)
    
    def view_samples(self, username: str) -> Optional[List[np.ndarray]]:
        """
        Get all face samples for a user
        
        Args:
            username: Username
            
        Returns:
            List of face encodings or None
        """
        return self.db.get_user_samples(username)
    
    def add_sample_from_camera(self, username: str) -> bool:
        """
        Add a face sample from camera
        
        Args:
            username: Username
            
        Returns:
            True if successful
        """
        print(f"\n📸 Adding sample for {username}")
        print("Please look at the camera...\n")
        
        if not self.authenticator.open_camera():
            print("❌ Failed to open camera")
            return False
        
        try:
            while True:
                frame = self.authenticator.capture_frame()
                if frame is None:
                    continue
                
                # Detect faces
                face_locations = self.authenticator.detect_faces(frame)
                
                if len(face_locations) == 0:
                    cv2.putText(frame, "No face detected", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow('Add Sample', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("\n❌ Cancelled")
                        return False
                    continue
                
                if len(face_locations) > 1:
                    cv2.putText(frame, "Multiple faces detected", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                    cv2.imshow('Add Sample', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("\n❌ Cancelled")
                        return False
                    continue
                
                # Encode face
                face_location = face_locations[0]
                encoding = self.authenticator.encode_face(frame, face_location)
                
                if encoding is not None:
                    # Draw rectangle
                    top, right, bottom, left = face_location
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, "Press SPACE to capture, Q to cancel", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.imshow('Add Sample', frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord(' '):  # Space to capture
                        if self.db.add_sample(username, encoding):
                            print("✅ Sample added successfully!")
                            return True
                        else:
                            print("❌ Failed to add sample")
                            return False
                    elif key == ord('q'):
                        print("\n❌ Cancelled")
                        return False
                
                cv2.imshow('Add Sample', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n❌ Cancelled")
                    return False
        finally:
            cv2.destroyAllWindows()
            self.authenticator.close_camera()
    
    def remove_sample(self, username: str, index: int) -> bool:
        """
        Remove a specific sample
        
        Args:
            username: Username
            index: Sample index (0-based)
            
        Returns:
            True if successful
        """
        return self.db.remove_sample(username, index)
    
    def get_sample_count(self, username: str) -> int:
        """Get number of samples for user"""
        return self.db.get_sample_count(username)
    
    def export_samples(self, username: str, output_dir: str) -> bool:
        """
        Export samples as visualization (not actual images)
        
        Args:
            username: Username
            output_dir: Output directory
            
        Returns:
            True if successful
        """
        samples = self.view_samples(username)
        if not samples:
            return False
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save encoding data
        for i, encoding in enumerate(samples):
            np.save(output_path / f"{username}_sample_{i}.npy", encoding)
        
        print(f"✅ Exported {len(samples)} samples to {output_dir}")
        return True
