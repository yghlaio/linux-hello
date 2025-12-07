#!/usr/bin/env python3
"""
Configuration management for Face Authentication System
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for face authentication system"""
    
    DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.yaml"
    USER_CONFIG_PATH = Path.home() / ".config" / "face-auth" / "config.yaml"
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Optional custom config file path
        """
        self.config_path = config_path or self._get_config_path()
        self.config: Dict[str, Any] = {}
        self.load()
    
    def _get_config_path(self) -> Path:
        """Get the configuration file path (user config or default)"""
        if self.USER_CONFIG_PATH.exists():
            return self.USER_CONFIG_PATH
        return self.DEFAULT_CONFIG_PATH
    
    def load(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"Loaded configuration from {self.config_path}")
            self._expand_paths()
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            self.config = {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise
    
    def _expand_paths(self) -> None:
        """Expand ~ and environment variables in path configurations"""
        if 'database' in self.config and 'path' in self.config['database']:
            self.config['database']['path'] = os.path.expanduser(
                self.config['database']['path']
            )
        
        if 'logging' in self.config and 'file' in self.config['logging']:
            self.config['logging']['file'] = os.path.expanduser(
                self.config['logging']['file']
            )
    
    def save(self, path: Optional[Path] = None) -> None:
        """
        Save configuration to file
        
        Args:
            path: Optional custom save path
        """
        save_path = path or self.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Saved configuration to {save_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'camera.device_id')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'camera.device_id')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"Set config {key} = {value}")
    
    def create_user_config(self) -> None:
        """Create user configuration file from default"""
        self.USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.USER_CONFIG_PATH.exists():
            # Copy default config to user config
            with open(self.DEFAULT_CONFIG_PATH, 'r') as src:
                with open(self.USER_CONFIG_PATH, 'w') as dst:
                    dst.write(src.read())
            logger.info(f"Created user config at {self.USER_CONFIG_PATH}")
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        # Database directory
        db_path = Path(self.get('database.path', '~/.local/share/face-auth/face_auth.db'))
        db_path = Path(os.path.expanduser(str(db_path)))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Log directory
        log_path = Path(self.get('logging.file', '~/.local/share/face-auth/face_auth.log'))
        log_path = Path(os.path.expanduser(str(log_path)))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.debug("Ensured all required directories exist")


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> None:
    """Reload global configuration"""
    global _config
    _config = Config()
