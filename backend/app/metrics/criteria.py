"""
Avaliação de critérios GO/NO-GO para estratégias.
"""

import math
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CriteriaResult:
    """Resultado da avaliação GO/NO-GO."""

    status: str  # "GO" ou "NO-GO"
    reasons: List[str]  # Razões para a decisão
    warnings: List[str]  # Avisos (mesmo se GO)


# Critérios padrão para crypto swing trading
DEFAULT_CRITERIA = {
    "min_cagr_vs_bh": 0.0,  # Deve superar ou igualar B&H
    "max_drawdown_pct": 35.0,  # Max DD aceitável
    "critical_drawdown_pct": 45.0,  # NO-GO automático
    "min_calmar_ratio": 1.0,
    "min_profit_factor": 1.3,
    "min_expectancy": 0.0,
    "min_trades": 100,
    "min_sharpe_ratio": 0.8,
    "max_trade_concentration": 0.70,  # 70% do lucro em poucos trades = alerta
    "warning_drawdown_pct": 30.0,  # Aviso se próximo do limite
}

# Perfil do Holdout (OOS): cópia explícita dos demais critérios globais com
# mínimos calibrados para o segmento curto (30% da janela). Não muta
# DEFAULT_CRITERIA; avaliações fora do walk-forward continuam com o default.
OOS_CRITERIA = {
    **DEFAULT_CRITERIA,
    "min_trades": 20,
    "min_sharpe_ratio": 0.30,
}

# Limiar relativo de retenção de Sharpe entre Treino (IS) e Holdout (OOS).
OOS_SHARPE_RETENTION_RATIO = 0.50

# Aviso de amostra pequena no holdout (não bloqueia).
OOS_SMALL_SAMPLE_MAX = 30


def _finite_or_none(metrics: Dict[str, any], key: str) -> Optional[float]:
    """Retorna o valor numérico finito da métrica ou None quando ausente/inválido."""
    value = metrics.get(key)
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def evaluate_walk_forward(
    is_metrics: Dict[str, any], oos_metrics: Dict[str, any]
) -> CriteriaResult:
    """Avalia o gate walk-forward combinado de Treino (IS) e Holdout (OOS).

    Avalia os segmentos separadamente (IS com DEFAULT_CRITERIA, OOS com
    OOS_CRITERIA), exige retenção de ao menos 50% do Sharpe IS no OOS e
    compõe um único CriteriaResult fail-closed: GO somente quando IS, OOS e
    consistência forem aprovados. Razões são ordenadas por IS, OOS e
    consistência, com valores observados e limiares.
    """
    is_metrics = is_metrics or {}
    oos_metrics = oos_metrics or {}

    reasons: List[str] = []
    warnings: List[str] = []
    fail_closed_reasons = []

    is_sharpe = _finite_or_none(is_metrics, "sharpe_ratio")
    is_trades = _finite_or_none(is_metrics, "total_trades")
    oos_sharpe = _finite_or_none(oos_metrics, "sharpe_ratio")
    oos_trades = _finite_or_none(oos_metrics, "total_trades")

    if is_sharpe is None:
        fail_closed_reasons.append(
            "Treino (IS) — NO-GO: métrica obrigatória sharpe_ratio ausente, nula ou não finita."
        )
    if is_trades is None:
        fail_closed_reasons.append(
            "Treino (IS) — NO-GO: métrica obrigatória total_trades ausente, nula ou não finita."
        )
    if oos_sharpe is None:
        fail_closed_reasons.append(
            "Holdout (OOS) — NO-GO: métrica obrigatória sharpe_ratio ausente, nula ou não finita."
        )
    if oos_trades is None:
        fail_closed_reasons.append(
            "Holdout (OOS) — NO-GO: métrica obrigatória total_trades ausente, nula ou não finita."
        )

    # Segmento IS com critérios globais vigentes.
    if is_sharpe is not None and is_trades is not None:
        is_result = evaluate_go_nogo(is_metrics, DEFAULT_CRITERIA)
        if is_result.status != "GO":
            reasons.extend(f"Treino (IS) — {r}" for r in is_result.reasons)
        warnings.extend(f"Treino (IS) — {w}" for w in is_result.warnings)

    # Segmento OOS com perfil próprio.
    if oos_sharpe is not None and oos_trades is not None:
        oos_result = evaluate_go_nogo(oos_metrics, OOS_CRITERIA)
        if oos_result.status != "GO":
            reasons.extend(f"Holdout (OOS) — {r}" for r in oos_result.reasons)
        warnings.extend(f"Holdout (OOS) — {w}" for w in oos_result.warnings)

        # Aviso não bloqueante de amostra pequena (20–29 trades fechados).
        if OOS_CRITERIA["min_trades"] <= oos_trades < OOS_SMALL_SAMPLE_MAX:
            warnings.append(
                f"Holdout (OOS) — aviso: {int(oos_trades)} trades; "
                f"amostra pequena, embora acima do mínimo {OOS_CRITERIA['min_trades']}."
            )

    # Consistência de Sharpe IS→OOS: exige retenção de ao menos 50% do IS,
    # com piso absoluto 0.30 (limiar efetivo max(0.30, 0.50 * IS)).
    if is_sharpe is not None and is_sharpe > 0 and oos_sharpe is not None:
        required_oos = max(
            OOS_CRITERIA["min_sharpe_ratio"],
            OOS_SHARPE_RETENTION_RATIO * is_sharpe,
        )
        if oos_sharpe < required_oos:
            retention_pct = (oos_sharpe / is_sharpe) * 100
            reasons.append(
                f"Consistência IS→OOS — NO-GO: Sharpe caiu de {is_sharpe:.2f} para "
                f"{oos_sharpe:.2f} (retenção {retention_pct:.0f}%; mínimo "
                f"{OOS_SHARPE_RETENTION_RATIO * 100:.0f}%; exigido {required_oos:.2f})."
            )

    all_reasons = fail_closed_reasons + reasons
    status = "GO" if not all_reasons else "NO-GO"
    if status == "GO":
        all_reasons.append("GO walk-forward: Treino (IS), Holdout (OOS) e consistência aprovados.")

    return CriteriaResult(status=status, reasons=all_reasons, warnings=warnings)


def evaluate_go_nogo(
    metrics: Dict[str, any], criteria: Optional[Dict[str, float]] = None
) -> CriteriaResult:
    """
    Avalia se uma estratégia atende aos critérios GO/NO-GO.

    Args:
        metrics: Dict com todas as métricas calculadas
        criteria: Critérios customizados (opcional, usa DEFAULT_CRITERIA se None)

    Returns:
        CriteriaResult com status, razões e avisos
    """
    criteria = criteria or DEFAULT_CRITERIA

    reasons = []
    warnings = []

    # === VERIFICAÇÕES CRÍTICAS (NO-GO AUTOMÁTICO) ===

    # 1. Drawdown crítico
    max_dd = metrics.get("max_drawdown", 0) * 100  # Converter para %
    if max_dd > criteria["critical_drawdown_pct"]:
        reasons.append(
            f"Max Drawdown crítico: {max_dd:.1f}% > {criteria['critical_drawdown_pct']}%"
        )

    # 2. Sharpe muito baixo
    sharpe = metrics.get("sharpe_ratio", 0)
    if sharpe < criteria["min_sharpe_ratio"]:
        reasons.append(
            f"Sharpe Ratio muito baixo: {sharpe:.2f} < {criteria['min_sharpe_ratio']:.2f}"
        )

    # 3. Lucro concentrado em poucos trades
    concentration = metrics.get("trade_concentration", 0)
    if concentration > criteria["max_trade_concentration"]:
        reasons.append(f"Lucro concentrado em poucos trades: {concentration*100:.0f}% em top 10")

    # === VERIFICAÇÕES DE QUALIDADE (GO) ===

    # 4. CAGR vs Buy & Hold
    cagr = metrics.get("cagr", 0)
    bh_cagr = metrics.get("benchmark", {}).get("cagr", 0)

    if cagr <= bh_cagr:
        reasons.append(f"CAGR não supera Buy & Hold: {cagr*100:.1f}% ≤ {bh_cagr*100:.1f}%")

    # 5. Max Drawdown aceitável
    if max_dd > criteria["max_drawdown_pct"]:
        reasons.append(f"Max Drawdown excessivo: {max_dd:.1f}% > {criteria['max_drawdown_pct']}%")

    # 6. Calmar Ratio
    calmar = metrics.get("calmar_ratio", 0)
    if calmar < criteria["min_calmar_ratio"]:
        reasons.append(f"Calmar Ratio baixo: {calmar:.2f} < {criteria['min_calmar_ratio']}")

    # 7. Profit Factor
    pf = metrics.get("profit_factor", 0)
    if pf < criteria["min_profit_factor"]:
        reasons.append(f"Profit Factor baixo: {pf:.2f} < {criteria['min_profit_factor']}")

    # 8. Expectancy
    expectancy = metrics.get("expectancy", 0)
    if expectancy <= criteria["min_expectancy"]:
        reasons.append(f"Expectancy negativa ou zero: ${expectancy:.2f}")

    # 9. Número mínimo de trades
    total_trades = metrics.get("total_trades", 0)
    if total_trades < criteria["min_trades"]:
        reasons.append(
            f"Poucos trades para validação estatística: {total_trades} < {criteria['min_trades']}"
        )

    # === AVISOS (não impedem GO, mas alertam) ===

    # Drawdown próximo do limite
    if max_dd > criteria["warning_drawdown_pct"] and max_dd <= criteria["max_drawdown_pct"]:
        warnings.append(
            f"Max Drawdown próximo ao limite: {max_dd:.1f}% (limite: {criteria['max_drawdown_pct']}%)"
        )

    # Calmar bom mas não excelente
    if calmar >= criteria["min_calmar_ratio"] and calmar < 1.5:
        warnings.append(f"Calmar Ratio aceitável mas não excelente: {calmar:.2f} (excelente: ≥1.5)")

    # Decidir status
    status = "GO" if len(reasons) == 0 else "NO-GO"

    # Se GO, adicionar razões positivas
    if status == "GO":
        positive_reasons = []

        if cagr > bh_cagr:
            alpha = (cagr - bh_cagr) * 100
            positive_reasons.append(f"Supera Buy & Hold em {alpha:.1f}%")

        if max_dd <= criteria["max_drawdown_pct"]:
            positive_reasons.append(
                f"Drawdown aceitável ({max_dd:.1f}% ≤ {criteria['max_drawdown_pct']}%)"
            )

        if calmar >= 1.5:
            positive_reasons.append(f"Calmar Ratio excelente ({calmar:.2f} ≥ 1.5)")
        elif calmar >= criteria["min_calmar_ratio"]:
            positive_reasons.append(
                f"Calmar Ratio bom ({calmar:.2f} ≥ {criteria['min_calmar_ratio']})"
            )

        if pf >= 2.0:
            positive_reasons.append(f"Profit Factor excelente ({pf:.2f})")

        reasons = positive_reasons

    return CriteriaResult(status=status, reasons=reasons, warnings=warnings)
