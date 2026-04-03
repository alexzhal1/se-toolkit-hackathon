from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Material
from app.services.ai_service import explain_material

router = APIRouter(tags=["materials"])


class MaterialCreate(BaseModel):
    user_id: int
    title: str = "Untitled"
    content: str


class MaterialResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    explanation: str | None
    created_at: str

    model_config = {"from_attributes": True}


@router.get("/materials", response_model=list[MaterialResponse])
async def list_materials(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Material).where(Material.user_id == user_id).order_by(Material.created_at.desc())
    )
    return result.scalars().all()


@router.post("/materials", response_model=MaterialResponse)
async def create_material(data: MaterialCreate, db: AsyncSession = Depends(get_db)):
    material = Material(user_id=data.user_id, title=data.title, content=data.content)
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material


@router.get("/materials/{material_id}", response_model=MaterialResponse)
async def get_material(material_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.post("/materials/{material_id}/explain", response_model=MaterialResponse)
async def explain(material_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    explanation = await explain_material(material.content)
    material.explanation = explanation
    await db.commit()
    await db.refresh(material)
    return material


@router.delete("/materials/{material_id}")
async def delete_material(material_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    await db.delete(material)
    await db.commit()
    return {"ok": True}
