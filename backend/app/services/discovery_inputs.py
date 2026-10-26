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


class InsufficientHistory(Exception):
    """A Binance não tem candles do ativo nessa janela: amostra insuficiente, não falha (card #1121)."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def history_failure_code(error_code):
    """``history_unavailable:<código da Binance>``: falha de coleta que entra nas 3 tentativas."""

    return f"history_unavailable:{error_code}" if error_code else "history_unavailable"


def _asset_class(inputs):
    """Classe pelo catálogo (``asset_identity``), não pela ``/``; sem catálogo, pelo formato."""

    from app.services.discovery_multiclass import class_of

    symbol = str(inputs.get("symbol", ""))
    known = inputs.get("asset_class")
    if known:
        return class_of(symbol, known)
    if "/" in symbol:
        return "crypto"
    try:
        from app.services.equity_backtest import asset_identity

        found = asset_identity(symbol).get("asset_class")
    except Exception:  # catálogo fora: sem classe, o caminho de antes
        return None
    # Ticker que o catálogo não conhece segue o caminho de antes (sem inventar classe).
    return found if found in ("stock", "etf") else None


def _manifest(sample, data_source, **extra):
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
        "data_source": data_source,
        **extra,
    }


def _prepare_equity(inputs, on_progress=None):
    """Ação/ETF pelo caminho do #1118 (card #1121, decisão 3).

    Coleta a série do tempo gráfico (1d nativo, ou o 5m de onde saem 15m/1h/4h) e o 5m do intrabar
    com ``prepare_equity_history``, lê do ``HistoryService`` e congela nos papéis ``candles`` e
    ``intraday`` (vazio sem 15m). A Binance sem candles na janela vira ``InsufficientHistory``;
    falha de coleta vira ``OperationalFailure`` (``history_unavailable:<código>``) e entra nas
    3 tentativas.
    """
    from app.services.discovery_multiclass import no_candles_reason
    from app.services.equity_backtest import (
        CODE_HISTORY_UNAVAILABLE,
        EquityRunError,
        inclusive_end,
        prepare_equity_history,
    )
    from app.services.market_data_providers import (
        BINANCE_EQUITY_SOURCE,
        BinanceEquityMarketDataProvider,
    )
    from app.services.market_history.facade import (
        get_history_service,
        spec_for_request,
        to_loader_frame,
    )
    from app.services.market_history.sample import ExecutionSample

    symbol = inputs["symbol"]
    timeframe = inputs["timeframe"]
    start, end = inputs["start_date"], inputs["end_date"]
    equity_class = (
        inputs.get("asset_class") if inputs.get("asset_class") in ("stock", "etf") else "stock"
    )

    def progress(role, series_timeframe, page, total):
        if on_progress is not None:
            on_progress(
                {
                    "phase": "collecting",
                    "role": role,
                    "series": series_timeframe,
                    "page": int(page),
                    "pages": int(total) if total else None,
                }
            )

    try:
        prep = prepare_equity_history(
            symbol, timeframe, start, end, intrabar=True, on_progress=progress
        )
    except EquityRunError as exc:
        extra = exc.extra or {}
        if exc.code == CODE_HISTORY_UNAVAILABLE and extra.get("error_code"):
            raise OperationalFailure(history_failure_code(extra["error_code"])) from exc
        if exc.code == CODE_HISTORY_UNAVAILABLE and "não tem candles" in str(
            extra.get("reason") or ""
        ):
            raise InsufficientHistory(
                no_candles_reason(symbol, timeframe, asset_class=equity_class)
            ) from exc
        if exc.code == CODE_HISTORY_UNAVAILABLE:
            # Coleta em pausa ou outra coleta da série em andamento: tenta de novo depois.
            raise OperationalFailure("history_unavailable:collection_busy") from exc
        raise OperationalFailure(exc.code or "history_unavailable") from exc

    # Coleta feita: a leitura é só do guardado, sem nova ida à Binance (como o lote do #1120).
    frame = BinanceEquityMarketDataProvider(ensure=False).fetch_ohlcv(
        symbol=symbol, timeframe=timeframe, since_str=start, until_str=end
    )
    if frame is None or frame.empty:
        raise InsufficientHistory(no_candles_reason(symbol, timeframe, asset_class=equity_class))
    service = get_history_service()
    intraday_series = service.resolve(spec_for_request(symbol=symbol, timeframe="15m"))
    intraday = to_loader_frame(service.read(intraday_series, start, inclusive_end(end)).candles)
    sample = ExecutionSample("discovery", owner_ref=f"discovery:{symbol}:{timeframe}")
    try:
        sample.freeze_symbol("candles", symbol, timeframe, start, end, frame)
        sample.freeze_symbol("intraday", symbol, "15m", start, end, intraday)
    except Exception as exc:
        code = getattr(exc, "code", None)
        if code:
            raise OperationalFailure(code) from exc
        raise
    return _manifest(
        sample,
        BINANCE_EQUITY_SOURCE,
        asset=prep.asset,
        collection=prep.collection,
    )


def _prepare_crypto(inputs):
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
    return _manifest(sample, "ccxt")


def manifest_source(manifest):
    """Fonte que o otimizador recebe (card #1121, decisão 3): ``binance_equity`` ou ``ccxt``."""

    if not manifest:
        return "ccxt"
    if manifest.get("data_source"):
        return manifest["data_source"]
    label = (manifest.get("provenance") or {}).get("data_source")
    return "binance_equity" if label == "Binance Ações" else "ccxt"


def prepare(inputs, on_progress=None):
    """Amostra da combinação: reaproveita o manifesto dado, ou coleta e congela pela classe."""

    manifest = inputs.get("candle_manifest")
    if manifest:
        validate(manifest)
        return manifest
    if _asset_class(inputs) in ("stock", "etf"):
        return _prepare_equity(inputs, on_progress)
    if _unified() and "/" in str(inputs.get("symbol", "")):
        return _prepare_crypto(inputs)
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
