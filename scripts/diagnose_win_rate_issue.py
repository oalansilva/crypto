"""
Script para diagnosticar o problema de Win Rate e Total Return.

Problema reportado:
- Sistema mostra: Win Rate 63.6%, Total Return 2,021,807.75%
- TradingView mostra: Win Rate 47.27% (26/55), Total Return 2,940.27%
- Usuário confirma: 26 trades de ganho (de 55 total)
"""

import sys
import os

# Add project root and backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'backend'))

def analyze_win_rate_issue():
    """Analisa o problema de Win Rate."""
    
    print("="*100)
    print("DIAGNOSTICO: Win Rate e Total Return")
    print("="*100)
    
    print("\n[PROBLEMA REPORTADO]:")
    print("   Sistema mostra: Win Rate 63.6%, Total Return 2,021,807.75%")
    print("   TradingView mostra: Win Rate 47.27% (26/55), Total Return 2,940.27%")
    print("   Usuario confirma: 26 trades de ganho de 55 total")
    
    print("\n[ANALISE]:")
    print("   1. Win Rate esperado: 26/55 = 47.27%")
    print("   2. Win Rate atual do sistema: 63.6% = 35/55")
    print("   3. Diferenca: 9 trades a mais sendo contados como wins")
    
    print("\n[POSSIVEIS CAUSAS]:")
    print("   1. Trades com profit > 0 que na verdade sao losses (erro no calculo de profit)")
    print("   2. Trades duplicados sendo contados")
    print("   3. Trades abertos sendo contados (mas o codigo filtra isso)")
    print("   4. Trades com profit = 0 sendo contados como wins (mas o codigo usa > 0)")
    print("   5. Sistema gerando trades diferentes do TradingView")
    
    print("\n[VERIFICACAO NECESSARIA]:")
    print("   1. Contar quantos trades realmente tem profit > 0 no sistema")
    print("   2. Verificar se ha trades duplicados")
    print("   3. Comparar lista completa de trades do sistema vs TradingView")
    print("   4. Verificar se o calculo de profit esta correto para todos os trades")
    
    print("\n[SOBRE TOTAL RETURN]:")
    print("   TradingView: 2,940.27% (equity final = $3,040.27 com capital inicial $100)")
    print("   Sistema: 2,021,807.75% (equity final = $2,021,907.75)")
    print("   ")
    print("   Se o sistema tem 35 wins e TradingView tem 26 wins:")
    print("   - Os 9 wins extras podem estar inflando o Return")
    print("   - Mas nao deveria ser 687x maior (isso sugere erro no calculo)")
    print("   ")
    print("   Possivel causa: Erro no calculo de compounding OU")
    print("   Trades completamente diferentes (nao apenas win rate)")
    
    print("\n[SOLUCAO PROPOSTA]:")
    print("   1. Verificar todos os 55 trades do sistema")
    print("   2. Contar quantos realmente tem profit > 0")
    print("   3. Comparar com os 26 wins do TradingView")
    print("   4. Identificar quais 9 trades estao sendo contados incorretamente como wins")
    print("   5. Verificar se esses trades tem profit calculado incorretamente")
    
    print("\n" + "="*100)
    
    # Calcular o que seria o Return correto
    print("\n[CALCULO TEORICO]:")
    print("   Se TradingView tem 26 wins e 29 losses:")
    print("   Return = 2,940.27%")
    print("   ")
    print("   Se o sistema tem 35 wins e 20 losses (9 wins a mais):")
    print("   O Return seria maior, mas nao 687x maior")
    print("   ")
    print("   Isso sugere que:")
    print("   - Os trades sao diferentes (nao apenas win rate)")
    print("   - OU ha um erro no calculo de compounding")
    print("   - OU ha trades com profit muito alto sendo contados incorretamente")

if __name__ == "__main__":
    analyze_win_rate_issue()
    
    print("\n[PROXIMOS PASSOS]:")
    print("   1. Exportar todos os 55 trades do sistema para CSV")
    print("   2. Contar quantos tem profit > 0")
    print("   3. Comparar com TradingView trade por trade")
    print("   4. Identificar quais trades estao sendo contados incorretamente")
