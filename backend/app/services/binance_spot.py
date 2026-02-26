from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List


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
      {"balances": [{"asset","free","locked","total"}, ...]}
    """

    api_key = _get_env("BINANCE_API_KEY")
    api_secret = _get_env("BINANCE_API_SECRET")
    base_url = _get_env("BINANCE_BASE_URL") or "https://api.binance.com"

    if not api_key or not api_secret:
        raise BinanceConfigError("Missing Binance credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET.")

    ts = int(time.time() * 1000)
    payload = _signed_get(base_url, api_key, api_secret, "/api/v3/account", {"timestamp": ts})

    balances = payload.get("balances") or []
    out: List[Dict[str, Any]] = []
    for b in balances:
        asset = (b.get("asset") or "").strip()
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
        out.append({"asset": asset, "free": free, "locked": locked, "total": total})

    # Default sort: total desc, then asset asc
    out.sort(key=lambda x: (-float(x.get("total") or 0), str(x.get("asset") or "")))
    return {"balances": out}
