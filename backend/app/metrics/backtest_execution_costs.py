"""Fixed per-side slippage by timeframe (card #1074)."""

from __future__ import annotations

import os
from typing import Any

TRADING_FEE = 0.00075  # Binance spot 0.075% per side

# Card #1119 (decisão 9): custo por classe. Cripto mantém 0,075% por lado. Ação/ETF usam a taxa da
# Binance Ações confirmada na tarefa 1.1 (24/10/2026), na página oficial de taxas de Stocks Trading
# (https://www.binance.com/en/fee/stocks): spread de negociação de 0,10% por ordem (padrão) e 0,05%
# promocional até 31/12/2026, para ordens a partir de US$ 340. O backtest usa o padrão (0,10%), que não
# depende da promoção; a taxa mínima por ordem (US$ 0,17) e a regra abaixo de US$ 340 não são
# simuladas (o capital da simulação é percentual).
EQUITY_FEE = 0.001
FEE_BY_CLASS: dict[str, tuple[float, bool]] = {
    "crypto": (TRADING_FEE, True),
    "stock": (EQUITY_FEE, True),
    "etf": (EQUITY_FEE, True),
}


def fee_for_class(asset_class: str | None) -> tuple[float, bool]:
    """(taxa por lado, confirmada?) da classe; classe desconhecida usa a de cripto."""
    return FEE_BY_CLASS.get(str(asset_class or "crypto").lower(), FEE_BY_CLASS["crypto"])


def fee_for_symbol(symbol: str | None) -> float:
    """Taxa por lado aplicada na simulação: par com ``/`` é cripto; ticker sem ``/`` é ação/ETF."""
    return fee_for_class("crypto" if "/" in str(symbol or "/") else "stock")[0]


def stop_gap_enabled() -> bool:
    """Interruptor ``STOP_GAP_EXIT`` (padrão ligado): só para rollback (decisão 6)."""
    return os.getenv("STOP_GAP_EXIT", "1").strip().lower() not in {"0", "false", "no", "off"}


STOP_EXIT_GAP_REASON = "stop_loss_gap"
STOP_EXIT_GAP_SIGNAL = "Stop com gap"


def gap_pct(stop_price: float, open_price: float) -> float:
    """Quanto a abertura passou do stop, em fração do stop (sempre positiva)."""
    if not stop_price:
        return 0.0
    return abs(float(open_price) - float(stop_price)) / abs(float(stop_price))


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


def fees_slippage_record(timeframe: str | None, asset_class: str | None = None) -> dict[str, Any]:
    """JSON persisted on Discovery results and evidence fingerprints.

    Card #1121 (decisão 11): a taxa é a da classe do resultado (cripto 0,075%; ação e ETF 0,10%),
    a mesma que a simulação aplicou. Sem classe, a de cripto (registro de antes).
    """
    fee = fee_for_class(asset_class)[0]
    slip = slippage_for_timeframe(timeframe)
    return {
        "fees": fee,
        "slippage": slip,
        "fee_pct": fee,
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
