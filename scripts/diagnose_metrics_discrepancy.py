"""
Script para diagnosticar a discrepância nas métricas.

TradingView mostra:
- Total P&L: +2,940.27 USD (+2,940.27%)
- Com 55 trades
- Capital inicial: $100 (assumido)

Sistema mostra:
- Total Return: 20,218.08% ou 2,021,807.75%
- Com 55 trades
- Capital inicial: $100 (configurado)

Vamos calcular o que deveria ser com os trades conhecidos.
"""

# Simular 55 trades baseado nos dados conhecidos
# TradingView: 26 wins, 29 losses (47.27% win rate)
# Sistema: 35 wins, 20 losses (63.6% win rate) - DIFERENTE!

# Vamos usar os trades conhecidos (8 trades) e extrapolar
known_trades = [
    {'profit': -0.0604},  # Trade 1: Stop
    {'profit': 0.2715},   # Trade 2: Close
    {'profit': -0.0604},  # Trade 3: Stop
    {'profit': -0.0604},  # Trade 4: Stop
    {'profit': 0.1301},   # Trade 5: Close
    {'profit': -0.0604},  # Trade 6: Stop
    {'profit': -0.0604},  # Trade 7: Stop
    {'profit': 0.0119},   # Trade 8: Close
]

def calculate_return(trades, initial_capital=100):
    """Calcula return com compounding."""
    equity = float(initial_capital)
    for t in trades:
        equity *= (1.0 + t['profit'])
    return (equity / initial_capital - 1) * 100.0

# Calcular com os 8 trades conhecidos
return_8_trades = calculate_return(known_trades, 100)
print(f"Return com 8 trades conhecidos: {return_8_trades:.2f}%")
print(f"Equity final: ${100 * (1 + return_8_trades/100):.2f}")

# Se TradingView tem 55 trades e mostra 2,940.27%
# Isso significa: equity final = 100 * (1 + 29.4027) = $3,040.27
# Ou seja: equity final = $3,040.27

# Se sistema tem 55 trades e mostra 20,218.08%
# Isso significa: equity final = 100 * (1 + 202.1808) = $20,318.08

# Se sistema mostra 2,021,807.75%
# Isso significa: equity final = 100 * (1 + 20218.0775) = $2,021,907.75

print("\n" + "="*80)
print("DIAGNOSTICO:")
print("="*80)
print(f"\nTradingView (55 trades, 26 wins, 29 losses):")
print(f"   Return: 2,940.27%")
print(f"   Equity final: $3,040.27")
print(f"   Capital inicial: $100")

print(f"\nSistema (55 trades, mas win rate diferente):")
print(f"   Return V1: 20,218.08% -> Equity final: $20,318.08")
print(f"   Return V2: 2,021,807.75% -> Equity final: $2,021,907.75")

print(f"\n[PROBLEMA] Win Rate diferente:")
print(f"   TradingView: 47.27% (26/55)")
print(f"   Sistema: 63.6% (35/55)")
print(f"   Diferenca: {63.6 - 47.27:.2f}%")

print(f"\n[POSSIVEL CAUSA]:")
print(f"   1. Sistema e TradingView podem ter trades diferentes")
print(f"   2. Ou a contagem de wins/losses esta diferente")
print(f"   3. Ou ha um erro no calculo de compounding")
print(f"   4. Ou o capital inicial usado e diferente")

print(f"\n[VERIFICACAO NECESSARIA]:")
print(f"   1. Comparar todos os 55 trades (nao apenas 8)")
print(f"   2. Verificar se win rate esta sendo calculado corretamente")
print(f"   3. Verificar capital inicial usado em ambos")
print(f"   4. Verificar se ha trades duplicados ou faltando")
