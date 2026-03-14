# file: backend/app/config.py
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

    # Background jobs
    arbitrage_monitor_enabled: str = "1"

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

    # CORS - Allow all origins in development
    cors_origins: list[str] = ["*"]

    # Agent chat (LLM conversation about strategies)
    agent_chat_enabled: str = "0"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
