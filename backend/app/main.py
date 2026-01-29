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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    logger.info("Initializing Database Tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
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
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
app.include_router(favorites_router)
app.include_router(combo_router)
app.include_router(opportunity_router)

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
