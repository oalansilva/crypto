"""Revalidação walk-forward de favoritos (card #470).

Roda a regra walk-forward (split treino/holdout + gate GO/NO-GO) na janela
recente de favoritos existentes e atualiza os dados persistidos de revalidação
(`metrics.revalidation*`), sem alterar parâmetros nem `auto_refresh_status`.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import FavoriteStrategy
from app.services.combo_optimizer import ComboOptimizer
from app.services.favorite_backtest_refresh_service import _fixed_optimization_ranges
from app.services.market_data_providers import resolve_data_source_for_symbol

logger = logging.getLogger(__name__)

REVALIDATION_WINDOW_DAYS = 90


def oos_gate_decision(
    verdict: dict[str, Any] | None,
    *,
    override: bool = False,
    is_admin: bool = False,
) -> dict[str, Any]:
    """Decisão do gate walk-forward (card #470) para criação de favorito.

    Retorna {"allowed": bool, "reason": str | None}. Candidato NO-GO é bloqueado
    a menos que admin forneça override explícito; payload legado (sem veredito)
    mantém comportamento atual.
    """
    if not isinstance(verdict, dict):
        return {"allowed": True, "reason": None}
    status = str(verdict.get("status") or "").strip().upper()
    if not status or status == "GO":
        return {"allowed": True, "reason": None}
    if override and is_admin:
        return {"allowed": True, "reason": "override admin explícito"}
    reasons = verdict.get("reasons") or [f"veredito {status} no holdout"]
    reason_text = "; ".join(str(r) for r in reasons[:8])
    return {
        "allowed": False,
        "reason": (
            f"Candidato reprovado na validação walk-forward (holdout): {reason_text}. "
            "Use override de admin apenas com decisão explícita."
        ),
    }


def _favorite_direction(parameters: dict[str, Any]) -> str:
    direction = str(parameters.get("direction") or "long").lower()
    return direction if direction in ("long", "short") else "long"


def _revalidation_window(favorite: FavoriteStrategy) -> tuple[str, str]:
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=REVALIDATION_WINDOW_DAYS)).strftime("%Y-%m-%d")
    return start_date, end_date


def revalidate_favorite(
    favorite: FavoriteStrategy,
    *,
    db: Session | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Roda o backtest do favorito na janela recente com split walk-forward e
    grava `metrics.revalidation*` no favorito (sem alterar parâmetros)."""
    parameters = favorite.parameters if isinstance(favorite.parameters, dict) else {}
    direction = _favorite_direction(parameters)
    data_source = parameters.get("data_source") or resolve_data_source_for_symbol(
        favorite.symbol, None
    )
    window_start, window_end = _revalidation_window(favorite)
    start = start_date or window_start
    end = end_date or window_end

    optimizer = ComboOptimizer()
    result = optimizer.run_optimization(
        template_name=favorite.strategy_name,
        symbol=favorite.symbol,
        timeframe=favorite.timeframe,
        data_source=data_source,
        start_date=start,
        end_date=end,
        custom_ranges=_fixed_optimization_ranges(parameters),
        deep_backtest=True,
        direction=direction,
        split_train_ratio=0.7,
    )

    best_metrics = result.get("best_metrics") or {}
    oos_metrics = result.get("oos_metrics")
    oos_verdict = result.get("oos_verdict")

    revalidation: dict[str, Any] = {
        "window_start": start,
        "window_end": end,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "best_metrics": best_metrics,
        "oos_metrics": oos_metrics,
        "oos_verdict": oos_verdict,
    }
    verdict_status = str((oos_verdict or {}).get("status") or "").strip().upper()

    session = db or SessionLocal()
    try:
        row = session.query(FavoriteStrategy).filter(FavoriteStrategy.id == favorite.id).first()
        if row is None:
            raise ValueError(f"Favorite {favorite.id} not found")
        metrics = dict(row.metrics or {})
        metrics["revalidation"] = revalidation
        metrics["revalidation_verdict"] = verdict_status or "UNKNOWN"
        metrics["revalidation_at"] = datetime.utcnow().isoformat() + "Z"
        row.metrics = metrics
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        if db is None:
            session.close()

    return {
        "favorite_id": favorite.id,
        "symbol": favorite.symbol,
        "timeframe": favorite.timeframe,
        "strategy_name": favorite.strategy_name,
        "verdict": verdict_status,
        "oos_verdict": oos_verdict,
        "window": {"start": start, "end": end},
        "revalidation": revalidation,
    }


def revalidate_all_favorites(
    *,
    db: Session | None = None,
    max_favorites: int | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Backfill em massa: revalida todos os favoritos (e favoritos do curated
    catalog usados pelo Monitor) com a mesma regra walk-forward."""
    session = db or SessionLocal()
    try:
        query = session.query(FavoriteStrategy)
        if user_id:
            query = query.filter(FavoriteStrategy.user_id == user_id)
        rows = query.order_by(FavoriteStrategy.id.asc()).all()
    finally:
        if db is None:
            session.close()

    if max_favorites is not None:
        rows = rows[:max_favorites]

    summary = {
        "total": len(rows),
        "revalidated": 0,
        "failures": 0,
        "go": 0,
        "no_go": 0,
        "results": [],
    }
    for row in rows:
        # Session própria por favorito evita PendingRollbackError compartilhada
        # quando um commit falha no meio do lote.
        per_item_db = None
        if db is None:
            per_item_db = SessionLocal()
        try:
            result = revalidate_favorite(row, db=per_item_db)
            summary["revalidated"] += 1
            if result.get("verdict") == "GO":
                summary["go"] += 1
            elif result.get("verdict") == "NO-GO":
                summary["no_go"] += 1
            summary["results"].append(
                {
                    "favorite_id": row.id,
                    "symbol": row.symbol,
                    "verdict": result.get("verdict"),
                }
            )
        except Exception as exc:
            summary["failures"] += 1
            logger.warning("Revalidation failed for favorite %s: %s", row.id, exc)
            summary["results"].append(
                {"favorite_id": row.id, "symbol": row.symbol, "error": str(exc)[:300]}
            )
        finally:
            if per_item_db is not None:
                per_item_db.close()
    return summary
