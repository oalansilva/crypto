# file: backend/app/main.py
# force reload 14
import sys
from pathlib import Path

# Ensure project root (parent of backend) is on path so "src" package can be imported
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import router
from app.routes.favorites import router as favorites_router
from app.routes.combo_routes import router as combo_router
from app.routes.opportunity_routes import router as opportunity_router
from app.routes.logs import router as logs_router
from app.routes.agent_chat import router as agent_chat_router
from app.routes.openspec import router as openspec_router

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
from app.database import Base, engine
# Import models to register them with Base
import app.models

def seed_combo_templates_if_empty():
    """Seed combo_templates from JSON export if the table is empty."""
    import json
    from pathlib import Path
    from app.database import DB_PATH
    import sqlite3
    
    json_path = Path(__file__).parent.parent / "config" / "combo_templates_export.json"
    if not json_path.exists():
        logger.warning(f"combo_templates_export.json not found at {json_path}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # Check if table has any rows
    cur.execute("SELECT COUNT(*) FROM combo_templates")
    count = cur.fetchone()[0]
    
    if count > 0:
        logger.info(f"combo_templates already has {count} templates, skipping seed")
        conn.close()
        return
    
    logger.info("combo_templates is empty, seeding from JSON export...")
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        inserted = 0
        
        for item in data:
            name = item.get("name")
            if not name:
                continue
            
            description = item.get("description") or ""
            is_prebuilt = 1 if item.get("is_prebuilt") else 0
            is_example = 1 if item.get("is_example") else 0
            is_readonly = 1 if item.get("is_readonly") else 0
            template_data = item.get("template_data") or {}
            optimization_schema = item.get("optimization_schema")
            created_at = item.get("created_at")
            
            if created_at:
                cur.execute(
                    """
                    INSERT INTO combo_templates (
                        name, description, is_prebuilt, is_example, is_readonly,
                        template_data, optimization_schema, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        name, description, is_prebuilt, is_example, is_readonly,
                        json.dumps(template_data, ensure_ascii=False),
                        json.dumps(optimization_schema, ensure_ascii=False) if optimization_schema else None,
                        created_at,
                    ),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO combo_templates (
                        name, description, is_prebuilt, is_example, is_readonly,
                        template_data, optimization_schema
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name, description, is_prebuilt, is_example, is_readonly,
                        json.dumps(template_data, ensure_ascii=False),
                        json.dumps(optimization_schema, ensure_ascii=False) if optimization_schema else None,
                    ),
                )
            inserted += 1
        
        conn.commit()
        logger.info(f"Seeded {inserted} combo_templates from JSON export")
    except Exception as e:
        logger.error(f"Error seeding combo_templates: {e}")
    finally:
        conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    logger.info("Initializing Database Tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
        
        # Seed combo_templates if empty
        seed_combo_templates_if_empty()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    yield
    # Cleanup if needed

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

# Include API routes
app.include_router(router)
app.include_router(favorites_router)
app.include_router(combo_router)
app.include_router(opportunity_router)
app.include_router(logs_router)
app.include_router(agent_chat_router)
app.include_router(openspec_router)

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
