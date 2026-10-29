"""Amostra fixa e casos da regressão cripto do card #1119 (tarefas 1.3 e 2.4).

BTC/USDT em 1d, 4h e 15m, 1 jan. a 31 dez. 2024 (Binance Spot, guardada em
``tests/fixtures/card_1119``). Os sinais saem de um cruzamento simples de médias
(a rotina de saída é que está sob teste); a execução é a mesma do otimizador.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "card_1119"
GOLDEN_BEFORE = FIXTURES / "regression_before.json"

STOPS = (0.015, 0.03)
DIRECTIONS = ("long", "short")
TIMEFRAMES = ("1d", "4h")
SLIPPAGE = {"1d": 0.0002, "4h": 0.0002}


def load(timeframe: str) -> pd.DataFrame:
    frame = pd.read_parquet(FIXTURES / f"btc_usdt_{timeframe}_2024.parquet")
    frame.index = pd.DatetimeIndex(frame.index)
    return frame


def with_signals(df: pd.DataFrame, direction: str, fast: int = 4, slow: int = 11) -> pd.DataFrame:
    """Entrada na abertura do candle seguinte ao cruzamento; saída no cruzamento contrário."""

    out = df.copy()
    fast_ma = out["close"].rolling(fast).mean()
    slow_ma = out["close"].rolling(slow).mean()
    up = ((fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))).fillna(False)
    down = ((fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))).fillna(False)
    enter, leave = (up, down) if direction == "long" else (down, up)
    signal = np.zeros(len(out), dtype=int)
    signal[1:][enter.to_numpy()[:-1]] = 1
    signal[1:][leave.to_numpy()[:-1] & ~enter.to_numpy()[:-1]] = -1
    out["signal"] = signal
    return out


def run_daily(extract: Callable[..., Any], timeframe: str, stop: float, direction: str) -> list:
    df = with_signals(load(timeframe), direction)
    return list(extract(df, stop, direction, SLIPPAGE[timeframe]))


def run_deep(simulate: Callable[..., Any], timeframe: str, stop: float, direction: str) -> list:
    df = with_signals(load(timeframe), direction)
    return list(simulate(df, load("15m"), stop, direction, SLIPPAGE[timeframe]))


def case_id(kind: str, timeframe: str, stop: float, direction: str) -> str:
    return f"{kind}|{timeframe}|{stop}|{direction}"


def all_cases() -> list[tuple[str, str, float, str]]:
    return [
        (kind, tf, stop, direction)
        for kind in ("daily", "deep")
        for tf in TIMEFRAMES
        for stop in STOPS
        for direction in DIRECTIONS
    ]


def run_case(case, extract: Callable[..., Any], simulate: Callable[..., Any]) -> list:
    kind, tf, stop, direction = case
    if kind == "daily":
        return run_daily(extract, tf, stop, direction)
    return run_deep(simulate, tf, stop, direction)


def jsonable(trades: list) -> list:
    return json.loads(json.dumps(trades, default=str))


def build_golden(extract, simulate) -> dict:
    return {case_id(*c): jsonable(run_case(c, extract, simulate)) for c in all_cases()}


if __name__ == "__main__":  # pragma: no cover - geração única, com a rotina ANTES do card
    from app.services.combo_optimizer import extract_trades_from_signals
    from app.services.deep_backtest import simulate_execution_with_15m

    golden = build_golden(extract_trades_from_signals, simulate_execution_with_15m)
    GOLDEN_BEFORE.write_text(json.dumps(golden, indent=0, sort_keys=True))
    print({k: len(v) for k, v in golden.items()})
