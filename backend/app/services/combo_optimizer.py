"""
Combo Strategy Optimizer

Hybrid Grid Optimization Strategy:
Combines Grid Search for correlated parameters with Sequential Optimization for independent ones.

Features:
- Hybrid Stage Generation: Automatically identifies correlated groups (e.g., [media_curta, media_inter, media_longa]) and generates joint Grid Search stages.
- Single Round Execution: Disables iterative refinement (max_rounds=1) when Grid Search is active to avoid local maximum traps.
- Parallel Execution: Uses ProcessPoolExecutor for both Sequential (single parameter) and Grid (multi-parameter) tests.
- Deep Backtesting: Integrated simulation for precision testing using 15m intraday data.
"""

import json
import concurrent.futures
import multiprocessing
import hashlib
import os
import time
import logging
import uuid
from functools import partial
import itertools  # For Grid Search cartesian product
from typing import Dict, List, Any, Optional
from pathlib import Path
import numpy as np
import pandas as pd

# Log 15m coverage warning only once per symbol per process (avoids thousands of identical lines)
_deep_coverage_warned: set = set()

from app.services.discovery_budget_cache import Cache, BUDGET, bounded_execution
from app.services.discovery_resources import ResourceProfile, CalculationFailure, track_pool
from app.services.discovery_stream import ResultSpool, execute_stream, report
from app.services.combo_service import ComboService
from app.services.market_data_providers import (
    BINANCE_EQUITY_SOURCE,
    get_market_data_provider,
    resolve_data_source_for_symbol,
    validate_data_source_timeframe,
)
from src.data.incremental_loader import IncrementalLoader
from app.services.market_history.sample import ACTIVE_SAMPLE_ID, ExecutionSample
from app.metrics.backtest_execution_costs import (
    STOP_EXIT_GAP_REASON,
    STOP_EXIT_GAP_SIGNAL,
    TRADING_FEE,
    fee_for_symbol,
    gap_pct,
    long_trade_profit_frac,
    short_trade_profit_frac,
    slippage_for_timeframe,
    stop_gap_enabled,
)
from app.services.deep_backtest import simulate_execution_with_15m
from app.metrics.indicators import ensure_ta_lib_context_columns
from app.services.combo_acceleration import enabled as acceleration_enabled
from app.services.combo_cache import (
    Snapshot,
    resolve,
    frame_identity,
    index_identity,
    protect,
    execution_lifecycle,
)

# -----------------------------------------------------------------------------
# WORKER-SIDE INTRADAY CACHE (per process)
# -----------------------------------------------------------------------------
# IMPORTANT:
# - This cache lives inside each ProcessPoolExecutor worker process.
# - It only becomes effective if we reuse the same executor across stages/rounds.
# All worker caches share the single bounded retained-byte/entry LRU budget
# (#1093 limits, #1091 combo_cache implementation). They are bounded whether or
# not the #1091 acceleration is enabled.
_WORKER_15M_CACHE = Cache("intraday")
_WORKER_INDICATOR_CACHE = Cache("indicators")
_WORKER_COVERAGE_CACHE = Cache("coverage")


def _combo_optimizer_legacy() -> bool:
    return os.environ.get("COMBO_OPTIMIZER_LEGACY") == "1"


def _local_ohlcv_covers(loader, symbol: str, timeframe: str, end_date: str) -> bool:
    """True when parquet for this pair/tf exists and its last bar covers period end."""
    try:
        if hasattr(loader, "_unified_history_enabled") and loader._unified_history_enabled(symbol):
            # Card #1118: a "cópia local" é a autoridade única (PostgreSQL), não um Parquet próprio.
            extent = loader.unified_coverage(symbol, timeframe)
            if extent is None:
                return False
            cache_end = pd.Timestamp(extent[1])
            if getattr(cache_end, "tz", None) is None:
                cache_end = cache_end.tz_localize("UTC")
            end_dt = pd.Timestamp(end_date)
            if getattr(end_dt, "tz", None) is None:
                end_dt = end_dt.tz_localize("UTC")
            return cache_end.date() >= end_dt.date()
        path = loader._get_parquet_path(symbol, timeframe)
        if not path or not os.path.exists(path):
            return False
        df_ts = pd.read_parquet(path, columns=["timestamp_utc"])
        if df_ts.empty:
            return False
        cache_end = pd.Timestamp(df_ts["timestamp_utc"].max())
        if getattr(cache_end, "tz", None) is None:
            cache_end = cache_end.tz_localize("UTC")
        end_dt = pd.Timestamp(end_date)
        if getattr(end_dt, "tz", None) is None:
            end_dt = end_dt.tz_localize("UTC")
        return cache_end.date() >= end_dt.date()
    except Exception:
        return False


def _worker_get_15m_cache(
    symbol: str, since_str: str, until_str: str, loader=None, sample_id: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Load (or reuse) the 15m DF in the current worker process."""
    accelerated = acceleration_enabled()
    frozen = os.getenv("DISCOVERY_FROZEN_INPUT_DIR") or os.getenv("DISCOVERY_FROZEN_SNAPSHOT_ID")
    # Card #1118: amostra congelada desta execução (id por argumento nos workers).
    sample_id = sample_id or ACTIVE_SAMPLE_ID.get()
    key = (
        (BUDGET.generation, symbol, since_str, until_str, frozen, sample_id)
        if accelerated
        else (symbol, since_str, until_str, frozen, sample_id)
    )
    cached = _WORKER_15M_CACHE.get(key)
    if cached is not None:
        return cached

    from app.services.discovery_inputs import read

    df_15m = read("intraday", sample_id) if sample_id else read("intraday")
    if df_15m is None:
        loader = loader or IncrementalLoader()
        df_15m = loader.fetch_intraday_data(
            symbol=symbol,
            timeframe="15m",
            since_str=since_str,
            until_str=until_str,
            read_only=True,
        )
    if accelerated:
        owned = df_15m.copy(deep=True)
        owned.index = df_15m.index.copy(deep=True)
        df_15m = protect(owned)
    _WORKER_15M_CACHE[key] = df_15m
    return df_15m


def split_train_holdout(df: pd.DataFrame, train_ratio: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Divide candles ordenados por tempo em treino (fração mais antiga) e
    holdout (fração mais recente), contíguos e disjuntos (card #470)."""
    if df is None or df.empty or len(df) < 2:
        raise ValueError("Cannot split empty or single-candle dataframe")
    if not (0.0 < train_ratio < 1.0):
        raise ValueError(f"train_ratio must be between 0 and 1 (got {train_ratio})")
    sorted_df = df.sort_index()
    split_idx = max(1, min(len(sorted_df) - 1, int(len(sorted_df) * train_ratio)))
    return sorted_df.iloc[:split_idx].copy(), sorted_df.iloc[split_idx:].copy()


# -----------------------------------------------------------------------------
# WORKER LOGGING (ProcessPoolExecutor workers run in separate processes)
# -----------------------------------------------------------------------------
def _init_worker_logging():
    from app.services.discovery_supervisor import parent_death_signal, register_pool_worker

    parent_death_signal()
    register_pool_worker()
    BUDGET.clear()
    """Configura logging nos workers para gravar em full_execution_log.txt (mesmo arquivo do main)."""
    log_file = Path(__file__).resolve().parents[2] / "full_execution_log.txt"
    root = logging.getLogger()
    for h in root.handlers:
        if isinstance(h, logging.FileHandler) and (getattr(h, "baseFilename", "") or "").endswith(
            "full_execution_log.txt"
        ):
            return
    fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root.addHandler(fh)


# -----------------------------------------------------------------------------
# SHARED LOGIC HELPER
# -----------------------------------------------------------------------------
def extract_trades_from_signals(
    df_with_signals,
    stop_loss: float,
    direction: str = "long",
    slippage: float = 0.0,
    fee: float = TRADING_FEE,
):
    if _combo_optimizer_legacy():
        return _legacy_extract_trades_from_signals(
            df_with_signals, stop_loss, direction, slippage, fee
        )
    return _fast_extract_trades_from_signals(df_with_signals, stop_loss, direction, slippage, fee)


def _legacy_extract_trades_from_signals(
    df_with_signals,
    stop_loss: float,
    direction: str = "long",
    slippage: float = 0.0,
    fee: float = TRADING_FEE,
):
    """
    Extract trades from signals with consistent logic:
    - Signal detected at CLOSE of candle i → Execute at OPEN of candle i+1 (next day)
    - ComboStrategy: logic confirmed at CLOSE of candle i → signal on candle i+1 → execute at OPEN of candle i+1
    - direction: "long" (default) or "short". Short = signal 1 opens short, -1 closes short; stop above entry, PnL when price falls.
    - Intra-candle Stop Loss - checked BEFORE signal processing (low for long, high for short)
    - Binance Fees (0.075% per op) - applied on both entry and exit
    - Exit at exact Stop Price if triggered

    CRITICAL PRIORITY RULES:
    - STOP LOSS ALWAYS has priority over exit signals
    - Stop loss is checked FIRST on each candle before checking exit signals
    """
    trades = []
    position = None
    is_short = (direction or "long").lower() == "short"
    stop_loss_pct = float(stop_loss) if stop_loss is not None else 0.0
    gap_on = stop_gap_enabled()

    for idx, row in df_with_signals.iterrows():
        # PRIORIDADE 1: Check stop loss FIRST if we have an open position
        if position is not None and stop_loss_pct > 0:
            entry_price = position["entry_price"]
            if is_short:
                exact_stop_price = entry_price * (1 + stop_loss_pct)  # short: stop above entry
                current_high = float(row["high"])
                hit_stop = current_high >= exact_stop_price
                gapped = gap_on and float(row["open"]) >= exact_stop_price
            else:
                exact_stop_price = entry_price * (1 - stop_loss_pct)  # long: stop below entry
                current_low = float(row["low"])
                hit_stop = current_low <= exact_stop_price
                gapped = gap_on and float(row["open"]) <= exact_stop_price

            if hit_stop:
                # Card #1119: candle que abre além do stop sai na abertura, não no preço do stop.
                fill_price = float(row["open"]) if gapped else exact_stop_price
                position["exit_time"] = idx.isoformat()
                position["exit_price"] = fill_price
                if is_short:
                    position["profit"] = short_trade_profit_frac(
                        entry_price, fill_price, slippage=slippage, fee=fee
                    )
                else:
                    position["profit"] = long_trade_profit_frac(
                        entry_price, fill_price, slippage=slippage, fee=fee
                    )
                if gapped:
                    position["exit_reason"] = STOP_EXIT_GAP_REASON
                    position["signal_type"] = STOP_EXIT_GAP_SIGNAL
                    position["stop_price"] = exact_stop_price
                    position["gap_pct"] = gap_pct(exact_stop_price, fill_price)
                else:
                    position["exit_reason"] = "stop_loss"
                    position["signal_type"] = "Stop"
                trades.append(position)
                position = None
                continue

        # PRIORIDADE 2: Check signals
        if row["signal"] == 1 and position is None:
            position = {
                "entry_time": idx.isoformat(),
                "entry_price": float(row["open"]),
                "type": "short" if is_short else "long",
                "entry_signal_type": "Vender" if is_short else "Comprar",
            }
        elif row["signal"] == -1 and position is not None:
            exit_price = float(row["open"])
            entry_price = position["entry_price"]
            position["exit_time"] = idx.isoformat()
            position["exit_price"] = exit_price
            if is_short:
                position["profit"] = short_trade_profit_frac(
                    entry_price, exit_price, slippage=slippage, fee=fee
                )
            else:
                position["profit"] = long_trade_profit_frac(
                    entry_price, exit_price, slippage=slippage, fee=fee
                )
            position["exit_reason"] = "signal"
            position["signal_type"] = "Close entry(s) order..."
            trades.append(position)
            position = None

    return trades


def _fast_extract_trades_from_signals(
    df_with_signals,
    stop_loss: float,
    direction: str = "long",
    slippage: float = 0.0,
    fee: float = TRADING_FEE,
):
    trades = []
    is_short = (direction or "long").lower() == "short"
    stop_loss_pct = float(stop_loss) if stop_loss is not None else 0.0
    gap_on = stop_gap_enabled()
    n = len(df_with_signals)
    if n == 0:
        return trades

    from app.services.deep_backtest import _iso_array

    index = df_with_signals.index
    iso = _iso_array(index)
    opens = df_with_signals["open"].to_numpy(dtype=np.float64, copy=False)
    highs = df_with_signals["high"].to_numpy(dtype=np.float64, copy=False)
    lows = df_with_signals["low"].to_numpy(dtype=np.float64, copy=False)
    signals = df_with_signals["signal"].to_numpy(copy=False)

    pos = None
    i = 0
    while i < n:
        if pos is not None and stop_loss_pct > 0:
            entry_price = pos["entry_price"]
            if is_short:
                exact_stop_price = entry_price * (1 + stop_loss_pct)
                hit_stop = float(highs[i]) >= exact_stop_price
                gapped = gap_on and float(opens[i]) >= exact_stop_price
            else:
                exact_stop_price = entry_price * (1 - stop_loss_pct)
                hit_stop = float(lows[i]) <= exact_stop_price
                gapped = gap_on and float(opens[i]) <= exact_stop_price
            if hit_stop:
                fill_price = float(opens[i]) if gapped else exact_stop_price
                pos["exit_time"] = iso[i]
                pos["exit_price"] = fill_price
                if is_short:
                    pos["profit"] = short_trade_profit_frac(
                        entry_price, fill_price, slippage=slippage, fee=fee
                    )
                else:
                    pos["profit"] = long_trade_profit_frac(
                        entry_price, fill_price, slippage=slippage, fee=fee
                    )
                if gapped:
                    pos["exit_reason"] = STOP_EXIT_GAP_REASON
                    pos["signal_type"] = STOP_EXIT_GAP_SIGNAL
                    pos["stop_price"] = exact_stop_price
                    pos["gap_pct"] = gap_pct(exact_stop_price, fill_price)
                else:
                    pos["exit_reason"] = "stop_loss"
                    pos["signal_type"] = "Stop"
                trades.append(pos)
                pos = None
                i += 1
                continue

        sig = signals[i]
        if sig == 1 and pos is None:
            pos = {
                "entry_time": iso[i],
                "entry_price": float(opens[i]),
                "type": "short" if is_short else "long",
                "entry_signal_type": "Vender" if is_short else "Comprar",
            }
        elif sig == -1 and pos is not None:
            exit_price = float(opens[i])
            entry_price = pos["entry_price"]
            pos["exit_time"] = iso[i]
            pos["exit_price"] = exit_price
            if is_short:
                pos["profit"] = short_trade_profit_frac(
                    entry_price, exit_price, slippage=slippage, fee=fee
                )
            else:
                pos["profit"] = long_trade_profit_frac(
                    entry_price, exit_price, slippage=slippage, fee=fee
                )
            pos["exit_reason"] = "signal"
            pos["signal_type"] = "Close entry(s) order..."
            trades.append(pos)
            pos = None
        i += 1

    return trades


def _infer_timeframe(index) -> str:
    """Tempo gráfico pelo espaçamento mais comum do índice (só quando o chamador não informa)."""
    try:
        idx = pd.DatetimeIndex(index)
        if len(idx) < 2:
            return "1d"
        step = pd.Series(idx[1:] - idx[:-1]).mode().iloc[0]
        minutes = step.total_seconds() / 60.0
    except Exception:
        return "1d"
    for label, size in (("15m", 15), ("1h", 60), ("4h", 240)):
        if abs(minutes - size) < 1:
            return label
    return "1d"


def _days_without_intraday(df_exec, df_15m) -> list:
    """Dias (pregões, em ação/ETF) do candle do tempo gráfico sem nenhum candle de 15m.

    Devolve faixas ``{"from": "AAAA-MM-DD", "to": "AAAA-MM-DD"}`` de dias seguidos da
    janela (card #1119, decisão 7): início no primeiro dia, fim no último, sem dia
    inteiro sem 15m. Pregão e dia são os da data UTC do candle (a sessão regular de
    Nova York cai sempre na mesma data UTC).
    """

    def _days(index):
        idx = pd.DatetimeIndex(index)
        if idx.tz is not None:
            idx = idx.tz_convert("UTC")
        return np.unique(idx.values.astype("datetime64[D]"))

    exec_days = _days(df_exec.index).tolist()
    have = set(_days(df_15m.index).tolist()) if len(df_15m) else set()
    runs: list = []
    current = None
    for day in exec_days:
        if day in have:
            if current is not None:
                runs.append(current)
                current = None
            continue
        label = day.isoformat()
        if current is None:
            current = {"from": label, "to": label}
        else:
            current["to"] = label
    if current is not None:
        runs.append(current)
    return runs


def extract_trades_with_mode(
    df_with_signals,
    stop_loss: float,
    deep_backtest: bool = False,
    symbol: str = None,
    since_str: str = None,
    until_str: str = None,
    df_15m_cache: Optional[pd.DataFrame] = None,
    direction: str = "long",
    return_mode: bool = False,
    slippage: float = 0.0,
    timeframe: Optional[str] = None,
    return_execution: bool = False,
    fee: float = TRADING_FEE,
):
    """
    Extract trades using either Fast (daily) or Deep (15m) backtesting mode.

    Args:
        df_with_signals: DataFrame with daily signals
        stop_loss: Stop loss percentage
        deep_backtest: If True, use 15m intraday simulation
        symbol: Trading pair (required for deep backtest)
        since_str: Start date (required for deep backtest)
        until_str: End date (required for deep backtest)
        direction: "long" (default) or "short"
        timeframe: tempo gráfico (para o título da precisão efetiva)
        return_execution: devolve ``(trades, modo, execution)``; ``execution`` diz a precisão
            pedida e a efetiva, o trecho sem intradiário e a contagem de stops com gap
            (card #1119, decisão 7). A queda nunca é silenciosa; quando cai, o modo é o de sempre.

    Returns:
        List of trades (``return_mode`` -> ``(trades, modo)``).
    """
    trades, mode, execution = _extract_trades_with_execution(
        df_with_signals,
        stop_loss,
        deep_backtest=deep_backtest,
        symbol=symbol,
        since_str=since_str,
        until_str=until_str,
        df_15m_cache=df_15m_cache,
        direction=direction,
        slippage=slippage,
        timeframe=timeframe,
        fee=fee,
    )
    if return_execution:
        if not execution.get("timeframe"):
            execution["timeframe"] = _infer_timeframe(df_with_signals.index)
        return trades, mode, execution
    return (trades, mode) if return_mode else trades


def _extract_trades_with_execution(
    df_with_signals,
    stop_loss,
    *,
    deep_backtest,
    symbol,
    since_str,
    until_str,
    df_15m_cache,
    direction,
    slippage,
    timeframe,
    fee=TRADING_FEE,
):
    df_exec = df_with_signals.copy() if _combo_optimizer_legacy() else df_with_signals
    tf = str(timeframe).lower() if timeframe else None
    execution = {
        "precision_requested": "intrabar" if deep_backtest else "daily",
        "precision_effective": "candle",
        "timeframe": tf,
        "intraday_missing": [],
        "intraday_reason": None,
        "intraday_error": None,
        "gap_stops": 0,
    }

    def finish(trades, mode):
        execution["gap_stops"] = sum(
            1
            for t in trades
            if isinstance(t, dict) and t.get("exit_reason") == STOP_EXIT_GAP_REASON
        )
        if mode == "deep_15m":
            execution["precision_effective"] = "intrabar_15m"
        return trades, mode, execution

    def fall_back(reason, missing=None, error=None):
        execution["intraday_reason"] = reason
        execution["intraday_missing"] = [dict(m) for m in (missing or [])]
        execution["intraday_error"] = error
        trades = extract_trades_from_signals(df_exec, stop_loss, direction, slippage, fee)
        return finish(trades, "fast_1d")

    if not deep_backtest:
        trades = extract_trades_from_signals(df_exec, stop_loss, direction, slippage, fee)
        return finish(trades, "fast_1d")

    logger = logging.getLogger(__name__)

    def whole_window():
        if len(df_exec) == 0:
            return []
        idx = pd.DatetimeIndex(df_exec.index)
        return [{"from": str(idx.min().date()), "to": str(idx.max().date())}]

    if not symbol or not since_str:
        logger.warning(
            "Deep Backtesting requires symbol and date range. Falling back to fast mode."
        )
        return fall_back("no_window", whole_window())

    try:
        if df_15m_cache is not None:
            df_15m = df_15m_cache
        else:
            # Fetch 15m data
            df_15m = _worker_get_15m_cache(symbol, since_str, until_str)

        if df_15m is None or df_15m.empty:
            if df_15m_cache is None:  # Only warn if we tried to fetch it
                logger.warning("No 15m data available. Falling back to fast mode.")
            return fall_back("missing", whole_window())

        # Coverage guard: the 15m must cover the whole window of the timeframe candle
        # (first day to last day, no whole day without 15m); otherwise the run falls
        # back to the precision of the timeframe candle and says which stretch is missing.
        try:
            cov_key = (
                symbol,
                str(df_exec.index.min()),
                str(df_exec.index.max()),
                len(df_exec),
                str(df_15m.index.min()),
                str(df_15m.index.max()),
                len(df_15m),
            )
            coverage_cache = _WORKER_COVERAGE_CACHE
            if acceleration_enabled():
                cov_key = (
                    BUDGET.generation,
                    symbol,
                    index_identity(df_exec.index),
                    index_identity(df_15m.index),
                    *cov_key[1:],
                )
            cached_cov = None if _combo_optimizer_legacy() else coverage_cache.get(cov_key)
            if cached_cov is not None:
                missing = cached_cov
            else:
                missing = _days_without_intraday(df_exec, df_15m)
                if not _combo_optimizer_legacy():
                    coverage_cache[cov_key] = missing

            if missing:
                # Log only once per symbol per process to avoid flooding the log (e.g. 16k identical lines)
                warn_key = (symbol,)
                if warn_key not in _deep_coverage_warned:
                    _deep_coverage_warned.add(warn_key)
                    logger.warning(
                        "15m coverage insufficient for deep backtest (%s): missing %s. Falling back to the precision of the timeframe candle.",
                        symbol,
                        missing[:3],
                    )
                return fall_back("coverage", missing)
        except Exception:
            logger.warning("Failed to validate 15m coverage; falling back to fast mode.")
            return fall_back("read_error", whole_window(), "cobertura do intradiário não validada")

        if df_15m_cache is None:
            logger.info(f"Fetched {len(df_15m)} 15m candles for deep backtest simulation")

        trades = simulate_execution_with_15m(
            df_daily_signals=df_exec,
            df_15m=df_15m,
            stop_loss=stop_loss,
            direction=direction,
            slippage=slippage,
            fee=fee,
        )
        return finish(trades, "deep_15m")

    except Exception as e:
        logger.error(f"Error in deep backtest: {e}. Falling back to fast mode.")
        return fall_back("read_error", whole_window(), str(e)[:200])


def _window_identity(df: pd.DataFrame) -> tuple:
    if acceleration_enabled():
        if isinstance(df, Snapshot):
            return df.identity
        return ("external", frame_identity(df))
    return (
        repr([(col, str(dtype)) for col, dtype in zip(df.columns, df.dtypes)]),
        repr((df.index.names, str(df.index.dtype))),
        hashlib.sha256(pd.util.hash_pandas_object(df, index=True).to_numpy().tobytes()).hexdigest(),
    )


def _indicator_cache_key(
    indicators,
    entry_logic,
    exit_logic,
    derived_features,
    df: pd.DataFrame,
    binding=None,
    window_identity=None,
) -> tuple:
    return (
        binding,
        json.dumps(indicators, sort_keys=True, default=str),
        entry_logic,
        exit_logic,
        json.dumps(derived_features or [], sort_keys=True, default=str),
        window_identity if window_identity is not None else _window_identity(df),
    )


def _optimizer_context(df, template_metadata):
    """Context enrichment cannot manufacture a competing bound producer."""
    had_adx = "ADX_14" in df.columns
    df = ensure_ta_lib_context_columns(df)
    if template_metadata.get("name") == "long_ma_pullback_rsi_adx" and not had_adx:
        # This diagnostic column is generated here, not supplied by the user.
        # The declared ADX producer will calculate its own effective period.
        df = df.drop(columns=["ADX_14"], errors="ignore")
    return df


# -----------------------------------------------------------------------------
# WORKER FUNCTION (Top-level for ProcessPoolExecutor)
# -----------------------------------------------------------------------------
def _run_backtest_logic(
    template_data,
    params,
    df,
    deep_backtest,
    symbol,
    since_str,
    until_str,
    df_15m_cache=None,
    initial_capital=100,
    window_identity=None,
):
    """
    Core backtest logic shared by single and batch workers.

    Args:
        initial_capital: Capital inicial em USD para cálculo de métricas (padrão: $100)
                        Usado para calcular Return e Profit Factor no estilo TradingView
    """
    data_context = df
    try:
        if isinstance(df, Snapshot):
            df = resolve(df) if acceleration_enabled() else df.copy_frame()
        # Reconstruct strategy logic locally to avoid DB connection in worker
        indicators = template_data["indicators"]
        from app.strategies.combos.indicator_binding import capture_binding

        binding = capture_binding(
            template_data.get("name"), indicators, template_data.get("derived_features")
        )
        entry_logic = template_data["entry_logic"]
        exit_logic = template_data["exit_logic"]
        stop_loss = template_data.get("stop_loss", 0.015)

        # Handle stop_loss if it's a dict with 'default' key
        if isinstance(stop_loss, dict):
            stop_loss = stop_loss.get("default", 0.015)

        # Apply parameter overrides
        import copy

        indicators = copy.deepcopy(indicators)

        if params:
            for param_key, param_value in params.items():
                if param_key == "stop_loss":
                    stop_loss = param_value
                    continue

                if param_key == "timeframe":
                    continue
                if param_key == "direction":
                    continue  # Top-level backtest config, not a strategy parameter

                matched = False
                for indicator in indicators:
                    alias = indicator.get("alias", "")
                    type_ = indicator.get("type", "")

                    # 1. Try "alias_param" format (e.g., "short_length") - Generated by auto-schema
                    if alias and param_key.startswith(f"{alias}_"):
                        target_field = param_key[len(alias) + 1 :]
                        if "params" not in indicator:
                            indicator["params"] = {}
                        indicator["params"][target_field] = param_value
                        matched = True
                        break

                    # 2. Try "type_alias" format (e.g., "sma_short") - Used in multi_ma_crossover
                    # Default to 'length' or 'period' if not specified
                    if alias and type_ and param_key == f"{type_}_{alias}":
                        if "params" not in indicator:
                            indicator["params"] = {}
                        # Try to find which param to update: length, period, or default to length
                        if "length" in indicator["params"]:
                            indicator["params"]["length"] = param_value
                        elif "period" in indicator["params"]:
                            indicator["params"]["period"] = param_value
                        else:
                            indicator["params"]["length"] = param_value  # Fallback
                        matched = True
                        break

                    # 3. Try exact alias match (e.g. "short")
                    if alias and param_key == alias:
                        if "params" not in indicator:
                            indicator["params"] = {}
                        if "length" in indicator["params"]:
                            indicator["params"]["length"] = param_value
                        elif "period" in indicator["params"]:
                            indicator["params"]["period"] = param_value
                        else:
                            indicator["params"]["length"] = param_value
                        matched = True
                        break

                    # 4. Fallback for indicators without alias:
                    # allow "type_param" format (e.g. "rsi_length") used by legacy stage generation.
                    if (not alias) and type_ and param_key.startswith(f"{type_}_"):
                        target_field = param_key[len(type_) + 1 :]
                        if "params" not in indicator:
                            indicator["params"] = {}
                        indicator["params"][target_field] = param_value
                        matched = True
                        break

        # Create strategy instance
        from app.strategies.combos import ComboStrategy

        direction = (params or {}).get("direction", "long")
        if direction not in ("long", "short"):
            direction = "long"
        timeframe = (params or {}).get("timeframe")
        slippage = slippage_for_timeframe(timeframe)
        derived_features = template_data.get("derived_features") or []
        strategy = ComboStrategy(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss,
            direction=direction,
            indicator_binding=binding,
        )

        if _combo_optimizer_legacy():
            df_with_signals = strategy._legacy_generate_signals(df.copy())
        else:
            cache_key = _indicator_cache_key(
                indicators,
                entry_logic,
                exit_logic,
                derived_features,
                data_context,
                binding,
                window_identity,
            )
            cached = _WORKER_INDICATOR_CACHE.get(cache_key)
            if cached is None:
                df_ind = strategy.calculate_indicators(df)
                try:
                    entry_mask = strategy._evaluate_logic_vectorized(df_ind, entry_logic)
                    exit_mask = strategy._evaluate_logic_vectorized(df_ind, exit_logic)
                except Exception as exc:
                    raise CalculationFailure("calculation_error") from exc
                cached = {
                    "frame": df_ind,
                    "entry": np.ascontiguousarray(entry_mask.fillna(False).astype(bool).to_numpy()),
                    "exit": np.ascontiguousarray(exit_mask.fillna(False).astype(bool).to_numpy()),
                }
                if acceleration_enabled():
                    cached["frame"].index = cached["frame"].index.copy(deep=True)
                    protect(cached["frame"])
                    cached["entry"].flags.writeable = False
                    cached["exit"].flags.writeable = False
                _WORKER_INDICATOR_CACHE[cache_key] = cached
            work = cached["frame"].copy(deep=False)
            entry_mask = pd.Series(cached["entry"], index=work.index)
            exit_mask = pd.Series(cached["exit"], index=work.index)
            df_with_signals = strategy._fast_position_loop(work, entry_mask, exit_mask)
        # Extract trades from signals WITH STOP LOSS using Deep or Fast mode
        trades = extract_trades_with_mode(
            df_with_signals,
            stop_loss,
            deep_backtest=deep_backtest,
            symbol=symbol,
            since_str=since_str,
            until_str=until_str,
            df_15m_cache=df_15m_cache,
            direction=direction,
            slippage=slippage,
            fee=fee_for_symbol(symbol),
        )

        # Construct full effective parameters (médias, stop) para log de "profit fora do range"
        full_params = {}
        for ind in indicators:
            p_prefix = ind.get("alias") or ind.get("type")
            for pk, pv in ind.get("params", {}).items():
                full_params[f"{p_prefix}_{pk}"] = pv
        full_params["stop_loss"] = stop_loss

        # Métricas via fonte única (_metrics_from_trades) – scoring e exibição consistentes
        metrics = _metrics_from_trades(trades, initial_capital, context_params=full_params)

        # Optional diagnostic indicators (best-effort).
        # Use df_with_signals because that's where indicator columns live.
        def _first_col(prefix: str):
            pref = prefix.upper()
            for c in df_with_signals.columns:
                try:
                    if str(c).upper().startswith(pref):
                        return c
                except Exception:
                    continue
            return None

        atr_col = _first_col("ATR")
        adx_col = _first_col("ADX")

        def _safe_mean(series):
            try:
                m = series.dropna().mean()
                # avoid serializing NaN
                if m != m:  # NaN
                    return None
                return float(m)
            except Exception:
                return None

        metrics["avg_atr"] = _safe_mean(df_with_signals[atr_col]) if atr_col else None
        metrics["avg_adx"] = _safe_mean(df_with_signals[adx_col]) if adx_col else None

        return metrics, full_params

    except Exception as e:
        # Return empty metrics on failure
        return {
            "total_trades": 0,
            "win_rate": 0,
            "total_return": 0,
            "avg_profit": 0,
            "sharpe_ratio": 0,
            "error": str(e),
        }, params


def _legacy_run_backtest_logic(*args, **kwargs):
    prev = os.environ.get("COMBO_OPTIMIZER_LEGACY")
    os.environ["COMBO_OPTIMIZER_LEGACY"] = "1"
    try:
        return _run_backtest_logic(*args, **kwargs)
    finally:
        if prev is None:
            os.environ.pop("COMBO_OPTIMIZER_LEGACY", None)
        else:
            os.environ["COMBO_OPTIMIZER_LEGACY"] = prev


def _worker_run_backtest(args):
    """Legacy worker for single execution (Sequential Mode)."""
    template_data, params, df, stage_param, value, deep_backtest, symbol, since_str, until_str = (
        args
    )
    # Silence loggers
    logging.getLogger("src.data.incremental_loader").setLevel(logging.WARNING)
    logging.getLogger("app.services.deep_backtest").setLevel(logging.WARNING)
    logging.getLogger("app.services.combo_optimizer").setLevel(logging.WARNING)

    metrics, full_params = _run_backtest_logic(
        template_data, params, df, deep_backtest, symbol, since_str, until_str
    )

    if "error" in metrics:
        return {"value": value, "error": metrics["error"], "success": False}
    else:
        return {
            "value": value,
            "params": params,  # Input overrides
            "full_params": full_params,  # Complete effective state
            "metrics": metrics,
            "trades_count": metrics["total_trades"],
            "success": True,
        }


def adopt_index(frame: pd.DataFrame) -> pd.DataFrame:
    """Give an external frame a private registered index so its identity is O(1).

    An external index can be mutated through its backing array, so it never
    receives a memo token and every trial would hash it in full. The index (only)
    is deep-copied once, frozen and registered in the bounded ``indices``
    namespace; columns stay shared and untouched. Already registered indices are
    returned unchanged; an index too large for BUDGET simply keeps hashing.
    """
    index = frame.index
    data = index._data
    known = BUDGET.get("indices", (id(data), repr(index.dtype), repr(index.names)))
    if known is not None and known[0] is data:
        return frame
    holder = protect(pd.DataFrame(index=index.copy(deep=True)))
    adopted = frame.copy(deep=False)
    adopted.index = holder.index
    return adopted


def _worker_run_batch(batch_args, intraday_loader=None, observer=None, sample_id=None):
    """
    Optimized worker for Grid Search BATCH execution.
    Uses worker-level 15m cache (per process) to eliminate redundant I/O.
    """
    if not batch_args:
        return []

    # Silence loggers
    logging.getLogger("src.data.incremental_loader").setLevel(logging.WARNING)
    logging.getLogger("app.services.deep_backtest").setLevel(logging.WARNING)
    logging.getLogger("app.services.combo_optimizer").setLevel(logging.WARNING)

    results = []

    # 1. Initialize Optimization Cache (Load 15m data once per WORKER process)
    df_15m_cache = None
    first_arg = batch_args[0]
    # unpacking args structure:
    # template_data, params, df, stage_param, value, deep_backtest, symbol, since_str, until_str
    if acceleration_enabled() and isinstance(first_arg[2], Snapshot):
        resolve(first_arg[2])
    deep_backtest = first_arg[5]
    symbol = first_arg[6]
    since_str = first_arg[7]
    until_str = first_arg[8]
    # The batch's input frame is immutable and shared by all its trials.
    window_identity = _window_identity(first_arg[2])

    if deep_backtest:
        try:
            df_15m_cache = _worker_get_15m_cache(
                symbol, since_str, until_str, intraday_loader, sample_id
            )
            if acceleration_enabled() and df_15m_cache is not None:
                # Every trial of the batch shares this frame: give its index a
                # registered identity once instead of hashing it per trial.
                df_15m_cache = adopt_index(df_15m_cache)
        except Exception as e:
            # proceed without cache
            pass

    # 2. Iterate through batch
    for args in batch_args:
        template_data, params, df, stage_param, value, deep_backtest, _, _, _ = args[:9]
        trial_index = args[9] if len(args) > 9 else 0

        metrics, full_params = _run_backtest_logic(
            template_data,
            params,
            df,
            deep_backtest,
            symbol,
            since_str,
            until_str,
            df_15m_cache,  # Pass the cached data
            window_identity=window_identity if df is first_arg[2] else None,
        )

        # Wrap result to match single worker structure
        if "error" in metrics:
            results.append(
                {
                    "value": value,
                    "error": metrics["error"],
                    "success": False,
                    "trial_index": trial_index,
                }
            )
        else:
            results.append(
                {
                    "value": value,
                    "params": params,
                    "full_params": full_params,
                    "metrics": metrics,
                    "trades_count": metrics["total_trades"],
                    "success": True,
                    "trial_index": trial_index,
                }
            )

    if results:
        from app.services.discovery_resources import telemetry

        results[0]["worker_telemetry"] = telemetry()
    if observer is not None:
        observer(results)
    return results


class ComboOptimizer:
    """
    Optimizer for combo strategies.

    Optimizes modern combo strategies and executes them through the
    direction-aware combo trade extractor.
    """

    def __init__(
        self,
        checkpoint_dir: str = "backend/data/checkpoints",
        *,
        combo_service=None,
        provider=None,
        loader=None,
        worker_loader=None,
        workers=None,
        worker_observer=None,
    ):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.combo_service = combo_service or ComboService()
        self.loader = loader or IncrementalLoader()
        self._provider = provider
        self._worker_loader = worker_loader
        self._workers = workers
        self._worker_observer = worker_observer
        # Nota "janela coberta menor que a pedida" da coleta de ação/ETF (card #1119, decisão 4).
        self.collection_note = None

    def generate_stages(
        self,
        template_name: str,
        symbol: str,
        fixed_timeframe: Optional[str] = None,
        custom_ranges: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate optimization stages for a combo strategy.
        Supports Grid Search for correlated parameters.

        Args:
            template_name: Name of combo template
            symbol: Trading symbol
            fixed_timeframe: If set, skips timeframe optimization
            custom_ranges: Custom parameter ranges

        Returns:
            List of stage configurations
        """
        # Get template metadata
        metadata = self.combo_service.get_template_metadata(template_name)

        # Validate correlation metadata if present
        self._validate_correlation_metadata(metadata)

        stages = []
        stage_num = 1

        # Get optimization schema from database (if available)
        # optimization_schema may be explicitly NULL in DB (e.g. example templates)
        #
        # STRUCTURE DECIDES GRID SHAPE:
        # - If schema has "parameters" (dict) + "correlated_groups" (list of param lists):
        #   PHASE 1 runs: one STAGE per group, each stage = JOINT GRID (product of all params in group).
        #   Example: correlated_groups = [["ema_short","sma_medium","sma_long","stop_loss"]] → 1 stage, N1×N2×N3×N4 combinations.
        # - If schema is FLAT (no "parameters", no "correlated_groups"; top-level keys = param names with min/max/step):
        #   Fallback: parameters = schema, correlated_groups = []. PHASE 2 runs: one STAGE per param (sequential = sum).
        #   Example: short_ema200_pullback → 5 stages, 17+16+11+9+8 = 61 combinations in R1.
        optimization_schema = metadata.get("optimization_schema") or {}
        correlated_groups = optimization_schema.get("correlated_groups", [])
        parameters = optimization_schema.get("parameters", {})

        # Fallback for Flat Schema (historical data support)
        if (
            not parameters
            and optimization_schema
            and not optimization_schema.get("correlated_groups")
        ):
            # Heuristic: If values are dicts with 'min'/'max', assume flat parameters
            first_key = next(iter(optimization_schema), None)
            if first_key:
                first_val = optimization_schema[first_key]
                if isinstance(first_val, dict) and ("min" in first_val or "start" in first_val):
                    parameters = optimization_schema

        # Track which parameters have been added to stages
        processed_params = set()

        # PHASE 1: Create Grid Search stages for correlated groups
        for group in correlated_groups:
            # Generate value lists for each parameter in the group
            value_lists = []
            param_names = []
            adaptive_meta = {}

            for param_name in group:
                if param_name not in parameters:
                    continue  # Skip if parameter not found (validation should have caught this)

                config = parameters[param_name]

                # Check for custom range override
                if custom_ranges and param_name in custom_ranges:
                    custom = custom_ranges[param_name]
                    p_min = custom.get("min", config.get("min"))
                    p_max = custom.get("max", config.get("max"))
                    target_step = custom.get("step", config.get("step"))
                else:
                    p_min = config.get("min")
                    p_max = config.get("max")
                    target_step = config.get("step")

                # FORCE STOP LOSS STEP to 0.001 if user intent is strict 0.5% in Round 1
                if param_name == "stop_loss" and target_step == 0.002:
                    target_step = 0.001

                # Correlated group = joint grid (product of all params). Use coarse step in R1 to avoid millions of combinations.
                coarse_step = self._calculate_coarse_step(p_min, p_max, target_step)
                values = self._generate_range_values(p_min, p_max, coarse_step)

                value_lists.append(values)
                param_names.append(param_name)
                processed_params.add(param_name)

                # Store metadata for adaptive refinement
                adaptive_meta[param_name] = {
                    "target_step": target_step,
                    "current_step": coarse_step,
                    "min": p_min,
                    "max": p_max,
                }

            # Create Grid Search stage
            if param_names:
                stage = {
                    "stage_num": stage_num,
                    "stage_name": f"Grid Search: {', '.join(param_names)}",
                    "parameter": param_names,  # List of parameters (Grid mode)
                    "values": value_lists,  # List of value lists
                    "locked_params": {},
                    "grid_mode": True,  # Flag for Grid Search
                    "description": f"Joint optimization of {', '.join(param_names)}",
                    "adaptive_meta": adaptive_meta,
                }

                # Calculate and log grid size
                grid_size = self._calculate_grid_size(stage)
                logging.info(f"Stage {stage_num}: Grid Search with {grid_size} combinations")

                stages.append(stage)
                stage_num += 1

        # PHASE 2: Create Sequential stages for independent parameters
        for param_name, config in parameters.items():
            # Skip if already processed in a correlated group
            if param_name in processed_params:
                continue

            # Check for custom range override
            if custom_ranges and param_name in custom_ranges:
                custom = custom_ranges[param_name]
                p_min = custom.get("min", config.get("min"))
                p_max = custom.get("max", config.get("max"))
                target_step = custom.get("step", config.get("step"))
            else:
                p_min = config.get("min")
                p_max = config.get("max")
                target_step = config.get("step")

            # Round 1: use full grid (schema step), same as long / non-adaptive grid
            round1_step = (
                target_step
                if target_step is not None
                else self._calculate_coarse_step(p_min, p_max, target_step)
            )
            values = self._generate_range_values(p_min, p_max, round1_step)

            adaptive_meta = {
                param_name: {
                    "target_step": target_step,
                    "current_step": round1_step,
                    "min": p_min,
                    "max": p_max,
                }
            }

            stages.append(
                {
                    "stage_num": stage_num,
                    "stage_name": f"Grid Search: {param_name}",
                    "parameter": [param_name],  # List for Grid
                    "values": [values],  # List of lists for Grid
                    "locked_params": {},
                    "grid_mode": True,  # Explicit Grid Mode
                    "description": f"Grid Search verification of {param_name}",
                    "adaptive_meta": adaptive_meta,
                }
            )
            stage_num += 1

        # FALLBACK: If no optimization_schema, use legacy behavior
        if not parameters:
            logging.warning(
                f"No optimization_schema found for {template_name} - using legacy stage generation"
            )

            # Legacy: Infer from indicators metadata
            # Legacy: Infer from indicators metadata

            # Step 1: Collect indicator parameters for Grid Search
            grid_param_names = []
            grid_value_lists = []

            for indicator in metadata.get("indicators", []):
                ind_type = indicator["type"]
                ind_alias = indicator.get("alias", ind_type)
                ind_params = indicator.get("params", {})

                # Get optimization ranges from indicator config or use defaults
                opt_range = indicator.get("optimization_range", {})

                for param_name, param_value in ind_params.items():
                    # Create full parameter name (e.g., "ema_fast_length")
                    full_param_name = f"{ind_alias}_{param_name}"

                    # Determine range values
                    if custom_ranges and full_param_name in custom_ranges:
                        custom = custom_ranges[full_param_name]
                        values = self._generate_range_values(
                            custom.get("min", param_value),
                            custom.get("max", param_value * 2),
                            custom.get("step", 1),
                        )
                    elif param_name in opt_range:
                        # Use optimization range from template
                        range_config = opt_range[param_name]
                        values = self._generate_range_values(
                            range_config.get("min", param_value),
                            range_config.get("max", param_value * 2),
                            range_config.get("step", 1),
                        )
                    else:
                        # Default range: ±50% of default value
                        min_val = max(1, int(param_value * 0.5))
                        max_val = int(param_value * 1.5)
                        step = max(1, int((max_val - min_val) / 10))
                        values = self._generate_range_values(min_val, max_val, step)

                    grid_param_names.append(full_param_name)
                    grid_value_lists.append(values)

            # Create Grid Search Stage (Stage 1)
            if grid_param_names:
                stage = {
                    "stage_num": stage_num,
                    "stage_name": f"Grid Search: {', '.join(grid_param_names)}",
                    "parameter": grid_param_names,
                    "values": grid_value_lists,
                    "locked_params": {},
                    "grid_mode": True,
                    "description": f"Joint optimization of {', '.join(grid_param_names)}",
                }

                # Check grid size safety
                grid_size = self._calculate_grid_size(stage)
                logging.info(f"Implicit Grid Stage generated with {grid_size} combinations")

                stages.append(stage)
                stage_num += 1

            # Step 2: Check for orphan parameters in custom_ranges (e.g. stop_loss)
            if custom_ranges:
                existing_params = set(grid_param_names)  # Use list of names from grid
                for s in stages:  # Also check other stages if any
                    if isinstance(s["parameter"], list):
                        existing_params.update(s["parameter"])
                    else:
                        existing_params.add(s["parameter"])

                for param, range_config in custom_ranges.items():
                    if param not in existing_params:
                        values = self._generate_range_values(
                            range_config.get("min"),
                            range_config.get("max"),
                            range_config.get("step"),
                        )
                        # Force Grid Mode for orphans too (1D Grid), as requested
                        stages.append(
                            {
                                "stage_num": stage_num,
                                "stage_name": f"Grid Search: {param}",
                                "parameter": [param],  # List for Grid
                                "values": [values],  # List of lists for Grid
                                "locked_params": {},
                                "grid_mode": True,  # Explicit Grid Mode
                                "description": f"Grid Search verification of {param}",
                            }
                        )
                        stage_num += 1

        logging.info(f"Generated {len(stages)} stages for {template_name}")
        return stages

    def _generate_values_from_range(
        self, min_val: float, max_val: float, step: float
    ) -> List[float]:
        """Generate list of values from min to max with step."""
        values = []
        current = min_val
        while current <= max_val:
            values.append(current)
            current += step
        return values

    # -------------------------------------------------------------------------
    # GRID SEARCH HELPER METHODS (Phase 1)
    # -------------------------------------------------------------------------

    def _validate_correlation_metadata(self, template_metadata: Dict[str, Any]) -> None:
        """
        Validate correlated_groups against available parameters.

        Raises:
            ValueError: If validation fails
        """
        # optimization_schema may be explicitly NULL in DB (e.g. example templates)
        optimization_schema = template_metadata.get("optimization_schema") or {}
        correlated_groups = optimization_schema.get("correlated_groups", [])
        parameters = optimization_schema.get("parameters", {})

        if not correlated_groups:
            return  # No validation needed (backward compatible)

        all_correlated_params = set()

        for group in correlated_groups:
            for param in group:
                # Check if parameter exists
                if param not in parameters:
                    raise ValueError(
                        f"Invalid correlated_groups: parameter '{param}' not found in parameters. "
                        f"Available: {list(parameters.keys())}"
                    )

                # Check for duplicates
                if param in all_correlated_params:
                    raise ValueError(
                        f"Invalid correlated_groups: parameter '{param}' appears in multiple groups"
                    )
                all_correlated_params.add(param)

    def _calculate_coarse_step(self, start: Any, end: Any, target_step: Any = None) -> Any:
        """
        Calculate a coarse step for Round 1 to cover the range efficiently.
        Heuristic: Try to cover range in ~4-6 distinct values.
        """
        try:
            # Check if all inputs are effectively integers
            is_int = (
                (isinstance(start, int) or float(start).is_integer())
                and (isinstance(end, int) or float(end).is_integer())
                and (
                    target_step is None
                    or isinstance(target_step, int)
                    or float(target_step).is_integer()
                )
            )

            val_range = float(end) - float(start)

            if is_int:
                val_range = int(val_range)
                if val_range <= 5:
                    return 1

                # Integer Logic: Strictly respect Target Step * 4 (Round 1) - USER REQUEST CHANGE 5->4
                # If target_step provided (usually 1 for periods), use 4x.
                if target_step:
                    return int(target_step) * 4

                # Fallback if no target step: Just use 4 as default coarse step
                return 4

            # Float/Decimal logic
            # If target_step provided, jump 5x target (Generic Round 1 Logic)
            if target_step:
                # STRICT USER RULE: Round 1 = Step 5 (Integers) or 0.50 (Decimais)
                # For Stop Loss, user explicitly wants 0.5% (0.005).
                # This implies Base Unit is 0.001 (0.1%).
                # We enforce this if we detect 'stop_loss' context, purely for compliance.
                # Since this method doesn't know param name easily without signature change,
                # we rely on the caller fixing target_step OR we make a best effort here.
                # Actually, best is to just trust target_step * 5.
                # If target_step for stop_loss is 0.002, we get 0.01.
                # To get 0.005, target must be 0.001.
                # I will handle the 0.001 enforcement in generate_stages instead.

                return float(target_step) * 5.0

            # No target step, guess based on range magnitude
            if val_range < 0.1:
                return val_range / 4.0  # e.g. 0.08 -> 0.02
            if val_range < 1.0:
                return 0.1
            if val_range < 10.0:
                return 1.0
            return 5.0

        except Exception:
            # Fallback to safe default
            return 1 if isinstance(start, int) else 0.1

    def _refine_stage_values(self, stage: Dict, best_params: Dict, round_num: int = 1) -> None:
        """
        Refine the search grid for the next round based on best results.
        Updates stage['values'] in-place.
        """
        adaptive_meta = stage.get("adaptive_meta")
        if not adaptive_meta:
            return

        new_value_lists = []
        param_names = stage["parameter"]  # List for grid

        # Iterate over parameters in this stage
        for i, param_name in enumerate(param_names):
            meta = adaptive_meta.get(param_name)
            if not meta:
                # Should not happen if structured correctly, but fallback
                new_value_lists.append(stage["values"][i])
                continue

            best_val = best_params.get(param_name)
            if best_val is None:
                # Fallback
                new_value_lists.append(stage["values"][i])
                continue

            current_step = meta["current_step"]
            target_step = meta.get("target_step")

            # --- CALCULATE NEW STEP BASED ON ROUND ---
            if target_step:
                tgt = float(target_step)
                if round_num == 2:
                    multiplier = 3.0
                elif round_num == 3:
                    multiplier = 2.0
                elif round_num >= 4:
                    multiplier = 1.0
                else:
                    multiplier = 5.0

                new_step = tgt * multiplier
            else:
                new_step = float(current_step) / 2.0

            # Ensure Integer Constraint
            is_int = (isinstance(best_val, int) or float(best_val).is_integer()) and (
                target_step is None
                or isinstance(target_step, int)
                or float(target_step).is_integer()
            )

            if is_int:
                new_step = max(1, int(new_step))

            # Update meta for next round
            meta["current_step"] = new_step

            # --- CALCULATE NEW RANGE ---
            # Radius = Previous Step size (roughly).
            if target_step:
                tgt = float(target_step)

                # Determine Previous Multiplier based on Type
                round1_mult = (
                    4.0 if is_int else 5.0
                )  # Integers start at 4x now, Decimals keep 5x (0.5%)

                if round_num == 2:
                    prev_mult = round1_mult
                elif round_num == 3:
                    prev_mult = 3.0
                elif round_num == 4:
                    prev_mult = 2.0
                else:
                    prev_mult = round1_mult

                radius_step = tgt * prev_mult
            else:
                radius_step = current_step

            if is_int:
                radius_step = int(radius_step)

            global_min = meta.get("min")
            global_max = meta.get("max")

            range_min = best_val - radius_step
            range_max = best_val + radius_step

            if global_min is not None:
                range_min = max(range_min, global_min)
            if global_max is not None:
                range_max = min(range_max, global_max)

            new_vals = self._generate_range_values(range_min, range_max, new_step)
            new_vals = sorted(list(set(new_vals)))
            new_value_lists.append(new_vals)

            logging.info(
                f"    Refining {param_name}: Best={best_val}, Step={new_step} (Round {round_num}), Range [{range_min}, {range_max}]"
            )

        # Update stage values
        stage["values"] = new_value_lists

    def _generate_range_values(self, start: Any, end: Any, step: Any) -> List[Any]:
        """
        Generate inclusive range supporting floats and integers.

        Args:
            start: Start value
            end: End value (inclusive)
            step: Step size

        Returns:
            List of values from start to end (inclusive)

        Examples:
            _generate_range_values(10, 20, 5) -> [10, 15, 20]
            _generate_range_values(0.1, 0.3, 0.1) -> [0.1, 0.2, 0.3]
        """
        values = []
        current = start

        # Use small epsilon for float comparison
        epsilon = step / 1000.0 if isinstance(step, float) else 0

        while current <= end + epsilon:
            # Round floats to avoid precision issues (e.g., 0.30000000004)
            if isinstance(current, float):
                # Determine decimal places from step
                if step >= 1:
                    decimal_places = 0
                elif step >= 0.1:
                    decimal_places = 1
                elif step >= 0.01:
                    decimal_places = 2
                elif step >= 0.001:
                    decimal_places = 3
                else:
                    decimal_places = 4
                current = round(current, decimal_places)

            values.append(current)
            current += step

        return values

    def _calculate_grid_size(self, stage: Dict[str, Any]) -> int:
        """
        Calculate total grid size for a stage.

        Args:
            stage: Stage configuration

        Returns:
            Total number of combinations
        """
        if not stage.get("grid_mode"):
            return len(stage.get("values", []))

        # Calculate product of all value list sizes
        grid_size = 1
        for value_list in stage["values"]:
            grid_size *= len(value_list)

        # Validate against limit
        MAX_GRID_SIZE = 1000
        if grid_size > MAX_GRID_SIZE:
            logging.warning(
                f"Grid size ({grid_size:,}) exceeds recommended limit ({MAX_GRID_SIZE:,}). "
                f"Estimated time: ~{grid_size * 2 / 3600:.1f} hours. "
                f"Consider increasing step size or reducing range."
            )

        return grid_size

    def _is_correlated_group(
        self, template_metadata: Dict[str, Any], param_names: List[str]
    ) -> bool:
        """
        Check if given parameters form a correlated group.

        Args:
            template_metadata: Template metadata
            param_names: List of parameter names to check

        Returns:
            True if params are in a correlated group
        """
        # optimization_schema may be explicitly NULL in DB (e.g. example templates)
        optimization_schema = template_metadata.get("optimization_schema") or {}
        correlated_groups = optimization_schema.get("correlated_groups", [])

        param_set = set(param_names)
        for group in correlated_groups:
            if set(group) == param_set:
                return True

        return False

    def _select_top_candidates(
        self, candidates: List[Dict], top_k: int = 3, min_dist: float = 0.5
    ) -> List[Dict]:
        """
        Select Top K DISTINCT candidates based on Euclidean distance of parameters.
        Prevents selecting neighbors in the same local maximum.
        """
        if not candidates:
            return []

        # Sort by score descending
        sorted_candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)

        selected = []
        selected.append(sorted_candidates[0])  # Always take the absolute best

        # Helper to calculate normalized distance
        def calc_distance(p1, p2):
            dist = 0
            keys = set(p1.keys()) | set(p2.keys())
            for k in keys:
                v1 = p1.get(k, 0)
                v2 = p2.get(k, 0)
                # Simple Euclidean distance
                if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                    dist += (v1 - v2) ** 2
            return dist**0.5

        # Greedy selection of next candidates that are "far enough"
        for cand in sorted_candidates[1:]:
            if len(selected) >= top_k:
                break

            # Check distance against all currently selected
            is_distinct = True
            for sel in selected:
                dist = calc_distance(cand["params"], sel["params"])

                # STRICT FILTER: min_dist default 0.5.
                # Integer params usually change by 1.0 or more.
                # If dist < 0.5, it implies only Stop Loss changed (e.g. 0.01 change).
                # We want structural diversity (Moving Averages must differ).
                if dist < min_dist:
                    is_distinct = False
                    break

            if is_distinct:
                selected.append(cand)

        return selected

    def _batch_worker(self):
        """Batch worker; binds the optional test hooks only when they are set."""
        loader = getattr(self, "_worker_loader", None)
        observer = getattr(self, "_worker_observer", None)
        sample_id = getattr(self, "_sample_id", None)
        if loader is None and observer is None and sample_id is None:
            return _worker_run_batch
        return partial(
            _worker_run_batch, intraday_loader=loader, observer=observer, sample_id=sample_id
        )

    def _execute_opt_stages(
        self,
        stages,
        initial_params,
        round_num,
        max_workers,
        template_name,
        symbol,
        timeframe,
        fixed_timeframe,
        start_date,
        end_date,
        deep_backtest,
        template_metadata,
        df,
        return_top_n: int = 1,
        executor: Optional[concurrent.futures.ProcessPoolExecutor] = None,
    ):
        """
        Execute all stages for a specific branch/candidate.
        Returns:
             If return_top_n > 1 (Grid Mode): List of dicts [{'params':..., 'metrics':...}]
             If return_top_n = 1 (Sequential): (best_params, best_metrics)
        """
        best_params = initial_params.copy()
        best_metrics = None

        import time  # Import at function level to avoid UnboundLocalError

        # Enrich DF with Regime/Context Metrics (if not present) to enable Worker Logic
        if df is not None and not df.empty and "regime" not in df.columns:
            try:
                df = df.copy()
                df = _optimizer_context(df, template_metadata)

                # Regime Classification with NaN handling
                sma_col = "SMA_50"
                if sma_col in df.columns:
                    df["regime"] = "Unknown"
                    mask_bull = df["close"] > df[sma_col]
                    mask_bear = df["close"] < df[sma_col]
                    df.loc[mask_bull, "regime"] = "Bull"
                    df.loc[mask_bear, "regime"] = "Bear"
            except Exception as e:
                logging.warning(f"Failed to enrich DF with regime metrics: {e}")

        # -----------------------------------------------------------
        # NOTE: For Multi-Focus Grid (Round 1), we typically have ONE stage (the 4D Grid).
        # We need to collect ALL results from that stage and return top N.
        # For Refinement (Sequential params), we follow the standard greedy path.
        # -----------------------------------------------------------

        if acceleration_enabled() and df is not None:
            df = Snapshot(
                df,
                generation=getattr(self, "_execution_generation", None),
                source=(symbol, timeframe),
                role="train",
                limits=(start_date, end_date),
            )
        collected_candidates = []
        total_combinations_tested = 0  # Track total across all stages

        for stage in stages:
            stage_param = stage["parameter"]
            stage_values = stage["values"]
            is_grid_mode = stage.get("grid_mode", False)

            start_time = time.time()
            stage_best_value = None
            stage_best_sharpe = float("-inf")

            profile = ResourceProfile.optimizer(max_workers)

            def arguments():
                for trial, args in enumerate(
                    self._stage_worker_args(
                        stage,
                        best_params,
                        df,
                        deep_backtest,
                        symbol,
                        start_date,
                        end_date,
                        template_metadata,
                    )
                ):
                    yield args[:9] + (trial,)

            planned = sum(
                1
                for _ in self._stage_worker_args(
                    stage,
                    best_params,
                    None,
                    deep_backtest,
                    symbol,
                    start_date,
                    end_date,
                    template_metadata,
                )
            )
            if not planned:
                continue
            logging.info(
                "Round %s stage %s planned=%s workers=%s",
                round_num,
                stage_param,
                planned,
                profile.effective_workers,
            )
            local_executor = None
            exec_to_use = executor
            if exec_to_use is None:
                local_executor = concurrent.futures.ProcessPoolExecutor(
                    max_workers=profile.effective_workers,
                    mp_context=multiprocessing.get_context("spawn"),
                    initializer=_init_worker_logging,
                )
                exec_to_use = local_executor
                track_pool(local_executor)
            try:
                with ResultSpool(profile) as spool:
                    counters = execute_stream(
                        exec_to_use, self._batch_worker(), arguments, planned, spool, profile
                    )
                    total_combinations_tested += counters["executed"]
                    scored_results = spool.ranked(
                        0,
                        best_params,
                        stage,
                        return_top_n * 2 if is_grid_mode and return_top_n > 1 else 1,
                    )
                if not scored_results:
                    raise CalculationFailure("empty_stage")
                if is_grid_mode and return_top_n > 1:
                    collected_candidates.extend(scored_results)
                top = scored_results[0]
                best_metrics = top["metrics"]
                best_params = top["params"]
            finally:
                if local_executor is not None:
                    local_executor.shutdown(wait=True, cancel_futures=True)

        # Log total combinations tested
        logging.info(f"📊 Total combinations tested in this execution: {total_combinations_tested}")

        if return_top_n > 1:
            if collected_candidates:
                # Sort all collected candidates (if multiple grid stages existed, unlikely for 4D)
                collected_candidates.sort(key=lambda x: x["score"], reverse=True)
                return collected_candidates[: return_top_n * 2]
            raise CalculationFailure("empty_optimization")

        return best_params, best_metrics

    def _execute_r2r4_pooled(
        self,
        candidates,
        stages,
        round_num,
        max_workers,
        template_name,
        symbol,
        timeframe,
        fixed_timeframe,
        start_date,
        end_date,
        deep_backtest,
        template_metadata,
        df,
        executor,
    ):
        """Submit all branches of each R2–R4 stage together, then greedy-update."""
        import copy

        if df is not None and not df.empty and "regime" not in df.columns:
            try:
                df = df.copy()
                df = _optimizer_context(df, template_metadata)
                if "SMA_50" in df.columns:
                    df["regime"] = "Unknown"
                    df.loc[df["close"] > df["SMA_50"], "regime"] = "Bull"
                    df.loc[df["close"] < df["SMA_50"], "regime"] = "Bear"
            except Exception as exc:
                logging.warning("Failed to enrich DF with regime metrics: %s", exc)

        if acceleration_enabled() and df is not None:
            df = Snapshot(
                df,
                generation=getattr(self, "_execution_generation", None),
                source=(symbol, timeframe),
                role="train",
                limits=(start_date, end_date),
            )
        branch_states = []
        for candidate in candidates:
            current_stages = copy.deepcopy(stages)
            for stage in current_stages:
                if stage.get("adaptive_meta"):
                    self._refine_stage_values(stage, candidate["params"], round_num=round_num)
            branch_states.append(
                {
                    "candidate": candidate,
                    "stages": current_stages,
                    "params": candidate["params"].copy(),
                    "metrics": {},
                    "score": float("-inf"),
                }
            )

        profile = ResourceProfile.optimizer(max_workers)
        n_stages = max((len(state["stages"]) for state in branch_states), default=0)
        for stage_i in range(n_stages):
            domains = [
                (domain, state, state["stages"][stage_i])
                for domain, state in enumerate(branch_states)
                if stage_i < len(state["stages"])
            ]
            planned = sum(
                sum(
                    1
                    for _ in self._stage_worker_args(
                        stage,
                        state["params"],
                        None,
                        deep_backtest,
                        symbol,
                        start_date,
                        end_date,
                        template_metadata,
                    )
                )
                for _, state, stage in domains
            )

            def arguments():
                trial = 0
                for domain, state, stage in domains:
                    for args in self._stage_worker_args(
                        stage,
                        state["params"],
                        df,
                        deep_backtest,
                        symbol,
                        start_date,
                        end_date,
                        template_metadata,
                    ):
                        yield args[:9] + (trial, domain)
                        trial += 1

            with ResultSpool(profile) as spool:
                execute_stream(executor, self._batch_worker(), arguments, planned, spool, profile)
                for domain, state, stage in domains:
                    ranked = spool.ranked(domain, state["params"], stage, 1)
                    if not ranked:
                        continue  # A stage with zero legal trials keeps the reference state.
                    top = ranked[0]
                    state["params"] = top["params"]
                    state["metrics"] = top["metrics"]
                    state["score"] = top["metrics"].get("sharpe_ratio", top["score"])

        next_round_candidates = []
        for state in branch_states:
            candidate = state["candidate"]
            metrics = state["metrics"]
            if not metrics:
                next_round_candidates.append(
                    {
                        "params": state["params"],
                        "meta": candidate["meta"],
                        "round": round_num + 1,
                        "score": float("-inf"),
                        "metrics": {},
                    }
                )
                continue
            next_round_candidates.append(
                {
                    "params": state["params"],
                    "meta": candidate["meta"],
                    "round": round_num + 1,
                    "score": metrics.get("sharpe_ratio", state["score"]),
                    "metrics": metrics,
                }
            )
        return next_round_candidates

    def _stage_worker_args(
        self,
        stage,
        best_params,
        df,
        deep_backtest,
        symbol,
        start_date,
        end_date,
        template_metadata,
    ):
        stage_param = stage["parameter"]
        stage_values = stage["values"]
        is_grid_mode = stage.get("grid_mode", False)
        if is_grid_mode:
            param_names = stage_param
            value_lists = stage_values
            for combo in itertools.product(*value_lists):
                test_params = best_params.copy()
                p_short = p_inter = p_long = None
                current_combo = dict(zip(param_names, combo))
                full_context = {**best_params, **current_combo}
                for k, v in full_context.items():
                    k_lower = str(k).lower()
                    if (
                        k_lower.endswith("media_curta")
                        or k_lower.endswith("ema_short")
                        or k_lower.endswith("sma_short")
                    ):
                        p_short = v
                    elif k_lower.endswith("media_inter") or k_lower.endswith("sma_medium"):
                        p_inter = v
                    elif k_lower.endswith("media_longa") or k_lower.endswith("sma_long"):
                        p_long = v
                if p_short is not None and p_inter is not None and p_long is not None:
                    try:
                        if not (float(p_short) < float(p_inter) < float(p_long)):
                            continue
                    except (ValueError, TypeError):
                        pass
                for pname, pval in zip(param_names, combo):
                    test_params[pname] = pval
                yield (
                    template_metadata,
                    test_params,
                    df,
                    param_names,
                    dict(zip(param_names, combo)),
                    deep_backtest,
                    symbol,
                    start_date,
                    end_date,
                )
        else:
            for value in stage_values:
                test_params = best_params.copy()
                if stage_param != "timeframe":
                    test_params[stage_param] = value
                    yield (
                        template_metadata,
                        test_params,
                        df,
                        stage_param,
                        value,
                        deep_backtest,
                        symbol,
                        start_date,
                        end_date,
                    )

    @bounded_execution
    @execution_lifecycle
    def run_optimization(
        self,
        template_name: str,
        symbol: str,
        timeframe: str = "1h",
        data_source: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        custom_ranges: Optional[Dict[str, Any]] = None,
        deep_backtest: bool = True,  # Default to Deep Backtesting
        job_id: Optional[str] = None,
        direction: str = "long",
        split_train_ratio: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Run parameter optimization (corpo em ``_run_optimization_body``).

        Card #1118: com ``MARKET_HISTORY_UNIFIED=1`` a execução congela a amostra no
        início (candles e 15m em segmentos com SHA-256) e todas as tentativas leem só
        dela. O resultado traz a proveniência e o ``snapshot_id``.
        """

        self._sample = None
        self._sample_id = None
        token = ACTIVE_SAMPLE_ID.set(None)
        try:
            result = self._run_optimization_body(
                template_name=template_name,
                symbol=symbol,
                timeframe=timeframe,
                data_source=data_source,
                start_date=start_date,
                end_date=end_date,
                custom_ranges=custom_ranges,
                deep_backtest=deep_backtest,
                job_id=job_id,
                direction=direction,
                split_train_ratio=split_train_ratio,
            )
            sample = self._sample
            if sample is not None and isinstance(result, dict):
                result["snapshot_id"] = sample.snapshot_id
                result["data_provenance"] = sample.provenance(
                    "candles", with_retention="/" not in str(symbol)
                )
                sample.finish()
            return result
        except BaseException:
            sample = self._sample
            if sample is not None and sample.snapshot_id:
                # Execução que falha não sustenta resultado: a amostra expira para o GC levar.
                try:
                    from app.services.market_history import snapshots as history_snapshots

                    history_snapshots.expire(sample.engine, sample.snapshot_id)
                except Exception:  # pragma: no cover
                    logging.exception("Could not expire the sample of a failed optimization")
            raise
        finally:
            ACTIVE_SAMPLE_ID.reset(token)
            self._sample_id = None

    def _begin_sample(self, selected_data_source, symbol, timeframe, start_date, end_date, df):
        """Congela os candles no início da execução.

        Cripto pelo caminho unificado (``MARKET_HISTORY_UNIFIED``); ação e ETF sempre, porque
        a série ``binance_equity`` só existe no histórico novo (card #1119, decisão 8).
        """
        from app.services.market_history import unified_enabled

        equity = selected_data_source == BINANCE_EQUITY_SOURCE
        if (
            not equity
            and (not unified_enabled() or selected_data_source != "ccxt" or "/" not in str(symbol))
            or os.getenv("DISCOVERY_FROZEN_INPUT_DIR")
            or os.getenv("DISCOVERY_FROZEN_SNAPSHOT_ID")
            or df is None
            or df.empty
        ):
            return df
        sample = ExecutionSample("optimization", owner_ref=f"optimization:{symbol}:{timeframe}")
        frozen = sample.freeze_symbol("candles", symbol, timeframe, start_date, end_date, df)
        self._sample = sample
        self._sample_id = sample.snapshot_id
        ACTIVE_SAMPLE_ID.set(sample.snapshot_id)
        return frozen

    def _freeze_intraday(self, symbol, start_date, end_date):
        sample = getattr(self, "_sample", None)
        if sample is None or sample.has("intraday"):
            return
        intraday = self.loader.fetch_intraday_data(
            symbol=symbol,
            timeframe="15m",
            since_str=start_date,
            until_str=end_date,
            read_only=True,
        )
        if intraday is not None and not intraday.empty:
            sample.freeze_crypto("intraday", symbol, "15m", start_date, end_date, intraday)

    def _freeze_equity_intraday(self, symbol, start_date, end_date):
        """15m de ação/ETF (montado do 5m pelo ``HistoryService``) na amostra da execução.

        Sem 15m, congela vazio: o worker lê vazio e a execução cai para o candle do tempo
        gráfico dizendo que o intradiário faltou (decisão 7), em vez de falhar.
        """
        sample = getattr(self, "_sample", None)
        if sample is None or sample.has("intraday"):
            return
        from app.services.equity_backtest import inclusive_end
        from app.services.market_history.facade import (
            get_history_service,
            spec_for_request,
            to_loader_frame,
        )

        service = get_history_service()
        series = service.resolve(spec_for_request(symbol=symbol, timeframe="15m"))
        result = service.read(series, start_date, inclusive_end(end_date))
        frame = to_loader_frame(result.candles)
        sample.freeze_symbol("intraday", symbol, "15m", start_date, end_date, frame)

    def _run_optimization_body(
        self,
        template_name: str,
        symbol: str,
        timeframe: str = "1h",
        data_source: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        custom_ranges: Optional[Dict[str, Any]] = None,
        deep_backtest: bool = True,
        job_id: Optional[str] = None,
        direction: str = "long",
        split_train_ratio: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Corpo de ``run_optimization``.

        Args:
            split_train_ratio: quando informado (ex.: 0.7), a otimização roda
                somente no treino (fração mais antiga dos candles) e o resultado
                final inclui métricas do holdout (período mais recente) com
                veredito GO/NO-GO (walk-forward gate, card #470). None mantém o
                comportamento legado (período inteiro, sem gate).
        """
        if direction not in ("long", "short"):
            direction = "long"

        optimization_start_time = time.time()
        # If data_source is omitted, infer based on symbol:
        # - symbols without "/" are treated as US tickers -> stooq
        # - symbols with "/" are treated as crypto pairs -> ccxt
        self._execution_generation = uuid.uuid4().hex
        if acceleration_enabled():
            BUDGET.begin(self._execution_generation)
        inferred = data_source
        if inferred is None or str(inferred).strip() == "":
            inferred = resolve_data_source_for_symbol(symbol, None)

        selected_data_source = validate_data_source_timeframe(inferred, timeframe)

        # Generate stages
        fixed_timeframe = timeframe if timeframe else None
        stages = self.generate_stages(
            template_name=template_name,
            symbol=symbol,
            fixed_timeframe=fixed_timeframe,
            custom_ranges=custom_ranges,
        )

        # Get template metadata ONCE for workers
        template_metadata = self.combo_service.get_template_metadata(template_name)

        # Ensure we have date ranges for Deep Backtesting
        # If not provided, use full period (2017-present for comprehensive testing)
        start_date_defaulted = False
        requested_window = {"start": start_date or None, "end": end_date or None}
        if not start_date:
            # Ação/ETF: "todo o histórico" começa onde a Binance começa (card #1119).
            start_date = (
                "2000-01-01"
                if selected_data_source == BINANCE_EQUITY_SOURCE
                else "2017-01-01"  # Full crypto history (works for most major assets)
            )
            start_date_defaulted = True
        if not end_date:
            from datetime import datetime

            end_date = datetime.now().strftime("%Y-%m-%d")

        # Load data from selected provider (ccxt default; stooq for US stocks EOD)
        provider = getattr(self, "_provider", None) or get_market_data_provider(
            selected_data_source
        )
        if os.getenv("DISCOVERY_FROZEN_INPUT_DIR") or os.getenv("DISCOVERY_FROZEN_SNAPSHOT_ID"):
            from app.services.discovery_inputs import FrozenProvider

            provider = FrozenProvider()
        df = provider.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since_str=start_date,
            until_str=end_date,
        )
        df = self._begin_sample(selected_data_source, symbol, timeframe, start_date, end_date, df)

        # Walk-forward split (card #470): when split_train_ratio is set, the
        # optimization stages run only on the oldest fraction (train) and the
        # final result includes holdout metrics with GO/NO-GO verdict.
        df_holdout = None
        df_train_tail_for_warmup = None
        if split_train_ratio is not None:
            try:
                train_full, df_holdout = split_train_holdout(df, float(split_train_ratio))
                # Burn-in: tail do treino para warmup de indicadores do holdout
                # (SMA_200 etc. precisam de histórico antes da primeira barra).
                burnin = max(50, int(os.getenv("WALK_FORWARD_BURNIN_CANDLES", "250")))
                df_train_tail_for_warmup = train_full.iloc[-burnin:].copy()
                df = train_full
                logging.info(
                    "Walk-forward split: train=%d candles (%.0f%%), holdout=%d candles (%.0f%%), burnin=%d",
                    len(df),
                    float(split_train_ratio) * 100,
                    len(df_holdout),
                    (1 - float(split_train_ratio)) * 100,
                    burnin,
                )
            except ValueError as exc:
                logging.warning(
                    "Walk-forward split skipped: %s (running without split, legacy behavior)",
                    exc,
                )
                df_holdout = None
                df_train_tail_for_warmup = None
        # Workers will only READ the parquet slice (read_only=True) to avoid concurrent writes/corruption.
        # After prefetch, ensure 15m tail is up to end_date (self-healing: avoids stale cache for this symbol).
        if (
            deep_backtest
            and selected_data_source == "ccxt"
            and not os.getenv("DISCOVERY_FROZEN_INPUT_DIR")
            and not os.getenv("DISCOVERY_FROZEN_SNAPSHOT_ID")
        ):
            period_end = end_date
            daily_covers = _local_ohlcv_covers(self.loader, symbol, timeframe, period_end)
            intra_covers = _local_ohlcv_covers(self.loader, symbol, "15m", period_end)
            if daily_covers and intra_covers:
                logging.info(
                    "Skipping exchange tail/setup for %s: 1d+15m already on disk covering %s",
                    symbol,
                    period_end,
                )
            else:
                try:
                    # For "all history", align intraday start to the first available daily candle
                    # (avoids downloading 15m before the exchange has data for the symbol).
                    intraday_since = start_date
                    allow_large = False
                    if start_date_defaulted and df is not None and not df.empty:
                        intraday_since = pd.Timestamp(df.index.min()).date().isoformat()
                        allow_large = True
                        logging.warning(
                            "Deep backtest requested for full history. Building/expanding 15m cache for %s from %s..%s. "
                            "This may take a long time on first run.",
                            symbol,
                            intraday_since,
                            end_date,
                        )
                    self.loader.fetch_intraday_data(
                        symbol=symbol,
                        timeframe="15m",
                        since_str=intraday_since,
                        until_str=end_date,
                        read_only=False,
                        allow_large_backfill=allow_large,
                    )
                except Exception as e:
                    logging.warning(
                        "Prefetch 15m failed for %s (%s..%s): %s. Deep backtest will fall back to fast mode.",
                        symbol,
                        start_date,
                        end_date,
                        e,
                    )
                # Self-healing: ensure 15m cache extends to end_date (handles stale cache or partial prefetch failure).
                try:
                    from datetime import datetime as _dt, timedelta

                    info = self.loader.check_intraday_availability(symbol, "15m")
                    end_dt = _dt.strptime(end_date, "%Y-%m-%d")
                    need_tail = False
                    if not info.get("available") or not info.get("coverage"):
                        need_tail = True  # No cache or empty: try last 30 days only
                    else:
                        cache_end_str = info["coverage"].get("end")
                        if cache_end_str:
                            cache_end = pd.Timestamp(cache_end_str)
                            if getattr(cache_end, "tz", None) is None:
                                cache_end = cache_end.tz_localize("UTC")
                            if cache_end.date() < end_dt.date():
                                need_tail = True
                    if need_tail:
                        tail_since = (end_dt - timedelta(days=30)).strftime("%Y-%m-%d")
                        logging.info(
                            "15m cache lags behind end_date; updating tail for %s (%s to %s)",
                            symbol,
                            tail_since,
                            end_date,
                        )
                        self.loader.fetch_intraday_data(
                            symbol=symbol,
                            timeframe="15m",
                            since_str=tail_since,
                            until_str=end_date,
                            read_only=False,
                            allow_large_backfill=False,
                        )
                except Exception as e2:
                    logging.debug("15m tail update check failed: %s", e2)
            logging.info(
                "Deep backtest ON: workers will use 15m intraday data for exit simulation (stop/target precision)."
            )
            try:
                self._freeze_intraday(symbol, start_date, end_date)
            except Exception as exc:
                logging.warning("Freeze of the 15m sample failed for %s: %s", symbol, exc)
        elif deep_backtest and selected_data_source == BINANCE_EQUITY_SOURCE:
            # Card #1119 (decisão 8): o intrabar de ação/ETF não depende mais da CCXT; o 15m sai
            # do 5m guardado e entra na amostra congelada, lida por todas as tentativas.
            try:
                self._freeze_equity_intraday(symbol, start_date, end_date)
            except Exception as exc:
                logging.warning("Freeze of the equity 15m sample failed for %s: %s", symbol, exc)
        elif deep_backtest and selected_data_source != "ccxt":
            logging.info(
                "Deep backtest disabled for data_source=%s (intraday cache is crypto/ccxt only).",
                selected_data_source,
            )
            deep_backtest = False

        # Initialize best parameters (direction and timeframe are fixed for the whole optimization)
        best_params = {"direction": direction, "timeframe": timeframe}
        best_metrics = None

        # Use ProcessPoolExecutor for parallel execution
        # An explicit worker count (benchmark/tests) is only the unprofiled default;
        # a configured #1093 resource profile still decides the effective workers.
        max_workers = ResourceProfile.optimizer(getattr(self, "_workers", None)).effective_workers

        # PHASE 2: Detect Grid Search and allow refinement
        # Grid Search finds the best region, then we refine it. Same logic for long and short (direction-agnostic).
        has_grid_search = any(stage.get("grid_mode", False) for stage in stages)
        has_adaptive = any(stage.get("adaptive_meta") for stage in stages)

        # Default Sequential Mode vars
        max_rounds = 5
        round_num = 1
        converged = False

        # Reuse a single executor across all stages/rounds in this optimization.
        # This drastically reduces process spawn overhead and enables per-worker caches (e.g. 15m data).
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers,
            mp_context=multiprocessing.get_context("spawn"),
            initializer=_init_worker_logging,
        ) as executor:
            track_pool(executor)
            if has_grid_search and has_adaptive:
                # -------------------------------------------------------------
                # 4D ADAPTIVE OPTIMIZATION (MULTI-BRANCH)
                # -------------------------------------------------------------
                max_rounds = 4
                logging.info("=" * 60)
                logging.info(
                    "Adaptive Grid Search detected - 4 rounds: full grid (R1) then refinement (R2-R4)"
                )
                logging.info("=" * 60)

                # Candidates list (starts with single 'root' candidate which covers the whole space)
                # Structure: {'params': dict, 'meta': dict, 'round': 1, 'score': float}
                candidates = [
                    {"params": best_params.copy(), "meta": {}, "round": 1, "score": float("-inf")}
                ]

                final_best_candidates = []

                for round_num in range(1, max_rounds + 1):
                    logging.info(f"--- STARTING ROUND {round_num} OF ADAPTIVE OPTIMIZATION ---")
                    logging.info(f"Candidates (Branches) to process: {len(candidates)}")

                    next_round_candidates = []

                    if round_num > 1 and len(candidates) > 1:
                        next_round_candidates = self._execute_r2r4_pooled(
                            candidates,
                            stages,
                            round_num,
                            max_workers,
                            template_name,
                            symbol,
                            timeframe,
                            fixed_timeframe,
                            start_date,
                            end_date,
                            deep_backtest,
                            template_metadata,
                            df,
                            executor,
                        )
                        # Skip the per-branch loop; selection below uses next_round_candidates.
                        idx = len(candidates)
                        execution_result = None
                    else:
                        for idx, candidate in enumerate(candidates):
                            logging.info(
                                f"Processing Branch {idx+1}/{len(candidates)} based on: {candidate['params']}"
                            )

                            # 1. Setup stages for this candidate
                            if round_num == 1:
                                current_stages = stages  # Use initial coarse stages
                            else:
                                # Clone stages to avoid polluting other branches
                                import copy

                                current_stages = copy.deepcopy(stages)
                                # Refine based on THIS candidate's best params
                                for stage in current_stages:
                                    if stage.get("adaptive_meta"):
                                        self._refine_stage_values(
                                            stage, candidate["params"], round_num=round_num
                                        )

                            # 2. Execute Optimization for this branch
                            # For Round 1 (Grid), we want multiple candidates to feed the logical branches.
                            # For Round > 1, we just want the best refinement for this specific branch.
                            return_n = 10 if round_num == 1 else 1

                            execution_result = self._execute_opt_stages(
                                current_stages,
                                candidate["params"],
                                round_num,
                                max_workers,
                                template_name,
                                symbol,
                                timeframe,
                                fixed_timeframe,
                                start_date,
                                end_date,
                                deep_backtest,
                                template_metadata,
                                df,
                                return_top_n=return_n,
                                executor=executor,
                            )

                            if round_num == 1:
                                # Reviewing multiple candidates from Grid (or single fallback when all batches failed)
                                branch_candidates = execution_result
                                if (
                                    isinstance(branch_candidates, (tuple, list))
                                    and len(branch_candidates) == 2
                                    and not isinstance(branch_candidates[0], dict)
                                ):
                                    branch_candidates = [
                                        {
                                            "params": branch_candidates[0],
                                            "metrics": branch_candidates[1] or {},
                                            "score": float("-inf"),
                                        }
                                    ]
                                for cand in branch_candidates:
                                    params = cand.get("params") if isinstance(cand, dict) else None
                                    if params is None:
                                        continue
                                    result_candidate = {
                                        "params": params,
                                        "meta": candidate["meta"],
                                        "round": round_num + 1,
                                        "score": cand.get("score", float("-inf")),
                                        "metrics": cand.get("metrics") or {},
                                    }
                                    next_round_candidates.append(result_candidate)
                            else:
                                # Standard single result
                                branch_best_params, branch_best_metrics = execution_result

                                # 3. Score this branch result
                                score = (
                                    branch_best_metrics.get("sharpe_ratio", -999)
                                    if branch_best_metrics
                                    else -999
                                )

                                result_candidate = {
                                    "params": branch_best_params,
                                    "meta": candidate["meta"],
                                    "round": round_num + 1,
                                    "score": score,
                                    "metrics": branch_best_metrics,
                                }

                                next_round_candidates.append(result_candidate)

                    # SELECTION LOGIC (End of Round)
                    if round_num < max_rounds:
                        # Select Top 10 Distinct Candidates for next round - USER REQUEST CHANGE 3 -> 10
                        # If Round 1 produced 20 candidates, we pick top 10 distinct ones here.
                        candidates = self._select_top_candidates(next_round_candidates, top_k=10)
                        logging.info(
                            f"Selected {len(candidates)} candidates for Round {round_num + 1}"
                        )
                    else:
                        # Final round - collect all results
                        final_best_candidates = next_round_candidates

                # Find absolute best from final candidates
                if final_best_candidates:
                    # Sort by score descending
                    final_best_candidates.sort(key=lambda x: x["score"], reverse=True)
                    best_candidate = final_best_candidates[0]

                    best_params = best_candidate["params"]
                    best_metrics = best_candidate["metrics"]

                    # Log details about the winner
                    logging.info(
                        f"Global Best Found from {len(final_best_candidates)} final branches"
                    )

                converged = True  # Mark as done so we skip legacy loop logic

            else:
                # -------------------------------------------------------------
                # LEGACY SEQUENTIAL / SIMPLE GRID (Backup)
                # -------------------------------------------------------------
                if has_grid_search:
                    max_rounds = 1
                    logging.info("=" * 60)
                    logging.info("Grid Search (Non-Adaptive) detected - running single round")
                    logging.info("=" * 60)
                else:
                    max_rounds = 5
                    logging.info("Sequential optimization - using iterative refinement (5 rounds)")

                while not converged and round_num <= max_rounds:
                    logging.info(f"--- STARTING ROUND {round_num} OF REFINE ---")

                    # Refine stages for rounds > 1 (Adaptive Zoom)
                    if round_num > 1:
                        logging.info(f"Refining search grid around best result: {best_params}")
                        for stage in stages:
                            if stage.get("adaptive_meta"):
                                self._refine_stage_values(stage, best_params)

                    # Execute stages using shared helper (single branch)
                    best_params, best_metrics = self._execute_opt_stages(
                        stages,
                        best_params,
                        round_num,
                        max_workers,
                        template_name,
                        symbol,
                        timeframe,
                        fixed_timeframe,
                        start_date,
                        end_date,
                        deep_backtest,
                        template_metadata,
                        df,
                        executor=executor,
                    )

                    # End of Round Analysis
                    # Simple loose check for convergence
                    params_changed = True  # (Simplify logic: always refine if rounds left in legacy mode unless strictly identical)

                    if round_num < max_rounds:
                        logging.info(
                            f"--- ROUND {round_num} COMPLETE: Parameters changed. Refining... ---"
                        )
                        round_num += 1
                    else:
                        converged = True

        if not converged:
            logging.warning(
                f"Optimization stopped after max rounds ({max_rounds}) without full convergence."
            )

        total_optimization_time = time.time() - optimization_start_time
        rounds_display = round_num if converged else round_num - 1

        # Run final backtest with best parameters to get complete data
        logging.info(f"Running final backtest with best parameters: {best_params}")

        try:
            # Reload data with best timeframe
            df_final = provider.fetch_ohlcv(
                symbol=symbol, timeframe=timeframe, since_str=start_date, until_str=end_date
            )
            # Walk-forward (card #470): o backtest final deve refletir o TREINO
            # (mesma janela usada na otimização); o holdout é avaliado à parte.
            if split_train_ratio is not None and df_holdout is not None:
                try:
                    df_final, _ = split_train_holdout(df_final, float(split_train_ratio))
                except ValueError as exc:
                    logging.warning("Final backtest split skipped: %s", exc)

            # Enrich df_final with regime for heavy metrics calculation
            if "regime" not in df_final.columns:
                try:
                    df_final = _optimizer_context(df_final, template_metadata)

                    # Use SMA_50 as fallback for better coverage (SMA_200 has more warmup NaNs)
                    if "SMA_50" not in df_final.columns and "SMA_200" in df_final.columns:
                        df_final["SMA_50"] = df_final["SMA_200"]

                    sma_col = "SMA_50" if "SMA_50" in df_final.columns else "SMA_200"
                    if sma_col in df_final.columns:
                        # Create regime with proper NaN handling
                        df_final["regime"] = "Unknown"
                        mask_bull = df_final["close"] > df_final[sma_col]
                        mask_bear = df_final["close"] < df_final[sma_col]
                        df_final.loc[mask_bull, "regime"] = "Bull"
                        df_final.loc[mask_bear, "regime"] = "Bear"

                        # Log regime distribution for debugging
                        regime_counts = df_final["regime"].value_counts()
                        logging.info(
                            f"Regime distribution using {sma_col}: {regime_counts.to_dict()}"
                        )
                except Exception as e:
                    logging.warning(f"Failed to enrich final DF with regime: {e}")

            # Create strategy with best parameters
            strategy = self.combo_service.create_strategy(
                template_name=template_name, parameters=best_params
            )

            # Generate signals
            if acceleration_enabled():
                df_final = Snapshot(
                    df_final,
                    generation=self._execution_generation,
                    source=(symbol, timeframe),
                    role="final-train",
                    limits=(start_date, end_date),
                ).copy_frame()
            df_with_signals = strategy.generate_signals(df_final.copy())
            report({"phase_complete": "final_signals"})

            # Extract trades (same direction as optimization)
            stop_loss = best_params.get("stop_loss", 0.0)
            direction = best_params.get("direction", "long")
            if direction not in ("long", "short"):
                direction = "long"
            final_slippage = slippage_for_timeframe(timeframe)
            final_intraday = (
                self._worker_loader.fetch_intraday_data(
                    symbol=symbol,
                    timeframe="15m",
                    since_str=start_date,
                    until_str=end_date,
                    read_only=True,
                )
                if getattr(self, "_worker_loader", None) is not None
                else None
            )
            final_outcome = extract_trades_with_mode(
                df_with_signals,
                stop_loss,
                deep_backtest=deep_backtest,
                symbol=symbol,
                since_str=start_date,
                until_str=end_date,
                **(
                    {"df_15m_cache": final_intraday}
                    if getattr(self, "_worker_loader", None) is not None
                    else {}
                ),
                direction=direction,
                return_mode=True,
                slippage=final_slippage,
                fee=fee_for_symbol(symbol),
                timeframe=timeframe,
                return_execution=True,
            )
            # (trades, modo, execution); uma extração substituta sem `execution` segue valendo.
            if len(final_outcome) == 3:
                trades, execution_mode, final_execution = final_outcome
            else:
                trades, execution_mode = final_outcome
                final_execution = None
            report({"phase_complete": "final_execution"})

            # Recompute core metrics from final backtest trades (same set as returned to frontend)
            # Fixes Total Return / Win Rate mismatch vs. "List of trades" / Cumulative P&L
            core_from_final = _metrics_from_trades(
                trades, initial_capital=100, context_params=best_params
            )
            if best_metrics is not None:
                best_metrics.update(core_from_final)

            # Post-Process Heavy Metrics (Only for best result)
            try:
                logging.info(f"Calculating heavy metrics for {len(trades)} trades")
                logging.info(
                    f"Regime column present in df_with_signals: {'regime' in df_with_signals.columns}"
                )
                if "regime" in df_with_signals.columns:
                    logging.info(
                        f"Regime values in signals df: {df_with_signals['regime'].value_counts().to_dict()}"
                    )

                heavy = _calculate_heavy_metrics(df_with_signals, trades)
                if best_metrics:
                    best_metrics.update(heavy)
                    logging.info(f"Heavy metrics calculated: {heavy}")
            except Exception as e:
                logging.error(f"Failed to calculate heavy metrics: {e}")
                import traceback

                traceback.print_exc()

            if split_train_ratio is None and best_metrics is not None:
                _enrich_ranking_metrics(
                    trades,
                    df_final["close"] if df_final is not None and not df_final.empty else None,
                    best_metrics,
                    legacy_zero_trade_ranking=False,
                )

            # Prepare candles data
            candles = []

            # Prepare candles data
            candles = []
            for idx, row in df_final.iterrows():
                candles.append(
                    {
                        "timestamp_utc": str(idx),
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": float(row["volume"]),
                    }
                )
                if len(candles) % 1000 == 0:
                    report({"phase_complete": f"final_candles:{len(candles)}"})

            # Extract indicator data (only numeric columns)
            indicator_data = {}
            excluded_cols = {
                "open",
                "high",
                "low",
                "close",
                "volume",
                "signal",
                "regime",
                # timestamps / indexes (never treat as numeric indicator series)
                "timestamp",
                "timestamp_utc",
                "time",
                "date",
            }

            try:
                from pandas.api.types import is_numeric_dtype
            except Exception:
                is_numeric_dtype = None

            for col in df_with_signals.columns:
                if col in excluded_cols:
                    continue

                try:
                    series = df_with_signals[col]
                    if is_numeric_dtype is not None and not is_numeric_dtype(series):
                        continue

                    # Ensure JSON-serializable numeric list
                    indicator_data[col] = [
                        float(x) if x is not None else 0.0 for x in series.fillna(0).tolist()
                    ]
                except Exception:
                    # Skip any non-numeric or non-serializable columns
                    continue

        except Exception as e:
            raise CalculationFailure("final_calculation_error") from e

        # Walk-forward holdout (card #470): backtest the best parameters on the
        # most recent fraction and compute GO/NO-GO verdict over holdout metrics.
        oos_metrics: Optional[Dict[str, Any]] = None
        oos_verdict: Optional[Dict[str, Any]] = None
        if split_train_ratio is not None and df_holdout is not None and not df_holdout.empty:
            try:
                strategy_holdout = self.combo_service.create_strategy(
                    template_name=template_name, parameters=best_params
                )
                # Burn-in: concatena a cauda do treino para warmup de indicadores;
                # trades com entry fora do holdout são descartados da avaliação.
                holdout_eval_start = df_holdout.index.min()
                holdout_frame = df_holdout
                if df_train_tail_for_warmup is not None and not df_train_tail_for_warmup.empty:
                    holdout_frame = pd.concat([df_train_tail_for_warmup, df_holdout])
                if acceleration_enabled():
                    holdout_frame = Snapshot(
                        holdout_frame,
                        generation=self._execution_generation,
                        source=(symbol, timeframe),
                        role="holdout-burnin",
                        limits=(str(holdout_eval_start), end_date),
                    ).copy_frame()
                df_holdout_signals = strategy_holdout.generate_signals(holdout_frame.copy())
                report({"phase_complete": "holdout_signals"})
                stop_loss = best_params.get("stop_loss", 0.0)
                direction = best_params.get("direction", "long")
                if direction not in ("long", "short"):
                    direction = "long"
                holdout_slippage = slippage_for_timeframe(timeframe)
                holdout_trades_raw, holdout_mode = extract_trades_with_mode(
                    df_holdout_signals,
                    stop_loss,
                    deep_backtest=deep_backtest,
                    symbol=symbol,
                    since_str=(
                        str(holdout_frame.index.min().date()) if len(holdout_frame) else start_date
                    ),
                    until_str=(
                        str(holdout_frame.index.max().date()) if len(holdout_frame) else end_date
                    ),
                    **(
                        {
                            "df_15m_cache": self._worker_loader.fetch_intraday_data(
                                symbol=symbol,
                                timeframe="15m",
                                since_str=start_date,
                                until_str=end_date,
                                read_only=True,
                            )
                        }
                        if getattr(self, "_worker_loader", None) is not None
                        else {}
                    ),
                    direction=direction,
                    return_mode=True,
                    slippage=holdout_slippage,
                    fee=fee_for_symbol(symbol),
                )
                holdout_trades = []
                for trade in holdout_trades_raw:
                    entry = trade.get("entry_time")
                    if not entry:
                        continue
                    try:
                        if pd.Timestamp(entry) >= holdout_eval_start:
                            holdout_trades.append(trade)
                    except Exception:
                        holdout_trades.append(trade)
                oos_metrics = _metrics_from_trades(
                    holdout_trades, initial_capital=100, context_params=best_params
                )
                try:
                    heavy_holdout = _calculate_heavy_metrics(df_holdout_signals, holdout_trades)
                    if oos_metrics:
                        oos_metrics.update(heavy_holdout)
                except Exception as exc:
                    logging.warning("Holdout heavy metrics failed: %s", exc)
                # CAGR / Calmar / benchmark sobre o holdout (gate GO/NO-GO precisa
                # dessas métricas; _metrics_from_trades não as produz).
                try:
                    from app.metrics.performance import calculate_cagr
                    from app.metrics.benchmark import calculate_buy_and_hold
                    from app.metrics.risk_adjusted import calculate_calmar_ratio

                    equity_values = [100.0]
                    cap = 100.0
                    for trade in sorted(
                        holdout_trades,
                        key=lambda t: pd.Timestamp(t.get("entry_time") or 0),
                    ):
                        cap *= 1.0 + float(trade.get("profit") or 0.0)
                        equity_values.append(cap)
                    equity = pd.Series(equity_values)
                    close_series = df_holdout["close"]
                    years = _calendar_years_from_evidence(close_series, holdout_trades)
                    if len(equity) >= 2 and len(holdout_trades) > 0 and years:
                        oos_cagr = calculate_cagr(equity, years=years)
                    else:
                        oos_cagr = 0.0
                    bh = calculate_buy_and_hold(close_series, 100.0)
                    oos_calmar = calculate_calmar_ratio(
                        oos_cagr, float(oos_metrics.get("max_drawdown") or 0.0)
                    )
                    if oos_metrics is not None:
                        oos_metrics["cagr"] = oos_cagr
                        oos_metrics["calmar_ratio"] = oos_calmar
                        oos_metrics["benchmark"] = bh
                except Exception as exc:
                    logging.warning("Holdout CAGR/benchmark metrics failed: %s", exc)
                from app.metrics.criteria import evaluate_walk_forward

                # O segmento IS (Treino) precisa das mesmas métricas que o
                # evaluate_go_nogo exige (CAGR, Calmar, benchmark); o bloco do
                # holdout acima enriquece apenas o OOS, e `best_metrics` vem de
                # _metrics_from_trades sem essas chaves.
                try:
                    if best_metrics is not None and "cagr" not in best_metrics:
                        is_close = df["close"] if df is not None and not df.empty else None
                        _enrich_ranking_metrics(
                            trades,
                            is_close,
                            best_metrics,
                            legacy_zero_trade_ranking=True,
                        )
                except Exception as exc:
                    logging.warning("Treino (IS) CAGR/benchmark metrics failed: %s", exc)

                # Gate combinado walk-forward (card #503): IS (Treino) usa os
                # critérios globais, OOS (Holdout) usa perfil próprio e exige
                # retenção de ao menos 50% do Sharpe IS. `oos_verdict` legado
                # passa a carregar o veredito final combinado; as razões
                # identificam o segmento.
                criteria_result = evaluate_walk_forward(best_metrics or {}, oos_metrics or {})
                oos_verdict = {
                    "status": criteria_result.status,
                    "reasons": criteria_result.reasons,
                    "warnings": criteria_result.warnings,
                    "holdout_trades": len(holdout_trades),
                    "execution_mode": holdout_mode,
                    "split_train_ratio": float(split_train_ratio),
                }
                report({"phase_complete": "holdout_complete"})
                logging.info(
                    "Walk-forward holdout verdict: %s (%d trades, %d reasons)",
                    criteria_result.status,
                    len(holdout_trades),
                    len(criteria_result.reasons),
                )
            except Exception as exc:
                raise CalculationFailure("holdout_calculation_error") from exc

        # COMPLETION SUMMARY (after final backtest so metrics match returned trades)
        logging.info("=" * 80)
        logging.info("🎯 OPTIMIZATION COMPLETE")
        logging.info("=" * 80)
        logging.info(f"Rounds completed: {rounds_display}/{max_rounds}")
        logging.info(
            f"Total execution time: {total_optimization_time:.1f}s ({total_optimization_time/60:.1f} minutes)"
        )
        logging.info(f"Convergence: {'Yes' if converged else 'No'}")
        logging.info(f"\nFinal Configuration:")
        for param, value in best_params.items():
            logging.info(f"  {param}: {value}")
        if best_metrics:
            tr_pct = best_metrics.get("total_return_pct")
            if tr_pct is None:
                tr_pct = (best_metrics.get("total_return") or 0) * 100.0
            logging.info(f"\nFinal Metrics:")
            logging.info(f"  Sharpe Ratio: {best_metrics.get('sharpe_ratio', 0):.3f}")
            logging.info(f"  Total Return: {tr_pct:.2f}%")
            logging.info(f"  Max Drawdown: {best_metrics.get('max_drawdown', 0):.3f}")
        logging.info("=" * 80)

        # Card #1119 (decisão 12): identidade, precisão efetiva e convenções até a resposta.
        from app.services.equity_backtest import asset_identity, finalize_execution

        try:
            result_asset = asset_identity(symbol)
            result_execution, result_conventions = finalize_execution(
                final_execution,
                asset=result_asset,
                timeframe=timeframe,
                direction=best_params.get("direction", direction),
                requested=requested_window,
                frame=df_final,
                collection=getattr(self, "collection_note", None),
            )
        except Exception as exc:  # a identidade nunca derruba o resultado já calculado
            logging.warning("Result identity could not be built for %s: %s", symbol, exc)
            result_asset = result_execution = result_conventions = None

        return {
            "job_id": job_id or "combo_opt_" + str(hash(template_name + symbol)),
            "template_name": template_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "stages": stages,
            "best_parameters": best_params,
            "best_metrics": best_metrics or {},
            "oos_metrics": oos_metrics,
            "oos_verdict": oos_verdict,
            "total_stages": len(stages),
            # Add complete backtest data
            "trades": trades,
            "candles": candles,
            "indicator_data": indicator_data,
            "parameters": best_params,  # For compatibility with ComboResultsPage
            "direction": best_params.get("direction", "long"),
            "data_source": selected_data_source,
            "execution_mode": execution_mode,
            "asset": result_asset,
            "execution": result_execution,
            "conventions": result_conventions,
            "strategy_transparency": self._build_strategy_transparency_result(
                template_name=template_name,
                timeframe=timeframe,
                parameters=best_params,
                dataframe=(df_with_signals if "df_with_signals" in locals() and candles else None),
            ),
        }

    def _build_strategy_transparency_result(
        self,
        *,
        template_name: str,
        timeframe: str,
        parameters: dict[str, Any],
        dataframe: pd.DataFrame | None,
    ) -> dict[str, Any]:
        from app.services.strategy_transparency import build_strategy_transparency

        metadata = self.combo_service.get_template_metadata(template_name)
        manifest = build_strategy_transparency(
            template_name,
            metadata,
            effective_parameters=parameters,
            timeframe=timeframe,
            dataframe=dataframe,
        )
        return manifest.model_dump(mode="json")


def _calendar_years_from_evidence(
    close_series: Optional[pd.Series],
    trades: list | None,
) -> float | None:
    """Years = calendar of the evidence window / 365, never n_trades or len(equity)."""
    from app.metrics.performance import calendar_years

    if close_series is not None and not close_series.empty:
        index = close_series.index
        if isinstance(index, pd.DatetimeIndex) and len(index) >= 2:
            try:
                return calendar_years(index[0], index[-1])
            except ValueError:
                pass
    times: list[pd.Timestamp] = []
    for trade in trades or []:
        if not isinstance(trade, dict):
            continue
        for key in ("exit_time", "entry_time"):
            raw = trade.get(key)
            if not raw:
                continue
            try:
                times.append(pd.Timestamp(raw))
            except (TypeError, ValueError):
                continue
    if len(times) >= 2:
        try:
            return calendar_years(min(times), max(times))
        except ValueError:
            return None
    return None


def _enrich_ranking_metrics(
    trades: list,
    close_series: Optional[pd.Series],
    metrics_dict: Optional[Dict[str, Any]],
    *,
    legacy_zero_trade_ranking: bool = False,
) -> None:
    """Populate cagr, calmar_ratio and benchmark on metrics_dict for leaderboard ranking."""
    if metrics_dict is None:
        return

    import math

    from app.metrics.benchmark import calculate_buy_and_hold
    from app.metrics.performance import calculate_cagr
    from app.metrics.risk_adjusted import calculate_calmar_ratio

    if not trades and not legacy_zero_trade_ranking:
        return

    try:
        if trades:
            equity_values = [100.0]
            cap = 100.0
            for trade in sorted(trades, key=lambda t: pd.Timestamp(t.get("entry_time") or 0)):
                cap *= 1.0 + float(trade.get("profit") or 0.0)
                equity_values.append(cap)
            equity = pd.Series(equity_values)
            years = _calendar_years_from_evidence(close_series, trades)
            if years is not None and years > 0 and len(equity) >= 2:
                cagr = calculate_cagr(equity, years=years)
            elif legacy_zero_trade_ranking:
                cagr = 0.0
            else:
                return
        elif legacy_zero_trade_ranking:
            cagr = 0.0
        else:
            return

        if close_series is not None and not close_series.empty:
            bh = calculate_buy_and_hold(close_series, 100.0)
        elif legacy_zero_trade_ranking:
            bh = {"cagr": 0.0}
        else:
            return

        calmar = calculate_calmar_ratio(cagr, float(metrics_dict.get("max_drawdown") or 0.0))

        if legacy_zero_trade_ranking:
            metrics_dict["cagr"] = cagr
            metrics_dict["calmar_ratio"] = calmar
            metrics_dict["benchmark"] = bh
            return

        if math.isfinite(cagr):
            metrics_dict["cagr"] = cagr
        if isinstance(bh, dict):
            bh_cagr = bh.get("cagr")
            if bh_cagr is not None and math.isfinite(float(bh_cagr)):
                metrics_dict["benchmark"] = bh
        if math.isfinite(calmar):
            metrics_dict["calmar_ratio"] = calmar
    except Exception as exc:
        logging.warning("Ranking metrics enrichment failed: %s", exc)


def _metrics_from_trades(
    trades: list, initial_capital: float = 100, context_params: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Single source of truth for all metrics derived from a trade list.
    Used by _run_backtest_logic (optimization scoring) and final backtest.
    Ensures Sharpe, Total Return, Win Rate, etc. are always computed the same way.
    context_params: opcional; se fornecido, é logado nos warnings "profit fora do range" (médias, stop, etc.).
    """
    import numpy as np

    out = {
        # --- Core ---
        "total_trades": 0,
        "win_rate": 0.0,
        "total_return": 0.0,  # decimal (e.g. 0.35 = +35%)
        "total_return_pct": 0.0,  # percent (e.g. 35.0)
        "avg_profit": 0.0,  # mean return per trade (decimal)
        # --- Risk / ratios ---
        "sharpe_ratio": 0.0,
        "sortino_ratio": None,  # may be None when degenerate
        "sortino_status": None,  # ok|degenerate|invalid
        "downside_deviation": None,  # downside std (same units as returns)
        "neg_return_count": 0,
        "return_series_kind": "per_trade",
        # --- PnL / trade stats ---
        "profit_factor": 0.0,
        "max_loss": 0.0,
        "max_consecutive_losses": 0,
        # Drawdown: keep both decimal + pct (avoid unit confusion)
        "max_drawdown": 0.0,  # decimal (0..1)
        "max_drawdown_pct": 0.0,  # percent (0..100)
        # Expectancy: provide multiple units explicitly
        "expectancy": 0.0,  # decimal per trade (same unit as avg_profit)
        "expectancy_pct": 0.0,  # percent per trade
        "expectancy_usd_10k": 0.0,  # legacy-style (assumes $10k notional)
    }
    if not trades:
        return out

    # Ordenar por entry_time (mesma ordem do frontend / Cumulative P&L)
    def _ts(t):
        et = t.get("entry_time")
        if et is None:
            return 0
        try:
            return pd.Timestamp(et).timestamp()
        except Exception:
            return 0

    sorted_trades = sorted(trades, key=_ts)

    # Coletar returns válidos; ignorar apenas trades com profit None
    # profit é decimal: 0.05 = 5%, 1.66 = 166%, 16.32 = 1632% — ganhos >100% são válidos (ex.: TradingView)
    returns = []
    for t in sorted_trades:
        p = t.get("profit")
        if p is None:
            continue
        returns.append(float(p))

    n = len(returns)
    if n == 0:
        out["total_trades"] = len(trades)
        return out

    wins = sum(1 for r in returns if r > 0)
    out["total_trades"] = n
    out["win_rate"] = wins / n

    # Compounding (equity curve)
    cap = float(initial_capital)
    equity_curve = [cap]
    for r in returns:
        cap *= 1.0 + r
        equity_curve.append(cap)

    total_return_pct = (cap / initial_capital - 1) * 100.0
    total_return = total_return_pct / 100.0
    out["total_return"] = float(total_return)
    out["total_return_pct"] = float(total_return_pct)

    # avg_profit = mean return per trade (decimal)
    out["avg_profit"] = float(np.mean(np.array(returns, dtype=float))) if n else 0.0

    # Sharpe (per-trade return series; not annualized)
    arr = np.array(returns, dtype=float)
    std_dev = float(np.std(arr))
    out["sharpe_ratio"] = float(np.mean(arr) / std_dev) if std_dev > 0 else 0.0

    # Sortino (downside deviation) with guardrails
    neg = arr[arr < 0]
    out["neg_return_count"] = int(len(neg))

    # Note: with very few negatives or near-zero downside deviation, Sortino is degenerate.
    # Returning a huge number is misleading; we return None + status instead.
    eps = 1e-9
    if len(neg) < 2:
        out["sortino_ratio"] = None
        out["downside_deviation"] = 0.0
        out["sortino_status"] = "degenerate"
    else:
        down_std = float(np.std(neg))
        out["downside_deviation"] = down_std
        if down_std < eps:
            out["sortino_ratio"] = None
            out["sortino_status"] = "degenerate"
        else:
            out["sortino_ratio"] = float(np.mean(arr) / down_std)
            out["sortino_status"] = "ok"

    # Profit factor (USD com compounding)
    cap2 = float(initial_capital)
    gross_profit_usd = 0.0
    gross_loss_usd = 0.0
    for r in returns:
        pnl = cap2 * r
        if r > 0:
            gross_profit_usd += pnl
        else:
            gross_loss_usd += abs(pnl)
        cap2 *= 1.0 + r
    out["profit_factor"] = (
        gross_profit_usd / gross_loss_usd
        if gross_loss_usd > 0
        else (999.0 if gross_profit_usd > 0 else 0.0)
    )

    out["max_loss"] = float(np.min(arr))

    # Expectancy: keep units explicit
    mean_r = float(np.mean(arr))
    out["expectancy"] = mean_r
    out["expectancy_pct"] = mean_r * 100.0
    out["expectancy_usd_10k"] = mean_r * 10000.0  # legacy: assumes $10k notional

    # Max consecutive losses
    streak = 0
    max_streak = 0
    for r in returns:
        if r < 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    out["max_consecutive_losses"] = max_streak

    # Max drawdown (equity curve em valor absoluto)
    peak = float(initial_capital)
    max_dd = 0.0
    for eq in equity_curve:
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak if peak > 0 else 0
        max_dd = max(max_dd, float(dd))

    # IMPORTANT: store drawdown as decimal + pct (avoid mixing units elsewhere)
    out["max_drawdown"] = float(max_dd)  # 0..1
    out["max_drawdown_pct"] = float(max_dd) * 100.0

    return out


def _calculate_heavy_metrics(df, trades):
    metrics = {}
    try:
        if "regime" in df.columns and trades:
            bull_wins = 0
            bull_count = 0
            bear_wins = 0
            bear_count = 0
            import pandas as pd

            for t in trades:
                et = t.get("entry_time")
                if et:
                    try:
                        if isinstance(et, str):
                            et = pd.to_datetime(et)

                        # Normalize Timezone to match DataFrame index
                        # If Index is Aware but ET is Naive -> Localize to UTC (assumption)
                        if df.index.tz is not None and et.tz is None:
                            et = et.tz_localize("UTC")
                        # If Index is Naive but ET is Aware -> Convert ET to Naive
                        elif df.index.tz is None and et.tz is not None:
                            et = et.tz_convert(None)

                        idx_match = df.index.asof(et)
                        if idx_match is not None:
                            # Verify if match is "close enough" (optional, but asof finds PREVIOUS)
                            # Logic assumes daily/intraday continuity.

                            r_val = df.loc[idx_match]["regime"]
                            if isinstance(r_val, pd.Series):
                                r_val = r_val.iloc[0]
                            is_win = t.get("profit", 0) > 0
                            if r_val == "Bull":
                                bull_count += 1
                                if is_win:
                                    bull_wins += 1
                            elif r_val == "Bear":
                                bear_count += 1
                                if is_win:
                                    bear_wins += 1
                    except Exception:
                        pass
            metrics["win_rate_bull"] = (bull_wins / bull_count) if bull_count > 0 else 0
            metrics["win_rate_bear"] = (bear_wins / bear_count) if bear_count > 0 else 0
    except Exception as e:
        pass
    return metrics
