"""
Exclui o template CRUZAMENTOMEDIAS (ou "Example: CRUZAMENTOMEDIAS") do banco.
Execute a partir da raiz do projeto: python scripts/delete_cruzamentomedias_template.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

import sqlite3

try:
    from app.database import DB_PATH
    db_path = str(DB_PATH)
except Exception:
    db_path = str(project_root / "backend" / "data" / "crypto_backtest.db")

NAMES = ("Example: CRUZAMENTOMEDIAS", "CRUZAMENTOMEDIAS")

def main():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for name in NAMES:
        cursor.execute("SELECT id, name FROM combo_templates WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            cursor.execute("DELETE FROM combo_templates WHERE name = ?", (name,))
            print(f"Excluído: {name}")
        else:
            print(f"Não encontrado: {name}")

    conn.commit()
    conn.close()
    print("Concluído.")

if __name__ == "__main__":
    main()
