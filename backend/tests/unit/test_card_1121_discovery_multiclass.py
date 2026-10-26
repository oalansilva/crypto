"""Descoberta com cripto, ação e ETF na mesma varredura (card #1121, tarefas 5.1 e 5.2).

Contratos do backend: aquisição e congelamento por classe (``binance_equity`` para ação/ETF), amostra
única por ativo e tempo reaproveitada por outras combinações e por novas tentativas, "sem candles" como
amostra insuficiente com motivo, falha de coleta nas 3 tentativas sem derrubar a varredura, cobertura
pelo calendário de NY, identidade/precisão/convenções em cada resultado, estado por ativo, filtro de
classe no ranking e promoção de ação/ETF sem nível de estrela com as chaves ``analysis_*``. A
regressão de cripto confere que a varredura só de cripto segue igual.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.metrics.backtest_execution_costs import TRADING_FEE, fees_slippage_record
from app.services import discovery_inputs, discovery_multiclass
from app.services.discovery_resources import OperationalFailure
from app.tasks.discovery_tasks import _expected_candles_for_window, run_combination
from test_card_1118_api_and_catalog import public_db  # noqa: F401
from test_discovery_insufficient_sample import (
    TEMPLATE_METADATA,
    _ensure_schema,
    _grant_possession,
    _patch_metadata,
    _patch_supervised,
)

# --------------------------------------------------------------------------- puras


def _utc(*args):
    return datetime(*args, tzinfo=timezone.utc)


def test_coverage_counts_new_york_sessions_for_equities_and_keeps_crypto_24x7():
    # Semana de 5 a 9 out. 2026 (seg a sex): candle 1d de ação na meia-noite de NY (04:00 UTC no verão).
    start, end = _utc(2026, 10, 5, 4), _utc(2026, 10, 9, 4)
    assert _expected_candles_for_window("1d", start, end, asset_class="stock") == 5
    # 4h: dois blocos por pregão (09:30–13:30 e 13:30–16:00); 1h: sete; 15m: vinte e seis.
    open_, close_ = _utc(2026, 10, 5, 13, 30), _utc(2026, 10, 9, 19, 30)
    assert _expected_candles_for_window("4h", open_, close_, asset_class="etf") == 10
    assert (
        _expected_candles_for_window("1h", open_, _utc(2026, 10, 9, 19, 30), asset_class="stock")
        == 35
    )
    assert (
        _expected_candles_for_window("15m", open_, _utc(2026, 10, 9, 19, 45), asset_class="stock")
        == 130
    )
    # Fim de semana e feriado não contam: 22 a 28 nov. 2026 tem o feriado de Ação de Graças (26).
    assert (
        _expected_candles_for_window(
            "1d", _utc(2026, 11, 22), _utc(2026, 11, 28), asset_class="stock"
        )
        == 4
    )
    # Cripto continua 24/7, com a mesma conta de antes.
    assert _expected_candles_for_window("1d", _utc(2026, 10, 5), _utc(2026, 10, 9)) == 4
    assert (
        _expected_candles_for_window(
            "4h", _utc(2026, 10, 5), _utc(2026, 10, 9), asset_class="crypto"
        )
        == 24
    )
    assert (
        _expected_candles_for_window("1d", _utc(2026, 10, 5), _utc(2026, 10, 9), symbol="BTC/USDT")
        == 4
    )


def test_fees_record_uses_the_fee_of_the_class():
    assert fees_slippage_record("1d")["fees"] == TRADING_FEE
    assert fees_slippage_record("1d", "crypto") == fees_slippage_record("1d")
    assert fees_slippage_record("4h", "stock")["fee_pct"] == pytest.approx(0.001)
    assert fees_slippage_record("4h", "etf")["slippage"] == pytest.approx(0.0002)


def test_precision_of_marks_daily_precision_with_the_stretch_and_old_results_as_unknown():
    daily = discovery_multiclass.precision_of(
        {
            "precision_requested": "intrabar",
            "precision_effective": "candle",
            "intraday_reason": "coverage",
            "intraday_missing": [{"from": "2003-01-02", "to": "2025-12-31"}],
        }
    )
    assert daily == {
        "kind": "daily",
        "missing": [{"from": "2003-01-02", "to": "2025-12-31"}],
        "reason": "coverage",
    }
    assert (
        discovery_multiclass.precision_of({"precision_effective": "intrabar_15m"})["kind"]
        == "intrabar_15m"
    )
    assert discovery_multiclass.precision_of(None) is None


def test_class_and_currency_never_mix_usd_and_usdt():
    assert discovery_multiclass.currency_of("BTC/USDT", "crypto") == "USDT"
    assert discovery_multiclass.currency_of("NVDA", "stock") == "USD"
    assert discovery_multiclass.currency_of("SPY", "etf") == "USD"
    # Sem classe conhecida segue o caminho de antes (cripto), nunca vira ação pelo formato.
    assert discovery_multiclass.class_of("BTCUSDT", None) == "crypto"
    combos = [{"symbol": s} for s in ("BTC/USDT", "BTC/USDT", "NVDA", "SPY")]
    assert discovery_multiclass.by_class(
        combos, {"BTC/USDT": "crypto", "NVDA": "stock", "SPY": "etf"}
    ) == {
        "crypto": {"assets": 1, "combinations": 2, "currency": "USDT"},
        "stock": {"assets": 1, "combinations": 1, "currency": "USD"},
        "etf": {"assets": 1, "combinations": 1, "currency": "USD"},
    }


def test_collection_failure_codes_are_isolated_from_the_resource_circuit():
    from app.services.discovery_recovery import isolated_failure

    assert isolated_failure("history_unavailable:binance_unavailable")
    assert not isolated_failure("lease_interrupted")
    assert discovery_inputs.history_failure_code("binance_rate_limited") == (
        "history_unavailable:binance_rate_limited"
    )


def test_equity_prepare_maps_no_candles_to_insufficient_and_errors_to_operational(monkeypatch):
    from app.services import equity_backtest

    def no_candles(*_a, **_k):
        raise equity_backtest.EquityRunError(
            "history_unavailable",
            "x",
            symbol="NVDA",
            reason="a Binance não tem candles de 4h de NVDA nessa janela",
        )

    monkeypatch.setattr(equity_backtest, "prepare_equity_history", no_candles)
    monkeypatch.setattr(
        discovery_multiclass,
        "_five_minute_start",
        lambda symbol: pd.Timestamp("2026-01-02", tz="UTC"),
    )
    inputs = {
        "symbol": "NVDA",
        "timeframe": "4h",
        "start_date": "2019-01-01",
        "end_date": "2020-12-31",
        "asset_class": "stock",
    }
    with pytest.raises(discovery_inputs.InsufficientHistory) as raised:
        discovery_inputs.prepare(inputs)
    assert raised.value.reason == (
        "sem candles de 4h de NVDA nessa janela (o 5m da Binance começa em 2 jan. 2026)"
    )

    def failing(*_a, **_k):
        raise equity_backtest.EquityRunError(
            "history_unavailable",
            "x",
            symbol="SPY",
            reason="Binance indisponível",
            error_code="binance_unavailable",
        )

    monkeypatch.setattr(equity_backtest, "prepare_equity_history", failing)
    with pytest.raises(OperationalFailure) as failed:
        discovery_inputs.prepare(
            {**inputs, "symbol": "SPY", "asset_class": "etf", "timeframe": "1d"}
        )
    assert failed.value.code == "history_unavailable:binance_unavailable"


def test_manifest_source_feeds_the_optimizer_with_the_asset_source():
    assert discovery_inputs.manifest_source({"data_source": "binance_equity"}) == "binance_equity"
    assert (
        discovery_inputs.manifest_source({"provenance": {"data_source": "Binance Ações"}})
        == "binance_equity"
    )
    assert (
        discovery_inputs.manifest_source({"provenance": {"data_source": "Binance Spot"}}) == "ccxt"
    )
    assert discovery_inputs.manifest_source(None) == "ccxt"


# --------------------------------------------------------------------------- banco


@pytest.fixture
def db(postgres_isolation, unit_database_url):
    from app.services.market_history.schema import (
        ADD_COLUMNS_SQL,
        execute_all,
        side_table_statements,
    )

    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    _ensure_schema(engine)
    with engine.begin() as conn:
        execute_all(conn, side_table_statements())
        execute_all(conn, ADD_COLUMNS_SQL)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


def _sweep(db, sweep_id, symbols, classes=None, timeframes=("1d",), templates=("MACD_Cross",)):
    from app.models_discovery import DiscoveryCombination, DiscoverySweep

    snapshot = {
        "period_type": "all",
        "axes": {
            "symbols": list(symbols),
            "timeframes": list(timeframes),
            "templates": list(templates),
            "directions": ["long"],
        },
        "asset_classes": classes or {},
        "survivorship": {"window": {"start": "2003-01-02", "start_label": "2 jan. 2003"}},
    }
    sweep = DiscoverySweep(
        id=sweep_id,
        actor="admin-1",
        state="running",
        idempotency_key=f"key-{sweep_id}",
        payload_hash="a" * 64,
        snapshot_token=f"tok-{sweep_id}",
        snapshot_hash="b" * 64,
        snapshot=snapshot,
        total=len(symbols) * len(timeframes) * len(templates),
    )
    db.add(sweep)
    combos = []
    for template in templates:
        for symbol in symbols:
            for tf in timeframes:
                combo = DiscoveryCombination(
                    sweep_id=sweep_id,
                    template_id=template,
                    symbol=symbol,
                    timeframe=tf,
                    direction="long",
                    state="pending",
                    input_snapshot={
                        "snapshot": snapshot,
                        "start_date": "2003-01-01",
                        "end_date": "2026-10-23",
                        "template_metadata": TEMPLATE_METADATA,
                    },
                )
                db.add(combo)
                combos.append(combo)
    db.commit()
    return sweep, combos


def _equity_manifest(snapshot_id="8b41d7e2aa00bb11cc22dd33ee44ff55"):
    return {
        "snapshot_id": snapshot_id,
        "files": {
            "candles": {"sha256": "c" * 64, "rows": 10, "segments": []},
            "intraday": {"sha256": "d" * 64, "rows": 0, "segments": []},
        },
        "data_source": "binance_equity",
        "provenance": {
            "data_source": "Binance Ações",
            "asset_class": "stock",
            "session": "rth",
            "adjustment": "adjusted",
            "timeframe_origin": "native",
            "period_requested": {"start": "2003-01-01", "end": "2026-10-23"},
            "period_covered": {
                "start": "2003-01-02T05:00:00+00:00",
                "end": "2026-10-23T04:00:00+00:00",
                "candles": 10,
            },
            "data_version": 1,
            "version_label": "1",
            "snapshot_id": snapshot_id,
        },
    }


def _equity_result(candles):
    return {
        "best_metrics": {
            "sharpe_ratio": 0.94,
            "profit_factor": 1.4,
            "max_drawdown": 0.17,
            "win_rate": 0.49,
            "cagr": 0.183,
            "calmar_ratio": 1.08,
            "benchmark": {"cagr": 0.1},
        },
        "trades": [{"entry_time": candles[0]["timestamp_utc"], "profit": 0.1}] * 40,
        "candles": candles,
        "best_parameters": {"direction": "long"},
        "data_source": "binance_equity",
        "asset": {
            "symbol": "NVDA",
            "asset_class": "stock",
            "currency": "USD",
            "asset_id": "binance:equity:EQ_NVDA",
        },
        "execution": {
            "precision_requested": "intrabar",
            "precision_effective": "candle",
            "timeframe": "1d",
            "intraday_reason": "coverage",
            "intraday_missing": [{"from": "2026-10-05", "to": "2026-10-16"}],
            "window": {
                "covered": {
                    "start": candles[0]["timestamp_utc"],
                    "end": candles[-1]["timestamp_utc"],
                    "candles": len(candles),
                }
            },
        },
        "conventions": {
            "fee": 0.001,
            "adjusted_prices": True,
            "calendar": {"kind": "nyse_regular_session", "sessions_per_year": 252},
        },
    }


def _nyse_daily(start="2026-10-05", end="2026-10-16"):
    days = pd.bdate_range(start, end)
    return [
        {
            "timestamp_utc": (pd.Timestamp(d, tz="America/New_York")).tz_convert("UTC").isoformat(),
            "close": 1.0,
        }
        for d in days
    ]


def test_run_combination_records_identity_precision_conventions_fee_and_nyse_coverage(
    db, monkeypatch
):
    from app.models_discovery import DiscoveryResult

    _, (combo,) = _sweep(db, "sw-1121-nvda", ["NVDA"], {"NVDA": "stock"})
    combo.input_snapshot = {**combo.input_snapshot, "candle_manifest": _equity_manifest()}
    db.commit()
    _grant_possession(db, combo)
    _patch_metadata(monkeypatch)
    captured = {}

    def run_supervised(config, beat):
        captured.update(config)
        return _equity_result(_nyse_daily())

    monkeypatch.setattr("app.services.discovery_supervisor.run_supervised", run_supervised)
    run_combination(db, combo, owner="worker-876")
    db.refresh(combo)
    result = db.query(DiscoveryResult).filter_by(id=combo.result_id).one()

    assert captured["asset_class"] == "stock"
    assert captured["candle_manifest"]["data_source"] == "binance_equity"
    assert combo.state == "succeeded"
    assert result.data_source == "Binance Ações" and result.asset_class == "stock"
    assert result.snapshot_id == "8b41d7e2aa00bb11cc22dd33ee44ff55"
    assert result.metrics["asset"]["currency"] == "USD"
    assert result.metrics["execution"]["intraday_missing"] == [
        {"from": "2026-10-05", "to": "2026-10-16"}
    ]
    assert result.metrics["conventions"]["calendar"]["kind"] == "nyse_regular_session"
    assert result.fees_slippage["fees"] == pytest.approx(0.001)
    # 10 pregões em duas semanas, todos presentes: 100% (fim de semana não conta como lacuna).
    assert result.expected_candles == 10 and result.coverage == pytest.approx(1.0)
    assert result.eligibility == "eligible"


def test_no_candles_ends_as_insufficient_sample_with_the_reason(db, monkeypatch):
    from app.models_discovery import DiscoveryResult

    _, (combo,) = _sweep(db, "sw-1121-4h", ["NVDA"], {"NVDA": "stock"}, timeframes=("4h",))
    _grant_possession(db, combo)
    _patch_metadata(monkeypatch)
    reason = "sem candles de 4h de NVDA nessa janela (o 5m da Binance começa em 2 jan. 2026)"
    _patch_supervised(
        monkeypatch,
        result={"insufficient": True, "listing_len": 0, "train_len": 0, "reason": reason},
    )
    run_combination(db, combo, owner="worker-876")
    db.refresh(combo)
    result = db.query(DiscoveryResult).filter_by(id=combo.result_id).one()
    assert combo.state == "insufficient_sample"
    assert result.eligibility == "insufficient_sample"
    assert result.eligibility_reason == reason
    assert result.asset_class == "stock"


def test_second_combination_and_retry_reuse_the_frozen_sample(db, monkeypatch):
    from app.models_discovery import DiscoverySweep
    from app.services.discovery_recovery import Possession, heartbeat, sample_key

    sweep, (first, second) = _sweep(
        db, "sw-1121-share", ["NVDA"], {"NVDA": "stock"}, templates=("MACD_Cross", "EMA_Cross")
    )
    _grant_possession(db, first)
    manifest = _equity_manifest()
    # O filho congela e manda o manifesto: a combinação guarda e a varredura registra a amostra única.
    heartbeat(
        db,
        Possession.of(first),
        [{"phase_complete": "input_snapshot", "candle_manifest": manifest}],
    )
    db.expire_all()
    stored = db.get(DiscoverySweep, sweep.id).snapshot["samples"]
    key = sample_key("NVDA", "1d", "2003-01-01", "2026-10-23")
    assert stored[key]["snapshot_id"] == manifest["snapshot_id"]
    assert (
        "samples"
        not in __import__("app.services.discovery_service", fromlist=["x"])
        .DiscoveryService()
        ._serialize_sweep(db.get(DiscoverySweep, sweep.id), db)["snapshot"]
    )

    seen = []

    def run_supervised(config, beat):
        seen.append(config["candle_manifest"])
        return {"insufficient": True, "listing_len": 1, "train_len": 0}

    monkeypatch.setattr("app.services.discovery_supervisor.run_supervised", run_supervised)
    _patch_metadata(monkeypatch)
    # Outro template do mesmo ativo e tempo lê o manifesto da varredura, sem coletar de novo.
    _grant_possession(db, second, owner="worker-2")
    run_combination(db, second, owner="worker-2")
    # Nova tentativa da primeira lê o próprio manifesto (mesmo snapshot_id em treino, tentativa e avaliação).
    db.refresh(first)
    run_combination(db, first, owner="worker-876")
    assert [m["snapshot_id"] for m in seen] == [manifest["snapshot_id"], manifest["snapshot_id"]]


def test_collection_failure_uses_the_3_attempts_then_fails_only_that_combination(db):
    from app.models_discovery import DiscoveryCircuit, DiscoverySweep
    from app.services.discovery_recovery import MAX_ATTEMPTS, Possession, fail

    sweep, (spy, btc) = _sweep(
        db, "sw-1121-fail", ["SPY", "BTC/USDT"], {"SPY": "etf", "BTC/USDT": "crypto"}
    )
    code = "history_unavailable:binance_unavailable"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        spy.attempts = attempt
        spy.lease_generation = attempt
        db.commit()
        _grant_possession(db, spy)
        fail(db, Possession.of(spy), code, operational=True)
        db.refresh(spy)
        if attempt < MAX_ATTEMPTS:
            assert spy.state == "pending" and spy.next_attempt_at is not None
    assert spy.state == "failed" and spy.last_failure_code == code
    db.expire_all()
    assert db.get(DiscoverySweep, sweep.id).state == "running"  # a varredura segue com BTC/USDT
    circuit = db.query(DiscoveryCircuit).first()
    assert circuit is None or (not circuit.opened_at and not circuit.failures)

    assets = {
        a["symbol"]: a
        for a in discovery_multiclass.sweep_assets(db, db.get(DiscoverySweep, sweep.id))
    }
    assert assets["SPY"]["state"] == "failed"
    assert assets["SPY"]["reason"].startswith(
        "a Binance não respondeu ao histórico de SPY nas 3 tentativas"
    )
    assert assets["BTC/USDT"]["state"] == "queued" and assets["BTC/USDT"]["currency"] == "USDT"


def test_sweep_assets_report_collection_progress_and_mixed_outcomes(db):
    from app.models_discovery import DiscoveryAttempt, DiscoveryResult, DiscoverySweep

    sweep, combos = _sweep(
        db,
        "sw-1121-assets",
        ["BTC/USDT", "NVDA", "SPY"],
        {"BTC/USDT": "crypto", "NVDA": "stock", "SPY": "etf"},
        timeframes=("1d", "4h"),
    )
    by = {(c.symbol, c.timeframe): c for c in combos}
    now = datetime.now(timezone.utc)

    def result(combo, eligibility, reason=None, execution=None):
        db.add(
            DiscoveryResult(
                id=f"RS-{combo.id}",
                sweep_id=sweep.id,
                combination_id=combo.id,
                template_id=combo.template_id,
                symbol=combo.symbol,
                timeframe=combo.timeframe,
                direction="long",
                parameters={},
                start_at=now,
                end_at=now,
                metrics={"execution": execution} if execution else {},
                strategy_identity_key=f"id-{combo.id}",
                evidence_fingerprint=f"fp-{combo.id}",
                eligibility=eligibility,
                eligibility_reason=reason,
                asset_class={"BTC/USDT": "crypto", "NVDA": "stock", "SPY": "etf"}[combo.symbol],
            )
        )
        combo.state = "succeeded" if eligibility == "eligible" else "insufficient_sample"
        combo.result_id = f"RS-{combo.id}"

    result(by[("BTC/USDT", "1d")], "eligible", execution={"precision_effective": "intrabar_15m"})
    result(by[("BTC/USDT", "4h")], "eligible", execution={"precision_effective": "intrabar_15m"})
    result(
        by[("NVDA", "1d")],
        "eligible",
        execution={
            "precision_requested": "intrabar",
            "precision_effective": "candle",
            "intraday_reason": "coverage",
            "intraday_missing": [{"from": "2019-01-02", "to": "2020-12-31"}],
        },
    )
    result(
        by[("NVDA", "4h")], "insufficient_sample", reason="sem candles de 4h de NVDA nessa janela"
    )
    db.commit()
    spy = by[("SPY", "1d")]
    _grant_possession(db, spy)
    attempt = db.get(DiscoveryAttempt, (spy.id, spy.attempts))
    attempt.counters = {"collecting": {"role": "intraday", "series": "5m", "page": 7, "pages": 16}}
    db.commit()

    assets = {
        a["symbol"]: a
        for a in discovery_multiclass.sweep_assets(db, db.get(DiscoverySweep, sweep.id))
    }
    assert assets["BTC/USDT"]["state"] == "done" and assets["BTC/USDT"]["done"] == 2
    nvda = assets["NVDA"]
    assert (
        nvda["state"] == "mixed"
        and nvda["outcomes"]["succeeded"] == 1
        and nvda["outcomes"]["insufficient"] == 1
    )
    assert nvda["details"][0]["precision"]["kind"] == "daily"
    assert nvda["details"][1]["reason"] == "sem candles de 4h de NVDA nessa janela"
    assert (
        assets["SPY"]["state"],
        assets["SPY"]["series"],
        assets["SPY"]["page"],
        assets["SPY"]["pages"],
    ) == (
        "collecting",
        "5m",
        7,
        16,
    )
    assert assets["SPY"]["asset_class"] == "etf" and assets["SPY"]["currency"] == "USD"


def _ranked_result(db, sweep_id, rid, symbol, asset_class, calmar, verdict):
    from app.models_discovery import DiscoveryResult

    now = datetime.now(timezone.utc)
    db.add(
        DiscoveryResult(
            id=rid,
            sweep_id=sweep_id,
            combination_id=abs(hash(rid)) % 10**9,
            template_id="MACD_Cross",
            symbol=symbol,
            timeframe="1d",
            direction="long",
            parameters={"direction": "long"},
            start_at=now - timedelta(days=300),
            end_at=now,
            metrics={"oos_verdict": {"status": verdict}},
            trades_count=40,
            calmar_ratio=calmar,
            coverage=1.0,
            strategy_identity_key=f"id-{rid}",
            evidence_fingerprint=f"fp-{rid}",
            eligibility="eligible",
            dedup_state="unique",
            asset_class=asset_class,
        )
    )


def test_one_ranking_for_every_class_with_class_filter_and_global_rank(db):
    from app.services.discovery_service import DiscoveryService

    _ranked_result(db, "sw-rank", "RS-BTC", "BTC/USDT", "crypto", 2.0, "NO-GO")
    _ranked_result(db, "sw-rank", "RS-NVDA", "NVDA", "stock", 1.6, "GO")
    _ranked_result(db, "sw-rank", "RS-SPY", "SPY", "etf", 0.9, "NO-GO")
    db.commit()
    service = DiscoveryService()
    counts: dict = {}
    rows, total, unfiltered = service.leaderboard("sw-rank", db=db, counts=counts)
    # GO de ação acima de NO-GO de cripto, mesmo com Calmar menor; nada é somado entre USD e USDT.
    assert [r["result_id"] for r in rows] == ["RS-NVDA", "RS-BTC", "RS-SPY"]
    assert counts == {"all": 3, "crypto": 1, "stock": 1, "etf": 1}
    assert {r["result_id"]: r["asset"]["currency"] for r in rows} == {
        "RS-NVDA": "USD",
        "RS-BTC": "USDT",
        "RS-SPY": "USD",
    }
    stocks, total, unfiltered = service.leaderboard("sw-rank", db=db, asset_class="stock")
    assert [(r["result_id"], r["rank"]) for r in stocks] == [("RS-NVDA", 1)]
    etfs, *_ = service.leaderboard("sw-rank", db=db, asset_class="etf")
    assert [(r["result_id"], r["rank"]) for r in etfs] == [("RS-SPY", 3)]
    assert total == 1 and unfiltered == 3


def test_promote_nvda_without_star_level_and_with_the_execution_identity(db, monkeypatch):
    from app.models import FavoriteStrategy
    from app.models_discovery import DiscoveryResult, DiscoverySweep
    from app.services import favorite_operational_period
    from app.services.discovery_service import DiscoveryService

    captured = {}

    def enrich(**kwargs):
        captured.update(kwargs)
        return (
            kwargs.get("period_type"),
            kwargs.get("start_date"),
            kwargs.get("end_date") or "2026-10-23",
            {},
        )

    def no_network_lookup(symbol, timeframe):
        raise AssertionError(f"primeiro candle de {symbol} {timeframe} buscado na rede")

    monkeypatch.setattr(favorite_operational_period, "enrich_walk_forward_favorite_create", enrich)
    monkeypatch.setattr(favorite_operational_period, "_first_candle_iso", no_network_lookup)
    sweep, _ = _sweep(db, "sw-1121-promo", ["NVDA"], {"NVDA": "stock"})
    sweep.snapshot = {**sweep.snapshot, "period_type": "all", "start_date": None, "end_date": None}
    now = datetime.now(timezone.utc)
    manifest = _equity_manifest()
    db.add(
        DiscoveryResult(
            id="RS-NVDA1121B2",
            sweep_id=sweep.id,
            combination_id=990001,
            template_id="multi_ma_crossover",
            symbol="NVDA",
            timeframe="1d",
            direction="long",
            parameters={"fast": 21, "slow": 89, "direction": "long", "timeframe": "1d"},
            start_at=now - timedelta(days=8000),
            end_at=now,
            metrics=_equity_result(_nyse_daily()) | {"oos_verdict": {"status": "GO"}},
            trades_count=61,
            calmar_ratio=1.08,
            coverage=1.0,
            strategy_identity_key="id-nvda-1121",
            evidence_fingerprint="fp-nvda-1121",
            eligibility="eligible",
            dedup_state="unique",
            data_source="Binance Ações",
            asset_class="stock",
            session="rth",
            adjustment="adjusted",
            period_covered=manifest["provenance"]["period_covered"],
            snapshot_id=manifest["snapshot_id"],
        )
    )
    db.commit()
    service = DiscoveryService()
    # Outro tier no payload continua recusado, também para ação e ETF (contrato fixo).
    refused_body, refused = service.promote_result(
        result_id="RS-NVDA1121B2",
        actor="admin-1",
        idempotency_key="promote-other",
        payload={"tier": 2, "result_id": "RS-NVDA1121B2"},
        db=db,
    )
    assert refused == 422 and db.query(FavoriteStrategy).count() == 0, refused_body
    # O contrato do payload segue exigindo tier 3; o servidor grava o nível pela classe.
    body, status = service.promote_result(
        result_id="RS-NVDA1121B2",
        actor="admin-1",
        idempotency_key="promote-RS-NVDA1121B2",
        payload={"tier": 3, "result_id": "RS-NVDA1121B2"},
        db=db,
    )
    assert status == 201, body
    favorite = db.get(FavoriteStrategy, int(body["favorite_id"]))
    # Card #1122: tier 3 em qualquer classe, sem "Alertar" e com a configuração do resultado.
    assert favorite.tier == 3
    assert favorite.notify_telegram is False
    assert favorite.data_source == "binance_equity"
    assert (
        favorite.parameters["data_source"] == "binance_equity"
        and favorite.parameters["direction"] == "long"
    )
    assert favorite.metrics["analysis_asset"]["asset_class"] == "stock"
    assert favorite.metrics["analysis_asset"]["currency"] == "USD"
    assert favorite.metrics["analysis_execution"]["precision_effective"] == "candle"
    assert favorite.metrics["analysis_conventions"]["calendar"]["kind"] == "nyse_regular_session"
    assert favorite.metrics["data_provenance"]["snapshot_id"] == manifest["snapshot_id"]
    assert favorite.metrics["origin_type"] == "discovery_sweep"
    assert favorite.snapshot_id == manifest["snapshot_id"]
    # "Todo o histórico" de ação começa no primeiro candle da amostra, nunca no Stooq.
    assert captured["parameters"]["data_source"] == "binance_equity"
    assert captured["start_date"] == "2003-01-02"


def test_crypto_promotion_stays_tier_3(db, monkeypatch):
    from app.models import FavoriteStrategy
    from app.models_discovery import DiscoveryResult
    from app.services import favorite_operational_period
    from app.services.discovery_service import DiscoveryService

    captured = {}

    def enrich(**kwargs):
        captured.update(kwargs)
        return kwargs.get("period_type"), kwargs.get("start_date"), kwargs.get("end_date"), {}

    def no_network_lookup(symbol, timeframe):
        raise AssertionError(f"primeiro candle de {symbol} {timeframe} buscado na rede")

    monkeypatch.setattr(favorite_operational_period, "enrich_walk_forward_favorite_create", enrich)
    monkeypatch.setattr(favorite_operational_period, "_first_candle_iso", no_network_lookup)
    # Varredura real com período explícito: o período do favorito sai do snapshot, sem rede.
    sweep, _ = _sweep(db, "sw-1121-btc-promo", ["BTC/USDT"], {"BTC/USDT": "crypto"})
    sweep.snapshot = {
        **sweep.snapshot,
        "period_type": "all",
        "start_date": "2017-08-17",
        "end_date": "2026-10-23",
    }
    now = datetime.now(timezone.utc)
    db.add(
        DiscoveryResult(
            id="RS-BTC1121A1",
            sweep_id=sweep.id,
            combination_id=990002,
            template_id="multi_ma_crossover",
            symbol="BTC/USDT",
            timeframe="1d",
            direction="long",
            parameters={"fast": 21},
            start_at=now,
            end_at=now,
            metrics={},
            trades_count=48,
            calmar_ratio=2.1,
            strategy_identity_key="id-btc-1121",
            evidence_fingerprint="fp-btc-1121",
            eligibility="eligible",
            dedup_state="unique",
        )
    )
    db.commit()
    body, status = DiscoveryService().promote_result(
        result_id="RS-BTC1121A1",
        actor="admin-1",
        idempotency_key="promote-RS-BTC1121A1",
        payload={"tier": 3, "result_id": "RS-BTC1121A1"},
        db=db,
    )
    assert status == 201, body
    favorite = db.get(FavoriteStrategy, int(body["favorite_id"]))
    assert favorite.tier == 3
    assert favorite.metrics["analysis_asset"]["asset_class"] == "crypto"
    assert favorite.parameters["data_source"] == "ccxt"
    assert (captured["period_type"], captured["start_date"], captured["end_date"]) == (
        "all",
        "2017-08-17",
        "2026-10-23",
    )


# --------------------------------------------------------------------------- regressão de cripto


def test_crypto_only_run_keeps_fee_coverage_eligibility_and_evidence(db, monkeypatch):
    from app.models_discovery import DiscoveryResult
    from app.services.discovery_service import build_evidence_fingerprint

    _, (combo,) = _sweep(db, "sw-1121-crypto", ["BTC/USDT"], {"BTC/USDT": "crypto"})
    _grant_possession(db, combo)
    _patch_metadata(monkeypatch)
    start, end = _utc(2024, 1, 1), _utc(2024, 3, 1)
    days = pd.date_range(start, end, freq="D")
    result = {
        "best_metrics": {
            "sharpe_ratio": 1.2,
            "profit_factor": 1.5,
            "max_drawdown": 0.15,
            "win_rate": 0.55,
            "cagr": 0.42,
            "calmar_ratio": 2.8,
            "benchmark": {"cagr": 0.18},
        },
        "trades": [{"entry_time": start.isoformat(), "profit": 0.1}] * 40,
        "candles": [{"timestamp_utc": d.isoformat(), "close": 1.0} for d in days],
        "best_parameters": {"direction": "long"},
        "data_source": "ccxt",
    }
    _patch_supervised(monkeypatch, result=result)
    run_combination(db, combo, owner="worker-876")
    db.refresh(combo)
    row = db.query(DiscoveryResult).filter_by(id=combo.result_id).one()
    # Mesma conta 24/7 de antes: intervalo [start, end) em dias.
    expected = max(1, int(((end - start).total_seconds() / 3600) // 24))
    assert row.expected_candles == expected
    assert row.fees_slippage == {
        "fees": TRADING_FEE,
        "slippage": 0.0002,
        "fee_pct": TRADING_FEE,
        "slippage_pct": 0.0002,
    }
    assert row.eligibility == "eligible"
    assert row.evidence_fingerprint == build_evidence_fingerprint(
        start_at=start,
        end_at=end,
        candle_source="ccxt",
        candle_version=None,
        expected_candles=expected,
        observed_valid_candles=len(days),
        coverage=min(1.0, len(days) / expected),
        fees_slippage={
            "fees": TRADING_FEE,
            "slippage": 0.0002,
            "fee_pct": TRADING_FEE,
            "slippage_pct": 0.0002,
        },
        metrics={
            "sharpe_ratio": 1.2,
            "profit_factor": 1.5,
            "max_drawdown": 0.15,
            "win_rate": 0.55,
            "total_trades": 40,
        },
    )


def test_crypto_only_preflight_keeps_the_same_snapshot_identity(monkeypatch):
    from app.services import asset_analysis_guard
    from app.services.discovery_service import DiscoveryService, _payload_hash

    monkeypatch.setattr(
        asset_analysis_guard,
        "discovery_catalog",
        lambda symbols: ({}, {s: "crypto" for s in symbols}),
    )
    monkeypatch.setattr(
        discovery_multiclass,
        "forecast",
        lambda *a, **k: {"collection": None, "precision_forecast": None, "survivorship": None},
    )
    service = DiscoveryService()
    monkeypatch.setattr(
        service.combo_service, "get_template_metadata", lambda name: {"direction": "long"}
    )
    monkeypatch.setattr(
        service.combo_service,
        "list_templates",
        lambda: {"prebuilt": [{"name": "multi_ma_crossover"}], "examples": []},
    )
    result = service.preflight(
        templates=["multi_ma_crossover"],
        symbols=["BTC/USDT", "ETH/USDT"],
        timeframes=["1d", "4h"],
        directions=["long"],
        start_date="2024-01-01",
        end_date="2024-12-31",
        period_type=None,
    )
    legacy = {
        "templates": ["multi_ma_crossover"],
        "symbols": ["BTC/USDT", "ETH/USDT"],
        "timeframes": ["1d", "4h"],
        "directions": ["long"],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "period_type": None,
        "valid_total": 4,
        "snapshot_version": "v1",
    }
    # Os campos novos (classe, coleta, precisão, viés) não entram na identidade do snapshot.
    assert result["snapshot_hash"] == _payload_hash(legacy)
    assert result["valid_total"] == 4 and result["errors"] == {}
    assert result["by_class"] == {"crypto": {"assets": 2, "combinations": 4, "currency": "USDT"}}


# --------------------------------------------------------------------------- caminho real de ação (HistoryService)


@pytest.fixture
def equity_history(public_db, unit_database_url, tmp_path, monkeypatch):  # noqa: F811
    from app.services.market_history import facade
    from app.services.market_history.cache import ParquetReadCache
    from app.services.market_history.service import HistoryService
    from market_history_support import FakeEquityProvider, history_schema
    from test_card_1118_api_and_catalog import _seed_catalog
    from test_card_1119_equity_backtest_api import RoutedProvider

    now = pd.Timestamp("2026-10-23 01:30", tz="UTC")
    _seed_catalog(public_db)
    monkeypatch.setenv("MARKET_HISTORY_SNAPSHOT_DIR", str(tmp_path / "snapshots"))
    with history_schema(unit_database_url) as engine:
        daily = FakeEquityProvider(timeframe="1d", now=now, page_size=400)
        daily.build(pd.Timestamp("2025-06-02", tz="UTC"), now)
        five = FakeEquityProvider(timeframe="5m", now=now, page_size=1000)
        five.build(pd.Timestamp("2026-01-02", tz="UTC"), now)
        provider = RoutedProvider({"1d": daily, "5m": five})
        service = HistoryService(
            engine,
            equity_provider=provider,
            clock=lambda: now.to_pydatetime(),
            update_ttl_seconds=0,
            lease_wait_seconds=0.2,
        )
        facade.set_history_service(service, ParquetReadCache(tmp_path / "series"))
        yield service, provider
        facade.set_history_service(None, None)
        for key in (discovery_inputs.SNAPSHOT_ID_ENV, discovery_inputs.SNAPSHOT_SEGMENTS_ENV):
            os.environ.pop(key, None)


def test_nvda_is_collected_and_frozen_from_binance_equity_once(equity_history):
    service, provider = equity_history
    pages = []
    inputs = {
        "symbol": "NVDA",
        "timeframe": "1d",
        "start_date": "2025-10-01",
        "end_date": "2026-10-20",
        "asset_class": "stock",
    }
    manifest = discovery_inputs.prepare(inputs, on_progress=pages.append)

    assert manifest["data_source"] == "binance_equity"
    prov = manifest["provenance"]
    assert prov["data_source"] == "Binance Ações" and prov["asset_class"] == "stock"
    assert prov["session"] == "rth" and prov["adjustment"] == "adjusted"
    assert prov["snapshot_id"] == manifest["snapshot_id"]
    assert set(manifest["files"]) == {"candles", "intraday"}
    assert manifest["asset"]["currency"] == "USD"
    assert pages and {p["phase"] for p in pages} == {"collecting"}
    assert {p["role"] for p in pages} <= {"candles", "intraday"}
    requested = len(provider.requests)
    # Nova tentativa: o mesmo manifesto é validado e devolvido, sem coletar nem congelar de novo.
    again = discovery_inputs.prepare({**inputs, "candle_manifest": manifest})
    assert again is manifest and len(provider.requests) == requested
    candles = discovery_inputs.read("candles", manifest["snapshot_id"])
    assert len(candles) == manifest["files"]["candles"]["rows"] > 100


def test_equity_4h_before_the_5m_starts_has_no_candles(equity_history):
    with pytest.raises(discovery_inputs.InsufficientHistory) as raised:
        discovery_inputs.prepare(
            {
                "symbol": "NVDA",
                "timeframe": "4h",
                "start_date": "2019-01-01",
                "end_date": "2020-12-31",
                "asset_class": "stock",
            }
        )
    assert raised.value.reason.startswith("sem candles de 4h de NVDA nessa janela")


@pytest.mark.timeout(600)
def test_nvda_frozen_sample_feeds_training_and_evaluation_with_daily_precision(equity_history):
    """O otimizador lê só da amostra congelada (fonte ``binance_equity``) e marca o trecho sem 15m."""
    from app.services.combo_optimizer import ComboOptimizer
    from test_card_1118_optimizer_regression import _FakeTemplates, _fixed_ranges

    inputs = {
        "symbol": "NVDA",
        "timeframe": "1d",
        "start_date": "2025-10-01",
        "end_date": "2026-10-20",
        "asset_class": "stock",
    }
    manifest = discovery_inputs.prepare(inputs)
    discovery_inputs.activate(manifest)
    try:
        optimizer = ComboOptimizer(workers=1)
        optimizer.combo_service = _FakeTemplates()
        result = optimizer.run_optimization(
            template_name="multi_ma_crossover",
            symbol="NVDA",
            timeframe="1d",
            data_source=discovery_inputs.manifest_source(manifest),
            start_date="2025-10-01",
            end_date="2026-10-20",
            custom_ranges=_fixed_ranges(),
            deep_backtest=True,
            split_train_ratio=0.7,
        )
    finally:
        for key in (discovery_inputs.SNAPSHOT_ID_ENV, discovery_inputs.SNAPSHOT_SEGMENTS_ENV):
            os.environ.pop(key, None)
    assert result["data_source"] == "binance_equity"
    # Sem amostra própria: treino, avaliação e tentativas leram a da varredura.
    assert "snapshot_id" not in result
    assert result["asset"]["asset_class"] == "stock" and result["asset"]["currency"] == "USD"
    execution = result["execution"]
    assert (
        execution["precision_effective"] == "candle" and execution["intraday_reason"] == "coverage"
    )
    assert execution["intraday_missing"][0]["from"] == "2025-10-01"
    precision = discovery_multiclass.precision_of(execution)
    assert precision["kind"] == "daily" and precision["missing"]
