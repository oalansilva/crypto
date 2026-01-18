# file: backend/init_db.py
from app.database import Base, engine
from app.models import BacktestRun, BacktestResult, FavoriteStrategy, AutoBacktestRun

print("✅ Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("✅ Banco de dados inicializado!")
