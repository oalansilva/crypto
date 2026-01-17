# file: backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Supabase (Optional for local SQLite)
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    
    # API
    api_title: str = "Crypto Backtester API"
    api_version: str = "1.0.0"
    
    # CORS - Allow all origins in development
    cors_origins: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
