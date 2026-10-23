"""Durable private candle snapshots reused by every attempt and final evaluation."""

import hashlib
import json
import os
from pathlib import Path
import tempfile

import pandas as pd

from app.services.discovery_resources import (
    OperationalFailure,
    spool_directory,
    GiB,
    mark_spool_owner,
)

SNAPSHOT_ID_ENV = "DISCOVERY_FROZEN_SNAPSHOT_ID"
SNAPSHOT_SEGMENTS_ENV = "DISCOVERY_FROZEN_SEGMENTS"
_SNAPSHOT_ROLES = ("candles", "intraday")


def is_snapshot_manifest(manifest):
    """Manifesto de amostra por segmentos (card #1118) em vez do spool ``inputs-*``."""
    return bool(manifest) and "snapshot_id" in manifest


def frozen_active():
    """True quando a execução lê só de entradas congeladas (spool antigo ou amostra)."""
    return bool(os.getenv("DISCOVERY_FROZEN_INPUT_DIR") or os.getenv(SNAPSHOT_ID_ENV))


def activate(manifest):
    """Aponta o processo (e os workers que herdam o ambiente) para a amostra congelada."""
    if is_snapshot_manifest(manifest):
        os.environ[SNAPSHOT_ID_ENV] = manifest["snapshot_id"]
        os.environ[SNAPSHOT_SEGMENTS_ENV] = json.dumps(
            {role: info["segments"] for role, info in manifest["files"].items()}
        )
    else:
        os.environ["DISCOVERY_FROZEN_INPUT_DIR"] = manifest["directory"]


def _unified():
    from app.services.market_history import unified_enabled

    return unified_enabled()


def _prepare_snapshot(inputs):
    """Congela candles e 15m em segmentos com SHA-256, compartilhados entre execuções."""
    from src.data.incremental_loader import IncrementalLoader
    from app.services.market_data_providers import CcxtMarketDataProvider
    from app.services.market_history.sample import ExecutionSample

    loader = IncrementalLoader()
    frame = CcxtMarketDataProvider(loader).fetch_ohlcv(
        symbol=inputs["symbol"],
        timeframe=inputs["timeframe"],
        since_str=inputs["start_date"],
        until_str=inputs["end_date"],
    )
    intraday = loader.fetch_intraday_data(
        symbol=inputs["symbol"],
        timeframe="15m",
        since_str=inputs["start_date"],
        until_str=inputs["end_date"],
        read_only=False,
    )
    sample = ExecutionSample(
        "discovery", owner_ref=f"discovery:{inputs['symbol']}:{inputs['timeframe']}"
    )
    try:
        sample.freeze_crypto(
            "candles",
            inputs["symbol"],
            inputs["timeframe"],
            inputs["start_date"],
            inputs["end_date"],
            frame,
        )
        sample.freeze_crypto(
            "intraday", inputs["symbol"], "15m", inputs["start_date"], inputs["end_date"], intraday
        )
    except Exception as exc:
        code = getattr(exc, "code", None)
        if code:
            raise OperationalFailure(code) from exc
        raise
    files = {
        role: {
            "sha256": sample.entry(role)["sha256"],
            "rows": sample.entry(role)["rows"],
            "segments": sample.entry(role)["segments"],
        }
        for role in _SNAPSHOT_ROLES
    }
    return {
        "snapshot_id": sample.snapshot_id,
        "files": files,
        "provenance": sample.provenance("candles"),
    }


def prepare(inputs):
    manifest = inputs.get("candle_manifest")
    if manifest:
        validate(manifest)
        return manifest
    if _unified() and "/" in str(inputs.get("symbol", "")):
        return _prepare_snapshot(inputs)
    from src.data.incremental_loader import IncrementalLoader
    from app.services.market_data_providers import CcxtMarketDataProvider

    loader = IncrementalLoader(cache_dir=os.getenv("DISCOVERY_MARKET_CACHE_DIR"))
    frame = CcxtMarketDataProvider(loader).fetch_ohlcv(
        symbol=inputs["symbol"],
        timeframe=inputs["timeframe"],
        since_str=inputs["start_date"],
        until_str=inputs["end_date"],
    )
    intraday = loader.fetch_intraday_data(
        symbol=inputs["symbol"],
        timeframe="15m",
        since_str=inputs["start_date"],
        until_str=inputs["end_date"],
        read_only=False,
    )
    root = Path(tempfile.mkdtemp(prefix="inputs-", dir=spool_directory()))
    mark_spool_owner(root)
    manifest = {"directory": str(root), "files": {}}
    try:
        for name, data in (("candles", frame), ("intraday", intraday)):
            path = root / f"{name}.parquet"
            data.to_parquet(path, index=True)
            path.chmod(0o600)
            with path.open("rb") as handle:
                os.fsync(handle.fileno())
            manifest["files"][name] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "rows": len(data),
            }
        if sum(path.stat().st_size for path in root.iterdir()) > 2 * GiB:
            raise OperationalFailure("input_spool_quota_exceeded")
        descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return manifest
    except BaseException:
        discard(manifest)
        raise


def _validate_snapshot(manifest):
    from app.services.market_history import snapshots

    root = snapshots.snapshot_root()
    try:
        for role, info in manifest["files"].items():
            snapshots.read_segments(root, info["segments"])
    except snapshots.SnapshotError as exc:
        raise OperationalFailure(exc.code) from exc


def validate(manifest):
    if is_snapshot_manifest(manifest):
        return _validate_snapshot(manifest)
    root = Path(manifest["directory"])
    if root.is_symlink():
        raise OperationalFailure("frozen_input_invalid")
    if root.parent.resolve() != spool_directory().resolve() or not root.name.startswith("inputs-"):
        raise OperationalFailure("frozen_input_invalid")
    for name, identity in manifest["files"].items():
        path = root / f"{name}.parquet"
        if path.is_symlink():
            raise OperationalFailure("frozen_input_invalid")
        if hashlib.sha256(path.read_bytes()).hexdigest() != identity["sha256"]:
            raise OperationalFailure("frozen_input_corrupt")


_SAMPLE_FRAMES = {}


def read(name, snapshot_id=None):
    sid = snapshot_id or os.getenv(SNAPSHOT_ID_ENV)
    if sid:
        key = (sid, name)
        cached = _SAMPLE_FRAMES.get(key)
        if cached is not None:
            return cached
        from app.services.market_history import snapshots

        raw = os.getenv(SNAPSHOT_SEGMENTS_ENV) if sid == os.getenv(SNAPSHOT_ID_ENV) else None
        try:
            if raw:
                segments = json.loads(raw)[name]
                frame = snapshots.read_segments(snapshots.snapshot_root(), segments)
            else:
                from app.database import engine

                frame = snapshots.load_frame(engine, sid, name)
        except snapshots.SnapshotError as exc:
            raise OperationalFailure(exc.code) from exc
        _SAMPLE_FRAMES[key] = frame
        return frame
    root = os.getenv("DISCOVERY_FROZEN_INPUT_DIR")
    if not root:
        return None
    return pd.read_parquet(Path(root) / f"{name}.parquet")


class FrozenProvider:
    def fetch_ohlcv(self, **kwargs):
        return read("candles")


def discard(manifest):
    if is_snapshot_manifest(manifest):
        # Soltar a referência, não apagar bytes: a amostra segue por 30 dias (card #1118).
        from app.database import engine
        from app.services.market_history import snapshots

        snapshots.finish(engine, manifest["snapshot_id"])
        return
    root = Path(manifest["directory"])
    if root.is_symlink():
        raise OperationalFailure("frozen_input_invalid")
    if root.parent.resolve() != spool_directory().resolve() or not root.name.startswith("inputs-"):
        raise OperationalFailure("frozen_input_invalid")
    for name in ("candles", "intraday"):
        (root / f"{name}.parquet").unlink(missing_ok=True)
    (root / "owner.json").unlink(missing_ok=True)
    root.rmdir()


def cleanup_unreferenced(manifests):
    from app.services.discovery_supervisor import process_identity
    import json

    referenced = {manifest["directory"] for manifest in manifests if "directory" in manifest}
    for root in spool_directory().glob("inputs-*"):
        if str(root) in referenced or root.is_symlink() or not (root / "owner.json").exists():
            continue
        owner = json.loads((root / "owner.json").read_text())
        if process_identity(owner["pid"]) != owner["start"]:
            discard({"directory": str(root)})
