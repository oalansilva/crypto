"""Migra a cripto de ``market_ohlcv`` + Parquet para a autoridade única (card #1118).

Roteiro do operador (PROD segue ``docs/prod-migration-runbook.md``; o card não roda
isto em DEV nem PROD sem ordem de Alan):

1. ``alembic upgrade head`` (cria ``market_ohlcv_v2``, ``market_series`` e demais);
2. pare o escritor de candles e o runtime-worker (nada grava durante a troca);
3. ``--execute`` copia, importa do Parquet só o que falta e confere por série
   (mostra divergências; não troca nada);
4. ``--execute --swap`` repete (idempotente) e, se tudo conferir, troca os nomes
   (``market_ohlcv`` -> ``market_ohlcv_legacy``) numa transação;
5. ligue ``MARKET_HISTORY_UNIFIED=1`` e reinicie os serviços;
6. reversão: desligue ``MARKET_HISTORY_UNIFIED`` e rode ``--rollback``.

Sem ``--execute`` o script só lê e conta (ensaio). ``--execute`` exige
``--confirm-database NOME`` igual ao banco da URL, para não migrar o banco errado.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
REPO_ROOT = BACKEND_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402

from app.services.market_history.migration import (  # noqa: E402
    DIVERGENCE_LIMIT,
    rollback_swap,
    run_migration,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument(
        "--parquet-dir",
        default=str(REPO_ROOT / "data" / "storage" / "binance"),
        help="Cache Parquet antigo (<BASE>_<QUOTE>_<tf>.parquet).",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Copia e importa (sem isto: ensaio)."
    )
    parser.add_argument(
        "--swap", action="store_true", help="Troca os nomes se a conferência passar."
    )
    parser.add_argument("--rollback", action="store_true", help="Desfaz a troca de nomes.")
    parser.add_argument(
        "--confirm-database", help="Nome do banco da URL (obrigatório com --execute/--rollback)."
    )
    parser.add_argument(
        "--only", action="append", default=[], help="SÍMBOLO:tf (ex.: BTC/USDT:1h). Repetível."
    )
    parser.add_argument("--max-divergence", type=float, default=DIVERGENCE_LIMIT)
    parser.add_argument("--report", help="Grava o relatório JSON neste caminho.")
    args = parser.parse_args(argv)

    if not args.database_url:
        parser.error("Informe --database-url ou DATABASE_URL.")
    url = make_url(args.database_url)
    if (args.execute or args.rollback) and args.confirm_database != url.database:
        parser.error(
            f"--confirm-database deve repetir o banco da URL ({url.database!r}) para escrever nele."
        )
    engine = create_engine(args.database_url)
    try:
        if args.rollback:
            rollback_swap(engine)
            print("Troca de nomes revertida: market_ohlcv voltou a ser o legado.")
            return 0
        only = None
        if args.only:
            only = set()
            for item in args.only:
                symbol, _, timeframe = item.rpartition(":")
                only.add((symbol.upper(), timeframe))
        report = run_migration(
            engine,
            parquet_dir=Path(args.parquet_dir),
            execute=args.execute,
            swap=args.swap,
            only=only,
            divergence_limit=args.max_divergence,
            progress=lambda msg: print(msg, flush=True),
        )
    finally:
        engine.dispose()
    data = report.as_dict()
    if args.report:
        Path(args.report).write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    print(
        json.dumps(
            {k: v for k, v in data.items() if k not in {"series", "divergences_sample"}},
            indent=2,
            ensure_ascii=False,
        )
    )
    failing = [s for s in report.series if not s.ok]
    for outcome in failing[:20]:
        print(f"FALHA {outcome.symbol} {outcome.timeframe}: {'; '.join(outcome.problems)}")
    return 1 if report.blocked and not report.swapped and args.execute else 0


if __name__ == "__main__":
    raise SystemExit(main())
