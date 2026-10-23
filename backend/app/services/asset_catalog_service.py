"""Catálogo persistido de ativos Binance (card #1117).

Reúne:

* a atualização por grupo (``crypto`` e ``equity``) com reconciliação, guarda de
  queda brusca e falha que preserva a última lista válida;
* o backfill de removidos e o resumo de histórico;
* a consulta paginada com pesquisa sem caixa nem acento, o ``resolve`` do
  "Todos do filtro" e a validação de ativos para as análises novas.
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterable

from sqlalchemy import case, func, or_, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models_asset_catalog import AssetCatalog, AssetCatalogRefresh
from app.services.asset_catalog_adapters import (
    ASSET_CLASSES,
    CATALOG_GROUPS,
    CLASS_CRYPTO,
    CLASS_ETF,
    CLASS_STOCK,
    FETCHERS,
    GROUP_CRYPTO,
    GROUP_EQUITY,
    STATE_REMOVED,
    STATE_TRADABLE,
    CatalogSourceError,
    ParsedCatalog,
    build_search_key,
    crypto_asset_id,
    normalize_search_text,
)

logger = logging.getLogger(__name__)

CLASS_GROUP = {CLASS_CRYPTO: GROUP_CRYPTO, CLASS_STOCK: GROUP_EQUITY, CLASS_ETF: GROUP_EQUITY}
GROUP_CLASSES = {
    GROUP_CRYPTO: (CLASS_CRYPTO,),
    GROUP_EQUITY: (CLASS_STOCK, CLASS_ETF),
}
CLASS_ORDER = {CLASS_CRYPTO: 0, CLASS_STOCK: 1, CLASS_ETF: 2}

FRESH_OK = "ok"
FRESH_STALE = "stale"
FRESH_UNAVAILABLE = "unavailable"

DEFAULT_PAGE_SIZE = 6
MAX_PAGE_SIZE = 100

REFRESH_INTERVAL_SECONDS = int(os.getenv("ASSET_CATALOG_REFRESH_INTERVAL_SECONDS", "21600"))
MIN_RESULT_RATIO = float(os.getenv("ASSET_CATALOG_MIN_RESULT_RATIO", "0.5"))
RETRY_THROTTLE_SECONDS = 60
HISTORY_TIMEFRAME = "1d"
MARKET_OHLCV_TABLE = "market_ohlcv"

EQUITY_UNSUPPORTED_MESSAGE = (
    "Análise ainda não disponível para ações e ETFs. " "Escolha pares cripto negociáveis em USDT."
)

_ADVISORY_KEY = 11170001
_REFRESH_LOCKS = {group: threading.Lock() for group in CATALOG_GROUPS}


def refresh_enabled() -> bool:
    if "PYTEST_CURRENT_TEST" in os.environ:
        return False
    return os.getenv("ASSET_CATALOG_REFRESH_ENABLED", "1").strip().lower() not in {
        "",
        "0",
        "false",
        "no",
        "off",
    }


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _iso(value: datetime | None) -> str | None:
    value = _aware(value)
    return value.astimezone(timezone.utc).isoformat() if value else None


def _session() -> Session:
    from app.database import SessionLocal

    return SessionLocal()


# --- Atualização ---------------------------------------------------------------


def _previous_live_count(db: Session, group: str) -> int:
    return int(
        db.execute(
            select(func.count())
            .select_from(AssetCatalog)
            .where(
                AssetCatalog.asset_class.in_(GROUP_CLASSES[group]),
                AssetCatalog.state != STATE_REMOVED,
            )
        ).scalar()
        or 0
    )


def _guard_result(db: Session, group: str, parsed: ParsedCatalog) -> None:
    """Falha de queda brusca ou lista vazia: nunca troca por lista menor ou vazia."""
    if not parsed.records:
        raise CatalogSourceError("empty", "A Binance devolveu uma lista vazia.")
    has_valid_before = (
        db.execute(
            select(AssetCatalogRefresh.id)
            .where(AssetCatalogRefresh.catalog_group == group, AssetCatalogRefresh.status == "ok")
            .limit(1)
        ).first()
        is not None
    )
    if not has_valid_before:
        return
    previous = _previous_live_count(db, group)
    if previous and len(parsed.records) < previous * MIN_RESULT_RATIO:
        raise CatalogSourceError(
            "sharp_drop",
            f"A lista caiu de {previous} para {len(parsed.records)} ativos; "
            "a lista anterior foi mantida.",
        )


def _apply_record(row: AssetCatalog, record, now: datetime) -> None:
    row.asset_class = record.asset_class
    row.symbol = record.symbol
    row.name = record.name
    row.binance_id = record.binance_id
    row.state = record.state
    row.state_reason = record.state_reason
    row.info_note = record.info_note
    row.search_key = build_search_key(record.symbol, record.name)
    row.extra = record.extra or None
    row.last_seen_at = now
    row.removed_at = None


def reconcile_group(
    db: Session, group: str, parsed: ParsedCatalog, now: datetime
) -> dict[str, int]:
    """Aplica a lista validada: upsert, ausentes viram Removido, removidos voltam."""
    classes = GROUP_CLASSES[group]
    existing = {
        row.asset_id: row
        for row in db.execute(select(AssetCatalog).where(AssetCatalog.asset_class.in_(classes)))
        .scalars()
        .all()
    }
    added = updated = reappeared = 0
    seen: set[str] = set()
    for record in parsed.records:
        seen.add(record.asset_id)
        row = existing.get(record.asset_id)
        if row is None:
            row = AssetCatalog(asset_id=record.asset_id, first_seen_at=now, last_seen_at=now)
            _apply_record(row, record, now)
            row.history_from = row.history_to = row.history_checked_at = None
            db.add(row)
            added += 1
            continue
        if row.state == STATE_REMOVED:
            reappeared += 1
        _apply_record(row, record, now)
        updated += 1

    removed_now = 0
    removed_date = now.astimezone(timezone.utc).strftime("%d/%m/%Y")
    for asset_id, row in existing.items():
        if asset_id in seen or row.state == STATE_REMOVED:
            continue
        row.state = STATE_REMOVED
        row.removed_at = now
        row.state_reason = f"Deixou de constar no catálogo da Binance em {removed_date}."
        removed_now += 1
    return {
        "added": added,
        "updated": updated,
        "removed_now": removed_now,
        "reappeared": reappeared,
    }


def backfill_removed(db: Session, now: datetime) -> int:
    """Favoritos e resultados com símbolo ``/USDT`` fora do catálogo entram como Removido."""
    symbols: set[str] = set()
    for table, column in (
        ("favorite_strategies", "symbol"),
        ("discovery_results", "symbol"),
        ("backtest_runs", "symbol"),
    ):
        try:
            with db.begin_nested():
                rows = db.execute(
                    text(f"SELECT DISTINCT {column} FROM {table} WHERE {column} LIKE '%/%'")
                ).all()
        except SQLAlchemyError:
            logger.info("Backfill de removidos: tabela %s indisponível", table)
            continue
        for (value,) in rows:
            symbol = str(value or "").strip().upper()
            if "/" in symbol and symbol.endswith("/USDT"):
                symbols.add(symbol)
    if not symbols:
        return 0
    known = {
        row[0]
        for row in db.execute(
            select(AssetCatalog.symbol).where(
                AssetCatalog.asset_class == CLASS_CRYPTO, AssetCatalog.symbol.in_(symbols)
            )
        ).all()
    }
    added = 0
    for symbol in sorted(symbols - known):
        base = symbol.split("/", 1)[0]
        db.add(
            AssetCatalog(
                asset_id=crypto_asset_id(symbol),
                asset_class=CLASS_CRYPTO,
                symbol=symbol,
                name=base,
                binance_id=symbol.replace("/", ""),
                state=STATE_REMOVED,
                state_reason=(
                    "Não consta na lista spot USDT atual da Binance; "
                    "mantido para explicar favoritos e resultados antigos."
                ),
                search_key=build_search_key(symbol, base),
                first_seen_at=now,
                last_seen_at=now,
                removed_at=now,
                extra={"source": "backfill"},
            )
        )
        added += 1
    return added


def update_history_summary(db: Session, now: datetime) -> int:
    """Resumo de histórico local dos cripto a partir de ``market_ohlcv`` (1d)."""
    try:
        with db.begin_nested():
            rows = db.execute(
                text(
                    f"SELECT symbol, MIN(candle_time), MAX(candle_time) FROM {MARKET_OHLCV_TABLE} "
                    "WHERE timeframe = :tf GROUP BY symbol"
                ),
                {"tf": HISTORY_TIMEFRAME},
            ).all()
    except SQLAlchemyError:
        logger.info("Resumo de histórico indisponível: market_ohlcv não respondeu")
        return 0
    summary = {str(symbol).upper(): (first, last) for symbol, first, last in rows}
    updated = 0
    for row in db.execute(
        select(AssetCatalog).where(AssetCatalog.asset_class == CLASS_CRYPTO)
    ).scalars():
        first, last = summary.get(row.symbol, (None, None))
        row.history_from = first
        row.history_to = last
        row.history_checked_at = now
        if first is not None:
            updated += 1
    return updated


def _record_refresh(
    group: str,
    trigger: str,
    started: datetime,
    status: str,
    counts: dict[str, Any] | None = None,
    error: CatalogSourceError | None = None,
) -> AssetCatalogRefresh:
    row = AssetCatalogRefresh(
        catalog_group=group,
        trigger=trigger,
        started_at=started,
        finished_at=_now(),
        status=status,
        error_code=error.code if error else None,
        error_message=error.message if error else None,
        counts=counts,
    )
    return row


def refresh_group(
    group: str,
    *,
    trigger: str = "scheduled",
    fetcher: Callable[[], ParsedCatalog] | None = None,
    session_factory: Callable[[], Session] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Atualiza um grupo. Em falha, não toca nas linhas do catálogo e grava o erro."""
    if group not in CATALOG_GROUPS:
        raise ValueError(f"Grupo de catálogo desconhecido: {group}")
    fetch = fetcher or FETCHERS[group]
    factory = session_factory or _session
    started = now or _now()
    lock = _REFRESH_LOCKS[group]
    if not lock.acquire(blocking=False):
        return {"group": group, "status": "skipped", "reason": "in_progress"}
    try:
        try:
            parsed = fetch()
        except CatalogSourceError as exc:
            return _fail(factory, group, trigger, started, exc)
        except Exception as exc:  # defensivo: nenhuma falha esvazia o catálogo
            logger.exception("Atualização do catálogo (%s) falhou", group)
            return _fail(
                factory,
                group,
                trigger,
                started,
                CatalogSourceError("unexpected", f"Falha inesperada: {exc.__class__.__name__}."),
            )

        db = factory()
        try:
            try:
                db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": _ADVISORY_KEY})
                _guard_result(db, group, parsed)
                stats = reconcile_group(db, group, parsed, started)
                counts = parsed.to_counts()
                counts["changes"] = stats
                if group == GROUP_CRYPTO:
                    counts["backfilled_removed"] = backfill_removed(db, started)
                    counts["with_local_history"] = update_history_summary(db, started)
                db.add(_record_refresh(group, trigger, started, "ok", counts=counts))
                db.commit()
            except CatalogSourceError as exc:
                db.rollback()
                db.close()
                return _fail(factory, group, trigger, started, exc)
            except SQLAlchemyError as exc:
                db.rollback()
                db.close()
                logger.exception("Gravação do catálogo (%s) falhou", group)
                return _fail(
                    factory,
                    group,
                    trigger,
                    started,
                    CatalogSourceError(
                        "storage", f"Falha ao gravar o catálogo: {exc.__class__.__name__}."
                    ),
                )
        finally:
            db.close()
        return {"group": group, "status": "ok", "counts": counts}
    finally:
        lock.release()


def _fail(
    factory: Callable[[], Session],
    group: str,
    trigger: str,
    started: datetime,
    error: CatalogSourceError,
) -> dict[str, Any]:
    logger.warning("Catálogo %s: atualização falhou (%s): %s", group, error.code, error.message)
    db = factory()
    try:
        db.add(_record_refresh(group, trigger, started, "error", error=error))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Não foi possível gravar a falha de atualização do catálogo (%s)", group)
    finally:
        db.close()
    return {
        "group": group,
        "status": "error",
        "error_code": error.code,
        "error_message": error.message,
    }


def refresh_all(*, trigger: str = "scheduled", **kwargs: Any) -> list[dict[str, Any]]:
    return [refresh_group(group, trigger=trigger, **kwargs) for group in CATALOG_GROUPS]


# --- Frescor ---------------------------------------------------------------------


def freshness_by_group(db: Session) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for group in CATALOG_GROUPS:
        last_ok = db.execute(
            select(AssetCatalogRefresh)
            .where(AssetCatalogRefresh.catalog_group == group, AssetCatalogRefresh.status == "ok")
            .order_by(AssetCatalogRefresh.started_at.desc(), AssetCatalogRefresh.id.desc())
            .limit(1)
        ).scalar()
        last_any = db.execute(
            select(AssetCatalogRefresh)
            .where(AssetCatalogRefresh.catalog_group == group)
            .order_by(AssetCatalogRefresh.started_at.desc(), AssetCatalogRefresh.id.desc())
            .limit(1)
        ).scalar()
        info: dict[str, Any] = {
            "status": FRESH_UNAVAILABLE,
            "updated_at": None,
            "last_attempt_at": (
                _iso(last_any.finished_at or last_any.started_at) if last_any else None
            ),
            "reason": None,
            "code": None,
            "refreshing": _REFRESH_LOCKS[group].locked(),
        }
        if last_ok is not None:
            info["updated_at"] = _iso(last_ok.finished_at or last_ok.started_at)
            if last_any is not None and last_any.status == "error":
                info["status"] = FRESH_STALE
                info["reason"] = last_any.error_message
                info["code"] = last_any.error_code
            else:
                info["status"] = FRESH_OK
        elif last_any is not None:
            info["reason"] = last_any.error_message
            info["code"] = last_any.error_code
        result[group] = info
    return result


def freshness_by_class(db: Session) -> dict[str, dict[str, Any]]:
    groups = freshness_by_group(db)
    return {asset_class: dict(groups[CLASS_GROUP[asset_class]]) for asset_class in ASSET_CLASSES}


def kick_refresh_if_needed(db: Session) -> list[str]:
    """Atualização preguiçosa: dispara em segundo plano o grupo sem lista ou vencido."""
    if not refresh_enabled():
        return []
    started: list[str] = []
    now = _now()
    for group, info in freshness_by_group(db).items():
        if info["refreshing"]:
            continue
        last_attempt = info["last_attempt_at"]
        attempt = datetime.fromisoformat(last_attempt) if last_attempt else None
        updated = datetime.fromisoformat(info["updated_at"]) if info["updated_at"] else None
        throttled = attempt is not None and (now - attempt).total_seconds() < RETRY_THROTTLE_SECONDS
        if throttled:
            continue
        due = updated is None or (now - updated).total_seconds() > REFRESH_INTERVAL_SECONDS
        if not due:
            continue
        threading.Thread(
            target=refresh_group, args=(group,), kwargs={"trigger": "startup"}, daemon=True
        ).start()
        started.append(group)
    return started


def ensure_group_loaded(group: str, *, db: Session | None = None) -> bool:
    """Garante uma lista válida do grupo para a validação de análises (síncrono, no máximo 1x/min)."""
    own = db is None
    session = db or _session()
    try:
        info = freshness_by_group(session)[group]
        if info["status"] != FRESH_UNAVAILABLE:
            return True
        last = info["last_attempt_at"]
        if (
            last
            and (_now() - datetime.fromisoformat(last)).total_seconds() < RETRY_THROTTLE_SECONDS
        ):
            return False
    except SQLAlchemyError:
        return False
    finally:
        if own:
            session.close()
    if not refresh_enabled():
        return False
    refresh_group(group, trigger="startup")
    session = _session()
    try:
        return freshness_by_group(session)[group]["status"] != FRESH_UNAVAILABLE
    except SQLAlchemyError:
        return False
    finally:
        session.close()


def run_scheduler_loop(stop_event: threading.Event, interval_seconds: int | None = None) -> None:
    """Laço do agendamento por classe (cada grupo a cada ``REFRESH_INTERVAL_SECONDS``)."""
    interval = interval_seconds or REFRESH_INTERVAL_SECONDS
    while not stop_event.is_set():
        for group in CATALOG_GROUPS:
            try:
                db = _session()
                try:
                    info = freshness_by_group(db)[group]
                finally:
                    db.close()
                updated = datetime.fromisoformat(info["updated_at"]) if info["updated_at"] else None
                if updated is None or (_now() - updated).total_seconds() >= interval:
                    refresh_group(group, trigger="scheduled")
            except Exception:  # pragma: no cover - laço nunca morre
                logger.exception("Agendamento do catálogo (%s) falhou", group)
        stop_event.wait(min(interval, 900))


# --- Consulta ---------------------------------------------------------------------

STATE_LABELS = {
    "tradable": "Negociável",
    "suspended": "Suspenso",
    "off_market": "Fora de mercado",
    "no_trading": "Sem negociação",
    "no_rules": "Sem regras de negociação",
    "removed": "Removido",
}


def _empty_history(tradable: bool) -> dict[str, Any]:
    return {
        "status": "on_demand" if tradable else "none",
        "from": None,
        "to": None,
        "updated_at": None,
        "gap_count": 0,
        "timeframes": [],
        "note": None,
        "calendar_timezone": None,
        "collecting": None,
        "error": None,
        "partial": None,
    }


def serialize_item(
    row: AssetCatalog, history_coverage: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Item do catálogo. ``history_coverage`` vem de ``market_series_coverage`` (card #1118):
    cobertura por timeframe, lacunas, coleta e falha. Sem ela, cripto cai no resumo
    de 1d do #1117 e as demais classes ficam "sob demanda" (nunca "não coletado")."""

    tradable = row.state == STATE_TRADABLE
    if history_coverage is not None:
        history = history_coverage
    elif row.asset_class == CLASS_CRYPTO and row.history_from is not None:
        history = _empty_history(tradable)
        history.update(
            {
                "status": "covered" if tradable else "frozen",
                "from": _iso(row.history_from),
                "to": _iso(row.history_to),
                "updated_at": _iso(row.history_checked_at),
                "gap_count": None,  # lacunas desconhecidas até a série entrar na autoridade nova
                "timeframes": [
                    {
                        "timeframe": "1d",
                        "from": _iso(row.history_from),
                        "to": _iso(row.history_to),
                        "gap_count": None,
                        "gaps": [],
                        "updated_at": _iso(row.history_checked_at),
                        "origin": "native",
                        "derived_from": None,
                        "state": "idle",
                        "insufficient": False,
                        "incomplete": False,
                    }
                ],
                "note": "Binance Spot · 24/7 · ajuste não se aplica",
            }
        )
    else:
        history = _empty_history(tradable)
    return {
        "asset_id": row.asset_id,
        "asset_class": row.asset_class,
        "symbol": row.symbol,
        "name": row.name,
        "state": row.state,
        "state_label": STATE_LABELS.get(row.state, row.state),
        "state_reason": row.state_reason,
        "info_note": row.info_note,
        "removed_at": _iso(row.removed_at),
        "selectable": tradable,
        "analysis_available": row.asset_class == CLASS_CRYPTO,
        "history": history,
    }


def _serialize_rows(db: Session, rows: list[AssetCatalog]) -> list[dict[str, Any]]:
    """Serializa a página com a cobertura do histórico lida de uma vez (sem varrer candles)."""

    from app.services.market_history.catalog_coverage import coverage_for_assets

    coverage = coverage_for_assets(db, rows)
    return [serialize_item(row, coverage.get(row.asset_id)) for row in rows]


def _available_classes(freshness: dict[str, dict[str, Any]]) -> list[str]:
    return [c for c in ASSET_CLASSES if freshness[c]["status"] != FRESH_UNAVAILABLE]


def _filter_clauses(q: str, asset_class: str | None, classes: list[str]):
    clauses = [AssetCatalog.asset_class.in_(classes)]
    if asset_class and asset_class != "all":
        clauses.append(AssetCatalog.asset_class == asset_class)
    norm = normalize_search_text(q)
    if norm:
        clauses.append(AssetCatalog.search_key.contains(norm, autoescape=True))
    return clauses, norm


def _order_by(norm: str):
    class_rank = case(
        (AssetCatalog.asset_class == CLASS_CRYPTO, 0),
        (AssetCatalog.asset_class == CLASS_STOCK, 1),
        else_=2,
    )
    if not norm:
        return [class_rank, AssetCatalog.symbol]
    symbol_lower = func.lower(AssetCatalog.symbol)
    base_lower = func.lower(func.split_part(AssetCatalog.symbol, "/", 1))
    rank = case(
        (or_(symbol_lower == norm, base_lower == norm), 0),
        (symbol_lower.startswith(norm, autoescape=True), 1),
        (symbol_lower.contains(norm, autoescape=True), 2),
        else_=3,
    )
    return [rank, class_rank, AssetCatalog.symbol]


def class_counts(db: Session, classes: list[str]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {
        "all": {"total": 0, "eligible": 0},
        **{c: {"total": 0, "eligible": 0} for c in ASSET_CLASSES},
    }
    if classes:
        rows = db.execute(
            select(
                AssetCatalog.asset_class,
                func.count(),
                func.sum(case((AssetCatalog.state == STATE_TRADABLE, 1), else_=0)),
            )
            .where(AssetCatalog.asset_class.in_(classes))
            .group_by(AssetCatalog.asset_class)
        ).all()
        for asset_class, total, eligible in rows:
            counts[asset_class] = {"total": int(total), "eligible": int(eligible or 0)}
            counts["all"]["total"] += int(total)
            counts["all"]["eligible"] += int(eligible or 0)
    return counts


def search_catalog(
    db: Session,
    *,
    q: str = "",
    asset_class: str | None = None,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict[str, Any]:
    page = max(1, int(page))
    page_size = max(1, min(int(page_size), MAX_PAGE_SIZE))
    freshness = freshness_by_class(db)
    classes = _available_classes(freshness)
    clauses, norm = _filter_clauses(q, asset_class, classes)

    total = int(
        db.execute(select(func.count()).select_from(AssetCatalog).where(*clauses)).scalar() or 0
    )
    eligible = int(
        db.execute(
            select(func.count())
            .select_from(AssetCatalog)
            .where(*clauses, AssetCatalog.state == STATE_TRADABLE)
        ).scalar()
        or 0
    )
    rows = (
        db.execute(
            select(AssetCatalog)
            .where(*clauses)
            .order_by(*_order_by(norm))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    counts = class_counts(db, classes)
    for asset_class_name in ASSET_CLASSES:
        if freshness[asset_class_name]["status"] == FRESH_UNAVAILABLE:
            counts[asset_class_name] = {"total": None, "eligible": None}
    return {
        "items": _serialize_rows(db, rows),
        "q": q,
        "class": asset_class or "all",
        "page": page,
        "page_size": page_size,
        "pages": max(1, -(-total // page_size)),
        "total": total,
        "eligible_total": eligible,
        "marked_total": total - eligible,
        "counts": counts,
        "freshness": freshness,
    }


def resolve_filter(db: Session, *, q: str = "", asset_class: str | None = None) -> dict[str, Any]:
    """Ids negociáveis do filtro atual (para o "Todos do filtro")."""
    freshness = freshness_by_class(db)
    classes = _available_classes(freshness)
    clauses, norm = _filter_clauses(q, asset_class, classes)
    rows = (
        db.execute(
            select(AssetCatalog)
            .where(*clauses, AssetCatalog.state == STATE_TRADABLE)
            .order_by(*_order_by(norm))
        )
        .scalars()
        .all()
    )
    total = int(
        db.execute(select(func.count()).select_from(AssetCatalog).where(*clauses)).scalar() or 0
    )
    return {
        "asset_ids": [row.asset_id for row in rows],
        "items": [
            {
                "asset_id": row.asset_id,
                "symbol": row.symbol,
                "asset_class": row.asset_class,
                "name": row.name,
            }
            for row in rows
        ],
        "eligible_total": len(rows),
        "marked_total": total - len(rows),
        "total": total,
    }


def lookup_assets(
    db: Session,
    *,
    asset_ids: Iterable[str] = (),
    symbols: Iterable[str] = (),
) -> list[dict[str, Any]]:
    """Reidrata ids ou símbolos (rascunho, snapshot, favorito, ``?symbol=``)."""
    ids = [str(i).strip() for i in asset_ids if str(i or "").strip()]
    syms = [str(s).strip().upper() for s in symbols if str(s or "").strip()]
    if not ids and not syms:
        return []
    conditions = []
    if ids:
        conditions.append(AssetCatalog.asset_id.in_(ids))
    if syms:
        conditions.append(AssetCatalog.symbol.in_(syms))
    rows = db.execute(select(AssetCatalog).where(or_(*conditions))).scalars().all()
    return _serialize_rows(db, rows)


def list_tradable_crypto_symbols(*, db: Session | None = None) -> list[str] | None:
    """Símbolos cripto negociáveis do catálogo, ou None sem lista válida de cripto."""
    own = db is None
    session = db or _session()
    try:
        if freshness_by_group(session)[GROUP_CRYPTO]["status"] == FRESH_UNAVAILABLE:
            if not ensure_group_loaded(GROUP_CRYPTO, db=session):
                return None
            session.expire_all()
        rows = session.execute(
            select(AssetCatalog.symbol)
            .where(AssetCatalog.asset_class == CLASS_CRYPTO, AssetCatalog.state == STATE_TRADABLE)
            .order_by(AssetCatalog.symbol)
        ).all()
        return [row[0] for row in rows]
    except SQLAlchemyError:
        logger.exception("Catálogo indisponível ao listar cripto negociáveis")
        return None
    finally:
        if own:
            session.close()


# --- Validação das análises novas ----------------------------------------------------


@dataclass
class AssetCheck:
    symbol: str
    found: bool
    asset_class: str | None = None
    asset_id: str | None = None
    state: str | None = None
    state_reason: str | None = None
    catalog_unavailable: bool = False

    @property
    def selectable(self) -> bool:
        return self.found and self.state == STATE_TRADABLE


def check_assets(symbols: Iterable[str], *, db: Session | None = None) -> list[AssetCheck]:
    """Classifica símbolos pelo catálogo. Cripto = símbolo com ``/``; ação e ETF = ticker."""
    normalized = [str(s or "").strip().upper() for s in symbols]
    own = db is None
    session = db or _session()
    try:
        freshness = freshness_by_group(session)
        crypto_ready = freshness[GROUP_CRYPTO]["status"] != FRESH_UNAVAILABLE
        equity_ready = freshness[GROUP_EQUITY]["status"] != FRESH_UNAVAILABLE
        if (
            not crypto_ready
            and any("/" in s for s in normalized)
            and ensure_group_loaded(GROUP_CRYPTO, db=session)
        ):
            crypto_ready = True
        rows = (
            session.execute(select(AssetCatalog).where(AssetCatalog.symbol.in_(set(normalized))))
            .scalars()
            .all()
        )
        by_symbol: dict[str, AssetCatalog] = {}
        for row in rows:
            by_symbol.setdefault(row.symbol, row)
    finally:
        if own:
            session.close()

    result: list[AssetCheck] = []
    for symbol in normalized:
        row = by_symbol.get(symbol)
        is_crypto = "/" in symbol
        group_ready = crypto_ready if is_crypto else equity_ready
        if row is not None and (row.asset_class == CLASS_CRYPTO) == is_crypto:
            result.append(
                AssetCheck(
                    symbol=symbol,
                    found=True,
                    asset_class=row.asset_class,
                    asset_id=row.asset_id,
                    state=row.state,
                    state_reason=row.state_reason,
                )
            )
        else:
            result.append(
                AssetCheck(symbol=symbol, found=False, catalog_unavailable=not group_ready)
            )
    return result


def catalog_symbol_reason(check: AssetCheck) -> str:
    """Motivo curto, em português, de um ativo que não entra em análise nova."""
    if check.found and check.asset_class in (CLASS_STOCK, CLASS_ETF):
        return "análise ainda não disponível para ações e ETFs"
    if check.found:
        label = STATE_LABELS.get(check.state or "", check.state or "")
        reason = (check.state_reason or "").rstrip(".")
        return f"{label}: {reason}" if reason else label
    return "ativo fora do catálogo da Binance"


def serialize_check(check: AssetCheck) -> dict[str, Any]:
    return {
        "symbol": check.symbol,
        "asset_id": check.asset_id,
        "asset_class": check.asset_class,
        "state": check.state,
        "state_label": STATE_LABELS.get(check.state or "", check.state),
        "reason": check.state_reason,
    }
