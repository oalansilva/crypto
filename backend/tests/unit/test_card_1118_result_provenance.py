"""Card #1118, tarefa 5.4: o resultado da Descoberta registra a proveniência e a amostra."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services import discovery_inputs
from app.services.discovery_service import DiscoveryService
from app.services.market_history import snapshots
from app.services.market_history.model import SeriesRef
from app.services.market_history.sample import ExecutionSample
from app.services.market_history.schema import ADD_COLUMNS_SQL, execute_all, side_table_statements
from test_discovery_ranking_metrics import (  # noqa: F401  (fixtures e apoio do card #599)
    _patch_combo_metadata,
    _seed_running_combination,
    _supervised_boundary,
)


def _series() -> SeriesRef:
    return SeriesRef(
        series_id=7,
        asset_id="binance:spot:ETH/USDT",
        symbol="ETH/USDT",
        asset_class="crypto",
        source="binance_spot",
        session="24x7",
        adjustment="na",
        timeframe="1d",
        origin="native",
        data_version=7,
        physical_timeframe="1d",
    )


def test_result_records_series_provenance_and_the_sample_reference(
    postgres_isolation, unit_database_url, tmp_path, monkeypatch
):
    from app.models_discovery import DiscoveryResult
    from app.tasks.discovery_tasks import run_combination

    monkeypatch.setenv("MARKET_HISTORY_SNAPSHOT_DIR", str(tmp_path / "snapshots"))
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        execute_all(conn, side_table_statements())
        execute_all(conn, ADD_COLUMNS_SQL)
        conn.exec_driver_sql("DELETE FROM execution_data_snapshots")
        conn.exec_driver_sql("DELETE FROM discovery_results")
        conn.exec_driver_sql("DELETE FROM discovery_combinations")
        conn.exec_driver_sql("DELETE FROM discovery_sweeps")

    index = pd.date_range("2024-01-01", periods=40, freq="1D", tz="UTC", name="candle_time")
    frame = pd.DataFrame(
        {
            "open": 1.0,
            "high": 2.0,
            "low": 0.5,
            "close": [1.0 + i for i in range(40)],
            "volume": 3.0,
        },
        index=index,
    )
    sample = ExecutionSample("discovery", engine=engine)
    sample.freeze("candles", _series(), "2024-01-01", "2024-02-10", frame)
    sample.freeze("intraday", _series(), "2024-01-01", "2024-02-10", frame)
    manifest = {
        "snapshot_id": sample.snapshot_id,
        "files": {
            role: {
                "sha256": sample.entry(role)["sha256"],
                "rows": 40,
                "segments": sample.entry(role)["segments"],
            }
            for role in ("candles", "intraday")
        },
        "provenance": sample.provenance("candles"),
    }

    Session = sessionmaker(bind=engine)
    db = Session()
    combo = _seed_running_combination(db, sweep_id="sw-1118")
    combo.input_snapshot = {**combo.input_snapshot, "candle_manifest": manifest}
    db.commit()
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 2, 9, tzinfo=timezone.utc)

    class FakeOptimizer:
        def run_optimization(self, **_kwargs):
            return {
                "best_metrics": {
                    "sharpe_ratio": 1.0,
                    "profit_factor": 1.2,
                    "max_drawdown": 0.1,
                    "win_rate": 0.5,
                    "cagr": 0.2,
                    "calmar_ratio": 2.0,
                    "benchmark": {"cagr": 0.1},
                },
                "trades": [{"entry_time": start.isoformat(), "profit": 0.1}] * 40,
                "candles": [
                    {"timestamp_utc": start.isoformat(), "close": 100.0},
                    {"timestamp_utc": end.isoformat(), "close": 110.0},
                ],
                "best_parameters": {"direction": "long"},
                "data_source": "ccxt",
            }

    _patch_combo_metadata(monkeypatch)
    monkeypatch.setattr("app.services.combo_optimizer.ComboOptimizer", FakeOptimizer)
    run_combination(db, combo, owner="worker-605")
    db.refresh(combo)
    result = db.query(DiscoveryResult).filter(DiscoveryResult.id == combo.result_id).one()

    assert result.candle_source == "Binance Spot" and result.candle_version == "7"
    assert (result.data_source, result.asset_class, result.session, result.adjustment) == (
        "Binance Spot",
        "crypto",
        "24x7",
        "na",
    )
    assert result.timeframe_origin == "native" and result.data_version == 7
    assert result.period_requested == {
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-02-10T00:00:00Z",
    }
    assert result.period_covered["candles"] == 40
    assert result.snapshot_id == sample.snapshot_id
    row = snapshots.get_manifest(engine, sample.snapshot_id)
    assert row["finished_at"] is not None  # o prazo de 30 dias conta daqui

    # O Decidir recebe a proveniência e o estado da amostra de cada resultado.
    ranked = DiscoveryService().leaderboard("sw-1118", db=db)[0]
    payload = next(r for r in ranked if r["result_id"] == result.id)
    assert payload["provenance"]["data_source"] == "Binance Spot"
    assert payload["provenance"]["data_version"] == 7
    assert payload["snapshot_id"] == sample.snapshot_id
    assert payload["sample"]["state"] == "kept" and payload["sample"]["retain_until"].endswith("Z")

    # Depois do prazo (ou sem manifesto), "não reproduzível exatamente".
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "UPDATE execution_data_snapshots SET retain_until = now() - interval '1 day'"
        )
    expired = DiscoveryService().leaderboard("sw-1118", db=db)[0][0]
    assert expired["sample"]["state"] == "expired"
    db.close()
    discovery_inputs._SAMPLE_FRAMES.clear()
