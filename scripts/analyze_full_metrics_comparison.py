"""
Script para analisar a discrepância completa nas métricas.

Baseado nos dados:
- TradingView: 55 trades, 26 wins (47.27%), Return 2,940.27%
- Sistema: 55 trades, mas win rate diferente (63.6%), Return muito maior

Os 8 trades comparados estão 100% corretos, então o problema está nos outros 47 trades.
"""

def analyze_discrepancy():
    """Analisa a discrepância nas métricas."""
    
    print("="*100)
    print("ANALISE DA DISCREPANCIA NAS METRICAS")
    print("="*100)
    
    print("\n[FATOS CONFIRMADOS]:")
    print("   1. Os 8 trades mais recentes (2024-2026) estao 100% corretos")
    print("   2. Datas, precos, sinais e P&L batem perfeitamente")
    print("   3. O calculo de compounding esta correto para esses 8 trades")
    print("   4. Ambos usam capital inicial de $100")
    
    print("\n[PROBLEMA IDENTIFICADO]:")
    print("   TradingView: 55 trades, 26 wins (47.27%), Return 2,940.27%")
    print("   Sistema: 55 trades, ~35 wins (63.6%), Return 20,218% ou 2,021,807%")
    print("   Diferenca no Win Rate: 16.33% (9 trades a mais como wins no sistema)")
    
    print("\n[HIPOTESES]:")
    print("   1. Os outros 47 trades (2017-2024) podem ter diferencas:")
    print("      - Datas de entrada/saida diferentes")
    print("      - Precos de entrada/saida diferentes")
    print("      - Sinais diferentes (Stop vs Close)")
    print("      - Trades que o sistema considera win mas TradingView considera loss")
    
    print("\n   2. Possivel causa: Diferenca na deteccao de stop loss")
    print("      - Sistema pode estar detectando stop loss em momentos diferentes")
    print("      - TradingView pode ter logica de stop loss mais restritiva")
    print("      - Ou vice-versa")
    
    print("\n   3. Possivel causa: Diferenca nos dados historicos")
    print("      - Sistema usa dados da Binance")
    print("      - TradingView pode usar dados de outra exchange ou agregados")
    print("      - Pequenas diferencas nos precos OHLCV podem gerar sinais diferentes")
    
    print("\n   4. Possivel causa: Periodo de backtest diferente")
    print("      - TradingView: Aug 16, 2017 - Jan 26, 2026")
    print("      - Sistema: Precisamos verificar o periodo exato")
    
    print("\n[SOLUCAO PROPOSTA]:")
    print("   1. Exportar todos os 55 trades do sistema (planilha completa)")
    print("   2. Comparar trade por trade com TradingView")
    print("   3. Identificar quais trades tem diferencas")
    print("   4. Analisar padroes nas diferencas (datas, precos, sinais)")
    print("   5. Verificar se ha trades duplicados ou faltando")
    
    print("\n[PROXIMOS PASSOS]:")
    print("   1. Criar script para ler planilha completa do sistema")
    print("   2. Extrair todos os 55 trades do TradingView (se possivel)")
    print("   3. Comparar trade por trade")
    print("   4. Gerar relatorio detalhado das diferencas")
    
    print("\n" + "="*100)
    
    # Calcular o que seria o Return correto
    print("\n[CALCULO TEORICO]:")
    print("   Se TradingView tem 26 wins e 29 losses em 55 trades:")
    print("   E o Return e 2,940.27% com capital inicial $100")
    print("   Entao equity final = $3,040.27")
    print("   ")
    print("   Se o sistema tem 35 wins e 20 losses (9 wins a mais):")
    print("   E esses 9 wins extras sao significativos, o Return seria maior")
    print("   Mas nao deveria ser 20,218% ou 2,021,807%")
    print("   ")
    print("   Isso sugere que ha um erro no calculo OU")
    print("   Os trades sao completamente diferentes (nao apenas win rate)")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    analyze_discrepancy()
