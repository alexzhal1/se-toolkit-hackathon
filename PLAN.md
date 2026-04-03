# Implementation Plan — StudyBot

**Idea:** An AI-powered study assistant that explains uploaded learning material, generates flashcards for memorization, and creates quizzes to test knowledge.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI |
| Database | PostgreSQL, SQLAlchemy (async), Alembic |
| AI | DeepSeek API (OpenAI-compatible) |
| Telegram Agent | aiogram 3 |
| Web Client | React, Vite, TypeScript |
| Deployment | Docker Compose, Nginx, VM |

---

## Version 1 — Explain & Flashcards

**Core feature:** User uploads study text → AI generates a detailed explanation → AI creates flashcards for memorization.

This is the most valuable feature for a student: understanding new material and having ready-made flashcards to review it. It is straightforward to implement and delivers immediate value.

### Components

**Backend (FastAPI)**
- `POST /api/auth` — register or identify user
- `POST /api/materials` — upload study text
- `GET /api/materials` — list user's materials
- `GET /api/materials/{id}` — get material with explanation
- `POST /api/materials/{id}/explain` — generate AI explanation
- `POST /api/materials/{id}/flashcards` — generate flashcards
- `GET /api/materials/{id}/flashcards` — retrieve flashcards

**Database (PostgreSQL)**
- **User** — id, telegram_id, username, first_name, created_at
- **Material** — id, user_id, title, content, explanation, created_at
- **Flashcard** — id, material_id, front, back, created_at

**Web Client (React)**
- **Home page** — list of uploaded materials
- **Upload page** — text input form to add new material
- **Material page** — view original text + AI explanation (rendered as Markdown)
- **Flashcards page** — interactive flip cards with navigation

**Telegram Bot (aiogram 3)**
- `/start` — register user, provide link to web app
- Send any text → automatically saved as study material
- `/materials` — list saved materials

### V1 Deliverable
A functioning product where a user can upload text, get an AI-generated explanation, and study with flashcards — via web interface or Telegram bot. Shown to TA for feedback.

---

## Version 2 — Quizzes + Spaced Repetition + Deploy

Builds on Version 1 by adding quiz generation and a spaced repetition system. Addresses TA feedback from V1 review.

### New Features

1. **Quiz generation** — AI creates a 10-question multiple-choice quiz from the material
2. **Quiz taking** — interactive UI: select answers, submit, see score
3. **Quiz results** — review mistakes with AI-generated explanations for each answer
4. **Spaced repetition** — flashcards scheduled using the SM-2 algorithm (cards you struggle with appear more often)
5. **Progress tracking** — stats on materials studied, cards reviewed, quiz scores

### New Components

**Backend — additional endpoints**
- `POST /api/materials/{id}/quiz` — generate quiz
- `GET /api/quizzes/{id}` — get quiz questions
- `POST /api/quizzes/{id}/submit` — submit answers, get results
- `GET /api/flashcards/review` — get cards due for review (SM-2)
- `POST /api/flashcards/{id}/review` — record review result

**Database — additional tables**
- **Quiz** — id, material_id, title, created_at
- **QuizQuestion** — id, quiz_id, question_text, options (JSON), correct_answer_index, explanation
- **QuizAttempt** — id, user_id, quiz_id, score, answers (JSON), completed_at
- **Flashcard** — add difficulty, next_review_at columns for SM-2

**Web Client — additional pages**
- **Quiz page** — take a quiz (select from 4 options per question)
- **Results page** — score + explanation of incorrect answers
- **Review page** — spaced repetition session for due flashcards

**Deployment**
- Docker Compose on VM (PostgreSQL + Backend + Frontend + Nginx)
- HTTPS via Certbot/Nginx
- Publicly accessible URL

### V2 Deliverable
A deployed, publicly available study assistant with explanations, flashcards (with spaced repetition), and quizzes. TA feedback from V1 is addressed.
