from __future__ import annotations

import pytest

from app.services import onchain_service


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


class _FakeClient:
    def __init__(self, payload):
        self._payload = payload

    async def get(self, url: str):
        return _FakeResponse(self._payload)


@pytest.mark.asyncio
async def test_defillama_tvl_matches_chain_by_name(monkeypatch):
    onchain_service._cache.clear()
    monkeypatch.setattr(
        onchain_service,
        "_get_onchain_client",
        lambda: _FakeClient(
            [
                {"name": "Ethereum", "slug": "wrong-slug", "tvl": 108_000_000_000},
            ]
        ),
    )

    tvl, active_addresses = await onchain_service._defillama_tvl("ethereum")

    assert tvl == 108_000_000_000
    assert active_addresses == 108_000_000_000
