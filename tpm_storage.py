#!/usr/bin/env python3
"""
TPM (Trusted Platform Module) storage support
Stores encryption keys in TPM if available, falls back to file storage
"""

import os
import logging
from pathlib import Path
from typing import Optional
import subprocess

logger = logging.getLogger(__name__)


class TPMStorage:
    """Handle TPM storage for encryption keys"""
    
    def __init__(self):
        """Initialize TPM storage"""
        self.tpm_available = self._check_tpm_available()
        self.tpm_index = 0x1500000  # TPM NV index for our key
        
    def _check_tpm_available(self) -> bool:
        """
        Check if TPM is available on the system
        
        Returns:
            True if TPM is available and accessible
        """
        try:
            # Check for tpm2-tools
            result = subprocess.run(
                ['which', 'tpm2_nvread'],
                capture_output=True,
                timeout=2
            )
            
            if result.returncode != 0:
                logger.info("TPM tools not found, using file-based storage")
                return False
            
            # Check if TPM device exists
            if not os.path.exists('/dev/tpm0') and not os.path.exists('/dev/tpmrm0'):
                logger.info("TPM device not found, using file-based storage")
                return False
            
            logger.info("TPM available, will use TPM storage for encryption keys")
            return True
            
        except Exception as e:
            logger.warning(f"Error checking TPM availability: {e}")
            return False
    
    def store_key(self, key: bytes, fallback_path: Path) -> bool:
        """
        Store encryption key in TPM or fallback to file
        
        Args:
            key: Encryption key bytes
            fallback_path: Path to use if TPM not available
            
        Returns:
            True if successful
        """
        if self.tpm_available:
            return self._store_in_tpm(key)
        else:
            return self._store_in_file(key, fallback_path)
    
    def retrieve_key(self, fallback_path: Path) -> Optional[bytes]:
        """
        Retrieve encryption key from TPM or file
        
        Args:
            fallback_path: Path to use if TPM not available
            
        Returns:
            Encryption key bytes or None
        """
        if self.tpm_available:
            key = self._retrieve_from_tpm()
            if key is not None:
                return key
            logger.warning("Failed to retrieve from TPM, trying file fallback")
        
        return self._retrieve_from_file(fallback_path)
    
    def _store_in_tpm(self, key: bytes) -> bool:
        """
        Store key in TPM NV RAM
        
        Args:
            key: Encryption key
            
        Returns:
            True if successful
        """
        try:
            # Define NV index if it doesn't exist
            subprocess.run(
                [
                    'tpm2_nvdefine',
                    hex(self.tpm_index),
                    '-s', str(len(key)),
                    '-a', 'ownerread|ownerwrite'
                ],
                capture_output=True,
                timeout=5
            )
            
            # Write key to TPM
            result = subprocess.run(
                ['tpm2_nvwrite', hex(self.tpm_index)],
                input=key,
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info(f"Encryption key stored in TPM at index {hex(self.tpm_index)}")
                return True
            else:
                logger.error(f"Failed to write to TPM: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing key in TPM: {e}")
            return False
    
    def _retrieve_from_tpm(self) -> Optional[bytes]:
        """
        Retrieve key from TPM NV RAM
        
        Returns:
            Key bytes or None
        """
        try:
            result = subprocess.run(
                ['tpm2_nvread', hex(self.tpm_index)],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info("Retrieved encryption key from TPM")
                return result.stdout
            else:
                logger.warning(f"Failed to read from TPM: {result.stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving key from TPM: {e}")
            return None
    
    def _store_in_file(self, key: bytes, path: Path) -> bool:
        """
        Store key in file (fallback)
        
        Args:
            key: Encryption key
            path: File path
            
        Returns:
            True if successful
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'wb') as f:
                f.write(key)
            os.chmod(path, 0o600)
            logger.info(f"Encryption key stored in file: {path}")
            return True
        except Exception as e:
            logger.error(f"Error storing key in file: {e}")
            return False
    
    def _retrieve_from_file(self, path: Path) -> Optional[bytes]:
        """
        Retrieve key from file (fallback)
        
        Args:
            path: File path
            
        Returns:
            Key bytes or None
        """
        try:
            if path.exists():
                with open(path, 'rb') as f:
                    key = f.read()
                logger.info(f"Retrieved encryption key from file: {path}")
                return key
            return None
        except Exception as e:
            logger.error(f"Error retrieving key from file: {e}")
            return None
    
    def delete_key(self, fallback_path: Path) -> bool:
        """
        Delete encryption key from TPM and/or file
        
        Args:
            fallback_path: File path
            
        Returns:
            True if successful
        """
        success = True
        
        if self.tpm_available:
            try:
                subprocess.run(
                    ['tpm2_nvundefine', hex(self.tpm_index)],
                    capture_output=True,
                    timeout=5
                )
                logger.info("Deleted encryption key from TPM")
            except Exception as e:
                logger.error(f"Error deleting key from TPM: {e}")
                success = False
        
        if fallback_path.exists():
            try:
                fallback_path.unlink()
                logger.info(f"Deleted encryption key file: {fallback_path}")
            except Exception as e:
                logger.error(f"Error deleting key file: {e}")
                success = False
        
        return success
