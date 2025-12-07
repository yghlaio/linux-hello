#!/usr/bin/env python3
"""
Camera testing utility
Lists and tests available cameras
"""

import cv2
import sys


def list_cameras():
    """List all available cameras"""
    print("Scanning for cameras...\n")
    
    available = []
    for i in range(10):  # Check first 10 devices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"✅ Camera {i}:")
            print(f"   Device: /dev/video{i}")
            print(f"   Resolution: {int(width)}x{int(height)}")
            print(f"   FPS: {int(fps)}")
            print()
            
            available.append(i)
            cap.release()
    
    if not available:
        print("❌ No cameras found!")
        return []
    
    print(f"Found {len(available)} camera(s)")
    return available


def test_camera(device_id):
    """Test a specific camera"""
    print(f"\nTesting camera {device_id}...")
    print("Press 'q' to quit, 's' to save snapshot\n")
    
    cap = cv2.VideoCapture(device_id)
    
    if not cap.isOpened():
        print(f"❌ Failed to open camera {device_id}")
        return False
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Failed to read frame")
            break
        
        frame_count += 1
        
        # Add info overlay
        cv2.putText(frame, f"Camera {device_id} - Frame {frame_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit, 's' for snapshot", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow(f'Camera Test - {device_id}', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"camera_{device_id}_snapshot.jpg"
            cv2.imwrite(filename, frame)
            print(f"📸 Snapshot saved: {filename}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n✅ Camera {device_id} test complete ({frame_count} frames)")
    return True


def main():
    """Main entry point"""
    print("=" * 50)
    print("Camera Testing Utility")
    print("=" * 50)
    print()
    
    # List cameras
    cameras = list_cameras()
    
    if not cameras:
        sys.exit(1)
    
    # Ask which to test
    print("\nWhich camera would you like to test?")
    for cam in cameras:
        print(f"  {cam}: /dev/video{cam}")
    print("  a: Test all")
    print("  q: Quit")
    
    choice = input("\nChoice: ").strip().lower()
    
    if choice == 'q':
        return
    elif choice == 'a':
        for cam in cameras:
            test_camera(cam)
    else:
        try:
            cam_id = int(choice)
            if cam_id in cameras:
                test_camera(cam_id)
            else:
                print(f"❌ Camera {cam_id} not available")
        except ValueError:
            print("❌ Invalid choice")


if __name__ == '__main__':
    main()
