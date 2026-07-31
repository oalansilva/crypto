from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

import pytest

from app.services import binance_spot_orders as orders


def test_build_client_order_id_is_stable_and_prefixed():
    a = orders.build_client_order_id(user_id="u1", symbol="ethusdt", opportunity_id="42")
    b = orders.build_client_order_id(user_id="u1", symbol="ETHUSDT", opportunity_id="42")
    assert a == b
    assert a.startswith("cfstop_")
    assert len(a) <= 36


def test_compute_order_prices_and_qty_applies_filters():
    symbol_info = {
        "filters": [
            {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
            {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
            {"filterType": "MIN_NOTIONAL", "minNotional": "10"},
        ]
    }
    stop, limit, qty = orders.compute_order_prices_and_qty(
        stop_price=100.019,
        free_qty=Decimal("1.2349"),
        symbol_info=symbol_info,
    )
    assert stop == Decimal("100.01")
    assert limit == Decimal("99.90")  # 100.01 * 0.999 floored to tick
    assert qty == Decimal("1.234")


def test_compute_order_prices_rejects_dust():
    symbol_info = {
        "filters": [
            {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
            {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.01"},
            {"filterType": "MIN_NOTIONAL", "minNotional": "10"},
        ]
    }
    with pytest.raises(orders.BinanceOrderError, match="Saldo free insuficiente"):
        orders.compute_order_prices_and_qty(
            stop_price=100.0,
            free_qty=Decimal("0.001"),
            symbol_info=symbol_info,
        )


def test_place_rejects_short():
    with pytest.raises(orders.BinanceOrderError, match="apenas para long"):
        orders.place_protective_stop(
            api_key="k",
            api_secret="s",
            user_id="u1",
            symbol="ETHUSDT",
            opportunity_id="1",
            stop_price=100.0,
            direction="short",
        )


@patch("app.services.binance_spot_orders.signed_request")
@patch("app.services.binance_spot_orders.fetch_free_balance", return_value=Decimal("2"))
@patch("app.services.binance_spot_orders.find_protective_order", return_value=None)
@patch(
    "app.services.binance_spot_orders.get_symbol_info",
    return_value={
        "symbol": "ETHUSDT",
        "baseAsset": "ETH",
        "quoteAsset": "USDT",
        "filters": [
            {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
            {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
            {"filterType": "MIN_NOTIONAL", "minNotional": "5"},
        ],
    },
)
def test_place_protective_stop_posts_stop_loss_limit(
    _symbol_info, _find, _free, signed_request
):
    signed_request.return_value = {"orderId": 99, "status": "NEW"}
    result = orders.place_protective_stop(
        api_key="k",
        api_secret="s",
        user_id="user-a",
        symbol="ETHUSDT",
        opportunity_id="77",
        stop_price=2000.0,
        direction="long",
    )
    assert result["protected"] is True
    assert result["order_id"] == 99
    assert result["quantity"] == 2.0
    kwargs = signed_request.call_args.kwargs
    assert kwargs["method"] == "POST"
    assert kwargs["path"] == "/api/v3/order"
    assert kwargs["params"]["type"] == "STOP_LOSS_LIMIT"
    assert kwargs["params"]["side"] == "SELL"
    assert kwargs["params"]["newClientOrderId"].startswith("cfstop_")


@patch("app.services.binance_spot_orders.signed_request")
@patch(
    "app.services.binance_spot_orders.find_protective_order",
    return_value={
        "orderId": 55,
        "clientOrderId": "cfstop_abc",
        "symbol": "ETHUSDT",
    },
)
def test_cancel_protective_stop_uses_orig_client_order_id(_find, signed_request):
    signed_request.return_value = {"orderId": 55, "status": "CANCELED"}
    result = orders.cancel_protective_stop(
        api_key="k",
        api_secret="s",
        user_id="user-a",
        symbol="ETHUSDT",
        opportunity_id="77",
    )
    assert result["protected"] is False
    kwargs = signed_request.call_args.kwargs
    assert kwargs["method"] == "DELETE"
    assert kwargs["params"]["origClientOrderId"] == "cfstop_abc"


def test_cancel_ignores_non_cfstop_orders():
    with patch(
        "app.services.binance_spot_orders.find_protective_order",
        return_value={"orderId": 1, "clientOrderId": "manual-1"},
    ):
        with pytest.raises(orders.BinanceOrderError, match="não é protetiva"):
            orders.cancel_protective_stop(
                api_key="k",
                api_secret="s",
                user_id="u",
                symbol="ETHUSDT",
                opportunity_id="1",
            )
