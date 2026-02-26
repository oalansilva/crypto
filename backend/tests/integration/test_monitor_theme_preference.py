from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.routes import monitor_preferences


def _build_test_app(tmp_path: Path) -> FastAPI:
    db_file = tmp_path / "monitor_theme_test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def _get_db_override():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(monitor_preferences.router)
    app.dependency_overrides[get_db] = _get_db_override
    return app


async def test_monitor_theme_field_roundtrips_on_preference(tmp_path: Path):
    app = _build_test_app(tmp_path)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        put_response = await client.put(
            "/api/monitor/preferences/BTC/USDT",
            json={"theme": "dark-green"},
        )
        get_response = await client.get("/api/monitor/preferences")

    assert put_response.status_code == 200, put_response.text
    assert put_response.json()["theme"] == "dark-green"

    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["BTC/USDT"]["theme"] == "dark-green"
