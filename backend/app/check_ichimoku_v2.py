import pandas as pd
import logging


def _rolling_mid(series, period):
    return (
        series.rolling(window=period, min_periods=period).max()
        + series.rolling(window=period, min_periods=period).min()
    ) / 2


def build_ichimoku(high: pd.Series, low: pd.Series, close: pd.Series, tenkan=9, kijun=26, senkou=52):
    its = _rolling_mid(high, tenkan)
    iks = _rolling_mid(low, kijun)
    isa = ((its + iks) / 2).shift(kijun)
    isb = _rolling_mid(high, senkou).shift(kijun)
    ichi = close.shift(-kijun)

    return {
        "ITS": its,
        "IKS": iks,
        "ISA": isa,
        "ISB": isb,
        "ICHI": ichi,
    }


logging.basicConfig(level=logging.INFO)


def debug_ichimoku():
    print("Creating dummy data...")
    df = pd.DataFrame(
        {
            "open": [100] * 200,
            "high": [110] * 200,
            "low": [90] * 200,
            "close": [100] * 200,
            "volume": [1000] * 200,
        }
    )

    tenkan = 10
    kijun = 30
    senkou = 60

    print(f"Calculating Ichimoku with tenkan={tenkan}, kijun={kijun}, senkou={senkou}")

    values = build_ichimoku(df["high"], df["low"], df["close"], tenkan=tenkan, kijun=kijun, senkou=senkou)
    result = pd.DataFrame(
        {
            "ITS_10": values["ITS"],
            "IKS_30": values["IKS"],
            "ISA_10_30": values["ISA"],
            "ISB_30": values["ISB"],
            "ICHI_10": values["ICHI"],
        }
    )

    print("\n--- Result Structure ---")
    print("Columns:", list(result.columns))


if __name__ == "__main__":
    debug_ichimoku()
