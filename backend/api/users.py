from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


# ----------------------
# Request Schemas
# ----------------------
class RegisterIn(BaseModel):
    username: str
    password: str


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ----------------------
# REGISTER
# ----------------------
@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    # check existing user
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username taken")

    password = body.password

    # 🔥 FIX: bcrypt max limit protection
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password too long (bcrypt supports max 72 bytes). Please use a shorter password."
        )

    # create user
    u = User(
        username=body.username,
        hashed_password=hash_password(password)
    )

    db.add(u)
    db.commit()
    db.refresh(u)

    token = create_access_token({"sub": u.username})

    return TokenOut(access_token=token)


# ----------------------
# LOGIN
# ----------------------
@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.username == body.username).first()

    if not u or not verify_password(body.password, u.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": u.username})

    return TokenOut(access_token=token)


# ----------------------
# CURRENT USER
# ----------------------
@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username
    }