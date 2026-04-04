import json
import logging

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

MODEL = "deepseek-reasoner"


async def explain_material(content: str) -> str:
    """Generate a detailed explanation of the study material."""
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    "You are an expert tutor. I will provide study material. "
                    "Your task is to explain it in a clear, structured, and detailed way. "
                    "Use headings, bullet points, and examples where appropriate. "
                    "Break down complex concepts into simpler parts. "
                    "All responses must be in English.\n\n"
                    f"Please explain the following study material in detail:\n\n{content}"
                ),
            },
        ],
        max_tokens=20000,
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
                "role": "user",
                "content": (
                    "You are an expert tutor creating flashcards for studying. "
                    "Generate 10-15 flashcards from the provided material. "
                    "Each flashcard should have a 'front' (question or term) and 'back' (answer or definition). "
                    "Cover the key concepts thoroughly. "
                    "All content must be in English. "
                    "Return ONLY a JSON array with no extra text, like: "
                    '[{"front": "...", "back": "..."}, ...]\n\n'
                    f"Create flashcards from this material:\n\n{context}"
                ),
            },
        ],
        max_tokens=20000,
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


async def chat_with_context(
    material_content: str,
    material_explanation: str | None,
    history: list[dict[str, str]],
    user_message: str,
) -> str:
    """Chat about the material with full context."""
    context = material_content
    if material_explanation:
        context += f"\n\n--- AI Explanation ---\n{material_explanation}"

    # deepseek-reasoner: no system role, inject context into first user message
    system_prompt = (
        "You are an expert tutor helping a student understand their study material. "
        "Below is the study material the student uploaded. "
        "Answer their questions based on this material. "
        "If the question is not related to the material, politely steer back. "
        "Be clear, detailed, and use examples when helpful.\n\n"
        f"--- STUDY MATERIAL ---\n{context}\n--- END MATERIAL ---"
    )

    messages: list[dict[str, str]] = []

    # Add conversation history
    for i, msg in enumerate(history):
        if i == 0 and msg["role"] == "user":
            # Prepend context to first user message
            messages.append({"role": "user", "content": f"{system_prompt}\n\n{msg['content']}"})
        else:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Add new user message
    if not messages:
        # First message ever — include context
        messages.append({"role": "user", "content": f"{system_prompt}\n\nMy question: {user_message}"})
    else:
        messages.append({"role": "user", "content": user_message})

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=20000,
    )
    return response.choices[0].message.content
