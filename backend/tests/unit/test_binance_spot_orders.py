from __future__ import annotations

import io
import json
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.routes import monitor_spot_stop
from app.services import binance_spot_orders as orders

SYMBOL_INFO = {
    "symbol": "ETHUSDT",
    "baseAsset": "ETH",
    "quoteAsset": "USDT",
    "filters": [
        {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
        {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
        {"filterType": "MIN_NOTIONAL", "minNotional": "5"},
    ],
}


def test_build_client_order_id_is_stable_and_prefixed():
    a = orders.build_client_order_id(user_id="u1", symbol="ethusdt", opportunity_id="42")
    b = orders.build_client_order_id(user_id="u1", symbol="ETHUSDT", opportunity_id="42")
    assert a == b
    assert a.startswith("cfstop_")
    assert len(a) <= 36


def test_normalize_symbol_and_split_base_quote():
    assert orders.normalize_symbol("eth/usdt") == "ETHUSDT"
    with pytest.raises(orders.BinanceOrderError):
        orders.normalize_symbol("***")
    base, quote = orders.split_base_quote(
        "ETHUSDT", {"symbols": [{"symbol": "ETHUSDT", "baseAsset": "ETH", "quoteAsset": "USDT"}]}
    )
    assert (base, quote) == ("ETH", "USDT")
    base2, quote2 = orders.split_base_quote("BTCUSDT", {"symbols": []})
    assert (base2, quote2) == ("BTC", "USDT")


def test_compute_order_prices_and_qty_applies_filters():
    stop, limit, qty = orders.compute_order_prices_and_qty(
        stop_price=100.019,
        free_qty=Decimal("1.2349"),
        symbol_info=SYMBOL_INFO,
    )
    assert stop == Decimal("100.01")
    assert limit == Decimal("99.90")
    assert qty == Decimal("1.234")


def test_compute_order_prices_rejects_dust_and_notional():
    with pytest.raises(orders.BinanceOrderError, match="Saldo free insuficiente"):
        orders.compute_order_prices_and_qty(
            stop_price=100.0,
            free_qty=Decimal("0.0001"),
            symbol_info=SYMBOL_INFO,
        )
    tiny = {
        "filters": [
            {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
            {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
            {"filterType": "MIN_NOTIONAL", "minNotional": "1000"},
        ]
    }
    with pytest.raises(orders.BinanceOrderError, match="Notional"):
        orders.compute_order_prices_and_qty(
            stop_price=10.0,
            free_qty=Decimal("1"),
            symbol_info=tiny,
        )


def test_format_and_floor_helpers():
    assert orders.format_decimal(Decimal("1.2300")) == "1.23"
    assert orders.decimal_floor(Decimal("1.239"), Decimal("0.01")) == Decimal("1.23")
    assert orders.decimal_floor(Decimal("1.2"), Decimal("0")) == Decimal("1.2")


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
@patch("app.services.binance_spot_orders.get_symbol_info", return_value=SYMBOL_INFO)
def test_place_protective_stop_posts_stop_loss_limit(_symbol_info, _find, _free, signed_request):
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
    assert kwargs["params"]["type"] == "STOP_LOSS_LIMIT"
    assert kwargs["params"]["side"] == "SELL"
    assert kwargs["params"]["newClientOrderId"].startswith("cfstop_")


@patch("app.services.binance_spot_orders.find_protective_order")
@patch("app.services.binance_spot_orders.get_symbol_info", return_value=SYMBOL_INFO)
def test_place_rejects_existing_protective(get_info, find):
    find.return_value = {"clientOrderId": "cfstop_x"}
    with pytest.raises(orders.BinanceOrderError, match="Já existe"):
        orders.place_protective_stop(
            api_key="k",
            api_secret="s",
            user_id="u",
            symbol="ETHUSDT",
            opportunity_id="1",
            stop_price=100.0,
        )


@patch("app.services.binance_spot_orders.signed_request")
@patch(
    "app.services.binance_spot_orders.find_protective_order",
    return_value={"orderId": 55, "clientOrderId": "cfstop_abc", "symbol": "ETHUSDT"},
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
    assert signed_request.call_args.kwargs["method"] == "DELETE"
    assert signed_request.call_args.kwargs["params"]["origClientOrderId"] == "cfstop_abc"


def test_cancel_ignores_non_cfstop_and_missing():
    with patch(
        "app.services.binance_spot_orders.find_protective_order",
        return_value={"orderId": 1, "clientOrderId": "manual-1"},
    ):
        with pytest.raises(orders.BinanceOrderError, match="não é protetiva"):
            orders.cancel_protective_stop(
                api_key="k", api_secret="s", user_id="u", symbol="ETHUSDT", opportunity_id="1"
            )
    with patch("app.services.binance_spot_orders.find_protective_order", return_value=None):
        with pytest.raises(orders.BinanceOrderError, match="Nenhuma ordem protetiva"):
            orders.cancel_protective_stop(
                api_key="k", api_secret="s", user_id="u", symbol="ETHUSDT", opportunity_id="1"
            )


@patch("app.services.binance_spot_orders.list_open_orders")
def test_find_and_status_protective_order(list_open):
    list_open.return_value = [
        {"clientOrderId": "other", "orderId": 1},
        {
            "clientOrderId": "cfstop_exact",
            "orderId": 2,
            "side": "SELL",
            "type": "STOP_LOSS_LIMIT",
            "status": "NEW",
            "stopPrice": "10",
            "price": "9.9",
            "origQty": "1",
        },
    ]
    found = orders.find_protective_order(
        api_key="k",
        api_secret="s",
        symbol="ETHUSDT",
        client_order_id="cfstop_exact",
    )
    assert found["orderId"] == 2
    with patch(
        "app.services.binance_spot_orders.find_protective_order",
        return_value=found,
    ):
        status = orders.get_protective_status(
            api_key="k",
            api_secret="s",
            user_id="u",
            symbol="ETHUSDT",
            opportunity_id="1",
        )
    assert status["protected"] is True
    assert status["order"]["quantity"] == 1.0

    list_open.return_value = [{"clientOrderId": "cfstop_other", "orderId": 9}]
    fallback = orders.find_protective_order(
        api_key="k", api_secret="s", symbol="ETHUSDT", client_order_id="cfstop_missing"
    )
    assert fallback["orderId"] == 9

    with patch("app.services.binance_spot_orders.find_protective_order", return_value=None):
        empty = orders.get_protective_status(
            api_key="k", api_secret="s", user_id="u", symbol="ETHUSDT", opportunity_id="1"
        )
    assert empty["protected"] is False


@patch("app.services.binance_spot_orders.signed_request")
def test_fetch_free_balance_and_list_open_orders(signed_request):
    signed_request.return_value = {
        "balances": [{"asset": "ETH", "free": "1.5", "locked": "0"}, {"asset": "BTC", "free": "0"}]
    }
    assert orders.fetch_free_balance(api_key="k", api_secret="s", asset="ETH") == Decimal("1.5")
    assert orders.fetch_free_balance(api_key="k", api_secret="s", asset="ADA") == Decimal("0")
    signed_request.return_value = [{"orderId": 1}]
    assert orders.list_open_orders(api_key="k", api_secret="s", symbol="ETHUSDT")[0]["orderId"] == 1
    signed_request.return_value = {"not": "a list"}
    assert orders.list_open_orders(api_key="k", api_secret="s", symbol="ETHUSDT") == []


@patch("app.services.binance_spot_orders.public_get")
def test_get_symbol_info(public_get):
    public_get.return_value = {"symbols": [SYMBOL_INFO]}
    assert orders.get_symbol_info("ETHUSDT")["baseAsset"] == "ETH"
    public_get.return_value = {"symbols": []}
    with pytest.raises(orders.BinanceOrderError, match="não encontrado"):
        orders.get_symbol_info("ETHUSDT")


@patch("urllib.request.urlopen")
def test_signed_request_success_and_http_errors(urlopen):
    ok = MagicMock()
    ok.read.return_value = b'{"ok": true}'
    ok.__enter__.return_value = ok
    ok.__exit__.return_value = False
    urlopen.return_value = ok
    assert orders.signed_request(
        method="GET", path="/api/v3/account", api_key="k", api_secret="s"
    ) == {"ok": True}

    err = type("E", (Exception,), {})()
    # HTTPError path
    import urllib.error

    http_err = urllib.error.HTTPError(
        url="http://x",
        code=400,
        msg="bad",
        hdrs=None,
        fp=io.BytesIO(json.dumps({"code": -2015, "msg": "Invalid API-key"}).encode()),
    )
    urlopen.side_effect = http_err
    with pytest.raises(orders.BinanceOrderError, match="Spot Trading"):
        orders.signed_request(method="POST", path="/api/v3/order", api_key="k", api_secret="s")

    urlopen.side_effect = RuntimeError("boom")
    with pytest.raises(orders.BinanceOrderError, match="Falha ao falar"):
        orders.signed_request(method="GET", path="/api/v3/account", api_key="k", api_secret="s")


@patch("urllib.request.urlopen")
def test_public_get(urlopen):
    ok = MagicMock()
    ok.read.return_value = b'{"symbols": []}'
    ok.__enter__.return_value = ok
    ok.__exit__.return_value = False
    urlopen.return_value = ok
    assert orders.public_get("/api/v3/exchangeInfo") == {"symbols": []}
    urlopen.side_effect = RuntimeError("x")
    with pytest.raises(orders.BinanceOrderError, match="exchangeInfo"):
        orders.public_get("/api/v3/exchangeInfo")


def test_require_creds_and_routes():
    db = MagicMock()
    with patch(
        "app.routes.monitor_spot_stop.get_user_exchange_credential",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc:
            monitor_spot_stop._require_user_binance_creds(db, "u1")
        assert exc.value.status_code == 400

    cred = SimpleNamespace(api_key="k", api_secret="s")
    with patch(
        "app.routes.monitor_spot_stop.get_user_exchange_credential",
        return_value=cred,
    ):
        assert monitor_spot_stop._require_user_binance_creds(db, "u1") is cred

    with pytest.raises(HTTPException) as exc2:
        monitor_spot_stop._raise_order_error(orders.BinanceOrderError("x", status_code=403))
    assert exc2.value.status_code == 403

    with (
        patch(
            "app.routes.monitor_spot_stop._require_user_binance_creds",
            return_value=cred,
        ),
        patch(
            "app.routes.monitor_spot_stop.get_protective_status",
            return_value={"protected": False},
        ),
    ):
        assert (
            monitor_spot_stop.get_spot_stop_order(
                symbol="ETHUSDT", opportunity_id="1", current_user_id="u1", db=db
            )["protected"]
            is False
        )

    with (
        patch(
            "app.routes.monitor_spot_stop._require_user_binance_creds",
            return_value=cred,
        ),
        patch(
            "app.routes.monitor_spot_stop.get_protective_status",
            side_effect=orders.BinanceOrderError("fail", status_code=400),
        ),
    ):
        with pytest.raises(HTTPException):
            monitor_spot_stop.get_spot_stop_order(
                symbol="ETHUSDT", opportunity_id="1", current_user_id="u1", db=db
            )

    payload = monitor_spot_stop.SpotStopPlacePayload(
        symbol="ETHUSDT", opportunity_id="1", stop_price=100.0, direction="long"
    )
    with (
        patch(
            "app.routes.monitor_spot_stop._require_user_binance_creds",
            return_value=cred,
        ),
        patch(
            "app.routes.monitor_spot_stop.place_protective_stop",
            return_value={"protected": True},
        ),
    ):
        assert (
            monitor_spot_stop.post_spot_stop_order(payload, current_user_id="u1", db=db)[
                "protected"
            ]
            is True
        )

    with (
        patch(
            "app.routes.monitor_spot_stop._require_user_binance_creds",
            return_value=cred,
        ),
        patch(
            "app.routes.monitor_spot_stop.place_protective_stop",
            side_effect=orders.BinanceOrderError("no", status_code=400),
        ),
    ):
        with pytest.raises(HTTPException):
            monitor_spot_stop.post_spot_stop_order(payload, current_user_id="u1", db=db)

    with (
        patch(
            "app.routes.monitor_spot_stop._require_user_binance_creds",
            return_value=cred,
        ),
        patch(
            "app.routes.monitor_spot_stop.cancel_protective_stop",
            return_value={"protected": False},
        ),
    ):
        assert (
            monitor_spot_stop.delete_spot_stop_order(
                symbol="ETHUSDT", opportunity_id="1", current_user_id="u1", db=db
            )["protected"]
            is False
        )

    with (
        patch(
            "app.routes.monitor_spot_stop._require_user_binance_creds",
            return_value=cred,
        ),
        patch(
            "app.routes.monitor_spot_stop.cancel_protective_stop",
            side_effect=orders.BinanceOrderError("no", status_code=400),
        ),
    ):
        with pytest.raises(HTTPException):
            monitor_spot_stop.delete_spot_stop_order(
                symbol="ETHUSDT", opportunity_id="1", current_user_id="u1", db=db
            )
