"""Plano do lote multiclasse (card #1120, decisões 3, 4 e 6).

``build_plan`` diz, por ativo, se roda ou fica fora (e por quê), de que classe e moeda ele é e se
precisa de coleta de histórico antes de otimizar. Não coleta nada e não grava nada: lê o catálogo
(#1117) e a cobertura guardada (#1118). O lote recalcula o plano ao começar e grava o resultado.

Regras de "fora" (decisão 4):

* ação/ETF com tempo fora de 15m, 1h, 4h e 1d (``timeframe_refusal`` do #1119);
* na Otimização (janela fixa), ação/ETF em 15m, 1h ou 4h cujo 5m guardado começa depois do início
  da janela: o 15m, 1h e 4h saem do 5m;
* ativo marcado pela Binance ou fora do catálogo.

Uma série **precisa de coleta** quando, dentro da janela pedida, a Binance tem candles que ainda
não estão guardados (ativo sob demanda, lacuna na cabeça ou o trecho desde a última coleta). O que
a Binance não tem não conta.
"""

from __future__ import annotations

import logging
from typing import Any, Iterable

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.services.asset_catalog_adapters import CLASS_CRYPTO, CLASS_ETF, CLASS_STOCK
from app.services.asset_catalog_service import STATE_LABELS, AssetCheck, check_assets
from app.services.equity_backtest import is_equity_class, timeframe_refusal
from app.services.market_data_providers import BINANCE_EQUITY_SOURCE, CCXT_SOURCE

logger = logging.getLogger(__name__)

PLAN_RUN = "run"
PLAN_OUT = "out"
COLLECT_NONE = "none"
COLLECT_MISSING = "missing"
COLLECT_TAIL = "tail"
# A Binance não tem candles dessa série dentro da janela: não conta como coleta (decisão 4).
COLLECT_BINANCE_NONE = "binance_none"

OPTIMIZE_DEFAULT_WINDOW = ("2024-01-01", "2024-01-31")
DERIVED_FROM_5M = ("15m", "1h", "4h")
MISSING_REASON = "ativo fora do catálogo da Binance"

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


def pt_date(value: Any, zone: str = "America/New_York") -> str:
    """``19 mai. 2026`` (dia no fuso informado)."""

    ts = pd.Timestamp(value)
    ts = ts.tz_localize("UTC") if ts.tzinfo is None else ts
    local = ts.tz_convert(zone)
    return f"{local.day} {_MONTHS[local.month - 1]} {local.year}"


def window_label(start: str, end: str) -> str:
    """``1 a 31 jan. 2024``."""

    a, b = pd.Timestamp(start), pd.Timestamp(end)
    if (a.year, a.month) == (b.year, b.month):
        return f"{a.day} a {b.day} {_MONTHS[b.month - 1]} {b.year}"
    return f"{a.day} {_MONTHS[a.month - 1]} {a.year} a {b.day} {_MONTHS[b.month - 1]} {b.year}"


def _window_months(start: pd.Timestamp | None, end: pd.Timestamp) -> str:
    """``jan. 2024`` (ou ``jan. 2024 a mar. 2024``) da janela pedida."""

    first = start if start is not None else end
    a = f"{_MONTHS[first.month - 1]} {first.year}"
    b = f"{_MONTHS[end.month - 1]} {end.year}"
    return a if a == b else f"{a} a {b}"


def class_key(asset_class: str | None) -> str | None:
    return asset_class if asset_class in (CLASS_CRYPTO, CLASS_STOCK, CLASS_ETF) else None


def currency_of(symbol: str, asset_class: str | None) -> str | None:
    if "/" in symbol:
        return symbol.split("/", 1)[1] or "USDT"
    return "USD" if asset_class in (CLASS_STOCK, CLASS_ETF, None) else None


def dedupe(symbols: Iterable[str]) -> list[str]:
    return list(
        dict.fromkeys(str(s or "").strip().upper() for s in symbols if str(s or "").strip())
    )


def _equity_5m_horizon(db: Any) -> pd.Timestamp | None:
    """Onde a Binance começa o 5m de ações/ETFs, pelas séries já coletadas até o começo."""

    try:
        with db.begin_nested():
            value = db.execute(
                text(
                    "SELECT min(f.binance_earliest) FROM market_series_fetch f "
                    "JOIN market_series s ON s.series_id = f.series_id "
                    "WHERE s.source = 'binance_equity' AND s.timeframe = '5m' "
                    "AND f.reached_start AND f.binance_earliest IS NOT NULL"
                )
            ).scalar()
    except SQLAlchemyError:
        return None
    if value is None:
        return None
    ts = pd.Timestamp(value)
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def _coverage(db: Any, asset_ids: list[str]) -> dict[str, dict[str, Any]]:
    """``asset_id`` -> ``{timeframe: entrada}`` lido da mesma cobertura do seletor (#1118)."""

    if not asset_ids:
        return {}
    from app.models_asset_catalog import AssetCatalog
    from app.services.market_history.catalog_coverage import coverage_for_assets

    try:
        rows = db.query(AssetCatalog).filter(AssetCatalog.asset_id.in_(asset_ids)).all()
        histories = coverage_for_assets(db, rows)
    except SQLAlchemyError:
        logger.info("Cobertura indisponível para o plano do lote; tudo conta como a coletar")
        return {}
    return {
        asset_id: {entry["timeframe"]: entry for entry in (history.get("timeframes") or [])}
        for asset_id, history in histories.items()
    }


def _series_need(
    entry: dict[str, Any] | None,
    *,
    window_start: pd.Timestamp | None,
    window_end: pd.Timestamp,
    now: pd.Timestamp,
    equity: bool,
    binance_horizon: pd.Timestamp | None = None,
) -> str:
    """``none`` | ``missing`` | ``tail`` para uma série e a janela pedida."""

    if entry is None or not entry.get("from"):
        # Sem nada guardado: conta, salvo se a Binance sabidamente não tem nada na janela.
        if binance_horizon is not None and binance_horizon > window_end:
            return COLLECT_BINANCE_NONE
        return COLLECT_MISSING
    if entry.get("state") == "collecting" or entry.get("incomplete"):
        return COLLECT_MISSING
    tolerance = pd.Timedelta(days=5 if equity else 2)
    first = pd.Timestamp(entry["from"]).tz_convert("UTC")
    last = pd.Timestamp(entry["to"]).tz_convert("UTC") if entry.get("to") else first
    starts_at = entry.get("starts_at")
    # A Binance não tem nada dentro da janela: nada a coletar.
    if starts_at and pd.Timestamp(starts_at).tz_convert("UTC") > window_end:
        return COLLECT_BINANCE_NONE
    # Cabeça não confirmada (a coleta nunca chegou ao começo da Binance): ainda pode haver candles.
    if not starts_at and (window_start is None or first > window_start + tolerance):
        return COLLECT_MISSING
    reference = min(window_end, now)
    if last + tolerance < reference:
        return COLLECT_TAIL
    return COLLECT_NONE


def _series_for(timeframe: str, equity: bool, deep: bool) -> list[tuple[str, str]]:
    """Séries físicas olhadas: ``[(rótulo, papel)]``; o 15m de ação/ETF sai do 5m."""

    tf = str(timeframe).lower()
    chart = ("5m" if equity and tf in DERIVED_FROM_5M else tf, "candles")
    series = [chart]
    if equity and deep and chart[0] != "5m":
        series.append(("5m", "intraday"))
    return series


def build_plan(
    payload: dict[str, Any],
    *,
    db: Any = None,
    page: str | None = None,
    now: pd.Timestamp | None = None,
) -> dict[str, Any]:
    """Plano do lote (ver o módulo). ``payload`` é o corpo de ``POST /backtest/batch``."""

    own = db is None
    if own:
        from app.database import SessionLocal

        db = SessionLocal()
    try:
        return _build_plan(payload, db=db, page=page or payload.get("page"), now=now)
    finally:
        if own:
            db.close()


def _build_plan(
    payload: dict[str, Any], *, db: Any, page: str | None, now: pd.Timestamp | None
) -> dict[str, Any]:
    now = now or pd.Timestamp.now(tz="UTC")
    symbols = dedupe(payload.get("symbols") or [])
    timeframe = str(payload.get("timeframe") or "1d").lower()
    deep = bool(payload.get("deep_backtest", True))
    fixed = page == "optimize"
    start_raw = payload.get("start_date") or (OPTIMIZE_DEFAULT_WINDOW[0] if fixed else None)
    end_raw = payload.get("end_date") or (OPTIMIZE_DEFAULT_WINDOW[1] if fixed else None)
    window_start = pd.Timestamp(start_raw, tz="UTC") if start_raw else None
    window_end = (
        pd.Timestamp(end_raw, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        if end_raw
        else now
    )

    try:
        checks = check_assets(symbols, db=db)
    except SQLAlchemyError:
        logger.exception("Catálogo indisponível no plano do lote; plano pelo formato do símbolo")
        checks = [AssetCheck(symbol=s, found=False, catalog_unavailable=True) for s in symbols]
    by_symbol = {c.symbol: c for c in checks}
    coverage = _coverage(db, [c.asset_id for c in checks if c.found and c.asset_id])
    horizon = _equity_5m_horizon(db)

    items: list[dict[str, Any]] = []
    for symbol in symbols:
        check = by_symbol.get(symbol) or AssetCheck(symbol=symbol, found=False)
        items.append(
            _plan_item(
                symbol,
                check,
                coverage=coverage.get(check.asset_id or "", {}),
                timeframe=timeframe,
                deep=deep,
                fixed=fixed,
                window_start=window_start,
                window_end=window_end,
                window_text=window_label(start_raw, end_raw) if (start_raw and end_raw) else None,
                now=now,
                horizon=horizon,
            )
        )
    return {
        "items": items,
        "totals": _totals(items),
        "config": {
            "template_name": payload.get("template_name"),
            "timeframe": timeframe,
            "start_date": start_raw,
            "end_date": end_raw,
            "page": page,
            "deep_backtest": deep,
            "direction": payload.get("direction", "long"),
        },
    }


def _out(item: dict[str, Any], reason: str, kind: str) -> dict[str, Any]:
    item.update(plan=PLAN_OUT, reason=reason, out_kind=kind)
    return item


def _plan_item(
    symbol: str,
    check: AssetCheck,
    *,
    coverage: dict[str, Any],
    timeframe: str,
    deep: bool,
    fixed: bool,
    window_start: pd.Timestamp | None,
    window_end: pd.Timestamp,
    window_text: str | None,
    now: pd.Timestamp,
    horizon: pd.Timestamp | None,
) -> dict[str, Any]:
    is_crypto_symbol = "/" in symbol
    asset_class = (
        class_key(check.asset_class)
        if check.found
        else (CLASS_CRYPTO if is_crypto_symbol else None)
    )
    equity = is_equity_class(asset_class) or (not is_crypto_symbol and not check.found)
    item: dict[str, Any] = {
        "symbol": symbol,
        "asset_id": check.asset_id,
        "asset_class": asset_class,
        "currency": currency_of(symbol, asset_class),
        "plan": PLAN_RUN,
        "reason": None,
        "needs_collection": [],
        "collect_note": None,
        "collect_kind": COLLECT_NONE,
        "covered_until": None,
        "data_source": BINANCE_EQUITY_SOURCE if equity else CCXT_SOURCE,
    }

    # ---- fora: ativo marcado, fora do catálogo, tempo ou cobertura
    if check.found and not check.selectable:
        label = STATE_LABELS.get(check.state or "", check.state or "")
        reason = (check.state_reason or label).strip().rstrip(".")
        return _out(item, f"{reason}; não entra em análise nova", "marked")
    if not check.found and not check.catalog_unavailable:
        return _out(item, MISSING_REASON, "missing")
    if not check.found and check.catalog_unavailable and equity:
        return _out(
            item,
            "o catálogo de ações e ETFs está indisponível agora; tente de novo em alguns minutos",
            "catalog_unavailable",
        )
    if equity:
        if timeframe_refusal(timeframe) is not None:
            advice = (
                "para incluí-los, use 1d aqui ou o Combo, que tem período"
                if fixed
                else "para incluí-los, use 15m, 1h, 4h ou 1d"
            )
            return _out(item, f"ação e ETF não rodam em {timeframe}; {advice}", "timeframe")
        if fixed and timeframe in DERIVED_FROM_5M and window_start is not None and window_text:
            five = coverage.get("5m")
            starts = (
                pd.Timestamp(five["from"]).tz_convert("UTC")
                if five and five.get("from")
                else horizon
            )
            if starts is not None and starts > window_start + pd.Timedelta(
                hours=23, minutes=59, seconds=59
            ):
                return _out(
                    item,
                    f"o 5m de {symbol} começa em {pt_date(starts)} e não cobre {window_text}, "
                    "o período fixo desta tela; use 1d aqui ou o Combo, que tem período",
                    "coverage",
                )

    # ---- roda: o que falta guardar
    needs: list[dict[str, str]] = []
    kinds: list[str] = []
    notes: list[str] = []
    for label, role in _series_for(timeframe, equity, deep):
        entry = coverage.get(label)
        kind = _series_need(
            entry,
            window_start=window_start,
            window_end=window_end,
            now=now,
            equity=equity,
            binance_horizon=horizon if (equity and label == "5m") else None,
        )
        if kind == COLLECT_BINANCE_NONE:
            if role == "intraday":
                notes.append(
                    f"O {label} de {symbol} não entra: a Binance não tem {label} dele em "
                    f"{_window_months(window_start, window_end)}."
                )
        elif kind != COLLECT_NONE:
            needs.append({"series": label, "role": role, "kind": kind})
            kinds.append(kind)
    chart_entry = coverage.get(_series_for(timeframe, equity, deep)[0][0])
    item["covered_until"] = chart_entry.get("to") if chart_entry else None
    item["needs_collection"] = needs
    item["collect_note"] = " ".join(notes) or None
    item["collect_kind"] = (
        COLLECT_MISSING if COLLECT_MISSING in kinds else COLLECT_TAIL if kinds else COLLECT_NONE
    )
    return item


def _totals(items: list[dict[str, Any]]) -> dict[str, Any]:
    run = [i for i in items if i["plan"] == PLAN_RUN]
    by_class: dict[str, dict[str, Any]] = {}
    for item in items:
        key = item["asset_class"] or "stock_etf"
        bucket = by_class.setdefault(key, {"run": 0, "out": 0, "currency": item["currency"]})
        bucket["run" if item["plan"] == PLAN_RUN else "out"] += 1
    needing = [i for i in run if i["collect_kind"] != COLLECT_NONE]
    return {
        "total": len(items),
        "run": len(run),
        "out": len(items) - len(run),
        "by_class": by_class,
        "collect": {
            "count": len(needing),
            "of": len(run),
            "missing": sum(1 for i in needing if i["collect_kind"] == COLLECT_MISSING),
            "tail": sum(1 for i in needing if i["collect_kind"] == COLLECT_TAIL),
        },
    }


def nothing_runs_detail(plan: dict[str, Any]) -> dict[str, Any]:
    """Detalhe do 422 quando nada roda: o motivo de cada ativo."""

    assets = [
        {
            "symbol": i["symbol"],
            "asset_id": i.get("asset_id"),
            "asset_class": i["asset_class"],
            "reason": i["reason"],
            "kind": i.get("out_kind"),
        }
        for i in plan["items"]
    ]
    names = "; ".join(f"{a['symbol']} ({a['reason']})" for a in assets[:5])
    rest = len(assets) - 5
    if rest > 0:
        names += f"; e mais {rest}"
    return {
        "code": "batch_nothing_to_run",
        "message": f"Nada será executado. Fora do lote: {names}.",
        "assets": assets,
    }


__all__ = [
    "COLLECT_MISSING",
    "COLLECT_NONE",
    "COLLECT_TAIL",
    "PLAN_OUT",
    "PLAN_RUN",
    "build_plan",
    "dedupe",
    "nothing_runs_detail",
]
