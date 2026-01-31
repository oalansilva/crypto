"""
Inspeciona o cache Parquet (data/storage/<exchange>/): lista arquivos, tamanho e timestamps.
Uso: python scripts/inspect_parquet_cache.py
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# project root
ROOT = Path(__file__).resolve().parent.parent
CACHE_BASE = ROOT / "data" / "storage"


def main():
    if not CACHE_BASE.exists():
        print(f"Cache base não existe: {CACHE_BASE}")
        return 0
    print(f"Cache base: {CACHE_BASE}\n")
    try:
        import pandas as pd
    except ImportError:
        print("pandas não instalado; mostrando apenas tamanhos de arquivo.")
        pd = None

    for exchange_dir in sorted(CACHE_BASE.iterdir()):
        if not exchange_dir.is_dir():
            continue
        print(f"--- {exchange_dir.name} ---")
        files = list(exchange_dir.glob("*.parquet"))
        if not files:
            print("  (nenhum .parquet)")
            continue
        for f in sorted(files):
            size_mb = f.stat().st_size / (1024 * 1024)
            mtime = f.stat().st_mtime
            mtime_str = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            ts_info = ""
            if pd is not None:
                try:
                    import pyarrow.parquet as pq
                    schema = pq.read_schema(f)
                    cols = list(schema.names) if hasattr(schema, "names") else [schema.field(i).name for i in range(len(schema))]
                    ts_col = "timestamp_utc" if "timestamp_utc" in cols else ("timestamp" if "timestamp" in cols else None)
                    if ts_col:
                        ts = pd.read_parquet(f, columns=[ts_col])
                        n = len(ts)
                        if n > 0:
                            ts_info = f"  rows={n}  min={ts[ts_col].min()}  max={ts[ts_col].max()}"
                except Exception as e:
                    ts_info = f"  (erro ao ler: {e})"
            print(f"  {f.name}  {size_mb:.2f} MB  mtime={mtime_str}{ts_info}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
