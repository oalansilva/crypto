"""TA-Lib indicator introspection helper."""

import inspect

from app.services import pandas_ta_inspector


def introspect_talib():
    print("TA-Lib Indicator Introspection")
    print("=" * 60)

    all_indicators = pandas_ta_inspector.get_all_indicators_metadata()
    total = sum(len(v) for v in all_indicators.values())
    print(f"\nTotal callable indicators: {total}")

    sample = ["ema", "sma", "rsi", "macd", "bbands", "atr", "adx", "stoch", "cci"]
    for indicator_name in sample:
        if indicator_name not in all_indicators.get("trend", []) and indicator_name not in all_indicators.get(
            "momentum", []
        ):
            continue

        # Locate descriptor by id
        descriptor = None
        for category_indicators in all_indicators.values():
            for item in category_indicators:
                if item.get("id") == indicator_name:
                    descriptor = item
                    break
            if descriptor:
                break

        if not descriptor:
            continue

        print(f"\n{'='*60}")
        print(f"Indicator: {descriptor['name']}")
        print(f"{'='*60}")
        for param in descriptor.get("params", []):
            print(f" - {param['name']}: default={param.get('default')} type={param.get('type')}")

    print(f"\n\n{'='*60}")
    print("Summary by category:")
    print(f"{'='*60}")
    for category, items in all_indicators.items():
        names = ", ".join(item["id"] for item in items)
        print(f"{category}: {names}")


if __name__ == "__main__":
    introspect_talib()
