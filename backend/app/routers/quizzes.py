from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Material, Quiz, QuizAttempt, QuizQuestion, User
from app.services.ai_service import generate_quiz

router = APIRouter(tags=["quizzes"])


class QuizQuestionResponse(BaseModel):
    id: int
    question_text: str
    options: list[str]
    correct_answer_indices: list[int]
    is_multi: bool
    explanation: str

    model_config = {"from_attributes": True}


class QuizResponse(BaseModel):
    id: int
    material_id: int
    title: str
    created_at: datetime
    questions: list[QuizQuestionResponse]

    model_config = {"from_attributes": True}


async def _load_quiz_for_material(
    material_id: int, user_id: int, db: AsyncSession
) -> Quiz | None:
    result = await db.execute(
        select(Quiz)
        .join(Material, Material.id == Quiz.material_id)
        .where(Quiz.material_id == material_id, Material.user_id == user_id)
        .options(selectinload(Quiz.questions))
        .order_by(Quiz.created_at.desc())
    )
    return result.scalars().first()


@router.get("/materials/{material_id}/quiz", response_model=QuizResponse | None)
async def get_quiz(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = await _load_quiz_for_material(material_id, current_user.id, db)
    return quiz


@router.post("/materials/{material_id}/quiz", response_model=QuizResponse)
async def create_quiz(
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

    # Delete existing quizzes for this material
    existing = await db.execute(select(Quiz).where(Quiz.material_id == material_id))
    for q in existing.scalars().all():
        await db.delete(q)
    await db.flush()

    questions_data = await generate_quiz(material.content, material.explanation)
    if not questions_data:
        raise HTTPException(status_code=500, detail="AI returned no questions")

    quiz = Quiz(material_id=material_id, title=f"Quiz: {material.title}")
    db.add(quiz)
    await db.flush()

    for q in questions_data:
        indices = q.get("correct_indices", [])
        if not isinstance(indices, list):
            indices = [indices]
        indices = [int(i) for i in indices]
        question = QuizQuestion(
            quiz_id=quiz.id,
            question_text=q.get("question", ""),
            options=q.get("options", []),
            correct_answer_indices=indices,
            is_multi=bool(q.get("multi", len(indices) > 1)),
            explanation=q.get("explanation", ""),
        )
        db.add(question)

    await db.commit()

    quiz = await _load_quiz_for_material(material_id, current_user.id, db)
    return quiz


class QuizSubmitPayload(BaseModel):
    answers: dict[str, list[int]]  # {question_id: [selected_indices]}


class QuizSubmitResponse(BaseModel):
    score: int
    total: int
    attempt_id: int


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    quiz_id: int,
    payload: QuizSubmitPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Quiz)
        .join(Material, Material.id == Quiz.material_id)
        .where(Quiz.id == quiz_id, Material.user_id == current_user.id)
        .options(selectinload(Quiz.questions))
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    score = 0
    for q in quiz.questions:
        user_sel = sorted(payload.answers.get(str(q.id), []))
        correct = sorted([int(i) for i in q.correct_answer_indices])
        if user_sel == correct:
            score += 1

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        total=len(quiz.questions),
        answers=payload.answers,
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    return QuizSubmitResponse(score=score, total=len(quiz.questions), attempt_id=attempt.id)
