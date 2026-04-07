from __future__ import annotations

import pytest

from app.services import onchain_service


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


class _FakeClient:
    def __init__(self, payload_by_url):
        self._payload_by_url = payload_by_url

    async def get(self, url: str):
        return _FakeResponse(self._payload_by_url[url])


@pytest.mark.asyncio
async def test_defillama_tvl_matches_chain_by_name(monkeypatch):
    onchain_service._cache.clear()
    monkeypatch.setattr(
        onchain_service,
        "_get_onchain_client",
        lambda: _FakeClient(
            {
                "https://api.llama.fi/chains": [
                {"name": "Ethereum", "slug": "wrong-slug", "tvl": 108_000_000_000},
                ]
            }
        ),
    )

    tvl, active_addresses = await onchain_service._defillama_tvl("ethereum")

    assert tvl == 108_000_000_000
    assert active_addresses == 108_000_000_000


@pytest.mark.asyncio
async def test_fetch_binance_ranked_pairs_filters_and_sorts(monkeypatch):
    onchain_service._cache.clear()
    monkeypatch.setattr(
        onchain_service,
        "_get_onchain_client",
        lambda: _FakeClient(
            {
                "https://api.binance.com/api/v3/exchangeInfo": {
                    "symbols": [
                        {"symbol": "ETHUSDT", "baseAsset": "ETH", "quoteAsset": "USDT", "status": "TRADING", "isSpotTradingAllowed": True},
                        {"symbol": "SOLUSDT", "baseAsset": "SOL", "quoteAsset": "USDT", "status": "TRADING", "isSpotTradingAllowed": True},
                        {"symbol": "USDCUSDT", "baseAsset": "USDC", "quoteAsset": "USDT", "status": "TRADING", "isSpotTradingAllowed": True},
                    ]
                },
                "https://api.binance.com/api/v3/ticker/24hr": [
                    {"symbol": "SOLUSDT", "quoteVolume": "1200", "count": "50", "lastPrice": "150"},
                    {"symbol": "ETHUSDT", "quoteVolume": "2500", "count": "75", "lastPrice": "3200"},
                    {"symbol": "USDCUSDT", "quoteVolume": "999999", "count": "99", "lastPrice": "1"},
                ],
            }
        ),
    )

    pairs = await onchain_service._fetch_binance_ranked_pairs(limit=10)

    assert [pair.symbol for pair in pairs] == ["ETHUSDT", "SOLUSDT"]
    assert pairs[0].chain == "ethereum"
    assert pairs[1].chain == "solana"


@pytest.mark.asyncio
async def test_build_onchain_snapshot_applies_filters(monkeypatch):
    async def _fake_ranked_pairs(limit=onchain_service.MAX_SNAPSHOT_PAIRS):
        return [
            onchain_service.RankedPair("ETHUSDT", "ETH", "ethereum", 1000.0, 10, 3200.0),
            onchain_service.RankedPair("SOLUSDT", "SOL", "solana", 900.0, 9, 150.0),
        ]

    async def _fake_chain_metrics(chain):
        return {
            "tvl": 1_000_000.0,
            "active_addresses": 500_000.0,
            "exchange_flow": 50_000.0,
            "github": {"commits_30d": 100, "stars": 1000, "prs": 10, "issues": 50},
        }

    monkeypatch.setattr(
        onchain_service,
        "_fetch_binance_ranked_pairs",
        _fake_ranked_pairs,
    )
    monkeypatch.setattr(
        onchain_service,
        "_fetch_chain_metrics",
        _fake_chain_metrics,
    )

    snapshot = await onchain_service.build_onchain_snapshot(chain="solana", limit=10)

    assert len(snapshot) == 1
    pair, result = snapshot[0]
    assert pair.symbol == "SOLUSDT"
    assert result.metrics.token == "SOL"
