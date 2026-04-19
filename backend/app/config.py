# file: backend/app/config.py
import json
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load backend/.env and repo-root .env into os.environ for runtime code that uses
# os.getenv directly (e.g. Binance wallet integration). Keep override=False so
# already-exported env vars still win.
_THIS_FILE = Path(__file__).resolve()
_BACKEND_DIR = _THIS_FILE.parents[1]
_REPO_ROOT = _THIS_FILE.parents[2]
for _env_path in (_BACKEND_DIR / ".env", _REPO_ROOT / ".env"):
    if _env_path.exists():
        load_dotenv(_env_path, override=False)


class Settings(BaseSettings):
    # Market data providers (optional)
    alphavantage_api_key: str | None = None

    # Main application DB. If omitted, runtime can fall back to workflow DB.
    database_url: str | None = None

    # Workflow DB (centralize-workflow-state-db)
    # NOTE: We declare these explicitly so values from backend/.env are available
    # through Settings even if they are not exported into os.environ.
    workflow_db_enabled: str = "0"
    workflow_database_url: str | None = None

    # Supabase (Optional for local SQLite)
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    # API
    api_title: str = "Crypto Backtester API"
    api_version: str = "1.0.0"

    # CORS origins for browser access. Accepts JSON arrays or comma-separated values.
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://72.60.150.140:5173",
    ]

    # Agent chat (LLM conversation about strategies)
    agent_chat_enabled: str = "0"

    # Async processing
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"
    celery_task_always_eager: str = "0"
    celery_worker_concurrency: int = 1
    celery_worker_prefetch_multiplier: int = 1
    celery_batch_max_retries: int = 3
    celery_retry_backoff_max: int = 300
    async_job_ttl_seconds: int = 604800
    async_dead_letter_max_items: int = 200

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    raw_origins = os.getenv("CORS_ORIGINS") or os.getenv("CORS_ALLOW_ORIGINS")
    if raw_origins:
        parsed_origins: list[str] | None = None
        try:
            loaded = json.loads(raw_origins)
            if isinstance(loaded, list):
                parsed_origins = [str(origin).strip() for origin in loaded if str(origin).strip()]
        except json.JSONDecodeError:
            parsed_origins = None

        settings.cors_origins = parsed_origins or [
            origin.strip() for origin in raw_origins.split(",") if origin.strip()
        ]
    return settings
