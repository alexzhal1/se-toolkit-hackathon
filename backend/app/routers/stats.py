from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Flashcard, Material, QuizAttempt

router = APIRouter(tags=["stats"])


class RecentAttempt(BaseModel):
    quiz_id: int
    score: int
    total: int
    completed_at: datetime


class StatsResponse(BaseModel):
    materials_count: int
    flashcards_count: int
    flashcards_due: int
    flashcards_learned: int
    quiz_attempts: int
    quiz_avg_pct: float
    recent_attempts: list[RecentAttempt]


@router.get("/users/{user_id}/stats", response_model=StatsResponse)
async def get_user_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)

    materials_count = (
        await db.execute(select(func.count(Material.id)).where(Material.user_id == user_id))
    ).scalar_one()

    fc_base = select(func.count(Flashcard.id)).join(
        Material, Material.id == Flashcard.material_id
    ).where(Material.user_id == user_id)
    flashcards_count = (await db.execute(fc_base)).scalar_one()
    flashcards_due = (
        await db.execute(fc_base.where(Flashcard.next_review_at <= now))
    ).scalar_one()
    flashcards_learned = (
        await db.execute(fc_base.where(Flashcard.repetitions >= 2))
    ).scalar_one()

    attempts_result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.completed_at.desc())
    )
    attempts = attempts_result.scalars().all()
    total_attempts = len(attempts)
    if total_attempts > 0:
        pct_sum = sum((a.score / a.total) * 100 for a in attempts if a.total > 0)
        avg = pct_sum / total_attempts
    else:
        avg = 0.0

    return StatsResponse(
        materials_count=materials_count,
        flashcards_count=flashcards_count,
        flashcards_due=flashcards_due,
        flashcards_learned=flashcards_learned,
        quiz_attempts=total_attempts,
        quiz_avg_pct=round(avg, 1),
        recent_attempts=[
            RecentAttempt(
                quiz_id=a.quiz_id,
                score=a.score,
                total=a.total,
                completed_at=a.completed_at,
            )
            for a in attempts[:10]
        ],
    )
