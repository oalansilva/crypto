"""
Avaliação de critérios GO/NO-GO para estratégias.
"""

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
    'min_cagr_vs_bh': 0.0,  # Deve superar ou igualar B&H
    'max_drawdown_pct': 35.0,  # Max DD aceitável
    'critical_drawdown_pct': 45.0,  # NO-GO automático
    'min_calmar_ratio': 1.0,
    'min_profit_factor': 1.3,
    'min_expectancy': 0.0,
    'min_trades': 100,
    'min_sharpe_ratio': 0.8,
    'max_trade_concentration': 0.70,  # 70% do lucro em poucos trades = alerta
    'warning_drawdown_pct': 30.0,  # Aviso se próximo do limite
}


def evaluate_go_nogo(
    metrics: Dict[str, any],
    criteria: Optional[Dict[str, float]] = None
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
    max_dd = metrics.get('max_drawdown', 0) * 100  # Converter para %
    if max_dd > criteria['critical_drawdown_pct']:
        reasons.append(
            f"Max Drawdown crítico: {max_dd:.1f}% > {criteria['critical_drawdown_pct']}%"
        )
    
    # 2. Sharpe muito baixo
    sharpe = metrics.get('sharpe_ratio', 0)
    if sharpe < criteria['min_sharpe_ratio']:
        reasons.append(
            f"Sharpe Ratio muito baixo: {sharpe:.2f} < {criteria['min_sharpe_ratio']}"
        )
    
    # 3. Lucro concentrado em poucos trades
    concentration = metrics.get('trade_concentration', 0)
    if concentration > criteria['max_trade_concentration']:
        reasons.append(
            f"Lucro concentrado em poucos trades: {concentration*100:.0f}% em top 10"
        )
    
    # === VERIFICAÇÕES DE QUALIDADE (GO) ===
    
    # 4. CAGR vs Buy & Hold
    cagr = metrics.get('cagr', 0)
    bh_cagr = metrics.get('benchmark', {}).get('cagr', 0)
    
    if cagr <= bh_cagr:
        reasons.append(
            f"CAGR não supera Buy & Hold: {cagr*100:.1f}% ≤ {bh_cagr*100:.1f}%"
        )
    
    # 5. Max Drawdown aceitável
    if max_dd > criteria['max_drawdown_pct']:
        reasons.append(
            f"Max Drawdown excessivo: {max_dd:.1f}% > {criteria['max_drawdown_pct']}%"
        )
    
    # 6. Calmar Ratio
    calmar = metrics.get('calmar_ratio', 0)
    if calmar < criteria['min_calmar_ratio']:
        reasons.append(
            f"Calmar Ratio baixo: {calmar:.2f} < {criteria['min_calmar_ratio']}"
        )
    
    # 7. Profit Factor
    pf = metrics.get('profit_factor', 0)
    if pf < criteria['min_profit_factor']:
        reasons.append(
            f"Profit Factor baixo: {pf:.2f} < {criteria['min_profit_factor']}"
        )
    
    # 8. Expectancy
    expectancy = metrics.get('expectancy', 0)
    if expectancy <= criteria['min_expectancy']:
        reasons.append(
            f"Expectancy negativa ou zero: ${expectancy:.2f}"
        )
    
    # 9. Número mínimo de trades
    total_trades = metrics.get('total_trades', 0)
    if total_trades < criteria['min_trades']:
        reasons.append(
            f"Poucos trades para validação estatística: {total_trades} < {criteria['min_trades']}"
        )
    
    # === AVISOS (não impedem GO, mas alertam) ===
    
    # Drawdown próximo do limite
    if max_dd > criteria['warning_drawdown_pct'] and max_dd <= criteria['max_drawdown_pct']:
        warnings.append(
            f"Max Drawdown próximo ao limite: {max_dd:.1f}% (limite: {criteria['max_drawdown_pct']}%)"
        )
    
    # Calmar bom mas não excelente
    if calmar >= criteria['min_calmar_ratio'] and calmar < 1.5:
        warnings.append(
            f"Calmar Ratio aceitável mas não excelente: {calmar:.2f} (excelente: ≥1.5)"
        )
    
    # Decidir status
    status = "GO" if len(reasons) == 0 else "NO-GO"
    
    # Se GO, adicionar razões positivas
    if status == "GO":
        positive_reasons = []
        
        if cagr > bh_cagr:
            alpha = (cagr - bh_cagr) * 100
            positive_reasons.append(f"Supera Buy & Hold em {alpha:.1f}%")
        
        if max_dd <= criteria['max_drawdown_pct']:
            positive_reasons.append(f"Drawdown aceitável ({max_dd:.1f}% ≤ {criteria['max_drawdown_pct']}%)")
        
        if calmar >= 1.5:
            positive_reasons.append(f"Calmar Ratio excelente ({calmar:.2f} ≥ 1.5)")
        elif calmar >= criteria['min_calmar_ratio']:
            positive_reasons.append(f"Calmar Ratio bom ({calmar:.2f} ≥ {criteria['min_calmar_ratio']})")
        
        if pf >= 2.0:
            positive_reasons.append(f"Profit Factor excelente ({pf:.2f})")
        
        reasons = positive_reasons
    
    return CriteriaResult(
        status=status,
        reasons=reasons,
        warnings=warnings
    )
