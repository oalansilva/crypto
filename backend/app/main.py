# file: backend/app/main.py
# force reload 14
import sys
from pathlib import Path

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
from app.routes.lab import router as lab_router
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
from app.routes.user_credentials import router as user_credentials_router
from app.routes.system_preferences import router as system_preferences_router
from app.services.signal_monitor import signal_monitor

# Configure logging to file
log_file = Path(__file__).parent.parent / "full_execution_log.txt"

# Get root logger and add file handler
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

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
        # Apply lightweight SQLite migrations for existing tables
        from app.database import ensure_sqlite_migrations
        ensure_sqlite_migrations()

        # Workflow DB (optional; enabled via WORKFLOW_DB_ENABLED=1)
        try:
            from app.workflow_database import init_workflow_schema, get_workflow_db
            from app.workflow_models import Project

            init_workflow_schema()

            # Seed default project "crypto" if not exists
            try:
                db = next(get_workflow_db())
                existing = db.query(Project).filter(Project.slug == "crypto").first()
                if not existing:
                    crypto_project = Project(slug="crypto", name="Crypto Project")
                    db.add(crypto_project)
                    db.commit()
                    logger.info("Seeded default project 'crypto'")
                db.close()
            except Exception as proj_err:
                logger.warning(f"Project seed skipped/failed: {proj_err}")
        except Exception as e:
            logger.warning(f"Workflow DB init skipped/failed: {e}")

        logger.info("Database initialized successfully.")

        # Seed combo_templates if empty
        seed_combo_templates_if_empty()
        signal_monitor.start()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

    yield
    signal_monitor.stop()

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan
)

# CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    # Dev/prod friendly: allow local dev + the current host origin.
    # If you want to lock this down later, replace "*" with explicit origins.
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_signals_disclaimer_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/signals"):
        response.headers["X-Disclaimer"] = "Isenção de responsabilidade: este não é advice financeiro."
    return response

# Include API routes
app.include_router(router)
app.include_router(favorites_router)
app.include_router(combo_router)
app.include_router(opportunity_router)
app.include_router(logs_router)
app.include_router(agent_chat_router)
app.include_router(openspec_router)
app.include_router(lab_router)
app.include_router(monitor_preferences_router)
app.include_router(external_balances_router)
app.include_router(coordination_router)
app.include_router(workflow_router)
app.include_router(workflow_validation_router)
app.include_router(market_router)
app.include_router(portfolio_router)
app.include_router(signals_router)
app.include_router(ai_dashboard_router)
app.include_router(auth_router)
app.include_router(user_credentials_router)
app.include_router(system_preferences_router)

@app.get("/")
async def root():
    return {
        "service": "Crypto Backtester API",
        "version": settings.api_version,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    # Forced reload for src updates
