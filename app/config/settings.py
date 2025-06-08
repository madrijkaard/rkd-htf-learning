from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    app_name: str
    symbols: List[str]
    capture_interval_seconds: int = 60
    depth_limit: int = 800

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
