import logging

import numpy as np
import pandas as pd
import talib

logger = logging.getLogger(__name__)


class DynamicStrategy:
    def __init__(self, config: dict):
        """
        Supports two formats:

        1) Full format (original):
        {
            "name": "Custom 1",
            "indicators": [{"kind": "rsi", "length": 14}],
            "entry": "RSI_14 < 30",
            "exit": "RSI_14 > 70"
        }

        2) Simplified format (from SimpleBacktestWizard):
        {
            "name": "rsi",
            "length": 14
        }
        """
        self.config = config
        self.name = config.get("name", "Dynamic")

        # Debug-level context
        logger.info("DEBUG __init__: config=%s", config)
        logger.info("DEBUG __init__: self.name=%s", self.name)

        if "indicators" not in config and "name" in config:
            indicator_name = config["name"].lower()
            params = {k: v for k, v in config.items() if k != "name"}

            logger.info("DEBUG __init__ SIMPLIFIED: indicator_name=%s, params=%s", indicator_name, params)
            self.indicators_config = [{"kind": indicator_name, **params}]
            self.entry_expr, self.exit_expr = self._generate_auto_signals(indicator_name, params)
        else:
            self.indicators_config = config.get("indicators", [])
            self.entry_expr = config.get("entry")
            self.exit_expr = config.get("exit")

            logger.info("DEBUG: indicators_config=%s, name=%s", self.indicators_config, self.name)
            logger.info("DEBUG: Full config keys: %s", config.keys())

            if self.indicators_config and self.name:
                top_level_params = {
                    k: v
                    for k, v in config.items()
                    if k not in ["name", "indicators", "entry", "exit"]
                }

                if top_level_params:
                    logger.info("DEBUG: top_level_params=%s", top_level_params)

                    for ind in self.indicators_config:
                        for k, v in top_level_params.items():
                            if k in ind or k in [
                                "length",
                                "std",
                                "fast",
                                "slow",
                                "signal",
                                "k",
                                "d",
                                "smooth_k",
                            ]:
                                ind[k] = v

                    if len(self.indicators_config) == 1:
                        ind = self.indicators_config[0]
                        indicator_name = ind.get("kind", "").lower()

                        if indicator_name:
                            params = {
                                k: v
                                for k, v in ind.items()
                                if k != "kind" and v is not None
                            }

                            new_entry, new_exit = self._generate_auto_signals(
                                indicator_name, params
                            )
                            self.entry_expr = new_entry
                            self.exit_expr = new_exit

                            logger.info(
                                "Regenerated %s expressions with params %s", indicator_name, params
                            )
                            logger.info("  Entry: %s", self.entry_expr)
                            logger.info("  Exit: %s", self.exit_expr)
                    else:
                        logger.warning(
                            "Multi-indicator strategy detected (%s indicators). Parameter update may not work correctly.",
                            len(self.indicators_config),
                        )

    @staticmethod
    def _as_int(value):
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value

    @staticmethod
    def _coerce_series(values, index, name: str):
        if isinstance(values, pd.Series):
            values = values.rename(name)
            values.index = index
            return values
        return pd.Series(values, index=index, name=name)

    @staticmethod
    def _ichimoku_columns(df: pd.DataFrame, tenkan=9, kijun=26, senkou=52):
        close = pd.to_numeric(df["close"], errors="coerce")
        high = pd.to_numeric(df["high"], errors="coerce")
        low = pd.to_numeric(df["low"], errors="coerce")

        def _rolling_mid(series, period):
            return (
                series.rolling(window=period, min_periods=period).max()
                + series.rolling(window=period, min_periods=period).min()
            ) / 2

        its = _rolling_mid(high, tenkan)
        iks = _rolling_mid(low, kijun)
        span_a = ((its + iks) / 2).shift(kijun)
        span_b = _rolling_mid(high, senkou).shift(kijun)
        chikou = close.shift(-kijun)

        return {
            f"ITS_{tenkan}": its,
            f"IKS_{kijun}": iks,
            f"ISA_{tenkan}": span_a,
            f"ISB_{kijun}": span_b,
            f"ICHI_{tenkan}_{kijun}_{senkou}": chikou,
        }

    def _generate_auto_signals(self, indicator: str, params: dict):
        """Generate default entry/exit signals for common indicators."""
        indicator = (indicator or "").lower()
        length = self._as_int(params.get("length", 14))

        if indicator == "rsi":
            col_name = f"RSI_{length}"
            ob = params.get("oversold", 70)
            os_val = params.get("overbought", 30)
            return f"crossover({col_name}, {os_val})", f"crossunder({col_name}, {ob})"

        if indicator == "sma":
            col_name = f"SMA_{length}"
            return f"close > {col_name}", f"close < {col_name}"

        if indicator == "ema":
            col_name = f"EMA_{length}"
            return f"close > {col_name}", f"close < {col_name}"

        if indicator == "macd":
            fast = self._as_int(params.get("fast", 12))
            slow = self._as_int(params.get("slow", 26))
            signal = self._as_int(params.get("signal", 9))
            return (
                f"MACD_{fast}_{slow}_{signal} > MACDs_{fast}_{slow}_{signal}",
                f"MACD_{fast}_{slow}_{signal} < MACDs_{fast}_{slow}_{signal}",
            )

        if indicator == "bbands":
            std = params.get("std", 2.0)
            lower_std = params.get("lower_std", std)
            upper_std = params.get("upper_std", std)
            lower_col = f"BBL_{length}_{lower_std}_{upper_std}"
            upper_col = f"BBU_{length}_{lower_std}_{upper_std}"
            return f"close < `{lower_col}`", f"close > `{upper_col}`"

        if indicator in ["stoch", "stochf"]:
            k = self._as_int(params.get("k", 14))
            d = self._as_int(params.get("d", 3))
            smooth_k = self._as_int(params.get("smooth_k", 3))
            return f"STOCH{k}_{d}_{smooth_k} < 20", f"STOCH{k}_{d}_{smooth_k} > 80"

        if indicator == "cci":
            c = params.get("c", 0.015)
            return f"CCI_{length}_{c} < -100", f"CCI_{length}_{c} > 100"

        if indicator == "willr":
            return f"WILLR_{length} < -80", f"WILLR_{length} > -20"

        if indicator == "mfi":
            return f"MFI_{length} < 20", f"MFI_{length} > 80"

        if indicator == "ichimoku":
            tenkan = self._as_int(params.get("tenkan") or 9)
            kijun = self._as_int(params.get("kijun") or 26)
            senkou = self._as_int(params.get("senkou") or 52)
            return (
                f"(ITS_{tenkan} > IKS_{kijun}) & (close > ISA_{tenkan}) & (close > ISB_{kijun})",
                f"(ITS_{tenkan} < IKS_{kijun}) & (close < ISA_{tenkan}) & (close < ISB_{kijun})",
            )

        col_name = f"{indicator.upper()}_{length}"
        return f"close > {col_name}", f"close < {col_name}"

    def _add_ichimoku_columns(self, df_sim: pd.DataFrame, params: dict):
        tenkan = self._as_int(params.get("tenkan") or 9)
        kijun = self._as_int(params.get("kijun") or 26)
        senkou = self._as_int(params.get("senkou") or 52)

        converted = {"tenkan": tenkan, "kijun": kijun, "senkou": senkou}
        converted = {k: v for k, v in converted.items() if isinstance(v, (int, float, np.integer))}
        if len(converted) != 3:
            tenkan = 9
            kijun = 26
            senkou = 52

        values = self._ichimoku_columns(df_sim, tenkan=tenkan, kijun=kijun, senkou=senkou)
        for name, series in values.items():
            df_sim[name] = series

    def _add_bands(self, df_sim: pd.DataFrame, name: str, df_values: pd.Series):
        df_sim[name] = df_values

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df_sim = df.copy()

        for ind in self.indicators_config:
            if "kind" not in ind or not ind["kind"]:
                continue

            indicator_name = str(ind["kind"]).lower()
            params = {k: v for k, v in ind.items() if k != "kind" and v is not None}

            close = pd.to_numeric(df_sim["close"], errors="coerce")
            high = pd.to_numeric(df_sim["high"], errors="coerce")
            low = pd.to_numeric(df_sim["low"], errors="coerce")
            volume = pd.to_numeric(df_sim["volume"], errors="coerce")

            # Normalize params
            normalized_params = {}
            for key, value in params.items():
                normalized_params[key] = (
                    self._as_int(value) if isinstance(value, float) else value
                )

            try:
                if indicator_name in ["ema", "sma", "wma", "dema", "tema"]:
                    period = self._as_int(normalized_params.get("length", 14))
                    if not isinstance(period, (int, np.integer)) or period <= 0:
                        raise ValueError(f"Invalid period for {indicator_name}: {period}")

                    if indicator_name == "ema":
                        values = talib.EMA(close, timeperiod=period)
                        df_sim[f"EMA_{period}"] = self._coerce_series(values, df_sim.index, f"EMA_{period}")
                    elif indicator_name == "sma":
                        values = talib.SMA(close, timeperiod=period)
                        df_sim[f"SMA_{period}"] = self._coerce_series(values, df_sim.index, f"SMA_{period}")
                    elif indicator_name == "wma":
                        values = talib.WMA(close, timeperiod=period)
                        df_sim[f"WMA_{period}"] = self._coerce_series(values, df_sim.index, f"WMA_{period}")
                    elif indicator_name == "dema":
                        values = talib.DEMA(close, timeperiod=period)
                        df_sim[f"DEMA_{period}"] = self._coerce_series(values, df_sim.index, f"DEMA_{period}")
                    else:
                        values = talib.TEMA(close, timeperiod=period)
                        df_sim[f"TEMA_{period}"] = self._coerce_series(values, df_sim.index, f"TEMA_{period}")

                elif indicator_name == "rsi":
                    length = self._as_int(normalized_params.get("length", 14))
                    values = talib.RSI(close, timeperiod=length)
                    df_sim[f"RSI_{length}"] = self._coerce_series(values, df_sim.index, f"RSI_{length}")

                elif indicator_name == "macd":
                    fast = self._as_int(normalized_params.get("fast", 12))
                    slow = self._as_int(normalized_params.get("slow", 26))
                    signal = self._as_int(normalized_params.get("signal", 9))

                    macd, macdsignal, _ = talib.MACD(
                        close,
                        fastperiod=fast,
                        slowperiod=slow,
                        signalperiod=signal,
                    )

                    df_sim[f"MACD_{fast}_{slow}_{signal}"] = self._coerce_series(
                        macd, df_sim.index, f"MACD_{fast}_{slow}_{signal}"
                    )
                    df_sim[f"MACDs_{fast}_{slow}_{signal}"] = self._coerce_series(
                        macdsignal, df_sim.index, f"MACDs_{fast}_{slow}_{signal}"
                    )

                elif indicator_name == "bbands":
                    length = self._as_int(normalized_params.get("length", 20))
                    std = float(normalized_params.get("std", 2.0))
                    upper, middle, lower = talib.BBANDS(
                        close,
                        timeperiod=length,
                        nbdevup=std,
                        nbdevdn=std,
                        matype=0,
                    )

                    label = f"{length}_{std}_{std}"
                    df_sim[f"BBU_{label}"] = self._coerce_series(
                        upper, df_sim.index, f"BBU_{label}"
                    )
                    df_sim[f"BBM_{label}"] = self._coerce_series(
                        middle, df_sim.index, f"BBM_{label}"
                    )
                    df_sim[f"BBL_{label}"] = self._coerce_series(
                        lower, df_sim.index, f"BBL_{label}"
                    )

                elif indicator_name in ["stoch", "stochf"]:
                    length = self._as_int(normalized_params.get("length", 14))
                    k = self._as_int(normalized_params.get("k", 14))
                    d = self._as_int(normalized_params.get("d", 3))
                    smooth_k = self._as_int(normalized_params.get("smooth_k", 3))

                    if indicator_name == "stoch":
                        k_line, d_line = talib.STOCH(
                            high,
                            low,
                            close,
                            fastk_period=k,
                            slowk_period=smooth_k,
                            slowk_matype=0,
                            slowd_period=d,
                            slowd_matype=0,
                        )
                        k_name = f"STOCH{k}_{d}_{smooth_k}"
                        d_name = f"STOCHd_{k}_{d}_{smooth_k}"
                    else:
                        k_line, d_line = talib.STOCHF(
                            high,
                            low,
                            close,
                            fastk_period=k,
                            fastd_period=d,
                            fastd_matype=0,
                        )
                        k_name = f"STOCHFk_{k}_{d}_{smooth_k}"
                        d_name = f"STOCHFd_{k}_{d}_{smooth_k}"

                    if indicator_name == "stoch":
                        d_name = f"STOCHd_{k}_{d}_{smooth_k}"

                    df_sim[k_name] = self._coerce_series(k_line, df_sim.index, k_name)
                    df_sim[d_name] = self._coerce_series(d_line, df_sim.index, d_name)

                elif indicator_name == "cci":
                    length = self._as_int(normalized_params.get("length", 14))
                    c = normalized_params.get("c", 0.015)
                    cci = talib.CCI(high, low, close, timeperiod=length)
                    df_sim[f"CCI_{length}_{c}"] = self._coerce_series(
                        cci, df_sim.index, f"CCI_{length}_{c}"
                    )

                elif indicator_name == "willr":
                    length = self._as_int(normalized_params.get("length", 14))
                    willr = talib.WILLR(high, low, close, timeperiod=length)
                    df_sim[f"WILLR_{length}"] = self._coerce_series(
                        willr, df_sim.index, f"WILLR_{length}"
                    )

                elif indicator_name == "mfi":
                    length = self._as_int(normalized_params.get("length", 14))
                    mfi = talib.MFI(high, low, close, volume, timeperiod=length)
                    df_sim[f"MFI_{length}"] = self._coerce_series(
                        mfi, df_sim.index, f"MFI_{length}"
                    )

                elif indicator_name == "atr":
                    length = self._as_int(normalized_params.get("length", 14))
                    atr = talib.ATR(high, low, close, timeperiod=length)
                    df_sim[f"ATR_{length}"] = self._coerce_series(atr, df_sim.index, f"ATR_{length}")

                elif indicator_name == "adx":
                    length = self._as_int(normalized_params.get("length", 14))
                    adx = talib.ADX(high, low, close, timeperiod=length)
                    df_sim[f"ADX_{length}"] = self._coerce_series(adx, df_sim.index, f"ADX_{length}")

                elif indicator_name == "obv":
                    obv = talib.OBV(close, volume)
                    df_sim["OBV"] = self._coerce_series(obv, df_sim.index, "OBV")

                elif indicator_name == "ad":
                    ad = talib.AD(high, low, close, volume)
                    df_sim["AD"] = self._coerce_series(ad, df_sim.index, "AD")

                elif indicator_name == "ichimoku":
                    self._add_ichimoku_columns(df_sim, normalized_params)

                elif indicator_name == "ema_sma":
                    # Keep backwards compatibility if caller passes this synthetic form.
                    period = self._as_int(normalized_params.get("length", 14))
                    df_sim[f"EMA_{period}"] = self._coerce_series(
                        talib.EMA(close, timeperiod=period),
                        df_sim.index,
                        f"EMA_{period}",
                    )
                else:
                    length = self._as_int(normalized_params.get("length", 14))
                    name = f"{indicator_name.upper()}_{length}"
                    df_sim[name] = self._coerce_series(
                        talib.SMA(close, timeperiod=length),
                        df_sim.index,
                        name,
                    )

                # Ensure column names for BBANDS and stochastic variants match signal expressions
                if indicator_name == "bbands":
                    std = float(normalized_params.get("std", 2.0))
                    length = self._as_int(normalized_params.get("length", 20))
                    label = f"{length}_{std}_{std}"
                    if "entry_expr" in locals() and "BBL_" in self.entry_expr:
                        current = self.entry_expr
                        if current:
                            self.entry_expr = f"close < `BBL_{label}`"
                            self.exit_expr = f"close > `BBU_{label}`"

            except Exception as e:  # pragma: no cover
                logger.error("Error calculating indicator '%s': %s", indicator_name, e)

        signals = pd.Series(0, index=df_sim.index)

        if self.entry_expr and "crossover(" in self.entry_expr:
            try:
                parts = self.entry_expr.replace("crossover(", "").replace(")", "").split(",")
                col = parts[0].strip()
                val = float(parts[1].strip())
                if col in df_sim.columns:
                    series = pd.to_numeric(df_sim[col], errors="coerce")
                    entries = (series > val) & (series.shift(1) <= val)
                    signals[entries] = 1
                else:
                    logger.warning("Column %s not found for crossover entry", col)
            except Exception as e:
                logger.error("Error processing crossover entry '%s': %s", self.entry_expr, e)
        elif self.entry_expr:
            try:
                signals[df_sim.eval(self.entry_expr)] = 1
            except Exception as e:
                logger.error("Error evaluating entry '%s': %s", self.entry_expr, e)

        if self.exit_expr and "crossunder(" in self.exit_expr:
            try:
                parts = self.exit_expr.replace("crossunder(", "").replace(")", "").split(",")
                col = parts[0].strip()
                val = float(parts[1].strip())
                if col in df_sim.columns:
                    series = pd.to_numeric(df_sim[col], errors="coerce")
                    exits = (series < val) & (series.shift(1) >= val)
                    signals[exits] = -1
                else:
                    logger.warning("Column %s not found for crossunder exit", col)
            except Exception as e:
                logger.error("Error processing crossunder exit '%s': %s", self.exit_expr, e)
        elif self.exit_expr:
            try:
                signals[df_sim.eval(self.exit_expr)] = -1
            except Exception as e:
                logger.error("Error evaluating exit '%s': %s", self.exit_expr, e)

        self.simulation_data = df_sim
        return signals
