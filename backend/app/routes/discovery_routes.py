"""Discovery sweep routes (card #469).

Admin-only: preflight, criação idempotente, lifecycle, leaderboard e promoção
tier 3. `403` é reservado a autorização negada; `409` a idempotência/duplicidade.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_admin
from app.services.discovery_service import DiscoveryService

router = APIRouter(prefix="/api/combos/discovery", tags=["discovery"])


class PreflightRequest(BaseModel):
    templates: list[str] = Field(min_length=1)
    symbols: list[str] = Field(min_length=1)
    timeframes: list[str] = Field(min_length=1)
    directions: list[str] = Field(min_length=1)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period_type: Optional[str] = None


class CreateSweepRequest(BaseModel):
    templates: list[str]
    symbols: list[str]
    timeframes: list[str]
    directions: list[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period_type: Optional[str] = None
    snapshot_token: str
    snapshot_hash: str
    idempotency_key: str = Field(min_length=8, max_length=64)


class PromoteRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=64)
    tier: int = 3


def _service() -> DiscoveryService:
    return DiscoveryService()


@router.post("/sweeps/preflight")
def discovery_preflight(
    req: PreflightRequest,
    actor: str = Depends(get_current_admin),
):
    service = _service()
    return service.preflight(
        templates=req.templates,
        symbols=req.symbols,
        timeframes=req.timeframes,
        directions=req.directions,
        start_date=req.start_date,
        end_date=req.end_date,
        period_type=req.period_type,
    )


@router.post("/sweeps", status_code=201)
def create_discovery_sweep(
    req: CreateSweepRequest,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = _service()
    payload = req.model_dump(exclude={"snapshot_token", "snapshot_hash", "idempotency_key"})
    payload["snapshot_hash"] = req.snapshot_hash
    body, status = service.create_sweep(
        actor=actor,
        idempotency_key=req.idempotency_key,
        snapshot_token=req.snapshot_token,
        payload=payload,
        db=db,
    )
    if status >= 400:
        raise HTTPException(status_code=status, detail=body)
    if status == 200:
        return JSONResponse(status_code=200, content=body)
    return body


@router.get("/sweeps/active")
def discovery_sweeps_active(
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = _service()
    return {"sweeps": service.list_active_sweeps(actor, db)}


@router.get("/sweeps/history")
def discovery_sweeps_history(
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = _service()
    return {"sweeps": service.list_history(actor, db)}


@router.get("/sweeps/{sweep_id}")
def get_discovery_sweep(
    sweep_id: str,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = _service()
    sweep = service.get_sweep(sweep_id, db, actor=actor)
    if not sweep:
        raise HTTPException(status_code=404, detail="sweep not found")
    return sweep


@router.post("/sweeps/{sweep_id}/pause")
def pause_discovery_sweep(
    sweep_id: str,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return _command(sweep_id, "pause", actor, db)


@router.post("/sweeps/{sweep_id}/resume")
def resume_discovery_sweep(
    sweep_id: str,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return _command(sweep_id, "resume", actor, db)


@router.post("/sweeps/{sweep_id}/cancel")
def cancel_discovery_sweep(
    sweep_id: str,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return _command(sweep_id, "cancel", actor, db)


def _command(sweep_id: str, command: str, actor: str, db: Session) -> dict[str, Any]:
    service = _service()
    body, status = service.command(sweep_id, command, db, actor=actor)
    if status >= 400:
        raise HTTPException(status_code=status, detail=body)
    return body


@router.get("/sweeps/{sweep_id}/leaderboard")
def discovery_leaderboard(
    sweep_id: str,
    metric: str = "calmar_ratio",
    symbol: str | None = None,
    timeframe: str | None = None,
    direction: str | None = None,
    eligibility: str | None = None,
    offset: int = 0,
    limit: int | None = None,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = _service()
    sweep = service.get_sweep(sweep_id, db, actor=actor)
    if not sweep:
        raise HTTPException(status_code=404, detail="sweep not found")
    if metric not in ("calmar_ratio", "delta_cagr_vs_bh"):
        raise HTTPException(
            status_code=400, detail="metric must be calmar_ratio or delta_cagr_vs_bh"
        )
    if offset is None or offset < 0:
        offset = 0
    if limit is None:
        limit = 50
    limit = max(1, min(limit, 200))
    results, total, unfiltered_total = service.leaderboard(
        sweep_id,
        metric=metric,
        symbol=symbol,
        timeframe=timeframe,
        direction=direction,
        eligibility=eligibility,
        offset=offset,
        limit=limit,
        db=db,
    )
    return {
        "sweep_id": sweep_id,
        "metric": metric,
        "results": results,
        "total": total,
        "unfiltered_total": unfiltered_total,
        "offset": offset,
        "limit": limit,
    }


@router.post("/results/{result_id}/promote", status_code=201)
def promote_discovery_result(
    result_id: str,
    req: PromoteRequest,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = _service()
    payload = {"tier": req.tier, "result_id": result_id}
    body, status = service.promote_result(
        result_id=result_id,
        actor=actor,
        idempotency_key=req.idempotency_key,
        payload=payload,
        db=db,
    )
    if status >= 400:
        raise HTTPException(status_code=status, detail=body)
    if status == 200:
        return JSONResponse(status_code=200, content=body)
    return body
