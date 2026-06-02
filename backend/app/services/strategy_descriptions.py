"""Public trader-facing strategy names and descriptions."""

from __future__ import annotations

import re
from typing import Any

PUBLIC_STRATEGY_DISPLAY_NAMES: dict[str, str] = {
    "multi_ma_crossover": "Médias Móveis: Tendência em Virada",
    "multi_ma_crossoverv2": "Médias Móveis: Tendência Confirmada",
    "ema_rsi": "RSI: Retomada com Força",
    "ema_macd_volume": "MACD + Volume: Movimento com Confirmação",
    "bollinger_rsi_adx": "Bandas + RSI: Retorno ao Equilíbrio",
    "volume_atr_breakout": "Volume + Volatilidade: Rompimento com Pressão",
    "ema_rsi_fibonacci": "Fibonacci: Recuo de Retomada",
    "short_ema200_pullback": "Médias Móveis: Repique de Baixa",
    "bollinger_breakout": "Bandas: Expansão de Volatilidade",
    "macd_cross": "MACD: Mudança de Ritmo",
    "rsi_ema_scalping": "RSI: Movimento Curto",
    "example_breakout_with_volume": "Volume: Rompimento com Pressão",
    "example_scalping_ema_5_13": "Médias Móveis: Leitura Ágil",
    "example_swing_rsi_divergence": "RSI: Virada de Swing",
    "quant_btc_1d_roc_ema_momentum_guard_long_v3": "Momentum BTC: Continuidade Protegida",
    "quant_btc_roc_ema_momentum_guard_long_v3": "Momentum BTC: Continuidade Protegida",
    "quant_btc_1d_adx_momentum_guard_long_v1": "Momentum BTC: Continuidade com Regime",
    "quant_btc_1d_ema_roc_trend_rider_long_v1": "Momentum BTC: Continuidade Equilibrada",
    "quant_btc_1d_ema_roc_rsi_regime_long_v2_20260601": "Momentum BTC: Continuidade com Filtro RSI",
    "quant_btc_1d_volume_momentum_pressure_long_v1": "Volume + Momentum: Continuidade com Pressão",
    "quant_btc_1d_macd_ema_roc_quality_long_v1_20260601": "MACD BTC: Continuidade com Risco Controlado",
    "quant_btc_1d_bbands_ema_rsi_quality_long_v1_20260602": "Bandas BTC: Continuidade com Qualidade",
    "quant_btc_1d_ema_roc_rsi_quality_guard_long_v1_20260602": "Momentum BTC: Continuidade com Filtro de Qualidade",
}

PUBLIC_STRATEGY_DESCRIPTIONS: dict[str, str] = {
    "multi_ma_crossover": (
        "Acompanha mudanças de direção para apoiar decisões quando o mercado mostra virada de tendência. Use como sinal de contexto, sempre conferindo risco e histórico antes de agir."
    ),
    "multi_ma_crossoverv2": (
        "Filtra movimentos direcionais e procura momentos em que a tendência parece ganhar confirmação. Ajuda a comparar oportunidades sem prometer continuidade do movimento."
    ),
    "ema_rsi": (
        "Observa força e fôlego do movimento para indicar quando uma retomada pode estar se formando. Serve como apoio para avaliar entrada, não como recomendação automática."
    ),
    "ema_macd_volume": (
        "Prioriza movimentos em que direção, força e participação do mercado parecem convergir. Útil para acompanhar tendências com confirmação ampla, sem garantia de resultado."
    ),
    "bollinger_rsi_adx": (
        "Busca leituras de possível retorno ao equilíbrio depois de movimentos esticados. Ajuda a separar exagero de mercado de tendência persistente."
    ),
    "volume_atr_breakout": (
        "Acompanha rompimentos quando preço, volume e volatilidade sugerem aceleração. Deve ser validada junto ao risco, pois rompimentos podem falhar."
    ),
    "ema_rsi_fibonacci": (
        "Observa recuos dentro de uma direção principal para identificar possíveis retomadas. Ajuda a estudar continuidade, sem expor a receita técnica da leitura."
    ),
    "short_ema200_pullback": (
        "Acompanha repiques contra uma direção principal de baixa para apoiar decisões de venda. Use apenas como leitura de contexto e com atenção ao risco."
    ),
    "bollinger_breakout": (
        "Observa momentos em que a volatilidade começa a expandir e pode abrir espaço para rompimento. Não substitui avaliação de risco e confirmação."
    ),
    "macd_cross": (
        "Acompanha mudanças de momentum para indicar quando a força do movimento pode estar mudando de lado."
    ),
    "rsi_ema_scalping": (
        "Foca leituras rápidas de curto prazo para apoiar decisões em movimentos mais ágeis. Exige acompanhamento próximo e controle de risco."
    ),
    "example: breakout with volume": (
        "Procura rompimentos que ganham participação do mercado. Deve ser usada como apoio para comparar cenários, não como promessa de acerto."
    ),
    "example: scalping ema 5/13": (
        "Apoia leituras curtas e rápidas para quem acompanha o movimento de perto. Não revela a configuração técnica usada."
    ),
    "example: swing rsi divergence": (
        "Observa sinais de enfraquecimento do movimento para estudar possíveis reversões em operações de swing."
    ),
    "quant_btc_1d_roc_ema_momentum_guard_long_v3": (
        "Acompanha a força direcional do BTC com filtros de proteção para evitar entradas em contexto fraco. Use como apoio para avaliar continuidade, sempre conferindo risco e histórico."
    ),
    "quant_btc_roc_ema_momentum_guard_long_v3": (
        "Acompanha a força direcional do BTC com filtros de proteção para evitar entradas em contexto fraco. Use como apoio para avaliar continuidade, sempre conferindo risco e histórico."
    ),
    "quant_btc_1d_adx_momentum_guard_long_v1": (
        "Usa leituras de momentum, tendência e regime de mercado para avaliar continuidade no BTC. Serve como apoio à decisão e deve ser comparada com histórico, contexto do ativo e risco."
    ),
    "quant_btc_1d_ema_roc_trend_rider_long_v1": (
        "Acompanha continuidade do BTC com leitura de tendência e força direcional, priorizando equilíbrio entre retorno e controle de risco. Pode sofrer em mercados laterais ou muito erráticos."
    ),
    "quant_btc_1d_ema_roc_rsi_regime_long_v2_20260601": (
        "Acompanha continuidade do BTC com filtro adicional de regime para evitar entradas fracas ou esticadas. Serve como apoio de leitura e deve ser comparada com histórico, contexto do ativo e risco."
    ),
    "quant_btc_1d_volume_momentum_pressure_long_v1": (
        "Observa continuidade do BTC quando força direcional e participação do mercado parecem convergir. Serve como apoio de leitura e pode sofrer quando o volume não confirma o movimento."
    ),
    "quant_btc_1d_macd_ema_roc_quality_long_v1_20260601": (
        "Acompanha continuidade do BTC combinando leitura de tendência, momentum e confirmação direcional para buscar avanço com controle de risco. Serve como apoio de leitura e deve ser comparada com histórico, contexto do ativo e risco."
    ),
    "quant_btc_1d_bbands_ema_rsi_quality_long_v1_20260602": (
        "Acompanha continuidade do BTC com filtros de tendência, volatilidade e qualidade de regime para evitar entradas fracas ou esticadas. Serve como apoio de leitura e deve ser comparada com histórico, contexto do ativo e risco."
    ),
    "quant_btc_1d_ema_roc_rsi_quality_guard_long_v1_20260602": (
        "Acompanha continuidade do BTC com filtro adicional de qualidade para evitar entradas fracas ou esticadas. Serve como apoio de leitura e deve ser comparada com histórico, contexto do ativo e risco."
    ),
}

SENSITIVE_NAME_PATTERN = re.compile(
    r"(\d|ema|sma|rsi|macd|adx|atr|bollinger|fibonacci|entry|exit|threshold|logic)",
    re.IGNORECASE,
)


def normalize_strategy_key(name: Any) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(name or "").strip().lower())
    return normalized.strip("_")


def public_strategy_display_name(name: Any) -> str:
    """Return a safe product name for visible strategy identity."""

    key = normalize_strategy_key(name)
    if key in PUBLIC_STRATEGY_DISPLAY_NAMES:
        return PUBLIC_STRATEGY_DISPLAY_NAMES[key]

    return "Estratégia Cripto Farol"


def public_strategy_description(name: Any, raw_description: Any = None) -> str:
    """Return safe, high-level copy for users without exposing parameters."""

    key = normalize_strategy_key(name)
    if key in PUBLIC_STRATEGY_DESCRIPTIONS:
        return PUBLIC_STRATEGY_DESCRIPTIONS[key]

    return (
        "Estratégia configurada para apoiar decisões de entrada e saída com regras protegidas "
        "no sistema. Avalie junto ao histórico, ao contexto do ativo e ao seu controle de risco."
    )
