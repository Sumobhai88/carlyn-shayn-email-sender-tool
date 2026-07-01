"""
Authentication service for Google OAuth
"""
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional
import logging

from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    
    @staticmethod
    async def verify_google_token(token: str) -> Optional[dict]:
        """Verify Google OAuth token and return user info"""
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Token is valid, return user info
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture')
            }
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            return None
    
    @staticmethod
    def get_or_create_user(db: Session, user_info: dict) -> User:
        """Get existing user or create new one"""
        # Check if user exists
        user = db.query(User).filter(User.google_id == user_info['google_id']).first()
        
        if user:
            # Update last login
            user.last_login = datetime.utcnow()
            user.name = user_info.get('name')
            user.picture = user_info.get('picture')
            db.commit()
            db.refresh(user)
            return user
        
        # Create new user
        user = User(
            google_id=user_info['google_id'],
            email=user_info['email'],
            name=user_info.get('name'),
            picture=user_info.get('picture'),
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def create_access_token(user_id: int) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return int(user_id)
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """Get current user from token"""
        user_id = AuthService.verify_token(token)
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
