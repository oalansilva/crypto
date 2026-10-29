"""Descoberta com cripto, ação e ETF na mesma varredura (card #1121).

Reúne o que o Preflight, a varredura e o ranking precisam saber de cada classe:

* ``by_class``: ativos e combinações que vão rodar, por classe e moeda (decisão 2);
* ``forecast``: quem precisa de coleta, a precisão diária prevista e o começo da janela (decisões 6, 9, 12);
* ``precision_of``: a marca de precisão de um resultado, derivada da execução (decisão 6);
* ``sweep_assets``: o estado de cada ativo da varredura para o quadro "Por ativo" (decisão 7);
* ``no_candles_reason``: o motivo "sem candles" de uma combinação sem série na janela (decisão 7).

Não coleta nada: lê o catálogo (#1117), a cobertura guardada (#1118) e as linhas da varredura.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Iterable

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

CLASS_CRYPTO = "crypto"
CLASS_STOCK = "stock"
CLASS_ETF = "etf"
CLASSES = (CLASS_CRYPTO, CLASS_STOCK, CLASS_ETF)
EQUITY_CLASSES = (CLASS_STOCK, CLASS_ETF)
DERIVED_FROM_5M = ("15m", "1h", "4h")

_MONTHS = [
    "jan.",
    "fev.",
    "mar.",
    "abr.",
    "mai.",
    "jun.",
    "jul.",
    "ago.",
    "set.",
    "out.",
    "nov.",
    "dez.",
]


# ---------------------------------------------------------------- classe e moeda


def class_of(symbol: str, asset_class: str | None = None) -> str:
    """Classe do ativo: a do catálogo, da proveniência ou da execução quando há.

    Sem classe conhecida, o ativo segue como cripto (o comportamento de antes do #1121): ação e ETF só
    são tratados como tal quando o catálogo ou a amostra dizem a classe, nunca pelo formato do símbolo.
    """

    if asset_class in CLASSES:
        return asset_class
    return CLASS_CRYPTO


def is_equity(symbol: str, asset_class: str | None = None) -> bool:
    return class_of(symbol, asset_class) in EQUITY_CLASSES


def currency_of(symbol: str, asset_class: str | None = None) -> str:
    """USDT (ou a cotação do par) na cripto; USD na ação e no ETF. Nunca as duas na mesma linha."""

    if class_of(symbol, asset_class) == CLASS_CRYPTO:
        return str(symbol).split("/", 1)[1] if "/" in str(symbol) else "USDT"
    return "USD"


def pt_day(value: Any) -> str | None:
    """``2 jan. 2003`` pelo dia UTC do instante (candle de ação/ETF fica na meia-noite de NY)."""

    if value is None or value == "":
        return None
    try:
        ts = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None
    if ts.tzinfo is not None:
        ts = ts.tz_convert("UTC")
    return f"{ts.day} {_MONTHS[ts.month - 1]} {ts.year}"


def iso_day(value: Any) -> str | None:
    if value is None or value == "":
        return None
    try:
        ts = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None
    if ts.tzinfo is not None:
        ts = ts.tz_convert("UTC")
    return ts.strftime("%Y-%m-%d")


def by_class(
    combinations: Iterable[dict[str, Any]], classes: dict[str, str | None]
) -> dict[str, dict[str, Any]]:
    """``{classe: {assets, combinations, currency}}`` só com as classes que vão rodar."""

    out: dict[str, dict[str, Any]] = {}
    seen: dict[str, set[str]] = {}
    for combo in combinations:
        symbol = combo["symbol"]
        cls = class_of(symbol, classes.get(symbol))
        bucket = out.setdefault(
            cls, {"assets": 0, "combinations": 0, "currency": currency_of(symbol, cls)}
        )
        bucket["combinations"] += 1
        if symbol not in seen.setdefault(cls, set()):
            seen[cls].add(symbol)
            bucket["assets"] += 1
    return {cls: out[cls] for cls in CLASSES if cls in out}


def by_class_text(counts: dict[str, dict[str, Any]]) -> str:
    """``1 cripto · 2.431 ações · 1 ETF``."""

    parts = []
    for cls in CLASSES:
        n = int((counts.get(cls) or {}).get("assets") or 0)
        if not n:
            continue
        label = {
            CLASS_CRYPTO: "cripto",
            CLASS_STOCK: "ação" if n == 1 else "ações",
            CLASS_ETF: "ETF" if n == 1 else "ETFs",
        }[cls]
        parts.append(f"{fmt_int(n)} {label}")
    return " · ".join(parts)


def fmt_int(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


# ---------------------------------------------------------------- previsão do Preflight


def _window(start_date: str | None, end_date: str | None, now: pd.Timestamp):
    start = pd.Timestamp(start_date, tz="UTC") if start_date else None
    end = (
        pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        if end_date
        else now
    )
    return start, end


def _ts(value: Any) -> pd.Timestamp | None:
    if not value:
        return None
    ts = pd.Timestamp(value)
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def forecast(
    symbols: list[str],
    timeframes: list[str],
    *,
    start_date: str | None,
    end_date: str | None,
    db: Any = None,
    now: pd.Timestamp | None = None,
) -> dict[str, Any]:
    """Coleta e precisão previstas antes de começar (decisões 6 e 9) e o começo da janela (12).

    Mesma regra do ``needs_collection`` do lote (#1120): conta só o que a Binance tem para a janela
    e não está guardado. A previsão nunca troca a marca do resultado, que vem da execução.
    """

    from app.services.asset_catalog_service import AssetCheck, check_assets
    from app.services.batch_backtest_plan import (
        COLLECT_BINANCE_NONE,
        COLLECT_NONE,
        _coverage,
        _equity_5m_horizon,
        _series_for,
        _series_need,
    )

    own = db is None
    if own:
        from app.database import SessionLocal

        db = SessionLocal()
    now = now or pd.Timestamp.now(tz="UTC")
    window_start, window_end = _window(start_date, end_date, now)
    collection_assets: list[dict[str, Any]] = []
    stored: list[str] = []
    daily: list[dict[str, Any]] = []
    no_candles: list[dict[str, Any]] = []
    unknown: list[str] = []
    first_seen: list[pd.Timestamp] = []
    try:
        try:
            checks = check_assets(symbols, db=db)
        except SQLAlchemyError:
            checks = [AssetCheck(symbol=s, found=False, catalog_unavailable=True) for s in symbols]
        by_symbol = {c.symbol: c for c in checks}
        coverage = _coverage(db, [c.asset_id for c in checks if c.found and c.asset_id])
        horizon = _equity_5m_horizon(db)
        for symbol in symbols:
            check = by_symbol.get(symbol) or AssetCheck(symbol=symbol, found=False)
            cls = class_of(symbol, check.asset_class if check.found else None)
            equity = cls in EQUITY_CLASSES
            entries = coverage.get(check.asset_id or "", {})
            series_needed: list[str] = []
            for timeframe in timeframes:
                for label, role in _series_for(timeframe, equity, True):
                    entry = entries.get(label)
                    kind = _series_need(
                        entry,
                        window_start=window_start,
                        window_end=window_end,
                        now=now,
                        equity=equity,
                        binance_horizon=horizon if (equity and label == "5m") else None,
                    )
                    if role == "candles" and entry and entry.get("from"):
                        first_seen.append(_ts(entry["from"]))
                    if kind in (COLLECT_NONE, COLLECT_BINANCE_NONE):
                        continue
                    name = f"{label} do intrabar" if role == "intraday" else label
                    if name not in series_needed:
                        series_needed.append(name)
                if equity:
                    _predict_precision(
                        symbol,
                        timeframe,
                        entries,
                        window_start=window_start,
                        window_end=window_end,
                        horizon=horizon,
                        daily=daily,
                        no_candles=no_candles,
                        unknown=unknown,
                    )
            if series_needed:
                collection_assets.append(
                    {"symbol": symbol, "asset_class": cls, "series": series_needed}
                )
            else:
                stored.append(symbol)
    finally:
        if own:
            db.close()
    window_first = window_start or (min(first_seen) if first_seen else None)
    return {
        "collection": {
            "count": len(collection_assets),
            "of": len(symbols),
            "assets": collection_assets,
            "stored": stored,
        },
        "precision_forecast": {
            "daily": daily,
            "no_candles": no_candles,
            "unknown": list(dict.fromkeys(unknown)),
        },
        "survivorship": {
            "catalog_as_of": now.isoformat(),
            "window": {
                "start": iso_day(window_first),
                "start_label": pt_day(window_first),
                "end": iso_day(window_end) if end_date else None,
                "end_label": pt_day(window_end) if end_date else None,
            },
        },
    }


def _predict_precision(
    symbol: str,
    timeframe: str,
    entries: dict[str, dict[str, Any]],
    *,
    window_start: pd.Timestamp | None,
    window_end: pd.Timestamp,
    horizon: pd.Timestamp | None,
    daily: list[dict[str, Any]],
    no_candles: list[dict[str, Any]],
    unknown: list[str],
) -> None:
    """Ação/ETF: 1d sem 15m no começo da janela cai para o candle diário; 15m/1h/4h sem 5m não têm candles."""

    five = entries.get("5m") or {}
    five_from = _ts(five.get("from"))
    five_starts = _ts(five.get("starts_at")) or five_from or horizon
    if timeframe in DERIVED_FROM_5M:
        # 15m, 1h e 4h saem do 5m: sem 5m na janela não há candle nenhum.
        if five_starts is not None and five_starts > window_end:
            no_candles.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "five_from": iso_day(five_starts),
                    "five_from_label": pt_day(five_starts),
                }
            )
        return
    chart = entries.get(timeframe) or {}
    chart_from = _ts(chart.get("from"))
    if five_from is None:
        if horizon is not None and horizon > window_end:
            start = window_start or chart_from
            daily.append(_stretch(symbol, timeframe, start, window_end, horizon))
        elif chart_from is None or not five:
            unknown.append(symbol)
        return
    begin = (
        max(x for x in (window_start, chart_from) if x is not None)
        if (window_start or chart_from)
        else None
    )
    if begin is None:
        unknown.append(symbol)
        return
    if five_from - begin <= pd.Timedelta(days=4):
        return  # o 15m cobre a janela: precisão intrabar
    end = min(five_from - pd.Timedelta(days=1), window_end)
    daily.append(_stretch(symbol, timeframe, begin, end, five_from))


def _stretch(symbol, timeframe, start, end, five_from) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "from": iso_day(start),
        "to": iso_day(end),
        "from_label": pt_day(start),
        "to_label": pt_day(end),
        "five_from": iso_day(five_from),
        "five_from_label": pt_day(five_from),
    }


def survivorship(start_date: str | None, end_date: str | None) -> dict[str, Any]:
    """Viés de sobrevivência sem ler a cobertura: a janela pedida (``todo o histórico`` sem começo)."""

    now = pd.Timestamp.now(tz="UTC")
    start, end = _window(start_date, end_date, now)
    return {
        "catalog_as_of": now.isoformat(),
        "window": {
            "start": iso_day(start),
            "start_label": pt_day(start),
            "end": iso_day(end) if end_date else None,
            "end_label": pt_day(end) if end_date else None,
        },
    }


# ---------------------------------------------------------------- precisão do resultado


def precision_of(execution: Any) -> dict[str, Any] | None:
    """Marca de precisão de um resultado (decisão 6), igual à de Favoritos (``precisionText``).

    ``intrabar_15m`` com o 15m cobrindo a janela; ``daily`` com os trechos sem 15m. Resultado antigo,
    sem ``execution``, devolve ``None`` ("Precisão: não registrada nesta varredura").
    """

    if not isinstance(execution, dict) or not execution:
        return None
    effective = execution.get("precision_effective")
    missing = [
        {"from": m.get("from"), "to": m.get("to")}
        for m in (execution.get("intraday_missing") or [])
        if isinstance(m, dict)
    ]
    if effective == "intrabar_15m":
        return {"kind": "intrabar_15m", "missing": []}
    requested = execution.get("precision_requested")
    if requested == "intrabar" or missing:
        return {"kind": "daily", "missing": missing, "reason": execution.get("intraday_reason")}
    return {"kind": "candle", "missing": missing}


# ---------------------------------------------------------------- "sem candles"


def no_candles_reason(symbol: str, timeframe: str, *, asset_class: str | None = None) -> str:
    """``sem candles de 4h de NVDA nessa janela (o 5m da Binance começa em 2 jan. 2026)``."""

    reason = f"sem candles de {timeframe} de {symbol} nessa janela"
    if is_equity(symbol, asset_class) and timeframe in DERIVED_FROM_5M:
        start = _five_minute_start(symbol)
        if start is not None:
            reason += f" (o 5m da Binance começa em {pt_day(start)})"
    return reason[:128]


def _five_minute_start(symbol: str) -> pd.Timestamp | None:
    """Onde a Binance começa o 5m do ativo (ou, sem a série dele, o das ações e ETFs)."""

    from sqlalchemy import text

    from app.database import SessionLocal

    db = SessionLocal()
    try:
        with db.begin_nested():
            value = db.execute(
                text(
                    "SELECT coalesce(f.binance_earliest, c.first_candle) FROM market_series s "
                    "LEFT JOIN market_series_coverage c ON c.series_id = s.series_id "
                    "LEFT JOIN market_series_fetch f ON f.series_id = s.series_id "
                    "WHERE s.source = 'binance_equity' AND s.timeframe = '5m' AND s.symbol = :sym "
                    "ORDER BY f.reached_start DESC NULLS LAST LIMIT 1"
                ),
                {"sym": symbol},
            ).scalar()
        if value is None:
            from app.services.batch_backtest_plan import _equity_5m_horizon

            return _equity_5m_horizon(db)
        return _ts(value)
    except SQLAlchemyError:
        return None
    finally:
        db.close()


# ---------------------------------------------------------------- estado por ativo


TERMINAL_COMBINATION = ("succeeded", "insufficient_sample", "failed", "skipped")


def _failure_reason(symbol: str, code: str | None, attempts: int, max_attempts: int) -> str:
    from app.services.equity_backtest import failure_text

    code = str(code or "")
    if code.startswith("history_"):
        detail = code.split(":", 1)[1] if ":" in code else None
        if detail and detail not in ("history_unavailable",):
            text_reason = failure_text(detail)
            if attempts >= max_attempts:
                return (
                    f"a Binance não respondeu ao histórico de {symbol} nas {max_attempts} tentativas"
                    f" ({text_reason})"
                )
            return text_reason
        if attempts >= max_attempts:
            return f"a Binance não respondeu ao histórico de {symbol} nas {max_attempts} tentativas"
        return "a Binance não respondeu"
    return f"falha operacional ({code})" if code else "falha operacional"


def sweep_assets(db: Any, sweep: Any) -> list[dict[str, Any]]:
    """Estado de cada ativo da varredura, na ordem da varredura (decisão 7).

    ``state``: ``queued``, ``collecting``, ``running``, ``done``, ``done_daily``, ``insufficient``,
    ``failed``, ``not_run`` ou ``mixed`` (desfechos diferentes, com ``outcomes``). ``details`` dá o
    desfecho por tempo (precisão e período efetivo, ou o motivo).
    """

    from app.models_discovery import DiscoveryAttempt, DiscoveryCombination, DiscoveryResult
    from app.services.discovery_recovery import MAX_ATTEMPTS

    snapshot = sweep.snapshot if isinstance(sweep.snapshot, dict) else {}
    classes = snapshot.get("asset_classes") or {}
    rows = (
        db.query(
            DiscoveryCombination.id,
            DiscoveryCombination.symbol,
            DiscoveryCombination.timeframe,
            DiscoveryCombination.state,
            DiscoveryCombination.attempts,
            DiscoveryCombination.last_failure_code,
            DiscoveryCombination.next_attempt_at,
        )
        .filter(DiscoveryCombination.sweep_id == sweep.id)
        .order_by(DiscoveryCombination.id)
        .all()
    )
    if not rows:
        return []
    results = {
        r.combination_id: r
        for r in db.query(
            DiscoveryResult.combination_id,
            DiscoveryResult.eligibility,
            DiscoveryResult.eligibility_reason,
            DiscoveryResult.asset_class,
            DiscoveryResult.period_covered,
            DiscoveryResult.start_at,
            DiscoveryResult.end_at,
            DiscoveryResult.metrics["execution"].label("execution"),
        )
        .filter(DiscoveryResult.sweep_id == sweep.id)
        .all()
    }
    running_ids = [r.id for r in rows if r.state == "running"]
    progress: dict[int, dict[str, Any]] = {}
    if running_ids:
        for attempt in (
            db.query(DiscoveryAttempt.combination_id, DiscoveryAttempt.counters)
            .join(
                DiscoveryCombination,
                (DiscoveryCombination.id == DiscoveryAttempt.combination_id)
                & (DiscoveryCombination.attempts == DiscoveryAttempt.attempt_seq),
            )
            .filter(DiscoveryAttempt.combination_id.in_(running_ids))
            .all()
        ):
            counters = attempt.counters or {}
            if counters.get("collecting") and "phase:input_snapshot" not in counters:
                progress[attempt.combination_id] = counters["collecting"]

    order = list(
        dict.fromkeys([*(snapshot.get("axes") or {}).get("symbols", []), *(r.symbol for r in rows)])
    )
    grouped: dict[str, list[Any]] = {}
    for row in rows:
        grouped.setdefault(row.symbol, []).append(row)

    out: list[dict[str, Any]] = []
    for symbol in order:
        combos = grouped.get(symbol)
        if not combos:
            continue
        result_class = next(
            (
                results[c.id].asset_class
                for c in combos
                if c.id in results and results[c.id].asset_class
            ),
            None,
        )
        cls = class_of(symbol, classes.get(symbol) or result_class)
        outcomes = {"succeeded": 0, "daily": 0, "insufficient": 0, "failed": 0, "skipped": 0}
        details: list[dict[str, Any]] = []
        reasons: list[str] = []
        current = None
        waiting = None
        for combo in combos:
            result = results.get(combo.id)
            if combo.state == "running":
                current = combo
            elif combo.state == "pending" and combo.attempts and waiting is None:
                waiting = combo
            if combo.state == "succeeded":
                precision = precision_of(result.execution if result else None)
                outcomes["succeeded"] += 1
                if precision and precision["kind"] == "daily":
                    outcomes["daily"] += 1
                details.append(
                    {
                        "timeframe": combo.timeframe,
                        "outcome": "succeeded",
                        "precision": precision,
                        "period": _period(result),
                    }
                )
            elif combo.state == "insufficient_sample":
                outcomes["insufficient"] += 1
                reason = (result.eligibility_reason if result else None) or "amostra insuficiente"
                reasons.append(reason)
                details.append(
                    {"timeframe": combo.timeframe, "outcome": "insufficient", "reason": reason}
                )
            elif combo.state == "failed":
                outcomes["failed"] += 1
                reason = _failure_reason(
                    symbol, combo.last_failure_code, combo.attempts, MAX_ATTEMPTS
                )
                reasons.append(reason)
                details.append(
                    {"timeframe": combo.timeframe, "outcome": "failed", "reason": reason}
                )
            elif combo.state == "skipped":
                outcomes["skipped"] += 1
                details.append({"timeframe": combo.timeframe, "outcome": "skipped"})
        done = sum(outcomes[k] for k in ("succeeded", "insufficient", "failed", "skipped"))
        total = len(combos)
        item: dict[str, Any] = {
            "symbol": symbol,
            "asset_class": cls,
            "currency": currency_of(symbol, cls),
            "done": done,
            "total": total,
            "state": "queued",
            "stage": None,
            "series": None,
            "page": None,
            "pages": None,
            "attempt": None,
            "max_attempts": MAX_ATTEMPTS,
            "reason": None,
            "outcomes": outcomes,
            "details": details,
        }
        if current is not None:
            collecting = progress.get(current.id)
            item["stage"] = current.timeframe
            item["attempt"] = current.attempts
            if collecting:
                item.update(
                    state="collecting",
                    series=collecting.get("series"),
                    page=collecting.get("page"),
                    pages=collecting.get("pages"),
                    role=collecting.get("role"),
                )
            else:
                item["state"] = "running"
            if current.attempts and current.attempts > 1 and current.last_failure_code:
                item["reason"] = _failure_reason(
                    symbol, current.last_failure_code, current.attempts - 1, MAX_ATTEMPTS
                )
        elif done < total:
            if waiting is not None:
                item["stage"] = waiting.timeframe
                item["attempt"] = waiting.attempts
                item["reason"] = _failure_reason(
                    symbol, waiting.last_failure_code, waiting.attempts, MAX_ATTEMPTS
                )
            item["state"] = "queued"
        else:
            kinds = [k for k in ("succeeded", "insufficient", "failed", "skipped") if outcomes[k]]
            if len(kinds) > 1:
                item["state"] = "mixed"
            elif kinds == ["succeeded"]:
                item["state"] = "done_daily" if outcomes["daily"] else "done"
            elif kinds == ["insufficient"]:
                item["state"] = "insufficient"
                item["reason"] = reasons[0] if reasons else None
            elif kinds == ["failed"]:
                item["state"] = "failed"
                item["reason"] = reasons[0] if reasons else None
            else:
                item["state"] = "not_run"
        out.append(item)
    return out


def _period(result: Any) -> dict[str, Any] | None:
    if result is None:
        return None
    covered = result.period_covered if isinstance(result.period_covered, dict) else {}
    start = covered.get("start") or (result.start_at.isoformat() if result.start_at else None)
    end = covered.get("end") or (result.end_at.isoformat() if result.end_at else None)
    if not start and not end:
        return None
    return {
        "start": iso_day(start),
        "end": iso_day(end),
        "start_label": pt_day(start),
        "end_label": pt_day(end),
    }


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
