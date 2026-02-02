"""
One-off: set all favorites with tier=3 to "Sem tier" (tier=NULL).
Run from backend: python scripts/set_tier3_to_no_tier.py
"""
import sys
from pathlib import Path

# Ensure backend is on path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models import FavoriteStrategy

def main():
    db = SessionLocal()
    try:
        updated = db.query(FavoriteStrategy).filter(FavoriteStrategy.tier == 3).update(
            {FavoriteStrategy.tier: None},
            synchronize_session=False
        )
        db.commit()
        print(f"[OK] {updated} favorito(s) com Tier 3 alterado(s) para Sem tier.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
