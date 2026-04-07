import logging
import secrets

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandObject
from sqlalchemy import select

from app.config import settings
from app.database import async_session
from app.models import Flashcard, LoginToken, Material, User
from app.services.ai_service import explain_material, generate_flashcards, generate_quiz
from app.services.file_parser import extract_text_from_file

logger = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


async def _get_or_create_user(message: types.Message) -> User:
    async with async_session() as db:
        result = await db.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name or "",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await _get_or_create_user(message)
    await message.answer(
        f"👋 Welcome to StudyBot, {message.from_user.first_name}!\n\n"
        "I help you learn by explaining study materials, creating flashcards, and quizzes.\n\n"
        "📝 Send me any text or .pdf/.docx file — I'll save it as study material.\n\n"
        "Commands:\n"
        "/login — Get a login code for the web app\n"
        "/materials — List your materials\n"
        "/explain <id> — Explain a material\n"
        "/cards <id> — Generate flashcards\n"
        "/quiz <id> — Generate a quiz\n"
        "/help — Show this message"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📚 StudyBot Help\n\n"
        "• Send text — saved as study material\n"
        "• Send .pdf/.docx — saved as study material\n"
        f"• Web app: {settings.TELEGRAM_MINI_APP_URL}\n\n"
        "Commands:\n"
        "/login — Get a code to log into the web app\n"
        "/materials — List your materials\n"
        "/explain <id> — Get an AI explanation\n"
        "/cards <id> — Generate flashcards\n"
        "/quiz <id> — Generate a quiz\n"
    )


@dp.message(Command("login"))
async def cmd_login(message: types.Message):
    user = await _get_or_create_user(message)
    token = secrets.token_urlsafe(8)
    async with async_session() as db:
        db.add(LoginToken(token=token, user_id=user.id))
        await db.commit()

    await message.answer(
        f"🔑 Your login code:\n\n`{token}`\n\n"
        f"Open {settings.TELEGRAM_MINI_APP_URL} and paste this code to log in.\n"
        "The code is one-time use.",
        parse_mode="Markdown",
    )


@dp.message(Command("materials"))
async def cmd_materials(message: types.Message):
    user = await _get_or_create_user(message)
    async with async_session() as db:
        result = await db.execute(
            select(Material)
            .where(Material.user_id == user.id)
            .order_by(Material.created_at.desc())
            .limit(20)
        )
        materials = result.scalars().all()

    if not materials:
        await message.answer("You have no materials yet. Send me text or a file to get started!")
        return

    lines = ["📚 Your Materials:\n"]
    for m in materials:
        title = m.title[:50]
        lines.append(f"• [{m.id}] {title}")

    lines.append(f"\n🌐 Open web app: {settings.TELEGRAM_MINI_APP_URL}")
    await message.answer("\n".join(lines))


async def _get_user_material(message: types.Message, material_id: int) -> Material | None:
    user = await _get_or_create_user(message)
    async with async_session() as db:
        result = await db.execute(
            select(Material).where(Material.id == material_id, Material.user_id == user.id)
        )
        return result.scalar_one_or_none()


def _parse_id(command: CommandObject) -> int | None:
    if not command.args:
        return None
    try:
        return int(command.args.strip().split()[0])
    except (ValueError, IndexError):
        return None


@dp.message(Command("explain"))
async def cmd_explain(message: types.Message, command: CommandObject):
    material_id = _parse_id(command)
    if material_id is None:
        await message.answer("Usage: /explain <material_id>\nUse /materials to see IDs.")
        return

    material = await _get_user_material(message, material_id)
    if not material:
        await message.answer("Material not found.")
        return

    await message.answer("🤔 Generating explanation, this may take a minute...")
    try:
        explanation = await explain_material(material.content)
    except Exception as e:
        logger.error("Explain failed: %s", e)
        await message.answer(f"Error: {e}")
        return

    async with async_session() as db:
        result = await db.execute(select(Material).where(Material.id == material_id))
        m = result.scalar_one()
        m.explanation = explanation
        await db.commit()

    # Telegram has a 4096-char limit
    chunks = [explanation[i : i + 4000] for i in range(0, len(explanation), 4000)]
    for chunk in chunks:
        await message.answer(chunk)


@dp.message(Command("cards"))
async def cmd_cards(message: types.Message, command: CommandObject):
    material_id = _parse_id(command)
    if material_id is None:
        await message.answer("Usage: /cards <material_id>")
        return

    material = await _get_user_material(message, material_id)
    if not material:
        await message.answer("Material not found.")
        return

    await message.answer("🎴 Generating flashcards...")
    try:
        cards_data = await generate_flashcards(material.content, material.explanation)
    except Exception as e:
        logger.error("Cards failed: %s", e)
        await message.answer(f"Error: {e}")
        return

    async with async_session() as db:
        existing = await db.execute(select(Flashcard).where(Flashcard.material_id == material_id))
        for c in existing.scalars().all():
            await db.delete(c)
        for c in cards_data:
            db.add(
                Flashcard(
                    material_id=material_id,
                    front=c.get("front", ""),
                    back=c.get("back", ""),
                )
            )
        await db.commit()

    lines = [f"🎴 Generated {len(cards_data)} flashcards:\n"]
    for i, c in enumerate(cards_data, 1):
        lines.append(f"*{i}. {c.get('front', '')}*\n→ {c.get('back', '')}\n")

    text = "\n".join(lines)
    chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        try:
            await message.answer(chunk, parse_mode="Markdown")
        except Exception:
            await message.answer(chunk)


@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message, command: CommandObject):
    from app.models import Quiz, QuizQuestion

    material_id = _parse_id(command)
    if material_id is None:
        await message.answer("Usage: /quiz <material_id>")
        return

    material = await _get_user_material(message, material_id)
    if not material:
        await message.answer("Material not found.")
        return

    await message.answer("📝 Generating quiz, this may take a minute...")
    try:
        questions_data = await generate_quiz(material.content, material.explanation)
    except Exception as e:
        logger.error("Quiz failed: %s", e)
        await message.answer(f"Error: {e}")
        return

    if not questions_data:
        await message.answer("AI returned no questions. Please try again.")
        return

    async with async_session() as db:
        existing = await db.execute(select(Quiz).where(Quiz.material_id == material_id))
        for q in existing.scalars().all():
            await db.delete(q)
        await db.flush()

        quiz = Quiz(material_id=material_id, title=f"Quiz: {material.title}")
        db.add(quiz)
        await db.flush()
        for q in questions_data:
            db.add(
                QuizQuestion(
                    quiz_id=quiz.id,
                    question_text=q.get("question", ""),
                    options=q.get("options", []),
                    correct_answer_index=int(q.get("correct_index", 0)),
                    explanation=q.get("explanation", ""),
                )
            )
        await db.commit()

    lines = [f"📝 Quiz with {len(questions_data)} questions:\n"]
    for i, q in enumerate(questions_data, 1):
        lines.append(f"*{i}. {q.get('question', '')}*")
        for j, opt in enumerate(q.get("options", [])):
            marker = "✅" if j == int(q.get("correct_index", 0)) else "▫️"
            lines.append(f"  {marker} {opt}")
        if q.get("explanation"):
            lines.append(f"  _💡 {q['explanation']}_")
        lines.append("")

    text = "\n".join(lines)
    chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        try:
            await message.answer(chunk, parse_mode="Markdown")
        except Exception:
            await message.answer(chunk)


@dp.message(F.document)
async def handle_document(message: types.Message):
    """Handle .pdf/.docx file uploads."""
    doc = message.document
    filename = doc.file_name or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ("pdf", "docx"):
        await message.answer("Only .pdf and .docx files are supported.")
        return

    user = await _get_or_create_user(message)
    await message.answer("📄 Processing file...")

    try:
        file = await bot.get_file(doc.file_id)
        file_io = await bot.download_file(file.file_path)
        file_bytes = file_io.read()
        content = extract_text_from_file(file_bytes, ext)
    except Exception as e:
        logger.error("File parse failed: %s", e)
        await message.answer(f"Failed to parse file: {e}")
        return

    if not content.strip():
        await message.answer("Could not extract text from the file.")
        return

    title = filename.rsplit(".", 1)[0][:80]
    async with async_session() as db:
        material = Material(user_id=user.id, title=title, content=content)
        db.add(material)
        await db.commit()
        await db.refresh(material)

    await message.answer(
        f"✅ File saved as material [{material.id}]: {material.title}\n\n"
        f"Use:\n/explain {material.id}\n/cards {material.id}\n/quiz {material.id}"
    )


@dp.message(F.text)
async def handle_text(message: types.Message):
    """Save any text message as a new material."""
    text = message.text.strip()
    if text.startswith("/"):
        return  # let command handlers handle it
    if len(text) < 10:
        await message.answer("Please send a longer text (at least 10 characters).")
        return

    user = await _get_or_create_user(message)
    async with async_session() as db:
        title = text.split("\n")[0][:50]
        material = Material(user_id=user.id, title=title, content=text)
        db.add(material)
        await db.commit()
        await db.refresh(material)

    await message.answer(
        f"✅ Material saved [{material.id}]: {material.title}\n\n"
        f"Use:\n/explain {material.id}\n/cards {material.id}\n/quiz {material.id}\n\n"
        f"Or open the web app: {settings.TELEGRAM_MINI_APP_URL}"
    )


async def start_bot():
    """Start the bot polling."""
    logger.info("Starting Telegram bot...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error("Bot error: %s", e)
