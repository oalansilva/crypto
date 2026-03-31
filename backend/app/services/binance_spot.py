from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.services.binance_prices import compute_usdt_price_for_asset, fetch_all_binance_prices
from app.services.binance_trades import compute_avg_buy_cost_usdt

# Ensure .env files are loaded before runtime os.getenv lookups below.
get_settings()


class BinanceConfigError(RuntimeError):
    pass


def _get_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    return value


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
    base_url: str,
    api_key: str,
    api_secret: str,
    path: str,
    params: Dict[str, Any],
    *,
    timeout_s: int,
) -> Dict[str, Any]:
    query = urllib.parse.urlencode(params)
    signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"{base_url}{path}?{query}&signature={signature}"

    req = urllib.request.Request(url)
    req.add_header("X-MBX-APIKEY", api_key)

    with urllib.request.urlopen(req, timeout=float(timeout_s)) as f:
        return json.load(f)


def fetch_spot_balances_snapshot(
    *,
    lookback_days: Optional[int] = None,
    min_usd: Optional[float] = None,
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch Binance Spot balances using server-side env credentials.

    Env vars:
      - BINANCE_API_KEY
      - BINANCE_API_SECRET
      - BINANCE_BASE_URL (optional; default https://api.binance.com)

    Safeguards:
      - HTTP timeout (env BINANCE_HTTP_TIMEOUT_SECONDS; default 10, clamped 1..60)
      - Max symbols to query trade history for (env BINANCE_MAX_TRADE_SYMBOLS; default 15, clamped 0..200)
      - Total time budget for trade-history lookups (env BINANCE_TRADE_LOOKUPS_BUDGET_SECONDS; default 15, clamped 1..120)
      - Optional lookback window applied when deriving avg_cost_usdt

    Returns:
      {
        "balances": [{"asset","free","locked","total","price_usdt","value_usd"}, ...],
        "total_usd": <float>,
        "as_of": <iso8601 str>
      }

    Notes:
    - Pricing is computed as USDT value (USDT≈USD) with fallbacks.
    """

    api_key = (api_key or _get_env("BINANCE_API_KEY")).strip()
    api_secret = (api_secret or _get_env("BINANCE_API_SECRET")).strip()
    base_url = (base_url or _get_env("BINANCE_BASE_URL") or "https://api.binance.com").strip()

    if not api_key or not api_secret:
        raise BinanceConfigError("Missing Binance credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET.")

    timeout_s = _clamp_int(_get_int_env("BINANCE_HTTP_TIMEOUT_SECONDS", 10), 1, 60)
    max_trade_symbols = _clamp_int(_get_int_env("BINANCE_MAX_TRADE_SYMBOLS", 15), 0, 200)
    trade_budget_s = _clamp_int(_get_int_env("BINANCE_TRADE_LOOKUPS_BUDGET_SECONDS", 15), 1, 120)

    ts = int(time.time() * 1000)
    as_of_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts / 1000.0))
    payload = _signed_get(base_url, api_key, api_secret, "/api/v3/account", {"timestamp": ts}, timeout_s=timeout_s)

    balances = payload.get("balances") or []

    # Fetch all prices once (public endpoint) and compute USD values.
    symbol_prices = fetch_all_binance_prices()

    # Build the list first (cheap), then run trade-history lookups only for the most relevant items.
    out: List[Dict[str, Any]] = []
    total_usd = 0.0

    # Dust threshold (backward-compatible default): hide positions with value_usd < 0.02
    MIN_USD_VALUE_TO_SHOW = float(min_usd) if min_usd is not None else 0.02

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
            "avg_cost_usdt": None,
            "pnl_usd": None,
            "pnl_pct": None,
        })

    # Prefer spending limited trade-history calls on largest positions.
    out.sort(key=lambda x: -(float(x.get("value_usd") or 0.0)))

    lookups_started = time.time()

    for i, row in enumerate(out):
        if max_trade_symbols <= 0:
            break
        if i >= max_trade_symbols:
            break
        if (time.time() - lookups_started) > float(trade_budget_s):
            break

        asset = str(row.get("asset") or "").strip().upper()
        avg_cost_usdt = compute_avg_buy_cost_usdt(
            asset,
            lookback_days=lookback_days,
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url,
        )
        row["avg_cost_usdt"] = avg_cost_usdt

        price_usdt = row.get("price_usdt")
        total = float(row.get("total") or 0.0)

        pnl_usd = None
        pnl_pct = None
        if avg_cost_usdt is not None and price_usdt is not None and float(avg_cost_usdt) > 0:
            pnl_usd = (float(price_usdt) - float(avg_cost_usdt)) * float(total)
            pnl_pct = ((float(price_usdt) / float(avg_cost_usdt)) - 1.0) * 100.0

        row["pnl_usd"] = pnl_usd
        row["pnl_pct"] = pnl_pct

    # Default sort: value desc (when present), else total desc, then asset asc
    def _sort_key(x: Dict[str, Any]):
        v = x.get("value_usd")
        v_sort = float(v) if v is not None else -1.0
        return (-v_sort, -float(x.get("total") or 0), str(x.get("asset") or ""))

    out.sort(key=_sort_key)
    return {"balances": out, "total_usd": total_usd, "as_of": as_of_iso}
