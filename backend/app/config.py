from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://studybot:studybot@db:5432/studybot"
    DEEPSEEK_API_KEY: str = ""
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
