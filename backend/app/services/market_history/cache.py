"""Cache de leitura em Parquet, derivado do PostgreSQL (card #1118, decisão 12).

``data/storage/series/<series_id>/v<versão>/<timeframe>.parquet``: escrito de
forma atômica a partir da autoridade. Apagar o diretório só faz o próximo pedido
refazer o arquivo, sem chamar a Binance. Versão nova = arquivo novo; o antigo
some no próximo varrimento. Teto de 3 GiB com descarte por último acesso.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Any

import pandas as pd

from app.services.market_history import store
from app.services.market_history.model import SeriesRef, to_utc
from app.services.market_history.nyse_calendar import DERIVED_15M_RULE_VERSION

logger = logging.getLogger(__name__)

GiB = 1024**3
DEFAULT_MAX_BYTES = 3 * GiB
COLUMNS = ["open", "high", "low", "close", "volume"]


def default_cache_root() -> Path:
    configured = os.getenv("MARKET_HISTORY_CACHE_DIR", "").strip()
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[4] / "data" / "storage" / "series"


class ParquetReadCache:
    def __init__(
        self, root: Path | str | None = None, *, max_bytes: int = DEFAULT_MAX_BYTES
    ) -> None:
        self.root = Path(root) if root is not None else default_cache_root()
        self.max_bytes = int(max_bytes)

    # -- caminhos ---------------------------------------------------------------

    def series_dir(self, series: SeriesRef) -> Path:
        return self.root / str(series.series_id)

    def file_name(self, series: SeriesRef) -> str:
        if series.is_derived:
            return f"{series.timeframe}.r{DERIVED_15M_RULE_VERSION}.parquet"
        return f"{series.timeframe}.parquet"

    def path(self, series: SeriesRef, version: int | None = None) -> Path:
        v = series.data_version if version is None else version
        return self.series_dir(series) / f"v{v}" / self.file_name(series)

    # -- leitura ----------------------------------------------------------------

    def _watermark(self, conn, series: SeriesRef) -> dict[str, Any]:
        cov = store.get_coverage(conn, series.series_id) or {}
        fresh = store.refresh_series(conn, series)
        return {
            "version": fresh.data_version,
            "content_seq": int(cov.get("content_seq") or 0),
            "count": int(cov.get("candle_count") or 0),
            "rule": DERIVED_15M_RULE_VERSION if series.is_derived else None,
        }

    def read(
        self,
        service,
        series: SeriesRef,
        start: Any = None,
        end: Any = None,
    ) -> pd.DataFrame:
        """Fatia de candles via cache; refaz o arquivo da autoridade quando preciso."""

        with service.engine.connect() as conn:
            mark = self._watermark(conn, series)
        current = series.with_version(mark["version"])
        target = self.path(current)
        meta = target.with_suffix(".meta.json")
        if not self._fresh(target, meta, mark):
            self._rebuild(service, current, target, meta, mark)
        else:
            self._touch(target)
        return self._slice(target, start, end)

    @staticmethod
    def _fresh(target: Path, meta: Path, mark: dict[str, Any]) -> bool:
        if not target.exists() or not meta.exists():
            return False
        try:
            stored = json.loads(meta.read_text())
        except (OSError, ValueError):
            return False
        return stored == mark

    @staticmethod
    def _touch(target: Path) -> None:
        try:
            os.utime(target, None)
        except OSError:
            pass

    def _rebuild(
        self, service, series: SeriesRef, target: Path, meta: Path, mark: dict[str, Any]
    ) -> None:
        result = service.read(series)
        frame = result.candles.copy()
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(f"{target.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
        try:
            out = frame.reset_index()
            out["timestamp"] = pd.DatetimeIndex(out["candle_time"]).as_unit("ms").asi8
            out.to_parquet(tmp, index=False)
            os.replace(tmp, target)
            mtmp = meta.with_name(f"{meta.name}.{uuid.uuid4().hex}.tmp")
            mtmp.write_text(json.dumps(mark))
            os.replace(mtmp, meta)
        finally:
            tmp.unlink(missing_ok=True)
        self.sweep(keep=target)

    @staticmethod
    def _slice(target: Path, start: Any, end: Any) -> pd.DataFrame:
        lo = to_utc(start)
        hi = to_utc(end)
        filters = []
        if lo is not None:
            filters.append(("timestamp", ">=", int(lo.timestamp() * 1000)))
        if hi is not None:
            filters.append(("timestamp", "<=", int(hi.timestamp() * 1000)))
        frame = pd.read_parquet(target, filters=filters or None)
        frame["candle_time"] = pd.to_datetime(frame["candle_time"], utc=True)
        frame = frame.set_index("candle_time")
        return frame[COLUMNS]

    # -- varrimento -------------------------------------------------------------

    def sweep(self, keep: Path | None = None) -> int:
        """Remove versões antigas da série e descarta por último acesso acima do teto."""

        removed = 0
        if keep is not None:
            series_dir = keep.parent.parent
            for version_dir in series_dir.glob("v*"):
                if version_dir != keep.parent:
                    shutil.rmtree(version_dir, ignore_errors=True)
                    removed += 1
        files = [p for p in self.root.rglob("*.parquet") if p.is_file()]
        total = sum(p.stat().st_size for p in files)
        if total > self.max_bytes:
            files.sort(key=lambda p: p.stat().st_mtime)
            for path in files:
                if keep is not None and path == keep:
                    continue
                size = path.stat().st_size
                path.unlink(missing_ok=True)
                path.with_suffix(".meta.json").unlink(missing_ok=True)
                total -= size
                removed += 1
                if total <= self.max_bytes:
                    break
        return removed

    def total_bytes(self) -> int:
        return sum(p.stat().st_size for p in self.root.rglob("*") if p.is_file())
