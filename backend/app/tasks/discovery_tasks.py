"""Discovery sweep orchestrator tasks (card #469).

Um job orquestrador por sweep/wake-up (outbox at-least-once). O payload é
idempotente (sweep_id + generation); combinações são reclamadas no PostgreSQL
em lotes de 20 com lease. Resultado commitado antes do ACK é reconhecido pela
unique key e não reexecutado.
"""

from __future__ import annotations

import logging
import math
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models_discovery import (
    DiscoveryCombination,
    DiscoveryOutbox,
    DiscoveryResult,
    DiscoverySweep,
)
from app.services.discovery_service import (
    DiscoveryService,
    MIN_ELIGIBLE_COVERAGE,
    MIN_ELIGIBLE_TRADES,
    build_evidence_fingerprint,
    build_strategy_identity,
)

logger = logging.getLogger(__name__)

DISCOVERY_SPLIT_TRAIN_RATIO = 0.7


def resolve_optimizer_date_range(
    snapshot: dict[str, Any], now: datetime | None = None
) -> tuple[str | None, str | None]:
    """Converte o período do discovery para o contrato de datas do otimizador."""
    start_date = snapshot.get("start_date")
    end_date = snapshot.get("end_date")
    if start_date or end_date:
        return start_date, end_date

    period_type = snapshot.get("period_type")
    if period_type not in {"6m", "2y"}:
        return None, None

    from dateutil.relativedelta import relativedelta

    end = (now or datetime.now(timezone.utc)).date()
    delta = relativedelta(months=6) if period_type == "6m" else relativedelta(years=2)
    return (end - delta).isoformat(), end.isoformat()


def enqueue_sweep_orchestrator(sweep_id: str, generation: int) -> None:
    """Publica o wake-up do orquestrador (idempotente por sweep+generation)."""
    try:
        from app.celery_app import celery_app
        from app.tasks.discovery_celery_tasks import run_sweep_orchestrator_task

        run_sweep_orchestrator_task.apply_async(
            args=[sweep_id, generation],
            queue="discovery",
        )
        logger.info("Discovery orchestrator enqueued: sweep=%s gen=%s", sweep_id, generation)
    except Exception as exc:  # pragma: no cover - broker down
        logger.warning("Discovery orchestrator enqueue failed (outbox redelivers): %s", exc)
        raise


def reconcile_sweep(sweep_id: str, db: Session) -> dict[str, Any]:
    """Reconcilia contadores e estado terminal a partir das combinações.

    Em caminhos terminais (cancelled/failed), toda combinação ainda não
    terminal vira skipped: processed = succeeded + failed + skipped = total
    em qualquer terminal (spec discovery-sweep).
    """
    sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == sweep_id).first()
    if not sweep:
        return {}
    rows = db.query(DiscoveryCombination).filter(DiscoveryCombination.sweep_id == sweep_id).all()
    now = datetime.now(timezone.utc)

    if sweep.state == "cancelling":
        # Cancelamento prevalece: pendentes viram skipped imediatamente.
        for r in rows:
            if r.state == "pending":
                r.state = "skipped"
                r.updated_at = now

    succeeded = sum(1 for r in rows if r.state == "succeeded")
    failed = sum(1 for r in rows if r.state == "failed")
    skipped = sum(1 for r in rows if r.state == "skipped")
    pending = sum(1 for r in rows if r.state == "pending")
    running = sum(1 for r in rows if r.state == "running")

    sweep.succeeded = succeeded
    sweep.failed = failed
    sweep.skipped = skipped
    sweep.processed = succeeded + failed + skipped
    sweep.updated_at = now

    if sweep.state == "cancelling" and pending == 0 and running == 0:
        sweep.state = "cancelled"
        sweep.completed_at = now
    elif sweep.state == "running" and pending == 0 and running == 0:
        if failed == 0 and succeeded > 0:
            sweep.state = "completed"
            sweep.completed_at = now
        elif succeeded > 0 and failed > 0:
            sweep.state = "partial_failure"
            sweep.completed_at = now
        elif succeeded == 0 and failed > 0:
            sweep.state = "failed"
            sweep.terminal_reason = "all_results_failed"
            sweep.completed_at = now
        elif succeeded == 0 and failed == 0 and skipped > 0:
            sweep.state = "failed"
            sweep.terminal_reason = "operational_failure"
            sweep.terminal_code = "execution_reconciliation_failure"
            sweep.completed_at = now
    elif sweep.state == "paused":
        # Sem transição automática; contadores atualizados apenas.
        pass
    db.commit()
    return {
        "state": sweep.state,
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
        "processed": succeeded + failed + skipped,
        "total": sweep.total,
    }


def run_combination(
    db: Session,
    combination: DiscoveryCombination,
    owner: str,
) -> None:
    """Executa o otimizador para uma combinação e persiste resultado único."""
    logger.info(
        "Discovery combination started: sweep=%s combination=%s template=%s symbol=%s timeframe=%s direction=%s",
        combination.sweep_id,
        combination.id,
        combination.template_id,
        combination.symbol,
        combination.timeframe,
        combination.direction,
    )
    sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == combination.sweep_id).first()
    if not sweep:
        combination.state = "skipped"
        combination.updated_at = datetime.now(timezone.utc)
        db.commit()
        return
    # Recheck transacional do estado: pause/cancel não podem iniciar otimização.
    if sweep.state != "running":
        combination.state = "pending"
        combination.lease_owner = None
        combination.lease_expires_at = None
        combination.updated_at = datetime.now(timezone.utc)
        db.commit()
        return

    service = DiscoveryService()
    from app.services.combo_optimizer import ComboOptimizer

    snapshot = sweep.snapshot or {}
    start_date, end_date = resolve_optimizer_date_range(snapshot)
    try:
        optimizer = ComboOptimizer()
        result = optimizer.run_optimization(
            template_name=combination.template_id,
            symbol=combination.symbol,
            timeframe=combination.timeframe,
            data_source="ccxt",
            start_date=start_date,
            end_date=end_date,
            direction=combination.direction,
            deep_backtest=True,
            split_train_ratio=DISCOVERY_SPLIT_TRAIN_RATIO,
        )
    except Exception as exc:
        logger.warning(
            "Discovery combination failed: %s %s: %s", combination.sweep_id, combination.id, exc
        )
        combination.state = "failed"
        combination.attempts += 1
        combination.updated_at = datetime.now(timezone.utc)
        db.commit()
        return

    best_metrics = dict(result.get("best_metrics") or {})
    trades = result.get("trades") or []
    candles = result.get("candles") or []
    parameters = result.get("best_parameters") or {}
    _ensure_in_sample_ranking(best_metrics, trades, candles)
    start_at = _first_candle_time(candles, snapshot)
    end_at = _last_candle_time(candles, snapshot)
    # Calendário 24x7 versionado por timeframe: denominador de coverage vem do
    # intervalo UTC [start_at, end_at), não dos candles retornados (spec
    # discovery-leaderboard: gaps reduzem coverage; sem forward-fill).
    expected_candles = _expected_candles_for_window(combination.timeframe, start_at, end_at)
    observed_valid_candles = len(candles) or 0
    coverage = min(1.0, (observed_valid_candles / expected_candles) if expected_candles else 0.0)
    trades_count = len(trades)

    metadata = service.combo_service.get_template_metadata(combination.template_id) or {}
    identity = build_strategy_identity(
        template_id=combination.template_id,
        parameters=parameters,
        symbol=combination.symbol,
        timeframe=combination.timeframe,
        direction=combination.direction,
        template_metadata=metadata,
    )
    metrics_snapshot = {
        "sharpe_ratio": best_metrics.get("sharpe_ratio"),
        "profit_factor": best_metrics.get("profit_factor"),
        "max_drawdown": best_metrics.get("max_drawdown"),
        "win_rate": best_metrics.get("win_rate"),
        "total_trades": trades_count,
    }
    evidence = build_evidence_fingerprint(
        start_at=start_at,
        end_at=end_at,
        candle_source=result.get("data_source"),
        candle_version=None,
        expected_candles=expected_candles,
        observed_valid_candles=observed_valid_candles,
        coverage=coverage,
        fees_slippage={"fees": 0.001, "slippage": 0.001},
        metrics=metrics_snapshot,
    )

    eligible = trades_count >= MIN_ELIGIBLE_TRADES and coverage >= MIN_ELIGIBLE_COVERAGE
    eligibility_reason = None
    if trades_count < MIN_ELIGIBLE_TRADES:
        eligibility_reason = f"trades {trades_count} < mínimo {MIN_ELIGIBLE_TRADES}"
    elif coverage < MIN_ELIGIBLE_COVERAGE:
        eligibility_reason = f"coverage {coverage:.0%} < mínimo {MIN_ELIGIBLE_COVERAGE:.0%}"

    existing = (
        db.query(DiscoveryResult)
        .filter(
            DiscoveryResult.strategy_identity_key == identity,
            DiscoveryResult.sweep_id == combination.sweep_id,
        )
        .first()
    )
    if existing:
        # Redelivery idempotente: resultado já commitado não reexecuta.
        combination.state = "succeeded"
        combination.result_id = existing.id
        combination.lease_owner = owner
        combination.updated_at = datetime.now(timezone.utc)
        db.commit()
        return

    result_id = f"RS-{uuid.uuid4().hex[:10].upper()}"
    cagr_f, calmar_f, benchmark_cagr, delta = _ranking_columns(best_metrics, len(trades))
    persisted_metrics = _persist_metrics_snapshot(best_metrics, result, len(trades))

    db.add(
        DiscoveryResult(
            id=result_id,
            sweep_id=combination.sweep_id,
            combination_id=combination.id,
            template_id=combination.template_id,
            template_version="v1",
            symbol=combination.symbol,
            timeframe=combination.timeframe,
            direction=combination.direction,
            parameters=parameters,
            start_at=start_at,
            end_at=end_at,
            candle_source=result.get("data_source"),
            candle_version=None,
            expected_candles=expected_candles,
            observed_valid_candles=observed_valid_candles,
            coverage=coverage,
            fees_slippage={"fees": 0.001, "slippage": 0.001},
            metrics=persisted_metrics,
            trades_count=trades_count,
            win_rate=best_metrics.get("win_rate"),
            sharpe_ratio=best_metrics.get("sharpe_ratio"),
            profit_factor=best_metrics.get("profit_factor"),
            max_drawdown=best_metrics.get("max_drawdown"),
            calmar_ratio=calmar_f,
            cagr=cagr_f,
            benchmark_cagr=benchmark_cagr,
            delta_cagr_vs_bh=delta,
            strategy_identity_key=identity,
            evidence_fingerprint=evidence,
            eligibility="eligible" if eligible else "low_sample",
            eligibility_reason=eligibility_reason,
            dedup_state="unique",
        )
    )
    combination.state = "succeeded"
    combination.result_id = result_id
    combination.lease_owner = owner
    combination.updated_at = datetime.now(timezone.utc)
    db.commit()
    logger.info(
        "Discovery combination completed: sweep=%s combination=%s result=%s eligibility=%s",
        combination.sweep_id,
        combination.id,
        result_id,
        "eligible" if eligible else "low_sample",
    )


def _finite_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _close_series_from_candles(candles: list[Any]):
    import pandas as pd

    if not candles:
        return None
    times: list[Any] = []
    closes: list[float] = []
    for candle in candles:
        if not isinstance(candle, dict):
            continue
        ts = candle.get("timestamp_utc") or candle.get("timestamp")
        close = candle.get("close")
        if ts is None or close is None:
            continue
        try:
            times.append(pd.Timestamp(ts))
            closes.append(float(close))
        except (TypeError, ValueError):
            continue
    if not closes:
        return None
    return pd.Series(closes, index=times)


def _ensure_in_sample_ranking(
    best_metrics: dict[str, Any],
    trades: list[Any],
    candles: list[Any],
) -> None:
    """Fill IS CAGR/Calmar/B&H when the optimizer omitted them (holdout ERROR)."""
    if not trades:
        return
    cagr = _finite_or_none(best_metrics.get("cagr"))
    if cagr is not None:
        return
    from app.services.combo_optimizer import _enrich_ranking_metrics

    _enrich_ranking_metrics(
        trades,
        _close_series_from_candles(candles),
        best_metrics,
        legacy_zero_trade_ranking=False,
    )


def _ranking_columns(
    best_metrics: dict[str, Any], trades_count: int
) -> tuple[float | None, float | None, float | None, float | None]:
    if trades_count == 0:
        return None, None, None, None
    cagr_f = _finite_or_none(best_metrics.get("cagr"))
    calmar_f = _finite_or_none(best_metrics.get("calmar_ratio"))
    benchmark_cagr = _finite_or_none((best_metrics.get("benchmark") or {}).get("cagr"))
    delta = (
        (cagr_f - benchmark_cagr) * 100
        if cagr_f is not None and benchmark_cagr is not None
        else None
    )
    return cagr_f, calmar_f, benchmark_cagr, delta


def _persist_metrics_snapshot(
    best_metrics: dict[str, Any], result: dict[str, Any], trades_count: int
) -> dict[str, Any]:
    metrics = dict(best_metrics)
    if trades_count == 0:
        metrics.pop("cagr", None)
        metrics.pop("calmar_ratio", None)
        metrics.pop("benchmark", None)
    _drop_nonfinite_ranking_keys(metrics)
    oos_metrics = result.get("oos_metrics")
    oos_verdict = result.get("oos_verdict")
    split_applied = isinstance(oos_verdict, dict) or isinstance(oos_metrics, dict)
    metrics["split_train_ratio"] = DISCOVERY_SPLIT_TRAIN_RATIO
    metrics["split_applied"] = split_applied
    if isinstance(oos_metrics, dict):
        oos_copy = dict(oos_metrics)
        _drop_nonfinite_ranking_keys(oos_copy)
        metrics["oos_metrics"] = oos_copy
    if isinstance(oos_verdict, dict):
        metrics["oos_verdict"] = oos_verdict
    return metrics


def _drop_nonfinite_ranking_keys(metrics: dict[str, Any]) -> None:
    """JSONB rejects Infinity/NaN; ranking non-finite values become omitted keys."""
    for key in ("cagr", "calmar_ratio"):
        if key in metrics and _finite_or_none(metrics.get(key)) is None:
            metrics.pop(key, None)
    benchmark = metrics.get("benchmark")
    if isinstance(benchmark, dict) and _finite_or_none(benchmark.get("cagr")) is None:
        metrics.pop("benchmark", None)


def _expected_candles_for_window(timeframe: str, start_at: datetime, end_at: datetime) -> int:
    """Calendário 24x7: número de candles esperados no intervalo [start, end)
    para 4h (6/dia) ou 1d (1/dia). Fonte de coverage versionada."""
    delta = end_at - start_at
    hours = delta.total_seconds() / 3600.0
    if hours <= 0:
        return 0
    if timeframe == "4h":
        return max(1, int(hours // 4))
    return max(1, int(hours // 24) + (1 if hours % 24 > 0 else 0))


def _first_candle_time(candles: list[Any], snapshot: dict[str, Any]) -> datetime:
    if candles:
        try:
            ts = candles[0].get("timestamp_utc") or candles[0].get("timestamp")
            return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except Exception:
            pass
    return datetime.now(timezone.utc)


def _last_candle_time(candles: list[Any], snapshot: dict[str, Any]) -> datetime:
    if candles:
        try:
            ts = candles[-1].get("timestamp_utc") or candles[-1].get("timestamp")
            return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except Exception:
            pass
    return datetime.now(timezone.utc)
