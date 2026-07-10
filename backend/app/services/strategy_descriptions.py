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
    "ema_rsi_fibonacci": "EMA + RSI: Retomada de Tendência",
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
    "quant_btc_1d_ema_roc_rsi_guard_long_v2_20260607": "Momentum BTC: Continuidade com Guard RSI",
    "quant_btc_1d_ma_trend_chain_w1_20260607": "Médias BTC: Tendência com Risco Menor",
    "quant_btc_1d_ma_trend_chain_w2_20260607": "Médias BTC: Tendência com Saída Ágil",
    "quant_btc_1d_ma_trend_chain_w3_20260607": "Médias BTC: Tendência com Defesa Reforçada",
    "quant_btc_1d_ema_roc_rsi_chain_w4_20260607": "Momentum BTC: Tendência com Força Relativa",
    "quant_btc_1d_ma_trend_chain_w5_20260607": "Médias BTC: Continuidade Defensiva",
    "quant_btc_1d_short_macd_bear_chain_w1_20260629": "MACD BTC: Baixa Controlada",
    "quant_btc_1d_short_ma_breakdown_chain_w2_20260629": "Médias BTC: Quebra de Baixa Defensiva",
    "quant_btc_1d_short_ma_breakdown_chain_w3_20260629": "Médias BTC: Continuidade de Baixa",
    "quant_btc_1d_short_ma_defense_chain_w4_20260629": "Médias BTC: Baixa Protegida",
    "quant_btc_1d_short_macd_defense_chain_w5_20260629": "MACD BTC: Baixa Defensiva",
    "quant_btc_1d_long_bb_roc_chain_w1_20260629": "Bandas + ROC BTC: Rompimento Defensivo",
    "quant_btc_1d_long_dual_momentum_chain_w2_20260629": "Momentum BTC: Continuidade Dupla",
    "quant_btc_1d_long_dual_momentum_chain_w3_20260629": "Momentum BTC: Aceleração Dupla",
    "quant_btc_1d_long_ma_breakout_chain_w4_20260629": "Médias BTC: Rompimento Confirmado",
    "quant_btc_1d_long_ma_trend_chain_w5_20260629": "Médias BTC: Continuidade Forte",
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
        "Combina uma média exponencial com RSI para observar direção e força relativa em possíveis retomadas. Serve como apoio à decisão, sem promessa de resultado."
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
    "example_breakout_with_volume": (
        "Procura rompimentos que ganham participação do mercado. Deve ser usada como apoio para comparar cenários, não como promessa de acerto."
    ),
    "example_scalping_ema_5_13": (
        "Apoia leituras curtas e rápidas para quem acompanha o movimento de perto. Não revela a configuração técnica usada."
    ),
    "example_swing_rsi_divergence": (
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
    "quant_btc_1d_ema_roc_rsi_guard_long_v2_20260607": (
        "Acompanha continuidade do BTC quando tendência, momentum e força relativa convergem, com proteção para reduzir entradas em contexto fraco. Use como apoio e sempre confira risco e histórico."
    ),
    "quant_btc_1d_ma_trend_chain_w1_20260607": (
        "Acompanha viradas de tendência do BTC em 1D com filtro de médias e controle de risco para reduzir quedas frente ao benchmark. Use como apoio e sempre confira risco e histórico."
    ),
    "quant_btc_1d_ma_trend_chain_w2_20260607": (
        "Acompanha continuidade do BTC em 1D com leitura de médias e saída mais ágil quando o movimento perde força. Use como apoio e sempre confira risco e histórico."
    ),
    "quant_btc_1d_ma_trend_chain_w3_20260607": (
        "Filtra tendências do BTC em 1D com médias próximas e proteção reforçada para buscar melhora de drawdown sem abandonar retorno. Use como apoio e sempre confira risco e histórico."
    ),
    "quant_btc_1d_ema_roc_rsi_chain_w4_20260607": (
        "Combina tendência, momentum e força relativa do BTC em 1D para buscar continuidade com queda menor na cadeia. Use como apoio e sempre confira risco e histórico."
    ),
    "quant_btc_1d_ma_trend_chain_w5_20260607": (
        "Acompanha continuidade defensiva do BTC em 1D com médias e controle de risco ajustado para superar a cadeia anterior. Use como apoio e sempre confira risco e histórico."
    ),
    "quant_btc_1d_short_macd_bear_chain_w1_20260629": (
        "Acompanha movimentos de baixa do BTC em 1D quando tendência e momentum favorecem operação Short, com saída para reduzir exposição quando a pressão vendedora perde força."
    ),
    "quant_btc_1d_short_ma_breakdown_chain_w2_20260629": (
        "Busca quebras de tendência do BTC em 1D para operações Short, combinando médias e controle de risco para melhorar a cadeia sem usar fallback Long."
    ),
    "quant_btc_1d_short_ma_breakdown_chain_w3_20260629": (
        "Filtra continuações de baixa do BTC em 1D com médias e stop ajustado para aumentar retorno e reduzir drawdown frente às vencedoras Short anteriores."
    ),
    "quant_btc_1d_short_ma_defense_chain_w4_20260629": (
        "Acompanha quedas do BTC em 1D com leitura defensiva de médias, priorizando melhora sequencial de drawdown em uma operação exclusivamente Short."
    ),
    "quant_btc_1d_short_macd_defense_chain_w5_20260629": (
        "Combina tendência e momentum de baixa do BTC em 1D para operação Short com perfil mais defensivo que a cadeia anterior e saída quando o regime enfraquece."
    ),
    "quant_btc_1d_long_bb_roc_chain_w1_20260629": (
        "Acompanha rompimentos Long do BTC em 1D quando volatilidade e momentum sugerem retomada, com controle de risco para formar o primeiro degrau defensivo da cadeia."
    ),
    "quant_btc_1d_long_dual_momentum_chain_w2_20260629": (
        "Combina duas leituras de momentum e tendência do BTC em 1D para buscar continuidade Long acima do primeiro degrau, mantendo controle de queda."
    ),
    "quant_btc_1d_long_dual_momentum_chain_w3_20260629": (
        "Usa uma configuração Long de momentum mais acelerada para o BTC em 1D, buscando ampliar retorno frente ao degrau anterior sem piorar drawdown."
    ),
    "quant_btc_1d_long_ma_breakout_chain_w4_20260629": (
        "Filtra rompimentos Long do BTC em 1D com médias e confirmação de força para melhorar qualidade e retorno na sequência da cadeia."
    ),
    "quant_btc_1d_long_ma_trend_chain_w5_20260629": (
        "Acompanha continuidade Long forte do BTC em 1D com médias e saída defensiva, buscando fechar a cadeia com retorno maior e drawdown menor."
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
