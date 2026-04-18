# file: backend/app/main.py
# force reload 14
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

# Ensure project root (parent of backend) is on path so "src" package can be imported
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import router
from app.routes.favorites import router as favorites_router
from app.routes.combo_routes import router as combo_router
from app.routes.opportunity_routes import router as opportunity_router
from app.routes.logs import router as logs_router
from app.routes.agent_chat import router as agent_chat_router
from app.routes.openspec import router as openspec_router
from app.routes.monitor_preferences import router as monitor_preferences_router
from app.routes.external_balances import router as external_balances_router
from app.routes.coordination import router as coordination_router
from app.routes.workflow import router as workflow_router
from app.routes.workflow_validation import router as workflow_validation_router
from app.routes.market import router as market_router
from app.routes.portfolio import router as portfolio_router
from app.routes.signals import router as signals_router
from app.routes.ai_dashboard import router as ai_dashboard_router
from app.routes.auth import router as auth_router
from app.routes.user_profile import router as user_profile_router
from app.routes.user_credentials import router as user_credentials_router
from app.routes.system_preferences import router as system_preferences_router
from app.routes.retrospectives import router as retrospectives_router
from app.routes.onchain_signals import router as onchain_signals_router
from app.services.signal_monitor import signal_monitor
from app.services.binance_service import (
    start_signal_feed_snapshot_worker,
    stop_signal_feed_snapshot_worker,
)

# Configure logging to file
log_file = Path(__file__).parent.parent / "full_execution_log.txt"

# Get root logger and add file handler
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

# Add handler if not already present
if not any(isinstance(h, logging.FileHandler) for h in root_logger.handlers):
    root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)
logger.info("=" * 80)
logger.info("Backend starting up - logging to %s", log_file)
logger.info("=" * 80)

from contextlib import asynccontextmanager
from app.database import Base, engine, sync_postgres_identity_sequences

# Import models to register them with Base
import app.models


def seed_combo_templates_if_empty():
    """Seed combo_templates from JSON export if the table is empty."""
    try:
        from app.startup_seed import seed_combo_templates_if_empty as seed_templates

        inserted = seed_templates()
        if inserted:
            logger.info("Seeded %s combo_templates from JSON export", inserted)
    except Exception as e:
        logger.error(f"Error seeding combo_templates: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    logger.info("Initializing Database Tables...")
    try:
        Base.metadata.create_all(bind=engine)
        sync_postgres_identity_sequences()
        # Apply lightweight forward-only schema migrations for existing tables
        from app.database import ensure_runtime_schema_migrations

        ensure_runtime_schema_migrations()

        # Workflow DB (optional; enabled via WORKFLOW_DB_ENABLED=1)
        try:
            from app.workflow_database import (
                bootstrap_project_workflow_db,
                init_workflow_schema,
                get_workflow_db,
            )
            from app.workflow_models import Project

            init_workflow_schema()

            # Seed default projects for independent Kanban contexts.
            try:
                db = next(get_workflow_db())
                default_projects = [
                    {
                        "slug": "crypto",
                        "name": "Crypto Project",
                        "root_directory": os.getenv("CRYPTO_ROOT_DIRECTORY", str(_project_root)),
                        "database_url": os.getenv("CRYPTO_DATABASE_URL"),
                        "frontend_url": os.getenv("CRYPTO_FRONTEND_URL", "http://localhost:5173"),
                        "backend_url": os.getenv("CRYPTO_BACKEND_URL", "http://localhost:8003"),
                        "workflow_database_url": os.getenv("CRYPTO_WORKFLOW_DATABASE_URL"),
                        "tech_stack": "FastAPI, React, Vite, Playwright",
                    },
                ]

                for project_data in default_projects:
                    if not project_data["workflow_database_url"]:
                        logger.warning(
                            "Project '%s' skipped because workflow database URL is not configured",
                            project_data["slug"],
                        )
                        continue

                    existing = (
                        db.query(Project).filter(Project.slug == project_data["slug"]).first()
                    )
                    if existing:
                        existing.root_directory = project_data["root_directory"]
                        existing.database_url = project_data["database_url"]
                        existing.frontend_url = project_data["frontend_url"]
                        existing.backend_url = project_data["backend_url"]
                        existing.workflow_database_url = project_data["workflow_database_url"]
                        existing.tech_stack = project_data["tech_stack"]
                        continue

                    db.add(Project(**project_data))
                    logger.info("Seeded default project '%s'", project_data["slug"])

                db.commit()
                for project in db.query(Project).all():
                    bootstrap_project_workflow_db(project)
                db.close()
            except Exception as proj_err:
                logger.warning(f"Project seed skipped/failed: {proj_err}")
        except Exception as e:
            logger.warning(f"Workflow DB init skipped/failed: {e}")

        logger.info("Database initialized successfully.")

        # Seed combo_templates if empty
        seed_combo_templates_if_empty()
        # signal_monitor.start()  # DISABLED FOR DEBUG
        # await start_signal_feed_snapshot_worker()  # DISABLED FOR DEBUG
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

    yield
    await stop_signal_feed_snapshot_worker()
    signal_monitor.stop()


settings = get_settings()


def _normalize_origin(value: str | None) -> str | None:
    if not value:
        return None

    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def _build_cors_origins() -> list[str]:
    configured_origins = list(settings.cors_origins)
    configured_origins.extend(
        [
            os.getenv("CRYPTO_FRONTEND_URL"),
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://72.60.150.140:5173",
        ]
    )

    origins: list[str] = []
    for candidate in configured_origins:
        normalized = _normalize_origin(candidate)
        if not normalized or normalized in origins:
            continue
        origins.append(normalized)
    return origins


cors_origins = _build_cors_origins()

app = FastAPI(title=settings.api_title, version=settings.api_version, lifespan=lifespan)

# CORS must be explicit when credentials are enabled, otherwise browsers reject
# cross-origin requests from the public frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_signals_disclaimer_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/signals"):
        response.headers["X-Disclaimer"] = (
            "Isenção de responsabilidade: este não é advice financeiro."
        )
    return response


# Include API routes
app.include_router(router)
app.include_router(favorites_router)
app.include_router(combo_router)
app.include_router(opportunity_router)
app.include_router(logs_router)
app.include_router(agent_chat_router)
app.include_router(openspec_router)
app.include_router(monitor_preferences_router)
app.include_router(external_balances_router)
app.include_router(coordination_router)
app.include_router(workflow_router)
app.include_router(workflow_validation_router)
app.include_router(market_router)
app.include_router(portfolio_router)
# NOTE: onchain_signals_router MUST be before signals_router to avoid
# the /{signal_id} catch-all route in signals_router matching /api/signals/onchain
app.include_router(onchain_signals_router)
app.include_router(signals_router)
app.include_router(ai_dashboard_router)
app.include_router(auth_router)
app.include_router(user_profile_router)
app.include_router(user_credentials_router)
app.include_router(system_preferences_router)
app.include_router(retrospectives_router)


@app.get("/")
async def root():
    return {"service": "Crypto Backtester API", "version": settings.api_version, "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    # Forced reload for src updates
