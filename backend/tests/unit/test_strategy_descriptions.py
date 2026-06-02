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
    assert (
        public_strategy_display_name("short_ema200_pullback") == "Médias Móveis: Repique de Baixa"
    )
    assert public_strategy_display_name("ema_rsi") == "RSI: Retomada com Força"
    assert (
        public_strategy_display_name("multi_ma_crossover") == "Médias Móveis: Tendência em Virada"
    )


def test_generated_quant_strategy_has_safe_product_copy():
    raw_name = "Quant BTC ROC+EMA Momentum Guard Long v3"
    description = public_strategy_description(raw_name)

    assert public_strategy_display_name(raw_name) == "Momentum BTC: Continuidade Protegida"
    assert "força direcional do btc" in description.lower()
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_adx_momentum_guard_strategy_has_safe_product_copy():
    raw_name = "quant_btc_1d_adx_momentum_guard_long_v1"
    description = public_strategy_description(raw_name)

    assert public_strategy_display_name(raw_name) == "Momentum BTC: Continuidade com Regime"
    assert "regime de mercado" in description.lower()
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_ema_roc_trend_rider_strategy_has_safe_product_copy():
    raw_name = "quant_btc_1d_ema_roc_trend_rider_long_v1"
    description = public_strategy_description(raw_name)

    assert public_strategy_display_name(raw_name) == "Momentum BTC: Continuidade Equilibrada"
    assert "controle de risco" in description.lower()
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_ema_roc_rsi_regime_strategy_has_safe_product_copy():
    raw_name = "quant_btc_1d_ema_roc_rsi_regime_long_v2_20260601"
    description = public_strategy_description(raw_name)

    assert public_strategy_display_name(raw_name) == "Momentum BTC: Continuidade com Filtro RSI"
    assert "filtro adicional de regime" in description.lower()
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_volume_momentum_pressure_strategy_has_safe_product_copy():
    raw_name = "quant_btc_1d_volume_momentum_pressure_long_v1"
    description = public_strategy_description(raw_name)

    assert public_strategy_display_name(raw_name) == "Volume + Momentum: Continuidade com Pressão"
    assert "participação do mercado" in description.lower()
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_macd_ema_roc_quality_strategy_has_safe_product_copy():
    raw_name = "quant_btc_1d_macd_ema_roc_quality_long_v1_20260601"
    description = public_strategy_description(raw_name)

    assert (
        public_strategy_display_name(raw_name)
        == "MACD BTC: Continuidade com Risco Controlado"
    )
    assert "confirmação direcional" in description.lower()
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_bbands_ema_rsi_quality_strategy_has_safe_product_copy():
    raw_name = "quant_btc_1d_bbands_ema_rsi_quality_long_v1_20260602"
    description = public_strategy_description(raw_name)

    assert public_strategy_display_name(raw_name) == "Bandas BTC: Continuidade com Qualidade"
    assert "qualidade de regime" in description.lower()
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_ema_roc_rsi_quality_guard_strategy_has_safe_product_copy():
    raw_name = "quant_btc_1d_ema_roc_rsi_quality_guard_long_v1_20260602"
    description = public_strategy_description(raw_name)

    assert (
        public_strategy_display_name(raw_name)
        == "Momentum BTC: Continuidade com Filtro de Qualidade"
    )
    assert "filtro adicional de qualidade" in description.lower()
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_unknown_sensitive_strategy_display_name_is_protected():
    assert public_strategy_display_name("ema_9_sma_50_rsi_30_70") == "Estratégia Cripto Farol"


def test_unknown_strategy_description_uses_safe_fallback():
    description = public_strategy_description(
        "custom_template",
        "Uses EMA 9, SMA 50, RSI 30-70 and entry_logic to recreate the strategy.",
    )

    assert "regras protegidas" in description
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)
