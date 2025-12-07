#!/usr/bin/env python3
"""
Database models for Face Authentication System
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    """User model for storing enrolled users"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    face_encodings = Column(Text, nullable=False)  # Encrypted JSON array of face encodings
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)
    enabled = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User(username='{self.username}', enrolled_at='{self.enrolled_at}')>"


class AuthenticationLog(Base):
    """Log of authentication attempts"""
    __tablename__ = 'auth_logs'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=True)
    success = Column(Boolean, nullable=False)
    confidence = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(50), nullable=False)  # 'login', 'unlock', 'presence_check'
    
    def __repr__(self):
        return f"<AuthLog(username='{self.username}', success={self.success}, timestamp='{self.timestamp}')>"


class PresenceLog(Base):
    """Log of presence/absence events"""
    __tablename__ = 'presence_logs'
    
    id = Column(Integer, primary_key=True)
    event = Column(String(50), nullable=False)  # 'present', 'absent'
    username = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action_taken = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<PresenceLog(event='{self.event}', timestamp='{self.timestamp}')>"


class Database:
    """Database manager for face authentication system"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = os.path.expanduser("~/.local/share/face-auth/face_auth.db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption key
        self.key_path = self.db_path.parent / ".encryption_key"
        self.cipher = self._get_cipher()
        
        # Create database engine
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        logger.info(f"Database initialized at {self.db_path}")
    
    def _get_cipher(self) -> Fernet:
        """Get or create encryption cipher"""
        if self.key_path.exists():
            with open(self.key_path, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_path, 'wb') as f:
                f.write(key)
            # Secure the key file
            os.chmod(self.key_path, 0o600)
        
        return Fernet(key)
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def encrypt_encodings(self, encodings: List) -> str:
        """
        Encrypt face encodings
        
        Args:
            encodings: List of face encoding arrays
            
        Returns:
            Encrypted string
        """
        # Convert numpy arrays to lists for JSON serialization
        encodings_list = [enc.tolist() for enc in encodings]
        json_str = json.dumps(encodings_list)
        encrypted = self.cipher.encrypt(json_str.encode())
        return encrypted.decode()
    
    def decrypt_encodings(self, encrypted_str: str) -> List:
        """
        Decrypt face encodings
        
        Args:
            encrypted_str: Encrypted encodings string
            
        Returns:
            List of face encoding arrays
        """
        import numpy as np
        decrypted = self.cipher.decrypt(encrypted_str.encode())
        encodings_list = json.loads(decrypted.decode())
        return [np.array(enc) for enc in encodings_list]
    
    def add_user(self, username: str, face_encodings: List) -> User:
        """
        Add a new user with face encodings
        
        Args:
            username: Username
            face_encodings: List of face encoding arrays
            
        Returns:
            Created User object
        """
        session = self.get_session()
        try:
            encrypted_encodings = self.encrypt_encodings(face_encodings)
            user = User(
                username=username,
                face_encodings=encrypted_encodings
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Added user: {username}")
            return user
        finally:
            session.close()
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User object or None
        """
        session = self.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            return user
        finally:
            session.close()
    
    def get_all_users(self) -> List[User]:
        """
        Get all enrolled users
        
        Returns:
            List of User objects
        """
        session = self.get_session()
        try:
            users = session.query(User).filter_by(enabled=True).all()
            return users
        finally:
            session.close()
    
    def remove_user(self, username: str) -> bool:
        """
        Remove user by username
        
        Args:
            username: Username
            
        Returns:
            True if user was removed, False otherwise
        """
        session = self.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                session.delete(user)
                session.commit()
                logger.info(f"Removed user: {username}")
                return True
            return False
        finally:
            session.close()
    
    def update_last_seen(self, username: str) -> None:
        """
        Update user's last seen timestamp
        
        Args:
            username: Username
        """
        session = self.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                user.last_seen = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    def log_authentication(self, username: Optional[str], success: bool, 
                          confidence: Optional[float] = None, 
                          event_type: str = 'login') -> None:
        """
        Log authentication attempt
        
        Args:
            username: Username (None if failed to recognize)
            success: Whether authentication succeeded
            confidence: Confidence score
            event_type: Type of authentication event
        """
        session = self.get_session()
        try:
            log = AuthenticationLog(
                username=username,
                success=success,
                confidence=f"{confidence:.2f}" if confidence else None,
                event_type=event_type
            )
            session.add(log)
            session.commit()
        finally:
            session.close()
    
    def log_presence(self, event: str, username: Optional[str] = None, 
                    action_taken: Optional[str] = None) -> None:
        """
        Log presence event
        
        Args:
            event: Event type ('present' or 'absent')
            username: Username if recognized
            action_taken: Action taken in response to event
        """
        session = self.get_session()
        try:
            log = PresenceLog(
                event=event,
                username=username,
                action_taken=action_taken
            )
            session.add(log)
            session.commit()
        finally:
            session.close()
    
    def get_sample_count(self, username: str) -> int:
        """Get number of face samples for a user"""
        user = self.get_user(username)
        if not user:
            return 0
        encodings = self.decrypt_encodings(user.face_encodings)
        return len(encodings)
    
    def get_user_samples(self, username: str) -> Optional[List]:
        """Get all face samples for a user"""
        user = self.get_user(username)
        if not user:
            return None
        return self.decrypt_encodings(user.face_encodings)
    
    def add_sample(self, username: str, encoding) -> bool:
        """Add a single face sample to existing user"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return False
            encodings = self.decrypt_encodings(user.face_encodings)
            encodings.append(encoding)
            user.face_encodings = self.encrypt_encodings(encodings)
            session.commit()
            logger.info(f"Added sample to user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error adding sample: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def remove_sample(self, username: str, index: int) -> bool:
        """Remove a specific face sample from user"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return False
            encodings = self.decrypt_encodings(user.face_encodings)
            if index < 0 or index >= len(encodings) or len(encodings) <= 1:
                return False
            encodings.pop(index)
            user.face_encodings = self.encrypt_encodings(encodings)
            session.commit()
            logger.info(f"Removed sample {index} from user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error removing sample: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_auth_logs(self, limit: int = 100) -> List[AuthenticationLog]:
        """Get recent authentication logs"""
        session = self.get_session()
        try:
            logs = session.query(AuthenticationLog).order_by(
                AuthenticationLog.timestamp.desc()
            ).limit(limit).all()
            return logs
        finally:
            session.close()
    
    def get_presence_logs(self, limit: int = 100) -> List[PresenceLog]:
        """Get recent presence logs"""
        session = self.get_session()
        try:
            logs = session.query(PresenceLog).order_by(
                PresenceLog.timestamp.desc()
            ).limit(limit).all()
            return logs
        finally:
            session.close()

