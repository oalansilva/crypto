from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from app.services.binance_spot import BinanceConfigError, fetch_spot_balances_snapshot

router = APIRouter(prefix="/api/external", tags=["external"])


@router.get("/binance/spot/balances")
def get_binance_spot_balances(lookback_days: Optional[int] = None):
    """Return Binance Spot balances (read-only).

    Query params:
      - lookback_days (optional): limits trade-history used for avg cost (startTime).
    """

    if lookback_days is not None:
        try:
            d = int(lookback_days)
        except Exception:
            raise HTTPException(status_code=400, detail="lookback_days must be an integer")
        if d <= 0 or d > 3650:
            raise HTTPException(status_code=400, detail="lookback_days must be between 1 and 3650")

    try:
        return fetch_spot_balances_snapshot(lookback_days=lookback_days)
    except BinanceConfigError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Avoid leaking sensitive details; return a generic message.
        raise HTTPException(status_code=502, detail=f"Failed to fetch Binance balances: {e.__class__.__name__}")
