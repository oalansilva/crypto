from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException

import app.globals as app_globals
import app.routes.logs as logs_route
import app.routes.market as market_route
import app.routes.openspec as openspec_route
import app.services.binance_trades as binance_trades
import app.services.coordination_comments_service as coordination_comments_service


def test_globals_logs_and_coordination_comments_cover_file_paths(monkeypatch, tmp_path):
    assert app_globals.RUN_PROGRESS == {}

    log_file = tmp_path / "sample.log"
    log_file.write_text("line-1\nline-2\nline-3\n", encoding="utf-8")
    assert logs_route._tail_lines(log_file, 2) == "line-2\nline-3"
    assert logs_route._tail_lines(tmp_path / "missing.log", 5) == ""

    monkeypatch.setattr(logs_route, "LOG_MAP", {"custom": log_file})
    payload = logs_route.tail_log(name="custom", lines=2)
    assert payload["name"] == "custom"
    assert payload["content"] == "line-2\nline-3"

    with pytest.raises(HTTPException) as unknown_exc:
        logs_route.tail_log(name="unknown", lines=10)
    assert unknown_exc.value.status_code == 404

    coordination_root = tmp_path / "docs" / "coordination"
    coordination_root.mkdir(parents=True)
    (coordination_root / "coverage-ratchet.md").write_text("# Card\n", encoding="utf-8")
    monkeypatch.setattr(coordination_comments_service, "project_root", lambda: tmp_path)
    monkeypatch.setattr(
        coordination_comments_service,
        "coordination_dir",
        lambda: coordination_root,
    )

    with pytest.raises(FileNotFoundError):
        coordination_comments_service.list_comments("missing-change")

    with pytest.raises(ValueError, match="change_id must not be empty"):
        coordination_comments_service.add_comment("", "dev", "body")
    with pytest.raises(ValueError, match="author must not be empty"):
        coordination_comments_service.add_comment("coverage-ratchet", "", "body")
    with pytest.raises(ValueError, match="body must not be empty"):
        coordination_comments_service.add_comment("coverage-ratchet", "dev", "   ")
    with pytest.raises(ValueError, match="at most"):
        coordination_comments_service.add_comment(
            "coverage-ratchet",
            "dev",
            "x" * (coordination_comments_service.MAX_COMMENT_BODY_LEN + 1),
        )

    comments_file = tmp_path / "data" / "coordination_comments" / "coverage-ratchet.jsonl"
    comments_file.parent.mkdir(parents=True)
    comments_file.write_text("", encoding="utf-8")

    seeded = coordination_comments_service.list_comments("coverage-ratchet")
    assert len(seeded) == 1
    assert seeded[0]["author"] == "system"
    assert "Thread created" in seeded[0]["body"]

    comments_file.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "id": "2",
                        "change": "coverage-ratchet",
                        "author": "qa",
                        "created_at": "2026-04-18T10:00:00+00:00",
                        "body": "Later comment",
                    }
                ),
                "{broken json",
                json.dumps(
                    {
                        "id": "1",
                        "change": "coverage-ratchet",
                        "author": "dev",
                        "created_at": "2026-04-18T09:00:00+00:00",
                        "body": "Earlier comment",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    ordered = coordination_comments_service.list_comments("coverage-ratchet")
    assert [item["id"] for item in ordered] == ["1", "2"]

    created = coordination_comments_service.add_comment(
        "coverage-ratchet",
        "Alan",
        "Need QA evidence.",
    )
    assert created["author"] == "Alan"
    assert created["body"] == "Need QA evidence."
    assert "Need QA evidence." in comments_file.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_market_route_covers_normalization_cache_fetch_and_failures(monkeypatch):
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 4, 18, 22, 30, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(market_route, "datetime", FrozenDateTime)
    monkeypatch.setattr(market_route, "_DEFAULT_SYMBOLS", ("BTCUSDT", "ETHUSDT", "SOLUSDT"))
    monkeypatch.setattr(market_route, "is_running", lambda: False)
    market_route._PRICE_CACHE.clear()

    assert market_route._utc_now_iso() == "2026-04-18T22:30:00Z"
    assert market_route._normalize_symbols(None) == ("BTCUSDT", "ETHUSDT", "SOLUSDT")
    assert market_route._normalize_symbols(" btcusdt, ETHusdt,btcusdt ,, solusdt ") == (
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
    )
    assert market_route._coerce_float("12.5") == 12.5
    assert market_route._coerce_float("nan") is None
    assert market_route._coerce_float("bad") is None

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class FakeAsyncClient:
        def __init__(self, payload):
            self._payload = payload

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params):
            assert "ticker/24hr" in url
            assert params["symbols"].startswith("[")
            assert params["symbols"].endswith("]")
            return FakeResponse(self._payload)

    monkeypatch.setattr(
        market_route.httpx,
        "AsyncClient",
        lambda timeout: FakeAsyncClient(
            [
                {"symbol": "ETHUSDT", "lastPrice": "3500", "priceChangePercent": "2.5"},
                {"symbol": "BTCUSDT", "lastPrice": "64000", "priceChangePercent": "-1.2"},
                {"symbol": "BAD", "lastPrice": "oops", "priceChangePercent": "1"},
                {"symbol": "", "lastPrice": "1", "priceChangePercent": "1"},
            ]
        ),
    )
    fetched = await market_route._fetch_binance_prices(("BTCUSDT", "ETHUSDT"))
    assert [item["symbol"] for item in fetched["prices"]] == ["BTCUSDT", "ETHUSDT"]
    assert fetched["prices"][0]["price"] == 64000.0

    monkeypatch.setattr(
        market_route.httpx,
        "AsyncClient",
        lambda timeout: FakeAsyncClient(
            {"symbol": "BTCUSDT", "lastPrice": "1", "priceChangePercent": "2"}
        ),
    )
    single = await market_route._fetch_binance_prices(("BTCUSDT",))
    assert single["prices"] == [{"symbol": "BTCUSDT", "price": 1.0, "change_24h_pct": 2.0}]

    monkeypatch.setattr(
        market_route.httpx,
        "AsyncClient",
        lambda timeout: FakeAsyncClient("bad-payload"),
    )
    with pytest.raises(ValueError, match="Unexpected Binance payload format"):
        await market_route._fetch_binance_prices(("BTCUSDT",))

    now_holder = {"value": 1000.0}
    monkeypatch.setattr(market_route.time, "time", lambda: now_holder["value"])
    market_route._PRICE_CACHE.clear()
    market_route._write_cache(
        ("BTCUSDT",),
        {"prices": [{"symbol": "BTCUSDT", "price": 100.0}], "fetched_at": "now"},
    )
    assert market_route._read_cache(("BTCUSDT",)) == {
        "prices": [{"symbol": "BTCUSDT", "price": 100.0}],
        "fetched_at": "now",
    }
    now_holder["value"] = 2000.0
    assert market_route._read_cache(("BTCUSDT",)) is None

    async def fake_fetch(symbols):
        return {
            "prices": [{"symbol": symbols[0], "price": 42.0, "change_24h_pct": 3.0}],
            "fetched_at": "2026-04-18T22:30:00Z",
        }

    monkeypatch.setattr(market_route, "_fetch_binance_prices", fake_fetch)
    market_route._PRICE_CACHE.clear()
    first = await market_route.get_market_prices("BTCUSDT")
    second = await market_route.get_market_prices("BTCUSDT")
    assert first == second

    async def failing_fetch(symbols):
        raise RuntimeError("binance unavailable")

    monkeypatch.setattr(market_route, "_fetch_binance_prices", failing_fetch)
    market_route._PRICE_CACHE.clear()
    failed = await market_route.get_market_prices("BTCUSDT")
    assert failed == {"prices": [], "fetched_at": None}


@pytest.mark.asyncio
async def test_openspec_routes_cover_listing_normalization_and_artifact_resolution(
    monkeypatch, tmp_path
):
    specs_dir = tmp_path / "openspec" / "specs"
    changes_dir = tmp_path / "openspec" / "changes"
    specs_dir.mkdir(parents=True)
    changes_dir.mkdir(parents=True)

    spec_a = specs_dir / "backend" / "alpha.md"
    spec_a.parent.mkdir(parents=True)
    spec_a.write_text(
        "---\ntitle: Alpha Spec\nstatus: draft\nupdated_at: 2026-04-18\n---\n# Alpha\n",
        encoding="utf-8",
    )
    spec_b = specs_dir / "crypto.lab.langgraph.studio.v1.md"
    spec_b.write_text("# Dot Spec\n", encoding="utf-8")
    spec_a.touch()
    spec_b.touch()

    monkeypatch.setattr(openspec_route, "_specs_dir", lambda: specs_dir)
    monkeypatch.setattr(openspec_route, "_changes_dir", lambda: changes_dir)

    assert openspec_route._normalize_spec_id(" backend/alpha.md ") == ["backend", "alpha"]
    assert openspec_route._normalize_spec_id("crypto.lab.langgraph.studio.v1") == [
        "crypto.lab.langgraph.studio.v1"
    ]
    with pytest.raises(HTTPException):
        openspec_route._normalize_spec_id("../escape")
    with pytest.raises(HTTPException):
        openspec_route._normalize_spec_id("bad path")

    assert openspec_route._parse_frontmatter(spec_a.read_text(encoding="utf-8")) == {
        "title": "Alpha Spec",
        "status": "draft",
        "updated_at": "2026-04-18",
    }
    assert openspec_route._parse_frontmatter("# No frontmatter\n") == {}

    listed = await openspec_route.list_specs()
    assert {item.id for item in listed.items} == {"backend/alpha", "crypto.lab.langgraph.studio.v1"}
    alpha_item = next(item for item in listed.items if item.id == "backend/alpha")
    assert alpha_item.title == "Alpha Spec"
    assert alpha_item.status == "draft"

    loaded = await openspec_route.get_spec("crypto.lab.langgraph.studio.v1")
    assert loaded.id == "crypto.lab.langgraph.studio.v1"
    assert loaded.markdown == "# Dot Spec\n"

    with pytest.raises(HTTPException) as missing_spec_exc:
        await openspec_route.get_spec("missing/spec")
    assert missing_spec_exc.value.status_code == 404

    with pytest.raises(HTTPException) as bad_change_exc:
        await openspec_route.get_change_artifact("bad id", "proposal")
    assert bad_change_exc.value.status_code == 400

    with pytest.raises(HTTPException) as bad_artifact_exc:
        await openspec_route.get_change_artifact("coverage-ratchet", "unknown")
    assert bad_artifact_exc.value.status_code == 404

    change_dir = changes_dir / "coverage-ratchet"
    (change_dir / "prototype").mkdir(parents=True)
    (change_dir / "proposal.md").write_text("# Proposal\n", encoding="utf-8")
    (change_dir / "prototype" / "prototype.html").write_text(
        "<html>prototype</html>", encoding="utf-8"
    )

    proposal = await openspec_route.get_change_artifact("coverage-ratchet", "proposal")
    assert proposal.markdown == "# Proposal\n"

    prototype = await openspec_route.get_change_artifact("coverage-ratchet", "prototype")
    assert prototype.markdown == "<html>prototype</html>"

    with pytest.raises(HTTPException) as missing_artifact_exc:
        await openspec_route.get_change_artifact("coverage-ratchet", "design")
    assert missing_artifact_exc.value.status_code == 404


def test_binance_trades_helpers_and_trade_filters(monkeypatch):
    monkeypatch.setenv("BINANCE_API_KEY", " key ")
    monkeypatch.setenv("BINANCE_API_SECRET", " secret ")
    monkeypatch.setenv("BINANCE_BASE_URL", " https://example.invalid ")
    monkeypatch.setenv("BINANCE_HTTP_TIMEOUT_SECONDS", "not-an-int")

    assert binance_trades._get_env("BINANCE_API_KEY") == "key"
    assert binance_trades._get_int_env("BINANCE_HTTP_TIMEOUT_SECONDS", 10) == 10
    assert binance_trades._clamp_int(-3, 1, 60) == 1

    captured_request: dict[str, object] = {}

    class JsonResponse(io.StringIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(req, timeout):
        captured_request["url"] = req.full_url
        captured_request["headers"] = dict(req.header_items())
        captured_request["timeout"] = timeout
        return JsonResponse('{"ok": true}')

    monkeypatch.setattr(binance_trades.urllib.request, "urlopen", fake_urlopen)
    signed = binance_trades._signed_get(
        "key",
        "secret",
        "https://example.invalid",
        "/api/v3/myTrades",
        {"symbol": "BTCUSDT", "timestamp": 1},
        timeout_s=9,
    )
    assert signed == {"ok": True}
    assert "signature=" in str(captured_request["url"])
    assert dict(captured_request["headers"]).get("X-mbx-apikey") == "key"
    assert captured_request["timeout"] == 9.0

    monkeypatch.delenv("BINANCE_API_KEY", raising=False)
    monkeypatch.delenv("BINANCE_API_SECRET", raising=False)
    assert binance_trades.fetch_my_trades("BTCUSDT") == []

    monkeypatch.setattr(binance_trades, "_signed_get", lambda *args, **kwargs: {"not": "a-list"})
    assert (
        binance_trades.fetch_my_trades(
            "BTCUSDT",
            api_key="key",
            api_secret="secret",
            base_url="https://example.invalid",
        )
        == []
    )

    def failing_signed_get(*args, **kwargs):
        raise RuntimeError("binance down")

    monkeypatch.setattr(binance_trades, "_signed_get", failing_signed_get)
    assert (
        binance_trades.fetch_my_trades(
            "BTCUSDT",
            api_key="key",
            api_secret="secret",
            base_url="https://example.invalid",
        )
        == []
    )

    monkeypatch.setattr(binance_trades.time, "time", lambda: 1_700_000_000.0)
    monkeypatch.setattr(
        binance_trades,
        "_signed_get",
        lambda *args, **kwargs: [
            {"time": 1_699_999_999_000, "isBuyer": True, "qty": "1", "price": "10"},
            {"time": 1_699_000_000_000, "isBuyer": True, "qty": "1", "price": "9"},
            {"time": "broken", "isBuyer": True, "qty": "1", "price": "8"},
        ],
    )
    filtered = binance_trades.fetch_my_trades(
        "ethusdt",
        lookback_days=1,
        api_key="key",
        api_secret="secret",
        base_url="https://example.invalid",
    )
    assert len(filtered) == 1
    assert filtered[0]["price"] == "10"

    unfiltered = binance_trades.fetch_my_trades(
        "ethusdt",
        lookback_days="not-a-number",
        api_key="key",
        api_secret="secret",
        base_url="https://example.invalid",
    )
    assert len(unfiltered) == 3

    assert (
        binance_trades.compute_avg_buy_cost_usdt_for_symbol(
            "BTCUSDT",
            [
                {"isBuyer": False, "qty": "1", "price": "10", "time": 1},
                {"isBuyer": True, "qty": "0", "price": "10", "time": 2},
                {"isBuyer": True, "qty": "1", "price": "bad", "time": 3},
            ],
        )
        is None
    )
    assert (
        binance_trades.compute_avg_buy_cost_usdt_for_symbol(
            "BTCUSDT",
            [
                {"isBuyer": True, "qty": "1", "price": "10"},
                {"isBuyer": True, "qty": "1", "price": "12", "time": "bad"},
            ],
        )
        == 12.0
    )

    assert binance_trades.compute_avg_buy_cost_usdt("") is None
    assert binance_trades.compute_avg_buy_cost_usdt("usdt") == 1.0
    assert binance_trades.compute_avg_buy_cost_usdt("busd") == 1.0

    fetch_calls: list[tuple[str, object]] = []

    def fake_fetch(symbol, **kwargs):
        fetch_calls.append((symbol, kwargs["lookback_days"]))
        return [{"isBuyer": True, "qty": "1", "price": "25", "time": 1}]

    monkeypatch.setattr(binance_trades, "fetch_my_trades", fake_fetch)
    assert (
        binance_trades.compute_avg_buy_cost_usdt(
            "sol",
            lookback_days=30,
            api_key="key",
            api_secret="secret",
            base_url="https://example.invalid",
        )
        == 25.0
    )
    assert fetch_calls == [("SOLUSDT", 30)]
