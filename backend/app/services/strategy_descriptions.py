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
    "quant_btc_1d_roc_ema_momentum_guard_long_v3": "BTC 1D Long — ROC + EMA: Impulso Filtrado",
    "quant_btc_roc_ema_momentum_guard_long_v3": "BTC Long — ROC + EMA: Força Direcional",
    "quant_btc_1d_adx_momentum_guard_long_v1": "BTC 1D Long — ADX: Regime de Tendência",
    "quant_btc_1d_ema_roc_rsi_guard_long_v2_20260607": "BTC 1D Long — EMA + ROC + RSI: Continuidade",
    "quant_btc_1d_ma_trend_chain_w1_20260607": "BTC 1D Long — Médias: Virada Inicial",
    "quant_btc_1d_ma_trend_chain_w2_20260607": "BTC 1D Long — Médias: Saída Rápida",
    "quant_btc_1d_ma_trend_chain_w3_20260607": "BTC 1D Long — Médias: Tendência Compacta",
    "quant_btc_1d_ema_roc_rsi_chain_w4_20260607": "BTC 1D Long — EMA + ROC + RSI: Força Relativa",
    "quant_btc_1d_ma_trend_chain_w5_20260607": "BTC 1D Long — Médias: Continuidade Ampla",
    "quant_btc_1d_short_macd_bear_chain_w1_20260629": "BTC 1D Short — MACD: Pressão Vendedora",
    "quant_btc_1d_short_ma_breakdown_chain_w2_20260629": "BTC 1D Short — Médias: Quebra 52",
    "quant_btc_1d_short_ma_breakdown_chain_w3_20260629": "BTC 1D Short — Médias: Quebra 58",
    "quant_btc_1d_short_ma_defense_chain_w4_20260629": "BTC 1D Short — Médias: Defesa Intermediária",
    "quant_btc_1d_short_macd_defense_chain_w5_20260629": "BTC 1D Short — MACD + RSI: Defesa Estrita",
    "quant_btc_1d_long_bb_roc_chain_w1_20260629": "BTC 1D Long — Bandas + ROC: Expansão",
    "quant_btc_1d_long_dual_momentum_chain_w2_20260629": "BTC 1D Long — ROC Duplo: Tendência Longa",
    "quant_btc_1d_long_dual_momentum_chain_w3_20260629": "BTC 1D Long — ROC Duplo: Tendência Rápida",
    "quant_btc_1d_long_ma_breakout_chain_w4_20260629": "BTC 1D Long — Médias + ROC: Cruzamento",
    "quant_btc_1d_long_ma_trend_chain_w5_20260629": "BTC 1D Long — Médias: Alinhamento Triplo",
}

PUBLIC_STRATEGY_DESCRIPTIONS: dict[str, str] = {
    "multi_ma_crossover": (
        "Compara médias de velocidades diferentes e entra quando a média curta assume a liderança sobre a tendência longa; encerra quando essa hierarquia se desfaz."
    ),
    "multi_ma_crossoverv2": (
        "Exige alinhamento entre médias curta, intermediária e longa para confirmar tendência; a perda do alinhamento aciona a saída."
    ),
    "ema_rsi": (
        "Combina preço acima da média exponencial com recuperação do RSI para buscar retomadas compradoras; sai quando tendência ou força relativa cedem."
    ),
    "ema_macd_volume": (
        "Confirma direção pela média, aceleração pelo MACD e participação pelo volume antes da entrada; reduz exposição quando momentum ou tendência revertem."
    ),
    "bollinger_rsi_adx": (
        "Procura retorno à média após preço tocar uma banda extrema, validando exaustão pelo RSI e intensidade do regime pelo ADX."
    ),
    "volume_atr_breakout": (
        "Opera expansão de faixa quando o preço rompe a máxima recente com volume acima da média e volatilidade suficiente; sai na perda do rompimento."
    ),
    "ema_rsi_fibonacci": (
        "Busca retomada compradora quando o fechamento supera a média exponencial e o RSI recupera força; sai se preço ou força relativa perdem confirmação."
    ),
    "short_ema200_pullback": (
        "Busca venda Short em repiques dentro de tendência principal de baixa quando preço retorna às médias, o RSI está na faixa definida e o candle confirma rejeição vendedora."
    ),
    "bollinger_breakout": (
        "Entra quando o fechamento supera a banda superior em expansão e encerra no retorno ao centro da faixa ou perda de impulso."
    ),
    "macd_cross": (
        "Usa o cruzamento da linha MACD com sua linha de sinal para marcar mudança de momentum e o cruzamento oposto para encerrar."
    ),
    "rsi_ema_scalping": (
        "Combina média exponencial curta e RSI para capturar impulsos breves, com saída rápida quando o preço perde a média ou o oscilador esfria."
    ),
    "example_breakout_with_volume": (
        "Valida rompimento de preço somente quando o volume confirma participação acima da referência recente e sai se o preço volta à faixa anterior."
    ),
    "example_scalping_ema_5_13": (
        "Opera cruzamentos entre duas médias exponenciais curtas para capturar deslocamentos rápidos e reverte a posição no cruzamento contrário."
    ),
    "example_swing_rsi_divergence": (
        "Compara extremos do preço e do RSI para identificar divergência em horizonte de swing, encerrando quando a reversão perde confirmação."
    ),
    "quant_btc_1d_roc_ema_momentum_guard_long_v3": (
        "No BTC diário, abre Long quando preço acima da EMA e ROC positivo confirmam impulso; sai na perda da tendência ou do momentum."
    ),
    "quant_btc_roc_ema_momentum_guard_long_v3": (
        "Abre Long no BTC quando tendência por EMA e aceleração por ROC apontam na mesma direção, encerrando assim que um dos dois filtros falha."
    ),
    "quant_btc_1d_adx_momentum_guard_long_v1": (
        "No BTC diário, condiciona o Long a tendência, momentum e ADX compatíveis com regime direcional; sai quando força ou direção deixam de confirmar."
    ),
    "quant_btc_1d_ema_roc_rsi_guard_long_v2_20260607": (
        "No BTC em 1D, exige preço acima da EMA, ROC positivo e RSI acima do piso de força para abrir Long; fecha na perda da EMA ou do piso de saída."
    ),
    "quant_btc_1d_ma_trend_chain_w1_20260607": (
        "No BTC em 1D, abre Long quando a média curta cruza a longa e já se mantém acima dela; encerra no cruzamento baixista da média longa."
    ),
    "quant_btc_1d_ma_trend_chain_w2_20260607": (
        "No BTC em 1D, combina cruzamento da média curta sobre médias intermediária ou longa e usa a perda da longa como saída rápida do Long."
    ),
    "quant_btc_1d_ma_trend_chain_w3_20260607": (
        "No BTC em 1D, usa médias de períodos próximos para reagir cedo à virada de alta e encerra o Long quando a média curta cruza abaixo da longa."
    ),
    "quant_btc_1d_ema_roc_rsi_chain_w4_20260607": (
        "No BTC em 1D, abre Long apenas com preço acima da EMA, ROC positivo e RSI forte; sai se preço ou força relativa perderem seus filtros."
    ),
    "quant_btc_1d_ma_trend_chain_w5_20260607": (
        "No BTC em 1D, confirma Long pelo cruzamento da média curta sobre a intermediária ou longa e protege a posição no cruzamento baixista da longa."
    ),
    "quant_btc_1d_short_macd_bear_chain_w1_20260629": (
        "No BTC em 1D, abre Short com preço abaixo da EMA, histograma MACD negativo e RSI fraco; recompra quando qualquer um desses sinais reverte."
    ),
    "quant_btc_1d_short_ma_breakdown_chain_w2_20260629": (
        "No BTC em 1D, abre Short quando a média rápida está abaixo da lenta e cruza sob a intermediária ou a lenta; recompra nos cruzamentos opostos."
    ),
    "quant_btc_1d_short_ma_breakdown_chain_w3_20260629": (
        "No BTC em 1D, mantém a mesma confirmação Short por cruzamentos, mas usa uma média lenta mais longa para filtrar quebras menos persistentes."
    ),
    "quant_btc_1d_short_ma_defense_chain_w4_20260629": (
        "No BTC em 1D, abre Short após cruzamento baixista da média rápida, usando uma referência intermediária mais lenta para reduzir trocas prematuras."
    ),
    "quant_btc_1d_short_macd_defense_chain_w5_20260629": (
        "No BTC em 1D, abre Short quando EMA, MACD e RSI confirmam pressão vendedora; recompra cedo quando força relativa ou momentum reage."
    ),
    "quant_btc_1d_long_bb_roc_chain_w1_20260629": (
        "No BTC em 1D, abre Long acima da banda superior com ROC dentro do filtro de impulso e sai no retorno à banda central ou ROC negativo."
    ),
    "quant_btc_1d_long_dual_momentum_chain_w2_20260629": (
        "No BTC em 1D, abre Long com EMA rápida acima da lenta e ROC curto superior ao ROC longo, exigindo momentum estrutural positivo."
    ),
    "quant_btc_1d_long_dual_momentum_chain_w3_20260629": (
        "No BTC em 1D, usa EMAs e ROCs mais rápidos para antecipar aceleração Long; sai na inversão das médias ou na perda do ROC curto."
    ),
    "quant_btc_1d_long_ma_breakout_chain_w4_20260629": (
        "No BTC em 1D, abre Long quando preço está sobre a média de tendência, a EMA cruza para cima e o ROC confirma força; sai na perda da EMA ou do ROC."
    ),
    "quant_btc_1d_long_ma_trend_chain_w5_20260629": (
        "No BTC em 1D, exige alinhamento e cruzamento entre três médias para abrir Long; encerra quando a média rápida cruza abaixo da referência longa."
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


def public_strategy_catalog_name(name: Any) -> str:
    """Catalog label: friendly display name when mapped, otherwise the raw name."""

    key = normalize_strategy_key(name)
    mapped = PUBLIC_STRATEGY_DISPLAY_NAMES.get(key)
    if mapped:
        return mapped
    return str(name or "").strip() or "Estratégia"


def public_strategy_description(name: Any, raw_description: Any = None) -> str:
    """Return safe, high-level copy for users without exposing parameters."""

    key = normalize_strategy_key(name)
    if key in PUBLIC_STRATEGY_DESCRIPTIONS:
        return PUBLIC_STRATEGY_DESCRIPTIONS[key]

    return (
        "Estratégia configurada para apoiar decisões de entrada e saída com regras protegidas "
        "no sistema. Avalie junto ao histórico, ao contexto do ativo e ao seu controle de risco."
    )
