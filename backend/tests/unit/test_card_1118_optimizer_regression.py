"""Card #1118, tarefa 4.5: otimização de cripto pelo histórico existente dá os mesmos números."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from app.services.combo_optimizer import ComboOptimizer
from app.strategies.combos.combo_strategy import ComboStrategy
from app.services.market_history import facade, snapshots
from app.services.market_history.cache import ParquetReadCache
from app.services.market_history.schema import execute_all, side_table_statements
from app.services.market_history.service import HistoryService
from market_history_support import FakeCcxt, history_schema
from oracles._build_card_945 import apply_param_overrides, load_templates, metadata_from_export
from src.data.incremental_loader import IncrementalLoader

pytestmark = pytest.mark.timeout(600)

SYMBOL = "TST1118/USDT"
START, END = "2025-01-01", "2026-02-05"


def _walk(index: pd.DatetimeIndex, seed: int, base: float, vol: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = base * np.exp(np.cumsum(rng.normal(0.0002, vol, len(index))))
    open_ = np.concatenate([[base], close[:-1]])
    high = np.maximum(open_, close) * (1 + rng.uniform(0, vol / 2, len(index)))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, vol / 2, len(index)))
    return pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": rng.uniform(10, 100, len(index)),
        },
        index=index,
    ).rename_axis("candle_time")


def _frames() -> dict[str, pd.DataFrame]:
    daily = pd.date_range("2025-01-01", "2026-02-12", freq="1D", tz="UTC")
    intraday = pd.date_range("2025-01-01", "2026-02-12", freq="15min", tz="UTC")
    return {"1d": _walk(daily, 11, 20000.0, 0.025), "15m": _walk(intraday, 12, 20000.0, 0.004)}


def _legacy_parquet(frames: dict[str, pd.DataFrame]) -> list[Path]:
    """Cache Parquet antigo (o que as análises liam antes) no diretório padrão do carregador."""

    loader = IncrementalLoader()
    paths = []
    for tf, frame in frames.items():
        out = frame.reset_index().rename(columns={"candle_time": "timestamp_utc"})
        out["timestamp"] = pd.DatetimeIndex(out["timestamp_utc"]).as_unit("ms").asi8
        path = Path(loader._get_parquet_path(SYMBOL, tf))
        out.to_parquet(path, index=False)
        paths.append(path)
    return paths


def _fixed_ranges():
    return {
        "ema_short": {"min": 9, "max": 9, "step": 1},
        "sma_medium": {"min": 21, "max": 21, "step": 1},
        "sma_long": {"min": 50, "max": 50, "step": 1},
        "stop_loss": {"min": 0.02, "max": 0.02, "step": 0.0001},
    }


class _FakeTemplates:
    """O banco de teste não traz os templates semeados: usa a exportação congelada do card #945."""

    def __init__(self) -> None:
        self.metadata = metadata_from_export(load_templates()["multi_ma_crossover"])

    def get_template_metadata(self, _name):
        return self.metadata

    def create_strategy(self, template_name, parameters=None):
        meta = self.metadata
        template = {
            "indicators": meta["indicators"],
            "stop_loss": meta.get("stop_loss", 0.015),
        }
        indicators, stop_loss = apply_param_overrides(template, parameters or {})
        return ComboStrategy(
            indicators=indicators,
            entry_logic=meta["entry_logic"],
            exit_logic=meta["exit_logic"],
            stop_loss=stop_loss,
            derived_features=meta.get("derived_features") or [],
            direction=(parameters or {}).get("direction", "long"),
        )


def _optimize():
    optimizer = ComboOptimizer(workers=1)
    optimizer.combo_service = _FakeTemplates()
    return optimizer.run_optimization(
        template_name="multi_ma_crossover",
        symbol=SYMBOL,
        timeframe="1d",
        data_source="ccxt",
        start_date=START,
        end_date=END,
        custom_ranges=_fixed_ranges(),
        deep_backtest=True,
    )


def test_optimization_gives_the_same_numbers_before_and_after_the_switch(
    unit_database_url, tmp_path, monkeypatch
):
    frames = _frames()
    paths = _legacy_parquet(frames)
    app_engine = create_engine(unit_database_url)
    with app_engine.begin() as conn:
        execute_all(conn, side_table_statements())
    try:
        monkeypatch.setenv("MARKET_HISTORY_UNIFIED", "0")
        before = _optimize()
        assert before["best_metrics"] and before["candles"] and "snapshot_id" not in before

        monkeypatch.setenv("MARKET_HISTORY_UNIFIED", "1")
        monkeypatch.setenv("MARKET_HISTORY_SNAPSHOT_DIR", str(tmp_path / "snapshots"))
        with history_schema(unit_database_url) as engine:
            ccxt = FakeCcxt({(SYMBOL, "1d"): frames["1d"], (SYMBOL, "15m"): frames["15m"]})
            service = HistoryService(engine, ccxt_client=ccxt, update_ttl_seconds=0)
            facade.set_history_service(service, ParquetReadCache(tmp_path / "series"))
            try:
                after = _optimize()
            finally:
                facade.set_history_service(None, None)
        assert after["snapshot_id"]
        assert before["best_metrics"] == after["best_metrics"]
        assert before["best_parameters"] == after["best_parameters"]
        assert before["trades"] == after["trades"]
        assert [c["close"] for c in before["candles"]] == [c["close"] for c in after["candles"]]
        assert before["execution_mode"] == after["execution_mode"]
        prov = after["data_provenance"]
        assert prov["data_source"] == "Binance Spot" and prov["timeframe_origin"] == "native"
        assert prov["snapshot_id"] == after["snapshot_id"]
        manifest = snapshots.get_manifest(app_engine, after["snapshot_id"])
        assert {e["role"] for e in manifest["series"]} == {"candles", "intraday"}
        assert manifest["pinned"] is False and manifest["finished_at"] is not None
    finally:
        for path in paths:
            path.unlink(missing_ok=True)
        with app_engine.begin() as conn:
            conn.execute(
                text("DELETE FROM execution_data_snapshots WHERE owner_ref LIKE :o"),
                {"o": f"optimization:{SYMBOL}%"},
            )
        app_engine.dispose()
