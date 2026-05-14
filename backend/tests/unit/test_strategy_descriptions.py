from app.services.strategy_descriptions import public_strategy_description


def test_known_strategy_description_is_public_and_high_level():
    description = public_strategy_description(
        "short_ema200_pullback",
        "Short-only: bearish trend with EMA200, EMA21, EMA50, RSI 45-70.",
    )

    assert "vendas" in description.lower()
    assert "rsi 45" not in description.lower()


def test_unknown_strategy_description_uses_safe_fallback():
    description = public_strategy_description("custom_template", "")

    assert "regras salvas" in description
