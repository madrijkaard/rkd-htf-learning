from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    app_name: str
    symbols: List[str]  # será preenchido com SYMBOLS do .env
    capture_interval_seconds: int = 300  # valor padrão caso não esteja no .env

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
