import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from sqlalchemy import select

from app.config import settings
from app.database import async_session
from app.models import Material, User

logger = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
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

    await message.answer(
        f"👋 Welcome to StudyBot, {message.from_user.first_name}!\n\n"
        "I help you learn by explaining study materials, creating flashcards, and quizzes.\n\n"
        "📝 Just send me any text and I'll save it as study material.\n"
        f"🌐 Open the web app: {settings.TELEGRAM_MINI_APP_URL}\n\n"
        "Commands:\n"
        "/materials — List your materials\n"
        "/help — Show this message"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📚 **StudyBot Help**\n\n"
        "Just send me any text and I'll save it as study material.\n\n"
        f"🌐 Web app: {settings.TELEGRAM_MINI_APP_URL}\n\n"
        "Commands:\n"
        "/start — Start the bot\n"
        "/materials — List your materials\n"
        "/help — Show this help",
        parse_mode="Markdown",
    )


@dp.message(Command("materials"))
async def cmd_materials(message: types.Message):
    async with async_session() as db:
        result = await db.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = result.scalar_one_or_none()
        if not user:
            await message.answer("Please /start first.")
            return

        result = await db.execute(
            select(Material).where(Material.user_id == user.id).order_by(Material.created_at.desc()).limit(10)
        )
        materials = result.scalars().all()

    if not materials:
        await message.answer("You have no materials yet. Send me some text to get started!")
        return

    lines = ["📚 **Your Materials:**\n"]
    for m in materials:
        title = m.title[:40]
        lines.append(f"• {title} (ID: {m.id})")

    lines.append(f"\n🌐 Open web app to study: {settings.TELEGRAM_MINI_APP_URL}")
    await message.answer("\n".join(lines), parse_mode="Markdown")


@dp.message(F.text)
async def handle_text(message: types.Message):
    """Save any text message as a new material."""
    text = message.text.strip()
    if len(text) < 10:
        await message.answer("Please send a longer text (at least 10 characters) to save as study material.")
        return

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

        # Use first line or first 50 chars as title
        title = text.split("\n")[0][:50]
        material = Material(user_id=user.id, title=title, content=text)
        db.add(material)
        await db.commit()
        await db.refresh(material)

    await message.answer(
        f"✅ Material saved: **{material.title}**\n\n"
        f"🌐 Open the web app to study it: {settings.TELEGRAM_MINI_APP_URL}",
        parse_mode="Markdown",
    )


async def start_bot():
    """Start the bot polling."""
    logger.info("Starting Telegram bot...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error("Bot error: %s", e)
