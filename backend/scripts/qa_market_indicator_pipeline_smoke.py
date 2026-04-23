#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import text

from app.database import DB_URL, engine
from app.services.market_indicator_service import get_market_indicator_service
from app.services.market_indicator_service import ACTIVE_TIMEFRAMES


TIMEFRAME_TO_DELTA_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}


@dataclass
class QAResult:
    section: str
    status: str
    details: dict[str, Any]


def _read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Smoke/check script for market_indicator pipeline: starts a recompute job "
            "for symbol/timeframes and validates table health."
        )
    )
    parser.add_argument("--symbol", required=True, help="symbol, ex.: BTCUSDT")
    parser.add_argument(
        "--timeframes",
        nargs="+",
        default=["1d", "1h"],
        help="timeframes to exercise, ex.: 1d 1h",
    )
    parser.add_argument(
        "--force-full",
        action="store_true",
        help="pass force_full=true to recompute all data for each timeframe",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=600,
        help="max wait for background job completion",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=1.5,
        help="polling interval between status checks",
    )
    parser.add_argument(
        "--strict-gaps",
        action="store_true",
        help="fail if there are timestamp gaps bigger than 2x expected timeframe",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="optional JSON evidence output path",
    )
    return parser.parse_args()


def _to_timestamp(value: Any) -> pd.Timestamp:
    return pd.to_datetime(value, utc=True)


def _validate_timeframes(requested: list[str]) -> list[str]:
    normalized = []
    for tf in requested:
        candidate = str(tf).strip().lower()
        if candidate not in ACTIVE_TIMEFRAMES:
            raise SystemExit(f"invalid timeframe: {candidate}")
        normalized.append(candidate)
    if not normalized:
        normalized = list(ACTIVE_TIMEFRAMES)
    return normalized


def _wait_for_job(job_id: str, timeout_seconds: int, interval_seconds: float) -> dict[str, Any]:
    service = get_market_indicator_service()
    started = time.time()
    last = None

    while True:
        job = service.get_job(job_id)
        if not job:
            raise RuntimeError(f"job {job_id} not found")
        last = job
        status = str(job.get("status", "")).lower()
        if status in {"completed", "failed"}:
            return job

        if time.time() - started > timeout_seconds:
            raise TimeoutError(f"timeout waiting for job {job_id}: {last}")
        time.sleep(interval_seconds)


def _check_job(
    job_id: str,
    symbol: str,
    timeframes: list[str],
    timeout_seconds: int,
    interval_seconds: float,
) -> QAResult:
    job = _wait_for_job(job_id, timeout_seconds, interval_seconds)
    status = str(job.get("status", "unknown")).lower()
    if status != "completed":
        raise RuntimeError(f"job {job_id} did not complete cleanly: {job.get('error')}")

    details = {
        "job_id": job_id,
        "symbol": symbol.upper(),
        "timeframes": job.get("timeframes", timeframes),
        "estimated_bars": int(job.get("estimated_bars") or 0),
        "estimated_bars_remaining": int(job.get("estimated_bars_remaining") or 0),
        "processed_timeframes": int(job.get("processed_timeframes") or 0),
        "error": job.get("error"),
    }
    return QAResult(section="pipeline_job", status=status, details=details)


def _query_latest_rows(symbol: str, timeframes: list[str]) -> QAResult:
    rows_by_tf = {}
    with engine.begin() as conn:
        for tf in timeframes:
            rows = (
                conn.execute(
                    text(
                        """
                        SELECT
                            ts,
                            ema_9,
                            ema_21,
                            sma_20,
                            sma_50,
                            rsi_14,
                            macd_line,
                            macd_signal,
                            macd_histogram,
                            source,
                            provider,
                            is_recomputed,
                            row_count,
                            source_window,
                            updated_at
                        FROM market_indicator
                        WHERE symbol = :symbol
                          AND timeframe = :timeframe
                        ORDER BY ts DESC
                        LIMIT 5
                        """
                    ),
                    {"symbol": symbol, "timeframe": tf},
                )
                .mappings()
                .all()
            )
            rows_by_tf[tf] = [dict(r) for r in rows]

    missing = [tf for tf, rows in rows_by_tf.items() if not rows]
    if missing:
        raise RuntimeError(f"no indicators found after recompute for timeframes: {missing}")

    return QAResult(
        section="latest_rows",
        status="pass",
        details={tf: {"count": len(rows), "latest_ts": str(rows[0]["ts"]) if rows else None} for tf, rows in rows_by_tf.items()},
    )


def _check_uniqueness_and_utc(symbol: str, timeframes: list[str], strict_gaps: bool) -> list[QAResult]:
    duplicates = []
    tz_ok = []
    gaps = []

    with engine.begin() as conn:
        for tf in timeframes:
            dup_rows = (
                conn.execute(
                    text(
                        """
                        SELECT ts, COUNT(*) AS total
                        FROM market_indicator
                        WHERE symbol = :symbol
                          AND timeframe = :timeframe
                        GROUP BY symbol, timeframe, ts
                        HAVING COUNT(*) > 1
                        ORDER BY ts ASC
                        """
                    ),
                    {"symbol": symbol, "timeframe": tf},
                )
                .all()
            )
            if dup_rows:
                duplicates.append({"timeframe": tf, "rows": [list(r) for r in dup_rows]})

            ts_rows = (
                conn.execute(
                    text(
                        """
                        SELECT ts
                        FROM market_indicator
                        WHERE symbol = :symbol
                          AND timeframe = :timeframe
                        ORDER BY ts ASC
                        """
                    ),
                    {"symbol": symbol, "timeframe": tf},
                )
                .scalars()
                .all()
            )
            parsed = [_to_timestamp(item) for item in ts_rows]

            if parsed:
                tz_ok.append(
                    {
                        "timeframe": tf,
                        "count": len(parsed),
                        "tz_aware": all(ts.tzinfo is not None for ts in parsed),
                        "monotonic": all(parsed[i] > parsed[i - 1] for i in range(1, len(parsed))),
                    }
                )

            if strict_gaps and len(parsed) >= 2:
                expected = pd.Timedelta(seconds=TIMEFRAME_TO_DELTA_SECONDS[tf])
                deltas = pd.Series(parsed).diff().dropna()
                too_large = [float(delta.total_seconds()) for delta in deltas if delta > (2 * expected)]
                if too_large:
                    gaps.append({"timeframe": tf, "oversized_gaps": too_large})

    if duplicates:
        raise RuntimeError(f"duplicate indicator keys detected: {duplicates}")

    for row in tz_ok:
        if not row["tz_aware"]:
            raise RuntimeError(f"timezone not set in market_indicator.ts for {row['timeframe']}")

    if strict_gaps and gaps:
        raise RuntimeError(f"large timestamp gaps detected: {gaps}")

    return [
        QAResult(section="uniqueness_and_tz", status="pass", details={"rows": tz_ok}),
        QAResult(section="gaps", status="pass", details={"timeframes": [row["timeframe"] for row in tz_ok]}),
    ]


def _to_pretty(results: list[QAResult]) -> str:
    lines = []
    for idx, result in enumerate(results, 1):
        lines.append(f"{idx}. {result.section}: {result.status}")
        for key, value in result.details.items():
            lines.append(f"   - {key}: {json.dumps(value, default=str)}")
    return "\n".join(lines)


def _run(args: argparse.Namespace) -> int:
    if not str(DB_URL).startswith("postgresql"):
        raise RuntimeError("QA smoke check for market_indicator requires PostgreSQL (DATABASE_URL).")

    symbol = args.symbol.strip().upper()
    timeframes = _validate_timeframes(args.timeframes)
    service = get_market_indicator_service()

    print(f"Starting recompute for {symbol} timeframes={timeframes} force_full={args.force_full}")
    job = service.start_recompute(symbol=symbol, timeframes=timeframes, force_full=args.force_full)
    job_id = job["job_id"]

    results = []
    results.append(QAResult(section="start", status="accepted", details={"job_id": job_id}))
    results.append(
        _check_job(
            job_id,
            symbol,
            timeframes,
            timeout_seconds=args.timeout_seconds,
            interval_seconds=args.interval_seconds,
        )
    )
    results.append(_query_latest_rows(symbol, timeframes))
    results.extend(_check_uniqueness_and_utc(symbol, timeframes, strict_gaps=args.strict_gaps))

    print(_to_pretty(results))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(
                {
                    "symbol": symbol,
                    "timeframes": timeframes,
                    "force_full": bool(args.force_full),
                    "results": [result.__dict__ for result in results],
                },
                default=str,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Evidence written to {args.output}")

    return 0


if __name__ == "__main__":
    args = _read_args()
    try:
        raise SystemExit(_run(args))
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover
        print(f"FAILED: {exc}")
        raise SystemExit(1)
