import asyncio
import base64
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.routes import lab as lab_routes
from app.routes.lab_logs_sse import get_log_path, stream_lab_logs


def _jwt_hs256(secret: str, payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}

    def _b64(obj: dict) -> str:
        raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")

    h = _b64(header)
    p = _b64(payload)
    sig = hmac.new(secret.encode("utf-8"), f"{h}.{p}".encode("utf-8"), hashlib.sha256).digest()
    s = base64.urlsafe_b64encode(sig).rstrip(b"=").decode("utf-8")
    return f"{h}.{p}.{s}"


@pytest.mark.asyncio
async def test_stream_lab_logs_yields_existing_entries():
    run_id = "run_stream_existing"
    step = "combo_optimization"
    log_path = get_log_path(run_id, step)
    log_path.write_text("[2026-02-13T18:00:00Z] [INFO] starting optimization\n", encoding="utf-8")

    generator = stream_lab_logs(
        run_id,
        step,
        run_state_reader=lambda: {"status": "done", "step": "done"},
        poll_interval=0.01,
        idle_timeout=0.2,
    )

    try:
        first = await asyncio.wait_for(anext(generator), timeout=1.0)
        payload = json.loads(first.split("data: ", 1)[1])
        assert payload["level"] == "INFO"
        assert payload["message"] == "starting optimization"
        assert payload["step"] == step
    finally:
        await generator.aclose()
        log_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_stream_lab_logs_sends_realtime_updates():
    run_id = "run_stream_realtime"
    step = "combo_optimization"
    log_path = get_log_path(run_id, step)
    log_path.write_text("", encoding="utf-8")

    state = {"status": "running", "step": step}

    async def _writer():
        await asyncio.sleep(0.05)
        line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] [INFO] heartbeat\n"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
        await asyncio.sleep(0.05)
        state["status"] = "done"
        state["step"] = "done"

    writer_task = asyncio.create_task(_writer())
    generator = stream_lab_logs(
        run_id,
        step,
        run_state_reader=lambda: state,
        poll_interval=0.01,
        idle_timeout=1.0,
    )

    received = None
    try:
        async for chunk in generator:
            if not chunk.startswith("data: "):
                continue
            payload = json.loads(chunk.split("data: ", 1)[1])
            if payload.get("message") == "heartbeat":
                received = payload
                break
    finally:
        await generator.aclose()
        await writer_task
        log_path.unlink(missing_ok=True)

    assert received is not None
    assert received["level"] == "INFO"
    assert received["step"] == step


def test_lab_logs_stream_endpoint_with_jwt_auth(tmp_path, monkeypatch):
    run_id = "run_stream_auth"
    step = "combo_optimization"

    run_payload = {
        "run_id": run_id,
        "status": "done",
        "step": "done",
        "phase": "done",
        "created_at_ms": 1,
        "updated_at_ms": 1,
    }
    (tmp_path / f"{run_id}.json").write_text(json.dumps(run_payload), encoding="utf-8")

    monkeypatch.setattr(lab_routes, "_run_path", lambda rid: tmp_path / f"{rid}.json")

    log_path = get_log_path(run_id, step)
    log_path.write_text("[2026-02-13T18:10:00Z] [INFO] auth log line\n", encoding="utf-8")

    app = FastAPI()
    app.include_router(lab_routes.router)
    client = TestClient(app)

    monkeypatch.setenv("LAB_LOGS_JWT_SECRET", "test-secret")

    no_auth = client.get(f"/api/lab/runs/{run_id}/logs/stream?step={step}")
    assert no_auth.status_code == 401

    token = _jwt_hs256("test-secret", {"sub": "tester", "exp": int(time.time()) + 60})
    with client.stream(
        "GET",
        f"/api/lab/runs/{run_id}/logs/stream?step={step}",
        headers={"Authorization": f"Bearer {token}"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        first_line = next((line for line in response.iter_lines() if line), "")
        assert first_line.startswith("data: ")
        payload = json.loads(first_line.split("data: ", 1)[1])
        assert payload["message"] == "auth log line"
        assert payload["step"] == step

    log_path.unlink(missing_ok=True)
