from __future__ import annotations

from decimal import Decimal
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.services.binance_market_orders import get_market_order_eligibility
from app.services.binance_spot_orders import BinanceOrderError
from app.services.monitor_spot_market_orders import (
    SpotMarketOrderError,
    create_preview,
    get_order_status,
    submit_order,
)
from app.services.user_exchange_credentials import BINANCE_PROVIDER, get_user_exchange_credential

router = APIRouter(prefix="/api/monitor/spot-market-orders", tags=["monitor"])


class SpotMarketPreviewPayload(BaseModel):
    symbol: str = Field(..., min_length=3, max_length=32)
    side: Literal["BUY", "SELL"]
    quote_amount_usdt: Optional[Decimal] = Field(
        default=None, gt=0, max_digits=24, decimal_places=8
    )
    quote_asset: Literal["USDT", "USDC"] = "USDT"


class SpotMarketSubmitPayload(BaseModel):
    preview_token: str = Field(..., min_length=32, max_length=4096)
    idempotency_key: str = Field(..., min_length=16, max_length=64)


class SpotMarketEligibilityPayload(BaseModel):
    symbols: List[str] = Field(..., min_length=1, max_length=100)


class SpotMarketEligibilityItem(BaseModel):
    symbol: str
    eligible: bool
    reason: Optional[str]


class SpotMarketEligibilityResponse(BaseModel):
    items: List[SpotMarketEligibilityItem]


class SpotMarketPreviewResponse(BaseModel):
    preview_token: str
    idempotency_key: str
    expires_at: str
    symbol: str
    strategy_symbol: str
    side: Literal["BUY", "SELL"]
    base_asset: str
    quote_asset: str
    indicative_price: str
    quote_balance: str
    base_balance: str
    requested_quote_amount: Optional[str]
    calculated_base_quantity: Optional[str]
    estimated_base_quantity: Optional[str]
    estimated_quote_amount: Optional[str]
    residual_quantity: str
    warning: str


class SpotMarketFeeResponse(BaseModel):
    asset: str
    amount: str


class SpotMarketOrderResponse(BaseModel):
    idempotency_key: str
    symbol: str
    strategy_symbol: Optional[str] = None
    side: Literal["BUY", "SELL"]
    state: Literal["submitting", "reconciling", "filled", "partial", "rejected"]
    quote_asset: Optional[str] = None
    requested_quote_amount: Optional[str]
    calculated_base_quantity: Optional[str]
    executed_base_quantity: Optional[str]
    executed_quote_amount: Optional[str]
    average_price: Optional[str]
    fees: List[SpotMarketFeeResponse]
    binance_status: Optional[str]
    residual_quantity: Optional[str]
    error_code: Optional[str]
    message: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


def _require_user_binance_creds(db: Session, user_id: str):
    credential = get_user_exchange_credential(db, user_id, BINANCE_PROVIDER)
    if (
        credential is None
        or not str(credential.api_key or "").strip()
        or not str(credential.api_secret or "").strip()
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "BINANCE_CREDENTIALS_REQUIRED",
                "message": (
                    "Configure a chave Binance em Meu Perfil com Spot Trading habilitado e sem saque."
                ),
            },
        )
    return credential


def _raise_service_error(exc: Exception) -> None:
    if isinstance(exc, SpotMarketOrderError):
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    if isinstance(exc, BinanceOrderError):
        if exc.safe_for_user:
            message = str(exc)
        elif exc.code in {-2014, -2015, -1022}:
            message = (
                "A Binance recusou a credencial ou assinatura. Revise a conexão em Meu Perfil."
            )
        elif exc.status_code >= 500:
            message = "A Binance está temporariamente indisponível. Tente novamente em instantes."
        else:
            message = "A Binance recusou a solicitação. Revise os dados e gere uma nova prévia."
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": "BINANCE_VALIDATION_ERROR", "message": message},
        ) from exc
    raise exc


@router.post(
    "/preview",
    response_model=SpotMarketPreviewResponse,
    responses={
        400: {"description": "Credencial ou regra Binance inválida"},
        502: {"description": "Binance indisponível"},
    },
)
def post_spot_market_preview(
    payload: SpotMarketPreviewPayload,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.side == "BUY" and payload.quote_amount_usdt is None:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "QUOTE_AMOUNT_REQUIRED",
                "message": f"Informe o valor em {payload.quote_asset}.",
            },
        )
    if payload.side == "SELL" and payload.quote_amount_usdt is not None:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "SELL_USES_FULL_BALANCE",
                "message": "A venda usa sempre 100% do saldo livre do ativo.",
            },
        )
    if payload.side == "SELL" and payload.quote_asset != "USDT":
        raise HTTPException(
            status_code=422,
            detail={
                "code": "SELL_QUOTE_FIXED",
                "message": "A venda 100% permanece no par da estratégia (USDT).",
            },
        )
    credential = _require_user_binance_creds(db, current_user_id)
    try:
        return create_preview(
            api_key=credential.api_key,
            api_secret=credential.api_secret,
            user_id=current_user_id,
            symbol=payload.symbol,
            side=payload.side,
            quote_amount=payload.quote_amount_usdt,
            quote_asset=payload.quote_asset if payload.side == "BUY" else "USDT",
        )
    except (SpotMarketOrderError, BinanceOrderError) as exc:
        _raise_service_error(exc)


@router.post(
    "/eligibility",
    response_model=SpotMarketEligibilityResponse,
    responses={
        400: {"description": "Símbolo inválido"},
        502: {"description": "Binance indisponível"},
    },
)
def post_spot_market_eligibility(
    payload: SpotMarketEligibilityPayload,
    current_user_id: str = Depends(get_current_user),
):
    del current_user_id
    try:
        return {"items": get_market_order_eligibility(payload.symbols)}
    except BinanceOrderError as exc:
        _raise_service_error(exc)


@router.post(
    "",
    response_model=SpotMarketOrderResponse,
    responses={
        400: {"description": "Operação inválida"},
        403: {"description": "Prévia de outro usuário"},
        409: {"description": "Prévia expirada ou conflito idempotente"},
        502: {"description": "Binance indisponível"},
    },
)
def post_spot_market_order(
    payload: SpotMarketSubmitPayload,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    credential = _require_user_binance_creds(db, current_user_id)
    try:
        return submit_order(
            db=db,
            api_key=credential.api_key,
            api_secret=credential.api_secret,
            user_id=current_user_id,
            preview_token=payload.preview_token,
            idempotency_key=payload.idempotency_key,
        )
    except (SpotMarketOrderError, BinanceOrderError) as exc:
        _raise_service_error(exc)


@router.get(
    "/{idempotency_key}",
    response_model=SpotMarketOrderResponse,
    responses={
        404: {"description": "Operação não encontrada"},
        502: {"description": "Binance indisponível"},
    },
)
def get_spot_market_order(
    idempotency_key: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not 16 <= len(idempotency_key) <= 64:
        raise HTTPException(
            status_code=422,
            detail={"code": "INVALID_IDEMPOTENCY_KEY", "message": "Identificador inválido."},
        )
    credential = get_user_exchange_credential(db, current_user_id, BINANCE_PROVIDER)
    try:
        return get_order_status(
            db=db,
            api_key=credential.api_key if credential is not None else None,
            api_secret=credential.api_secret if credential is not None else None,
            user_id=current_user_id,
            idempotency_key=idempotency_key,
        )
    except (SpotMarketOrderError, BinanceOrderError) as exc:
        _raise_service_error(exc)
