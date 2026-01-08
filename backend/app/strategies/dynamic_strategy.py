import pandas as pd
import pandas_ta as ta
import logging

logger = logging.getLogger(__name__)

class DynamicStrategy:
    def __init__(self, config: dict):
        """
        Supports two formats:
        
        1. Full format (original):
        {
            "name": "Custom 1",
            "indicators": [{"kind": "rsi", "length": 14}],
            "entry": "RSI_14 < 30",
            "exit": "RSI_14 > 70"
        }
        
        2. Simplified format (from SimpleBacktestWizard):
        {
            "name": "rsi",
            "length": 14
        }
        """
        self.config = config
        self.name = config.get('name', 'Dynamic')
        
        # DEBUG: Log initial config
        logger.info(f"DEBUG __init__: config={config}")
        logger.info(f"DEBUG __init__: self.name={self.name}")
        
        # Check if it's simplified format (single indicator)
        if 'indicators' not in config and 'name' in config:
            # Simplified format - convert to full format
            indicator_name = config['name'].lower()
            params = {k: v for k, v in config.items() if k != 'name'}
            
            # DEBUG: Log params extraction
            logger.info(f"DEBUG __init__ SIMPLIFIED: indicator_name={indicator_name}, params={params}")
            
            self.indicators_config = [{
                "kind": indicator_name,
                **params
            }]
            
            # DEBUG: Log indicators_config
            logger.info(f"DEBUG __init__ SIMPLIFIED: indicators_config={self.indicators_config}")
            
            # Auto-generate entry/exit based on indicator type
            self.entry_expr, self.exit_expr = self._generate_auto_signals(indicator_name, params)
        else:
            # Full format
            self.indicators_config = config.get('indicators', [])
            self.entry_expr = config.get('entry')
            self.exit_expr = config.get('exit')
            
            # CRITICAL FIX: Allow top-level params to override indicator config
            # This is necessary for optimization where params are passed at top level
            # but the strategy might have been loaded from a JSON file (full format)
            logger.info(f"DEBUG: indicators_config={self.indicators_config}, name={self.name}")
            logger.info(f"DEBUG: Full config keys: {config.keys()}")
            
            if self.indicators_config and self.name:
                top_level_params = {k: v for k, v in config.items() if k not in ['name', 'indicators', 'entry', 'exit']}
                logger.info(f"DEBUG: top_level_params={top_level_params}")
                
                if top_level_params:
                    # Update parameters in the indicators list
                    for ind in self.indicators_config:
                        # If simple strategy (e.g. RSI), assume params belong to it
                        # For now, we just update matching keys
                        for k, v in top_level_params.items():
                             if k in ind or k in ['length', 'std', 'fast', 'slow', 'signal', 'k', 'd']:
                                 ind[k] = v
                    
                    # GENERIC FIX: Regenerate entry/exit expressions when params change
                    # This ensures ALL indicators use the correct parameters from optimization
                    # Assume single indicator strategy (most common case)
                    if len(self.indicators_config) == 1:
                        ind = self.indicators_config[0]
                        indicator_name = ind.get('kind', '').lower()
                        
                        if indicator_name:
                            # Extract params (excluding 'kind')
                            params = {k: v for k, v in ind.items() if k != 'kind' and v is not None}
                            
                            # Regenerate expressions with updated params
                            new_entry, new_exit = self._generate_auto_signals(indicator_name, params)
                            
                            # Update expressions
                            self.entry_expr = new_entry
                            self.exit_expr = new_exit
                            
                            logger.info(f"Regenerated {indicator_name.upper()} expressions with params {params}")
                            logger.info(f"  Entry: {self.entry_expr}")
                            logger.info(f"  Exit: {self.exit_expr}")
                    else:
                        # Multi-indicator strategies - log warning for now
                        logger.warning(f"Multi-indicator strategy detected ({len(self.indicators_config)} indicators). Parameter update may not work correctly.")

    
    def _generate_auto_signals(self, indicator: str, params: dict):
        """Generate default entry/exit signals for common indicators"""
        length = params.get('length', 14)
        
        # Convert float to int if it's a whole number (e.g., 30.0 -> 30)
        if isinstance(length, float) and length.is_integer():
            length = int(length)
        
        # RSI-based signals (simple threshold strategy)
        if indicator == 'rsi':
            col_name = f'RSI_{length}'
            ob = params.get('overbought', 70)
            os_val = params.get('oversold', 30)
            # Use Standard TradingView Logic:
            # Entry: Crossover (RSI crosses Over 30) -> Buy on recovery
            # Exit: Crossunder (RSI crosses Under 70) -> Sell on correction
            # Note: We use a special marker 'crossover' to trigger manual handling below
            return f'crossover({col_name}, {os_val})', f'crossunder({col_name}, {ob})'
        
        # SMA crossover
        elif indicator == 'sma':
            col_name = f'SMA_{length}'
            return f'close > {col_name}', f'close < {col_name}'
        
        # EMA crossover
        elif indicator == 'ema':
            col_name = f'EMA_{length}'
            return f'close > {col_name}', f'close < {col_name}'
        
        # MACD signals
        elif indicator == 'macd':
            fast = params.get('fast', 12)
            slow = params.get('slow', 26)
            signal = params.get('signal', 9)
            # Convert to int if whole numbers
            if isinstance(fast, float) and fast.is_integer():
                fast = int(fast)
            if isinstance(slow, float) and slow.is_integer():
                slow = int(slow)
            if isinstance(signal, float) and signal.is_integer():
                signal = int(signal)
            return f'MACD_{fast}_{slow}_{signal} > MACDs_{fast}_{slow}_{signal}', f'MACD_{fast}_{slow}_{signal} < MACDs_{fast}_{slow}_{signal}'
        
        # Bollinger Bands
        elif indicator == 'bbands':
            # Get std parameter first
            std = params.get('std', 2.0)
            # Use std as fallback for lower/upper if not explicitly provided
            lower_std = params.get('lower_std', std)
            upper_std = params.get('upper_std', std)
            if isinstance(length, float) and length.is_integer():
                length = int(length)
            # Use backticks to handle decimal points in column names
            lower_col = f'BBL_{length}_{lower_std}_{upper_std}'
            upper_col = f'BBU_{length}_{lower_std}_{upper_std}'
            return f'close < `{lower_col}`', f'close > `{upper_col}`'
        
        # Stochastic
        elif indicator in ['stoch', 'stochf']:
            k = params.get('k', 14)
            d = params.get('d', 3)
            if isinstance(k, float) and k.is_integer():
                k = int(k)
            if isinstance(d, float) and d.is_integer():
                d = int(d)
            return f'STOCHk_{k}_{d}_3 < 20', f'STOCHk_{k}_{d}_3 > 80'
        
        # CCI
        elif indicator == 'cci':
            if isinstance(length, float) and length.is_integer():
                length = int(length)
            # CCI column name includes decimal constant, use backticks
            return f'`CCI_{length}_0.015` < -100', f'`CCI_{length}_0.015` > 100'
        
        # Williams %R
        elif indicator == 'willr':
            if isinstance(length, float) and length.is_integer():
                length = int(length)
            return f'WILLR_{length} < -80', f'WILLR_{length} > -20'
        
        # MFI
        elif indicator == 'mfi':
            if isinstance(length, float) and length.is_integer():
                length = int(length)
            return f'MFI_{length} < 20', f'MFI_{length} > 80'
        
        # Default: price crossover with indicator
        else:
            if isinstance(length, float) and length.is_integer():
                length = int(length)
            col_name = f'{indicator.upper()}_{length}'
            return f'close > {col_name}', f'close < {col_name}'
        
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # Create a copy to calculate indicators
        df_sim = df.copy()
        
        # Debug file
        debug_file = 'c:/Users/alans.triggo/OneDrive - Corpay/Documentos/projetos/crypto/backend/signal_debug.log'
        
        # 1. Run Indicators - call them directly
        for ind in self.indicators_config:
            if 'kind' in ind and ind['kind']:
                indicator_name = ind['kind']
                # Filter out null params and 'kind'
                params = {k: v for k, v in ind.items() if k != 'kind' and v is not None}
                
                # DEBUG: Log MACD parameters
                if indicator_name == 'macd':
                    logger.info(f"DEBUG MACD: ind={ind}, params={params}")
                
                # Convert float parameters to int if they're whole numbers
                # This is critical for pandas_ta indicators that use numba
                converted_params = {}
                for k, v in params.items():
                    if isinstance(v, float) and v.is_integer():
                        converted_params[k] = int(v)
                    else:
                        converted_params[k] = v
                
                # DEBUG: Log converted MACD parameters
                if indicator_name == 'macd':
                    logger.info(f"DEBUG MACD: converted_params={converted_params}")
                
                # Call the indicator function directly
                try:
                    # Get the indicator function from pandas_ta
                    indicator_func = getattr(ta, indicator_name, None)
                    if indicator_func:
                        # Determine arguments based on indicator type
                        # OHLC indicators
                        if indicator_name in ['stoch', 'stochf', 'cci', 'willr', 'atr', 'adx', 'supertrend']:
                            result = indicator_func(high=df_sim['high'], low=df_sim['low'], close=df_sim['close'], **converted_params)
                        # Volume indicators (some might need it)
                        elif indicator_name in ['obv', 'mfi', 'ad']:
                            if indicator_name == 'mfi': # MFI needs high, low, close, volume
                                result = indicator_func(high=df_sim['high'], low=df_sim['low'], close=df_sim['close'], volume=df_sim['volume'], **converted_params)
                            elif indicator_name == 'obv': # OBV needs close, volume
                                result = indicator_func(close=df_sim['close'], volume=df_sim['volume'], **converted_params)
                            elif indicator_name == 'ad': # AD needs high, low, close, volume
                                result = indicator_func(high=df_sim['high'], low=df_sim['low'], close=df_sim['close'], volume=df_sim['volume'], **converted_params)
                        # Default to Close price (RSI, SMA, EMA, MACD, BBANDS, etc)
                        else:
                            result = indicator_func(df_sim['close'], **converted_params)
                        
                        # pandas_ta returns Series or DataFrame
                        if isinstance(result, pd.DataFrame):
                            # Merge all columns
                            for col in result.columns:
                                df_sim[col] = result[col]
                        elif isinstance(result, pd.Series):
                            # Single column - use default naming
                            df_sim[result.name] = result
                        
                        # Check for 0-1 scale and normalize to 0-100 if looks like RSI/Stoch
                        if isinstance(result, pd.Series) and result.max() <= 1.05 and result.min() >= -0.05:
                             if indicator_name in ['rsi', 'stoch', 'cci', 'mfi']: # CCI usually isn't 0-1 but check just in case
                                  result = result * 100
                                  # Update in DF
                                  if isinstance(result, pd.Series):
                                      df_sim[result.name] = result

                        # Calculate stats for debug
                        if isinstance(result, pd.Series):
                            stats = f"Min: {result.min():.2f}, Max: {result.max():.2f}, Mean: {result.mean():.2f}, NaNs: {result.isna().sum()}"
                        elif isinstance(result, pd.DataFrame):
                            stats = f"Stats: {result.describe().to_dict()}"
                        else:
                            stats = "N/A"

                        # Check for 0-1 scale and normalize to 0-100 if looks like RSI/Stoch
                        if isinstance(result, pd.Series) and result.max() <= 1.05 and result.min() >= -0.05:
                             if indicator_name in ['rsi', 'stoch', 'cci', 'mfi']: 
                                  result = result * 100
                                  if isinstance(result, pd.Series):
                                      df_sim[result.name] = result
                        
                        # DEBUG: Log columns for BBands
                        if indicator_name == 'bbands':
                             cols = result.columns.tolist() if isinstance(result, pd.DataFrame) else [result.name]
                             lower_band = next((c for c in cols if c.startswith('BBL')), None)
                             upper_band = next((c for c in cols if c.startswith('BBU')), None)
                             
                             if lower_band and upper_band:
                                 # Use bracket notation to avoid syntax errors with decimal points in column names
                                 self.entry_expr = f"close < `{lower_band}`"
                                 self.exit_expr = f"close > `{upper_band}`"
                                 logger.info(f"Updated BBands strategy to: Entry='{self.entry_expr}', Exit='{self.exit_expr}'")
                        
                        # Dynamic MACD Check
                        elif indicator_name == 'macd':
                             cols = result.columns.tolist() if isinstance(result, pd.DataFrame) else [result.name]
                             # MACD usually has 3 cols: MACD (line), MACDh (hist), MACDs (signal)
                             macd_line = next((c for c in cols if c.startswith('MACD_')), None)
                             macd_signal = next((c for c in cols if c.startswith('MACDs_')), None)
                             
                             if macd_line and macd_signal:
                                 self.entry_expr = f"{macd_line} > {macd_signal}"
                                 self.exit_expr = f"{macd_line} < {macd_signal}"
                                 logger.info(f"Updated MACD strategy to: Entry='{self.entry_expr}', Exit='{self.exit_expr}'")

                        # Dynamic Stochastic Check
                        elif indicator_name in ['stoch', 'stochf']:
                             cols = result.columns.tolist() if isinstance(result, pd.DataFrame) else [result.name]
                             k_line = next((c for c in cols if c.startswith('STOCHk_') or c.startswith('STOCHFk_')), None)
                             # d_line = next((c for c in cols if c.startswith('STOCHd_') or c.startswith('STOCHFd_')), None)
                             
                             if k_line:
                                self.entry_expr = f"{k_line} < 20"
                                self.exit_expr = f"{k_line} > 80"
                                logger.info(f"Updated Stoch strategy to: Entry='{self.entry_expr}', Exit='{self.exit_expr}'")

                except Exception as e:
                    logger.error(f"Error calculating indicator '{indicator_name}': {e}")
            
        # 2. Evaluate Signals
        signals = pd.Series(0, index=df_sim.index)
        
        # Manual Crossover Detection Handling
        if self.entry_expr and 'crossover(' in self.entry_expr:
            try:
                # Parse: crossover(RSI_14, 30)
                parts = self.entry_expr.replace('crossover(', '').replace(')', '').split(',')
                col = parts[0].strip()
                val = float(parts[1].strip())
                
                if col in df_sim.columns:
                    series = df_sim[col]
                    # Entry: Cross Over (Series > val AND PrevSeries <= val)
                    entries = (series > val) & (series.shift(1) <= val)
                    signals[entries] = 1
                    logger.info(f"Processed crossover entry for {col} > {val}: {entries.sum()} signals")
                else:
                    logger.warning(f"Column {col} not found for crossover entry")
            except Exception as e:
                logger.error(f"Error processing crossover entry '{self.entry_expr}': {e}")
                
        elif self.entry_expr:
            try:
                entries = df_sim.eval(self.entry_expr)
                signals[entries] = 1
            except Exception as e:
                logger.error(f"Error evaluating entry '{self.entry_expr}': {e}")

        # Manual Crossunder Detection Handling
        if self.exit_expr and 'crossunder(' in self.exit_expr:
             try:
                # Parse: crossunder(RSI_14, 70)
                parts = self.exit_expr.replace('crossunder(', '').replace(')', '').split(',')
                col = parts[0].strip()
                val = float(parts[1].strip())
                
                if col in df_sim.columns:
                    series = df_sim[col]
                    # Exit: Cross Under (Series < val AND PrevSeries >= val)
                    exits = (series < val) & (series.shift(1) >= val) # Standardized to Crossing UNDER
                    signals[exits] = -1
                    logger.info(f"Processed crossunder exit for {col} < {val}: {exits.sum()} signals")
                else:
                    logger.warning(f"Column {col} not found for crossunder exit")
             except Exception as e:
                logger.error(f"Error processing crossunder exit '{self.exit_expr}': {e}")
                
        elif self.exit_expr:
            try:
                exits = df_sim.eval(self.exit_expr)
                signals[exits] = -1
            except Exception as e:
                logger.error(f"Error evaluating exit '{self.exit_expr}': {e}")
        
        # Store simulation data (with indicators) for result access
        self.simulation_data = df_sim
        
        return signals
