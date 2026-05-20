from app.services.strategy_descriptions import (
    public_strategy_description,
    public_strategy_display_name,
)

SENSITIVE_COPY_TOKENS = (
    "ema200",
    "ema21",
    "ema50",
    "rsi 45",
    "45-70",
    "0.618",
    "entry_logic",
    "exit_logic",
)


def test_known_strategy_description_is_public_and_high_level():
    description = public_strategy_description(
        "short_ema200_pullback",
        "Short-only: bearish trend with EMA200, EMA21, EMA50, RSI 45-70.",
    )

    assert "venda" in description.lower()
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_known_strategy_display_name_is_product_copy():
    assert public_strategy_display_name("short_ema200_pullback") == "Repique em Tendência de Baixa"
    assert public_strategy_display_name("ema_rsi") == "Pulso de Momentum"


def test_unknown_sensitive_strategy_display_name_is_protected():
    assert public_strategy_display_name("ema_9_sma_50_rsi_30_70") == "Estratégia Protegida"


def test_unknown_strategy_description_uses_safe_fallback():
    description = public_strategy_description(
        "custom_template",
        "Uses EMA 9, SMA 50, RSI 30-70 and entry_logic to recreate the strategy.",
    )

    assert "regras protegidas" in description
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)
