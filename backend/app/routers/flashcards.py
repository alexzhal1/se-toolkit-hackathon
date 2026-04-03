from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Flashcard, Material
from app.services.ai_service import generate_flashcards

router = APIRouter(tags=["flashcards"])


class FlashcardResponse(BaseModel):
    id: int
    material_id: int
    front: str
    back: str

    model_config = {"from_attributes": True}


@router.get("/materials/{material_id}/flashcards", response_model=list[FlashcardResponse])
async def get_flashcards(material_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Flashcard).where(Flashcard.material_id == material_id))
    return result.scalars().all()


@router.post("/materials/{material_id}/flashcards", response_model=list[FlashcardResponse])
async def create_flashcards(material_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Material).where(Material.id == material_id))
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
