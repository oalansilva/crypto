# file: backend/init_db.py
# -*- coding: utf-8 -*-
import sys
import io

# Configurar stdout para UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import Base, engine
from app.models import BacktestRun, BacktestResult, FavoriteStrategy, AutoBacktestRun

print("Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("Banco de dados inicializado!")
