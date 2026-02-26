from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.binance_spot import BinanceConfigError, fetch_spot_balances_snapshot

router = APIRouter(prefix="/api/external", tags=["external"])


@router.get("/binance/spot/balances")
def get_binance_spot_balances():
    """Return Binance Spot balances (read-only)."""
    try:
        return fetch_spot_balances_snapshot()
    except BinanceConfigError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Avoid leaking sensitive details; return a generic message.
        raise HTTPException(status_code=502, detail=f"Failed to fetch Binance balances: {e.__class__.__name__}")
