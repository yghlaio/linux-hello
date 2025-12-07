#!/usr/bin/env python3
"""
Monitoring daemon for Face Authentication System
Continuously monitors for user presence and triggers actions
"""

import time
import logging
import signal
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

from config import get_config
from models import Database
from face_auth import FaceAuthenticator
from actions import ActionHandler
from event_hooks import EventHooks

logger = logging.getLogger(__name__)


class MonitorDaemon:
    """Daemon for continuous face monitoring"""
    
    def __init__(self):
        """Initialize monitoring daemon"""
        self.config = get_config()
        self.db = Database(self.config.get('database.path'))
        self.authenticator = FaceAuthenticator(self.db)
        self.event_hooks = EventHooks()
        
        # Load hooks from config
        hooks_config = self.config.get('hooks', {})
        self.event_hooks.load_from_config(hooks_config)
        
        # Monitoring settings
        self.enabled = self.config.get('monitoring.enabled', True)
        self.check_interval = self.config.get('monitoring.check_interval', 2.0)
        self.absence_timeout = self.config.get('monitoring.absence_timeout', 30.0)
        self.presence_timeout = self.config.get('monitoring.presence_timeout', 5.0)
        
        # State tracking
        self.running = False
        self.user_present = False
        self.current_user: Optional[str] = None
        self.last_seen_time: Optional[float] = None
        self.last_absent_time: Optional[float] = None
        self.absence_action_triggered = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self) -> None:
        """Start monitoring daemon"""
        if not self.enabled:
            logger.warning("Monitoring is disabled in configuration")
            return
        
        logger.info("Starting face monitoring daemon...")
        logger.info(f"Check interval: {self.check_interval}s")
        logger.info(f"Absence timeout: {self.absence_timeout}s")
        
        # Open camera
        if not self.authenticator.open_camera():
            logger.error("Failed to open camera, cannot start monitoring")
            return
        
        self.running = True
        
        try:
            self._monitoring_loop()
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop monitoring daemon"""
        logger.info("Stopping face monitoring daemon...")
        self.running = False
        self.authenticator.close_camera()
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                # Check for presence
                present, username, confidence = self.authenticator.check_presence()
                current_time = time.time()
                
                if present and username:
                    self._handle_presence(username, confidence, current_time)
                else:
                    self._handle_absence(current_time)
                
                # Sleep until next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop iteration: {e}", exc_info=True)
                time.sleep(self.check_interval)
    
    def _handle_presence(self, username: str, confidence: float, current_time: float) -> None:
        """
        Handle user presence detection
        
        Args:
            username: Detected username
            confidence: Recognition confidence
            current_time: Current timestamp
        """
        self.last_seen_time = current_time
        
        # Check if this is a new presence event
        if not self.user_present:
            # User just appeared
            self.user_present = True
            self.current_user = username
            self.absence_action_triggered = False
            
            logger.info(f"User present: {username} (confidence: {confidence:.2f})")
            
            # Log presence
            self.db.log_presence('present', username)
            
            # Trigger presence actions
            actions = self.config.get('actions.on_presence', [])
            event_data = {
                'username': username,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
            ActionHandler.execute_actions(actions, event_data)
            
            # Trigger event hooks
            self.event_hooks.trigger('on_presence', event_data)
        
        else:
            # User still present, update current user if different
            if self.current_user != username:
                logger.info(f"User changed: {self.current_user} -> {username}")
                self.current_user = username
    
    def _handle_absence(self, current_time: float) -> None:
        """
        Handle user absence detection
        
        Args:
            current_time: Current timestamp
        """
        if self.user_present:
            # User was present, now absent
            if self.last_absent_time is None:
                # First absence detection
                self.last_absent_time = current_time
                logger.debug("User not detected, starting absence timer...")
            
            else:
                # Check if absence timeout exceeded
                absence_duration = current_time - self.last_absent_time
                
                if absence_duration >= self.absence_timeout and not self.absence_action_triggered:
                    # Trigger absence actions
                    logger.warning(f"User absent for {absence_duration:.1f}s, triggering actions")
                    
                    self.user_present = False
                    self.absence_action_triggered = True
                    
                    # Log absence
                    self.db.log_presence('absent', self.current_user)
                    
                    # Trigger absence actions
                    actions = self.config.get('actions.on_absence', [])
                    event_data = {
                        'username': self.current_user,
                        'absence_duration': absence_duration,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Log which actions will be taken
                    action_names = ', '.join(actions) if actions else 'none'
                    self.db.log_presence('absent', self.current_user, action_names)
                    
                    ActionHandler.execute_actions(actions, event_data)
                    
                    # Trigger event hooks
                    self.event_hooks.trigger('on_absence', event_data)
                    
                    self.current_user = None
        
        else:
            # User already marked as absent
            self.last_absent_time = None


def main():
    """Main entry point for daemon"""
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
    logger.info("Face Authentication Monitoring Daemon")
    logger.info("=" * 60)
    
    # Create and start daemon
    daemon = MonitorDaemon()
    daemon.start()


if __name__ == '__main__':
    main()
