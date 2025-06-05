from pydantic_settings import BaseSettings  # ⬅️ novo import!

class Settings(BaseSettings):
    app_name: str
    symbol: str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
