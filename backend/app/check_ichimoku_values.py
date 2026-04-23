import pandas as pd
import numpy as np


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


def check_ichimoku_sensitivity():
    print("Creating dummy data...")
    np.random.seed(42)
    close = np.random.randn(200).cumsum() + 100
    high = close + 2
    low = close - 2

    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000})

    print("Calculating senkou=52...")
    res1 = build_ichimoku(df["high"], df["low"], df["close"], tenkan=9, kijun=26, senkou=52)
    isb1 = res1["ISB"]

    print("Calculating senkou=60...")
    res2 = build_ichimoku(df["high"], df["low"], df["close"], tenkan=9, kijun=26, senkou=60)
    isb2 = res2["ISB"]

    diff = (isb1 - isb2).abs().sum()
    print(f"\nDifference sum between ISB(52) and ISB(60): {diff}")

    if diff == 0:
        print("CRITICAL: ISB values are IDENTICAL! 'senkou' parameter is being IGNORED!")
    else:
        print("SUCCESS: ISB values are different. 'senkou' parameter is working.")


if __name__ == "__main__":
    check_ichimoku_sensitivity()
