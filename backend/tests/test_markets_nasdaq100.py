import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path for "app" imports in tests.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.api import router


def _build_client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_get_nasdaq100_universe_disabled_for_crypto_only_mvp():
    client = _build_client()

    response = client.get("/api/markets/us/nasdaq100")

    assert response.status_code == 410
    payload = response.json()

    assert "US stocks are disabled" in payload["detail"]
