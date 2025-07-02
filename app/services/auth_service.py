"""Authentication service for user management"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.models.user import User
from app.core.config import settings
from app.core.logging import app_logger

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service for authentication and user management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            stmt = select(User).where(User.email == email)
            result = self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            app_logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            stmt = select(User).where(User.username == username)
            result = self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            app_logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = self.get_user_by_email(email)
            if not user:
                return None
            
            if not self.verify_password(password, user.hashed_password):
                return None
            
            if not user.is_active:
                app_logger.warning(f"Inactive user attempted login: {email}")
                return None
            
            app_logger.info(f"User authenticated successfully: {email}")
            return user
        except Exception as e:
            app_logger.error(f"Error authenticating user {email}: {e}")
            return None
    
    def create_user(self, username: str, email: str, password: str, full_name: str = None) -> Optional[User]:
        """Create a new user"""
        try:
            # Check if user already exists
            if self.get_user_by_email(email):
                app_logger.warning(f"Attempted to create user with existing email: {email}")
                return None
            
            if self.get_user_by_username(username):
                app_logger.warning(f"Attempted to create user with existing username: {username}")
                return None
            
            # Create new user
            hashed_password = self.get_password_hash(password)
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                is_active=True
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            app_logger.info(f"Created new user: {email}")
            return user
        except Exception as e:
            app_logger.error(f"Error creating user {email}: {e}")
            self.db.rollback()
            return None
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError as e:
            app_logger.warning(f"Invalid token: {e}")
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            email: str = payload.get("sub")
            if not email:
                return None
            
            user = self.get_user_by_email(email)
            return user
        except Exception as e:
            app_logger.error(f"Error getting current user from token: {e}")
            return None
    
    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user information"""
        try:
            user = self.db.get(User, user_id)
            if not user:
                return None
            
            for key, value in user_data.items():
                if hasattr(user, key) and key != 'id':
                    setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            app_logger.info(f"Updated user: {user.email}")
            return user
        except Exception as e:
            app_logger.error(f"Error updating user {user_id}: {e}")
            self.db.rollback()
            return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.db.get(User, user_id)
            if not user:
                return False
            
            if not self.verify_password(old_password, user.hashed_password):
                app_logger.warning(f"Invalid old password for user {user_id}")
                return False
            
            user.hashed_password = self.get_password_hash(new_password)
            self.db.commit()
            app_logger.info(f"Password changed for user: {user.email}")
            return True
        except Exception as e:
            app_logger.error(f"Error changing password for user {user_id}: {e}")
            self.db.rollback()
            return False