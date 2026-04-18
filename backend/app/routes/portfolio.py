"""Portfolio KPIs — real data from Binance spot balances."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.services.binance_spot import BinanceConfigError, fetch_spot_balances_snapshot
from app.services.user_exchange_credentials import BINANCE_PROVIDER, get_user_exchange_credential

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


def _get_latest_snapshot(db: Session, user_id: str | None = None) -> Optional[Dict[str, Any]]:
    """Get the most recent portfolio snapshot for a user."""
    if user_id:
        result = db.execute(
            text(
                "SELECT * FROM portfolio_snapshots WHERE user_id = :user_id ORDER BY recorded_at DESC LIMIT 1"
            ),
            {"user_id": user_id},
        )
    else:
        result = db.execute(
            text("SELECT * FROM portfolio_snapshots ORDER BY recorded_at DESC LIMIT 1")
        )
    row = result.fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "recorded_at": row[1],
        "total_usd": row[2],
        "btc_value": row[3],
        "usdt_value": row[4],
        "eth_value": row[5],
        "other_usd": row[6],
        "pnl_today_pct": row[7],
        "drawdown_30d_pct": row[8],
        "drawdown_peak_date": row[9],
        "btc_change_24h_pct": row[10],
        "user_id": row[11] if len(row) > 11 else None,
    }


def _save_snapshot(
    db: Session,
    total_usd: float,
    btc_value: float,
    usdt_value: float,
    eth_value: float,
    other_usd: float,
    pnl_today_pct: Optional[float],
    drawdown_30d_pct: Optional[float],
    drawdown_peak_date: Optional[str],
    btc_change_24h_pct: Optional[float],
    user_id: str | None = None,
) -> int:
    """Save a portfolio snapshot and return its id."""
    result = db.execute(
        text("""
            INSERT INTO portfolio_snapshots
            (total_usd, btc_value, usdt_value, eth_value, other_usd,
             pnl_today_pct, drawdown_30d_pct, drawdown_peak_date, btc_change_24h_pct, user_id)
            VALUES (:total_usd, :btc_value, :usdt_value, :eth_value, :other_usd,
                    :pnl_today_pct, :drawdown_30d_pct, :drawdown_peak_date, :btc_change_24h_pct, :user_id)
            RETURNING id
        """),
        {
            "total_usd": total_usd,
            "btc_value": btc_value,
            "usdt_value": usdt_value,
            "eth_value": eth_value,
            "other_usd": other_usd,
            "pnl_today_pct": pnl_today_pct,
            "drawdown_30d_pct": drawdown_30d_pct,
            "drawdown_peak_date": drawdown_peak_date,
            "btc_change_24h_pct": btc_change_24h_pct,
            "user_id": user_id,
        },
    )
    db.commit()
    return int(result.scalar_one())


def _get_30d_snapshots(db: Session, user_id: str | None = None) -> List[Dict[str, Any]]:
    """Get snapshots from the last 30 days for drawdown calculation."""
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    if user_id:
        result = db.execute(
            text("""
                SELECT total_usd, recorded_at FROM portfolio_snapshots
                WHERE recorded_at >= :cutoff AND user_id = :user_id
                ORDER BY recorded_at ASC
            """),
            {"cutoff": cutoff, "user_id": user_id},
        )
    else:
        result = db.execute(
            text("""
                SELECT total_usd, recorded_at FROM portfolio_snapshots
                WHERE recorded_at >= :cutoff
                ORDER BY recorded_at ASC
            """),
            {"cutoff": cutoff},
        )
    rows = result.fetchall()
    return [{"total_usd": row[0], "recorded_at": row[1]} for row in rows]


def _calculate_drawdown_30d(snapshots: List[Dict[str, Any]]) -> tuple[float, Optional[str]]:
    """
    Calculate 30-day drawdown from snapshots.
    Returns (drawdown_pct, peak_date_str).
    """
    if not snapshots:
        return 0.0, None

    peak_value = max(s["total_usd"] for s in snapshots)
    latest_value = snapshots[-1]["total_usd"]

    if peak_value == 0:
        return 0.0, None

    drawdown_pct = ((latest_value - peak_value) / peak_value) * 100

    # Find peak date
    peak_date = None
    for s in snapshots:
        if s["total_usd"] == peak_value:
            peak_date = s["recorded_at"]
            break

    peak_date_str = None
    if peak_date:
        if isinstance(peak_date, str):
            peak_date_str = peak_date[:10]
        else:
            peak_date_str = peak_date.strftime("%Y-%m-%d")

    return round(drawdown_pct, 2), peak_date_str


@router.get("/kpi")
async def get_portfolio_kpi(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get portfolio KPIs with real data.

    Returns:
    {
        "pnl_today_pct": float or None,
        "pnl_today_vs_btc_pct": float or None,
        "drawdown_30d_pct": float,
        "drawdown_peak_date": str or None,
        "btc_change_24h_pct": float or None,
        "total_usd": float,
        "btc_value": float,
        "usdt_value": float,
        "eth_value": float,
        "other_usd": float,
        "_history_insufficient": bool,
    }
    """
    try:
        cred = get_user_exchange_credential(db, current_user_id, BINANCE_PROVIDER)
        if cred is None:
            raise HTTPException(
                status_code=503, detail="Binance credentials not configured for this user"
            )
        balances_data = fetch_spot_balances_snapshot(
            min_usd=0.01,
            api_key=cred.api_key,
            api_secret=cred.api_secret,
        )
    except BinanceConfigError:
        raise HTTPException(status_code=503, detail="Binance credentials not configured")
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to fetch Binance balances")

    # Extract values
    balances = balances_data.get("balances", [])
    total_usd = balances_data.get("total_usd", 0.0)

    btc_value = 0.0
    usdt_value = 0.0
    eth_value = 0.0
    other_usd = 0.0

    for b in balances:
        asset = b.get("asset", "")
        value = b.get("value_usd", 0.0) or 0.0
        if asset == "BTC":
            btc_value = value
        elif asset == "USDT" or asset == "BUSD":
            usdt_value = value
        elif asset == "ETH":
            eth_value = value
        else:
            other_usd += value

    # Get BTC 24h change
    btc_change_24h_pct = None
    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.binance.com/api/v3/ticker/24hr",
                params={"symbols": '["BTCUSDT"]'},
            )
            data = resp.json()
            if isinstance(data, dict) and data.get("symbol") == "BTCUSDT":
                pct = data.get("priceChangePercent")
                if pct is not None:
                    btc_change_24h_pct = float(pct)
    except Exception:
        pass

    # Get previous day's snapshot for PnL calculation
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    if current_user_id:
        prev_result = db.execute(
            text("""
                SELECT total_usd FROM portfolio_snapshots
                WHERE date(recorded_at) = :yesterday AND user_id = :user_id
                ORDER BY recorded_at DESC LIMIT 1
            """),
            {"yesterday": yesterday, "user_id": current_user_id},
        )
    else:
        prev_result = db.execute(
            text("""
                SELECT total_usd FROM portfolio_snapshots
                WHERE date(recorded_at) = :yesterday
                ORDER BY recorded_at DESC LIMIT 1
            """),
            {"yesterday": yesterday},
        )
    prev_row = prev_result.fetchone()
    prev_total = prev_row[0] if prev_row else None

    pnl_today_pct = None
    pnl_today_vs_btc_pct = None
    if prev_total and prev_total > 0:
        pnl_today_pct = round(((total_usd - prev_total) / prev_total) * 100, 2)
        if btc_change_24h_pct is not None:
            pnl_today_vs_btc_pct = round(pnl_today_pct - btc_change_24h_pct, 2)

    # Calculate 30d drawdown
    snapshots_30d = _get_30d_snapshots(db, user_id=current_user_id)
    drawdown_30d_pct, drawdown_peak_date = _calculate_drawdown_30d(snapshots_30d)

    # Save current snapshot
    _save_snapshot(
        db,
        total_usd=total_usd,
        btc_value=btc_value,
        usdt_value=usdt_value,
        eth_value=eth_value,
        other_usd=other_usd,
        pnl_today_pct=pnl_today_pct,
        drawdown_30d_pct=drawdown_30d_pct,
        drawdown_peak_date=drawdown_peak_date,
        btc_change_24h_pct=btc_change_24h_pct,
        user_id=current_user_id,
    )

    history_insufficient = len(snapshots_30d) < 2

    return {
        "pnl_today_pct": pnl_today_pct,
        "pnl_today_vs_btc_pct": pnl_today_vs_btc_pct,
        "drawdown_30d_pct": drawdown_30d_pct,
        "drawdown_peak_date": drawdown_peak_date,
        "btc_change_24h_pct": btc_change_24h_pct,
        "total_usd": round(total_usd, 2),
        "btc_value": round(btc_value, 2),
        "usdt_value": round(usdt_value, 2),
        "eth_value": round(eth_value, 2),
        "other_usd": round(other_usd, 2),
        "_history_insufficient": history_insufficient,
    }
