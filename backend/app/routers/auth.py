from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User

router = APIRouter(tags=["auth"])


class AuthRequest(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str = ""


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    first_name: str

    model_config = {"from_attributes": True}


@router.post("/auth", response_model=UserResponse)
async def authenticate(data: AuthRequest, db: AsyncSession = Depends(get_db)):
    """Register or get existing user by telegram_id."""
    result = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=data.telegram_id,
            username=data.username,
            first_name=data.first_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.username = data.username
        user.first_name = data.first_name
        await db.commit()

    return user
