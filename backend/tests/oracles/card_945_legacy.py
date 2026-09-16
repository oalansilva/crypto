"""Frozen combo-optimizer path at baseline-945=e43b93e5e0569a9c4a82d4cce2ef24dfa0ef5e4c.

Literal copies of:
- ComboStrategy.calculate_indicators
- ComboStrategy._evaluate_logic_vectorized
- ComboStrategy.generate_signals (position loop)
- simulate_execution_with_15m
- extract_trades_from_signals
- _metrics_from_trades

Test-only. Not product. Speed commits MUST NOT edit this module.
"""

from __future__ import annotations

import ast
import copy
import logging
import re
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import talib

from app.strategies.combos.helpers import HELPER_FUNCTIONS
from src.data.incremental_loader import IncrementalLoader

_deep_coverage_warned: set = set()


class LegacyComboStrategy:
    """
    Base class for combo strategies that combine multiple indicators.

    Supports:
    - Multiple instances of the same indicator
    - Indicator aliases for clear logic
    - Custom entry/exit logic evaluation
    - Helper functions (crossover, crossunder, etc.)
    """

    def __init__(
        self,
        indicators: List[Dict[str, Any]],
        entry_logic: str,
        exit_logic: str,
        stop_loss: float = 0.015,
        stop_gain: Optional[float] = None,
        derived_features: Optional[List[Dict[str, Any]]] = None,
        force_recompute: bool = True,
        direction: str = "long",
    ):
        """
        Initialize combo strategy.

        Args:
            indicators: List of indicator configs with type, alias, and params
            entry_logic: Entry logic expression (e.g., "(close > fast) AND (RSI < 30)")
            exit_logic: Exit logic expression
            stop_loss: Stop loss percentage (default 1.5%)
            stop_gain: Stop gain percentage (optional)
        """
        self.indicators = indicators
        self.entry_logic = entry_logic
        self.exit_logic = exit_logic
        self.stop_loss = stop_loss
        self.stop_gain = stop_gain
        self.derived_features = derived_features or []
        self.force_recompute = bool(force_recompute)
        self.direction = "short" if str(direction or "").lower() == "short" else "long"

        self._indicator_cache = {}
        self._validate_aliases()

    def _validate_aliases(self):
        """Validate that all aliases are unique."""
        aliases = [ind.get("alias") for ind in self.indicators if ind.get("alias")]
        if len(aliases) != len(set(aliases)):
            duplicates = [a for a in aliases if aliases.count(a) > 1]
            raise ValueError(f"Duplicate aliases found: {set(duplicates)}")

    @staticmethod
    def _coerce_int(value: Any, default: int | None = None) -> int | None:
        try:
            parsed = int(float(value))
            if parsed <= 0:
                return default
            return parsed
        except Exception:
            return default

    @staticmethod
    def _coerce_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except Exception:
            return float(default)

    @staticmethod
    def _required_columns(indicator: Dict[str, Any]) -> list[str]:
        ind_type = str(indicator.get("type", "")).lower()
        params = indicator.get("params", {}) or {}
        alias = indicator.get("alias")

        if ind_type == "ema":
            length = ComboStrategy._coerce_int(params.get("length", 9), default=9)
            if length is None:
                return []
            return [alias if alias else f"EMA_{length}"]
        if ind_type == "sma":
            length = ComboStrategy._coerce_int(params.get("length", 20), default=20)
            if length is None:
                return []
            return [alias if alias else f"SMA_{length}"]
        if ind_type == "rsi":
            length = ComboStrategy._coerce_int(params.get("length", 14), default=14)
            if length is None:
                return []
            if alias:
                return [alias]
            return [f"RSI_{length}"]
        if ind_type == "macd":
            fast = ComboStrategy._coerce_int(params.get("fast", 12), default=12)
            slow = ComboStrategy._coerce_int(params.get("slow", 26), default=26)
            signal = ComboStrategy._coerce_int(params.get("signal", 9), default=9)
            if fast is None or slow is None or signal is None:
                return []
            prefix = alias if alias else "MACD"
            cols = [f"{prefix}_macd", f"{prefix}_signal", f"{prefix}_histogram"]
            if not alias and fast == 12 and slow == 26 and signal == 9:
                cols.extend(["MACDs_12_26_9", "MACDh_12_26_9"])
            return cols
        if ind_type in ("bbands", "bollinger"):
            prefix = alias if alias else "BB"
            return [f"{prefix}_upper", f"{prefix}_middle", f"{prefix}_lower"]
        if ind_type == "atr":
            length = ComboStrategy._coerce_int(params.get("length", 14), default=14)
            if length is None:
                return []
            return [alias if alias else f"ATR_{length}"]
        if ind_type == "adx":
            length = ComboStrategy._coerce_int(params.get("length", 14), default=14)
            if length is None:
                return []
            return [alias if alias else f"ADX_{length}"]
        if ind_type == "roc":
            length = ComboStrategy._coerce_int(params.get("length", 20), default=20)
            if length is None:
                return []
            return [alias if alias else f"ROC_{length}"]
        if ind_type == "volume_sma":
            length = ComboStrategy._coerce_int(params.get("length", 20), default=20)
            if length is None:
                return []
            return [alias if alias else f"VOL_SMA_{length}"]
        if alias:
            return [alias]
        return []

    @staticmethod
    def _is_cached(df: pd.DataFrame, indicator: Dict[str, Any]) -> bool:
        required = ComboStrategy._required_columns(indicator)
        return bool(required) and all(col in df.columns for col in required)

    def _normalize_derived_feature(self, item: Any) -> Optional[Dict[str, Any]]:
        if isinstance(item, str):
            token = item.strip()
            if not token:
                return None
            m = re.match(
                r"^(?P<source>[A-Za-z_][A-Za-z0-9_]*)_(?P<suffix>prev|lag|shift|slope|mean|rolling_mean|pct_change)(?P<num>\d+)?$",
                token,
            )
            if not m:
                return None
            source = m.group("source")
            suffix = m.group("suffix")
            num = m.group("num")
            period = int(num) if num else 1
            transform = "lag" if suffix in ("prev", "lag", "shift") else suffix
            if transform == "mean":
                transform = "rolling_mean"
            return {
                "name": token,
                "source": source,
                "transform": transform,
                "params": {"period": period} if period else {},
            }

        if not isinstance(item, dict):
            return None

        name = str(item.get("name") or item.get("alias") or "").strip()
        source = str(item.get("source") or item.get("base") or "").strip()
        transform = str(item.get("transform") or "").strip().lower()
        params = item.get("params") if isinstance(item.get("params"), dict) else {}

        if not source or not transform:
            return None

        if not name:
            if transform in ("lag", "prev", "shift"):
                name = f"{source}_prev"
            elif transform == "rolling_mean":
                name = f"{source}_mean"
            else:
                name = f"{source}_{transform}"

        if transform == "prev":
            transform = "lag"
        if transform == "shift":
            transform = "lag"
        if transform == "mean":
            transform = "rolling_mean"

        return {
            "name": name,
            "source": source,
            "transform": transform,
            "params": params,
        }

    def _apply_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.derived_features:
            return df

        allowed = {"lag", "slope", "rolling_mean", "pct_change"}
        for raw in self.derived_features:
            spec = self._normalize_derived_feature(raw)
            if not spec:
                raise RuntimeError(f"Invalid derived feature declaration: {raw}")

            name = spec.get("name")
            source = spec.get("source")
            transform = spec.get("transform")
            params = spec.get("params") or {}

            if transform not in allowed:
                raise RuntimeError(f"Unsupported derived transform: {transform}")

            if source not in df.columns:
                raise RuntimeError(f"Derived feature source not found: {source}")

            period = 1
            try:
                period = int(params.get("period") or params.get("window") or 1)
            except Exception:
                period = 1
            period = max(1, period)

            series = df[source]
            if transform == "lag":
                df[name] = series.shift(period)
            elif transform == "slope":
                df[name] = (series - series.shift(period)) / float(period)
            elif transform == "rolling_mean":
                df[name] = series.rolling(window=period).mean()
            elif transform == "pct_change":
                df[name] = series.pct_change(periods=period)

        return df

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all indicators and add them to the dataframe.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with calculated indicators
        """
        df = df.copy()
        if not self.force_recompute and "calculated" in self._indicator_cache:
            return self._indicator_cache["calculated"].copy()

        for indicator in self.indicators:
            ind_type = indicator["type"].lower()
            params = indicator.get("params", {})
            alias = indicator.get("alias")
            if not self.force_recompute and self._is_cached(df, indicator):
                continue

            try:
                if ind_type == "ema":
                    length = self._coerce_int(params.get("length", 9), default=9)
                    if length is None:
                        raise RuntimeError("Invalid length for EMA")
                    col_name = alias if alias else f"EMA_{length}"
                    df[col_name] = talib.EMA(df["close"], timeperiod=length)

                elif ind_type == "sma":
                    length = self._coerce_int(params.get("length", 20), default=20)
                    if length is None:
                        raise RuntimeError("Invalid length for SMA")
                    col_name = alias if alias else f"SMA_{length}"
                    df[col_name] = talib.SMA(df["close"], timeperiod=length)

                elif ind_type == "rsi":
                    length = self._coerce_int(params.get("length", 14), default=14)
                    if length is None:
                        raise RuntimeError("Invalid length for RSI")
                    col_name = f"RSI_{length}"
                    rsi_series = talib.RSI(df["close"], timeperiod=length)
                    df[col_name] = rsi_series
                    if alias and alias != col_name:
                        df[alias] = rsi_series

                elif ind_type == "macd":
                    fast = self._coerce_int(params.get("fast", 12), default=12)
                    slow = self._coerce_int(params.get("slow", 26), default=26)
                    signal = self._coerce_int(params.get("signal", 9), default=9)
                    if fast is None or slow is None or signal is None:
                        raise RuntimeError("Invalid parameters for MACD")
                    alias_prefix = alias if alias else "MACD"

                    macd_line, macd_signal, macd_hist = talib.MACD(
                        df["close"],
                        fastperiod=fast,
                        slowperiod=slow,
                        signalperiod=signal,
                    )
                    df[f"{alias_prefix}_macd"] = macd_line
                    df[f"{alias_prefix}_signal"] = macd_signal
                    df[f"{alias_prefix}_histogram"] = macd_hist
                    if not alias and fast == 12 and slow == 26 and signal == 9:
                        df["MACDs_12_26_9"] = macd_signal
                        df["MACDh_12_26_9"] = macd_hist

                elif ind_type == "bbands" or ind_type == "bollinger":
                    length = self._coerce_int(params.get("length", 20), default=20)
                    std = self._coerce_float(params.get("std", 2), default=2)
                    if length is None:
                        raise RuntimeError("Invalid length for BBANDS")
                    alias_prefix = alias if alias else "BB"

                    upper, middle, lower = talib.BBANDS(
                        df["close"],
                        timeperiod=length,
                        nbdevup=std,
                        nbdevdn=std,
                        matype=0,
                    )
                    df[f"{alias_prefix}_upper"] = upper
                    df[f"{alias_prefix}_middle"] = middle
                    df[f"{alias_prefix}_lower"] = lower

                elif ind_type == "atr":
                    length = self._coerce_int(params.get("length", 14), default=14)
                    if length is None:
                        raise RuntimeError("Invalid length for ATR")
                    col_name = f"ATR_{length}"
                    atr_series = talib.ATR(df["high"], df["low"], df["close"], timeperiod=length)
                    df[col_name] = atr_series
                    # Support stable alias when provided (e.g. "atr")
                    if alias and alias != col_name:
                        df[alias] = atr_series

                elif ind_type == "adx":
                    length = self._coerce_int(params.get("length", 14), default=14)
                    if length is None:
                        raise RuntimeError("Invalid length for ADX")
                    col_name = f"ADX_{length}"
                    df[col_name] = talib.ADX(df["high"], df["low"], df["close"], timeperiod=length)
                    # Support stable alias when provided (e.g. "adx")
                    if alias and alias != col_name:
                        df[alias] = df[col_name]

                elif ind_type == "roc":
                    length = self._coerce_int(params.get("length", 20), default=20)
                    if length is None:
                        raise RuntimeError("Invalid length for ROC")
                    roc_series = talib.ROC(df["close"], timeperiod=length)
                    col_name = f"ROC_{length}"
                    df[col_name] = roc_series
                    if alias and alias != col_name:
                        df[alias] = roc_series

                elif ind_type == "volume_sma":
                    length = self._coerce_int(params.get("length", 20), default=20)
                    if length is None:
                        raise RuntimeError("Invalid length for VOLUME_SMA")
                    col_name = alias if alias else f"VOL_SMA_{length}"
                    df[col_name] = talib.SMA(df["volume"], timeperiod=length)

                else:
                    raise RuntimeError(
                        f"Unsupported indicator type for TA-Lib strategy: {ind_type}"
                    )

            except Exception as e:
                raise RuntimeError(f"Error calculating {ind_type}: {str(e)}")

        df = self._apply_derived_features(df)

        # Ensure all columns are numeric to prevent NoneType errors in eval evaluation
        # IMPORTANT: Skip 'regime' column as it contains categorical strings
        for col in df.columns:
            if col == "regime":  # Preserve regime column
                continue
            if df[col].dtype == "object":
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Cache the result
        self._indicator_cache["calculated"] = df.copy()

        return df

    def _evaluate_logic_vectorized(self, df: pd.DataFrame, logic: str) -> pd.Series:
        """
        Evaluate entry/exit logic for the ENTIRE dataframe at once.

        Args:
            df: DataFrame with indicators
            logic: Logic expression to evaluate

        Returns:
            Boolean Series where True means logic condition is met
        """
        try:
            # Normalize boolean keywords for parsing.
            # Templates may use AND/OR/NOT (case-insensitive). We'll parse them as Python `and/or/not`,
            # then rewrite the AST to safe vectorized operations (no precedence bugs like `a < 30 & b > c`).
            logic_expr = re.sub(r"\bAND\b", "and", logic, flags=re.IGNORECASE)
            logic_expr = re.sub(r"\bOR\b", "or", logic_expr, flags=re.IGNORECASE)
            logic_expr = re.sub(r"\bNOT\b", "not", logic_expr, flags=re.IGNORECASE)
            # Also accept C-style operators if present in templates.
            logic_expr = logic_expr.replace("&&", " and ").replace("||", " or ")

            # Backward-compatible dotted indicator access:
            # Some templates use bb.upper / macd.signal style references. Internally we
            # materialize those as bb_upper / macd_signal.
            logic_expr = re.sub(
                r"\b([A-Za-z_][A-Za-z0-9_]*)\.(upper|middle|lower|macd|signal|histogram)\b",
                r"\1_\2",
                logic_expr,
            )

            # Create local context with vectorized helper functions
            local_context = HELPER_FUNCTIONS.copy()

            # Vectorized NOT helper (works for Series and scalars)
            def NOT(x):
                if isinstance(x, pd.Series):
                    return (~x.fillna(False)).astype(bool)
                # numpy arrays / scalars
                try:
                    return not bool(x)
                except Exception:
                    return ~x

            local_context["NOT"] = NOT

            # Add all dataframe columns to context (Vectors/Series)
            for col in df.columns:
                local_context[col] = df[col]

            # Preflight: detect unknown identifiers early (avoids silent 0-trade runs)
            # This catches cases like `bb.upper` (mapped to bb_upper) when the column doesn't exist.
            tokens = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", logic_expr))
            reserved = {
                "and",
                "or",
                "not",
                "True",
                "False",
                "None",
                # Safe pandas Series methods used by stored template expressions.
                # Attribute access remains constrained by the identifier preflight:
                # unsupported method names still fail before eval.
                "abs",
                "shift",
                "rolling",
                "mean",
                "max",
                "min",
                "sum",
            }
            # helper functions are available via HELPER_FUNCTIONS/local_context
            allowed = set(local_context.keys()) | reserved
            missing = sorted([t for t in tokens if t not in allowed])
            if missing:
                raise RuntimeError(
                    "Logic references unknown columns/functions: "
                    + ", ".join(missing)
                    + ". Available example columns: "
                    + ", ".join(list(df.columns)[:20])
                )

            # Compatibility mapping for RSI references:
            # Some example templates hardcode RSI_14 but also define optimization over RSI length.
            # If there is a single RSI indicator, map any referenced RSI_<n> token to the computed RSI series.
            try:
                referenced_rsi = set(re.findall(r"\bRSI_\d+\b", logic_expr))
                if referenced_rsi:
                    rsi_inds = [
                        i for i in self.indicators if str(i.get("type", "")).lower() == "rsi"
                    ]
                    if len(rsi_inds) == 1:
                        ind = rsi_inds[0]
                        ind_params = ind.get("params", {}) or {}
                        ind_len = ind_params.get("length", 14)
                        expected_col = f"RSI_{ind_len}"
                        alias = ind.get("alias")
                        series = None
                        if alias and alias in df.columns:
                            series = df[alias]
                        elif expected_col in df.columns:
                            series = df[expected_col]
                        else:
                            # fallback: if exactly one RSI_* column exists, use it
                            rsi_cols = [c for c in df.columns if re.match(r"^RSI_\d+$", str(c))]
                            if len(rsi_cols) == 1:
                                series = df[rsi_cols[0]]
                        if series is not None:
                            for token in referenced_rsi:
                                if token not in local_context:
                                    local_context[token] = series
            except Exception:
                # If mapping fails, let eval raise a clear error later.
                pass

            # Compatibility mapping for MA/ATR/ADX references:
            # Some templates hardcode EMA_20 / SMA_50 / ATR_14 / ADX_14 in logic, while optimization changes the
            # underlying indicator length (changing the computed column name). To keep logic stable during
            # optimization, map referenced tokens to the computed series when unambiguous.
            def _map_length_token(prefix: str, ind_type: str) -> None:
                try:
                    referenced = set(re.findall(rf"\b{re.escape(prefix)}_\d+\b", logic_expr))
                    if not referenced:
                        return

                    inds = [
                        i for i in self.indicators if str(i.get("type", "")).lower() == ind_type
                    ]
                    if not inds:
                        return

                    # Helper: choose series for one indicator
                    def series_for_indicator(ind: Dict[str, Any]) -> Optional[pd.Series]:
                        params = ind.get("params", {}) or {}
                        length = params.get("length")
                        alias = ind.get("alias")
                        if alias and alias in df.columns:
                            return df[alias]
                        if length is not None:
                            col = (
                                f"{prefix}_{int(length)}"
                                if float(length).is_integer()
                                else f"{prefix}_{length}"
                            )
                            if col in df.columns:
                                return df[col]
                        return None

                    # If exactly one indicator of this type exists, map ALL referenced PREFIX_<n> tokens to it.
                    if len(inds) == 1:
                        s = series_for_indicator(inds[0])
                        if s is None:
                            # fallback: if exactly one PREFIX_* column exists, use it
                            cols = [
                                c
                                for c in df.columns
                                if re.match(rf"^{re.escape(prefix)}_\d+$", str(c))
                            ]
                            if len(cols) == 1:
                                s = df[cols[0]]
                        if s is None:
                            return
                        for token in referenced:
                            if token not in local_context:
                                local_context[token] = s
                        return

                    # Multiple indicators: map only when token length matches an indicator length.
                    for token in referenced:
                        if token in local_context:
                            continue
                        m = re.match(rf"^{re.escape(prefix)}_(\d+)$", token)
                        if not m:
                            continue
                        want_len = int(m.group(1))
                        match = None
                        for ind in inds:
                            try:
                                ilen = int((ind.get("params", {}) or {}).get("length"))
                            except Exception:
                                continue
                            if ilen == want_len:
                                match = ind
                                break
                        if match is None:
                            continue
                        s = series_for_indicator(match)
                        if s is not None:
                            local_context[token] = s
                except Exception:
                    return

            _map_length_token("EMA", "ema")
            _map_length_token("SMA", "sma")
            _map_length_token("ATR", "atr")
            _map_length_token("ADX", "adx")

            # Rewrite boolean logic to vectorized operators using AST (prevents precedence bugs).
            # Example: `rsi < 30 and close > ema_fast` becomes `(rsi < 30) & (close > ema_fast)`
            class _VectorizeBoolOps(ast.NodeTransformer):
                def visit_BoolOp(self, node: ast.BoolOp):
                    self.generic_visit(node)
                    if isinstance(node.op, ast.And):
                        expr = node.values[0]
                        for v in node.values[1:]:
                            expr = ast.BinOp(left=expr, op=ast.BitAnd(), right=v)
                        return ast.copy_location(expr, node)
                    if isinstance(node.op, ast.Or):
                        expr = node.values[0]
                        for v in node.values[1:]:
                            expr = ast.BinOp(left=expr, op=ast.BitOr(), right=v)
                        return ast.copy_location(expr, node)
                    return node

                def visit_UnaryOp(self, node: ast.UnaryOp):
                    self.generic_visit(node)
                    if isinstance(node.op, ast.Not):
                        call = ast.Call(
                            func=ast.Name(id="NOT", ctx=ast.Load()),
                            args=[node.operand],
                            keywords=[],
                        )
                        return ast.copy_location(call, node)
                    return node

            parsed = ast.parse(logic_expr, mode="eval")
            rewritten = _VectorizeBoolOps().visit(parsed)
            ast.fix_missing_locations(rewritten)
            code = compile(rewritten, filename="<combo_logic>", mode="eval")

            # Evaluate the logic globally (fast!)
            result = eval(code, {"__builtins__": {}}, local_context)

            if isinstance(result, pd.Series):
                return result.fillna(False).astype(bool)

            # If result is scalar (e.g. "True"), broadcast to Series
            return pd.Series([bool(result)] * len(df), index=df.index)

        except Exception as e:
            # Fallback or strict error
            raise RuntimeError(f"Error evaluating vectorized logic '{logic}': {str(e)}")

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate entry/exit signals based on entry/exit logic and long-side stop loss.

        CRITICAL: Signals are generated AFTER candle close confirmation (TradingView style).
        - Crossover detected on day N → Signal applied on day N+1
        - This ensures we only trade on confirmed crossovers after candle close
        - Signal 1 means strategy entry and -1 means strategy exit. The trade
          extractor maps those phases to buy/sell or sell/cover based on direction.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with 'signal' column (1=entry, -1=exit, 0=hold)
        """
        # Use empty check
        if df.empty:
            df["signal"] = 0
            return df

        # Calculate indicators
        df = self.calculate_indicators(df)

        # Initialize signal column
        df["signal"] = 0
        df["signal_reason"] = ""

        # ---------------------------------------------------------------------
        # OPTIMIZATION: Vectorized Logic Evaluation
        # ---------------------------------------------------------------------
        # Pre-calculate entry and exit masks for the whole dataframe
        # This replaces the O(N^2) row-by-row slicing loop.
        try:
            entry_mask = self._evaluate_logic_vectorized(df, self.entry_logic)
            exit_mask = self._evaluate_logic_vectorized(df, self.exit_logic)
        except Exception as e:
            print(f"Error in vectorized logic: {e}")
            return df

        # Optimization: Early exit if no entries
        if not entry_mask.any():
            return df

        # Iteration is still needed for state management (In Position, Stop Loss),
        # but now we strictly check boolean flags (O(1)) instead of evaluating logic.

        in_position = False
        entry_price = None
        pending_entry = False
        pending_exit = False

        # Pre-convert columns to Numpy arrays for max speed in the loop
        # (Pandas .iloc is slow inside loops)
        close_arr = df["close"].values
        open_arr = df["open"].values
        low_arr = df["low"].values

        entry_bits = entry_mask.values
        exit_bits = exit_mask.values

        # Output signal arrays
        signals = np.zeros(len(df), dtype=int)
        signal_reasons = np.full(len(df), "", dtype=object)

        stop_loss_decimal = self.stop_loss

        for i in range(len(df)):
            # Apply confirmed signals from Previous Candle
            if pending_entry and not in_position:
                signals[i] = 1
                signal_reasons[i] = "entry"
                in_position = True
                entry_price = float(open_arr[i])
                pending_entry = False
                continue

            if pending_exit and in_position:
                signals[i] = -1
                signal_reasons[i] = "exit_logic"
                in_position = False
                entry_price = None
                pending_exit = False
                continue

            # Intra-candle Stop Loss Check (Priority)
            #
            # Short stop loss is handled in the direction-aware trade extractor
            # using candle high above entry. Keeping the old low-based stop here
            # for short would close profitable short moves as losses.
            if self.direction == "long" and in_position and entry_price is not None:
                current_low = float(low_arr[i])
                low_pnl = (current_low - entry_price) / entry_price

                if low_pnl <= -stop_loss_decimal:
                    signals[i] = -1
                    signal_reasons[i] = "stop_loss"
                    in_position = False
                    entry_price = None
                    pending_exit = False
                    continue

            # Logic Check for Signal Confirmation (happens at close)
            # If logic is True at index i (Close of candle i),
            # we set pending flag for index i+1 (Open of candle i+1)

            if i > 0:  # Logic usually requires lookback (shift)
                # Entry Logic
                if not in_position:
                    if entry_bits[i]:
                        pending_entry = True

                # Exit Logic
                elif in_position:
                    if exit_bits[i]:
                        pending_exit = True

        # Write back results
        df["signal"] = signals
        df["signal_reason"] = signal_reasons
        return df

    def get_indicator_columns(self) -> List[str]:
        """
        Get list of indicator column names for chart visualization.

        Returns:
            List of column names
        """
        columns = []

        for indicator in self.indicators:
            ind_type = indicator["type"].lower()
            params = indicator.get("params", {})
            alias = indicator.get("alias")

            if ind_type in ["ema", "sma"]:
                length = params.get("length", 9 if ind_type == "ema" else 20)
                columns.append(alias if alias else f"{ind_type.upper()}_{length}")

            elif ind_type == "rsi":
                length = params.get("length", 14)
                columns.append(f"RSI_{length}")

            elif ind_type == "macd":
                alias_prefix = alias if alias else "MACD"
                columns.extend(
                    [f"{alias_prefix}_macd", f"{alias_prefix}_signal", f"{alias_prefix}_histogram"]
                )

            elif ind_type in ["bbands", "bollinger"]:
                alias_prefix = alias if alias else "BB"
                columns.extend(
                    [f"{alias_prefix}_upper", f"{alias_prefix}_middle", f"{alias_prefix}_lower"]
                )

            elif ind_type == "atr":
                length = params.get("length", 14)
                columns.append(f"ATR_{length}")

            elif ind_type == "adx":
                length = params.get("length", 14)
                columns.append(f"ADX_{length}")

            elif ind_type == "volume_sma":
                length = params.get("length", 20)
                columns.append(alias if alias else f"VOL_SMA_{length}")

        return columns


TRADING_FEE = 0.00075  # Binance 0.075%


def simulate_execution_with_15m(
    df_daily_signals: pd.DataFrame, df_15m: pd.DataFrame, stop_loss: float, direction: str = "long"
) -> List[Dict]:
    """
    Simulate trade execution using 15-minute candles for realistic stop/target validation.

    direction: "long" (default) or "short". Short = stop above entry (high >= stop_price), PnL when price falls.

    CRITICAL PRIORITY RULES:
    - STOP LOSS ALWAYS has priority over exit signals
    - Stop loss is checked FIRST in the period between entry and exit signal

    Args:
        df_daily_signals: DataFrame with 1D candles and signals (indexed by timestamp_utc)
        df_15m: DataFrame with 15m candles (indexed by timestamp_utc)
        stop_loss: Stop loss percentage (e.g., 0.015 for 1.5%)
        direction: "long" or "short"

    Returns:
        List of trade dictionaries with accurate entry/exit times and prices
    """
    trades = []
    stop_loss_pct = float(stop_loss) if stop_loss is not None else 0.0
    is_short = (direction or "long").lower() == "short"

    if df_15m.empty:
        times_15m = np.array([])
        lows_15m = np.array([])
        highs_15m = np.array([])
    else:
        times_15m = df_15m.index
        lows_15m = df_15m["low"].values
        highs_15m = df_15m["high"].values

    # Pre-calculate entry signals
    entry_signals = df_daily_signals[df_daily_signals["signal"] == 1]

    # Pre-calculate ALL exit signals (signal == -1) to avoid repeated filtering
    exit_signals = df_daily_signals[df_daily_signals["signal"] == -1]
    exit_times = exit_signals.index
    # Exit executes at OPEN of daily candle (signal detected at CLOSE of previous candle → execute at OPEN of next day)
    exit_prices = exit_signals["open"].values

    last_exit_time = None

    for entry_time, entry_row in entry_signals.iterrows():
        # 1. Skip if we are still in a position (simulated strictly sequential trades)
        if last_exit_time is not None and entry_time < last_exit_time:
            continue

        entry_price = float(entry_row["open"])
        if is_short:
            exact_stop_price = entry_price * (1 + stop_loss_pct)  # short: stop above entry
        else:
            exact_stop_price = entry_price * (1 - stop_loss_pct)  # long: stop below entry

        next_exit_idx = exit_times.searchsorted(entry_time, side="right")
        if next_exit_idx < len(exit_times):
            signal_exit_time = exit_times[next_exit_idx]
            signal_exit_price = float(exit_prices[next_exit_idx])
            reason_end = "signal"
        else:
            signal_exit_time = df_daily_signals.index[-1] + pd.Timedelta(days=1)
            signal_exit_price = float(df_daily_signals.iloc[-1]["close"])
            reason_end = "end_of_period"

        # 3. PRIORIDADE 1: Intraday stop loss check (high for short, low for long)
        if len(times_15m) > 0:
            start_idx = times_15m.searchsorted(entry_time)
            end_idx = times_15m.searchsorted(signal_exit_time)
            if is_short:
                chunk_ohlc = highs_15m[start_idx:end_idx]
                hit_stop = (
                    stop_loss_pct > 0
                    and chunk_ohlc.size > 0
                    and np.any(chunk_ohlc >= exact_stop_price)
                )
            else:
                chunk_ohlc = lows_15m[start_idx:end_idx]
                hit_stop = (
                    stop_loss_pct > 0
                    and chunk_ohlc.size > 0
                    and np.any(chunk_ohlc <= exact_stop_price)
                )

            if hit_stop and stop_loss_pct > 0 and chunk_ohlc.size > 0:
                if is_short:
                    hit_indices = np.where(chunk_ohlc >= exact_stop_price)[0]
                else:
                    hit_indices = np.where(chunk_ohlc <= exact_stop_price)[0]
                if hit_indices.size > 0:
                    hit_offset = hit_indices[0]
                    first_hit_time = times_15m[start_idx + hit_offset]
                    final_exit_time = pd.Timestamp(first_hit_time)
                    if final_exit_time.tz is None and entry_time.tz is not None:
                        final_exit_time = final_exit_time.tz_localize(entry_time.tz)
                    final_exit_price = exact_stop_price
                    exit_reason = "stop_loss"
                else:
                    final_exit_time = signal_exit_time
                    final_exit_price = signal_exit_price
                    exit_reason = reason_end
            else:
                final_exit_time = signal_exit_time
                final_exit_price = signal_exit_price
                exit_reason = reason_end
        else:
            final_exit_time = signal_exit_time
            final_exit_price = signal_exit_price
            exit_reason = reason_end

        # An open position is not a completed trade.  The old implementation
        # fabricated an exit on the day after the last candle, which could be
        # cached and exposed as a future sell signal by the monitor.
        if exit_reason == "end_of_period":
            continue

        last_exit_time = final_exit_time
        if is_short:
            profit = (
                entry_price * (1 - TRADING_FEE) - float(final_exit_price) * (1 + TRADING_FEE)
            ) / (entry_price * (1 - TRADING_FEE))
        else:
            profit = (
                (final_exit_price * (1 - TRADING_FEE)) - (entry_price * (1 + TRADING_FEE))
            ) / (entry_price * (1 + TRADING_FEE))

        signal_type = "Stop" if exit_reason == "stop_loss" else "Close entry(s) order..."
        trades.append(
            {
                "entry_time": entry_time.isoformat(),
                "entry_price": entry_price,
                "type": "short" if is_short else "long",
                "exit_time": final_exit_time.isoformat(),
                "exit_price": float(final_exit_price),
                "profit": profit,
                "exit_reason": "stop_loss_15m" if exit_reason == "stop_loss" else "signal_15m",
                "signal_type": signal_type,
                "entry_signal_type": "Vender" if is_short else "Comprar",
            }
        )

    # logger.info(f"Deep Backtest complete: {len(trades)} trades extracted")
    return trades


def extract_trades_from_signals(df_with_signals, stop_loss: float, direction: str = "long"):
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
    TRADING_FEE = 0.00075  # Binance spot fee: 0.075%
    trades = []
    position = None
    is_short = (direction or "long").lower() == "short"
    stop_loss_pct = float(stop_loss) if stop_loss is not None else 0.0

    for idx, row in df_with_signals.iterrows():
        # PRIORIDADE 1: Check stop loss FIRST if we have an open position
        if position is not None and stop_loss_pct > 0:
            entry_price = position["entry_price"]
            if is_short:
                exact_stop_price = entry_price * (1 + stop_loss_pct)  # short: stop above entry
                current_high = float(row["high"])
                hit_stop = current_high >= exact_stop_price
            else:
                exact_stop_price = entry_price * (1 - stop_loss_pct)  # long: stop below entry
                current_low = float(row["low"])
                hit_stop = current_low <= exact_stop_price

            if hit_stop:
                position["exit_time"] = idx.isoformat()
                position["exit_price"] = exact_stop_price
                if is_short:
                    # Short PnL: sold at entry*(1-fee), buy back at exit*(1+fee); profit when exit < entry
                    position["profit"] = (
                        entry_price * (1 - TRADING_FEE) - exact_stop_price * (1 + TRADING_FEE)
                    ) / (entry_price * (1 - TRADING_FEE))
                else:
                    position["profit"] = (
                        (exact_stop_price * (1 - TRADING_FEE)) - (entry_price * (1 + TRADING_FEE))
                    ) / (entry_price * (1 + TRADING_FEE))
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
                position["profit"] = (
                    entry_price * (1 - TRADING_FEE) - exit_price * (1 + TRADING_FEE)
                ) / (entry_price * (1 - TRADING_FEE))
            else:
                position["profit"] = (
                    (exit_price * (1 - TRADING_FEE)) - (entry_price * (1 + TRADING_FEE))
                ) / (entry_price * (1 + TRADING_FEE))
            position["exit_reason"] = "signal"
            position["signal_type"] = "Close entry(s) order..."
            trades.append(position)
            position = None

    return trades


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

    Returns:
        List of trades
    """
    df_exec = df_with_signals.copy()

    if not deep_backtest:
        trades = extract_trades_from_signals(df_exec, stop_loss, direction)
        return (trades, "fast_1d") if return_mode else trades

    logger = logging.getLogger(__name__)

    if not symbol or not since_str:
        logger.warning(
            "Deep Backtesting requires symbol and date range. Falling back to fast mode."
        )
        trades = extract_trades_from_signals(df_exec, stop_loss, direction)
        return (trades, "fast_1d") if return_mode else trades

    try:
        if df_15m_cache is not None:
            df_15m = df_15m_cache
        else:
            # Fetch 15m data
            loader = IncrementalLoader()
            df_15m = loader.fetch_intraday_data(
                symbol=symbol,
                timeframe="15m",
                since_str=since_str,
                until_str=until_str,
                read_only=True,
            )

        if df_15m.empty:
            if df_15m_cache is None:  # Only warn if we tried to fetch it
                logger.warning("No 15m data available. Falling back to fast mode.")
            trades = extract_trades_from_signals(df_exec, stop_loss, direction)
            return (trades, "fast_1d") if return_mode else trades

        # Coverage guard: we need 15m for the current day of each trade to simulate stop/target correctly.
        # So 15m must cover the full daily range (same end as daily); otherwise fallback to fast mode.
        try:
            daily_start = df_exec.index.min()
            daily_end = df_exec.index.max()
            intraday_start = df_15m.index.min()
            intraday_end = df_15m.index.max()

            # Some markets start trading partway through the first "day" (listing time).
            # Daily candles are still labeled at 00:00 UTC, but intraday data may begin later that same date
            # (e.g., BTC/USDT starting at 04:00 UTC on the first day). This is NOT a real coverage problem.
            start_ok = True
            if intraday_start > daily_start:
                try:
                    start_ok = intraday_start.date() == daily_start.date()
                except Exception:
                    start_ok = False

            # 15m must extend to at least the last daily candle so we have intraday data for the day of each trade.
            end_ok = intraday_end >= daily_end

            if (not start_ok) or (not end_ok):
                # Log only once per symbol per process to avoid flooding the log (e.g. 16k identical lines)
                warn_key = (symbol,)
                if warn_key not in _deep_coverage_warned:
                    _deep_coverage_warned.add(warn_key)
                    logger.warning(
                        "15m coverage insufficient for deep backtest (%s): daily=[%s..%s] 15m=[%s..%s]. Falling back to fast mode.",
                        symbol,
                        str(daily_start),
                        str(daily_end),
                        str(intraday_start),
                        str(intraday_end),
                    )
                trades = extract_trades_from_signals(df_exec, stop_loss, direction)
                return (trades, "fast_1d") if return_mode else trades
        except Exception:
            logger.warning("Failed to validate 15m coverage; falling back to fast mode.")
            trades = extract_trades_from_signals(df_exec, stop_loss, direction)
            return (trades, "fast_1d") if return_mode else trades

        if df_15m_cache is None:
            logger.info(f"Fetched {len(df_15m)} 15m candles for deep backtest simulation")

        trades = simulate_execution_with_15m(
            df_daily_signals=df_exec, df_15m=df_15m, stop_loss=stop_loss, direction=direction
        )
        return (trades, "deep_15m") if return_mode else trades

    except Exception as e:
        logger.error(f"Error in deep backtest: {e}. Falling back to fast mode.")
        trades = extract_trades_from_signals(df_exec, stop_loss, direction)
        return (trades, "fast_1d") if return_mode else trades


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
):
    """
    Core backtest logic shared by single and batch workers.

    Args:
        initial_capital: Capital inicial em USD para cálculo de métricas (padrão: $100)
                        Usado para calcular Return e Profit Factor no estilo TradingView
    """
    try:
        # Reconstruct strategy logic locally to avoid DB connection in worker
        indicators = template_data["indicators"]
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
        ComboStrategy = LegacyComboStrategy

        strategy = ComboStrategy(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss,
            direction=(params or {}).get("direction", "long"),
        )

        # Generate signals
        df_with_signals = strategy.generate_signals(df.copy())

        # Direction: long (default) or short
        direction = (params or {}).get("direction", "long")
        if direction not in ("long", "short"):
            direction = "long"
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
