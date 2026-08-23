"""Discovery sweep orchestration (card #469).

Varredura sistemática de estratégias swing: preflight server-side, criação
idempotente com snapshot imutável, máquina de estados completa, claim com
lease, outbox at-least-once, leaderboard determinístico, deduplicação por
identidade de estratégia e promoção exclusivamente tier 3.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import FavoriteStrategy
from app.models_discovery import (
    DiscoveryCombination,
    DiscoveryDedupEvidence,
    DiscoveryOutbox,
    DiscoveryResult,
    DiscoverySweep,
    strategy_identity_key,
)

logger = logging.getLogger(__name__)

# --- Limites e defaults (configuráveis/versionados; spec discovery-sweep) ---
DISCOVERY_SWING_TIMEFRAMES = ("4h", "1d")
DISCOVERY_DIRECTIONS = ("long", "short")
DEFAULT_MAX_TOTAL = int(__import__("os").getenv("DISCOVERY_MAX_TOTAL", "1000"))
SNAPSHOT_TTL_SECONDS = int(__import__("os").getenv("DISCOVERY_SNAPSHOT_TTL", "600"))
LEASE_SECONDS = int(__import__("os").getenv("DISCOVERY_LEASE_SECONDS", "300"))
OUTBOX_POLL_LIMIT = 100
OUTBOX_BATCH_SIZE = 20
OUTBOX_MAX_GLOBAL = 8
OUTBOX_MAX_PER_SWEEP = 1
CLAIM_BATCH = 20

# Elegibilidade default (spec discovery-leaderboard): trades >= 30, coverage >= 0.90
MIN_ELIGIBLE_TRADES = int(__import__("os").getenv("DISCOVERY_MIN_TRADES", "30"))
MIN_ELIGIBLE_COVERAGE = float(__import__("os").getenv("DISCOVERY_MIN_COVERAGE", "0.90"))

SWEEP_STATES = {
    "pending": {"running", "cancelling", "failed"},
    "running": {"paused", "cancelling", "completed", "partial_failure", "failed"},
    "paused": {"running", "cancelling", "failed"},
    "cancelling": {"cancelled", "failed"},
    "cancelled": set(),
    "failed": set(),
    "partial_failure": set(),
    "completed": set(),
}
TERMINAL_STATES = {"cancelled", "failed", "partial_failure", "completed"}
NON_TERMINAL_STATES = {"pending", "running", "paused", "cancelling"}

STRUCTURE_VERSION = "discovery-structure-v1"
QUANTUM_VERSION = "discovery-quantum-v1"
CANONICAL_ALIASES = {
    "sma": "SMA",
    "ema": "EMA",
    "rsi": "RSI",
    "macd": "MACD",
    "bb": "BB",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _utc_iso(dt: datetime | None) -> str | None:
    return dt.astimezone(timezone.utc).isoformat() if dt else None


def _canonical_axis_value(value: Any) -> str:
    return str(value).strip()


def _canonicalize_idempotency_payload(payload: dict[str, Any]) -> dict[str, Any]:
    canonical = dict(payload)
    for key in ("templates", "symbols", "timeframes", "directions"):
        if key not in canonical or not isinstance(canonical[key], list):
            continue
        values = [
            _canonical_axis_value(item) for item in canonical[key] if _canonical_axis_value(item)
        ]
        if key == "symbols":
            values = [item.upper() for item in values]
        canonical[key] = sorted(set(values))
    return canonical


def _payload_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        _canonicalize_idempotency_payload(payload),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def _normalize_symbols(symbols: list[str]) -> list[str]:
    return sorted({s.upper().strip() for s in symbols if s and s.strip()})


def _normalize_aliases(value: Any) -> Any:
    if isinstance(value, str):
        return CANONICAL_ALIASES.get(value.lower(), value)
    if isinstance(value, dict):
        return {k: _normalize_aliases(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_aliases(v) for v in value]
    return value


def _quantize(value: float, quantum: float) -> int:
    """round_half_away_from_zero(value / quantum) (spec discovery-deduplication)."""
    scaled = value / quantum if quantum else value
    if scaled >= 0:
        return math.floor(scaled + 0.5)
    return math.ceil(scaled - 0.5)


def _canonical_parameters(
    parameters: dict[str, Any], template_metadata: dict[str, Any]
) -> dict[str, Any]:
    """Aliases -> defaults -> quantização determinística."""
    from app.services.combo_service import ComboService

    metadata = template_metadata or {}
    schema = metadata.get("optimization_schema") or {}
    normalized = _normalize_aliases(parameters or {})
    canonical: dict[str, Any] = {}
    for key, value in normalized.items():
        if isinstance(value, bool) or isinstance(value, str) or isinstance(value, int):
            canonical[key] = value
            continue
        if isinstance(value, float):
            field_schema = schema.get(key) or {}
            quantum = float(field_schema.get("quantum") or 1.0)
            canonical[key] = _quantize(value, quantum)
            continue
        canonical[key] = value
    return canonical


def build_strategy_identity(
    *,
    template_id: str,
    parameters: dict[str, Any],
    symbol: str,
    timeframe: str,
    direction: str,
    template_metadata: dict[str, Any] | None = None,
) -> str:
    canonical = _canonical_parameters(parameters, template_metadata or {})
    body = {
        "template": template_id,
        "parameters": canonical,
        "symbol": symbol,
        "timeframe": timeframe,
        "direction": direction,
    }
    return strategy_identity_key(
        structure_version=STRUCTURE_VERSION,
        canonical=json.dumps(body, sort_keys=True, separators=(",", ":")),
    )


def build_evidence_fingerprint(
    *,
    start_at: datetime,
    end_at: datetime,
    candle_source: str | None,
    candle_version: str | None,
    expected_candles: int | None,
    observed_valid_candles: int | None,
    coverage: float | None,
    fees_slippage: dict[str, Any] | None,
    metrics: dict[str, Any],
) -> str:
    payload = {
        "start_at": _utc_iso(start_at),
        "end_at": _utc_iso(end_at),
        "candle_source": candle_source,
        "candle_version": candle_version,
        "expected_candles": expected_candles,
        "observed_valid_candles": observed_valid_candles,
        "coverage": coverage,
        "fees_slippage": fees_slippage,
        "metrics": metrics,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _canonical_templates(templates: list[str]) -> list[str]:
    return sorted({t.strip() for t in templates if t and t.strip()})


class DiscoveryService:
    """Orquestra preflight, criação, lifecycle, claims e leaderboard."""

    def __init__(self) -> None:
        from app.services.combo_service import ComboService

        self.combo_service = ComboService()

    # --- Preflight ---------------------------------------------------------

    def preflight(
        self,
        *,
        templates: list[str],
        symbols: list[str],
        timeframes: list[str],
        directions: list[str],
        start_date: str | None,
        end_date: str | None,
        period_type: str | None,
    ) -> dict[str, Any]:
        from app.services.exchange_service import ExchangeService

        normalized_templates = _canonical_templates(templates)
        normalized_symbols = _normalize_symbols(symbols)
        normalized_timeframes = sorted(
            {tf for tf in timeframes if tf in DISCOVERY_SWING_TIMEFRAMES}
        )
        normalized_directions = sorted({d for d in directions if d in DISCOVERY_DIRECTIONS})

        axis_errors: dict[str, str] = {}
        if not normalized_templates:
            axis_errors["templates"] = "pelo menos um template é obrigatório"
        if not normalized_symbols:
            axis_errors["symbols"] = "pelo menos um símbolo é obrigatório"
        if not normalized_timeframes:
            axis_errors["timeframes"] = "use um ou ambos de 4h/1d"
        if not normalized_directions:
            axis_errors["directions"] = "use long e/ou short"

        catalog = {t["name"]: t for t in self.combo_service.list_templates().get("prebuilt", [])}
        catalog.update(
            {t["name"]: t for t in self.combo_service.list_templates().get("examples", [])}
        )

        # Direção real por template: list_templates não expõe direction, então
        # buscamos a metadata uma única vez por template (evita N chamadas e
        # garante que short só seja excluído quando o template é long-only).
        template_meta: dict[str, dict[str, Any]] = {}
        for template in normalized_templates:
            try:
                template_meta[template] = self.combo_service.get_template_metadata(template) or {}
            except Exception:
                template_meta[template] = {}

        exclusions: dict[str, dict[str, Any]] = {}
        valid: list[dict[str, Any]] = []
        raw_total = (
            len(normalized_templates)
            * len(normalized_symbols)
            * len(normalized_timeframes)
            * len(normalized_directions)
        )
        for template in normalized_templates:
            for symbol in normalized_symbols:
                for timeframe in normalized_timeframes:
                    for direction in normalized_directions:
                        key = f"{template} × {symbol} × {timeframe} × {direction}"
                        reason = self._combination_reason(
                            template, symbol, timeframe, direction, template_meta
                        )
                        if reason:
                            exclusions.setdefault(
                                key,
                                {
                                    "template": template,
                                    "symbol": symbol,
                                    "timeframe": timeframe,
                                    "direction": direction,
                                    "reasons": [],
                                },
                            )
                            if reason not in exclusions[key]["reasons"]:
                                exclusions[key]["reasons"].append(reason)
                            continue
                        valid.append(
                            {
                                "template": template,
                                "symbol": symbol,
                                "timeframe": timeframe,
                                "direction": direction,
                            }
                        )

        valid_total = len(valid)
        if valid_total > DEFAULT_MAX_TOTAL:
            axis_errors["total"] = f"total válido {valid_total} excede o limite {DEFAULT_MAX_TOTAL}"

        snapshot: dict[str, Any] = {
            "templates": normalized_templates,
            "symbols": normalized_symbols,
            "timeframes": normalized_timeframes,
            "directions": normalized_directions,
            "start_date": start_date,
            "end_date": end_date,
            "period_type": period_type,
            "valid_total": valid_total,
            "snapshot_version": "v1",
        }
        snapshot_hash = _payload_hash(snapshot)
        # Token derivado deterministicamente do hash + janela de TTL: criação
        # revalida o mesmo token sem estado compartilhado e snapshots fora da
        # janela de validade são rejeitados.
        token_input = {
            "hash": snapshot_hash,
            "window": int(_utcnow().timestamp() // SNAPSHOT_TTL_SECONDS),
        }
        snapshot_token = hashlib.sha256(
            f"discovery-v1:{json.dumps(token_input, sort_keys=True)}".encode()
        ).hexdigest()
        expiry = _utcnow() + timedelta(seconds=SNAPSHOT_TTL_SECONDS)

        return {
            "axes": {
                "templates": normalized_templates,
                "symbols": normalized_symbols,
                "timeframes": normalized_timeframes,
                "directions": normalized_directions,
            },
            "raw_total": raw_total,
            "exclusions": exclusions,
            "excluded_count": raw_total - valid_total,
            "valid_total": valid_total,
            "limits": {
                "max_total": DEFAULT_MAX_TOTAL,
                "snapshot_ttl_seconds": SNAPSHOT_TTL_SECONDS,
                "global_concurrency": OUTBOX_MAX_GLOBAL,
                "per_sweep_concurrency": OUTBOX_MAX_PER_SWEEP,
            },
            "errors": axis_errors,
            "expires_at": _utc_iso(expiry),
            "snapshot_token": snapshot_token,
            "snapshot_hash": snapshot_hash,
            "start_date": start_date,
            "end_date": end_date,
            "period_type": period_type,
            "combinations": valid,
        }

    def _combination_reason(
        self,
        template: str,
        symbol: str,
        timeframe: str,
        direction: str,
        template_meta: dict[str, dict[str, Any]],
    ) -> str | None:
        from app.services.opportunity_service import is_excluded_symbol

        if template not in template_meta:
            return "template não suportado"
        if is_excluded_symbol(symbol):
            return "símbolo excluído"
        meta = template_meta[template]
        template_direction = str(meta.get("direction") or "long")
        if direction == "short" and template_direction == "long":
            return "template não suporta short"
        return None

    # --- Criação idempotente ----------------------------------------------

    def create_sweep(
        self,
        *,
        actor: str,
        idempotency_key: str,
        snapshot_token: str,
        payload: dict[str, Any],
        db: Session,
    ) -> tuple[dict[str, Any], int]:
        # snapshot_hash é validado separadamente contra o snapshot recalculado;
        # o payload hash (idempotência) não inclui o campo de validação.
        idem_payload = {k: v for k, v in payload.items() if k != "snapshot_hash"}
        payload_hash = _payload_hash(idem_payload)

        existing = (
            db.query(DiscoverySweep)
            .filter(
                DiscoverySweep.actor == actor,
                DiscoverySweep.idempotency_key == idempotency_key,
            )
            .first()
        )
        if existing:
            if existing.payload_hash != payload_hash:
                return (
                    {
                        "error": "idempotency conflict",
                        "detail": "mesma chave com payload divergente",
                    },
                    409,
                )
            return {
                "sweep_id": existing.id,
                "state": existing.state,
                "idempotent_retry": True,
            }, 200

        # Revalida o token do snapshot atomicamente (spec discovery-sweep).
        preflight_result = self.preflight(
            templates=payload.get("templates", []),
            symbols=payload.get("symbols", []),
            timeframes=payload.get("timeframes", []),
            directions=payload.get("directions", []),
            start_date=payload.get("start_date"),
            end_date=payload.get("end_date"),
            period_type=payload.get("period_type"),
        )
        if preflight_result["errors"]:
            return (
                {"error": "invalid snapshot", "detail": preflight_result["errors"]},
                400,
            )
        if preflight_result["snapshot_hash"] != payload.get("snapshot_hash"):
            return (
                {
                    "error": "stale snapshot",
                    "detail": "catálogo ou limites mudaram; rode preflight novamente",
                },
                409,
            )
        if preflight_result["snapshot_token"] != snapshot_token:
            return (
                {
                    "error": "stale snapshot token",
                    "detail": "token expirado ou inválido; rode preflight novamente",
                },
                409,
            )

        sweep_id = uuid.uuid4().hex
        total = preflight_result["valid_total"]
        sweep = DiscoverySweep(
            id=sweep_id,
            actor=actor,
            state="pending",
            idempotency_key=idempotency_key,
            payload_hash=payload_hash,
            snapshot_token=snapshot_token,
            snapshot_hash=preflight_result["snapshot_hash"],
            snapshot=preflight_result,
            total=total,
        )
        db.add(sweep)

        for combo in preflight_result.get("combinations") or self._materialize_combinations(
            preflight_result
        ):
            db.add(
                DiscoveryCombination(
                    sweep_id=sweep_id,
                    template_id=combo["template"],
                    symbol=combo["symbol"],
                    timeframe=combo["timeframe"],
                    direction=combo["direction"],
                )
            )

        db.add(DiscoveryOutbox(sweep_id=sweep_id, generation=1, state="pending"))
        try:
            db.commit()
        except Exception:
            db.rollback()
            # Corrida concorrente com a mesma chave: o vencedor já persistiu.
            existing = (
                db.query(DiscoverySweep)
                .filter(
                    DiscoverySweep.actor == actor,
                    DiscoverySweep.idempotency_key == idempotency_key,
                )
                .first()
            )
            if existing:
                if existing.payload_hash != payload_hash:
                    return (
                        {
                            "error": "idempotency conflict",
                            "detail": "mesma chave com payload divergente",
                        },
                        409,
                    )
                return {
                    "sweep_id": existing.id,
                    "state": existing.state,
                    "idempotent_retry": True,
                }, 200
            raise

        # Dispatcher: transiciona pending -> running e publica o wake-up.
        self._start_sweep(db, sweep_id)
        return {"sweep_id": sweep_id, "state": "running", "total": total}, 201

    def _start_sweep(self, db: Session, sweep_id: str) -> None:
        """Dispatcher: pending -> running e entrega o intent do outbox
        (spec discovery-sweep: 'dispatcher starts')."""
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == sweep_id).first()
        if not sweep or sweep.state != "pending":
            return
        sweep.state = "running"
        sweep.started_at = _utcnow()
        sweep.updated_at = _utcnow()
        db.commit()
        self.dispatch_outbox(db=db)

    def _materialize_combinations(self, preflight: dict[str, Any]) -> list[dict[str, Any]]:
        combinations: list[dict[str, Any]] = []
        axes = preflight["axes"]
        exclusions = preflight.get("exclusions") or {}
        for template in axes["templates"]:
            for symbol in axes["symbols"]:
                for timeframe in axes["timeframes"]:
                    for direction in axes["directions"]:
                        key = f"{template} × {symbol} × {timeframe} × {direction}"
                        if key in exclusions:
                            continue
                        combinations.append(
                            {
                                "template": template,
                                "symbol": symbol,
                                "timeframe": timeframe,
                                "direction": direction,
                            }
                        )
        return combinations

    # --- Lifecycle ---------------------------------------------------------

    def _apply_transition(
        self, sweep: DiscoverySweep, target: str
    ) -> tuple[dict[str, Any], int] | None:
        if sweep.state in TERMINAL_STATES:
            return {"sweep_id": sweep.id, "state": sweep.state}, 200
        if sweep.state == "cancelling" and target in ("running", "paused"):
            return (
                {
                    "error": "cancelling prevails",
                    "detail": "pause/resume rejeitados durante cancelamento",
                },
                409,
            )
        if target not in SWEEP_STATES[sweep.state]:
            return (
                {
                    "error": "invalid transition",
                    "detail": f"{sweep.state} → {target} não permitido",
                },
                409,
            )
        sweep.state = target
        sweep.updated_at = _utcnow()
        if target == "running" and sweep.started_at is None:
            sweep.started_at = _utcnow()
        if target == "cancelling":
            sweep.cancellation_requested = True
        if target in TERMINAL_STATES:
            sweep.completed_at = _utcnow()
        return None

    def _transition(
        self, db: Session, sweep: DiscoverySweep, target: str
    ) -> tuple[dict[str, Any], int]:
        error = self._apply_transition(sweep, target)
        if error is not None and error[1] != 200:
            return error
        if error is not None and error[1] == 200 and sweep.state in TERMINAL_STATES:
            db.commit()
            return error
        if error is not None:
            db.commit()
            return error
        db.commit()
        return {"sweep_id": sweep.id, "state": sweep.state}, 200

    def _combination_counts(self, sweep_id: str, db: Session) -> dict[str, int]:
        rows = (
            db.query(DiscoveryCombination.state, func.count())
            .filter(DiscoveryCombination.sweep_id == sweep_id)
            .group_by(DiscoveryCombination.state)
            .all()
        )
        counts = {state: int(n) for state, n in rows}
        succeeded = counts.get("succeeded", 0)
        failed = counts.get("failed", 0)
        skipped = counts.get("skipped", 0)
        return {
            "succeeded": succeeded,
            "failed": failed,
            "skipped": skipped,
            "processed": succeeded + failed + skipped,
            "pending": counts.get("pending", 0),
            "running": counts.get("running", 0),
        }

    def _serialize_sweep(self, sweep: DiscoverySweep, db: Session) -> dict[str, Any]:
        counters = self._combination_counts(sweep.id, db)
        return {
            "sweep_id": sweep.id,
            "state": sweep.state,
            "total": sweep.total,
            "succeeded": counters["succeeded"],
            "failed": counters["failed"],
            "skipped": counters["skipped"],
            "processed": counters["processed"],
            "terminal_reason": sweep.terminal_reason,
            "terminal_code": sweep.terminal_code,
            "draft_key": sweep.idempotency_key,
            "snapshot": sweep.snapshot,
            "started_at": _utc_iso(sweep.started_at),
            "completed_at": _utc_iso(sweep.completed_at),
            "created_at": _utc_iso(sweep.created_at),
            "updated_at": _utc_iso(sweep.updated_at),
        }

    def get_sweep(
        self, sweep_id: str, db: Session, actor: str | None = None
    ) -> dict[str, Any] | None:
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == sweep_id).first()
        if not sweep:
            return None
        if actor is not None and sweep.actor != actor:
            return None
        return self._serialize_sweep(sweep, db)

    def list_active_sweeps(self, actor: str, db: Session) -> list[dict[str, Any]]:
        rows = (
            db.query(DiscoverySweep)
            .filter(
                DiscoverySweep.actor == actor,
                DiscoverySweep.state.in_(tuple(NON_TERMINAL_STATES)),
            )
            .order_by(desc(DiscoverySweep.created_at), desc(DiscoverySweep.id))
            .all()
        )
        return [self._serialize_sweep(row, db) for row in rows]

    def list_history(self, actor: str, db: Session, *, limit: int = 50) -> list[dict[str, Any]]:
        rows = (
            db.query(DiscoverySweep)
            .filter(DiscoverySweep.actor == actor)
            .order_by(desc(DiscoverySweep.created_at), desc(DiscoverySweep.id))
            .limit(limit)
            .all()
        )
        return [
            {
                **self._serialize_sweep(row, db),
                "snapshot_hash": (row.snapshot or {}).get("snapshot_hash"),
            }
            for row in rows
        ]

    def _claimable_pending(self, sweep_id: str, db: Session) -> int:
        return (
            db.query(DiscoveryCombination)
            .filter(
                DiscoveryCombination.sweep_id == sweep_id,
                DiscoveryCombination.state == "pending",
            )
            .count()
        )

    def _lock_sweep(self, db: Session, sweep_id: str) -> DiscoverySweep | None:
        return (
            db.query(DiscoverySweep)
            .filter(DiscoverySweep.id == sweep_id)
            .with_for_update()
            .first()
        )

    def ensure_sweep_wakeup(
        self,
        db: Session,
        sweep_id: str,
        *,
        sweep: DiscoverySweep | None = None,
        rotate_from: int | None = None,
    ) -> dict[str, Any]:
        """Garante no máximo um wake-up reclamável (pending/delivered) para o sweep.

        Não cria intent enquanto o sweep está paused ou cancelling. Sweep pending
        com combinações é promovido a running sob o lock da linha pai.
        Com rotate_from, insere a próxima generation pending mesmo se a generation
        atual ainda estiver delivered (rotação antes do ACK).
        """
        locked = sweep or self._lock_sweep(db, sweep_id)
        if not locked:
            return {"sweep_id": sweep_id, "wake_up_state": None, "created": False}
        now = _utcnow()
        if locked.state == "pending":
            locked.state = "running"
            if locked.started_at is None:
                locked.started_at = now
            locked.updated_at = now
        if locked.state != "running":
            return {
                "sweep_id": locked.id,
                "state": locked.state,
                "wake_up_state": None,
                "created": False,
            }
        if self._claimable_pending(locked.id, db) <= 0:
            outstanding = (
                db.query(DiscoveryOutbox)
                .filter(
                    DiscoveryOutbox.sweep_id == locked.id,
                    DiscoveryOutbox.state.in_(("pending", "delivered")),
                )
                .order_by(desc(DiscoveryOutbox.generation))
                .first()
            )
            return {
                "sweep_id": locked.id,
                "state": locked.state,
                "wake_up_state": outstanding.state if outstanding else None,
                "generation": outstanding.generation if outstanding else None,
                "created": False,
            }
        pending_intent = (
            db.query(DiscoveryOutbox)
            .filter(
                DiscoveryOutbox.sweep_id == locked.id,
                DiscoveryOutbox.state == "pending",
            )
            .order_by(desc(DiscoveryOutbox.generation))
            .first()
        )
        if pending_intent is not None:
            return {
                "sweep_id": locked.id,
                "state": locked.state,
                "wake_up_state": pending_intent.state,
                "generation": pending_intent.generation,
                "created": False,
            }
        delivered_intent = (
            db.query(DiscoveryOutbox)
            .filter(
                DiscoveryOutbox.sweep_id == locked.id,
                DiscoveryOutbox.state == "delivered",
            )
            .order_by(desc(DiscoveryOutbox.generation))
            .first()
        )
        if delivered_intent is not None and (
            rotate_from is None or delivered_intent.generation != rotate_from
        ):
            return {
                "sweep_id": locked.id,
                "state": locked.state,
                "wake_up_state": delivered_intent.state,
                "generation": delivered_intent.generation,
                "created": False,
            }
        max_gen = (
            db.query(func.max(DiscoveryOutbox.generation))
            .filter(DiscoveryOutbox.sweep_id == locked.id)
            .scalar()
        )
        next_gen = int(max_gen or 0) + 1
        intent = DiscoveryOutbox(sweep_id=locked.id, generation=next_gen, state="pending")
        nested = db.begin_nested()
        try:
            db.add(intent)
            db.flush()
            nested.commit()
        except IntegrityError:
            nested.rollback()
            existing = (
                db.query(DiscoveryOutbox)
                .filter(
                    DiscoveryOutbox.sweep_id == locked.id,
                    DiscoveryOutbox.state.in_(("pending", "delivered")),
                )
                .order_by(desc(DiscoveryOutbox.generation))
                .first()
            )
            return {
                "sweep_id": locked.id,
                "state": locked.state,
                "wake_up_state": existing.state if existing else None,
                "generation": existing.generation if existing else None,
                "created": False,
            }
        return {
            "sweep_id": locked.id,
            "state": locked.state,
            "wake_up_state": "pending",
            "generation": next_gen,
            "created": True,
        }

    def _wakeup_status(self, db: Session, sweep_id: str) -> dict[str, Any]:
        outstanding = (
            db.query(DiscoveryOutbox)
            .filter(
                DiscoveryOutbox.sweep_id == sweep_id,
                DiscoveryOutbox.state.in_(("pending", "delivered")),
            )
            .order_by(desc(DiscoveryOutbox.generation))
            .first()
        )
        latest = (
            db.query(DiscoveryOutbox)
            .filter(DiscoveryOutbox.sweep_id == sweep_id)
            .order_by(desc(DiscoveryOutbox.generation))
            .first()
        )
        wake_state = outstanding.state if outstanding else (latest.state if latest else None)
        return {
            "wake_up_state": wake_state,
            "generation": (outstanding or latest).generation if (outstanding or latest) else None,
        }

    def command(
        self, sweep_id: str, command: str, db: Session, actor: str | None = None
    ) -> tuple[dict[str, Any], int]:
        sweep = self._lock_sweep(db, sweep_id)
        if not sweep:
            return {"error": "sweep not found"}, 404
        if actor is not None and sweep.actor != actor:
            return {"error": "sweep not found"}, 404
        target = {"pause": "paused", "resume": "running", "cancel": "cancelling"}.get(command)
        if not target:
            return {"error": "unknown command"}, 400
        if command == "resume" and sweep.state == "running":
            wake = self.ensure_sweep_wakeup(db, sweep.id, sweep=sweep)
            del wake
            db.commit()
            published = self.dispatch_outbox(db=db)
            status = self._wakeup_status(db, sweep.id)
            if status.get("wake_up_state") == "delivered":
                dispatch_status = "published"
            elif status.get("wake_up_state") == "pending":
                dispatch_status = "deferred" if published == 0 else "queued"
            else:
                dispatch_status = "idle"
            body = self.get_sweep(sweep.id, db) or {"sweep_id": sweep.id, "state": sweep.state}
            body.update(
                {
                    "wake_up_state": status.get("wake_up_state"),
                    "dispatch_status": dispatch_status,
                }
            )
            return body, 200
        if command == "pause" and sweep.state == "paused":
            db.commit()
            return {"sweep_id": sweep.id, "state": sweep.state}, 200
        if command == "cancel" and sweep.state in ("cancelling", "cancelled"):
            db.commit()
            return {"sweep_id": sweep.id, "state": sweep.state}, 200
        error = self._apply_transition(sweep, target)
        if error is not None:
            db.commit()
            return error
        wake = {"wake_up_state": None, "created": False}
        if command == "resume" and sweep.state == "running":
            wake = self.ensure_sweep_wakeup(db, sweep.id, sweep=sweep)
        db.commit()
        dispatch_status = "idle"
        if command == "resume" and sweep.state == "running":
            published = self.dispatch_outbox(db=db)
            status = self._wakeup_status(db, sweep.id)
            if status.get("wake_up_state") == "delivered":
                dispatch_status = "published"
            elif status.get("wake_up_state") == "pending":
                dispatch_status = "deferred" if published == 0 else "queued"
            else:
                dispatch_status = "idle"
            body = self.get_sweep(sweep.id, db) or {"sweep_id": sweep.id, "state": sweep.state}
            body.update(
                {
                    "wake_up_state": status.get("wake_up_state"),
                    "dispatch_status": dispatch_status,
                }
            )
            return body, 200
        return {"sweep_id": sweep.id, "state": sweep.state}, 200

    # --- Claims / leases (spec discovery-sweep) ----------------------------

    def claim_combinations(
        self,
        sweep_id: str,
        owner: str,
        limit: int = CLAIM_BATCH,
        db: Session | None = None,
    ) -> list[DiscoveryCombination]:
        from app.database import SessionLocal

        session = db or SessionLocal()
        try:
            sweep = session.query(DiscoverySweep).filter(DiscoverySweep.id == sweep_id).first()
            if not sweep or sweep.state != "running":
                return []
            now = _utcnow()
            claimed: list[DiscoveryCombination] = []
            rows = (
                session.query(DiscoveryCombination)
                .filter(
                    DiscoveryCombination.sweep_id == sweep_id,
                    DiscoveryCombination.state == "pending",
                )
                .order_by(DiscoveryCombination.id.asc())
                .limit(limit)
                .with_for_update(skip_locked=True)
                .all()
            )
            for row in rows:
                row.state = "running"
                row.attempts += 1
                row.lease_owner = owner
                row.lease_expires_at = now + timedelta(seconds=LEASE_SECONDS)
                row.updated_at = now
                claimed.append(row)
            session.commit()
            return claimed
        finally:
            if db is None:
                session.close()

    def release_expired_leases(self, db: Session | None = None) -> int:
        from app.database import SessionLocal

        session = db or SessionLocal()
        try:
            now = _utcnow()
            expired = (
                session.query(DiscoveryCombination)
                .filter(
                    DiscoveryCombination.state == "running",
                    DiscoveryCombination.lease_expires_at.isnot(None),
                    DiscoveryCombination.lease_expires_at < now,
                )
                .all()
            )
            for row in expired:
                if row.result_id:
                    row.state = "succeeded"
                else:
                    row.state = "pending"
                    row.lease_owner = None
                    row.lease_expires_at = None
                row.updated_at = now
            session.commit()
            return len(expired)
        finally:
            if db is None:
                session.close()

    def count_claimable(self, sweep_id: str, db: Session | None = None) -> int:
        """Número de combinações pendentes reclamáveis (para o orquestrador
        decidir se re-agenda wake-up)."""
        from app.database import SessionLocal

        session = db or SessionLocal()
        try:
            return (
                session.query(DiscoveryCombination)
                .filter(
                    DiscoveryCombination.sweep_id == sweep_id,
                    DiscoveryCombination.state == "pending",
                )
                .count()
            )
        finally:
            if db is None:
                session.close()

    # --- Outbox at-least-once (spec discovery-sweep) ------------------------

    def _repair_incomplete_sweeps(self, session: Session) -> None:
        """Promove start interrompido e cria wake-up para running sem intent reclamável."""
        incomplete = (
            session.query(DiscoverySweep)
            .filter(DiscoverySweep.state.in_(("pending", "running")))
            .order_by(DiscoverySweep.created_at.asc())
            .all()
        )
        for row in incomplete:
            locked = self._lock_sweep(session, row.id)
            if not locked:
                continue
            if locked.state in ("pending", "running"):
                self.ensure_sweep_wakeup(session, locked.id, sweep=locked)

    def dispatch_outbox(self, db: Session | None = None) -> int:
        """Lê intents pending (≤100), publica lotes (≤20) respeitando limites
        globais (8) e por sweep (1). Payload idempotente: sweep_id+generation.
        Intents delivered além do TTL de lease voltam a pending (redelivery)."""
        from app.database import SessionLocal

        session = db or SessionLocal()
        published = 0
        try:
            now = _utcnow()
            self._repair_incomplete_sweeps(session)
            # Redelivery: intents entregues há mais de OUTBOX_REDELIVERY_SECONDS
            # voltam a pending (broker caiu antes do ACK; at-least-once).
            stale = (
                session.query(DiscoveryOutbox)
                .filter(
                    DiscoveryOutbox.state == "delivered",
                    DiscoveryOutbox.updated_at
                    < now
                    - timedelta(
                        seconds=int(
                            __import__("os").getenv("DISCOVERY_OUTBOX_REDELIVERY_SECONDS", "600")
                        )
                    ),
                )
                .all()
            )
            for intent in stale:
                intent.state = "pending"
                intent.updated_at = now

            intents = (
                session.query(DiscoveryOutbox)
                .filter(DiscoveryOutbox.state == "pending")
                .order_by(DiscoveryOutbox.created_at.asc())
                .limit(OUTBOX_POLL_LIMIT)
                .all()
            )
            # Limites: contam intents delivered não acked (em voo), por sweep.
            delivered = (
                session.query(DiscoveryOutbox).filter(DiscoveryOutbox.state == "delivered").all()
            )
            global_running = len(delivered)
            per_sweep_running: dict[str, int] = {}
            for intent in delivered:
                per_sweep_running[intent.sweep_id] = per_sweep_running.get(intent.sweep_id, 0) + 1
            for intent in intents:
                if published >= OUTBOX_BATCH_SIZE:
                    break
                if global_running >= OUTBOX_MAX_GLOBAL:
                    break
                if per_sweep_running.get(intent.sweep_id, 0) >= OUTBOX_MAX_PER_SWEEP:
                    continue
                intent.attempts += 1
                intent.updated_at = now
                try:
                    from app.tasks.discovery_tasks import enqueue_sweep_orchestrator

                    enqueue_sweep_orchestrator(intent.sweep_id, intent.generation)
                except Exception:
                    # Keep the durable intent claimable when the broker is down.
                    intent.state = "pending"
                    continue
                intent.state = "delivered"
                global_running += 1
                per_sweep_running[intent.sweep_id] = per_sweep_running.get(intent.sweep_id, 0) + 1
                published += 1
            session.commit()
            return published
        finally:
            if db is None:
                session.close()

    def ack_outbox(self, sweep_id: str, generation: int, db: Session | None = None) -> int:
        """Confirma o wake-up somente após a execução do orquestrador."""
        from app.database import SessionLocal

        session = db or SessionLocal()
        try:
            now = _utcnow()
            updated = (
                session.query(DiscoveryOutbox)
                .filter(
                    DiscoveryOutbox.sweep_id == sweep_id,
                    DiscoveryOutbox.generation == generation,
                    DiscoveryOutbox.state == "delivered",
                )
                .update(
                    {
                        DiscoveryOutbox.state: "acked",
                        DiscoveryOutbox.acked_at: now,
                        DiscoveryOutbox.updated_at: now,
                    },
                    synchronize_session=False,
                )
            )
            session.commit()
            return updated
        finally:
            if db is None:
                session.close()

    # --- Leaderboard (spec discovery-leaderboard) ---------------------------

    def _result_row(
        self,
        row: DiscoveryResult,
        rank: int | None,
        *,
        identity_map: dict[str, dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        identity = (identity_map or {}).get(str(row.template_id or ""), {})
        payload = {
            "rank": rank,
            "result_id": row.id,
            "sweep_id": row.sweep_id,
            "template_id": row.template_id,
            "display_name": identity.get("display_name"),
            "description": identity.get("description"),
            "symbol": row.symbol,
            "timeframe": row.timeframe,
            "direction": row.direction,
            "parameters": row.parameters,
            "metrics": row.metrics,
            "calmar_ratio": row.calmar_ratio,
            "cagr": row.cagr,
            "benchmark_cagr": row.benchmark_cagr,
            "delta_cagr_vs_bh": row.delta_cagr_vs_bh,
            "max_drawdown": row.max_drawdown,
            "sharpe_ratio": row.sharpe_ratio,
            "profit_factor": row.profit_factor,
            "win_rate": row.win_rate,
            "trades_count": row.trades_count,
            "coverage": row.coverage,
            "eligibility": row.eligibility,
            "eligibility_reason": row.eligibility_reason,
            "dedup_state": row.dedup_state,
            "dedup_reference": row.dedup_reference,
            "strategy_identity_key": row.strategy_identity_key,
            "evidence_fingerprint": row.evidence_fingerprint,
            "start_at": _utc_iso(row.start_at),
            "end_at": _utc_iso(row.end_at),
            "candle_source": row.candle_source,
            "candle_version": row.candle_version,
            "expected_candles": row.expected_candles,
            "observed_valid_candles": row.observed_valid_candles,
            "fees_slippage": row.fees_slippage,
        }
        return payload

    def rank_eligible(
        self, sweep_id: str, metric: str = "calmar_ratio", db: Session | None = None
    ) -> list[dict[str, Any]]:
        from app.database import SessionLocal

        session = db or SessionLocal()
        try:
            rows = session.query(DiscoveryResult).filter(DiscoveryResult.sweep_id == sweep_id).all()
            eligible: list[DiscoveryResult] = []
            ineligible: list[DiscoveryResult] = []
            for row in rows:
                if row.eligibility == "eligible":
                    eligible.append(row)
                else:
                    ineligible.append(row)
            finite: list[DiscoveryResult] = []
            na: list[DiscoveryResult] = []
            for row in eligible:
                value = getattr(row, metric)
                if value is None or (isinstance(value, float) and not math.isfinite(value)):
                    na.append(row)
                else:
                    finite.append(row)
            finite.sort(
                key=lambda r: (
                    -float(getattr(r, metric)),
                    -int(r.trades_count or 0),
                    r.id,
                )
            )
            na.sort(key=lambda r: (-int(r.trades_count or 0), r.id))
            ranked = finite + na
            ineligible.sort(key=lambda r: r.id)
            from app.services.combo_service import ComboService

            template_names = [str(row.template_id) for row in rows if row.template_id]
            identity_map = ComboService.identity_map_for_template_names(session, template_names)
            return [
                self._result_row(row, idx + 1, identity_map=identity_map)
                for idx, row in enumerate(ranked)
            ] + [self._result_row(row, None, identity_map=identity_map) for row in ineligible]
        finally:
            if db is None:
                session.close()

    @staticmethod
    def _norm_symbol(value: str) -> str:
        return value.upper().strip().replace("/", "")

    def leaderboard(
        self,
        sweep_id: str,
        metric: str = "calmar_ratio",
        *,
        symbol: str | None = None,
        timeframe: str | None = None,
        direction: str | None = None,
        eligibility: str | None = None,
        offset: int = 0,
        limit: int | None = None,
        db: Session | None = None,
    ) -> tuple[list[dict[str, Any]], int, int]:
        """Leaderboard com rank global preservado sob filtros e paginação.

        Filtros e paginação não re-numeram posições: o rank é calculado sobre
        todos os resultados elegíveis do sweep antes do recorte (spec 3.5).
        """
        ranked = self.rank_eligible(sweep_id, metric=metric, db=db)
        unfiltered_total = len(ranked)
        matched = ranked
        if symbol:
            norm = self._norm_symbol(symbol)
            matched = [r for r in matched if self._norm_symbol(r["symbol"]) == norm]
        if timeframe:
            matched = [r for r in matched if r["timeframe"] == timeframe]
        if direction:
            matched = [r for r in matched if r["direction"] == direction]
        if eligibility:
            matched = [r for r in matched if r["eligibility"] == eligibility]
        total = len(matched)
        if limit is not None:
            matched = matched[offset : offset + limit]
        return matched, total, unfiltered_total

    # --- Promoção tier 3 (spec discovery-promotion) -------------------------

    def promote_result(
        self,
        *,
        result_id: str,
        actor: str,
        idempotency_key: str,
        payload: dict[str, Any],
        db: Session,
    ) -> tuple[dict[str, Any], int]:
        from app.models_discovery import DiscoveryIdempotency
        from app.services.favorite_uniqueness import lock_and_find_duplicate

        payload_hash = _payload_hash(payload)
        existing_idem = (
            db.query(DiscoveryIdempotency)
            .filter(
                DiscoveryIdempotency.actor == actor,
                DiscoveryIdempotency.idempotency_key == idempotency_key,
            )
            .first()
        )
        if existing_idem:
            if existing_idem.payload_hash != payload_hash:
                return ({"error": "idempotency conflict"}, 409)
            return {
                "favorite_id": existing_idem.resource_id,
                "result_id": result_id,
            }, 200

        result = db.query(DiscoveryResult).filter(DiscoveryResult.id == result_id).first()
        if not result:
            return {"error": "result not found"}, 404
        if result.eligibility != "eligible":
            return (
                {
                    "error": "ineligible",
                    "detail": result.eligibility_reason or "baixa amostra",
                },
                422,
            )
        if result.dedup_state == "duplicate_favorite":
            return (
                {
                    "error": "duplicate",
                    "detail": "candidato já duplica favorito ativo",
                    "reference": result.dedup_reference,
                },
                409,
            )
        if result.dedup_state == "already_promoted":
            return {"favorite_id": result.dedup_reference, "result_id": result.id}, 200

        tier = payload.get("tier")
        if tier != 3:
            return {
                "error": "tier must be 3",
                "detail": "promoção exclusivamente tier 3",
            }, 422

        # Lock transacional por identidade de estratégia (spec discovery-deduplication).
        lock_key = int(hashlib.sha256(result.strategy_identity_key.encode()).hexdigest()[:16], 16)
        lock_key &= 0x7FFFFFFFFFFFFFFF  # bigint signed (63 bits)
        from sqlalchemy import text

        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})

        duplicate = None
        try:
            from sqlalchemy import text

            rows = db.execute(
                text(
                    "SELECT id FROM favorite_strategies "
                    "WHERE CAST(metrics AS jsonb)->>'strategy_identity_key' = :key LIMIT 1"
                ),
                {"key": result.strategy_identity_key},
            ).first()
            if rows is not None:
                duplicate = (
                    db.query(FavoriteStrategy).filter(FavoriteStrategy.id == rows[0]).first()
                )
        except Exception:
            # Fallback: varredura em memória quando o schema do favorito não
            # expõe a coluna (ex.: tabela fixture minimalista de teste).
            for fav in db.query(FavoriteStrategy).all():
                metrics = fav.metrics or {}
                if metrics.get("strategy_identity_key") == result.strategy_identity_key:
                    duplicate = fav
                    break
        if duplicate is None:
            duplicate = lock_and_find_duplicate(
                db,
                user_id=actor,
                strategy_name=result.template_id,
                symbol=result.symbol,
                timeframe=result.timeframe,
                period_type="all",
                start_date=result.start_at.date().isoformat(),
                end_date=result.end_at.date().isoformat(),
                parameters=result.parameters,
            )
        if duplicate is not None:
            result.dedup_state = "duplicate_favorite"
            result.dedup_reference = str(duplicate.id)
            db.add(
                DiscoveryDedupEvidence(
                    result_id=result.id,
                    classification="duplicate_favorite",
                    matched_reference=str(duplicate.id),
                    structure_version=STRUCTURE_VERSION,
                    quantum_version=QUANTUM_VERSION,
                )
            )
            db.commit()
            return (
                {
                    "error": "duplicate",
                    "detail": "candidato já duplica favorito",
                    "reference": str(duplicate.id),
                },
                409,
            )

        favorite = FavoriteStrategy(
            user_id=actor,
            name=f"{result.template_id} · {result.symbol} · {result.timeframe} · {result.direction}",
            symbol=result.symbol,
            timeframe=result.timeframe,
            strategy_name=result.template_id,
            parameters=result.parameters,
            tier=3,
            notes=f"descoberta via sweep {result.sweep_id} (result {result.id})",
            start_date=result.start_at.date().isoformat(),
            end_date=result.end_at.date().isoformat(),
            period_type="all",
            metrics={
                "origin_type": "discovery_sweep",
                "sweep_id": result.sweep_id,
                "result_id": result.id,
                "strategy_identity_key": result.strategy_identity_key,
                "evidence_fingerprint": result.evidence_fingerprint,
                "template_version": result.template_version,
                "parameters": result.parameters,
                "metrics_snapshot": result.metrics,
                "promoted_at": _utc_iso(_utcnow()),
            },
        )
        db.add(favorite)
        db.flush()
        result.dedup_state = "already_promoted"
        result.dedup_reference = str(favorite.id)
        result.updated_at = _utcnow()
        db.add(
            DiscoveryIdempotency(
                actor=actor,
                idempotency_key=idempotency_key,
                payload_hash=payload_hash,
                resource_type="promotion",
                resource_id=str(favorite.id),
            )
        )
        try:
            db.commit()
        except Exception:
            db.rollback()
            # Corrida concorrente: o vencedor já registrou a idempotência.
            existing_idem = (
                db.query(DiscoveryIdempotency)
                .filter(
                    DiscoveryIdempotency.actor == actor,
                    DiscoveryIdempotency.idempotency_key == idempotency_key,
                )
                .first()
            )
            if existing_idem:
                if existing_idem.payload_hash != payload_hash:
                    return ({"error": "idempotency conflict"}, 409)
                return {
                    "favorite_id": existing_idem.resource_id,
                    "result_id": result_id,
                }, 200
            raise
        return {"favorite_id": str(favorite.id), "result_id": result.id}, 201
