"""Public trader-facing strategy names and descriptions."""

from __future__ import annotations

import re
from typing import Any

PUBLIC_STRATEGY_DISPLAY_NAMES: dict[str, str] = {
    "multi_ma_crossover": "Virada de Tendência",
    "multi_ma_crossoverv2": "Tendência Confirmada",
    "ema_rsi": "Pulso de Momentum",
    "ema_macd_volume": "Força com Volume",
    "bollinger_rsi_adx": "Retorno ao Equilíbrio",
    "volume_atr_breakout": "Rompimento com Volatilidade",
    "ema_rsi_fibonacci": "Pullback de Retomada",
    "short_ema200_pullback": "Repique em Tendência de Baixa",
    "bollinger_breakout": "Expansão de Volatilidade",
    "macd_cross": "Mudança de Momentum",
    "rsi_ema_scalping": "Leitura Rápida de Movimento",
    "example: breakout with volume": "Rompimento com Volume",
    "example: scalping ema 5/13": "Leitura Ágil de Curto Prazo",
    "example: swing rsi divergence": "Reversão de Swing",
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
}

SENSITIVE_NAME_PATTERN = re.compile(
    r"(\d|ema|sma|rsi|macd|adx|atr|bollinger|fibonacci|entry|exit|threshold|logic)",
    re.IGNORECASE,
)


def normalize_strategy_key(name: Any) -> str:
    return str(name or "").strip().lower().replace("-", "_")


def public_strategy_display_name(name: Any) -> str:
    """Return a safe product name for visible strategy identity."""

    key = normalize_strategy_key(name)
    if key in PUBLIC_STRATEGY_DISPLAY_NAMES:
        return PUBLIC_STRATEGY_DISPLAY_NAMES[key]

    raw = str(name or "").strip()
    if not raw:
        return "Estratégia Protegida"
    if SENSITIVE_NAME_PATTERN.search(raw):
        return "Estratégia Protegida"

    parts = raw.replace("-", "_").split("_")
    normalized = [part[:1].upper() + part[1:] for part in parts if part.strip()]
    return " ".join(normalized) or "Estratégia Protegida"


def public_strategy_description(name: Any, raw_description: Any = None) -> str:
    """Return safe, high-level copy for users without exposing parameters."""

    key = normalize_strategy_key(name)
    if key in PUBLIC_STRATEGY_DESCRIPTIONS:
        return PUBLIC_STRATEGY_DESCRIPTIONS[key]

    return (
        "Estratégia configurada para apoiar decisões de entrada e saída com regras protegidas "
        "no sistema. Avalie junto ao histórico, ao contexto do ativo e ao seu controle de risco."
    )
