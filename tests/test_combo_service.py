import sqlite3
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.combo_service import ComboService


def _init_combo_db(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE combo_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            is_example BOOLEAN DEFAULT 0,
            is_prebuilt BOOLEAN DEFAULT 0,
            is_readonly BOOLEAN DEFAULT 0,
            template_data JSON NOT NULL,
            optimization_schema JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def test_create_template_success(tmp_path: Path) -> None:
    db_path = tmp_path / "combo.db"
    _init_combo_db(db_path)

    service = ComboService(db_path=str(db_path))
    saved = service.create_template(
        name="lab_test_template",
        template_data={
            "indicators": [
                {"type": "ema", "alias": "fast", "params": {"length": 10}},
                {"type": "ema", "alias": "slow", "params": {"length": 50}},
            ],
            "entry_logic": "fast > slow",
            "exit_logic": "fast < slow",
            "stop_loss": 0.02,
        },
        category="custom",
        metadata={"one_liner": "Template de teste"},
    )

    assert saved["name"] == "lab_test_template"
    assert saved["category"] == "custom"
    assert saved["metadata"]["one_liner"] == "Template de teste"
    assert saved["entry_logic"] == "fast > slow"
    assert saved["exit_logic"] == "fast < slow"
    assert saved["stop_loss"]["default"] == 0.02


def test_create_template_missing_entry_logic(tmp_path: Path) -> None:
    db_path = tmp_path / "combo.db"
    _init_combo_db(db_path)

    service = ComboService(db_path=str(db_path))

    with pytest.raises(ValueError, match="entry_logic"):
        service.create_template(
            name="bad_template",
            template_data={
                "indicators": [{"type": "rsi", "params": {"length": 14}}],
                "exit_logic": "rsi > 70",
            },
        )
