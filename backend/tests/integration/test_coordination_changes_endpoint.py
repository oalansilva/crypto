from __future__ import annotations

from fastapi import FastAPI
import httpx

from app.routes.coordination import router as coordination_router
import app.services.coordination_service as coordination_service


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


async def test_coordination_changes_lists_active_and_archived(monkeypatch, tmp_path):
    coord_dir = tmp_path / "coordination"
    coord_dir.mkdir(parents=True)

    _write(
        coord_dir / "a-change.md",
        """# A Change\n\n## Status\n- PO: done\n- DEV: not started\n- QA: not started\n- Alan approval: approved\n- Homologation: not reviewed\n\n## Notes\n...\n""",
    )

    _write(
        coord_dir / "b-archived.md",
        """# B Archived\n\n## Status\n- PO: done\n- DEV: done\n- QA: done\n- Alan approval: approved\n- Homologation: approved\n\n## Closed\n""",
    )

    monkeypatch.setattr(coordination_service, "coordination_dir", lambda: coord_dir)

    res = await _get("/api/coordination/changes")
    assert res.status_code == 200, res.text
    payload = res.json()

    ids = {i["id"] for i in payload["items"]}
    assert ids == {"a-change", "b-archived"}

    by_id = {i["id"]: i for i in payload["items"]}

    assert by_id["a-change"]["archived"] is False
    assert by_id["a-change"]["column"] == "DEV"

    assert by_id["b-archived"]["archived"] is True
    assert by_id["b-archived"]["column"] == "Archived"


async def test_coordination_changes_normalize_legacy_homologation_status(monkeypatch, tmp_path):
    coord_dir = tmp_path / "coordination"
    coord_dir.mkdir(parents=True)

    _write(
        coord_dir / "legacy-change.md",
        """# Legacy Change\n\n## Status\n- PO: done\n- DEV: done\n- QA: done\n- Alan approval: approved\n- Alan homologation: approved\n\n## Notes\n...\n""",
    )

    monkeypatch.setattr(coordination_service, "coordination_dir", lambda: coord_dir)

    res = await _get("/api/coordination/changes")
    assert res.status_code == 200, res.text
    payload = res.json()

    item = payload["items"][0]
    assert item["status"]["Homologation"] == "approved"
    assert "Alan homologation" not in item["status"]
