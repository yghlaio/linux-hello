#!/usr/bin/env python3
"""
Action handlers for Face Authentication System
"""

import subprocess
import logging
import os
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ActionHandler:
    """Handler for system actions triggered by events"""
    
    @staticmethod
    def lock_screen() -> bool:
        """
        Lock the screen using loginctl
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try loginctl first (systemd)
            result = subprocess.run(
                ['loginctl', 'lock-session'],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info("Screen locked via loginctl")
                return True
            
            # Fallback to other methods
            # Try gnome-screensaver
            result = subprocess.run(
                ['gnome-screensaver-command', '-l'],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info("Screen locked via gnome-screensaver")
                return True
            
            # Try xdg-screensaver
            result = subprocess.run(
                ['xdg-screensaver', 'lock'],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info("Screen locked via xdg-screensaver")
                return True
            
            logger.error("Failed to lock screen: no suitable method found")
            return False
            
        except subprocess.TimeoutExpired:
            logger.error("Screen lock command timed out")
            return False
        except FileNotFoundError as e:
            logger.error(f"Screen lock command not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Error locking screen: {e}")
            return False
    
    @staticmethod
    def suspend() -> bool:
        """
        Suspend the system
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ['systemctl', 'suspend'],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info("System suspended")
                return True
            
            logger.error(f"Failed to suspend: {result.stderr.decode()}")
            return False
            
        except subprocess.TimeoutExpired:
            logger.error("Suspend command timed out")
            return False
        except Exception as e:
            logger.error(f"Error suspending system: {e}")
            return False
    
    @staticmethod
    def hibernate() -> bool:
        """
        Hibernate the system
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ['systemctl', 'hibernate'],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info("System hibernated")
                return True
            
            logger.error(f"Failed to hibernate: {result.stderr.decode()}")
            return False
            
        except subprocess.TimeoutExpired:
            logger.error("Hibernate command timed out")
            return False
        except Exception as e:
            logger.error(f"Error hibernating system: {e}")
            return False
    
    @staticmethod
    def run_custom_script(script_path: str, event_data: Optional[dict] = None) -> bool:
        """
        Run a custom script
        
        Args:
            script_path: Path to script to execute
            event_data: Optional event data to pass as environment variables
            
        Returns:
            True if successful, False otherwise
        """
        script_path = os.path.expanduser(script_path)
        
        if not os.path.exists(script_path):
            logger.error(f"Script not found: {script_path}")
            return False
        
        if not os.access(script_path, os.X_OK):
            logger.error(f"Script not executable: {script_path}")
            return False
        
        try:
            env = os.environ.copy()
            
            # Add event data to environment
            if event_data:
                for key, value in event_data.items():
                    env[f'FACE_AUTH_{key.upper()}'] = str(value)
            
            result = subprocess.run(
                [script_path],
                env=env,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully executed script: {script_path}")
                if result.stdout:
                    logger.debug(f"Script output: {result.stdout.decode()}")
                return True
            else:
                logger.error(f"Script failed with code {result.returncode}: {script_path}")
                if result.stderr:
                    logger.error(f"Script error: {result.stderr.decode()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Script timed out: {script_path}")
            return False
        except Exception as e:
            logger.error(f"Error executing script {script_path}: {e}")
            return False
    
    @staticmethod
    def send_notification(title: str, message: str, urgency: str = 'normal') -> bool:
        """
        Send desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            urgency: Urgency level (low, normal, critical)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ['notify-send', '-u', urgency, title, message],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.debug(f"Sent notification: {title}")
                return True
            
            return False
            
        except FileNotFoundError:
            logger.warning("notify-send not found, skipping notification")
            return False
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    @staticmethod
    def execute_action(action: str, event_data: Optional[dict] = None) -> bool:
        """
        Execute an action based on action string
        
        Args:
            action: Action to execute (e.g., 'lock_screen', 'custom_script:/path/to/script')
            event_data: Optional event data
            
        Returns:
            True if successful, False otherwise
        """
        if action == 'lock_screen':
            return ActionHandler.lock_screen()
        
        elif action == 'suspend':
            return ActionHandler.suspend()
        
        elif action == 'hibernate':
            return ActionHandler.hibernate()
        
        elif action == 'log':
            logger.info(f"Event logged: {event_data}")
            return True
        
        elif action.startswith('custom_script:'):
            script_path = action.split(':', 1)[1]
            return ActionHandler.run_custom_script(script_path, event_data)
        
        elif action.startswith('notify:'):
            message = action.split(':', 1)[1]
            title = event_data.get('event', 'Face Auth') if event_data else 'Face Auth'
            return ActionHandler.send_notification(title, message)
        
        else:
            logger.warning(f"Unknown action: {action}")
            return False
    
    @staticmethod
    def execute_actions(actions: List[str], event_data: Optional[dict] = None) -> None:
        """
        Execute multiple actions
        
        Args:
            actions: List of actions to execute
            event_data: Optional event data
        """
        for action in actions:
            try:
                ActionHandler.execute_action(action, event_data)
            except Exception as e:
                logger.error(f"Error executing action {action}: {e}")
