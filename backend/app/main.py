# file: backend/app/main.py
# force reload 14
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import router
from app.routes.sequential_optimization import router as sequential_router
from app.routes.parameter_optimization import router as parameter_router
from app.routes.risk_optimization import router as risk_router
from app.routes.favorites import router as favorites_router

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

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version
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
app.include_router(sequential_router)  # Sequential optimization routes (WebSocket-based, legacy)
app.include_router(parameter_router)  # Parameter optimization routes (simplified)
app.include_router(risk_router)  # Risk management optimization routes
app.include_router(favorites_router)  # Favorites management routes

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
