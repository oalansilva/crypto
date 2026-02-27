from __future__ import annotations

from fastapi import FastAPI
import httpx

from app.routes.coordination import router as coordination_router
import app.services.change_tasks_service as change_tasks_service


def _build_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(coordination_router)
    return test_app


async def _get(path: str):
    app = _build_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(path)


def _write(p, text: str):
    p.write_text(text, encoding="utf-8")


async def test_change_tasks_parses_sections_and_nested_items(monkeypatch, tmp_path):
    # tmp openspec layout
    openspec = tmp_path / "openspec" / "changes" / "my-change"
    openspec.mkdir(parents=True)

    _write(
        openspec / "tasks.md",
        """\
## 1. Backend

- [x] 1.1 First task
- [ ] 1.2 Second task
  - detail line

## 2. Frontend

- [ ] 2.1 UI task
""",
    )

    monkeypatch.setattr(change_tasks_service, "project_root", lambda: tmp_path)

    res = await _get("/api/coordination/changes/my-change/tasks")
    assert res.status_code == 200, res.text
    payload = res.json()

    assert payload["change_id"] == "my-change"
    assert payload["path"].endswith("openspec/changes/my-change/tasks.md")

    assert [s["title"] for s in payload["sections"]] == ["1. Backend", "2. Frontend"]

    backend_items = payload["sections"][0]["items"]
    assert backend_items[0]["checked"] is True
    assert backend_items[0]["code"] == "1.1"

    assert backend_items[1]["checked"] is False
    assert backend_items[1]["code"] == "1.2"
    assert backend_items[1]["children"][0]["checked"] is None


async def test_change_tasks_missing_returns_404(monkeypatch, tmp_path):
    monkeypatch.setattr(change_tasks_service, "project_root", lambda: tmp_path)

    res = await _get("/api/coordination/changes/nope/tasks")
    assert res.status_code == 404
