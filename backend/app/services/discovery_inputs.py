"""Durable private candle snapshots reused by every attempt and final evaluation."""

import hashlib
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


def prepare(inputs):
    manifest = inputs.get("candle_manifest")
    if manifest:
        validate(manifest)
        return manifest
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


def validate(manifest):
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


def read(name):
    root = os.getenv("DISCOVERY_FROZEN_INPUT_DIR")
    if not root:
        return None
    return pd.read_parquet(Path(root) / f"{name}.parquet")


class FrozenProvider:
    def fetch_ohlcv(self, **kwargs):
        return read("candles")


def discard(manifest):
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

    referenced = {manifest["directory"] for manifest in manifests}
    for root in spool_directory().glob("inputs-*"):
        if str(root) in referenced or root.is_symlink() or not (root / "owner.json").exists():
            continue
        owner = json.loads((root / "owner.json").read_text())
        if process_identity(owner["pid"]) != owner["start"]:
            discard({"directory": str(root)})
