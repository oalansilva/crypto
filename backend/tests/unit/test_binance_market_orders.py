from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from io import BytesIO
import json
from types import SimpleNamespace
from urllib.error import HTTPError
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import MonitorSpotOrderRequest
from app.routes import monitor_spot_market
from app.services import binance_market_orders as market
from app.services import monitor_spot_market_orders as workflow
from app.services.binance_spot_orders import BinanceOrderError
from app.services import binance_spot_orders

SYMBOL_INFO = {
    "symbol": "ETHUSDT",
    "status": "TRADING",
    "baseAsset": "ETH",
    "quoteAsset": "USDT",
    "isSpotTradingAllowed": True,
    "quoteOrderQtyMarketAllowed": True,
    "orderTypes": ["LIMIT", "MARKET"],
    "filters": [
        {
            "filterType": "MARKET_LOT_SIZE",
            "stepSize": "0.001",
            "minQty": "0.001",
            "maxQty": "100",
        },
        {"filterType": "MIN_NOTIONAL", "minNotional": "5", "applyToMarket": True},
    ],
}


def _plan(*, side: str = "BUY") -> market.MarketOrderPlan:
    return market.MarketOrderPlan(
        symbol="ETHUSDT",
        side=side,
        base_asset="ETH",
        quote_asset="USDT",
        account_identity_hash="a" * 64,
        indicative_price=Decimal("2000"),
        quote_balance=Decimal("500"),
        base_balance=Decimal("1.2345"),
        quote_amount=Decimal("100") if side == "BUY" else None,
        base_quantity=Decimal("1.234") if side == "SELL" else None,
        estimated_base_quantity=Decimal("0.05") if side == "BUY" else None,
        estimated_quote_amount=Decimal("2468") if side == "SELL" else None,
        residual_quantity=Decimal("0.0005") if side == "SELL" else Decimal("0"),
    )


@patch("app.services.binance_market_orders.signed_request")
@patch("app.services.binance_market_orders.public_get")
@patch("app.services.binance_market_orders.get_symbol_info", return_value=SYMBOL_INFO)
def test_buy_plan_uses_quote_amount_and_free_usdt(_info, public_get, signed_request):
    public_get.return_value = {"price": "2000"}
    signed_request.return_value = {
        "canTrade": True,
        "balances": [{"asset": "USDT", "free": "500"}, {"asset": "ETH", "free": "1"}],
    }
    plan = market.build_market_order_plan(
        api_key="key",
        api_secret="secret",
        symbol="ETH/USDT",
        side="BUY",
        quote_amount=Decimal("125.50"),
    )
    assert plan.quote_amount == Decimal("125.50")
    assert plan.estimated_base_quantity == Decimal("0.06275")


@patch("app.services.binance_market_orders.signed_request")
@patch("app.services.binance_market_orders.public_get", return_value={"price": "2000"})
@patch("app.services.binance_market_orders.get_symbol_info", return_value=SYMBOL_INFO)
def test_sell_plan_uses_maximum_valid_free_balance(_info, _price, signed_request):
    signed_request.return_value = {
        "canTrade": True,
        "balances": [{"asset": "USDT", "free": "10"}, {"asset": "ETH", "free": "1.2345"}],
    }
    plan = market.build_market_order_plan(
        api_key="key", api_secret="secret", symbol="ETHUSDT", side="SELL"
    )
    assert plan.base_quantity == Decimal("1.234")
    assert plan.residual_quantity == Decimal("0.0005")
    assert plan.estimated_quote_amount == Decimal("2468.000")


def test_market_lot_zero_step_preserves_its_active_maximum():
    symbol_info = {
        **SYMBOL_INFO,
        "filters": [
            {
                "filterType": "LOT_SIZE",
                "stepSize": "0.001",
                "minQty": "0.001",
                "maxQty": "100",
            },
            {
                "filterType": "MARKET_LOT_SIZE",
                "stepSize": "0",
                "minQty": "0",
                "maxQty": "1",
            },
            {"filterType": "MIN_NOTIONAL", "minNotional": "0", "applyToMarket": True},
        ],
    }
    with (
        patch("app.services.binance_market_orders.get_symbol_info", return_value=symbol_info),
        patch("app.services.binance_market_orders.public_get", return_value={"price": "2000"}),
        patch(
            "app.services.binance_market_orders.signed_request",
            return_value={
                "canTrade": True,
                "balances": [{"asset": "ETH", "free": "2"}],
            },
        ),
        pytest.raises(BinanceOrderError, match="Quantidade acima do máximo"),
    ):
        market.build_market_order_plan(
            api_key="key", api_secret="secret", symbol="ETHUSDT", side="SELL"
        )


def test_sell_notional_uses_binance_average_price_when_filter_requires_it():
    symbol_info = {
        **SYMBOL_INFO,
        "filters": [
            SYMBOL_INFO["filters"][0],
            {
                "filterType": "NOTIONAL",
                "minNotional": "5",
                "maxNotional": "0",
                "applyMinToMarket": True,
                "applyMaxToMarket": False,
                "avgPriceMins": 5,
            },
        ],
    }

    def price_response(path, _params, **_kwargs):
        return {"price": "10" if path.endswith("ticker/price") else "4"}

    with (
        patch("app.services.binance_market_orders.get_symbol_info", return_value=symbol_info),
        patch(
            "app.services.binance_market_orders.public_get", side_effect=price_response
        ) as public_get,
        patch(
            "app.services.binance_market_orders.signed_request",
            return_value={
                "canTrade": True,
                "balances": [{"asset": "ETH", "free": "1.2"}],
            },
        ),
        pytest.raises(BinanceOrderError, match="Valor abaixo do mínimo"),
    ):
        market.build_market_order_plan(
            api_key="key", api_secret="secret", symbol="ETHUSDT", side="SELL"
        )
    assert [call.args[0] for call in public_get.call_args_list] == [
        "/api/v3/ticker/price",
        "/api/v3/avgPrice",
    ]


@pytest.mark.parametrize(
    ("side", "free_balance", "quote_amount", "message"),
    [
        ("SELL", "101", None, "acima do máximo"),
        ("BUY", "1000000", Decimal("202000"), "acima do máximo"),
    ],
)
@patch("app.services.binance_market_orders.public_get", return_value={"price": "2000"})
@patch("app.services.binance_market_orders.get_symbol_info", return_value=SYMBOL_INFO)
def test_plan_rejects_market_quantities_outside_lot_limits(
    _info,
    _price,
    side,
    free_balance,
    quote_amount,
    message,
):
    balances = [
        {"asset": "USDT", "free": free_balance if side == "BUY" else "10"},
        {"asset": "ETH", "free": free_balance if side == "SELL" else "1"},
    ]
    with (
        patch(
            "app.services.binance_market_orders.signed_request",
            return_value={"canTrade": True, "balances": balances},
        ),
        pytest.raises(BinanceOrderError, match=message),
    ):
        market.build_market_order_plan(
            api_key="key",
            api_secret="secret",
            symbol="ETHUSDT",
            side=side,
            quote_amount=quote_amount,
        )


def test_buy_plan_rejects_estimated_quantity_below_market_lot_minimum():
    symbol_info = {
        **SYMBOL_INFO,
        "filters": [
            SYMBOL_INFO["filters"][0],
            {"filterType": "MIN_NOTIONAL", "minNotional": "0", "applyToMarket": True},
        ],
    }
    with (
        patch("app.services.binance_market_orders.get_symbol_info", return_value=symbol_info),
        patch("app.services.binance_market_orders.public_get", return_value={"price": "2000"}),
        patch(
            "app.services.binance_market_orders.signed_request",
            return_value={
                "canTrade": True,
                "balances": [{"asset": "USDT", "free": "500"}],
            },
        ),
        pytest.raises(BinanceOrderError, match="Quantidade abaixo do mínimo"),
    ):
        market.build_market_order_plan(
            api_key="key",
            api_secret="secret",
            symbol="ETHUSDT",
            side="BUY",
            quote_amount=Decimal("1"),
        )


@patch("app.services.binance_market_orders.signed_request")
@patch("app.services.binance_market_orders.public_get", return_value={"price": "2000"})
@patch("app.services.binance_market_orders.get_symbol_info", return_value=SYMBOL_INFO)
def test_plan_rejects_read_only_binance_credential(_info, _price, signed_request):
    signed_request.return_value = {"canTrade": False, "balances": []}
    with pytest.raises(BinanceOrderError, match="Spot Trading") as error:
        market.build_market_order_plan(
            api_key="read-only",
            api_secret="secret",
            symbol="ETHUSDT",
            side="BUY",
            quote_amount=Decimal("10"),
        )
    assert error.value.status_code == 403
    assert error.value.safe_for_user is True


@pytest.mark.parametrize(
    ("symbol_info", "message"),
    [
        ({**SYMBOL_INFO, "status": "BREAK"}, "indisponível"),
        ({**SYMBOL_INFO, "quoteAsset": "BTC"}, "USDT"),
        ({**SYMBOL_INFO, "orderTypes": ["LIMIT"]}, "MARKET"),
    ],
)
def test_plan_rejects_ineligible_symbols(symbol_info, message):
    with (
        patch("app.services.binance_market_orders.get_symbol_info", return_value=symbol_info),
        pytest.raises(BinanceOrderError, match=message),
    ):
        market.build_market_order_plan(
            api_key="key",
            api_secret="secret",
            symbol="ETHUSDT",
            side="BUY",
            quote_amount=Decimal("10"),
        )


@patch("app.services.binance_market_orders.public_get")
def test_batch_eligibility_uses_live_exchange_info(public_get):
    available = {
        "ETHUSDT": SYMBOL_INFO,
        "BADUSDT": {**SYMBOL_INFO, "symbol": "BADUSDT", "status": "BREAK"},
    }

    def exchange_info(_path, params):
        requested = json.loads(params["symbols"])
        if "NONEUSDT" in requested:
            raise BinanceOrderError("Invalid symbol", code=-1121)
        return {"symbols": [available[symbol] for symbol in requested if symbol in available]}

    public_get.side_effect = exchange_info
    results = market.get_market_order_eligibility(["ETH/USDT", "BADUSDT", "NONEUSDT"])
    assert results == [
        {"symbol": "ETHUSDT", "eligible": True, "reason": None},
        {
            "symbol": "BADUSDT",
            "eligible": False,
            "reason": "Ativo indisponível para negociação Spot",
        },
        {
            "symbol": "NONEUSDT",
            "eligible": False,
            "reason": "Par não encontrado na Binance Spot.",
        },
    ]
    assert public_get.call_count > 1


def test_public_exchange_info_error_preserves_invalid_symbol_code():
    error = HTTPError(
        "https://api.binance.com/api/v3/exchangeInfo",
        400,
        "error",
        {},
        BytesIO(b'{"code":-1121,"msg":"Invalid symbol."}'),
    )
    with (
        patch("app.services.binance_spot_orders.urllib.request.urlopen", side_effect=error),
        pytest.raises(BinanceOrderError) as raised,
    ):
        binance_spot_orders.public_get("/api/v3/exchangeInfo", {"symbol": "NONEUSDT"})
    assert raised.value.code == -1121


@pytest.mark.parametrize(
    ("status_code", "body"),
    [
        (408, b'{"code":-1007,"msg":"Timeout waiting for response"}'),
        (400, b'{"code":-1006,"msg":"Unexpected response"}'),
    ],
)
def test_submit_timeout_errors_are_classified_as_unknown_outcomes(status_code, body):
    error = HTTPError("https://api.binance.com", status_code, "error", {}, BytesIO(body))
    with (
        patch("app.services.binance_spot_orders.urllib.request.urlopen", side_effect=error),
        pytest.raises(BinanceOrderError) as raised,
    ):
        binance_spot_orders.signed_request(
            method="POST",
            path="/api/v3/order",
            api_key="key",
            api_secret="secret",
        )
    assert raised.value.outcome_unknown is True
    assert raised.value.status_code == 502


@patch("app.services.binance_market_orders.signed_request")
def test_submit_buy_uses_quote_order_qty_and_sell_uses_quantity(signed_request):
    signed_request.return_value = {"status": "FILLED"}
    market.submit_market_order(
        api_key="key", api_secret="secret", plan=_plan(side="BUY"), client_order_id="cftrade_a"
    )
    buy_params = signed_request.call_args.kwargs["params"]
    assert buy_params["type"] == "MARKET"
    assert buy_params["quoteOrderQty"] == "100"
    assert "quantity" not in buy_params

    market.submit_market_order(
        api_key="key", api_secret="secret", plan=_plan(side="SELL"), client_order_id="cftrade_b"
    )
    sell_params = signed_request.call_args.kwargs["params"]
    assert sell_params["quantity"] == "1.234"
    assert "quoteOrderQty" not in sell_params


def test_normalize_result_keeps_only_safe_summary():
    result = market.normalize_market_order_result(
        {
            "orderId": 42,
            "status": "FILLED",
            "executedQty": "0.05",
            "cummulativeQuoteQty": "101",
            "fills": [
                {"commissionAsset": "ETH", "commission": "0.00002", "price": "2020"},
                {"commissionAsset": "ETH", "commission": "0.00003", "price": "2020"},
            ],
            "signature": "must-not-leak",
        }
    )
    assert result == {
        "state": "filled",
        "external_order_id": "42",
        "executed_base_quantity": "0.05",
        "executed_quote_amount": "101",
        "average_price": "2020",
        "fees": [{"asset": "ETH", "amount": "0.00005"}],
        "binance_status": "FILLED",
    }
    assert "signature" not in result


def test_normalize_partial_and_rejected_results():
    partial = market.normalize_market_order_result(
        {
            "orderId": 43,
            "status": "PARTIALLY_FILLED",
            "executedQty": "0.02",
            "cummulativeQuoteQty": "40",
        }
    )
    rejected = market.normalize_market_order_result(
        {
            "orderId": 44,
            "status": "CANCELED",
            "executedQty": "0",
            "cummulativeQuoteQty": "0",
        }
    )
    expired_in_match = market.normalize_market_order_result(
        {
            "orderId": 45,
            "status": "EXPIRED_IN_MATCH",
            "executedQty": "0",
            "cummulativeQuoteQty": "0",
        }
    )
    assert partial["state"] == "reconciling"
    assert partial["average_price"] == "2000"
    assert rejected["state"] == "rejected"
    assert expired_in_match["state"] == "rejected"
    canceled_after_fill = market.normalize_market_order_result(
        {
            "orderId": 46,
            "status": "CANCELED",
            "executedQty": "0.01",
            "cummulativeQuoteQty": "20",
        }
    )
    assert canceled_after_fill["state"] == "partial"


class _FakeQuery:
    def __init__(self, session):
        self.session = session

    def filter(self, *args):
        return self

    def first(self):
        return self.session.record

    def update(self, values, **kwargs):
        record = self.session.record
        if record is None or record.state not in ("submitting", "reconciling"):
            return 0
        for key, value in values.items():
            setattr(record, key, value)
        return 1


class _FakeSession:
    def __init__(self):
        self.record = None

    def query(self, _model):
        return _FakeQuery(self)

    def add(self, record):
        self.record = record
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        record.created_at = now
        record.updated_at = now

    def commit(self):
        return None

    def rollback(self):
        return None

    def refresh(self, _record):
        return None


def _filled_payload():
    return {
        "orderId": 42,
        "status": "FILLED",
        "executedQty": "0.05",
        "cummulativeQuoteQty": "100",
        "fills": [],
    }


def test_preview_token_is_user_scoped_and_submit_is_idempotent():
    session = _FakeSession()
    with patch(
        "app.services.monitor_spot_market_orders.build_market_order_plan", return_value=_plan()
    ):
        preview = workflow.create_preview(
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            symbol="ETHUSDT",
            side="BUY",
            quote_amount=Decimal("100"),
        )
        with patch(
            "app.services.monitor_spot_market_orders.submit_market_order",
            return_value=_filled_payload(),
        ) as submit_mock:
            first = workflow.submit_order(
                db=session,
                api_key="key",
                api_secret="secret",
                user_id="user-a",
                preview_token=preview["preview_token"],
                idempotency_key=preview["idempotency_key"],
            )
            second = workflow.submit_order(
                db=session,
                api_key="key",
                api_secret="secret",
                user_id="user-a",
                preview_token=preview["preview_token"],
                idempotency_key=preview["idempotency_key"],
            )
    assert first["state"] == "filled"
    assert second["state"] == "filled"
    submit_mock.assert_called_once()
    assert session.record.client_order_id.startswith("cftrade_")
    assert len(session.record.client_order_id) <= 36


def test_preview_token_cannot_be_reused_by_another_user():
    with patch(
        "app.services.monitor_spot_market_orders.build_market_order_plan", return_value=_plan()
    ):
        preview = workflow.create_preview(
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            symbol="ETHUSDT",
            side="BUY",
            quote_amount=Decimal("100"),
        )
    with pytest.raises(workflow.SpotMarketOrderError, match="não pertence"):
        workflow.submit_order(
            db=_FakeSession(),
            api_key="key",
            api_secret="secret",
            user_id="user-b",
            preview_token=preview["preview_token"],
            idempotency_key=preview["idempotency_key"],
        )


def test_preview_token_is_bound_to_the_current_binance_credential():
    with patch(
        "app.services.monitor_spot_market_orders.build_market_order_plan", return_value=_plan()
    ):
        preview = workflow.create_preview(
            api_key="key",
            api_secret="original-secret",
            user_id="user-a",
            symbol="ETHUSDT",
            side="BUY",
            quote_amount=Decimal("100"),
        )
    with pytest.raises(workflow.SpotMarketOrderError, match="Prévia inválida"):
        workflow.submit_order(
            db=_FakeSession(),
            api_key="key",
            api_secret="rotated-secret",
            user_id="user-a",
            preview_token=preview["preview_token"],
            idempotency_key=preview["idempotency_key"],
        )


def test_sell_preview_rejects_balance_or_quantity_changed_before_confirmation():
    reviewed_plan = _plan(side="SELL")
    current_plan = replace(
        reviewed_plan,
        base_balance=Decimal("2.2345"),
        base_quantity=Decimal("2.234"),
        estimated_quote_amount=Decimal("4468"),
    )
    with patch(
        "app.services.monitor_spot_market_orders.build_market_order_plan",
        return_value=reviewed_plan,
    ):
        preview = workflow.create_preview(
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            symbol="ETHUSDT",
            side="SELL",
            quote_amount=None,
        )

    with (
        patch(
            "app.services.monitor_spot_market_orders.build_market_order_plan",
            return_value=current_plan,
        ),
        pytest.raises(workflow.SpotMarketOrderError, match="saldo livre mudou") as error,
    ):
        workflow.submit_order(
            db=_FakeSession(),
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            preview_token=preview["preview_token"],
            idempotency_key=preview["idempotency_key"],
        )
    assert error.value.code == "PREVIEW_STALE"


def test_existing_order_is_reconciled_before_an_expired_preview_is_decoded():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="filled",
        requested_quote_amount=Decimal("100"),
        executed_base_quantity=Decimal("0.05"),
        executed_quote_amount=Decimal("100"),
        average_price=Decimal("2000"),
        result_summary={"fees": [], "binance_status": "FILLED"},
        created_at=now,
        updated_at=now,
    )
    with patch("app.services.monitor_spot_market_orders._decode_preview") as decode_preview:
        result = workflow.submit_order(
            db=session,
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            preview_token="expired-or-unreadable-token",
            idempotency_key="existing-idempotency-key",
        )
    assert result["state"] == "filled"
    decode_preview.assert_not_called()


def test_fresh_key_is_blocked_while_same_symbol_order_remains_unresolved():
    with patch(
        "app.services.monitor_spot_market_orders.build_market_order_plan", return_value=_plan()
    ):
        preview = workflow.create_preview(
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            symbol="ETHUSDT",
            side="BUY",
            quote_amount=Decimal("100"),
        )
    pending = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="other-key",
        client_order_id="cftrade_pending",
        symbol="ETHUSDT",
        side="BUY",
        state="reconciling",
        result_summary={},
    )
    db = MagicMock()
    exact_query = MagicMock()
    exact_query.filter.return_value.first.return_value = None
    unresolved_query = MagicMock()
    unresolved_query.filter.return_value.first.return_value = pending
    db.query.side_effect = [exact_query, unresolved_query]
    with (
        patch(
            "app.services.monitor_spot_market_orders._reconcile",
            return_value={"state": "reconciling"},
        ),
        pytest.raises(workflow.SpotMarketOrderError, match="aguardando confirmação") as error,
    ):
        workflow.submit_order(
            db=db,
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            preview_token=preview["preview_token"],
            idempotency_key=preview["idempotency_key"],
        )
    assert error.value.code == "ORDER_PENDING"


def test_fresh_key_requires_new_preview_after_prior_order_is_reconciled():
    with patch(
        "app.services.monitor_spot_market_orders.build_market_order_plan", return_value=_plan()
    ):
        preview = workflow.create_preview(
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            symbol="ETHUSDT",
            side="BUY",
            quote_amount=Decimal("100"),
        )
    pending = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="prior-key",
        client_order_id="cftrade_prior",
        symbol="ETHUSDT",
        side="BUY",
        state="reconciling",
        result_summary={},
    )
    prior_fill = {"idempotency_key": "prior-key", "state": "filled"}
    db = MagicMock()
    exact_query = MagicMock()
    exact_query.filter.return_value.first.return_value = None
    unresolved_query = MagicMock()
    unresolved_query.filter.return_value.first.return_value = pending
    db.query.side_effect = [exact_query, unresolved_query]
    with (
        patch(
            "app.services.monitor_spot_market_orders._reconcile",
            return_value=prior_fill,
        ),
        patch("app.services.monitor_spot_market_orders.build_market_order_plan") as build_plan,
        patch("app.services.monitor_spot_market_orders.submit_market_order") as submit_market,
    ):
        with pytest.raises(workflow.SpotMarketOrderError) as error:
            workflow.submit_order(
                db=db,
                api_key="key",
                api_secret="secret",
                user_id="user-a",
                preview_token=preview["preview_token"],
                idempotency_key=preview["idempotency_key"],
            )
    assert error.value.code == "PRIOR_ORDER_RECONCILED"
    build_plan.assert_not_called()
    submit_market.assert_not_called()


def test_unknown_submit_outcome_reconciles_without_retry():
    session = _FakeSession()
    with patch(
        "app.services.monitor_spot_market_orders.build_market_order_plan", return_value=_plan()
    ):
        preview = workflow.create_preview(
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            symbol="ETHUSDT",
            side="BUY",
            quote_amount=Decimal("100"),
        )
        with (
            patch(
                "app.services.monitor_spot_market_orders.submit_market_order",
                side_effect=BinanceOrderError(
                    "Falha ao falar com a Binance.",
                    status_code=502,
                    outcome_unknown=True,
                ),
            ) as submit_mock,
            patch(
                "app.services.monitor_spot_market_orders.query_market_order",
                return_value=_filled_payload(),
            ) as query_mock,
        ):
            result = workflow.submit_order(
                db=session,
                api_key="key",
                api_secret="secret",
                user_id="user-a",
                preview_token=preview["preview_token"],
                idempotency_key=preview["idempotency_key"],
            )
    assert result["state"] == "filled"
    submit_mock.assert_called_once()
    query_mock.assert_called_once()


def test_terminal_rejection_replaces_stale_reconciliation_message():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="reconciling",
        result_summary={"message": "A Binance ainda está confirmando a operação."},
        created_at=now,
        updated_at=now,
    )
    result = workflow._apply_result(
        session,
        session.record,
        market.normalize_market_order_result(
            {
                "orderId": 42,
                "status": "REJECTED",
                "executedQty": "0",
                "cummulativeQuoteQty": "0",
            }
        ),
    )
    assert result["state"] == "rejected"
    assert result["message"] == "A Binance confirmou que a ordem não foi executada."


def test_repeated_order_not_found_after_grace_releases_never_submitted_record():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="submitting",
        submitting_account_identity_hash="a" * 64,
        result_summary={},
        created_at=now - timedelta(seconds=31),
        updated_at=now - timedelta(seconds=31),
    )
    with (
        patch(
            "app.services.monitor_spot_market_orders.query_market_order",
            side_effect=BinanceOrderError("Order does not exist", code=-2013),
        ) as query_mock,
        patch(
            "app.services.monitor_spot_market_orders.get_binance_account_identity_hash",
            return_value="a" * 64,
        ),
    ):
        first = workflow.get_order_status(
            db=session,
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
        second = workflow.get_order_status(
            db=session,
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
        third = workflow.get_order_status(
            db=session,
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )

    assert first["state"] == "reconciling"
    assert second["state"] == "reconciling"
    assert third["state"] == "rejected"
    assert third["error_code"] == "BINANCE_ORDER_NOT_FOUND"
    assert "nova prévia" in third["message"]
    assert "not_found_reconcile_count" not in session.record.result_summary
    # 3 observation queries + 1 final live verification before releasing the lock
    assert query_mock.call_count == 4


def test_order_not_found_terminal_runs_final_verification_and_records_fill():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="submitting",
        submitting_account_identity_hash="a" * 64,
        result_summary={},
        created_at=now - timedelta(seconds=31),
        updated_at=now - timedelta(seconds=31),
    )
    not_found = BinanceOrderError("Order does not exist", code=-2013)
    with (
        patch(
            "app.services.monitor_spot_market_orders.query_market_order",
            side_effect=[not_found, not_found, not_found, _filled_payload()],
        ) as query_mock,
        patch(
            "app.services.monitor_spot_market_orders.get_binance_account_identity_hash",
            return_value="a" * 64,
        ),
    ):
        workflow.get_order_status(
            db=session,
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
        workflow.get_order_status(
            db=session,
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
        final = workflow.get_order_status(
            db=session,
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
    assert query_mock.call_count == 4
    assert final["state"] == "filled"
    assert final["error_code"] is None
    assert session.record.state == "filled"


def test_terminal_state_is_never_regressed_by_concurrent_reconcile():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="filled",
        requested_quote_amount=Decimal("100"),
        executed_base_quantity=Decimal("0.05"),
        executed_quote_amount=Decimal("100"),
        average_price=Decimal("2000"),
        result_summary={"fees": [], "binance_status": "FILLED"},
        created_at=now,
        updated_at=now,
    )
    # A stale reconcile that would write `reconciling` must not overwrite `filled`.
    workflow._mark_reconciling(session, session.record)
    assert session.record.state == "filled"
    assert session.record.error_code is None

    # A stale apply of a not-found rejection must not regress the terminal state.
    result = workflow._handle_order_not_found(
        session,
        session.record,
        api_key="key",
        api_secret="secret",
    )
    assert result["state"] == "filled"
    assert session.record.state == "filled"


def test_repeated_query_errors_after_grace_release_lock_with_safe_message():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="submitting",
        submitting_account_identity_hash="a" * 64,
        result_summary={},
        created_at=now - timedelta(seconds=60),
        updated_at=now - timedelta(seconds=60),
    )
    rate_limited = BinanceOrderError("Too many requests", status_code=429, code=-1003)
    with patch(
        "app.services.monitor_spot_market_orders.query_market_order",
        side_effect=rate_limited,
    ):
        for _ in range(5):
            response = workflow.get_order_status(
                db=session,
                api_key="key",
                api_secret="secret",
                user_id="user-a",
                idempotency_key="existing-idempotency-key",
            )
    assert response["state"] == "rejected"
    assert response["error_code"] == "BINANCE_QUERY_FAILED"
    assert "query_error_count" not in session.record.result_summary
    assert session.record.state == "rejected"


def test_query_error_counter_resets_after_successful_reconcile():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="submitting",
        submitting_account_identity_hash="a" * 64,
        result_summary={},
        created_at=now - timedelta(seconds=60),
        updated_at=now - timedelta(seconds=60),
    )
    rate_limited = BinanceOrderError("Too many requests", status_code=429, code=-1003)
    with (
        patch(
            "app.services.monitor_spot_market_orders.query_market_order",
            side_effect=[rate_limited, _filled_payload()],
        ) as query_mock,
        patch(
            "app.services.monitor_spot_market_orders.get_binance_account_identity_hash",
            return_value="a" * 64,
        ),
    ):
        first = workflow.get_order_status(
            db=session,
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
        second = workflow.get_order_status(
            db=session,
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
    assert first["state"] == "reconciling"
    assert second["state"] == "filled"
    assert query_mock.call_count == 2
    assert "query_error_count" not in session.record.result_summary


def test_order_not_found_on_different_binance_account_keeps_request_locked():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="reconciling",
        submitting_account_identity_hash="a" * 64,
        error_code="ORDER_STATUS_UNKNOWN",
        result_summary={},
        created_at=now - timedelta(seconds=60),
        updated_at=now - timedelta(seconds=60),
    )
    with (
        patch(
            "app.services.monitor_spot_market_orders.query_market_order",
            side_effect=BinanceOrderError("Order does not exist", code=-2013),
        ),
        patch(
            "app.services.monitor_spot_market_orders.get_binance_account_identity_hash",
            return_value="b" * 64,
        ),
        pytest.raises(workflow.SpotMarketOrderError) as error,
    ):
        workflow.get_order_status(
            db=session,
            api_key="other-account-key",
            api_secret="other-account-secret",
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
    assert error.value.code == "BINANCE_ACCOUNT_CHANGED"
    assert session.record.state == "reconciling"
    assert session.record.error_code == "ORDER_STATUS_UNKNOWN"
    assert "not_found_reconcile_count" not in session.record.result_summary


def test_terminal_order_status_remains_readable_without_binance_credentials():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="filled",
        result_summary={"fees": [], "binance_status": "FILLED"},
        created_at=now,
        updated_at=now,
    )
    with patch("app.services.monitor_spot_market_orders.query_market_order") as query_mock:
        result = workflow.get_order_status(
            db=session,
            api_key=None,
            api_secret=None,
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
    assert result["state"] == "filled"
    query_mock.assert_not_called()


def test_unresolved_order_status_requires_binance_credentials_for_live_reconciliation():
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="reconciling",
        result_summary={},
    )
    with pytest.raises(workflow.SpotMarketOrderError) as error:
        workflow.get_order_status(
            db=session,
            api_key=None,
            api_secret=None,
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
    assert error.value.code == "BINANCE_CREDENTIALS_REQUIRED"


@pytest.mark.parametrize("code", [-2014, -2015, -1022])
def test_reconciliation_surfaces_credential_errors_without_releasing_order_lock(code):
    session = _FakeSession()
    session.record = MonitorSpotOrderRequest(
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
        client_order_id="cftrade_existing",
        symbol="ETHUSDT",
        side="BUY",
        state="reconciling",
        error_code="ORDER_STATUS_UNKNOWN",
        result_summary={},
    )
    with (
        patch(
            "app.services.monitor_spot_market_orders.query_market_order",
            side_effect=BinanceOrderError("Invalid credentials", status_code=403, code=code),
        ),
        pytest.raises(BinanceOrderError) as error,
    ):
        workflow.get_order_status(
            db=session,
            api_key="revoked-key",
            api_secret="revoked-secret",
            user_id="user-a",
            idempotency_key="existing-idempotency-key",
        )
    assert error.value.code == code
    assert session.record.state == "reconciling"
    assert session.record.error_code == "ORDER_STATUS_UNKNOWN"


def test_definitive_binance_rejection_is_persisted_without_sensitive_payload():
    session = _FakeSession()
    with patch(
        "app.services.monitor_spot_market_orders.build_market_order_plan", return_value=_plan()
    ):
        preview = workflow.create_preview(
            api_key="key",
            api_secret="secret",
            user_id="user-a",
            symbol="ETHUSDT",
            side="BUY",
            quote_amount=Decimal("100"),
        )
        with patch(
            "app.services.monitor_spot_market_orders.submit_market_order",
            side_effect=BinanceOrderError("Valor abaixo do mínimo", code=-1013),
        ):
            result = workflow.submit_order(
                db=session,
                api_key="key",
                api_secret="secret",
                user_id="user-a",
                preview_token=preview["preview_token"],
                idempotency_key=preview["idempotency_key"],
            )
    assert result["state"] == "rejected"
    assert result["error_code"] == "BINANCE_-1013"
    assert (
        result["message"]
        == "A Binance rejeitou a ordem por um filtro atualizado. Gere uma nova prévia."
    )
    serialized = str(result)
    assert "api_secret" not in serialized
    assert "signature" not in serialized
    assert "client_order_id" not in serialized


def test_route_requires_quote_only_for_buy():
    db = MagicMock()
    with pytest.raises(HTTPException) as buy_error:
        monitor_spot_market.post_spot_market_preview(
            monitor_spot_market.SpotMarketPreviewPayload(symbol="ETHUSDT", side="BUY"),
            current_user_id="u1",
            db=db,
        )
    assert buy_error.value.status_code == 422

    with pytest.raises(HTTPException) as sell_error:
        monitor_spot_market.post_spot_market_preview(
            monitor_spot_market.SpotMarketPreviewPayload(
                symbol="ETHUSDT", side="SELL", quote_amount_usdt=Decimal("10")
            ),
            current_user_id="u1",
            db=db,
        )
    assert sell_error.value.detail["code"] == "SELL_USES_FULL_BALANCE"


def test_route_uses_current_users_credentials():
    db = MagicMock()
    credential = SimpleNamespace(api_key="key", api_secret="secret")
    payload = monitor_spot_market.SpotMarketPreviewPayload(
        symbol="ETHUSDT", side="BUY", quote_amount_usdt=Decimal("10")
    )
    with (
        patch(
            "app.routes.monitor_spot_market.get_user_exchange_credential",
            return_value=credential,
        ) as get_credential,
        patch("app.routes.monitor_spot_market.create_preview", return_value={"side": "BUY"}),
    ):
        assert monitor_spot_market.post_spot_market_preview(
            payload, current_user_id="user-a", db=db
        ) == {"side": "BUY"}
    get_credential.assert_called_once_with(db, "user-a", "binance")


def test_status_route_reads_persisted_terminal_result_without_credentials():
    db = MagicMock()
    terminal = {"state": "filled"}
    with (
        patch(
            "app.routes.monitor_spot_market.get_user_exchange_credential",
            return_value=None,
        ),
        patch(
            "app.routes.monitor_spot_market.get_order_status",
            return_value=terminal,
        ) as status_mock,
    ):
        assert (
            monitor_spot_market.get_spot_market_order(
                "existing-idempotency-key",
                current_user_id="user-a",
                db=db,
            )
            == terminal
        )
    status_mock.assert_called_once_with(
        db=db,
        api_key=None,
        api_secret=None,
        user_id="user-a",
        idempotency_key="existing-idempotency-key",
    )


def test_route_never_exposes_raw_binance_transport_diagnostics():
    raw_error = BinanceOrderError(
        "proxy diagnostic containing apiKey=secret-value",
        status_code=400,
    )
    with pytest.raises(HTTPException) as error:
        monitor_spot_market._raise_service_error(raw_error)
    assert error.value.detail["message"] == (
        "A Binance recusou a solicitação. Revise os dados e gere uma nova prévia."
    )
    assert "secret-value" not in str(error.value.detail)


def test_model_has_user_scoped_idempotency_constraint():
    names = {constraint.name for constraint in MonitorSpotOrderRequest.__table__.constraints}
    assert "uq_monitor_spot_order_requests_user_key" in names
    assert "uq_monitor_spot_order_requests_client_order_id" in names
    index_names = {index.name for index in MonitorSpotOrderRequest.__table__.indexes}
    assert "uq_monitor_spot_order_requests_unresolved_symbol" in index_names
    assert MonitorSpotOrderRequest.__table__.c.submitting_account_identity_hash.nullable is False


def test_route_contract_is_additive_and_typed():
    routes = {
        (route.path, next(iter(route.methods))): route
        for route in monitor_spot_market.router.routes
    }
    assert (
        routes[("/api/monitor/spot-market-orders/preview", "POST")].response_model
        is monitor_spot_market.SpotMarketPreviewResponse
    )
    assert (
        routes[("/api/monitor/spot-market-orders", "POST")].response_model
        is monitor_spot_market.SpotMarketOrderResponse
    )
    assert (
        routes[("/api/monitor/spot-market-orders/{idempotency_key}", "GET")].response_model
        is monitor_spot_market.SpotMarketOrderResponse
    )
    assert (
        routes[("/api/monitor/spot-market-orders/eligibility", "POST")].response_model
        is monitor_spot_market.SpotMarketEligibilityResponse
    )

    preview_schema = monitor_spot_market.SpotMarketPreviewPayload.model_json_schema()
    assert preview_schema["properties"]["side"]["enum"] == ["BUY", "SELL"]
    assert "quote_amount_usdt" in preview_schema["properties"]
