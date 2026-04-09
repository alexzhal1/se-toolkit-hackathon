import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="StudyBot API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import auth, chat, flashcards, materials, quizzes, stats  # noqa: E402

app.include_router(auth.router, prefix="/api")
app.include_router(materials.router, prefix="/api")
app.include_router(flashcards.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(quizzes.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
