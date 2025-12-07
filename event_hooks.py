#!/usr/bin/env python3
"""
Event hooks system for Face Authentication System
"""

import logging
from typing import List, Optional, Dict, Callable
from pathlib import Path
import threading

from actions import ActionHandler

logger = logging.getLogger(__name__)


class EventHooks:
    """Event hooks manager for custom script integration"""
    
    def __init__(self):
        """Initialize event hooks manager"""
        self.hooks: Dict[str, List[str]] = {
            'on_presence': [],
            'on_absence': [],
            'on_auth_success': [],
            'on_auth_failure': [],
        }
        self.callbacks: Dict[str, List[Callable]] = {
            'on_presence': [],
            'on_absence': [],
            'on_auth_success': [],
            'on_auth_failure': [],
        }
    
    def register_script(self, event_type: str, script_path: str) -> bool:
        """
        Register a script to be executed on event
        
        Args:
            event_type: Event type (on_presence, on_absence, etc.)
            script_path: Path to script
            
        Returns:
            True if successful, False otherwise
        """
        if event_type not in self.hooks:
            logger.error(f"Invalid event type: {event_type}")
            return False
        
        script_path = str(Path(script_path).expanduser().resolve())
        
        if script_path not in self.hooks[event_type]:
            self.hooks[event_type].append(script_path)
            logger.info(f"Registered script for {event_type}: {script_path}")
            return True
        
        logger.warning(f"Script already registered for {event_type}: {script_path}")
        return False
    
    def unregister_script(self, event_type: str, script_path: str) -> bool:
        """
        Unregister a script
        
        Args:
            event_type: Event type
            script_path: Path to script
            
        Returns:
            True if successful, False otherwise
        """
        if event_type not in self.hooks:
            return False
        
        script_path = str(Path(script_path).expanduser().resolve())
        
        if script_path in self.hooks[event_type]:
            self.hooks[event_type].remove(script_path)
            logger.info(f"Unregistered script for {event_type}: {script_path}")
            return True
        
        return False
    
    def register_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Register a Python callback function
        
        Args:
            event_type: Event type
            callback: Callback function
            
        Returns:
            True if successful, False otherwise
        """
        if event_type not in self.callbacks:
            logger.error(f"Invalid event type: {event_type}")
            return False
        
        if callback not in self.callbacks[event_type]:
            self.callbacks[event_type].append(callback)
            logger.info(f"Registered callback for {event_type}")
            return True
        
        return False
    
    def unregister_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Unregister a callback function
        
        Args:
            event_type: Event type
            callback: Callback function
            
        Returns:
            True if successful, False otherwise
        """
        if event_type not in self.callbacks:
            return False
        
        if callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            logger.info(f"Unregistered callback for {event_type}")
            return True
        
        return False
    
    def trigger(self, event_type: str, event_data: Optional[Dict] = None) -> None:
        """
        Trigger event hooks
        
        Args:
            event_type: Event type to trigger
            event_data: Optional event data
        """
        if event_type not in self.hooks:
            logger.error(f"Invalid event type: {event_type}")
            return
        
        if event_data is None:
            event_data = {}
        
        event_data['event'] = event_type
        
        # Execute registered scripts in background threads
        for script_path in self.hooks[event_type]:
            thread = threading.Thread(
                target=ActionHandler.run_custom_script,
                args=(script_path, event_data),
                daemon=True
            )
            thread.start()
        
        # Execute registered callbacks
        for callback in self.callbacks[event_type]:
            try:
                thread = threading.Thread(
                    target=callback,
                    args=(event_data,),
                    daemon=True
                )
                thread.start()
            except Exception as e:
                logger.error(f"Error executing callback for {event_type}: {e}")
    
    def load_from_config(self, config_hooks: Dict[str, List[str]]) -> None:
        """
        Load hooks from configuration
        
        Args:
            config_hooks: Hooks configuration dictionary
        """
        for event_type, scripts in config_hooks.items():
            if event_type in self.hooks:
                for script in scripts:
                    self.register_script(event_type, script)
    
    def get_hooks(self, event_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get registered hooks
        
        Args:
            event_type: Optional event type to filter
            
        Returns:
            Dictionary of hooks
        """
        if event_type:
            return {event_type: self.hooks.get(event_type, [])}
        return self.hooks.copy()
