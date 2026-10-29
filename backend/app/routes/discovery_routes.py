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
    # Card #1122 (d2): a promoção cria o favorito sem estrela; um pedido com ``tier`` (qualquer
    # valor) é recusado com 422 "promoção sem estrela" e nada muda.
    tier: Optional[int] = None


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
    sweep = service.get_sweep(sweep_id, db, actor=actor, with_assets=True)
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
    exclude_eligibility: str | None = None,
    asset_class: str | None = None,
    offset: int = 0,
    limit: int | None = None,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = _service()
    if asset_class is not None and asset_class not in ("crypto", "stock", "etf"):
        raise HTTPException(status_code=400, detail="asset_class must be crypto, stock or etf")
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
    class_counts: dict[str, int] = {}
    results, total, unfiltered_total = service.leaderboard(
        sweep_id,
        metric=metric,
        symbol=symbol,
        timeframe=timeframe,
        direction=direction,
        eligibility=eligibility,
        exclude_eligibility=exclude_eligibility,
        asset_class=asset_class,
        offset=offset,
        limit=limit,
        db=db,
        counts=class_counts,
    )
    # Card #1123 (decisão 10): coluna extra lida por junção; não mexe na ordem nem no rank.
    from app.services import discovery_reference_column as refcol

    try:
        reference_column = refcol.attach_to_leaderboard(db, sweep_id, actor, results)
    except Exception:
        reference_column = None
    return {
        "sweep_id": sweep_id,
        "metric": metric,
        "results": results,
        "total": total,
        "unfiltered_total": unfiltered_total,
        "class_counts": class_counts,
        "offset": offset,
        "limit": limit,
        "reference_column": reference_column,
    }


LEADERBOARD_EXPORT_COLUMNS = (
    "Rank global",
    "Candidato",
    "Template",
    "Timeframe",
    "Direção",
    "Sharpe",
    "Trades",
    "Win%",
    "Return",
    "Max DD",
    "Calmar",
    "CAGR anualizado",
    "B&H CAGR",
    "Δ vs B&H",
    "Profit Factor",
    "GO/NO-GO",
    "Elegibilidade",
    "Motivo",
)


def _ratio_cell(value: Any):
    from app.services.export_context import pct

    return pct(value)


def _number_cell(value: Any, fmt: str = "0.00"):
    from app.services.export_context import Cell, empty

    try:
        number = float(value)
    except (TypeError, ValueError):
        return empty()
    if number != number or number in (float("inf"), float("-inf")):
        return empty()
    return Cell(number, "registrado", fmt)


def _leaderboard_today(row: dict[str, Any]) -> list[Any]:
    from app.services.export_context import empty, pp

    verdict = (
        (row.get("oos_verdict") or {}).get("status")
        if isinstance(row.get("oos_verdict"), dict)
        else None
    )
    total_return = row.get("total_return")
    if total_return is None and row.get("total_return_pct") is not None:
        total_return = float(row["total_return_pct"]) / 100.0
    delta = row.get("delta_cagr_vs_bh")
    return [
        row.get("rank") if row.get("rank") is not None else "—",
        f"{row.get('symbol')} · {row.get('timeframe')} · {str(row.get('direction') or '').capitalize()}",
        row.get("display_name") or row.get("template_id"),
        row.get("timeframe"),
        str(row.get("direction") or "").capitalize(),
        _number_cell(row.get("sharpe_ratio")),
        row.get("trades_count") if row.get("trades_count") is not None else empty(),
        _ratio_cell(row.get("win_rate")),
        _ratio_cell(total_return),
        _ratio_cell(row.get("max_drawdown")),
        _number_cell(row.get("calmar_ratio")),
        _ratio_cell(row.get("cagr")),
        _ratio_cell(row.get("benchmark_cagr")),
        # ``delta_cagr_vs_bh`` já é gravado em p.p. (``(cagr - benchmark_cagr) * 100``).
        pp(delta),
        _number_cell(row.get("profit_factor")),
        verdict or "",
        row.get("eligibility") or "",
        row.get("eligibility_reason") or "",
    ]


@router.get("/sweeps/{sweep_id}/leaderboard/export")
def export_discovery_leaderboard(
    sweep_id: str,
    metric: str = "calmar_ratio",
    symbol: str | None = None,
    timeframe: str | None = None,
    direction: str | None = None,
    asset_class: str | None = None,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Recorte filtrado inteiro (todas as páginas), na ordem e com o rank global do leaderboard.

    Colunas de hoje + os 22 campos de contexto (referência = próprio ativo) e, com a coluna extra
    ativa e concluída, as 13 colunas "(extra)" lidas das comparações gravadas. Sem recálculo.
    """

    import io

    from fastapi.responses import StreamingResponse

    from app.services import discovery_reference_column as refcol
    from app.services import export_context as xc

    service = _service()
    if asset_class is not None and asset_class not in ("crypto", "stock", "etf"):
        raise HTTPException(status_code=400, detail="asset_class must be crypto, stock or etf")
    sweep = service.get_sweep(sweep_id, db, actor=actor)
    if not sweep:
        raise HTTPException(status_code=404, detail="sweep not found")
    if metric not in ("calmar_ratio", "delta_cagr_vs_bh"):
        raise HTTPException(
            status_code=400, detail="metric must be calmar_ratio or delta_cagr_vs_bh"
        )
    results, _total, _unfiltered = service.leaderboard(
        sweep_id,
        metric=metric,
        symbol=symbol,
        timeframe=timeframe,
        direction=direction,
        asset_class=asset_class,
        offset=0,
        limit=None,
        db=db,
    )
    snapshot = sweep.get("snapshot") if isinstance(sweep.get("snapshot"), dict) else {}
    sweep_info = {
        "sweep_id": sweep_id,
        "start_date": snapshot.get("start_date") or sweep.get("start_date"),
        "end_date": snapshot.get("end_date") or sweep.get("end_date"),
        "completed_at": sweep.get("completed_at"),
    }
    column, cells = refcol.export_cells(db, sweep_id, actor)
    extra = column is not None and column.status == "done"
    header = list(LEADERBOARD_EXPORT_COLUMNS) + list(xc.CONTEXT_FIELDS)
    if extra:
        header += list(xc.EXTRA_FIELDS)
    body = []
    for row in results:
        line = _leaderboard_today(row) + xc.discovery_context(row, sweep_info)
        if extra:
            payload = cells.get(str(row.get("result_id")))
            if payload is None or row.get("eligibility") == "insufficient_sample":
                # Fora do cálculo: sem amostra (``insufficient_sample``) ou sem CAGR gravado. A
                # referência é a da coluna, não o próprio ativo.
                if row.get("eligibility") == "insufficient_sample":
                    situation = "Sem amostra: o candidato não tem métrica gravada."
                else:
                    situation = refcol.NO_CAGR_TEXT
                line += (
                    [
                        xc.Cell(
                            xc.reference_text(
                                {"reference": {**(column.reference or {}), "kind": "catalog"}}
                            )
                        )
                    ]
                    + [xc.empty()] * 8
                    + [xc.Cell(situation), xc.empty(), xc.empty(), xc.empty()]
                )
            else:
                line += xc.comparison_cells(payload, short_reason=True)
        body.append(line)
    content = xc.write_workbook(
        [("Ranking", header, body), xc.legend_sheet(ranking=True, extra=extra)]
    )
    filename = f"descoberta_{sweep_id}_ranking.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    headers["X-Export-Rows"] = str(len(body))
    if column is not None:
        headers["X-Export-Extra"] = "included" if extra else "computing"
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


class ReferenceColumnRequest(BaseModel):
    reference_symbol: Optional[str] = None


def _owned_sweep(sweep_id: str, actor: str, db: Session) -> dict[str, Any]:
    sweep = _service().get_sweep(sweep_id, db, actor=actor)
    if not sweep:
        raise HTTPException(status_code=404, detail="sweep not found")
    return sweep


@router.get("/sweeps/{sweep_id}/reference-column")
def get_reference_column(
    sweep_id: str,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    from app.services import discovery_reference_column as refcol

    _owned_sweep(sweep_id, actor, db)
    return refcol.state(db, sweep_id, actor)


@router.put("/sweeps/{sweep_id}/reference-column")
def put_reference_column(
    sweep_id: str,
    req: ReferenceColumnRequest,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """``null`` = Próprio ativo (sem coluna). Já gravada: reativa (200). Nova: 202 e job na fila."""

    from app.services import discovery_reference_column as refcol

    sweep = _owned_sweep(sweep_id, actor, db)
    from app.services.discovery_service import NON_TERMINAL_STATES

    if sweep.get("state") in NON_TERMINAL_STATES and req.reference_symbol:
        raise HTTPException(
            status_code=409,
            detail="A coluna extra é escolhida depois que a varredura termina.",
        )
    body, status = refcol.set_reference(db, sweep_id, actor, req.reference_symbol)
    if status >= 400:
        raise HTTPException(status_code=status, detail=body)
    return JSONResponse(status_code=status, content=body)


@router.post("/sweeps/{sweep_id}/reference-column/retry")
def retry_reference_column(
    sweep_id: str,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    from app.services import discovery_reference_column as refcol

    _owned_sweep(sweep_id, actor, db)
    body, status = refcol.retry(db, sweep_id, actor)
    if status >= 400:
        raise HTTPException(status_code=status, detail=body)
    return JSONResponse(status_code=status, content=body)


@router.post("/results/{result_id}/promote", status_code=201)
def promote_discovery_result(
    result_id: str,
    req: PromoteRequest,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = _service()
    payload: dict = {"result_id": result_id}
    if "tier" in req.model_fields_set:
        payload["tier"] = req.tier
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


@router.post("/results/{result_id}/discard")
def discard_discovery_result(
    result_id: str,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    del actor
    service = _service()
    body, status = service.discard_result(result_id=result_id, db=db)
    if status >= 400:
        raise HTTPException(status_code=status, detail=body)
    return body
