import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import coordination_comments_service, coordination_service


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def tmp_project(monkeypatch, tmp_path: Path):
    """Create a temporary project root and monkeypatch coordination services to use it."""

    # temp project structure
    (tmp_path / "docs" / "coordination").mkdir(parents=True)

    def _project_root():
        return tmp_path

    def _coord_dir():
        return tmp_path / "docs" / "coordination"

    # Patch both modules (coordination_comments_service imports these symbols).
    monkeypatch.setattr(coordination_service, "project_root", _project_root)
    monkeypatch.setattr(coordination_service, "coordination_dir", _coord_dir)
    monkeypatch.setattr(coordination_comments_service, "project_root", _project_root)
    monkeypatch.setattr(coordination_comments_service, "coordination_dir", _coord_dir)

    return tmp_path


def test_parse_status_section_only():
    md = """# my-change

## Status
- PO: done
- DEV: in progress

## Notes
- DEV: blocked
"""
    status = coordination_service.parse_status(md)
    assert status == {"PO": "done", "DEV": "in progress"}


def test_alan_fallback_for_missing_explicit_fields_affects_column_and_archived():
    md = """# legacy-change

## Status
- PO: done
- DEV: in progress
- QA: done
- Alan (Stakeholder): approved
"""
    status = coordination_service.parse_status(md)

    # Fallback should treat stakeholder value as both approval + homologation when missing.
    archived = coordination_service.is_archived(md, status)
    assert archived is False  # DEV not done

    col = coordination_service.derive_column(status, archived=archived)
    assert col == "DEV"

    # If DEV becomes done, the all-gates-complete archived rule should fire.
    md2 = md.replace("DEV: in progress", "DEV: done")
    status2 = coordination_service.parse_status(md2)
    archived2 = coordination_service.is_archived(md2, status2)
    assert archived2 is True


def test_parse_status_normalizes_legacy_alan_homologation_label():
    md = """# legacy-homologation

## Status
- PO: done
- Alan homologation: approved
"""

    status = coordination_service.parse_status(md)

    assert status["Homologation"] == "approved"
    assert "Alan homologation" not in status


def test_archived_by_closed_heading_overrides_gates():
    md = """# closed-change

## Status
- PO: in progress
- DEV: not started
- Alan approval: not reviewed

## Closed
This change is archived.
"""
    status = coordination_service.parse_status(md)
    archived = coordination_service.is_archived(md, status)
    assert archived is True
    assert coordination_service.derive_column(status, archived=archived) == "Archived"


def test_derive_column_gate_order_includes_design_between_po_and_approval():
    md = """# change

## Status
- PO: in progress
- DEV: done
- QA: done
- Alan approval: approved
- Homologation: approved
"""
    status = coordination_service.parse_status(md)
    assert coordination_service.derive_column(status, archived=False) == "PO"

    # PO done but DESIGN incomplete => DESIGN
    md2 = """# change

## Status
- PO: done
- DESIGN: in progress
- DEV: done
- QA: done
- Alan approval: approved
- Homologation: approved
"""
    status2 = coordination_service.parse_status(md2)
    assert coordination_service.derive_column(status2, archived=False) == "DESIGN"

    # Backward compat: missing DESIGN => skipped => proceed to Alan approval
    md3 = """# change

## Status
- PO: done
- DEV: done
- QA: done
- Alan approval: reviewed
- Homologation: approved
"""
    status3 = coordination_service.parse_status(md3)
    assert coordination_service.derive_column(status3, archived=False) == "Alan approval"



def test_comments_service_append_only_and_sorted(tmp_project: Path):
    # Create a known change.
    cid = "my-change"
    (tmp_project / "docs" / "coordination" / f"{cid}.md").write_text("# my-change\n\n## Status\n- PO: done\n", encoding="utf-8")

    c1 = coordination_comments_service.add_comment(cid, author="Alan", body="first")
    c2 = coordination_comments_service.add_comment(cid, author="Alan", body="second")

    # File should be JSONL with 2 lines.
    p = tmp_project / "data" / "coordination_comments" / f"{cid}.jsonl"
    lines = p.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["id"] == c1["id"]
    assert json.loads(lines[1])["id"] == c2["id"]

    items = coordination_comments_service.list_comments(cid)
    assert [it["id"] for it in items] == [c1["id"], c2["id"]]


def test_comments_service_validation_and_unknown_change(tmp_project: Path):
    cid = "my-change"
    (tmp_project / "docs" / "coordination" / f"{cid}.md").write_text("# my-change\n\n## Status\n- PO: done\n", encoding="utf-8")

    with pytest.raises(ValueError):
        coordination_comments_service.add_comment(cid, author="", body="ok")
    with pytest.raises(ValueError):
        coordination_comments_service.add_comment(cid, author="Alan", body="   ")
    with pytest.raises(ValueError):
        coordination_comments_service.add_comment(cid, author="Alan", body="x" * 2001)

    with pytest.raises(FileNotFoundError):
        coordination_comments_service.list_comments("unknown-change")


def test_comments_endpoints_required_fields_and_limits(tmp_project: Path, client: TestClient):
    cid = "my-change"
    (tmp_project / "docs" / "coordination" / f"{cid}.md").write_text("# my-change\n\n## Status\n- PO: done\n", encoding="utf-8")

    # Unknown change => 404
    r = client.get(f"/api/coordination/changes/unknown/comments")
    assert r.status_code == 404

    # Missing required fields => 422 (pydantic)
    r = client.post(f"/api/coordination/changes/{cid}/comments", json={"body": "hi"})
    assert r.status_code == 422

    # Empty author/body => 400 (service validation)
    r = client.post(f"/api/coordination/changes/{cid}/comments", json={"author": " ", "body": "hi"})
    assert r.status_code == 400

    r = client.post(f"/api/coordination/changes/{cid}/comments", json={"author": "Alan", "body": "   "})
    assert r.status_code == 400

    # Too-long body => 422 (pydantic max_length)
    r = client.post(
        f"/api/coordination/changes/{cid}/comments",
        json={"author": "Alan", "body": "x" * 2001},
    )
    assert r.status_code == 422

    # Append-only behavior via endpoints.
    r1 = client.post(f"/api/coordination/changes/{cid}/comments", json={"author": "Alan", "body": "one"})
    assert r1.status_code == 200

    r2 = client.post(f"/api/coordination/changes/{cid}/comments", json={"author": "Alan", "body": "two"})
    assert r2.status_code == 200

    r3 = client.get(f"/api/coordination/changes/{cid}/comments")
    assert r3.status_code == 200
    payload = r3.json()
    assert payload["change_id"] == cid
    assert [it["body"] for it in payload["items"]] == ["one", "two"]
