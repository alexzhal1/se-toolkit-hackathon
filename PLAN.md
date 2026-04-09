# Implementation Plan — StudyBot

**Idea:** An AI-powered study assistant that explains uploaded learning material, generates flashcards for memorization, and creates quizzes to test knowledge.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI |
| Database | PostgreSQL 16, SQLAlchemy (async), Alembic |
| AI | DeepSeek API (OpenAI-compatible) |
| Auth | JWT (bcrypt + PyJWT) |
| Web Client | React 18, Vite, TypeScript |
| Deployment | Docker Compose, Nginx, Ubuntu 24.04 VM |

---

## Version 1 — Explain & Flashcards ✅ Implemented

**Core feature:** User uploads study text → AI generates a detailed explanation → AI creates flashcards for memorization.

This is the single most valuable feature for a student: understanding new material and having ready-made flashcards to review it.

### Components

**Backend (FastAPI)** — ✅ Fully functional
- `POST /api/auth/register` — register new user with email, login, password
- `POST /api/auth/login` — login, receive JWT token
- `POST /api/materials` — upload study text as material
- `GET /api/materials` — list current user's materials
- `GET /api/materials/{id}` — get material with explanation
- `POST /api/materials/{id}/explain` — generate AI explanation via DeepSeek
- `POST /api/materials/{id}/flashcards` — generate flashcards via DeepSeek
- `GET /api/materials/{id}/flashcards` — retrieve flashcards
- All endpoints protected with JWT authentication (`get_current_user` dependency)

**Database (PostgreSQL)** — ✅ All tables created and working
- **User** — id, email (unique), login (unique), hashed_password, created_at
- **Material** — id, user_id (FK), title, content, explanation, created_at
- **Flashcard** — id, material_id (FK), front, back, created_at

**Web Client (React)** — ✅ All pages functional
- **Login/Register page** — toggle between sign up and log in, form validation, JWT storage
- **Home page** — list of uploaded materials with date and explanation status
- **Upload page** — text input + PDF/DOCX file upload
- **Material page** — view original text + AI explanation rendered as Markdown (with KaTeX for formulas)
- **Flashcards page** — interactive flip cards with flip animation

### V1 Deliverable ✅ Done
A functioning product where a user can register, upload text or files, get an AI-generated explanation, and study with flashcards — via a modern web interface. Ready to be shown to the TA for feedback.

---

## Version 2 — Quizzes + Spaced Repetition + Stats + Deploy ✅ Implemented

Builds on Version 1 by adding quiz generation, SM-2 spaced repetition for flashcards, progress tracking, and Docker deployment.

### New Features

1. **Quiz generation** — AI creates a 10-question multiple-choice quiz (some with multiple correct answers)
2. **Quiz taking** — interactive UI with single/multi-select, submit all at once
3. **Quiz results** — score display, correct/incorrect highlighting, AI explanation per question
4. **Spaced repetition (SM-2)** — flashcards scheduled with ease_factor, interval, repetitions, next_review_at
5. **Review session** — flip-card review with grading (Again/Hard/Good/Easy → quality 0–5)
6. **Progress tracking** — stats dashboard with materials count, flashcards due/learned, quiz avg score
7. **AI Chat** — contextual chat about a specific material with conversation history
8. **Docker Compose deployment** — 4 containers (PostgreSQL, FastAPI, React, Nginx)

### New Components

**Backend — additional endpoints** ✅ Implemented
- `POST /api/materials/{id}/quiz` — generate quiz via DeepSeek
- `GET /api/materials/{id}/quiz` — get existing quiz for a material
- `POST /api/quizzes/{id}/submit` — submit answers, record attempt, return score
- `GET /api/flashcards/review` — get SM-2 due cards for current user
- `POST /api/flashcards/{id}/review` — record review result, apply SM-2 algorithm
- `GET /api/flashcards/review/stats` — review queue stats (due, total, learned)
- `GET /api/users/me/stats` — full user statistics
- `GET/POST/DELETE /api/materials/{id}/chat` — chat with AI about a material

**Database — additional tables** ✅ Implemented
- **Quiz** — id, material_id (FK), title, created_at
- **QuizQuestion** — id, quiz_id (FK), question_text, options (JSON), correct_answer_indices (JSON), is_multi, explanation
- **QuizAttempt** — id, user_id (FK), quiz_id (FK), score, total, answers (JSON), completed_at
- **Flashcard** — enhanced with ease_factor, interval_days, repetitions, next_review_at (SM-2)

**Web Client — additional pages** ✅ Implemented
- **Quiz page** — take a quiz, submit answers, see score + explanations
- **Review page** — SM-2 spaced repetition session with card flip and grading buttons
- **Stats page** — progress dashboard with tile cards and recent quiz attempts table
- **Chat page** — chat interface with message history and AI responses

**Deployment** ✅ Implemented
- `docker-compose.yml` — PostgreSQL 16 + FastAPI + React (Vite) + Nginx
- `nginx.conf` — reverse proxy: `/api/` → backend:8000, `/` → frontend:3000
- `Dockerfile` for backend (Python 3.12 slim)
- `Dockerfile` for frontend (Node 18, Vite)
- Ready for Ubuntu 24.04 VM deployment

### V2 Deliverable ✅ Done
A deployed, publicly available study assistant with explanations, flashcards (with SM-2 spaced repetition), quizzes, AI chat, and progress tracking. All three required components are functional: **backend** (FastAPI with JWT auth), **database** (PostgreSQL with 7 tables), and **end-user client** (React web app).

---

## Component Completeness Check

| Component | Status | Details |
|-----------|--------|---------|
| **Backend** | ✅ Complete | FastAPI with 17 endpoints, JWT middleware, AI service integration |
| **Database** | ✅ Complete | PostgreSQL, 7 tables, async SQLAlchemy, 6 Alembic migrations |
| **Web Client** | ✅ Complete | React 18, 8 pages, JWT auth, API client with error handling |
