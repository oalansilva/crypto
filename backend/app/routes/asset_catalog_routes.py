"""Rotas do catálogo de ativos Binance (card #1117)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_admin, get_current_user
from app.services import asset_catalog_service as catalog
from app.services.asset_catalog_adapters import ASSET_CLASSES, CATALOG_GROUPS

router = APIRouter(prefix="/api/assets", tags=["assets"])


class ResolveRequest(BaseModel):
    q: str = ""
    asset_class: Optional[str] = Field(default=None, alias="class")

    model_config = {"populate_by_name": True}


class LookupRequest(BaseModel):
    asset_ids: list[str] = Field(default_factory=list, max_length=20000)
    symbols: list[str] = Field(default_factory=list, max_length=20000)


class RefreshRequest(BaseModel):
    group: Optional[str] = None


def _validate_class(value: Optional[str]) -> Optional[str]:
    if value in (None, "", "all"):
        return None
    if value not in ASSET_CLASSES:
        raise HTTPException(
            status_code=422, detail="Classe inválida: use all, crypto, stock ou etf."
        )
    return value


@router.get("/catalog")
def get_asset_catalog(
    q: str = Query("", max_length=120),
    asset_class: Optional[str] = Query(None, alias="class"),
    page: int = Query(1, ge=1),
    page_size: int = Query(catalog.DEFAULT_PAGE_SIZE, ge=1, le=catalog.MAX_PAGE_SIZE),
    _user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Pesquisa paginada, sem caixa nem acento, com contagens e frescor por classe."""
    result = catalog.search_catalog(
        db, q=q, asset_class=_validate_class(asset_class), page=page, page_size=page_size
    )
    catalog.kick_refresh_if_needed(db)
    return result


@router.post("/catalog/resolve")
def resolve_asset_catalog(
    req: ResolveRequest,
    _user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Ids negociáveis do filtro atual, para o "Todos do filtro". Marcados nunca entram."""
    return catalog.resolve_filter(db, q=req.q, asset_class=_validate_class(req.asset_class))


@router.post("/catalog/lookup")
def lookup_asset_catalog(
    req: LookupRequest,
    _user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Reidrata ids ou símbolos de rascunho, snapshot, favorito ou ``?symbol=``."""
    return {
        "items": catalog.lookup_assets(db, asset_ids=req.asset_ids, symbols=req.symbols),
        "freshness": catalog.freshness_by_class(db),
    }


@router.post("/catalog/refresh")
def refresh_asset_catalog(
    req: RefreshRequest,
    _admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Gatilho manual de admin ("Tentar de novo"). Falha mantém a última lista válida."""
    if req.group is not None and req.group not in CATALOG_GROUPS:
        raise HTTPException(status_code=422, detail="Grupo inválido: use crypto ou equity.")
    groups = [req.group] if req.group else list(CATALOG_GROUPS)
    results = [catalog.refresh_group(group, trigger="manual") for group in groups]
    db.expire_all()
    return {"results": results, "freshness": catalog.freshness_by_class(db)}
