"""Amostra estável de execução (card #1118, decisões 13 a 15 e 18).

No início de uma execução (backtest, combo, otimização, descoberta) a janela é
congelada em segmentos mensais por série em Parquet, gravados uma vez em
``data/snapshots/segments/<sha[:2]>/<sha>.parquet`` (SHA-256 dos bytes), e um
manifesto em ``execution_data_snapshots`` diz quais segmentos formam a amostra.
Todas as tentativas leem só do manifesto e conferem o SHA-256; atualização,
correção ou cache refeito não mudam uma execução em andamento.

Prazo: 30 dias depois do mais tarde entre o fim da execução e o momento em que o
manifesto deixou de ser a amostra de um favorito. Manifesto fixado por um
favorito (``pinned``) não vence.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.services.market_history.model import (
    SeriesRef,
    SOURCE_LABELS,
    iso,
    to_utc,
)
from app.services.market_history.nyse_calendar import DERIVED_15M_RULE_VERSION

logger = logging.getLogger(__name__)

RETENTION_DAYS = 30
SEGMENT_GRACE_SECONDS = 3600  # segmento recém-gravado, ainda sem manifesto, não é órfão
ALERT_BYTES = 5 * 1024**3
COLUMNS = ("open", "high", "low", "close", "volume")


class SnapshotError(Exception):
    code = "snapshot_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


def snapshot_root() -> Path:
    configured = os.getenv("MARKET_HISTORY_SNAPSHOT_DIR", "").strip()
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[4] / "data" / "snapshots"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime | None) -> datetime:
    if value is None:
        return _now()
    return (
        value.replace(tzinfo=timezone.utc)
        if value.tzinfo is None
        else value.astimezone(timezone.utc)
    )


# --- segmentos -----------------------------------------------------------------


def segment_path(root: Path, sha: str) -> Path:
    return root / "segments" / sha[:2] / f"{sha}.parquet"


def encode_segment(frame: pd.DataFrame) -> bytes:
    """Bytes determinísticos de um mês de candles (mesmos dados -> mesmo SHA-256)."""

    index = pd.DatetimeIndex(frame.index)
    table = pa.table(
        {
            "timestamp": pa.array(index.as_unit("ms").asi8, pa.int64()),
            **{c: pa.array(frame[c].to_numpy(dtype="float64"), pa.float64()) for c in COLUMNS},
        }
    )
    sink = io.BytesIO()
    pq.write_table(table, sink, compression="zstd", use_dictionary=False, write_statistics=False)
    return sink.getvalue()


def write_segment(root: Path, data: bytes) -> tuple[str, bool]:
    """Grava uma vez só. Devolve ``(sha256, novo)``.

    Segmento reaproveitado tem o mtime renovado: a carência do GC protege o arquivo até o
    manifesto da nova execução existir (um órfão antigo não pode sumir no meio do caminho).
    """

    sha = hashlib.sha256(data).hexdigest()
    path = segment_path(root, sha)
    if path.exists():
        try:
            os.utime(path)
        except OSError:  # arquivo apagado entre o exists e o utime: regrava abaixo
            pass
        else:
            return sha, False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with tmp.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
    return sha, True


def freeze_frame(root: Path, frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Divide em meses (UTC) e grava os segmentos; devolve a lista do manifesto."""

    if frame is None or frame.empty:
        return []
    clean = frame[list(COLUMNS)].copy()
    index = pd.DatetimeIndex(clean.index)
    if index.tz is None:
        index = index.tz_localize("UTC")
    clean.index = index
    clean = clean[~clean.index.duplicated(keep="last")].sort_index()
    segments: list[dict[str, Any]] = []
    months = clean.index.strftime("%Y-%m")
    for month in pd.unique(months):
        part = clean[months == month]
        data = encode_segment(part)
        sha, _ = write_segment(root, data)
        segments.append({"month": month, "sha256": sha, "rows": int(len(part)), "bytes": len(data)})
    return segments


def read_segments(root: Path, segments: Iterable[dict[str, Any]]) -> pd.DataFrame:
    """Lê e confere o SHA-256 de cada segmento. Corrompido ou ausente levanta."""

    frames = []
    for seg in segments:
        path = segment_path(root, seg["sha256"])
        if path.is_symlink() or not path.exists():
            raise SnapshotError(
                "A amostra congelada não está mais no disco.", code="frozen_input_invalid"
            )
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != seg["sha256"]:
            raise SnapshotError("A amostra congelada está corrompida.", code="frozen_input_corrupt")
        frames.append(pq.read_table(io.BytesIO(data)).to_pandas())
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["timestamp_utc"] = pd.DatetimeIndex(
        pd.to_datetime(out["timestamp"], unit="ms", utc=True)
    ).as_unit("us")
    out = out.set_index("timestamp_utc")
    return out[["timestamp", *COLUMNS]]


# --- manifesto -----------------------------------------------------------------


def content_sha(segments: Iterable[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for seg in segments:
        digest.update(seg["sha256"].encode())
    return digest.hexdigest()


def series_entry(
    role: str,
    series: SeriesRef,
    requested_start: Any,
    requested_end: Any,
    frame: pd.DataFrame,
    segments: list[dict[str, Any]],
) -> dict[str, Any]:
    first = last = None
    if frame is not None and not frame.empty:
        first, last = pd.DatetimeIndex(frame.index).min(), pd.DatetimeIndex(frame.index).max()
    version_label = (
        f"{series.data_version}+r{DERIVED_15M_RULE_VERSION}"
        if series.is_derived
        else str(series.data_version)
    )
    return {
        "role": role,
        "series_id": series.series_id,
        "asset_id": series.asset_id,
        "symbol": series.symbol,
        "asset_class": series.asset_class,
        "source": series.source,
        "source_label": SOURCE_LABELS.get(series.source, series.source),
        "session": series.session,
        "adjustment": series.adjustment,
        "timeframe": series.timeframe,
        "origin": series.origin,
        "data_version": series.data_version,
        "version_label": version_label,
        "requested": {"start": iso(requested_start), "end": iso(requested_end)},
        "covered": {
            "start": iso(first),
            "end": iso(last),
            "candles": int(len(frame)) if frame is not None else 0,
        },
        "segments": segments,
        "sha256": content_sha(segments),
        "rows": int(sum(s["rows"] for s in segments)),
    }


def create_manifest(
    engine: Engine,
    *,
    kind: str,
    entries: list[dict[str, Any]],
    owner_ref: str | None = None,
    snapshot_id: str | None = None,
    retain_days: int = RETENTION_DAYS,
) -> str:
    """Grava o manifesto. ``retain_until`` já nasce com 30 dias de folga (execução que morre não vira órfã)."""

    sid = snapshot_id or uuid.uuid4().hex
    now = _now()
    flat = [{"sha256": s["sha256"], "bytes": s["bytes"]} for e in entries for s in e["segments"]]
    starts = [to_utc(e["requested"]["start"]) for e in entries if e["requested"]["start"]]
    ends = [to_utc(e["requested"]["end"]) for e in entries if e["requested"]["end"]]
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO execution_data_snapshots "
                "(snapshot_id, kind, owner_ref, series, segments, window_start, window_end, "
                "created_at, retain_until, pinned) "
                "VALUES (:id, :kind, :owner, CAST(:series AS jsonb), CAST(:segments AS jsonb), "
                ":ws, :we, :now, :ru, FALSE) "
                "ON CONFLICT (snapshot_id) DO UPDATE SET series = EXCLUDED.series, "
                "segments = EXCLUDED.segments, window_start = EXCLUDED.window_start, "
                "window_end = EXCLUDED.window_end"
            ),
            {
                "id": sid,
                "kind": kind,
                "owner": owner_ref,
                "series": json.dumps(entries),
                "segments": json.dumps(flat),
                "ws": min(starts).to_pydatetime() if starts else None,
                "we": max(ends).to_pydatetime() if ends else None,
                "now": now,
                "ru": now + timedelta(days=retain_days),
            },
        )
    return sid


def get_manifest(engine: Engine, snapshot_id: str) -> dict[str, Any] | None:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT snapshot_id, kind, owner_ref, series, window_start, window_end, created_at, "
                "finished_at, retain_until, pinned FROM execution_data_snapshots WHERE snapshot_id = :i"
            ),
            {"i": snapshot_id},
        ).first()
    if row is None:
        return None
    series = row.series if isinstance(row.series, list) else json.loads(row.series or "[]")
    return {
        "snapshot_id": row.snapshot_id,
        "kind": row.kind,
        "owner_ref": row.owner_ref,
        "series": series,
        "window_start": row.window_start,
        "window_end": row.window_end,
        "created_at": row.created_at,
        "finished_at": row.finished_at,
        "retain_until": row.retain_until,
        "pinned": bool(row.pinned),
    }


def entry_for(manifest: dict[str, Any], role: str) -> dict[str, Any] | None:
    return next((e for e in manifest["series"] if e["role"] == role), None)


def load_frame(
    engine: Engine, snapshot_id: str, role: str, root: Path | None = None
) -> pd.DataFrame:
    manifest = get_manifest(engine, snapshot_id)
    if manifest is None:
        raise SnapshotError("Amostra não encontrada.", code="frozen_input_invalid")
    entry = entry_for(manifest, role)
    if entry is None:
        raise SnapshotError(f"A amostra não tem o papel {role}.", code="frozen_input_invalid")
    return read_segments(root or snapshot_root(), entry["segments"])


def validate(engine: Engine, snapshot_id: str, root: Path | None = None) -> dict[str, Any]:
    """Confere que todos os segmentos existem e batem com o SHA-256."""

    manifest = get_manifest(engine, snapshot_id)
    if manifest is None:
        raise SnapshotError("Amostra não encontrada.", code="frozen_input_invalid")
    base = root or snapshot_root()
    for entry in manifest["series"]:
        read_segments(base, entry["segments"])
    return manifest


# --- prazo, favorito e coleta de lixo -------------------------------------------


def finish(engine: Engine, snapshot_id: str, when: datetime | None = None) -> None:
    """Fim da execução: ``retain_until`` = fim + 30 dias (nunca encurta; fixado não vence)."""

    when = _aware(when)
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE execution_data_snapshots SET finished_at = :w, "
                "retain_until = GREATEST(COALESCE(retain_until, :ru), :ru) "
                "WHERE snapshot_id = :i"
            ),
            {"w": when, "ru": when + timedelta(days=RETENTION_DAYS), "i": snapshot_id},
        )


def pin(conn, snapshot_id: str) -> None:
    """Amostra de um favorito: fixada, não vence."""

    conn.execute(
        text("UPDATE execution_data_snapshots SET pinned = TRUE WHERE snapshot_id = :i"),
        {"i": snapshot_id},
    )


def release(conn, snapshot_id: str, when: datetime | None = None) -> None:
    """Deixou de ser a amostra de um favorito: 30 dias a partir de agora (regra única)."""

    when = _aware(when)
    conn.execute(
        text(
            "UPDATE execution_data_snapshots SET pinned = FALSE, "
            "retain_until = GREATEST(COALESCE(retain_until, :ru), :ru) WHERE snapshot_id = :i"
        ),
        {"ru": when + timedelta(days=RETENTION_DAYS), "i": snapshot_id},
    )


def expire(engine_or_conn: Any, snapshot_id: str, when: datetime | None = None) -> None:
    """Amostra de uma tentativa que falhou: não sustenta número nenhum, o GC leva."""

    when = _aware(when)
    sql = text(
        "UPDATE execution_data_snapshots SET retain_until = :w, finished_at = COALESCE(finished_at, :w) "
        "WHERE snapshot_id = :i AND pinned = FALSE"
    )
    if isinstance(engine_or_conn, Engine):
        with engine_or_conn.begin() as conn:
            conn.execute(sql, {"w": when, "i": snapshot_id})
    else:
        engine_or_conn.execute(sql, {"w": when, "i": snapshot_id})


def sample_state(row: dict[str, Any] | None, now: datetime | None = None) -> dict[str, Any]:
    """Estado da amostra para a tela: ``kept`` (até quando), ``expired``, ``pinned`` ou ``none``."""

    now = now or _now()
    if row is None:
        return {"state": "none", "retain_until": None}
    if row.get("pinned"):
        return {"state": "pinned", "retain_until": None}
    retain = row.get("retain_until")
    if retain is None:
        return {"state": "none", "retain_until": None}
    if retain.tzinfo is None:
        retain = retain.replace(tzinfo=timezone.utc)
    return {
        "state": "expired" if retain < now else "kept",
        "retain_until": retain.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def states_for(
    engine_or_conn: Any, snapshot_ids: Iterable[str | None], now: datetime | None = None
) -> dict[str, dict[str, Any]]:
    """Estado de várias amostras; manifesto ausente (apagado) conta como vencido."""

    ids = sorted({i for i in snapshot_ids if i})
    if not ids:
        return {}
    sql = text(
        "SELECT snapshot_id, retain_until, pinned FROM execution_data_snapshots "
        "WHERE snapshot_id = ANY(:ids)"
    )
    if isinstance(engine_or_conn, Engine):
        with engine_or_conn.connect() as conn:
            rows = conn.execute(sql, {"ids": ids}).all()
    else:
        rows = engine_or_conn.execute(sql, {"ids": ids}).all()
    found = {r.snapshot_id: {"retain_until": r.retain_until, "pinned": r.pinned} for r in rows}
    out = {}
    for sid in ids:
        if sid in found:
            out[sid] = sample_state(found[sid], now)
        else:
            out[sid] = {"state": "expired", "retain_until": None}
    return out


def collect_garbage(
    engine: Engine, root: Path | None = None, now: datetime | None = None
) -> dict[str, int]:
    """Job diário: apaga manifestos vencidos e, depois, segmentos sem referência."""

    base = root or snapshot_root()
    now = now or _now()
    with engine.begin() as conn:
        deleted = conn.execute(
            text(
                "DELETE FROM execution_data_snapshots WHERE pinned = FALSE "
                "AND retain_until IS NOT NULL AND retain_until < :now "
                # Favorito (atual) ainda aponta? Nunca apaga o que está referenciado.
                "AND snapshot_id NOT IN (SELECT snapshot_id FROM favorite_strategies "
                "WHERE snapshot_id IS NOT NULL)"
            ),
            {"now": now},
        ).rowcount
        referenced: set[str] = set()
        for (flat,) in conn.execute(text("SELECT segments FROM execution_data_snapshots")):
            items = flat if isinstance(flat, list) else json.loads(flat or "[]")
            referenced.update(item["sha256"] for item in items)
    removed = 0
    freed = 0
    total = 0
    seg_root = base / "segments"
    if seg_root.exists():
        cutoff = now.timestamp() - SEGMENT_GRACE_SECONDS
        candidates = []
        for path in seg_root.rglob("*.parquet"):
            size = path.stat().st_size
            if path.stem in referenced or path.stat().st_mtime > cutoff:
                total += size
            else:
                candidates.append((path, size))
        if candidates:
            # Um manifesto pode ter nascido depois da primeira leitura: confere de novo.
            with engine.connect() as conn:
                for (flat,) in conn.execute(text("SELECT segments FROM execution_data_snapshots")):
                    items = flat if isinstance(flat, list) else json.loads(flat or "[]")
                    referenced.update(item["sha256"] for item in items)
        for path, size in candidates:
            if path.stem in referenced:
                total += size
                continue
            path.unlink(missing_ok=True)
            removed += 1
            freed += size
        for directory in sorted(seg_root.glob("*"), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
    if total > ALERT_BYTES:
        logger.warning("Segmentos de amostra passam de 5 GiB (%d bytes): revisar o prazo.", total)
    return {
        "manifests_deleted": int(deleted),
        "segments_deleted": removed,
        "bytes_freed": freed,
        "bytes_kept": total,
    }
