from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.services.binance_spot import BinanceConfigError, fetch_spot_balances_snapshot
from app.services.user_exchange_credentials import BINANCE_PROVIDER, get_user_exchange_credential

router = APIRouter(prefix="/api/external", tags=["external"])


@router.get("/binance/spot/balances")
def get_binance_spot_balances(
    lookback_days: Optional[int] = None,
    min_usd: Optional[float] = None,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return Binance Spot balances (read-only).

    Query params:
      - lookback_days (optional): limits trade-history used for avg cost (startTime).
      - min_usd (optional): dust threshold; hides positions with value_usd < min_usd.
        Default (when omitted): 0.02 (backward-compatible).
    """

    if lookback_days is not None:
        try:
            d = int(lookback_days)
        except Exception:
            raise HTTPException(status_code=400, detail="lookback_days must be an integer")
        if d <= 0 or d > 3650:
            raise HTTPException(status_code=400, detail="lookback_days must be between 1 and 3650")

    if min_usd is not None:
        try:
            v = float(min_usd)
        except Exception:
            raise HTTPException(status_code=400, detail="min_usd must be a number")
        if v < 0 or v > 1_000_000:
            raise HTTPException(status_code=400, detail="min_usd must be between 0 and 1000000")

    try:
        cred = get_user_exchange_credential(db, current_user_id, BINANCE_PROVIDER)
        if cred is None:
            raise HTTPException(status_code=503, detail="Binance credentials not configured for this user")
        return fetch_spot_balances_snapshot(
            lookback_days=lookback_days,
            min_usd=min_usd,
            api_key=cred.api_key,
            api_secret=cred.api_secret,
        )
    except HTTPException:
        raise
    except BinanceConfigError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Avoid leaking sensitive details; return a generic message.
        raise HTTPException(status_code=502, detail=f"Failed to fetch Binance balances: {e.__class__.__name__}")
