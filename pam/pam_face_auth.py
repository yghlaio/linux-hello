#!/usr/bin/env python3
"""
PAM Face Authentication Module
Python-based PAM module for face recognition authentication
"""

import sys
import syslog
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Database
from face_auth import FaceAuthenticator
from config import get_config


def pam_sm_authenticate(pamh, flags, argv):
    """
    PAM authentication function
    
    Args:
        pamh: PAM handle
        flags: PAM flags
        argv: Module arguments
        
    Returns:
        PAM result code
    """
    try:
        # Get username
        user = pamh.get_user(None)
        
        if not user:
            syslog.syslog(syslog.LOG_ERR, "face_auth: No username provided")
            return pamh.PAM_USER_UNKNOWN
        
        syslog.syslog(syslog.LOG_INFO, f"face_auth: Authenticating user {user}")
        
        # Initialize face authenticator
        config = get_config()
        db = Database(config.get('database.path'))
        authenticator = FaceAuthenticator(db)
        
        # Check if user is enrolled
        db_user = db.get_user(user)
        if not db_user:
            syslog.syslog(syslog.LOG_INFO, f"face_auth: User {user} not enrolled")
            return pamh.PAM_USER_UNKNOWN
        
        # Attempt face authentication
        timeout = 15  # 15 second timeout for PAM
        success, username, confidence = authenticator.authenticate(
            timeout=timeout,
            show_preview=False  # No preview in PAM mode
        )
        
        if success and username == user:
            syslog.syslog(syslog.LOG_INFO, 
                         f"face_auth: Authentication successful for {user} (confidence: {confidence:.2f})")
            return pamh.PAM_SUCCESS
        else:
            syslog.syslog(syslog.LOG_WARNING, 
                         f"face_auth: Authentication failed for {user}")
            return pamh.PAM_AUTH_ERR
            
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, f"face_auth: Error during authentication: {e}")
        return pamh.PAM_AUTH_ERR


def pam_sm_setcred(pamh, flags, argv):
    """PAM set credentials function"""
    return pamh.PAM_SUCCESS


def pam_sm_acct_mgmt(pamh, flags, argv):
    """PAM account management function"""
    return pamh.PAM_SUCCESS


def pam_sm_open_session(pamh, flags, argv):
    """PAM open session function"""
    return pamh.PAM_SUCCESS


def pam_sm_close_session(pamh, flags, argv):
    """PAM close session function"""
    return pamh.PAM_SUCCESS


def pam_sm_chauthtok(pamh, flags, argv):
    """PAM change authentication token function"""
    return pamh.PAM_SUCCESS
