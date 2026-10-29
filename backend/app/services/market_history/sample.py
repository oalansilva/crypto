"""Amostra de uma execução (card #1118): congela no início e só lê do manifesto."""

from __future__ import annotations

import contextvars
import logging
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.engine import Engine

from app.services.market_history import snapshots
from app.services.market_history.model import SeriesRef, crypto_spec, iso

logger = logging.getLogger(__name__)

# Amostra ativa da thread (processo principal); os workers recebem o id por argumento.
ACTIVE_SAMPLE_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "market_history_active_sample", default=None
)


def to_loader_format(frame: pd.DataFrame) -> pd.DataFrame:
    """Índice ``timestamp_utc`` e colunas ``timestamp``, open, high, low, close, volume."""

    if frame is None or frame.empty:
        return pd.DataFrame()
    out = frame[[*snapshots.COLUMNS]].copy()
    index = pd.DatetimeIndex(out.index)
    if index.tz is None:
        index = index.tz_localize("UTC")
    out.insert(0, "timestamp", index.as_unit("ms").asi8)
    out.index = pd.DatetimeIndex(index.as_unit("us"), name="timestamp_utc")
    return out


class ExecutionSample:
    """Congela séries no início da execução; todas as leituras seguintes vêm dos segmentos."""

    def __init__(
        self,
        kind: str,
        *,
        owner_ref: str | None = None,
        engine: Engine | None = None,
        root: Path | None = None,
        snapshot_id: str | None = None,
    ) -> None:
        if engine is None:
            from app.database import engine as app_engine

            engine = app_engine
        self.engine = engine
        self.kind = kind
        self.owner_ref = owner_ref
        self.root = root or snapshots.snapshot_root()
        self._snapshot_id = snapshot_id
        self._entries: dict[str, dict[str, Any]] = {}
        self._frames: dict[str, pd.DataFrame] = {}

    # -- identidade ------------------------------------------------------------

    @property
    def snapshot_id(self) -> str | None:
        return self._snapshot_id

    @classmethod
    def open(
        cls, snapshot_id: str, *, engine: Engine | None = None, root: Path | None = None
    ) -> "ExecutionSample":
        """Reabre uma amostra existente (nova tentativa, worker ou reprodução)."""

        sample = cls("reopen", engine=engine, root=root, snapshot_id=snapshot_id)
        manifest = snapshots.validate(sample.engine, snapshot_id, sample.root)
        sample.kind = manifest["kind"]
        sample._entries = {e["role"]: e for e in manifest["series"]}
        return sample

    # -- congelar ---------------------------------------------------------------

    def freeze(
        self,
        role: str,
        series: SeriesRef,
        requested_start: Any,
        requested_end: Any,
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        """Congela ``frame`` (lido da autoridade agora) e devolve a leitura dos segmentos."""

        if role in self._entries:
            return self.frame(role)
        segments = snapshots.freeze_frame(self.root, frame)
        entry = snapshots.series_entry(
            role, series, requested_start, requested_end, frame, segments
        )
        self._entries[role] = entry
        self._snapshot_id = snapshots.create_manifest(
            self.engine,
            kind=self.kind,
            entries=list(self._entries.values()),
            owner_ref=self.owner_ref,
            snapshot_id=self._snapshot_id,
        )
        return self.frame(role)

    def freeze_crypto(
        self,
        role: str,
        symbol: str,
        timeframe: str,
        requested_start: Any,
        requested_end: Any,
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        from app.services.market_history.facade import get_history_service

        service = get_history_service()
        series = service.resolve(crypto_spec(symbol, timeframe))
        series = service.read(series, limit=1).series  # versão atual
        return self.freeze(role, series, requested_start, requested_end, frame)

    def freeze_symbol(
        self,
        role: str,
        symbol: str,
        timeframe: str,
        requested_start: Any,
        requested_end: Any,
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        """Cripto (par com ``/``) ou ação/ETF (ticker do catálogo): card #1119, decisão 8."""

        if "/" in str(symbol):
            return self.freeze_crypto(
                role, symbol, timeframe, requested_start, requested_end, frame
            )
        from app.services.market_history.facade import get_history_service, spec_for_request

        service = get_history_service()
        series = service.resolve(spec_for_request(symbol=symbol, timeframe=timeframe))
        series = service.read(series, limit=1).series  # versão atual
        return self.freeze(role, series, requested_start, requested_end, frame)

    # -- ler ----------------------------------------------------------------------

    def has(self, role: str) -> bool:
        return role in self._entries

    def frame(self, role: str) -> pd.DataFrame:
        cached = self._frames.get(role)
        if cached is not None:
            return cached
        entry = self._entries.get(role)
        if entry is None:
            raise snapshots.SnapshotError(
                f"A amostra não tem o papel {role}.", code="frozen_input_invalid"
            )
        loaded = snapshots.read_segments(self.root, entry["segments"])
        self._frames[role] = loaded
        return loaded

    def entry(self, role: str) -> dict[str, Any] | None:
        return self._entries.get(role)

    # -- fim e proveniência ---------------------------------------------------------

    def finish(self) -> None:
        if self._snapshot_id:
            snapshots.finish(self.engine, self._snapshot_id)

    def provenance(self, role: str, *, with_retention: bool = False) -> dict[str, Any]:
        """Campos de proveniência do resultado (decisão 15).

        ``with_retention`` (card #1119, decisão 16): acrescenta ``kept_until``, o fim do prazo de 30 dias
        da amostra de ação/ETF, que nunca vira favorito. Cripto não usa: o prazo da amostra dos favoritos
        é outro.
        """

        entry = self._entries.get(role)
        if entry is None:
            return {}
        out = provenance_from_entry(entry, self._snapshot_id)
        if with_retention:
            out["kept_until"] = iso(
                pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=snapshots.RETENTION_DAYS)
            )
        return out


def provenance_from_entry(entry: dict[str, Any], snapshot_id: str | None) -> dict[str, Any]:
    return {
        "data_source": entry["source_label"],
        "asset_class": entry["asset_class"],
        "session": entry["session"],
        "adjustment": entry["adjustment"],
        "timeframe_origin": entry["origin"],
        "period_requested": entry["requested"],
        "period_covered": entry["covered"],
        "data_version": entry["data_version"],
        "version_label": entry["version_label"],
        "snapshot_id": snapshot_id,
        "content_sha256": entry["sha256"],
    }
