import sys
import os
import pandas as pd

# Add project root and backend
current_dir = os.getcwd()
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'backend'))

from src.data.incremental_loader import IncrementalLoader
from app.services.combo_service import ComboService

def quick_test():
    print("\n" + "="*60)
    print("TESTE RÁPIDO: Verificação de Timezone (UTC)")
    print("="*60)
    
    # Load data
    loader = IncrementalLoader()
    df = loader.fetch_data(
        symbol="BTC/USDT",
        timeframe="1d",
        since_str="2025-09-01",
        until_str="2025-10-15"
    )
    
    # Create strategy
    combo_service = ComboService()
    strategy = combo_service.create_strategy(
        template_name="multi_ma_crossover",
        parameters={
            "short_length": 17,
            "medium_length": 21,
            "long_length": 34,
            "stop_loss": 0.039
        }
    )
    
    # Generate signals
    df_signals = strategy.generate_signals(df.copy())
    
    # Extract trades using the SAME logic as combo_optimizer
    from app.services.combo_optimizer import extract_trades_from_signals
    trades = extract_trades_from_signals(df_signals, stop_loss=0.039)
    
    print(f"\n✅ Total de trades encontrados: {len(trades)}")
    print("\n📊 Primeiros 5 trades:\n")
    
    for i, trade in enumerate(trades[:5]):
        entry_time = trade['entry_time']
        exit_time = trade.get('exit_time', 'N/A')
        entry_price = trade['entry_price']
        exit_price = trade.get('exit_price', 0)
        profit = trade.get('profit', 0) * 100
        
        print(f"Trade #{i+1}:")
        print(f"  Entry:  {entry_time} @ ${entry_price:,.2f}")
        print(f"  Exit:   {exit_time} @ ${exit_price:,.2f}")
        print(f"  Profit: {profit:+.2f}%")
        print()
    
    # Specific check for Oct 02 entry
    print("\n🔍 Verificação específica: Trade de Outubro")
    oct_trades = [t for t in trades if '2025-10' in t['entry_time']]
    if oct_trades:
        first_oct = oct_trades[0]
        print(f"  Entry Time: {first_oct['entry_time']}")
        print(f"  Entry Price: ${first_oct['entry_price']:,.2f}")
        print(f"  ✅ Esperado: 2025-10-02T00:00:00+00:00 @ $118,594.99")
        
        # Check if it matches
        if '2025-10-02' in first_oct['entry_time'] and abs(first_oct['entry_price'] - 118594.99) < 1:
            print(f"  ✅ CORRETO! Data em UTC e preço exato.")
        else:
            print(f"  ❌ ERRO! Não bate com o esperado.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    quick_test()
