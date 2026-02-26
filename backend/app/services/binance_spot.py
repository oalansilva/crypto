from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List

from app.services.binance_prices import compute_usdt_price_for_asset, fetch_all_binance_prices


class BinanceConfigError(RuntimeError):
    pass


def _get_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    return value


def _signed_get(base_url: str, api_key: str, api_secret: str, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    query = urllib.parse.urlencode(params)
    signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"{base_url}{path}?{query}&signature={signature}"

    req = urllib.request.Request(url)
    req.add_header("X-MBX-APIKEY", api_key)

    with urllib.request.urlopen(req, timeout=30) as f:
        return json.load(f)


def fetch_spot_balances_snapshot() -> Dict[str, Any]:
    """Fetch Binance Spot balances using server-side env credentials.

    Env vars:
      - BINANCE_API_KEY
      - BINANCE_API_SECRET
      - BINANCE_BASE_URL (optional; default https://api.binance.com)

    Returns:
      {
        "balances": [{"asset","free","locked","total","price_usdt","value_usd"}, ...],
        "total_usd": <float>
      }

    Notes:
    - Pricing is computed as USDT value (USDT≈USD) with fallbacks.
    """

    api_key = _get_env("BINANCE_API_KEY")
    api_secret = _get_env("BINANCE_API_SECRET")
    base_url = _get_env("BINANCE_BASE_URL") or "https://api.binance.com"

    if not api_key or not api_secret:
        raise BinanceConfigError("Missing Binance credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET.")

    ts = int(time.time() * 1000)
    payload = _signed_get(base_url, api_key, api_secret, "/api/v3/account", {"timestamp": ts})

    balances = payload.get("balances") or []

    # Fetch all prices once (public endpoint) and compute USD values.
    symbol_prices = fetch_all_binance_prices()

    out: List[Dict[str, Any]] = []
    total_usd = 0.0

    MIN_USD_VALUE_TO_SHOW = 0.02

    for b in balances:
        asset = (b.get("asset") or "").strip().upper()
        if not asset:
            continue
        try:
            free = float(b.get("free") or 0)
            locked = float(b.get("locked") or 0)
        except Exception:
            continue
        total = free + locked
        if total <= 0:
            continue

        price_usdt = compute_usdt_price_for_asset(asset, symbol_prices)
        value_usd = (total * price_usdt) if price_usdt is not None else None
        if value_usd is None:
            continue

        # Hide dust: do not include in response nor total
        if float(value_usd) < MIN_USD_VALUE_TO_SHOW:
            continue

        total_usd += float(value_usd)

        out.append({
            "asset": asset,
            "free": free,
            "locked": locked,
            "total": total,
            "price_usdt": price_usdt,
            "value_usd": value_usd,
        })

    # Default sort: value desc (when present), else total desc, then asset asc
    def _sort_key(x: Dict[str, Any]):
        v = x.get("value_usd")
        v_sort = float(v) if v is not None else -1.0
        return (-v_sort, -float(x.get("total") or 0), str(x.get("asset") or ""))

    out.sort(key=_sort_key)
    return {"balances": out, "total_usd": total_usd}
