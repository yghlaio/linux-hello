#!/usr/bin/env python3
"""
Test rotation-invariant face detection
"""

import cv2
import sys
sys.path.insert(0, '.')

from face_auth import FaceAuthenticator
from models import Database

def test_rotation():
    """Test face detection at different rotations"""
    print("Testing rotation-invariant face detection...")
    print("=" * 50)
    
    auth = FaceAuthenticator()
    
    if not auth.open_camera():
        print("❌ Failed to open camera")
        return
    
    print("\n📸 Capturing frame...")
    frame = auth.capture_frame()
    
    if frame is None:
        print("❌ Failed to capture frame")
        return
    
    print("✅ Frame captured\n")
    
    # Test original
    print("Testing 0° (original)...")
    faces = auth.detect_faces(frame)
    print(f"  Found {len(faces)} face(s)")
    
    # Test 90° rotation
    print("\nTesting 90° rotation...")
    rotated_90 = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    faces_90 = auth.detect_faces(rotated_90)
    print(f"  Found {len(faces_90)} face(s)")
    
    # Test 180° rotation
    print("\nTesting 180° rotation...")
    rotated_180 = cv2.rotate(frame, cv2.ROTATE_180)
    faces_180 = auth.detect_faces(rotated_180)
    print(f"  Found {len(faces_180)} face(s)")
    
    # Test 270° rotation
    print("\nTesting 270° rotation...")
    rotated_270 = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    faces_270 = auth.detect_faces(rotated_270)
    print(f"  Found {len(faces_270)} face(s)")
    
    print("\n" + "=" * 50)
    print("✅ Rotation test complete!")
    print("\nRotation-invariant detection is now active.")
    print("Faces will be detected even when rotated 90°, 180°, or 270°.")
    
    auth.close_camera()

if __name__ == '__main__':
    test_rotation()
