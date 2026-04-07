import json
import logging
import random

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
        max_tokens=10000,
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
        max_tokens=10000,
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


def _strip_code_fences(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines)
    return raw


def _shuffle_options(question: dict) -> dict:
    """Shuffle options in-place and remap correct_indices accordingly."""
    options = list(question.get("options", []))
    correct = question.get("correct_indices") or []
    if not isinstance(correct, list):
        correct = [correct]
    correct = [int(i) for i in correct if isinstance(i, (int, float))]

    if not options:
        question["options"] = []
        question["correct_indices"] = []
        return question

    # Pair each option with a flag: is it correct?
    pairs = [(opt, idx in correct) for idx, opt in enumerate(options)]
    random.shuffle(pairs)

    new_options = [p[0] for p in pairs]
    new_correct = [i for i, p in enumerate(pairs) if p[1]]

    question["options"] = new_options
    question["correct_indices"] = new_correct
    return question


async def generate_quiz(content: str, explanation: str | None = None) -> list[dict]:
    """Generate a multiple-choice quiz (single + multi answer) from the study material."""
    context = content
    if explanation:
        context += f"\n\nExplanation:\n{explanation}"

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    "You are an expert tutor creating a quiz. "
                    "Generate exactly 10 questions from the provided material. "
                    "Each question must have 4 options. "
                    "Mix single-answer and multi-answer questions: roughly 7 single-answer "
                    "(exactly one correct option) and 3 multi-answer (2 or more correct options). "
                    "For each question, provide 'correct_indices' as a JSON array of 0-based "
                    "indices of correct options. For single-answer questions the array has one "
                    "element; for multi-answer it has two or more. "
                    "Provide a brief explanation of the correct answer(s). "
                    "IMPORTANT: Do NOT always place correct answers first — vary their positions. "
                    "All content must be in English. "
                    "Return ONLY a JSON array with no extra text, in this format:\n"
                    '[{"question": "...", "options": ["A", "B", "C", "D"], '
                    '"correct_indices": [2], "multi": false, "explanation": "..."}, '
                    '{"question": "...", "options": ["W", "X", "Y", "Z"], '
                    '"correct_indices": [0, 2], "multi": true, "explanation": "..."}, ...]\n\n'
                    f"Material:\n\n{context}"
                ),
            },
        ],
        max_tokens=10000,
    )

    raw = _strip_code_fences(response.choices[0].message.content)
    try:
        questions = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Failed to parse quiz JSON: %s", raw[:200])
        return []

    # Backwards-compat: accept old "correct_index" as a fallback
    for q in questions:
        if "correct_indices" not in q and "correct_index" in q:
            q["correct_indices"] = [int(q["correct_index"])]
        q["multi"] = bool(q.get("multi", len(q.get("correct_indices", [])) > 1))

    # Shuffle options so the correct answer is not always first
    for q in questions:
        _shuffle_options(q)

    return questions


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
        max_tokens=10000,
    )
    return response.choices[0].message.content
