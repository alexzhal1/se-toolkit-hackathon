from datetime import datetime, timedelta, timezone

import jwt
import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import User

router = APIRouter(tags=["auth"])

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 24 hours


# --------------- Pydantic schemas ---------------

class RegisterRequest(BaseModel):
    email: str
    login: str
    password: str


class LoginRequest(BaseModel):
    login: str
    password: str


class AuthResponse(BaseModel):
    user: "UserResponse"
    token: str


class UserResponse(BaseModel):
    id: int
    email: str
    login: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --------------- Helpers ---------------

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _create_jwt(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


# --------------- Routes ---------------

@router.post("/auth/register", response_model=AuthResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user with email, login, and password."""
    # Check duplicates
    existing = await db.execute(
        select(User).where((User.email == data.email) | (User.login == data.login))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email or login already exists")

    user = User(
        email=data.email,
        login=data.login,
        hashed_password=_hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = _create_jwt(user.id)
    return AuthResponse(user=user, token=token)


@router.post("/auth/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with login (or email) and password. Returns user + JWT."""
    result = await db.execute(
        select(User).where((User.login == data.login) | (User.email == data.login))
    )
    user = result.scalar_one_or_none()
    if not user or not _verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = _create_jwt(user.id)
    return AuthResponse(user=user, token=token)
