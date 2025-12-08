#!/usr/bin/env python3
"""
Face recognition module for Face Authentication System
"""

import cv2
import face_recognition
import numpy as np
from typing import List, Optional, Tuple
import logging
import time
from pathlib import Path

from config import get_config
from models import Database

logger = logging.getLogger(__name__)


class FaceAuthenticator:
    """Face recognition and authentication handler"""
    
    def __init__(self, db: Optional[Database] = None):
        """
        Initialize face authenticator
        
        Args:
            db: Database instance (creates new if None)
        """
        self.config = get_config()
        self.db = db or Database(self.config.get('database.path'))
        
        # Camera settings
        self.camera_id = self.config.get('camera.device_id', 0)
        self.camera_width = self.config.get('camera.width', 640)
        self.camera_height = self.config.get('camera.height', 480)
        
        # Recognition settings
        self.tolerance = self.config.get('recognition.tolerance', 0.6)
        self.model = self.config.get('recognition.model', 'hog')
        self.num_jitters = self.config.get('recognition.num_jitters', 1)
        
        # Performance settings
        self.scale_factor = self.config.get('recognition.scale_factor', 0.5)  # Downscale for faster detection
        self.skip_frames = self.config.get('recognition.skip_frames', 0)  # Skip frames for speed
        self.try_rotations = self.config.get('recognition.try_rotations', False)  # Try 90/180/270 rotations
        
        self.camera: Optional[cv2.VideoCapture] = None
    
    def open_camera(self) -> bool:
        """
        Open camera device with retry logic
        
        Returns:
            True if successful, False otherwise
        """
        if self.camera is not None and self.camera.isOpened():
            return True
        
        max_retries = 2
        retry_delay = 0.3  # seconds - fast fail for PAM
        
        for attempt in range(max_retries):
            self.camera = cv2.VideoCapture(self.camera_id)
            
            if self.camera.isOpened():
                # Set camera properties
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
                logger.info(f"Opened camera {self.camera_id}")
                return True
            
            # Camera not available, retry after delay
            if attempt < max_retries - 1:
                logger.warning(f"Camera {self.camera_id} unavailable, retry {attempt + 1}/{max_retries}...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        logger.error(f"Failed to open camera {self.camera_id} after {max_retries} attempts")
        return False
    
    def close_camera(self) -> None:
        """Close camera device"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            logger.info("Closed camera")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera
        
        Returns:
            Frame as numpy array or None if failed
        """
        if not self.open_camera():
            return None
        
        ret, frame = self.camera.read()
        if not ret:
            logger.error("Failed to capture frame")
            return None
        
        return frame
    
    def detect_faces(self, frame: np.ndarray, use_scaling: bool = True, try_rotations: bool = False) -> List[Tuple]:
        """
        Detect faces in frame with optional rotation invariance
        
        Args:
            frame: Image frame (BGR format from OpenCV)
            use_scaling: If True, scale down frame for faster detection
            try_rotations: If True, try 90°, 180°, 270° rotations if no face found
            
        Returns:
            List of face locations (top, right, bottom, left) in original orientation
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Optionally scale down for faster detection
        if use_scaling and self.scale_factor < 1.0:
            small_frame = cv2.resize(rgb_frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
            face_locations = face_recognition.face_locations(small_frame, model=self.model)
            # Scale locations back to original size
            scale = 1.0 / self.scale_factor
            face_locations = [(int(top*scale), int(right*scale), int(bottom*scale), int(left*scale)) 
                             for (top, right, bottom, left) in face_locations]
        else:
            face_locations = face_recognition.face_locations(rgb_frame, model=self.model)
        
        if len(face_locations) > 0:
            return face_locations
        
        # Skip rotations if not requested (faster auth)
        if not try_rotations:
            return []
        
        # If no faces found, try rotations
        rotations = [
            (90, cv2.ROTATE_90_CLOCKWISE),
            (180, cv2.ROTATE_180),
            (270, cv2.ROTATE_90_COUNTERCLOCKWISE)
        ]
        
        for angle, rotation_code in rotations:
            # Rotate frame
            rotated_frame = cv2.rotate(rgb_frame, rotation_code)
            
            # Detect faces in rotated frame
            face_locations = face_recognition.face_locations(rotated_frame, model=self.model)
            
            if len(face_locations) > 0:
                logger.info(f"Faces detected at {angle}° rotation")
                
                # Transform coordinates back to original orientation
                h, w = rgb_frame.shape[:2]
                h_rot, w_rot = rotated_frame.shape[:2]
                
                transformed_locations = []
                for (top, right, bottom, left) in face_locations:
                    if angle == 90:
                        # 90° clockwise: (x,y) -> (h-y, x)
                        new_top = left
                        new_right = h - top
                        new_bottom = right
                        new_left = h - bottom
                    elif angle == 180:
                        # 180°: (x,y) -> (w-x, h-y)
                        new_top = h - bottom
                        new_right = w - left
                        new_bottom = h - top
                        new_left = w - right
                    else:  # 270
                        # 270° clockwise (90° counter): (x,y) -> (y, w-x)
                        new_top = w - right
                        new_right = bottom
                        new_bottom = w - left
                        new_left = top
                    
                    transformed_locations.append((new_top, new_right, new_bottom, new_left))
                
                return transformed_locations
        
        # No faces found at any rotation
        return []

    
    def encode_face(self, frame: np.ndarray, face_location: Tuple) -> Optional[np.ndarray]:
        """
        Generate face encoding from frame
        
        Args:
            frame: Image frame (BGR format)
            face_location: Face location tuple (top, right, bottom, left)
            
        Returns:
            Face encoding array or None
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Generate encoding
        encodings = face_recognition.face_encodings(
            rgb_frame, 
            [face_location],
            num_jitters=self.num_jitters
        )
        
        if len(encodings) > 0:
            return encodings[0]
        
        return None
    
    def enroll_user(self, username: str, num_samples: Optional[int] = None, 
                   sample_delay: Optional[float] = None, 
                   show_preview: bool = True) -> bool:
        """
        Enroll a new user by capturing face samples
        
        Args:
            username: Username to enroll
            num_samples: Number of face samples to capture
            sample_delay: Delay between samples in seconds
            show_preview: Whether to show camera preview
            
        Returns:
            True if enrollment successful, False otherwise
        """
        if num_samples is None:
            num_samples = self.config.get('enrollment.num_samples', 5)
        if sample_delay is None:
            sample_delay = self.config.get('enrollment.sample_delay', 1.0)
        
        # Check if user already exists
        existing_user = self.db.get_user(username)
        if existing_user:
            logger.error(f"User {username} already enrolled")
            return False
        
        if not self.open_camera():
            return False
        
        face_encodings = []
        samples_captured = 0
        
        logger.info(f"Starting enrollment for {username}. Capturing {num_samples} samples...")
        print(f"\n🎥 Enrolling user: {username}")
        print(f"📸 Please look at the camera. Capturing {num_samples} samples...\n")
        
        try:
            while samples_captured < num_samples:
                frame = self.capture_frame()
                if frame is None:
                    continue
                
                # Detect faces
                face_locations = self.detect_faces(frame, try_rotations=True)
                
                if len(face_locations) == 0:
                    if show_preview:
                        cv2.putText(frame, "No face detected", (10, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.imshow('Enrollment', frame)
                        cv2.waitKey(1)
                    continue
                
                if len(face_locations) > 1:
                    if show_preview:
                        cv2.putText(frame, "Multiple faces detected", (10, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                        cv2.imshow('Enrollment', frame)
                        cv2.waitKey(1)
                    continue
                
                # Encode face
                face_location = face_locations[0]
                encoding = self.encode_face(frame, face_location)
                
                if encoding is not None:
                    face_encodings.append(encoding)
                    samples_captured += 1
                    
                    logger.info(f"Captured sample {samples_captured}/{num_samples}")
                    print(f"✓ Sample {samples_captured}/{num_samples} captured")
                    
                    # Draw rectangle around face
                    if show_preview:
                        top, right, bottom, left = face_location
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(frame, f"Sample {samples_captured}/{num_samples}", 
                                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.imshow('Enrollment', frame)
                        cv2.waitKey(1)
                    
                    # Wait before next sample
                    if samples_captured < num_samples:
                        time.sleep(sample_delay)
                
                if show_preview:
                    cv2.imshow('Enrollment', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        logger.info("Enrollment cancelled by user")
                        print("\n❌ Enrollment cancelled")
                        return False
            
            # Save to database
            self.db.add_user(username, face_encodings)
            logger.info(f"Successfully enrolled {username}")
            print(f"\n✅ Successfully enrolled {username} with {num_samples} samples!\n")
            
            return True
            
        finally:
            if show_preview:
                cv2.destroyAllWindows()
            self.close_camera()

    def enroll_user_interactive(self, username: str, callback=None) -> bool:
        """
        Interactive enrollment with callback for GUI updates
        
        Args:
            username: Username to enroll
            callback: Function(frame, status_text, progress) called per frame
            
        Returns:
            True if enrollment successful
        """
        # Check if user already exists
        existing_user = self.db.get_user(username)
        if existing_user:
            logger.error(f"User {username} already enrolled")
            return False
        
        if not self.open_camera():
            return False
            
        face_encodings = []
        
        # Defined angles for robust enrollment
        phases = [
            ("Center", "Look straight at the camera"),
            ("Left", "Turn head slightly LEFT"),
            ("Right", "Turn head slightly RIGHT"),
            ("Up", "Tilt head slightly UP"),
            ("Down", "Tilt head slightly DOWN")
        ]
        
        try:
            for i, (phase_name, instruction) in enumerate(phases):
                captured = False
                start_phase = time.time()
                
                while not captured:
                    # Check for timeout (30 seconds per phase)
                    if time.time() - start_phase > 30:
                        if callback:
                            callback(None, "Timeout waiting for face", 0)
                        return False
                        
                    frame = self.capture_frame()
                    if frame is None:
                        continue
                        
                    # Detect faces
                    face_locations = self.detect_faces(frame, try_rotations=True)
                    
                    status = f"{instruction}"
                    color = (255, 255, 255)
                    
                    if len(face_locations) == 0:
                        status = "No face detected"
                        color = (0, 0, 255)
                    elif len(face_locations) > 1:
                        status = "Multiple faces detected"
                        color = (0, 0, 255)
                    else:
                        # Good face detected
                        status = "Hold steady..."
                        color = (0, 255, 0)
                        
                        # Draw box on frame for preview
                        top, right, bottom, left = face_locations[0]
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        
                        # Capture logic: specific to phase? 
                        # For now, just require a clear face for 1 second continuously?
                        # Or just take one good frame after a delay?
                        # Let's simple it: unique valid frame
                        
                        encoding = self.encode_face(frame, face_locations[0])
                        if encoding is not None:
                            face_encodings.append(encoding)
                            captured = True
                            # Brief pause/success feedback
                            if callback:
                                # Show success for a moment
                                cv2.putText(frame, "Captured!", (10, 60), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                                callback(frame, f"Captured {phase_name}!", (i + 1) / len(phases) * 100)
                            time.sleep(0.5)
                            continue

                    # Send update to GUI
                    if callback:
                        # Resize frame for GUI if needed, or pass raw
                        # Convert to RGB for PIL
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        callback(rgb_frame, status, (i) / len(phases) * 100)
                    
                    # Allow cancellation via callback return value?
                    # interactive implementation implies running in a thread
                    
            # Save to database
            self.db.add_user(username, face_encodings)
            logger.info(f"Successfully enrolled {username}")
            return True
            
        finally:
            self.close_camera()
    
    def authenticate(self, timeout: float = 10.0, show_preview: bool = False) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Authenticate user by comparing face with enrolled users
        
        Args:
            timeout: Maximum time to wait for authentication
            show_preview: Whether to show camera preview
            
        Returns:
            Tuple of (success, username, confidence)
        """
        if not self.open_camera():
            return False, None, None
        
        # Get all enrolled users
        users = self.db.get_all_users()
        if not users:
            logger.warning("No enrolled users found")
            return False, None, None
        
        # Load all face encodings
        known_encodings = []
        known_usernames = []
        
        for user in users:
            encodings = self.db.decrypt_encodings(user.face_encodings)
            for encoding in encodings:
                known_encodings.append(encoding)
                known_usernames.append(user.username)
        
        logger.info(f"Authenticating against {len(users)} enrolled users...")
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                frame = self.capture_frame()
                if frame is None:
                    continue
                
                # Detect faces (use rotation detection if configured)
                face_locations = self.detect_faces(frame, try_rotations=self.try_rotations)
                
                if len(face_locations) == 0:
                    if show_preview:
                        cv2.putText(frame, "No face detected", (10, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.imshow('Authentication', frame)
                        cv2.waitKey(1)
                    continue
                
                # Use first detected face
                face_location = face_locations[0]
                encoding = self.encode_face(frame, face_location)
                
                if encoding is None:
                    continue
                
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    known_encodings, encoding, tolerance=self.tolerance
                )
                face_distances = face_recognition.face_distance(known_encodings, encoding)
                
                if True in matches:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        username = known_usernames[best_match_index]
                        confidence = 1.0 - face_distances[best_match_index]
                        
                        # Update last seen
                        self.db.update_last_seen(username)
                        self.db.log_authentication(username, True, confidence)
                        
                        logger.info(f"Authentication successful: {username} (confidence: {confidence:.2f})")
                        
                        if show_preview:
                            top, right, bottom, left = face_location
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                            cv2.putText(frame, f"{username} ({confidence:.2f})", 
                                      (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                                      0.5, (0, 255, 0), 2)
                            cv2.imshow('Authentication', frame)
                            cv2.waitKey(1000)
                        
                        return True, username, confidence
                
                if show_preview:
                    cv2.imshow('Authentication', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            
            # Authentication failed
            self.db.log_authentication(None, False)
            logger.warning("Authentication failed: no match found")
            return False, None, None
            
        finally:
            if show_preview:
                cv2.destroyAllWindows()
            self.close_camera()
    
    def check_presence(self) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Quick check if any enrolled user is present
        
        Returns:
            Tuple of (present, username, confidence)
        """
        frame = self.capture_frame()
        if frame is None:
            return False, None, None
        
        # Detect faces
        face_locations = self.detect_faces(frame)
        
        if len(face_locations) == 0:
            return False, None, None
        
        # Get all enrolled users
        users = self.db.get_all_users()
        if not users:
            return False, None, None
        
        # Load all face encodings
        known_encodings = []
        known_usernames = []
        
        for user in users:
            encodings = self.db.decrypt_encodings(user.face_encodings)
            for encoding in encodings:
                known_encodings.append(encoding)
                known_usernames.append(user.username)
        
        # Check first detected face
        face_location = face_locations[0]
        encoding = self.encode_face(frame, face_location)
        
        if encoding is None:
            return False, None, None
        
        # Compare with known faces
        matches = face_recognition.compare_faces(
            known_encodings, encoding, tolerance=self.tolerance
        )
        face_distances = face_recognition.face_distance(known_encodings, encoding)
        
        if True in matches:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                username = known_usernames[best_match_index]
                confidence = 1.0 - face_distances[best_match_index]
                return True, username, confidence
        
        return False, None, None
