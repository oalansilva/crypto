"""Fixed per-side slippage by timeframe (card #1074)."""

from __future__ import annotations

from typing import Any

TRADING_FEE = 0.00075  # Binance spot 0.075% per side

# Timeframes in the Entra / Discovery table only.
TIMEFRAME_SLIPPAGE_PER_SIDE: dict[str, float] = {
    "1d": 0.0002,
    "4h": 0.0002,
    "1h": 0.0003,
    "15m": 0.0005,
}


def slippage_for_timeframe(timeframe: str | None) -> float:
    """Return per-side slippage for table timeframes; 0 for Combo-only intervals."""
    tf = str(timeframe or "").strip().lower()
    return TIMEFRAME_SLIPPAGE_PER_SIDE.get(tf, 0.0)


def fees_slippage_record(timeframe: str | None) -> dict[str, Any]:
    """JSON persisted on Discovery results and evidence fingerprints."""
    slip = slippage_for_timeframe(timeframe)
    return {
        "fees": TRADING_FEE,
        "slippage": slip,
        "fee_pct": TRADING_FEE,
        "slippage_pct": slip,
    }


def long_trade_profit_frac(
    entry_price: float,
    exit_price: float,
    *,
    fee: float = TRADING_FEE,
    slippage: float = 0.0,
) -> float:
    entry_eff = float(entry_price) * (1.0 + slippage)
    exit_eff = float(exit_price) * (1.0 - slippage)
    cost_basis = entry_eff * (1.0 + fee)
    if cost_basis <= 0:
        return 0.0
    return (exit_eff * (1.0 - fee) - cost_basis) / cost_basis


def short_trade_profit_frac(
    entry_price: float,
    exit_price: float,
    *,
    fee: float = TRADING_FEE,
    slippage: float = 0.0,
) -> float:
    entry_eff = float(entry_price) * (1.0 - slippage)
    exit_eff = float(exit_price) * (1.0 + slippage)
    proceeds = entry_eff * (1.0 - fee)
    if proceeds <= 0:
        return 0.0
    return (proceeds - exit_eff * (1.0 + fee)) / proceeds
