from __future__ import annotations

import json
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import SystemPreference
from app.services import binance_prices, change_tasks_service, preset_service, upstream_guard
from app.services.binance_prices import compute_usdt_price_for_asset, fetch_all_binance_prices
from app.services.change_tasks_service import (
    get_change_tasks_checklist,
    parse_tasks_markdown,
    toggle_task_checkbox,
)
from app.services.system_preferences_service import (
    SIGNAL_HISTORY_ALLOW_BUY_KEY,
    delete_system_preference_value,
    get_system_preference,
    get_system_preference_bool,
    get_system_preference_float,
    get_system_preference_int,
    get_system_preference_value,
    mask_secret,
    set_optional_system_preference_value,
    set_system_preference_value,
)
from app.strategies.combos.helpers import above, below, crossover, crossunder
from app.symbols_config import (
    _base_ends_with_up_or_down,
    get_excluded_symbols,
    is_excluded_symbol,
    reload_excluded_symbols,
)
import app.symbols_config as symbols_config


@pytest.fixture
def app_db_session():
    engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/postgres")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def test_combo_helper_functions_cover_cross_and_window_logic():
    left = pd.Series([1, 3, 4], index=[0, 1, 2])
    right = pd.Series([2, 2, 3], index=[0, 1, 2])
    short = pd.Series([1], index=[0])

    assert list(crossover(left, right)) == [False, True, False]
    assert list(crossunder(right, left)) == [False, True, False]
    assert list(above(left, right, periods=2)) == [False, False, True]
    assert list(below(right, left, periods=2)) == [False, False, True]
    assert list(crossover(short, short)) == [False]
    assert list(above(short, short, periods=2)) == [False]


def test_symbols_config_supports_reload_and_symbol_filters(tmp_path, monkeypatch):
    config_dir = tmp_path / "backend"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "excluded_symbols.json"
    config_path.write_text(
        json.dumps({"excluded_symbols": [" btc/usdt ", "eth/usdt", "", None]}),
        encoding="utf-8",
    )

    monkeypatch.setattr(symbols_config, "CONFIG_PATH", config_path)
    monkeypatch.setattr(symbols_config, "_EXCLUDED", frozenset())

    reloaded = reload_excluded_symbols()

    assert reloaded == frozenset({"BTC/USDT", "ETH/USDT"})
    assert get_excluded_symbols() == reloaded
    assert _base_ends_with_up_or_down("ADAUP/USDT") is True
    assert _base_ends_with_up_or_down("btc/usdt") is False
    assert _base_ends_with_up_or_down("BTCUSDT") is False
    assert is_excluded_symbol("btc/usdt") is True
    assert is_excluded_symbol("adadown/usdt") is True
    assert is_excluded_symbol("") is True
    assert is_excluded_symbol("sol/usdt") is False


def test_symbols_config_falls_back_when_config_is_missing_or_invalid(tmp_path, monkeypatch):
    missing_path = tmp_path / "missing.json"
    monkeypatch.setattr(symbols_config, "CONFIG_PATH", missing_path)
    monkeypatch.setattr(symbols_config, "_EXCLUDED", frozenset())
    assert reload_excluded_symbols() == symbols_config._DEFAULT_SYMBOLS

    broken_path = tmp_path / "broken.json"
    broken_path.write_text("{invalid json", encoding="utf-8")
    monkeypatch.setattr(symbols_config, "CONFIG_PATH", broken_path)
    assert reload_excluded_symbols() == symbols_config._DEFAULT_SYMBOLS


def test_compute_usdt_price_for_asset_supports_direct_brl_btc_and_none():
    prices = {
        "BTCUSDT": 60000.0,
        "ETHBTC": 0.05,
        "SOLUSDT": 150.0,
        "USDTBRL": 5.0,
    }

    assert compute_usdt_price_for_asset("USDT", prices) == 1.0
    assert compute_usdt_price_for_asset("USDC", prices) == 1.0
    assert compute_usdt_price_for_asset("SOL", prices) == 150.0
    assert compute_usdt_price_for_asset("ETH", prices) == 3000.0
    assert compute_usdt_price_for_asset("BRL", prices) == pytest.approx(0.2)
    assert compute_usdt_price_for_asset("DOGE", prices) is None
    assert compute_usdt_price_for_asset("", prices) is None


def test_fetch_all_binance_prices_ignores_bad_rows(monkeypatch):
    payload = [
        {"symbol": "BTCUSDT", "price": "64000.0"},
        {"symbol": "ETHUSDT", "price": "not-a-number"},
        {"symbol": "", "price": "1.0"},
    ]

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    monkeypatch.setattr(binance_prices.urllib.request, "urlopen", lambda *_a, **_k: _Response())
    monkeypatch.setenv("BINANCE_BASE_URL", "https://example.invalid")

    assert fetch_all_binance_prices() == {"BTCUSDT": 64000.0}


def test_get_presets_returns_expected_shapes(monkeypatch):
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 4, 18, 12, 0, 0)

    monkeypatch.setattr(preset_service, "datetime", FrozenDateTime)

    presets = preset_service.get_presets()

    assert len(presets) == 4
    assert presets[0].id == "btc-swing-2y"
    assert presets[0].config.symbol == "BTC/USDT"
    assert presets[1].config.timeframe == "1d"
    assert presets[2].config.mode == "run"
    assert presets[3].config.symbol == "LINK/USDT"
    assert presets[0].config.since.startswith("2024-")


def test_change_tasks_parser_toggle_and_archived_lookup(tmp_path, monkeypatch):
    change_id = "coverage-ratchet"
    active_tasks = tmp_path / "openspec" / "changes" / change_id / "tasks.md"
    active_tasks.parent.mkdir(parents=True)
    active_tasks.write_text(
        "\n".join(
            [
                "# Title",
                "## Implementation",
                "- [ ] 1.1 Build parser",
                "  - note child",
                "- [x] 1.2 Add tests",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(change_tasks_service, "project_root", lambda: tmp_path)

    parsed = parse_tasks_markdown(active_tasks.read_text(encoding="utf-8"))
    assert parsed[0].title == "Implementation"
    assert parsed[0].items[0].code == "1.1"
    assert parsed[0].items[0].children[0].checked is None

    assert toggle_task_checkbox(change_id, "1.1", True) is True
    payload = get_change_tasks_checklist(change_id)
    assert payload["change_id"] == change_id
    assert payload["sections"][0]["items"][0]["checked"] is True

    archived = (
        tmp_path / "openspec" / "changes" / "archive" / f"2026-04-18-{change_id}" / "tasks.md"
    )
    archived.parent.mkdir(parents=True)
    archived.write_text("## Archived\n- [ ] 1.1 Restore\n", encoding="utf-8")

    active_tasks.unlink()
    archived_payload = get_change_tasks_checklist(change_id)
    assert archived_payload["path"].endswith(f"archive/2026-04-18-{change_id}/tasks.md")


def test_change_tasks_service_handles_missing_changes(monkeypatch, tmp_path):
    monkeypatch.setattr(change_tasks_service, "project_root", lambda: tmp_path)
    assert toggle_task_checkbox("missing-change", "1.1", True) is False
    with pytest.raises(change_tasks_service.HTTPException) as exc:
        get_change_tasks_checklist("missing-change")
    assert exc.value.status_code == 404


def test_system_preferences_service_handles_missing_table_and_crud(app_db_session):
    broken_engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/postgres")
    BrokenSession = sessionmaker(autocommit=False, autoflush=False, bind=broken_engine)
    broken_db = BrokenSession()
    try:
        assert get_system_preference(broken_db, "missing") is None
    finally:
        broken_db.close()
        broken_engine.dispose()

    assert get_system_preference_value(app_db_session, SIGNAL_HISTORY_ALLOW_BUY_KEY) is None

    pref = set_system_preference_value(
        app_db_session,
        key=SIGNAL_HISTORY_ALLOW_BUY_KEY,
        value=" true ",
        updated_by_user_id="qa",
    )
    assert isinstance(pref, SystemPreference)
    assert get_system_preference_value(app_db_session, SIGNAL_HISTORY_ALLOW_BUY_KEY) == "true"
    assert (
        get_system_preference_bool(app_db_session, SIGNAL_HISTORY_ALLOW_BUY_KEY, default=False)
        is True
    )
    assert get_system_preference_int(app_db_session, "missing-int", default=7) == 7
    assert get_system_preference_float(app_db_session, "missing-float", default=1.5) == 1.5
    assert get_system_preference_bool(app_db_session, "missing-bool", default=True) is True

    updated = set_system_preference_value(
        app_db_session,
        key=SIGNAL_HISTORY_ALLOW_BUY_KEY,
        value="off",
        updated_by_user_id="dev",
    )
    assert updated.updated_by_user_id == "dev"
    assert (
        get_system_preference_bool(app_db_session, SIGNAL_HISTORY_ALLOW_BUY_KEY, default=True)
        is False
    )

    set_system_preference_value(
        app_db_session,
        key="custom-int",
        value="not-int",
        updated_by_user_id="qa",
    )
    set_system_preference_value(
        app_db_session,
        key="custom-float",
        value="not-float",
        updated_by_user_id="qa",
    )
    set_system_preference_value(
        app_db_session,
        key="custom-bool",
        value="maybe",
        updated_by_user_id="qa",
    )
    assert get_system_preference_int(app_db_session, "custom-int", default=9) == 9
    assert get_system_preference_float(app_db_session, "custom-float", default=2.5) == 2.5
    assert get_system_preference_bool(app_db_session, "custom-bool", default=False) is False

    assert (
        set_optional_system_preference_value(
            app_db_session,
            key=SIGNAL_HISTORY_ALLOW_BUY_KEY,
            value=None,
            updated_by_user_id="qa",
        )
        is None
    )
    assert delete_system_preference_value(app_db_session, key=SIGNAL_HISTORY_ALLOW_BUY_KEY) is False
    assert mask_secret(None) is None
    assert mask_secret("12345678") == "********"
    assert mask_secret("1234567890") == "1234****7890"


def test_upstream_guard_evaluates_changes_and_blocks_when_needed(monkeypatch, tmp_path):
    outputs = {
        ("branch", "--show-current"): "feature/coverage-ratchet\n",
        ("status", "--porcelain"): " M README.md\n?? qa_artifacts/tmp.txt\n?? notes.txt\n",
        ("ls-files", "--others", "--exclude-standard"): "qa_artifacts/tmp.txt\nnotes.txt\n",
        (
            "rev-parse",
            "--abbrev-ref",
            "--symbolic-full-name",
            "@{upstream}",
        ): "origin/feature/coverage-ratchet\n",
        ("log", "--oneline", "origin/feature/coverage-ratchet..HEAD"): "abc123 Commit one\n",
    }

    monkeypatch.setattr(
        upstream_guard,
        "_git",
        lambda _root, *args, check=True: outputs.get(tuple(args), ""),
    )
    monkeypatch.setenv("UPSTREAM_GUARD_IGNORE", "tmp/**:notes-to-ignore/**")

    result = upstream_guard.evaluate_upstream_guard(tmp_path, target_statuses=["QA"])

    assert result.ok is False
    assert result.branch == "feature/coverage-ratchet"
    assert result.relevant_tracked_changes == ["README.md"]
    assert result.relevant_untracked_changes == ["notes.txt"]
    assert "qa_artifacts/tmp.txt" in result.ignored_ephemeral_changes
    assert result.unpushed_commits == ["abc123 Commit one"]
    assert result.blocking_reasons

    with pytest.raises(upstream_guard.UpstreamGuardError, match="Publish relevant changes"):
        upstream_guard.require_upstream_published(tmp_path, target_statuses=["QA"])
