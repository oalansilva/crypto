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


def test_ema_roc_rsi_guard_strategy_has_safe_product_copy():
    raw_name = "quant_btc_1d_ema_roc_rsi_guard_long_v2_20260607"
    description = public_strategy_description(raw_name)

    assert public_strategy_display_name(raw_name) == "Momentum BTC: Continuidade com Guard RSI"
    assert "continuidade do btc" in description.lower()
    assert "força relativa" in description.lower()
    assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_card_262_chain_winners_have_safe_product_copy():
    expected = {
        "quant_btc_1d_ma_trend_chain_w1_20260607": "BTC 1D WINNER 1: Médias com Risco Menor",
        "quant_btc_1d_ma_trend_chain_w2_20260607": "BTC 1D WINNER 2: Médias com Saída Ágil",
        "quant_btc_1d_ma_trend_chain_w3_20260607": "BTC 1D WINNER 3: Médias com Defesa Reforçada",
        "quant_btc_1d_ema_roc_rsi_chain_w4_20260607": "BTC 1D WINNER 4: Momentum com Força Relativa",
        "quant_btc_1d_ma_trend_chain_w5_20260607": "BTC 1D WINNER 5: Médias com Continuidade Defensiva",
    }

    for strategy_name, display_name in expected.items():
        description = public_strategy_description(strategy_name)

        assert public_strategy_display_name(strategy_name) == display_name
        assert "btc em 1d" in description.lower()
        assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_card_276_short_chain_winners_have_safe_product_copy():
    expected = {
        "quant_btc_1d_short_macd_bear_chain_w1_20260629": "BTC 1D SHORT WINNER 1: MACD de Baixa Controlada",
        "quant_btc_1d_short_ma_breakdown_chain_w2_20260629": "BTC 1D SHORT WINNER 2: Médias de Quebra Defensiva",
        "quant_btc_1d_short_ma_breakdown_chain_w3_20260629": "BTC 1D SHORT WINNER 3: Médias de Baixa com Menor Queda",
        "quant_btc_1d_short_ma_defense_chain_w4_20260629": "BTC 1D SHORT WINNER 4: Médias de Baixa Protegida",
        "quant_btc_1d_short_macd_defense_chain_w5_20260629": "BTC 1D SHORT WINNER 5: MACD Short Defensivo",
    }

    for strategy_name, display_name in expected.items():
        description = public_strategy_description(strategy_name)

        assert public_strategy_display_name(strategy_name) == display_name
        assert "short" in display_name.lower()
        assert "short" in description.lower()
        assert all(token not in description.lower() for token in SENSITIVE_COPY_TOKENS)


def test_card_277_long_chain_winners_have_safe_product_copy():
    expected = {
        "quant_btc_1d_long_bb_roc_chain_w1_20260629": "BTC 1D LONG WINNER 1: Bandas com Rompimento Defensivo",
        "quant_btc_1d_long_dual_momentum_chain_w2_20260629": "BTC 1D LONG WINNER 2: Momentum Duplo de Continuidade",
        "quant_btc_1d_long_dual_momentum_chain_w3_20260629": "BTC 1D LONG WINNER 3: Momentum Duplo Acelerado",
        "quant_btc_1d_long_ma_breakout_chain_w4_20260629": "BTC 1D LONG WINNER 4: Médias com Rompimento Confirmado",
        "quant_btc_1d_long_ma_trend_chain_w5_20260629": "BTC 1D LONG WINNER 5: Médias com Continuidade Forte",
    }

    for strategy_name, display_name in expected.items():
        description = public_strategy_description(strategy_name)

        assert public_strategy_display_name(strategy_name) == display_name
        assert "long" in display_name.lower()
        assert "long" in description.lower()
        assert "btc em 1d" in description.lower()
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
