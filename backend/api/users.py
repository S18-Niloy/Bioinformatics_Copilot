from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
import logging
import re
from jose import JWTError, jwt

from database import get_db
from models.user import User
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    MAX_PASSWORD_LENGTH,
    SECRET_KEY,
    ALGORITHM,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])


# ----------------------
# Request Schemas
# ----------------------
class RegisterIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=MAX_PASSWORD_LENGTH)

    @validator("username")
    def username_alphanumeric(cls, v):
        """Validate username contains only alphanumeric, underscores, and hyphens."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username must contain only alphanumeric characters, underscores, and hyphens")
        return v

    @validator("password")
    def password_strength(cls, v):
        """Validate password has minimum security requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*" for c in v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*)")
        return v


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds


# ----------------------
# REGISTER
# ----------------------
@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    """Register a new user with validation and secure password hashing."""
    # Check if user already exists
    if db.query(User).filter(User.username == body.username).first():
        logger.warning(f"Registration attempt with existing username: {body.username}")
        raise HTTPException(status_code=400, detail="Username already taken")

    try:
        # Create user
        user = User(
            username=body.username,
            hashed_password=hash_password(body.password)
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User registered successfully: {user.username}")

        # Generate tokens
        access_token = create_access_token({"sub": user.username})
        refresh_token = create_refresh_token({"sub": user.username})

        return TokenOut(access_token=access_token, refresh_token=refresh_token)
        
    except ValueError as e:
        logger.error(f"Validation error during registration: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Registration failed")


# ----------------------
# LOGIN
# ----------------------
@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    """Login user and return access and refresh tokens."""
    user = db.query(User).filter(User.username == body.username).first()

    if not user or not verify_password(body.password, user.hashed_password):
        # Don't leak whether user exists
        logger.warning(f"Failed login attempt for user: {body.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {body.username}")
        raise HTTPException(status_code=403, detail="User account is inactive")

    # Generate tokens
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    
    logger.info(f"User logged in successfully: {user.username}")

    return TokenOut(access_token=access_token, refresh_token=refresh_token)


# ----------------------
# REFRESH TOKEN
# ----------------------
@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token"
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        
        if not username or token_type != "refresh":
            raise cred_exc
    except JWTError:
        raise cred_exc
    
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise cred_exc
    
    access_token = create_access_token({"sub": user.username})
    logger.info(f"Access token refreshed for user: {user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 900
    }


# ----------------------
# CURRENT USER
# ----------------------
@router.get("/me")
def me(user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at,
    }