#!/usr/bin/env python3
"""
Security modes for face authentication
Implements fast, balanced, and secure authentication modes
"""

from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class SecurityMode:
    """Security mode configuration"""
    
    MODES = {
        'fast': {
            'tolerance': 0.7,
            'min_matches': 1,
            'description': 'Quick authentication, less secure'
        },
        'balanced': {
            'tolerance': 0.6,
            'min_matches': 2,
            'description': 'Balanced speed and security (recommended)'
        },
        'secure': {
            'tolerance': 0.5,
            'min_matches': 3,
            'description': 'Slower but more secure authentication'
        }
    }
    
    @staticmethod
    def get_mode_config(mode: str) -> dict:
        """
        Get configuration for security mode
        
        Args:
            mode: Security mode name
            
        Returns:
            Mode configuration dict
        """
        if mode not in SecurityMode.MODES:
            logger.warning(f"Invalid security mode '{mode}', using 'balanced'")
            mode = 'balanced'
        
        return SecurityMode.MODES[mode]
    
    @staticmethod
    def validate_authentication(matches: list, mode: str) -> Tuple[bool, float]:
        """
        Validate authentication based on security mode
        
        Args:
            matches: List of match results (True/False)
            mode: Security mode
            
        Returns:
            Tuple of (success, confidence)
        """
        config = SecurityMode.get_mode_config(mode)
        min_matches = config['min_matches']
        
        # Count successful matches
        match_count = sum(1 for m in matches if m)
        
        if match_count >= min_matches:
            # Calculate confidence based on match ratio
            confidence = match_count / len(matches) if matches else 0.0
            return True, confidence
        
        return False, 0.0
    
    @staticmethod
    def get_tolerance(mode: str) -> float:
        """Get tolerance value for security mode"""
        config = SecurityMode.get_mode_config(mode)
        return config['tolerance']
    
    @staticmethod
    def list_modes() -> dict:
        """List all available security modes"""
        return SecurityMode.MODES.copy()
