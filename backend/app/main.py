# file: backend/app/main.py
# force reload 14
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import router
from app.routes.sequential_optimization import router as sequential_router
from app.routes.parameter_optimization import router as parameter_router

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
