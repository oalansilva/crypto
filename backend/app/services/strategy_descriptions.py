"""Public trader-facing strategy descriptions."""

from __future__ import annotations

from typing import Any

PUBLIC_STRATEGY_DESCRIPTIONS: dict[str, str] = {
    "multi_ma_crossover": (
        "Segue a tendência usando médias móveis para indicar quando a força de compra ou venda muda."
    ),
    "multi_ma_crossoverv2": (
        "Busca movimentos de tendência com médias móveis e filtro de direção antes de sinalizar entrada ou saída."
    ),
    "ema_rsi": (
        "Combina tendência e força do movimento para procurar entradas com confirmação de momentum."
    ),
    "ema_macd_volume": (
        "Procura movimentos de tendência confirmados por momentum e aumento de volume."
    ),
    "bollinger_rsi_adx": (
        "Busca oportunidades de retorno ao preço médio quando o ativo estica demais dentro do contexto de tendência."
    ),
    "volume_atr_breakout": (
        "Observa rompimentos com volume e volatilidade para capturar movimentos mais fortes."
    ),
    "ema_rsi_fibonacci": (
        "Procura pullbacks em tendência usando força do movimento e regiões prováveis de retomada."
    ),
    "short_ema200_pullback": (
        "Busca vendas em repiques contra uma tendência principal de baixa, com gestão por stop."
    ),
    "bollinger_breakout": (
        "Observa expansão de volatilidade nas Bandas de Bollinger para identificar rompimentos."
    ),
    "macd_cross": ("Usa cruzamentos de MACD para acompanhar mudanças de momentum na tendência."),
    "rsi_ema_scalping": (
        "Combina RSI e médias curtas para leituras rápidas em movimentos de curto prazo."
    ),
    "example: breakout with volume": (
        "Procura rompimentos de preço que ganham confirmação pelo aumento de volume."
    ),
    "example: scalping ema 5/13": (
        "Usa médias rápidas para capturar movimentos curtos com resposta ágil."
    ),
    "example: swing rsi divergence": (
        "Procura divergências de RSI para antecipar possíveis viradas em operações de swing."
    ),
}


def normalize_strategy_key(name: Any) -> str:
    return str(name or "").strip().lower().replace("-", "_")


def public_strategy_description(name: Any, raw_description: Any = None) -> str:
    """Return safe, high-level copy for users without exposing parameters."""

    key = normalize_strategy_key(name)
    if key in PUBLIC_STRATEGY_DESCRIPTIONS:
        return PUBLIC_STRATEGY_DESCRIPTIONS[key]

    raw = str(raw_description or "").strip()
    if not raw:
        return "Estratégia configurada para avaliar entradas e saídas com regras salvas no sistema."

    first_sentence = raw.split(".")[0].strip()
    if not first_sentence:
        return "Estratégia configurada para avaliar entradas e saídas com regras salvas no sistema."

    if len(first_sentence) > 180:
        first_sentence = first_sentence[:177].rstrip() + "..."
    return first_sentence
