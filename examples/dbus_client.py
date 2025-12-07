#!/usr/bin/env python3
"""
Example D-Bus client for Face Authentication System
Demonstrates how to integrate with the face auth system via D-Bus
"""

import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import sys


def on_user_present(username, confidence):
    """Callback for user presence signal"""
    print(f"🟢 User present: {username} (confidence: {confidence:.2%})")


def on_user_absent(username):
    """Callback for user absence signal"""
    print(f"🔴 User absent: {username}")


def on_auth_success(username, confidence):
    """Callback for authentication success signal"""
    print(f"✅ Authentication successful: {username} (confidence: {confidence:.2%})")


def on_auth_failed():
    """Callback for authentication failure signal"""
    print(f"❌ Authentication failed")


def main():
    """Main entry point"""
    print("Face Authentication D-Bus Client Example")
    print("=" * 60)
    
    # Initialize D-Bus
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    
    try:
        bus = dbus.SessionBus()
        
        # Get service object
        service = bus.get_object(
            'org.faceauth.Service',
            '/org/faceauth/Service'
        )
        
        # Get interface
        iface = dbus.Interface(service, 'org.faceauth.Service')
        
        print("\n📡 Connected to Face Authentication D-Bus service\n")
        
        # Example 1: Get presence status
        print("1. Checking presence status...")
        present, username, confidence = iface.GetPresenceStatus()
        if present:
            print(f"   ✓ User present: {username} (confidence: {confidence:.2%})")
        else:
            print(f"   ✗ No user detected")
        
        # Example 2: Get enrolled users
        print("\n2. Getting enrolled users...")
        users = iface.GetEnrolledUsers()
        print(f"   Enrolled users: {', '.join(users) if users else 'None'}")
        
        # Example 3: Register event handler
        # Example: Register a script to run on presence
        import os
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(script_dir, "examples", "on_presence.sh")
        success = iface.RegisterEventHandler(script_path, 'on_presence')
        if success:
            print(f"   ✓ Registered event handler")
        else:
            print(f"   ✗ Failed to register event handler")
        
        # Example 4: Connect to signals
        print("\n4. Listening for signals...")
        print("   (Press Ctrl+C to exit)\n")
        
        bus.add_signal_receiver(
            on_user_present,
            signal_name='UserPresent',
            dbus_interface='org.faceauth.Service'
        )
        
        bus.add_signal_receiver(
            on_user_absent,
            signal_name='UserAbsent',
            dbus_interface='org.faceauth.Service'
        )
        
        bus.add_signal_receiver(
            on_auth_success,
            signal_name='UserAuthenticationSuccess',
            dbus_interface='org.faceauth.Service'
        )
        
        bus.add_signal_receiver(
            on_auth_failed,
            signal_name='UserAuthenticationFailed',
            dbus_interface='org.faceauth.Service'
        )
        
        # Run main loop
        loop = GLib.MainLoop()
        loop.run()
        
    except dbus.DBusException as e:
        print(f"\n❌ D-Bus error: {e}")
        print("\nMake sure the face-auth D-Bus service is running:")
        print("  python dbus_service.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)


if __name__ == '__main__':
    main()
