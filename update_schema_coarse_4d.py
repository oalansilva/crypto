
import sqlite3
import json

db_path = "backend/data/crypto_backtest.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Busca o template atual
cursor.execute("SELECT template_data, optimization_schema FROM combo_templates WHERE name = 'multi_ma_crossover'")
row = cursor.fetchone()

if row:
    template_data = json.loads(row[0])
    opt_schema = json.loads(row[1])
    
    print("Esquema Atual:", json.dumps(opt_schema, indent=2))
    
    # 1. Atualizar Parâmetros para Grade Grossa
    params = opt_schema.get("parameters", {})
    
    # EMA Short: Passo 2 (3, 5, 7...)
    params["ema_short"] = {"min": 3, "max": 20, "step": 2, "default": 9}
    
    # SMA Medium: Passo 5 (10, 15, 20...)
    params["sma_medium"] = {"min": 10, "max": 40, "step": 5, "default": 21}
    
    # SMA Long: Passo 10 (20, 30, 40...)
    params["sma_long"] = {"min": 20, "max": 100, "step": 10, "default": 50}
    
    # Stop Loss: Passo 0.01 (1%, 2%, 3%...)
    params["stop_loss"] = {"min": 0.01, "max": 0.08, "step": 0.01, "default": 0.03}
    
    opt_schema["parameters"] = params

    # 2. Atualizar Grupo Correlacionado para 4D (Todas as Médias + Stop)
    opt_schema["correlated_groups"] = [
        ["ema_short", "sma_medium", "sma_long", "stop_loss"]
    ]

    # Salvar alterações
    cursor.execute("""
        UPDATE combo_templates 
        SET optimization_schema = ? 
        WHERE name = 'multi_ma_crossover'
    """, (json.dumps(opt_schema),))
    
    conn.commit()
    print("\n✅ Banco de dados atualizado para Grade 4D Grossa!")
    print("Novo Esquema:", json.dumps(opt_schema, indent=2))

else:
    print("Template não encontrado.")

conn.close()
