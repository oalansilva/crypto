#!/usr/bin/env python3
"""Binance Spot snapshot (balances) via API.

Usage:
  BINANCE_API_KEY=... BINANCE_API_SECRET=... python3 scripts/binance_spot_snapshot.py

Notes:
- Requires read-only API key.
- If you use IP whitelist, run from the whitelisted host.
"""

import os
import time
import hmac
import hashlib
import urllib.parse
import urllib.request
import json

BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

if not API_KEY or not API_SECRET:
    raise SystemExit("Missing BINANCE_API_KEY or BINANCE_API_SECRET env vars")


def signed_request(path: str, params: dict):
    query = urllib.parse.urlencode(params)
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"{BASE_URL}{path}?{query}&signature={signature}"
    req = urllib.request.Request(url)
    req.add_header("X-MBX-APIKEY", API_KEY)
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.load(f)


def main():
    ts = int(time.time() * 1000)
    account = signed_request("/api/v3/account", {"timestamp": ts})

    balances = account.get("balances", [])
    out = []
    for b in balances:
        asset = b.get("asset")
        free = float(b.get("free", 0) or 0)
        locked = float(b.get("locked", 0) or 0)
        total = free + locked
        if total <= 0:
            continue
        out.append({"asset": asset, "free": free, "locked": locked, "total": total})

    out.sort(key=lambda x: x["asset"])
    print(json.dumps({"balances": out}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
