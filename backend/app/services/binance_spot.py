from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from app.config import get_settings
from app.services.binance_prices import compute_usdt_price_for_asset, fetch_all_binance_prices
from app.services.binance_trades import (
    EARN_STABLE_PREFIX,
    compute_avg_buy_cost_usdt,
    is_usd_stable_asset,
)

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


def _earn_base_asset(asset: str) -> Optional[str]:
    """Return base asset for Binance Earn LD* wrappers (e.g. LDUSDC -> USDC)."""
    a = (asset or "").strip().upper()
    if not a.startswith(EARN_STABLE_PREFIX) or len(a) <= len(EARN_STABLE_PREFIX):
        return None
    base = a[len(EARN_STABLE_PREFIX) :]
    return base if is_usd_stable_asset(base) else None


def _fetch_simple_earn_positions(
    *,
    base_url: str,
    api_key: str,
    api_secret: str,
    timeout_s: int,
) -> Tuple[Dict[str, float], bool]:
    """Fetch Simple Earn flexible + locked positions aggregated by asset.

    Returns (amounts_by_asset, success). On failure returns ({}, False).
    """
    ts = int(time.time() * 1000)
    amounts: Dict[str, float] = {}

    for path in (
        "/sapi/v1/simple-earn/flexible/position",
        "/sapi/v1/simple-earn/locked/position",
    ):
        try:
            payload = _signed_get(
                base_url,
                api_key,
                api_secret,
                path,
                {"timestamp": ts, "size": 100},
                timeout_s=timeout_s,
            )
        except Exception:
            return {}, False

        if not isinstance(payload, dict):
            return {}, False

        for row in payload.get("rows") or []:
            asset = (row.get("asset") or "").strip().upper()
            if not asset:
                continue
            try:
                amount = float(row.get("totalAmount") or 0)
            except Exception:
                continue
            if amount <= 0:
                continue
            amounts[asset] = amounts.get(asset, 0.0) + amount

    return amounts, True


def _append_balance_row(
    out: List[Dict[str, Any]],
    *,
    asset: str,
    free: float,
    locked: float,
    total: float,
    price_usdt: float,
    value_usd: float,
) -> None:
    is_stable = is_usd_stable_asset(asset)
    out.append(
        {
            "asset": asset,
            "free": free,
            "locked": locked,
            "total": total,
            "price_usdt": price_usdt,
            "value_usd": value_usd,
            "avg_cost_usdt": 1.0 if is_stable else None,
            "pnl_usd": 0.0 if is_stable else None,
            "pnl_pct": 0.0 if is_stable else None,
        }
    )


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
    - Simple Earn flexible/locked positions are preferred over incomplete LD* wrappers
      on /api/v3/account when the Earn API succeeds.
    """

    api_key = (api_key or _get_env("BINANCE_API_KEY")).strip()
    api_secret = (api_secret or _get_env("BINANCE_API_SECRET")).strip()
    base_url = (base_url or _get_env("BINANCE_BASE_URL") or "https://api.binance.com").strip()

    if not api_key or not api_secret:
        raise BinanceConfigError(
            "Missing Binance credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET."
        )

    timeout_s = _clamp_int(_get_int_env("BINANCE_HTTP_TIMEOUT_SECONDS", 10), 1, 60)
    max_trade_symbols = _clamp_int(_get_int_env("BINANCE_MAX_TRADE_SYMBOLS", 15), 0, 200)
    trade_budget_s = _clamp_int(_get_int_env("BINANCE_TRADE_LOOKUPS_BUDGET_SECONDS", 15), 1, 120)

    ts = int(time.time() * 1000)
    as_of_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts / 1000.0))
    payload = _signed_get(
        base_url, api_key, api_secret, "/api/v3/account", {"timestamp": ts}, timeout_s=timeout_s
    )

    balances = payload.get("balances") or []

    earn_amounts, earn_ok = _fetch_simple_earn_positions(
        base_url=base_url,
        api_key=api_key,
        api_secret=api_secret,
        timeout_s=timeout_s,
    )
    earn_assets = set(earn_amounts.keys()) if earn_ok else set()

    symbol_prices = fetch_all_binance_prices()

    out: List[Dict[str, Any]] = []
    by_asset: Dict[str, Dict[str, Any]] = {}
    total_usd = 0.0

    MIN_USD_VALUE_TO_SHOW = float(min_usd) if min_usd is not None else 0.02

    for b in balances:
        asset = (b.get("asset") or "").strip().upper()
        if not asset:
            continue

        earn_base = _earn_base_asset(asset)
        if earn_ok and earn_base and earn_base in earn_assets:
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
        if price_usdt is None and is_usd_stable_asset(asset):
            price_usdt = 1.0
        value_usd = (total * price_usdt) if price_usdt is not None else None
        if value_usd is None:
            continue
        if float(value_usd) < MIN_USD_VALUE_TO_SHOW:
            continue

        total_usd += float(value_usd)
        _append_balance_row(
            out,
            asset=asset,
            free=free,
            locked=locked,
            total=total,
            price_usdt=float(price_usdt),
            value_usd=float(value_usd),
        )
        by_asset[asset] = out[-1]

    if earn_ok:
        for asset, amount in earn_amounts.items():
            if amount <= 0:
                continue

            price_usdt = compute_usdt_price_for_asset(asset, symbol_prices)
            if price_usdt is None and is_usd_stable_asset(asset):
                price_usdt = 1.0
            value_usd = (amount * price_usdt) if price_usdt is not None else None
            if value_usd is None:
                continue
            if float(value_usd) < MIN_USD_VALUE_TO_SHOW:
                continue

            total_usd += float(value_usd)
            if asset in by_asset:
                row = by_asset[asset]
                row["free"] = float(row["free"]) + amount
                row["total"] = float(row["total"]) + amount
                row["value_usd"] = float(row["value_usd"]) + float(value_usd)
            else:
                _append_balance_row(
                    out,
                    asset=asset,
                    free=amount,
                    locked=0.0,
                    total=amount,
                    price_usdt=float(price_usdt),
                    value_usd=float(value_usd),
                )
                by_asset[asset] = out[-1]

    out.sort(key=lambda x: -(float(x.get("value_usd") or 0.0)))

    lookups_started = time.time()
    trade_lookups = 0

    for row in out:
        if max_trade_symbols <= 0:
            break
        if trade_lookups >= max_trade_symbols:
            break
        if (time.time() - lookups_started) > float(trade_budget_s):
            break

        asset = str(row.get("asset") or "").strip().upper()
        if is_usd_stable_asset(asset):
            continue

        avg_cost_usdt = compute_avg_buy_cost_usdt(
            asset,
            lookback_days=lookback_days,
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url,
        )
        trade_lookups += 1
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

    def _sort_key(x: Dict[str, Any]):
        v = x.get("value_usd")
        v_sort = float(v) if v is not None else -1.0
        return (-v_sort, -float(x.get("total") or 0), str(x.get("asset") or ""))

    out.sort(key=_sort_key)
    return {"balances": out, "total_usd": total_usd, "as_of": as_of_iso}
