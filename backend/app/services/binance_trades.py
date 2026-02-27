from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional


def _get_env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def _get_int_env(name: str, default: int) -> int:
    raw = _get_env(name)
    if not raw:
        return int(default)
    try:
        return int(raw)
    except Exception:
        return int(default)


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(value)))


def _signed_get(
    api_key: str,
    api_secret: str,
    base_url: str,
    path: str,
    params: Dict[str, Any],
    *,
    timeout_s: int,
) -> Any:
    query = urllib.parse.urlencode(params)
    signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"{base_url}{path}?{query}&signature={signature}"

    req = urllib.request.Request(url)
    req.add_header("X-MBX-APIKEY", api_key)

    with urllib.request.urlopen(req, timeout=float(timeout_s)) as f:
        return json.load(f)


def fetch_my_trades(
    symbol: str,
    *,
    limit: int = 1000,
    lookback_days: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Fetch executed trades for a given symbol using Binance Spot myTrades.

    Safeguards:
    - HTTP timeout (env BINANCE_HTTP_TIMEOUT_SECONDS; default 10, clamped 1..60)
    - Optional lookback window (startTime), in days

    Notes:
    - Requires BINANCE_API_KEY / BINANCE_API_SECRET.
    - Binance returns trades in ascending order by time by default.
    """

    api_key = _get_env("BINANCE_API_KEY")
    api_secret = _get_env("BINANCE_API_SECRET")
    base_url = _get_env("BINANCE_BASE_URL") or "https://api.binance.com"

    if not api_key or not api_secret:
        return []

    timeout_s = _clamp_int(_get_int_env("BINANCE_HTTP_TIMEOUT_SECONDS", 10), 1, 60)

    ts = int(time.time() * 1000)

    params: Dict[str, Any] = {
        "symbol": symbol.upper(),
        "limit": int(limit),
        "timestamp": ts,
        "recvWindow": 5000,
    }

    if lookback_days is not None:
        try:
            days = int(lookback_days)
            if days > 0:
                # Clamp to avoid unrealistic ranges.
                days = _clamp_int(days, 1, 3650)
                params["startTime"] = ts - (days * 24 * 60 * 60 * 1000)
        except Exception:
            pass

    try:
        payload = _signed_get(
            api_key,
            api_secret,
            base_url,
            "/api/v3/myTrades",
            params,
            timeout_s=timeout_s,
        )
    except Exception:
        # If the key lacks trade-history permissions or the endpoint fails,
        # return empty to keep the wallet usable.
        return []

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


def compute_avg_buy_cost_usdt(asset: str, *, lookback_days: Optional[int] = None) -> Optional[float]:
    """Compute avg buy cost (USDT) for an asset using symbol ASSETUSDT (buys-only).

    lookback_days:
      - If set, limits trades fetched using Binance startTime to reduce API volume.
    """

    a = (asset or "").strip().upper()
    if not a:
        return None
    if a in {"USDT", "USDC", "BUSD", "TUSD"}:
        return 1.0

    symbol = f"{a}USDT"
    trades = fetch_my_trades(symbol, lookback_days=lookback_days)
    return compute_avg_buy_cost_usdt_for_symbol(symbol, trades)
