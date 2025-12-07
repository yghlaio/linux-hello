#!/usr/bin/env python3
"""
D-Bus service for Face Authentication System
Provides integration interface for external scripts
"""

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import logging
import sys
from typing import Optional

from config import get_config
from models import Database
from face_auth import FaceAuthenticator
from event_hooks import EventHooks

logger = logging.getLogger(__name__)


class FaceAuthDBusService(dbus.service.Object):
    """D-Bus service for face authentication"""
    
    def __init__(self, bus_name, object_path):
        """
        Initialize D-Bus service
        
        Args:
            bus_name: D-Bus bus name
            object_path: D-Bus object path
        """
        super().__init__(bus_name, object_path)
        
        self.config = get_config()
        self.db = Database(self.config.get('database.path'))
        self.authenticator = FaceAuthenticator(self.db)
        self.event_hooks = EventHooks()
        
        self.monitoring_enabled = False
        self.presence_status = False
        self.current_user: Optional[str] = None
        
        logger.info("D-Bus service initialized")
    
    @dbus.service.method(
        dbus_interface='org.faceauth.Service',
        in_signature='', out_signature='(bsd)'
    )
    def Authenticate(self):
        """
        Trigger face authentication
        
        Returns:
            Tuple of (success: bool, username: str, confidence: float)
        """
        logger.info("D-Bus: Authenticate called")
        
        try:
            success, username, confidence = self.authenticator.authenticate(timeout=10.0)
            
            if success:
                logger.info(f"D-Bus: Authentication successful - {username}")
                self.UserAuthenticationSuccess(username, confidence or 0.0)
                return (True, username or '', confidence or 0.0)
            else:
                logger.info("D-Bus: Authentication failed")
                self.UserAuthenticationFailed()
                return (False, '', 0.0)
                
        except Exception as e:
            logger.error(f"D-Bus: Authentication error - {e}")
            return (False, str(e), 0.0)
    
    @dbus.service.method(
        dbus_interface='org.faceauth.Service',
        in_signature='', out_signature='(bsd)'
    )
    def GetPresenceStatus(self):
        """
        Check if user is currently present
        
        Returns:
            Tuple of (present: bool, username: str, confidence: float)
        """
        logger.debug("D-Bus: GetPresenceStatus called")
        
        try:
            present, username, confidence = self.authenticator.check_presence()
            
            return (present, username or '', confidence or 0.0)
            
        except Exception as e:
            logger.error(f"D-Bus: Presence check error - {e}")
            return (False, str(e), 0.0)
    
    @dbus.service.method(
        dbus_interface='org.faceauth.Service',
        in_signature='', out_signature='b'
    )
    def EnableMonitoring(self):
        """
        Enable continuous monitoring
        
        Returns:
            True if successful
        """
        logger.info("D-Bus: EnableMonitoring called")
        self.monitoring_enabled = True
        return True
    
    @dbus.service.method(
        dbus_interface='org.faceauth.Service',
        in_signature='', out_signature='b'
    )
    def DisableMonitoring(self):
        """
        Disable continuous monitoring
        
        Returns:
            True if successful
        """
        logger.info("D-Bus: DisableMonitoring called")
        self.monitoring_enabled = False
        return True
    
    @dbus.service.method(
        dbus_interface='org.faceauth.Service',
        in_signature='ss', out_signature='b'
    )
    def RegisterEventHandler(self, script_path, event_type):
        """
        Register a custom script for an event
        
        Args:
            script_path: Path to script
            event_type: Event type (on_presence, on_absence, etc.)
            
        Returns:
            True if successful
        """
        logger.info(f"D-Bus: RegisterEventHandler called - {event_type}: {script_path}")
        
        try:
            return self.event_hooks.register_script(event_type, script_path)
        except Exception as e:
            logger.error(f"D-Bus: Error registering event handler - {e}")
            return False
    
    @dbus.service.method(
        dbus_interface='org.faceauth.Service',
        in_signature='ss', out_signature='b'
    )
    def UnregisterEventHandler(self, script_path, event_type):
        """
        Unregister a custom script
        
        Args:
            script_path: Path to script
            event_type: Event type
            
        Returns:
            True if successful
        """
        logger.info(f"D-Bus: UnregisterEventHandler called - {event_type}: {script_path}")
        
        try:
            return self.event_hooks.unregister_script(event_type, script_path)
        except Exception as e:
            logger.error(f"D-Bus: Error unregistering event handler - {e}")
            return False
    
    @dbus.service.method(
        dbus_interface='org.faceauth.Service',
        in_signature='', out_signature='as'
    )
    def GetEnrolledUsers(self):
        """
        Get list of enrolled users
        
        Returns:
            List of usernames
        """
        logger.debug("D-Bus: GetEnrolledUsers called")
        
        try:
            users = self.db.get_all_users()
            return [user.username for user in users]
        except Exception as e:
            logger.error(f"D-Bus: Error getting enrolled users - {e}")
            return []
    
    # Signals
    @dbus.service.signal(
        dbus_interface='org.faceauth.Service',
        signature='sd'
    )
    def UserPresent(self, username, confidence):
        """
        Signal emitted when user is detected
        
        Args:
            username: Detected username
            confidence: Recognition confidence
        """
        logger.debug(f"D-Bus signal: UserPresent - {username}")
    
    @dbus.service.signal(
        dbus_interface='org.faceauth.Service',
        signature='s'
    )
    def UserAbsent(self, username):
        """
        Signal emitted when user leaves
        
        Args:
            username: Username that left
        """
        logger.debug(f"D-Bus signal: UserAbsent - {username}")
    
    @dbus.service.signal(
        dbus_interface='org.faceauth.Service',
        signature='sd'
    )
    def UserAuthenticationSuccess(self, username, confidence):
        """
        Signal emitted on successful authentication
        
        Args:
            username: Authenticated username
            confidence: Recognition confidence
        """
        logger.debug(f"D-Bus signal: UserAuthenticationSuccess - {username}")
    
    @dbus.service.signal(
        dbus_interface='org.faceauth.Service',
        signature=''
    )
    def UserAuthenticationFailed(self):
        """Signal emitted on failed authentication"""
        logger.debug("D-Bus signal: UserAuthenticationFailed")


def main():
    """Main entry point for D-Bus service"""
    # Setup logging
    config = get_config()
    config.ensure_directories()
    
    log_level = config.get('logging.level', 'INFO')
    log_file = config.get('logging.file')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger.info("=" * 60)
    logger.info("Face Authentication D-Bus Service")
    logger.info("=" * 60)
    
    # Initialize D-Bus
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    
    service_name = config.get('dbus.service_name', 'org.faceauth.Service')
    object_path = config.get('dbus.object_path', '/org/faceauth/Service')
    
    try:
        bus = dbus.SessionBus()
        name = dbus.service.BusName(service_name, bus)
        service = FaceAuthDBusService(name, object_path)
        
        logger.info(f"D-Bus service started: {service_name}")
        logger.info(f"Object path: {object_path}")
        
        # Run main loop
        loop = GLib.MainLoop()
        logger.info("D-Bus service running...")
        loop.run()
        
    except KeyboardInterrupt:
        logger.info("D-Bus service stopped by user")
    except Exception as e:
        logger.error(f"D-Bus service error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
