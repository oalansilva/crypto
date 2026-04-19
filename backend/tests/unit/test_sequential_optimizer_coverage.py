from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import pytest

import app.services.sequential_optimizer as sequential_optimizer
from app.services.sequential_optimizer import SequentialOptimizer


def _fake_schema(**param_defs):
    return SimpleNamespace(
        name="mock",
        parameters={
            name: SimpleNamespace(
                default=definition["default"],
                optimization_range=SimpleNamespace(
                    min=definition["min"],
                    max=definition["max"],
                    step=definition["step"],
                ),
                description=definition["description"],
                market_standard=definition["market_standard"],
            )
            for name, definition in param_defs.items()
        },
    )


def test_generate_stages_raises_unknown_strategy():
    optimizer = SequentialOptimizer(checkpoint_dir="/tmp/seq-optimizer-tests")
    with pytest.raises(ValueError, match="Unknown strategy"):
        optimizer.generate_stages("unknown", "BTC/USDT")


def test_generate_stages_covers_timeframe_and_indicator_ranges(monkeypatch):
    optimizer = SequentialOptimizer(checkpoint_dir="/tmp/seq-optimizer-tests")
    monkeypatch.setattr(
        sequential_optimizer,
        "get_indicator_schema",
        lambda _: _fake_schema(
            ema={
                "default": 3,
                "min": 3,
                "max": 4,
                "step": 1,
                "description": "EMA period",
                "market_standard": "default",
            }
        ),
    )

    stages = optimizer.generate_stages(
        strategy="mock",
        symbol="BTC/USDT",
        include_risk=False,
    )

    assert stages[0]["stage_name"] == "Timeframe"
    assert stages[0]["stage_num"] == 1
    assert stages[0]["parameter"] == "timeframe"
    assert stages[0]["values"] == ["5m", "15m", "30m", "1h", "2h", "4h", "1d"]
    assert stages[1]["stage_num"] == 2
    assert stages[1]["parameter"] == "ema"
    assert stages[1]["values"] == [3, 4]


def test_generate_stages_custom_ranges_and_zero_stop_loss(monkeypatch):
    optimizer = SequentialOptimizer(checkpoint_dir="/tmp/seq-optimizer-tests")
    monkeypatch.setattr(
        sequential_optimizer,
        "get_indicator_schema",
        lambda _: _fake_schema(
            stop_loss={
                "default": 0.005,
                "min": 0.01,
                "max": 0.02,
                "step": 0.01,
                "description": "stop loss",
                "market_standard": "default",
            }
        ),
    )

    stages = optimizer.generate_stages(
        strategy="mock",
        symbol="BTC/USDT",
        fixed_timeframe="1h",
        custom_ranges={"stop_loss": {"min": 0.001, "max": 0.002, "step": 0}},
        include_risk=True,
    )

    # Risk params outside custom map are ignored, but stop_loss can appear in both
    # indicator + risk schema paths and both get tested with the same range.
    assert [stage["stage_num"] for stage in stages] == [1, 2]
    assert stages[0]["parameter"] == "stop_loss"
    assert stages[1]["parameter"] == "stop_loss"
    assert stages[0]["values"] == [0.0, 0.001]
    assert stages[1]["values"] == [0.0, 0.001]


def test_get_full_history_dates_uses_timestamp_column(monkeypatch):
    optimizer = SequentialOptimizer(checkpoint_dir="/tmp/seq-optimizer-tests")

    class Loader:
        def fetch_data(self, *args, **kwargs):
            return pd.DataFrame(
                {
                    "timestamp_utc": pd.to_datetime(
                        ["2026-04-01T10:00:00Z", "2026-04-02T10:00:00Z"]
                    )
                }
            )

    monkeypatch.setattr(sequential_optimizer, "IncrementalLoader", Loader)
    assert optimizer.get_full_history_dates("BTC/USDT") == (
        "2026-04-01T10:00:00+00:00",
        "2026-04-02T10:00:00+00:00",
    )


def test_get_full_history_dates_raises_when_empty(monkeypatch):
    optimizer = SequentialOptimizer(checkpoint_dir="/tmp/seq-optimizer-tests")

    class Loader:
        def fetch_data(self, *args, **kwargs):
            return pd.DataFrame()

    monkeypatch.setattr(sequential_optimizer, "IncrementalLoader", Loader)
    with pytest.raises(ValueError, match="No data available"):
        optimizer.get_full_history_dates("BTC/USDT")


def test_checkpoint_roundtrip_and_incomplete_jobs(tmp_path):
    optimizer = SequentialOptimizer(checkpoint_dir=str(tmp_path / "checkpoints"))

    state = {"job_id": "job-1", "status": "in_progress"}
    optimizer.create_checkpoint("job-1", state)

    loaded = optimizer.load_checkpoint("job-1")
    assert loaded is not None
    assert loaded["job_id"] == "job-1"
    assert loaded["status"] == "in_progress"
    assert "timestamp" in loaded

    (tmp_path / "checkpoints" / "job-2.json").write_text(
        '{"status":"done","job_id":"job-2"}',
        encoding="utf-8",
    )
    (tmp_path / "checkpoints" / "job-3.json").write_text(
        '{"status":"in_progress","job_id":"job-3"}',
        encoding="utf-8",
    )

    incomplete = optimizer.find_incomplete_jobs()
    assert {item["job_id"] for item in incomplete} == {"job-1", "job-3"}

    optimizer.delete_checkpoint("job-1")
    assert optimizer.load_checkpoint("job-1") is None


@pytest.mark.asyncio
async def test_run_stage_selects_best_result_and_checkpoints(monkeypatch, tmp_path):
    optimizer = SequentialOptimizer(checkpoint_dir=str(tmp_path / "checkpoints"))
    monkeypatch.setattr(
        optimizer,
        "get_full_history_dates",
        lambda _symbol: ("2026-01-01", "2026-01-31"),
    )

    call_count = []

    def run_backtest(config):
        call_count.append(config)
        return {
            "results": {
                "Test": {
                    "metrics": {"total_pnl": 2 if config["params"]["macd"] == 11 else -1},
                    "trades": [{"trade": 1}],
                }
            }
        }

    monkeypatch.setattr(optimizer.backtest_service, "run_backtest", run_backtest)

    stage = {
        "stage_num": 2,
        "stage_name": "Period",
        "parameter": "lookback",
        "values": [10, 11],
    }
    result = await optimizer.run_stage(
        job_id="job-1",
        stage_config=stage,
        symbol="BTC/USDT",
        strategy="macd",
        locked_params={"timeframe": "1h"},
        start_from_test=1,
    )

    assert result["best_value"] == 11
    assert result["best_result"]["test_num"] == 2
    assert len(call_count) == 1
    assert call_count[0]["stop_pct"] is None
    assert call_count[0]["take_pct"] is None


@pytest.mark.asyncio
async def test_run_stage_fallbacks_on_bad_payload(monkeypatch, tmp_path):
    optimizer = SequentialOptimizer(checkpoint_dir=str(tmp_path / "checkpoints"))
    monkeypatch.setattr(
        optimizer,
        "get_full_history_dates",
        lambda _symbol: ("2026-01-01", "2026-01-31"),
    )

    def run_backtest_error(_config):
        return {"results": {"Test": {"error": "boom"}}}

    monkeypatch.setattr(optimizer.backtest_service, "run_backtest", run_backtest_error)

    stage = {
        "stage_num": 3,
        "stage_name": "Stop",
        "parameter": "stop_loss",
        "values": [0.1],
    }
    result = await optimizer.run_stage(
        job_id="job-2",
        stage_config=stage,
        symbol="BTC/USDT",
        strategy="macd",
        locked_params={"timeframe": "1h"},
    )

    assert result["results"][0]["metrics"]["total_pnl"] == 0
    assert "error" in result["results"][0]["metrics"]


@pytest.mark.asyncio
async def test_resume_from_checkpoint_reuses_stage_from_checkpoint(monkeypatch, tmp_path):
    optimizer = SequentialOptimizer(checkpoint_dir=str(tmp_path / "checkpoints"))

    checkpoint = {
        "symbol": "BTC/USDT",
        "strategy": "macd",
        "current_stage": 2,
        "tests_completed": 1,
        "locked_params": {"timeframe": "1h"},
    }
    monkeypatch.setattr(optimizer, "load_checkpoint", lambda _job_id: checkpoint)
    monkeypatch.setattr(
        optimizer,
        "generate_stages",
        lambda strategy, symbol: [
            {"stage_num": 1, "stage_name": "Stage1", "parameter": "timeframe", "values": [1]},
            {"stage_num": 2, "stage_name": "Stage2", "parameter": "lookback", "values": [5, 6]},
        ],
    )

    payload = {"called": False}

    async def fake_run_stage(*args, **kwargs):
        payload["called"] = True
        return {"payload": "ok", "start_from_test": kwargs["start_from_test"]}

    monkeypatch.setattr(optimizer, "run_stage", fake_run_stage)

    out = await optimizer.resume_from_checkpoint("job-2")
    assert payload["called"] is True
    assert out == {"payload": "ok", "start_from_test": 1}


@pytest.mark.asyncio
async def test_resume_from_checkpoint_without_checkpoint_raises(monkeypatch):
    optimizer = SequentialOptimizer(checkpoint_dir="/tmp/seq-optimizer-tests")
    monkeypatch.setattr(optimizer, "load_checkpoint", lambda _job_id: None)
    with pytest.raises(ValueError, match="No checkpoint found"):
        await optimizer.resume_from_checkpoint("missing")
