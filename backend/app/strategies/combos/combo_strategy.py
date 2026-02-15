"""
Base ComboStrategy class for multi-indicator strategies.

This class provides the foundation for combo strategies that combine
multiple indicators with custom entry/exit logic.
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, List, Any, Optional
import re
import ast
from .helpers import HELPER_FUNCTIONS


class ComboStrategy:
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
        stop_gain: Optional[float] = None
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

        self._indicator_cache = {}
        self._validate_aliases()

    def _validate_aliases(self):
        """Validate that all aliases are unique."""
        aliases = [ind.get('alias') for ind in self.indicators if ind.get('alias')]
        if len(aliases) != len(set(aliases)):
            duplicates = [a for a in aliases if aliases.count(a) > 1]
            raise ValueError(f"Duplicate aliases found: {set(duplicates)}")

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all indicators and add them to the dataframe.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with calculated indicators
        """
        # Check cache
        if 'calculated' in self._indicator_cache:
            return self._indicator_cache['calculated'].copy()

        df = df.copy()

        for indicator in self.indicators:
            ind_type = indicator['type'].lower()
            params = indicator.get('params', {})
            alias = indicator.get('alias')

            try:
                if ind_type == 'ema':
                    length = params.get('length', 9)
                    col_name = alias if alias else f'EMA_{length}'
                    df[col_name] = ta.ema(df['close'], length=length)

                elif ind_type == 'sma':
                    length = params.get('length', 20)
                    col_name = alias if alias else f'SMA_{length}'
                    df[col_name] = ta.sma(df['close'], length=length)

                elif ind_type == 'rsi':
                    length = params.get('length', 14)
                    # Keep the traditional RSI_{length} column name for backward-compatible logic,
                    # but also support a stable alias (e.g. "rsi") when provided.
                    col_name = f'RSI_{length}'
                    rsi_series = ta.rsi(df['close'], length=length)
                    df[col_name] = rsi_series
                    if alias and alias != col_name:
                        df[alias] = rsi_series

                elif ind_type == 'macd':
                    fast = params.get('fast', 12)
                    slow = params.get('slow', 26)
                    signal = params.get('signal', 9)
                    alias_prefix = alias if alias else 'MACD'

                    macd_result = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
                    df[f'{alias_prefix}_macd'] = macd_result[f'MACD_{fast}_{slow}_{signal}']
                    df[f'{alias_prefix}_signal'] = macd_result[f'MACDs_{fast}_{slow}_{signal}']
                    df[f'{alias_prefix}_histogram'] = macd_result[f'MACDh_{fast}_{slow}_{signal}']

                elif ind_type == 'bbands' or ind_type == 'bollinger':
                    length = params.get('length', 20)
                    std = params.get('std', 2)
                    alias_prefix = alias if alias else 'BB'

                    bbands_result = ta.bbands(df['close'], length=length, std=std)
                    # Handle potential column name variations (e.g. with .0 suffix)
                    cols = bbands_result.columns.tolist()
                    lower_col = next(c for c in cols if c.startswith(f'BBL_{length}_{std}'))
                    mid_col = next(c for c in cols if c.startswith(f'BBM_{length}_{std}'))
                    upper_col = next(c for c in cols if c.startswith(f'BBU_{length}_{std}'))

                    df[f'{alias_prefix}_upper'] = bbands_result[upper_col]
                    df[f'{alias_prefix}_middle'] = bbands_result[mid_col]
                    df[f'{alias_prefix}_lower'] = bbands_result[lower_col]

                elif ind_type == 'atr':
                    length = params.get('length', 14)
                    col_name = f'ATR_{length}'
                    atr_series = ta.atr(df['high'], df['low'], df['close'], length=length)
                    df[col_name] = atr_series
                    # Support stable alias when provided (e.g. "atr")
                    if alias and alias != col_name:
                        df[alias] = atr_series

                elif ind_type == 'adx':
                    length = params.get('length', 14)
                    col_name = f'ADX_{length}'
                    adx_result = ta.adx(df['high'], df['low'], df['close'], length=length)
                    adx_series = adx_result[f'ADX_{length}']
                    df[col_name] = adx_series
                    # Support stable alias when provided (e.g. "adx")
                    if alias and alias != col_name:
                        df[alias] = adx_series

                elif ind_type == 'roc':
                    length = params.get('length', 20)
                    col_name = f'ROC_{length}'
                    roc_series = ta.roc(df['close'], length=length)
                    df[col_name] = roc_series
                    if alias and alias != col_name:
                        df[alias] = roc_series

                elif ind_type == 'volume_sma':
                    length = params.get('length', 20)
                    col_name = alias if alias else f'VOL_SMA_{length}'
                    df[col_name] = ta.sma(df['volume'], length=length)

            except Exception as e:
                raise RuntimeError(f"Error calculating {ind_type}: {str(e)}")

        # Ensure all columns are numeric to prevent NoneType errors in eval evaluation
        # This handles cases where pandas-ta might return object types with None
        # IMPORTANT: Skip 'regime' column as it contains categorical strings
        for col in df.columns:
            if col == 'regime':  # Preserve regime column
                continue
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Cache the result
        self._indicator_cache['calculated'] = df.copy()

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
            # Some templates use bb.upper / bb.middle / bb.lower. Internally we materialize as
            # bb_upper / bb_middle / bb_lower.
            logic_expr = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\.(upper|middle|lower)\b", r"\1_\2", logic_expr)

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
                    rsi_inds = [i for i in self.indicators if str(i.get("type", "")).lower() == "rsi"]
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

                    inds = [i for i in self.indicators if str(i.get("type", "")).lower() == ind_type]
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
                            col = f"{prefix}_{int(length)}" if float(length).is_integer() else f"{prefix}_{length}"
                            if col in df.columns:
                                return df[col]
                        return None

                    # If exactly one indicator of this type exists, map ALL referenced PREFIX_<n> tokens to it.
                    if len(inds) == 1:
                        s = series_for_indicator(inds[0])
                        if s is None:
                            # fallback: if exactly one PREFIX_* column exists, use it
                            cols = [c for c in df.columns if re.match(rf"^{re.escape(prefix)}_\d+$", str(c))]
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
                        call = ast.Call(func=ast.Name(id="NOT", ctx=ast.Load()), args=[node.operand], keywords=[])
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
        Generate buy/sell signals based on entry/exit logic AND stop loss.

        CRITICAL: Signals are generated AFTER candle close confirmation (TradingView style).
        - Crossover detected on day N → Signal applied on day N+1
        - This ensures we only trade on confirmed crossovers after candle close

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with 'signal' column (1=buy, -1=sell, 0=hold)
        """
        # Use empty check
        if df.empty:
            df['signal'] = 0
            return df

        # Calculate indicators
        df = self.calculate_indicators(df)

        # Initialize signal column
        df['signal'] = 0

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
        close_arr = df['close'].values
        open_arr = df['open'].values
        low_arr = df['low'].values

        entry_bits = entry_mask.values
        exit_bits = exit_mask.values

        # Output signal arrays
        signals = np.zeros(len(df), dtype=int)

        stop_loss_decimal = self.stop_loss

        for i in range(len(df)):
            # Apply confirmed signals from Previous Candle
            if pending_entry and not in_position:
                signals[i] = 1
                in_position = True
                entry_price = float(open_arr[i])
                pending_entry = False
                continue

            if pending_exit and in_position:
                signals[i] = -1
                in_position = False
                entry_price = None
                pending_exit = False
                continue

            # Intra-candle Stop Loss Check (Priority)
            if in_position and entry_price is not None:
                current_low = float(low_arr[i])
                low_pnl = (current_low - entry_price) / entry_price

                if low_pnl <= -stop_loss_decimal:
                    signals[i] = -1
                    in_position = False
                    entry_price = None
                    pending_exit = False
                    continue

            # Logic Check for Signal Confirmation (happens at close)
            # If logic is True at index i (Close of candle i),
            # we set pending flag for index i+1 (Open of candle i+1)

            if i > 0: # Logic usually requires lookback (shift)
                # Entry Logic
                if not in_position:
                    if entry_bits[i]:
                        pending_entry = True

                # Exit Logic
                elif in_position:
                    if exit_bits[i]:
                        pending_exit = True

        # Write back results
        df['signal'] = signals
        return df

    def get_indicator_columns(self) -> List[str]:
        """
        Get list of indicator column names for chart visualization.

        Returns:
            List of column names
        """
        columns = []

        for indicator in self.indicators:
            ind_type = indicator['type'].lower()
            params = indicator.get('params', {})
            alias = indicator.get('alias')

            if ind_type in ['ema', 'sma']:
                length = params.get('length', 9 if ind_type == 'ema' else 20)
                columns.append(alias if alias else f'{ind_type.upper()}_{length}')

            elif ind_type == 'rsi':
                length = params.get('length', 14)
                columns.append(f'RSI_{length}')

            elif ind_type == 'macd':
                alias_prefix = alias if alias else 'MACD'
                columns.extend([
                    f'{alias_prefix}_macd',
                    f'{alias_prefix}_signal',
                    f'{alias_prefix}_histogram'
                ])

            elif ind_type in ['bbands', 'bollinger']:
                alias_prefix = alias if alias else 'BB'
                columns.extend([
                    f'{alias_prefix}_upper',
                    f'{alias_prefix}_middle',
                    f'{alias_prefix}_lower'
                ])

            elif ind_type == 'atr':
                length = params.get('length', 14)
                columns.append(f'ATR_{length}')

            elif ind_type == 'adx':
                length = params.get('length', 14)
                columns.append(f'ADX_{length}')

            elif ind_type == 'volume_sma':
                length = params.get('length', 20)
                columns.append(alias if alias else f'VOL_SMA_{length}')

        return columns
