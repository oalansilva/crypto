"""Reprodução exata de um favorito pela amostra do último refresh (card #1118, decisão 18).

Disponível no serviço e na API; a tela só mostra o estado da amostra (decisão 1 do
Design). Refazer igual lê apenas os segmentos do manifesto, confere o SHA-256 e
compara as métricas com o número que aparece em ``/favorites``.
"""

from __future__ import annotations

import json
import math
import os
import threading
from contextlib import contextmanager
from typing import Any, Callable

from app.services.market_history import snapshots

NOT_REPRODUCIBLE = "não reproduzível exatamente"
_ENV_LOCK = threading.Lock()
_ENV_KEYS = ("DISCOVERY_FROZEN_SNAPSHOT_ID", "DISCOVERY_FROZEN_SEGMENTS")
TOLERANCE = 1e-9


def sample_status(engine, snapshot_id: str | None) -> dict[str, Any]:
    """Estado da amostra em linguagem de produto."""

    if not snapshot_id:
        return {
            "snapshot_id": None,
            "state": "none",
            "reproducible": False,
            "retain_until": None,
            "message": "Sem amostra guardada: a reprodução exata não é prometida.",
        }
    state = snapshots.states_for(engine, [snapshot_id])[snapshot_id]
    reproducible = state["state"] in {"kept", "pinned"}
    if state["state"] == "expired":
        message = f"Amostra expirada: {NOT_REPRODUCIBLE}."
    elif state["state"] == "pinned":
        message = "Amostra do último refresh: refazer igual reproduz o número de Favoritos."
    else:
        message = "Amostra guardada pelo prazo fixo."
    return {
        "snapshot_id": snapshot_id,
        "state": state["state"],
        "reproducible": reproducible,
        "retain_until": state["retain_until"],
        "message": message,
    }


@contextmanager
def frozen_environment(manifest: dict[str, Any]):
    """Aponta o processo para a amostra durante a execução (travado: um por vez)."""

    from app.services import discovery_inputs

    segments = {entry["role"]: entry["segments"] for entry in manifest["series"]}
    with _ENV_LOCK:
        saved = {key: os.environ.get(key) for key in _ENV_KEYS}
        os.environ["DISCOVERY_FROZEN_SNAPSHOT_ID"] = manifest["snapshot_id"]
        os.environ["DISCOVERY_FROZEN_SEGMENTS"] = json.dumps(segments)
        discovery_inputs._SAMPLE_FRAMES.clear()
        try:
            yield
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            discovery_inputs._SAMPLE_FRAMES.clear()


def _numbers(metrics: dict[str, Any]) -> dict[str, float]:
    out = {}
    for key, value in (metrics or {}).items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if isinstance(value, float) and not math.isfinite(value):
            continue
        out[key] = float(value)
    return out


def compare_metrics(
    stored: dict[str, Any], reproduced: dict[str, Any]
) -> dict[str, dict[str, float]]:
    """Diferenças numéricas acima da tolerância nas chaves presentes dos dois lados."""

    a, b = _numbers(stored), _numbers(reproduced)
    deltas = {}
    for key in sorted(set(a) & set(b)):
        scale = max(abs(a[key]), abs(b[key]), 1e-12)
        if abs(a[key] - b[key]) / scale > TOLERANCE:
            deltas[key] = {"stored": a[key], "reproduced": b[key]}
    return deltas


def reproduce_favorite(
    favorite: Any,
    *,
    engine=None,
    optimizer_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    """Refaz o último refresh do favorito só com a amostra guardada e compara com ``/favorites``."""

    if engine is None:
        from app.database import engine as app_engine

        engine = app_engine
    status = sample_status(engine, favorite.snapshot_id)
    if not status["reproducible"]:
        return {"reproduced": False, "status": status, "metrics_match": None, "deltas": {}}

    manifest = snapshots.validate(engine, favorite.snapshot_id)
    candles = snapshots.entry_for(manifest, "candles")
    if candles is None:
        return {
            "reproduced": False,
            "status": {**status, "reproducible": False, "message": NOT_REPRODUCIBLE},
            "metrics_match": None,
            "deltas": {},
        }
    from app.services.favorite_backtest_refresh_service import (
        _decode_jsonish,
        _favorite_direction,
        _fixed_optimization_ranges,
    )

    parameters = _decode_jsonish(favorite.parameters)
    parameters = parameters if isinstance(parameters, dict) else {}
    if optimizer_factory is None:
        from app.services.combo_optimizer import ComboOptimizer

        optimizer_factory = ComboOptimizer
    start = candles["requested"]["start"]
    end = (candles["requested"]["end"] or "")[:10] or None
    with frozen_environment(manifest):
        result = optimizer_factory().run_optimization(
            template_name=favorite.strategy_name,
            symbol=favorite.symbol,
            timeframe=favorite.timeframe,
            data_source="ccxt",
            start_date=(start or "")[:10] or favorite.start_date,
            end_date=end,
            custom_ranges=_fixed_optimization_ranges(parameters),
            deep_backtest=True,
            direction=_favorite_direction(parameters),
        )
    reproduced = result.get("best_metrics") or result.get("metrics") or {}
    stored = _decode_jsonish(favorite.metrics)
    stored = stored if isinstance(stored, dict) else {}
    deltas = compare_metrics(stored, reproduced)
    return {
        "reproduced": True,
        "status": status,
        "metrics_match": not deltas,
        "deltas": deltas,
        "metrics": reproduced,
        "candles": int(candles["rows"]),
        "sha256": candles["sha256"],
    }
