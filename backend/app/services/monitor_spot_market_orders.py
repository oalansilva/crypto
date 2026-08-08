from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import MonitorSpotOrderRequest
from app.services.binance_market_orders import (
    MarketOrderPlan,
    build_market_order_plan,
    get_binance_account_identity_hash,
    normalize_market_order_result,
    query_market_order,
    submit_market_order,
)
from app.services.binance_spot_orders import BinanceOrderError, format_decimal, normalize_symbol

PREVIEW_AUDIENCE = "monitor-spot-market-order"
TERMINAL_STATES = frozenset({"filled", "partial", "rejected"})


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class SpotMarketOrderError(RuntimeError):
    def __init__(self, message: str, *, status_code: int = 400, code: str = "INVALID_ORDER"):
        super().__init__(message)
        self.status_code = status_code
        self.code = code


def _preview_secret(api_secret: str) -> bytes:
    """Derive a domain-specific signing key without persisting or exposing the Binance secret."""
    return hashlib.sha256(f"crypto-farol:monitor-spot-preview:{api_secret}".encode()).digest()


def _preview_ttl_seconds() -> int:
    raw = (os.getenv("SPOT_ORDER_PREVIEW_TTL_SECONDS") or "300").strip()
    try:
        return max(60, min(900, int(raw)))
    except Exception:
        return 300


def _not_found_grace_seconds() -> int:
    raw = (os.getenv("SPOT_ORDER_NOT_FOUND_GRACE_SECONDS") or "30").strip()
    try:
        return max(10, min(300, int(raw)))
    except Exception:
        return 30


def _client_order_id(user_id: str, idempotency_key: str) -> str:
    digest = hashlib.sha256(f"{user_id}:{idempotency_key}".encode()).hexdigest()[:24]
    return f"cftrade_{digest}"


def _query_error_limit() -> int:
    raw = (os.getenv("SPOT_ORDER_QUERY_ERROR_LIMIT") or "5").strip()
    try:
        return max(3, min(10, int(raw)))
    except Exception:
        return 5


def _safe_rejection_message(exc: BinanceOrderError) -> str:
    if exc.code in {-2014, -2015, -1022}:
        return "A Binance recusou a credencial ou assinatura. Revise a conexão em Meu Perfil."
    if exc.code == -1013:
        return "A Binance rejeitou a ordem por um filtro atualizado. Gere uma nova prévia."
    if exc.code in {-2010, -2011}:
        return "A Binance rejeitou a ordem. Revise saldo e permissão Spot Trading."
    return "A Binance rejeitou a ordem. Gere uma nova prévia antes de tentar novamente."


def _plan_summary(plan: MarketOrderPlan) -> Dict[str, Any]:
    return {
        "base_asset": plan.base_asset,
        "quote_asset": plan.quote_asset,
        "indicative_price": format_decimal(plan.indicative_price),
        "quote_balance": format_decimal(plan.quote_balance),
        "base_balance": format_decimal(plan.base_balance),
        "requested_quote_amount": (
            format_decimal(plan.quote_amount) if plan.quote_amount is not None else None
        ),
        "calculated_base_quantity": (
            format_decimal(plan.base_quantity) if plan.base_quantity is not None else None
        ),
        "estimated_base_quantity": (
            format_decimal(plan.estimated_base_quantity)
            if plan.estimated_base_quantity is not None
            else None
        ),
        "estimated_quote_amount": (
            format_decimal(plan.estimated_quote_amount)
            if plan.estimated_quote_amount is not None
            else None
        ),
        "residual_quantity": format_decimal(plan.residual_quantity),
    }


def create_preview(
    *,
    api_key: str,
    api_secret: str,
    user_id: str,
    symbol: str,
    side: str,
    quote_amount: Optional[Decimal],
) -> Dict[str, Any]:
    plan = build_market_order_plan(
        api_key=api_key,
        api_secret=api_secret,
        symbol=symbol,
        side=side,
        quote_amount=quote_amount,
    )
    idempotency_key = secrets.token_urlsafe(24)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=_preview_ttl_seconds())
    claims = {
        "aud": PREVIEW_AUDIENCE,
        "sub": user_id,
        "jti": idempotency_key,
        "symbol": plan.symbol,
        "side": plan.side,
        "quote_amount": (
            format_decimal(plan.quote_amount) if plan.quote_amount is not None else None
        ),
        "base_balance": (format_decimal(plan.base_balance) if plan.side == "SELL" else None),
        "base_quantity": (
            format_decimal(plan.base_quantity)
            if plan.side == "SELL" and plan.base_quantity is not None
            else None
        ),
        "iat": now,
        "exp": expires_at,
    }
    summary = _plan_summary(plan)
    return {
        "preview_token": jwt.encode(claims, _preview_secret(api_secret), algorithm="HS256"),
        "idempotency_key": idempotency_key,
        "expires_at": expires_at.isoformat(),
        "symbol": plan.symbol,
        "side": plan.side,
        **summary,
        "warning": (
            "A compra será enviada a mercado e o preço final pode variar."
            if plan.side == "BUY"
            else "A venda usará 100% do saldo livre possível; filtros da Binance podem deixar resíduo."
        ),
    }


def _decode_preview(
    preview_token: str,
    *,
    api_secret: str,
    user_id: str,
    idempotency_key: str,
) -> Dict[str, Any]:
    try:
        claims = jwt.decode(
            preview_token,
            _preview_secret(api_secret),
            algorithms=["HS256"],
            audience=PREVIEW_AUDIENCE,
        )
    except jwt.ExpiredSignatureError as exc:
        raise SpotMarketOrderError(
            "A confirmação expirou. Gere uma nova prévia.",
            status_code=409,
            code="PREVIEW_EXPIRED",
        ) from exc
    except jwt.PyJWTError as exc:
        raise SpotMarketOrderError(
            "Prévia inválida. Gere uma nova confirmação.",
            status_code=400,
            code="INVALID_PREVIEW",
        ) from exc
    if str(claims.get("sub") or "") != user_id or str(claims.get("jti") or "") != idempotency_key:
        raise SpotMarketOrderError(
            "Prévia não pertence a esta operação.",
            status_code=403,
            code="PREVIEW_SCOPE_MISMATCH",
        )
    return claims


def _record_response(record: MonitorSpotOrderRequest) -> Dict[str, Any]:
    summary = dict(record.result_summary or {})
    return {
        "idempotency_key": record.idempotency_key,
        "symbol": record.symbol,
        "side": record.side,
        "state": record.state,
        "requested_quote_amount": (
            format_decimal(record.requested_quote_amount)
            if record.requested_quote_amount is not None
            else None
        ),
        "calculated_base_quantity": (
            format_decimal(record.calculated_base_quantity)
            if record.calculated_base_quantity is not None
            else None
        ),
        "executed_base_quantity": (
            format_decimal(record.executed_base_quantity)
            if record.executed_base_quantity is not None
            else None
        ),
        "executed_quote_amount": (
            format_decimal(record.executed_quote_amount)
            if record.executed_quote_amount is not None
            else None
        ),
        "average_price": (
            format_decimal(record.average_price) if record.average_price is not None else None
        ),
        "fees": summary.get("fees") or [],
        "binance_status": summary.get("binance_status"),
        "residual_quantity": summary.get("residual_quantity"),
        "error_code": record.error_code,
        "message": summary.get("message"),
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }


def _transition(
    db: Session,
    record: MonitorSpotOrderRequest,
    *,
    from_states: tuple[str, ...],
    values: Dict[str, Any],
) -> bool:
    """Apply a state transition only when the current state still allows it.

    Guards against last-write-wins regressions when two reconciliations run
    concurrently for the same record: a terminal result committed by one
    reconciler is never overwritten by a stale write from another.
    """
    updated = (
        db.query(MonitorSpotOrderRequest)
        .filter(
            MonitorSpotOrderRequest.id == record.id,
            MonitorSpotOrderRequest.state.in_(from_states),
        )
        .update(values, synchronize_session=False)
    )
    db.commit()
    db.refresh(record)
    return bool(updated)


def _apply_result(
    db: Session,
    record: MonitorSpotOrderRequest,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    summary = dict(record.result_summary or {})
    result_fees = result.get("fees") or []
    if result_fees or "fees" not in summary:
        summary["fees"] = result_fees
    summary["binance_status"] = result.get("binance_status")
    summary.pop("not_found_reconcile_count", None)
    summary.pop("query_error_count", None)
    if result["state"] == "rejected":
        summary["message"] = "A Binance confirmou que a ordem não foi executada."
    else:
        summary.pop("message", None)
    now = _utcnow()
    _transition(
        db,
        record,
        from_states=("submitting", "reconciling"),
        values={
            "state": str(result["state"]),
            "external_order_id": result.get("external_order_id"),
            "executed_base_quantity": Decimal(str(result["executed_base_quantity"])),
            "executed_quote_amount": Decimal(str(result["executed_quote_amount"])),
            "average_price": Decimal(str(result["average_price"])),
            "error_code": None,
            "result_summary": summary,
            "updated_at": now,
            "last_reconciled_at": now,
        },
    )
    return _record_response(record)


def _mark_reconciling(db: Session, record: MonitorSpotOrderRequest) -> None:
    summary = dict(record.result_summary or {})
    summary.pop("not_found_reconcile_count", None)
    summary.pop("query_error_count", None)
    summary["message"] = (
        "A Binance recebeu a solicitação, mas o resultado ainda está sendo confirmado."
    )
    _transition(
        db,
        record,
        from_states=("submitting", "reconciling"),
        values={
            "state": "reconciling",
            "error_code": "ORDER_STATUS_UNKNOWN",
            "result_summary": summary,
            "updated_at": _utcnow(),
            "last_reconciled_at": _utcnow(),
        },
    )


def _handle_query_error(db: Session, record: MonitorSpotOrderRequest) -> Dict[str, Any]:
    """Bound the reconciling loop for persistent non-auth query errors.

    A bounded strike counter terminates in a safe terminal state with a
    sanitized message, so a permanently failing query can never wedge the
    per-symbol lock indefinitely.
    """
    now = _utcnow()
    summary = dict(record.result_summary or {})
    error_count = int(summary.get("query_error_count") or 0) + 1
    summary["query_error_count"] = error_count
    created_at = record.created_at or now
    age_seconds = max(0.0, (now - created_at).total_seconds())

    if error_count >= _query_error_limit() and age_seconds >= _not_found_grace_seconds():
        summary.pop("query_error_count", None)
        summary["message"] = (
            "Não foi possível confirmar o resultado com a Binance após novas consultas. "
            "Verifique o saldo no Monitor antes de gerar uma nova prévia."
        )
        _transition(
            db,
            record,
            from_states=("submitting", "reconciling"),
            values={
                "state": "rejected",
                "error_code": "BINANCE_QUERY_FAILED",
                "result_summary": summary,
                "updated_at": now,
                "last_reconciled_at": now,
            },
        )
    else:
        summary["message"] = (
            "A Binance recebeu a solicitação, mas o resultado ainda está sendo confirmado."
        )
        _transition(
            db,
            record,
            from_states=("submitting", "reconciling"),
            values={
                "state": "reconciling",
                "error_code": "ORDER_STATUS_UNKNOWN",
                "result_summary": summary,
                "updated_at": now,
                "last_reconciled_at": now,
            },
        )
    return _record_response(record)


def _handle_order_not_found(
    db: Session,
    record: MonitorSpotOrderRequest,
    *,
    api_key: str,
    api_secret: str,
) -> Dict[str, Any]:
    """Resolve a durable request that Binance repeatedly confirms does not exist.

    A short grace period avoids treating exchange propagation delay as a rejection.
    Before the lock is released, one final live verification query runs so a fill
    that only became visible after the last -2013 is still recorded as executed.
    """
    now = _utcnow()
    summary = dict(record.result_summary or {})
    not_found_count = int(summary.get("not_found_reconcile_count") or 0) + 1
    summary["not_found_reconcile_count"] = not_found_count
    created_at = record.created_at or now
    age_seconds = max(0.0, (now - created_at).total_seconds())

    if not_found_count >= 3 and age_seconds >= _not_found_grace_seconds():
        summary.pop("not_found_reconcile_count", None)
        try:
            final_payload = query_market_order(
                api_key=api_key,
                api_secret=api_secret,
                symbol=record.symbol,
                client_order_id=record.client_order_id,
            )
        except BinanceOrderError:
            final_payload = None
        if final_payload is not None:
            return _apply_result(db, record, normalize_market_order_result(final_payload))
        summary["message"] = (
            "A ordem não foi localizada na Binance após novas consultas. "
            "Nenhuma execução foi registrada; gere uma nova prévia para tentar novamente."
        )
        _transition(
            db,
            record,
            from_states=("submitting", "reconciling"),
            values={
                "state": "rejected",
                "error_code": "BINANCE_ORDER_NOT_FOUND",
                "result_summary": summary,
                "updated_at": now,
                "last_reconciled_at": now,
            },
        )
    else:
        summary["message"] = (
            "A Binance ainda não localizou a ordem. Continuaremos consultando antes de liberar "
            "um novo envio."
        )
        _transition(
            db,
            record,
            from_states=("submitting", "reconciling"),
            values={
                "state": "reconciling",
                "error_code": "ORDER_STATUS_UNKNOWN",
                "result_summary": summary,
                "updated_at": now,
                "last_reconciled_at": now,
            },
        )
    return _record_response(record)


def _reconcile(
    *,
    db: Session,
    record: MonitorSpotOrderRequest,
    api_key: str,
    api_secret: str,
) -> Dict[str, Any]:
    if record.state in TERMINAL_STATES:
        return _record_response(record)
    try:
        payload = query_market_order(
            api_key=api_key,
            api_secret=api_secret,
            symbol=record.symbol,
            client_order_id=record.client_order_id,
        )
    except BinanceOrderError as exc:
        if exc.code == -2013:
            current_identity = get_binance_account_identity_hash(
                api_key=api_key,
                api_secret=api_secret,
            )
            submitting_identity = str(record.submitting_account_identity_hash or "")
            if not submitting_identity or not secrets.compare_digest(
                current_identity,
                submitting_identity,
            ):
                raise SpotMarketOrderError(
                    "A conta Binance vinculada mudou durante a verificação. "
                    "Reconecte a conta usada no envio original antes de continuar.",
                    status_code=409,
                    code="BINANCE_ACCOUNT_CHANGED",
                )
            return _handle_order_not_found(
                db,
                record,
                api_key=api_key,
                api_secret=api_secret,
            )
        if exc.code in {-2014, -2015, -1022}:
            raise
        return _handle_query_error(db, record)
    return _apply_result(db, record, normalize_market_order_result(payload))


def submit_order(
    *,
    db: Session,
    api_key: str,
    api_secret: str,
    user_id: str,
    preview_token: str,
    idempotency_key: str,
) -> Dict[str, Any]:
    existing = (
        db.query(MonitorSpotOrderRequest)
        .filter(
            MonitorSpotOrderRequest.user_id == user_id,
            MonitorSpotOrderRequest.idempotency_key == idempotency_key,
        )
        .first()
    )
    if existing is not None:
        return _reconcile(
            db=db,
            record=existing,
            api_key=api_key,
            api_secret=api_secret,
        )

    claims = _decode_preview(
        preview_token,
        api_secret=api_secret,
        user_id=user_id,
        idempotency_key=idempotency_key,
    )

    preview_symbol = normalize_symbol(str(claims.get("symbol") or ""))
    unresolved = (
        db.query(MonitorSpotOrderRequest)
        .filter(
            MonitorSpotOrderRequest.user_id == user_id,
            MonitorSpotOrderRequest.symbol == preview_symbol,
            MonitorSpotOrderRequest.state.in_(("submitting", "reconciling")),
        )
        .first()
    )
    if unresolved is not None:
        current = _reconcile(
            db=db,
            record=unresolved,
            api_key=api_key,
            api_secret=api_secret,
        )
        if current["state"] not in TERMINAL_STATES:
            raise SpotMarketOrderError(
                "Já existe uma operação deste ativo aguardando confirmação da Binance. "
                "Aguarde a reconciliação antes de enviar outra ordem.",
                status_code=409,
                code="ORDER_PENDING",
            )
        raise SpotMarketOrderError(
            "Uma operação anterior deste ativo acabou de ser reconciliada. "
            "Revise o resultado no Monitor e gere uma nova prévia antes de confirmar outra ordem.",
            status_code=409,
            code="PRIOR_ORDER_RECONCILED",
        )

    quote_raw = claims.get("quote_amount")
    plan = build_market_order_plan(
        api_key=api_key,
        api_secret=api_secret,
        symbol=preview_symbol,
        side=str(claims.get("side") or ""),
        quote_amount=Decimal(str(quote_raw)) if quote_raw is not None else None,
    )
    if plan.side == "SELL":
        try:
            reviewed_balance = Decimal(str(claims["base_balance"]))
            reviewed_quantity = Decimal(str(claims["base_quantity"]))
        except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise SpotMarketOrderError(
                "Prévia de venda inválida. Gere uma nova confirmação.",
                status_code=400,
                code="INVALID_PREVIEW",
            ) from exc
        if plan.base_balance != reviewed_balance or plan.base_quantity != reviewed_quantity:
            raise SpotMarketOrderError(
                "O saldo livre mudou após a prévia. Revise e confirme novamente a venda de 100%.",
                status_code=409,
                code="PREVIEW_STALE",
            )
    plan_summary = _plan_summary(plan)
    record = MonitorSpotOrderRequest(
        user_id=user_id,
        idempotency_key=idempotency_key,
        client_order_id=_client_order_id(user_id, idempotency_key),
        symbol=plan.symbol,
        side=plan.side,
        state="submitting",
        submitting_account_identity_hash=plan.account_identity_hash,
        requested_quote_amount=plan.quote_amount,
        calculated_base_quantity=plan.base_quantity,
        result_summary={
            "residual_quantity": plan_summary["residual_quantity"],
            "base_asset": plan.base_asset,
            "quote_asset": plan.quote_asset,
        },
    )
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(MonitorSpotOrderRequest)
            .filter(
                MonitorSpotOrderRequest.user_id == user_id,
                MonitorSpotOrderRequest.idempotency_key == idempotency_key,
            )
            .first()
        )
        if existing is None:
            unresolved = (
                db.query(MonitorSpotOrderRequest)
                .filter(
                    MonitorSpotOrderRequest.user_id == user_id,
                    MonitorSpotOrderRequest.symbol == plan.symbol,
                    MonitorSpotOrderRequest.state.in_(("submitting", "reconciling")),
                )
                .first()
            )
            if unresolved is not None:
                raise SpotMarketOrderError(
                    "Já existe uma operação deste ativo aguardando confirmação da Binance.",
                    status_code=409,
                    code="ORDER_PENDING",
                )
            raise SpotMarketOrderError(
                "Não foi possível registrar a operação.",
                status_code=409,
                code="IDEMPOTENCY_CONFLICT",
            )
        return _reconcile(
            db=db,
            record=existing,
            api_key=api_key,
            api_secret=api_secret,
        )

    try:
        payload = submit_market_order(
            api_key=api_key,
            api_secret=api_secret,
            plan=plan,
            client_order_id=record.client_order_id,
        )
    except BinanceOrderError as exc:
        if exc.outcome_unknown:
            _mark_reconciling(db, record)
            return _reconcile(
                db=db,
                record=record,
                api_key=api_key,
                api_secret=api_secret,
            )
        _transition(
            db,
            record,
            from_states=("submitting", "reconciling"),
            values={
                "state": "rejected",
                "error_code": (
                    f"BINANCE_{exc.code}" if exc.code is not None else "BINANCE_REJECTED"
                ),
                "result_summary": {
                    **dict(record.result_summary or {}),
                    "message": _safe_rejection_message(exc),
                },
                "updated_at": _utcnow(),
                "last_reconciled_at": _utcnow(),
            },
        )
        return _record_response(record)
    return _apply_result(db, record, normalize_market_order_result(payload))

def get_order_status(
    *,
    db: Session,
    api_key: Optional[str],
    api_secret: Optional[str],
    user_id: str,
    idempotency_key: str,
) -> Dict[str, Any]:
    record = (
        db.query(MonitorSpotOrderRequest)
        .filter(
            MonitorSpotOrderRequest.user_id == user_id,
            MonitorSpotOrderRequest.idempotency_key == idempotency_key,
        )
        .first()
    )
    if record is None:
        raise SpotMarketOrderError(
            "Operação não encontrada.",
            status_code=404,
            code="ORDER_NOT_FOUND",
        )
    if record.state in TERMINAL_STATES:
        return _record_response(record)
    if not str(api_key or "").strip() or not str(api_secret or "").strip():
        raise SpotMarketOrderError(
            "Reconecte a Binance em Meu Perfil para concluir a verificação desta operação.",
            status_code=400,
            code="BINANCE_CREDENTIALS_REQUIRED",
        )
    return _reconcile(
        db=db,
        record=record,
        api_key=str(api_key),
        api_secret=str(api_secret),
    )
