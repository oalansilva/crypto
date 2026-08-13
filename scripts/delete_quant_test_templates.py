"""Exclusão física dos templates de teste quant_* e favoritos órfãos (card #489).

- Backup JSON antes da deleção (auditoria).
- Deleta favoritos cujo strategy_name é template quant_*.
- Deleta templates com nome quant_* (case-insensitive).

Uso:
    DATABASE_URL=postgresql+psycopg2://... python scripts/delete_quant_test_templates.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from app.database import SessionLocal
from app.models import ComboTemplate, FavoriteStrategy

QUANT_PREFIX = "quant_"


def _quant_names(rows) -> set[str]:
    return {r.name for r in rows if str(r.name or "").strip().lower().startswith(QUANT_PREFIX)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Somente reporta, sem deletar.")
    parser.add_argument(
        "--backup-dir",
        default=str(Path(__file__).resolve().parent / "backups"),
        help="Diretório do backup JSON.",
    )
    args = parser.parse_args()

    session = SessionLocal()
    try:
        templates = session.query(ComboTemplate).all()
        quant_templates = [t for t in templates if str(t.name or "").strip().lower().startswith(QUANT_PREFIX)]
        quant_names = {t.name for t in quant_templates}

        favorites = session.query(FavoriteStrategy).all()
        orphan_favorites = [f for f in favorites if str(f.strategy_name or "") in quant_names]

        summary = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "dry_run": args.dry_run,
            "quant_templates": [
                {"id": t.id, "name": t.name, "description": t.description} for t in quant_templates
            ],
            "orphan_favorites": [
                {"id": f.id, "name": f.name, "symbol": f.symbol, "strategy_name": f.strategy_name}
                for f in orphan_favorites
            ],
        }

        backup_path = Path(args.backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"quant_templates_deletion_{stamp}.json"
        backup_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Backup: {backup_file}")

        print(f"Templates quant_*: {len(quant_templates)}")
        print(f"Favoritos órfãos: {len(orphan_favorites)}")

        if args.dry_run:
            print("DRY-RUN: nenhuma deleção executada.")
            return 0

        fav_ids = [f.id for f in orphan_favorites]
        if fav_ids:
            session.query(FavoriteStrategy).filter(FavoriteStrategy.id.in_(fav_ids)).delete(
                synchronize_session=False
            )
            print(f"Deletados favoritos: {fav_ids}")

        tmpl_ids = [t.id for t in quant_templates]
        if tmpl_ids:
            session.query(ComboTemplate).filter(ComboTemplate.id.in_(tmpl_ids)).delete(
                synchronize_session=False
            )
            print(f"Deletados templates: {tmpl_ids}")

        session.commit()
        print("Exclusão concluída.")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
