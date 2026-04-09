from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Flashcard, Material, User
from app.services.ai_service import generate_flashcards

router = APIRouter(tags=["flashcards"])


class FlashcardResponse(BaseModel):
    id: int
    material_id: int
    front: str
    back: str

    model_config = {"from_attributes": True}


class ReviewFlashcardResponse(FlashcardResponse):
    material_title: str
    ease_factor: float
    interval_days: int
    repetitions: int


class ReviewSubmit(BaseModel):
    quality: int  # 0..5 (SM-2 grading)


@router.get("/materials/{material_id}/flashcards", response_model=list[FlashcardResponse])
async def get_flashcards(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Flashcard, Material)
        .join(Material, Material.id == Flashcard.material_id)
        .where(Flashcard.material_id == material_id, Material.user_id == current_user.id)
    )
    rows = result.all()
    return [card for card, _ in rows]


@router.post("/materials/{material_id}/flashcards", response_model=list[FlashcardResponse])
async def create_flashcards(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Material).where(
            Material.id == material_id, Material.user_id == current_user.id
        )
    )
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Delete existing flashcards for this material
    existing = await db.execute(select(Flashcard).where(Flashcard.material_id == material_id))
    for card in existing.scalars().all():
        await db.delete(card)

    cards_data = await generate_flashcards(material.content, material.explanation)

    cards = []
    for card_data in cards_data:
        card = Flashcard(
            material_id=material_id,
            front=card_data.get("front", ""),
            back=card_data.get("back", ""),
        )
        db.add(card)
        cards.append(card)

    await db.commit()
    for card in cards:
        await db.refresh(card)

    return cards


@router.get("/flashcards/review", response_model=list[ReviewFlashcardResponse])
async def get_review_queue(
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return flashcards owned by user that are due for review (SM-2)."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Flashcard, Material.title)
        .join(Material, Material.id == Flashcard.material_id)
        .where(Material.user_id == current_user.id, Flashcard.next_review_at <= now)
        .order_by(Flashcard.next_review_at.asc())
        .limit(limit)
    )
    rows = result.all()
    return [
        ReviewFlashcardResponse(
            id=card.id,
            material_id=card.material_id,
            front=card.front,
            back=card.back,
            material_title=title,
            ease_factor=card.ease_factor,
            interval_days=card.interval_days,
            repetitions=card.repetitions,
        )
        for card, title in rows
    ]


@router.post("/flashcards/{card_id}/review", response_model=FlashcardResponse)
async def submit_review(
    card_id: int,
    payload: ReviewSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Apply SM-2 algorithm to update card scheduling.

    Quality: 0..5
      0..2 — failed (reset repetitions, review again tomorrow)
      3..5 — passed (advance interval)
    """
    result = await db.execute(
        select(Flashcard)
        .join(Material, Material.id == Flashcard.material_id)
        .where(Flashcard.id == card_id, Material.user_id == current_user.id)
    )
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    q = max(0, min(5, int(payload.quality)))

    if q < 3:
        card.repetitions = 0
        card.interval_days = 1
    else:
        if card.repetitions == 0:
            card.interval_days = 1
        elif card.repetitions == 1:
            card.interval_days = 6
        else:
            card.interval_days = max(1, round(card.interval_days * card.ease_factor))
        card.repetitions += 1

    new_ef = card.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    card.ease_factor = max(1.3, new_ef)
    card.next_review_at = datetime.now(timezone.utc) + timedelta(days=card.interval_days)

    await db.commit()
    await db.refresh(card)
    return card


class ReviewStatsResponse(BaseModel):
    due_now: int
    total: int
    learned: int  # repetitions >= 2


@router.get("/flashcards/review/stats", response_model=ReviewStatsResponse)
async def review_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    base = select(func.count(Flashcard.id)).join(
        Material, Material.id == Flashcard.material_id
    ).where(Material.user_id == current_user.id)
    total = (await db.execute(base)).scalar_one()
    due = (await db.execute(base.where(Flashcard.next_review_at <= now))).scalar_one()
    learned = (await db.execute(base.where(Flashcard.repetitions >= 2))).scalar_one()
    return ReviewStatsResponse(due_now=due, total=total, learned=learned)
