import json
import logging

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

MODEL = "deepseek-chat"


async def explain_material(content: str) -> str:
    """Generate a detailed explanation of the study material."""
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert tutor. The user will provide study material. "
                    "Your task is to explain it in a clear, structured, and detailed way. "
                    "Use headings, bullet points, and examples where appropriate. "
                    "Break down complex concepts into simpler parts. "
                    "All responses must be in English."
                ),
            },
            {
                "role": "user",
                "content": f"Please explain the following study material in detail:\n\n{content}",
            },
        ],
        temperature=0.7,
        max_tokens=4000,
    )
    return response.choices[0].message.content


async def generate_flashcards(content: str, explanation: str | None = None) -> list[dict]:
    """Generate flashcards from the study material."""
    context = content
    if explanation:
        context += f"\n\nExplanation:\n{explanation}"

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert tutor creating flashcards for studying. "
                    "Generate 10-15 flashcards from the provided material. "
                    "Each flashcard should have a 'front' (question or term) and 'back' (answer or definition). "
                    "Cover the key concepts thoroughly. "
                    "All content must be in English. "
                    "Return ONLY a JSON array with no extra text, like: "
                    '[{"front": "...", "back": "..."}, ...]'
                ),
            },
            {
                "role": "user",
                "content": f"Create flashcards from this material:\n\n{context}",
            },
        ],
        temperature=0.7,
        max_tokens=4000,
    )

    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = lines[1:]  # remove opening ```json or ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines)

    try:
        cards = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Failed to parse flashcards JSON: %s", raw[:200])
        cards = [{"front": "Error", "back": "AI returned invalid format. Please try again."}]

    return cards
