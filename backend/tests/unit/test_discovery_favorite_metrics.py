"""Unit tests for discovery snapshot flatten onto Favorites grid keys (card #897)."""

from __future__ import annotations

from types import SimpleNamespace

from app.services.discovery_favorite_metrics import (
    build_promoted_favorite_metrics,
    flatten_discovery_grid_metrics,
    grid_metrics_from_snapshot,
    overlay_snapshot_grid_metrics,
)

SNAPSHOT_193 = {
    "sharpe_ratio": 0.31,
    "win_rate": 0.467,
    "total_return": 169.51,
    "total_return_pct": 16951,
    "max_drawdown": 0.165,
    "total_trades": 30,
    "profit_factor": 1.42,
}


def test_grid_metrics_from_snapshot_maps_aliases_and_pct_pair():
    grid = grid_metrics_from_snapshot(
        {"sharpe": 0.31, "win_rate": 0.467, "total_return_pct": 16951, "trades_count": 30}
    )
    assert grid["sharpe_ratio"] == 0.31
    assert grid["win_rate"] == 0.467
    assert grid["total_return_pct"] == 16951
    assert grid["total_return"] == 169.51
    assert grid["total_trades"] == 30


def test_flatten_discovery_get_fills_193_without_promote():
    stored = {
        "origin_type": "discovery_sweep",
        "sweep_id": "sw-193",
        "result_id": "RS-B109ED2C80",
        "strategy_identity_key": "id-193",
        "evidence_fingerprint": "fp-193",
        "metrics_snapshot": SNAPSHOT_193,
        "promoted_at": "2026-09-11T00:00:00Z",
    }
    flat = flatten_discovery_grid_metrics(stored)
    assert flat["sharpe_ratio"] == 0.31
    assert flat["total_trades"] == 30
    assert flat["win_rate"] == 0.467
    assert flat["total_return_pct"] == 16951
    assert flat["max_drawdown"] == 0.165
    assert flat["profit_factor"] == 1.42
    assert flat["origin_type"] == "discovery_sweep"
    assert flat["result_id"] == "RS-B109ED2C80"
    assert flat["metrics_snapshot"] == SNAPSHOT_193


def test_flatten_does_not_rewrite_combo_saved():
    combo = {"total_return_pct": 12.3, "total_trades": 8, "sharpe_ratio": 1.4}
    assert flatten_discovery_grid_metrics(combo) is combo


def test_overlay_keeps_snapshot_keys_after_regenerated_merge():
    stored = {
        "origin_type": "discovery_sweep",
        "result_id": "RS-B109ED2C80",
        "metrics_snapshot": SNAPSHOT_193,
        "sharpe_ratio": 0.31,
        "total_trades": 30,
        "win_rate": 0.467,
        "total_return": 169.51,
        "total_return_pct": 16951,
        "max_drawdown": 0.165,
    }
    merged = {
        **stored,
        "sharpe_ratio": 0.01,
        "total_trades": 12,
        "win_rate": 0.333,
        "total_return": -0.1392,
        "total_return_pct": -13.92,
        "max_drawdown": None,
        "trades": [{"profit": -0.1}] * 12,
    }
    restored = overlay_snapshot_grid_metrics(merged, source=stored)
    assert restored["sharpe_ratio"] == 0.31
    assert restored["total_trades"] == 30
    assert restored["win_rate"] == 0.467
    assert restored["total_return_pct"] == 16951
    assert restored["max_drawdown"] == 0.165
    assert restored["origin_type"] == "discovery_sweep"
    assert restored["metrics_snapshot"] == SNAPSHOT_193
    assert len(restored["trades"]) == 12


def test_build_promoted_favorite_metrics_copies_grid_keys():
    result = SimpleNamespace(
        id="RS-PRO",
        sweep_id="sw-1",
        strategy_identity_key="id-1",
        evidence_fingerprint="fp-1",
        template_version="v1",
        parameters={"fast": 7},
        metrics=SNAPSHOT_193,
        sharpe_ratio=0.31,
        win_rate=0.467,
        max_drawdown=0.165,
        profit_factor=1.42,
        trades_count=30,
    )
    payload = build_promoted_favorite_metrics(result, promoted_at="2026-09-11T00:00:00Z")
    assert payload["origin_type"] == "discovery_sweep"
    assert payload["metrics_snapshot"] == SNAPSHOT_193
    assert payload["sharpe_ratio"] == 0.31
    assert payload["total_trades"] == 30
    assert payload["total_return_pct"] == 16951
    assert payload["promoted_at"] == "2026-09-11T00:00:00Z"
