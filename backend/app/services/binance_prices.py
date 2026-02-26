from __future__ import annotations

import json
import os
import urllib.request
from typing import Dict, Optional


def _get_env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def fetch_all_binance_prices() -> Dict[str, float]:
    """Fetch all Binance symbol prices (public endpoint).

    Returns a mapping like {"BTCUSDT": 50000.0, ...}

    Notes:
    - Uses the public endpoint `/api/v3/ticker/price` (no auth required).
    - Uses BINANCE_BASE_URL if set, otherwise https://api.binance.com.
    """

    base_url = _get_env("BINANCE_BASE_URL") or "https://api.binance.com"
    url = f"{base_url}/api/v3/ticker/price"
    req = urllib.request.Request(url)

    with urllib.request.urlopen(req, timeout=30) as f:
        data = json.load(f)

    out: Dict[str, float] = {}
    if isinstance(data, list):
        for row in data:
            sym = (row.get("symbol") or "").strip().upper()
            if not sym:
                continue
            try:
                out[sym] = float(row.get("price"))
            except Exception:
                continue

    return out


def _price(symbol_prices: Dict[str, float], symbol: str) -> Optional[float]:
    return symbol_prices.get(symbol.upper())


def compute_usdt_price_for_asset(asset: str, symbol_prices: Dict[str, float]) -> Optional[float]:
    """Compute an asset price in USDT using best-effort fallbacks.

    Strategy:
    1) If asset is USDT: 1
    2) Direct pair: ASSETUSDT
    3) Via BTC: ASSETBTC * BTCUSDT
    4) Fiat BRL: derive from USDTBRL (USD ~ USDT): BRLUSDT = 1 / USDTBRL

    Returns None if no pricing path is found.
    """

    a = (asset or "").strip().upper()
    if not a:
        return None

    if a == "USDT":
        return 1.0
    if a == "USDC":
        # Treat stablecoin as ~1 USDT for display.
        return 1.0

    direct = _price(symbol_prices, f"{a}USDT")
    if direct is not None:
        return direct

    # BRL special case (often quoted as USDTBRL)
    if a == "BRL":
        usdtbrl = _price(symbol_prices, "USDTBRL")
        if usdtbrl and usdtbrl > 0:
            return 1.0 / usdtbrl

    # Via BTC
    a_btc = _price(symbol_prices, f"{a}BTC")
    btc_usdt = _price(symbol_prices, "BTCUSDT")
    if a_btc is not None and btc_usdt is not None:
        return a_btc * btc_usdt

    return None
