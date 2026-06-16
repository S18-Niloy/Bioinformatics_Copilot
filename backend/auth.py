from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
import logging

from database import get_db
from models.user import User

logger = logging.getLogger(__name__)

# Security: Use environment variable, raise error if not set in production
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    if os.getenv("ENVIRONMENT") == "production":
        raise ValueError("JWT_SECRET environment variable is required in production")
    logger.warning("JWT_SECRET not set; using insecure default for development only")
    SECRET_KEY = "dev-secret-change-in-production-minimum-32-characters-long"

if len(SECRET_KEY) < 32:
    logger.warning("JWT_SECRET is too short (< 32 characters); consider a longer key")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Reduced from 1440 to 15 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_PASSWORD_LENGTH = 72  # bcrypt limit

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

def hash_password(password: str) -> str:
    """Hash password using argon2 with secure parameters."""
    if not password or len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password must be between 1 and {MAX_PASSWORD_LENGTH} characters")
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    if not password or not hashed_password:
        return False
    try:
        return pwd_context.verify(password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {type(e).__name__}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with short expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token for token renewal."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Validate JWT and return current user."""
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        
        if not username or token_type != "access":
            raise cred_exc
    except JWTError as e:
        logger.debug(f"JWT decode error: {type(e).__name__}")
        raise cred_exc
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise cred_exc
    return user
