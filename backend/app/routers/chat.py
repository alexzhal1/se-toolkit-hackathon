from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import ChatMessage, Material, User
from app.services.ai_service import chat_with_context

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    material_id: int
    role: str
    content: str

    model_config = {"from_attributes": True}


@router.get("/materials/{material_id}/chat", response_model=list[ChatMessageResponse])
async def get_chat_history(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatMessage, Material)
        .join(Material, Material.id == ChatMessage.material_id)
        .where(ChatMessage.material_id == material_id, Material.user_id == current_user.id)
        .order_by(ChatMessage.created_at)
    )
    return [msg for msg, _ in result.all()]


@router.post("/materials/{material_id}/chat", response_model=ChatMessageResponse)
async def send_message(
    material_id: int,
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get material (ensure user owns it)
    result = await db.execute(
        select(Material).where(
            Material.id == material_id, Material.user_id == current_user.id
        )
    )
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Get chat history
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.material_id == material_id)
        .order_by(ChatMessage.created_at)
    )
    history = [{"role": m.role, "content": m.content} for m in result.scalars().all()]

    # Save user message
    user_msg = ChatMessage(material_id=material_id, role="user", content=data.message)
    db.add(user_msg)
    await db.commit()

    # Get AI response
    ai_response = await chat_with_context(
        material_content=material.content,
        material_explanation=material.explanation,
        history=history,
        user_message=data.message,
    )

    # Save assistant message
    assistant_msg = ChatMessage(material_id=material_id, role="assistant", content=ai_response)
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    return assistant_msg


@router.delete("/materials/{material_id}/chat")
async def clear_chat(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatMessage, Material)
        .join(Material, Material.id == ChatMessage.material_id)
        .where(ChatMessage.material_id == material_id, Material.user_id == current_user.id)
    )
    for msg, _ in result.all():
        await db.delete(msg)
    await db.commit()
    return {"ok": True}
