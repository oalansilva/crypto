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


def test_get_nasdaq100_universe():
    client = _build_client()

    response = client.get('/api/markets/us/nasdaq100')

    assert response.status_code == 200
    payload = response.json()

    assert payload['market'] == 'us-stocks'
    assert payload['universe'] == 'nasdaq-100'
    assert payload['version'] == '2026-02-23'
    assert isinstance(payload['symbols'], list)
    assert payload['count'] == len(payload['symbols']) == 100
    assert 'AAPL' in payload['symbols']
    assert 'MSFT' in payload['symbols']
    assert all('/' not in symbol for symbol in payload['symbols'])
