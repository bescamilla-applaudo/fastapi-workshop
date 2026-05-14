from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    secret_key: str = "change-me-to-a-random-string-at-least-32-chars"
    database_url: str = "sqlite+aiosqlite:///./ideas.db"
    debug: bool = False
    access_token_expire_minutes: int = 30

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
