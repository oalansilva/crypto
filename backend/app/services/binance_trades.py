from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


def _get_env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def _signed_get(api_key: str, api_secret: str, base_url: str, path: str, params: Dict[str, Any]) -> Any:
    query = urllib.parse.urlencode(params)
    signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"{base_url}{path}?{query}&signature={signature}"

    req = urllib.request.Request(url)
    req.add_header("X-MBX-APIKEY", api_key)

    with urllib.request.urlopen(req, timeout=30) as f:
        return json.load(f)


def fetch_my_trades(symbol: str, limit: int = 1000) -> List[Dict[str, Any]]:
    """Fetch executed trades for a given symbol using Binance Spot myTrades.

    Notes:
    - Requires BINANCE_API_KEY / BINANCE_API_SECRET.
    - Binance returns trades in ascending order by time by default.
    """

    api_key = _get_env("BINANCE_API_KEY")
    api_secret = _get_env("BINANCE_API_SECRET")
    base_url = _get_env("BINANCE_BASE_URL") or "https://api.binance.com"

    if not api_key or not api_secret:
        return []

    ts = int(time.time() * 1000)
    payload = _signed_get(
        api_key,
        api_secret,
        base_url,
        "/api/v3/myTrades",
        {
            "symbol": symbol.upper(),
            "limit": int(limit),
            "timestamp": ts,
            "recvWindow": 5000,
        },
    )

    if isinstance(payload, list):
        return payload
    return []


def compute_avg_buy_cost_usdt_for_symbol(symbol: str, trades: List[Dict[str, Any]]) -> Optional[float]:
    """Compute weighted average buy cost from trades (buys only)."""

    qty_sum = 0.0
    notional_sum = 0.0

    for t in trades:
        # Binance myTrades returns isBuyer boolean.
        if not bool(t.get("isBuyer")):
            continue
        try:
            qty = float(t.get("qty") or 0)
            price = float(t.get("price") or 0)
        except Exception:
            continue
        if qty <= 0 or price <= 0:
            continue
        qty_sum += qty
        notional_sum += qty * price

    if qty_sum <= 0:
        return None

    return notional_sum / qty_sum


def compute_avg_buy_cost_usdt(asset: str) -> Optional[float]:
    """Compute avg buy cost (USDT) for an asset using symbol ASSETUSDT (buys-only)."""

    a = (asset or "").strip().upper()
    if not a:
        return None
    if a in {"USDT", "USDC", "BUSD", "TUSD"}:
        return 1.0

    symbol = f"{a}USDT"
    trades = fetch_my_trades(symbol)
    return compute_avg_buy_cost_usdt_for_symbol(symbol, trades)
