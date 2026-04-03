from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://studybot:studybot@db:5432/studybot"
    DEEPSEEK_API_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_MINI_APP_URL: str = "https://localhost:3000"
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
