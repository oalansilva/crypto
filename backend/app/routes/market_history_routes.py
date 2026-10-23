"""``GET /api/market/history``: consulta de histórico para qualquer classe (card #1118).

É a "consulta" que coleta ação e ETF até o #1119 (decisão de Alan, 23/10/2026): as
análises recusam a classe antes de qualquer coleta, e catálogo, filtro e
"Todos do filtro" nunca chegam aqui. A resposta traz sempre período pedido,
período coberto, lacunas, atualização, versão e o estado da coleta; falha da
Binance vem como falha, nunca como lista vazia nem como período completo.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.services.market_history.facade import get_history_service, spec_for_request
from app.services.market_history.model import HistoryError, HistoryNotReady, SeriesNotSupported
from app.services.market_history.service import HistoryService

router = APIRouter(prefix="/api/market", tags=["market-history"])
logger = logging.getLogger(__name__)

# Mensagens para o usuário: o código cru da Binance (488006) nunca aparece (P3 aceito do Design).
_FAILURE_TEXT = {
    "binance_rate_limited": "limite de requisições da Binance",
    "binance_unavailable": "Binance indisponível",
    "binance_business_error": "a Binance recusou o pedido",
    "binance_format_changed": "formato da Binance mudou",
    "binance_circuit_open": "coleta em pausa por falhas seguidas da Binance",
    "internal_error": "erro interno na coleta",
}


def _candles_payload(frame) -> list[dict[str, Any]]:
    return [
        {
            "timestamp_utc": ts.isoformat(),
            "open": float(row.open),
            "high": float(row.high),
            "low": float(row.low),
            "close": float(row.close),
            "volume": float(row.volume or 0.0),
        }
        for ts, row in frame.iterrows()
    ]


def user_failure_text(code: str | None) -> str:
    return _FAILURE_TEXT.get(code or "", "falha na coleta")


@router.get("/history")
def get_market_history(
    timeframe: str = Query(
        "1d", description="1d, 5m ou 15m (montado do 5m) para ação e ETF; cripto: 1m a 1d"
    ),
    asset_id: Optional[str] = Query(
        None, description="Identidade do catálogo (binance:equity:EQ_NVDA)"
    ),
    symbol: Optional[str] = Query(None, description="Ticker (NVDA) ou par (BTC/USDT)"),
    adjustment: str = Query("adjusted", pattern="^(adjusted|raw)$"),
    start: Optional[str] = Query(None, description="Início do período (ISO 8601)"),
    end: Optional[str] = Query(None, description="Fim do período (ISO 8601)"),
    limit: int = Query(
        1000, ge=1, le=20000, description="Máximo de candles devolvidos (os mais recentes)"
    ),
    collect: bool = Query(
        True, alias="ensure", description="Coleta o trecho que falta antes de ler"
    ),
    budget_seconds: float = Query(20.0, ge=1.0, le=55.0, description="Tempo máximo desta coleta"),
    _user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    tf = str(timeframe or "").strip().lower()
    try:
        spec = spec_for_request(
            timeframe=tf, asset_id=asset_id, symbol=symbol, adjustment=adjustment, db=db
        )
        service: HistoryService = get_history_service()
        series = service.resolve(spec)
        result = service.history(
            series,
            start,
            end,
            limit=limit,
            ensure=collect,
            budget_seconds=budget_seconds,
        )
    except SeriesNotSupported as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)})
    except HistoryNotReady as exc:
        raise HTTPException(status_code=503, detail={"code": exc.code, "message": str(exc)})
    except HistoryError as exc:
        status = 404 if exc.code == "asset_not_in_catalog" else 400
        raise HTTPException(status_code=status, detail={"code": exc.code, "message": str(exc)})

    coverage = result.coverage
    outcome = result.ensure
    collection = None
    if outcome is not None:
        collection = {
            "status": outcome.status,
            "pages": outcome.pages,
            "candles_written": outcome.candles_written,
            "version_changed": outcome.version_changed,
        }
        if outcome.status == "failed":
            collection["error"] = {
                "code": outcome.error_code,
                "message": user_failure_text(outcome.error_code),
            }
    if coverage.get("error"):
        coverage["error"]["message"] = user_failure_text(coverage["error"].get("code"))
    return {
        "series": result.series.as_dict(),
        "timeframe": tf,
        "count": int(len(result.candles)),
        "candles": _candles_payload(result.candles),
        "coverage": coverage,
        "data_version": coverage["version_label"],
        "collection": collection,
    }
