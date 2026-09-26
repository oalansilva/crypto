"""TypeSafe/Jev client. Key lives only in server env. Never log the secret."""

from __future__ import annotations

import json
import logging
import math
import os
import time
import urllib.error
import urllib.request
import uuid
from decimal import Decimal
from typing import Any, Optional

from app.services.scalp_engine import (
    JEV_CALL_TIMEOUT_MS,
    JEV_LATE_MS,
    TOXIC_NOUL_DECISION,
    TOXIC_NOUL_NOT_TOXIC_BELOW,
    TOXIC_NOUL_TOXIC_ABOVE,
    JevSignal,
    Side,
    SYMBOL,
)
from app.services.scalp_jev_log import (
    ERROR_BODY_READ_BYTES,
    RECORD_TOKEN_CHARS,
    log_call_entry,
    log_call_error,
    log_call_raw,
    log_call_return,
    raw_payload_enabled,
    redact,
    summarize_body,
)
from app.services.scalp_state_window import (
    state_window_arm as ab_arm,
    state_window_s,
)
from app.services.scalp_window import (
    MOVE_BAND_BELOW_COST,
    MOVE_BAND_COVERS_COST,
    MOVE_BAND_COVERS_WITH_SLACK,
    move_band,
)

logger = logging.getLogger(__name__)

# Key lookup (first name wins). Redaction uses the wider list in scalp_jev_log.
_SECRET_ENV_NAMES = ("JEV_API_KEY", "TYPESAFE_API_KEY")
_DEFAULT_BASE_URL = "https://api.typesafe.ai"
_SYSTEMONE_PATH = "/v1/systemone"
# Card #1028: the call requests a fixed model version, never the moving alias
# ``jev-latest`` that changes when the provider publishes. The pinned default
# is the version observed in the repo's DEV evidence (test fixture of the reply,
# ``backend/tests/unit/test_scalp_direcional_jev.py``); it is overridable by
# ``SCALP_JEV_MODEL`` and the alias never comes back through configuration.
_DEFAULT_JEV_MODEL = "jev-1.13.0"
_MOVING_JEV_ALIAS = "jev-latest"

# Ordered Score criteria (ten levels). Index i maps to these exact bp values.
# Card #1029: the reply is read as a position on this ordered scale; the level
# **already reached** (rounded down) is the only bp the cost comparison uses.
_EXPECTED_MOVE_BP_LEVELS_BP: tuple[int, ...] = (0, 5, 10, 15, 20, 25, 30, 35, 50, 80)

# Card #1029: the A/B arm is derived from the effective state window inside
# ``state_window_arm`` (re-exported as ``ab_arm`` so both call sites — the call
# return and the cycle record — inherit the derivation). The independent
# ``SCALP_JEV_AB_ARM`` no longer exists: it could label ``larger`` a call made
# with the 900 s window, the false label the T18 proved.

# Model-facing text of each band (record keeps the token from ``scalp_window``).
_BAND_LABEL_TEXT = {
    MOVE_BAND_BELOW_COST: "below cost",
    MOVE_BAND_COVERS_COST: "covers cost",
    MOVE_BAND_COVERS_WITH_SLACK: "covers cost with slack",
}


def _expected_move_bp_criteria(fee_bp: Decimal, spread_bp: Decimal) -> list[str]:
    """The ten ladder levels, each labelled with its band against the cycle cost.

    Card #1029: the ten options stay (ordered, same ``score`` type, the answer
    is still a position); the label of each level is its band relative to the
    **real cost of this cycle** instead of a bare bp number. The band uses the
    same predicates as the decision, so the label the model sees and the band
    the decision reads agree. The bp of the level stays in the label, next to
    the band, so the ten ordered positions remain distinguishable and the
    shared explanation still lives in the question instructions (card #1025:
    input per call ≤ ~500 tokens).
    """
    return [
        f"{bp} bp ({_BAND_LABEL_TEXT[move_band(Decimal(str(bp)), fee_bp, spread_bp)]})"
        for bp in _EXPECTED_MOVE_BP_LEVELS_BP
    ]


def _credited_level_index(score: Any) -> int:
    """Index of the level **already reached** by ``score``: clipped, floored.

    Card #1029: between two levels the reply credits the lower one (the level
    already reached), never the interpolated magnitude. Values at or beyond the
    ends of the scale clip to the first/last level; a missing/invalid score is
    read as level 0 (today's defensive zero).
    """
    levels = _EXPECTED_MOVE_BP_LEVELS_BP
    if not levels:
        return 0
    try:
        value = float(score)
    except (TypeError, ValueError):
        return 0
    if math.isnan(value):
        return 0
    if value <= 0:
        return 0
    max_idx = len(levels) - 1
    if value >= max_idx:
        return max_idx
    return int(math.floor(value))


def _credited_level_bp(score: Any) -> Decimal:
    """Exact bp of the level already reached (card #1029, decision 2)."""
    levels = _EXPECTED_MOVE_BP_LEVELS_BP
    if not levels:
        return Decimal("0")
    return Decimal(str(levels[_credited_level_index(score)]))


def jev_api_key() -> Optional[str]:
    for name in _SECRET_ENV_NAMES:
        value = (os.getenv(name) or "").strip()
        if value:
            return value
    return None


def jev_available() -> bool:
    if jev_api_key():
        return True
    return _stand_in_enabled()


def _stand_in_enabled() -> bool:
    return (os.getenv("JEV_STAND_IN") or "").strip().lower() in {"1", "true", "yes", "on"}


def jev_model() -> str:
    """Fixed model version requested by the call (card #1028).

    Never returns the moving alias: an empty/alias override falls back to the
    pinned default, so ``jev-latest`` cannot come back through configuration.
    """
    raw = (os.getenv("SCALP_JEV_MODEL") or "").strip()
    if not raw or raw.lower() == _MOVING_JEV_ALIAS:
        return _DEFAULT_JEV_MODEL
    return raw


def _base_url() -> str:
    return (os.getenv("JEV_BASE_URL") or "").strip().rstrip("/")


def _endpoint_url() -> str:
    return f"{_base_url() or _DEFAULT_BASE_URL}{_SYSTEMONE_PATH}"


def _redact(message: str) -> str:
    """Never log a secret: replace every configured env value and bearer token."""
    return redact(message)


def _parse_side(value: Any) -> Optional[Side]:
    token = str(value or "").strip().upper()
    if token in {"BUY", "SELL"}:
        return token  # type: ignore[return-value]
    return None


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _decimal(value: Any, default: str = "0") -> Decimal:
    try:
        return Decimal(str(value if value is not None else default))
    except Exception:
        return Decimal(default)


def _payload_cost_bp(payload: Any) -> tuple[Decimal, Decimal]:
    """``(fee_bp, spread_bp)`` carried by the state the call is built from.

    Card #1029: the band labels of the question need the **real cost of the
    cycle**. The payload already carries it (``state.account.fee_bp`` from the
    signed maker read, ``state.touch.spread_bp`` from the fresh touch), so the
    question is labelled from the same cost the entry predicates use without a
    new argument on the client call. A missing cost reads as zero (no cost),
    which only affects synthetic payloads — the service always sends both.
    """
    state = _as_dict(_as_dict(payload).get("state")) or _as_dict(payload)
    account = _as_dict(state.get("account"))
    touch = _as_dict(state.get("touch"))
    return _decimal(account.get("fee_bp")), _decimal(touch.get("spread_bp"))


def _hold_signal(latency_ms: int, *, model: Optional[str] = None) -> JevSignal:
    return JevSignal(
        side=None,
        confidence=Decimal("0"),
        expected_move_bp=Decimal("0"),
        book_toxic=False,
        latency_ms=latency_ms,
        cost_quote=Decimal("0"),
        model=model,
    )


def stand_in_signal(*, latency_ms: int = 1) -> JevSignal:
    """Test/dev stand-in. Live without a key MUST NOT send (caller checks jev_api_key)."""
    side = _parse_side(os.getenv("JEV_STAND_IN_SIDE"))
    confidence_raw = (os.getenv("JEV_STAND_IN_CONFIDENCE") or "0").strip()
    try:
        confidence = Decimal(confidence_raw)
    except Exception:
        confidence = Decimal("0")
    move_raw = (os.getenv("JEV_STAND_IN_MOVE_BP") or os.getenv("JEV_STAND_IN_EDGE") or "25").strip()
    try:
        expected_move_bp = Decimal(move_raw)
    except Exception:
        expected_move_bp = Decimal("25")
    toxic = (os.getenv("JEV_STAND_IN_TOXIC") or "").strip().lower() in {"1", "true", "yes", "on"}
    return JevSignal(
        side=side,
        confidence=confidence,
        expected_move_bp=expected_move_bp,
        book_toxic=toxic,
        latency_ms=latency_ms,
        cost_quote=Decimal("0"),
    )


def _systemone_payload(payload: dict[str, Any]) -> dict[str, Any]:
    state = payload.get("state") if isinstance(payload.get("state"), dict) else payload
    fee_bp, spread_bp = _payload_cost_bp(payload)
    return {
        "state": state,
        "model": jev_model(),
        "questions": {
            "side": {
                "type": "choice",
                "instructions": (
                    "Directional BTCUSDT scalp this cycle: post-only BUY at the best bid, "
                    "SELL at the best ask, or HOLD (send nothing)."
                ),
                "criteria": {
                    "BUY": "Post-only buy",
                    "SELL": "Post-only sell",
                    "HOLD": "Do not send",
                },
            },
            "expected_move_bp": {
                "type": "score",
                "instructions": (
                    "Expected absolute price move in basis points over the next 900 s "
                    "for the chosen side; each of the ten ordered levels is labelled "
                    "with its band against this cycle's real cost (below cost / "
                    "covers cost / covers cost with slack)."
                ),
                "criteria": _expected_move_bp_criteria(fee_bp, spread_bp),
            },
            "book_toxic": {
                "type": "noul",
                "instructions": "Is the book toxic so we must not post?",
            },
        },
    }


def estimate_input_tokens(payload: Any) -> int:
    """Heuristic input size of one call: compact JSON bytes / 4.

    The instrument of measurement is P3 (card #1025); the budget it checks is
    contract: input per call ≤ ~500 tokens.
    """
    try:
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
    except Exception:  # pragma: no cover - defensive
        raw = str(payload)
    return (len(raw.encode("utf-8")) + 3) // 4


def systemone_input_tokens(payload: dict[str, Any]) -> int:
    """Input tokens of the wire body built from ``payload``."""
    return estimate_input_tokens(_systemone_payload(payload))


def _noul_yes(answer: Any) -> bool:
    """Decision boolean only: today's single cut-off (>= 0.5), unchanged."""
    return _decimal(_as_dict(answer).get("noul")) >= TOXIC_NOUL_DECISION


def noul_label(noul: Optional[Decimal]) -> str:
    """Record-only toxicity label with two cut-offs and a band (card #1028).

    Never feeds the decision: ``not_toxic`` (< 0.4), ``indeterminate``
    (0.4..0.6 inclusive), ``toxic`` (> 0.6) and ``unknown`` without a value.
    """
    if noul is None:
        return "unknown"
    if noul < TOXIC_NOUL_NOT_TOXIC_BELOW:
        return "not_toxic"
    if noul > TOXIC_NOUL_TOXIC_ABOVE:
        return "toxic"
    return "indeterminate"


def _side_confidence(side_answer: dict[str, Any]) -> tuple[Decimal, str]:
    """Confidence value the decision consumes, with the origin it came from.

    Card #1028: one reading, two returns — ``reply_field`` when the reply
    carries the field, ``choice_probability`` when it only carries the chosen
    option's probability, ``none`` when neither exists. The value returned is
    exactly the one the entry gate compares against the threshold.
    """
    if side_answer.get("confidence") is not None:
        return _decimal(side_answer.get("confidence")), "reply_field"
    choice = str(side_answer.get("choice") or "").strip()
    probs = _as_dict(side_answer.get("probabilities"))
    if choice and choice in probs:
        return _decimal(probs.get(choice)), "choice_probability"
    upper = choice.upper()
    if upper and upper in probs:
        return _decimal(probs.get(upper)), "choice_probability"
    return Decimal("0"), "none"


def _reply_model(parsed: Any) -> Optional[str]:
    """Model version that answered (card #1028); ``None`` when absent.

    The identifier is a free vendor field, so it is flattened to a single
    bounded token (whitespace collapsed, secrets redacted) before it can reach
    a record or the cycle suffix.
    """
    token = summarize_body(_as_dict(parsed).get("model"), limit=RECORD_TOKEN_CHARS)
    return token or None


def _expected_move_bp(answers: dict[str, Any]) -> Decimal:
    """Bp the cost predicates consume: the exact bp of the credited level.

    Card #1029: a ``score`` reply is read as a position on the ordered ladder
    and the **level already reached** (rounded down) credits its exact bp — the
    linear interpolation between levels is gone from the decision path. The
    legacy ``number``/``value`` fallbacks keep today's literal reading (outside
    the band contract, declared in the change).
    """
    raw = answers.get("expected_move_bp")
    if isinstance(raw, dict):
        if raw.get("score") is not None:
            return _credited_level_bp(raw["score"])
        if raw.get("number") is not None:
            return _decimal(raw.get("number"))
        if raw.get("value") is not None:
            return _decimal(raw.get("value"))
        return Decimal("0")
    if raw is None:
        return Decimal("0")
    return _decimal(raw)


def _map_systemone(
    parsed: Any,
    *,
    latency_ms: int,
    fee_bp: Optional[Decimal] = None,
    spread_bp: Optional[Decimal] = None,
) -> JevSignal:
    data = _as_dict(parsed)
    answers = _as_dict(data.get("answers"))
    if not answers:
        return _hold_signal(latency_ms, model=_reply_model(parsed))
    side_answer = _as_dict(answers.get("side"))
    confidence, confidence_origin = _side_confidence(side_answer)
    noul = _noul_value(parsed)
    expected_move_bp = _expected_move_bp(answers)
    position = _move_position(parsed)
    # Card #1029: the band of the level already reached against the cycle's real
    # cost, from the same predicates the decision uses. Without a ladder score
    # there is no position, so the band is declared unknown (the literal
    # ``number``/``value`` fallbacks stay outside the band contract).
    band = "unknown"
    if position is not None:
        band = move_band(expected_move_bp, fee_bp or Decimal("0"), spread_bp or Decimal("0"))
    return JevSignal(
        side=_parse_side(side_answer.get("choice")),
        confidence=confidence,
        expected_move_bp=expected_move_bp,
        book_toxic=_noul_yes(answers.get("book_toxic")),
        latency_ms=latency_ms,
        cost_quote=Decimal("0"),
        # Card #1028: diagnostics only; the decision reads `confidence`/`book_toxic`.
        model=_reply_model(parsed),
        confidence_origin=confidence_origin,
        noul=noul,
        noul_label=noul_label(noul),
        # Card #1029: position on the scale + band of the credited level.
        move_position=position,
        move_band=band,
    )


def _move_score(parsed: Any) -> Optional[float]:
    """Raw ``expected_move_bp`` score of the reply, for the diagnostic record."""
    answers = _as_dict(_as_dict(parsed).get("answers"))
    raw = answers.get("expected_move_bp")
    if isinstance(raw, dict) and raw.get("score") is not None:
        try:
            return float(raw["score"])
        except (TypeError, ValueError):
            return None
    return None


def _move_position(parsed: Any) -> Optional[int]:
    """Position on the scale credited to the reply (card #1029).

    ``None`` when the reply has no ladder ``score`` (legacy ``number``/``value``
    fallback or no movement answer): there is no position to credit.
    """
    score = _move_score(parsed)
    if score is None:
        return None
    return _credited_level_index(score)


def _noul_value(parsed: Any) -> Optional[Decimal]:
    """Raw ``noul`` of the reply, for the diagnostic record (card #1025, G)."""
    answers = _as_dict(_as_dict(parsed).get("answers"))
    raw = _as_dict(answers.get("book_toxic")).get("noul")
    if raw is None:
        return None
    return _decimal(raw)


def _window_features(payload: Any) -> dict[str, Any]:
    """Window features the ``book_toxic`` decision used (card #1025, G)."""
    state = _as_dict(_as_dict(payload).get("state"))
    return _as_dict(state.get("window"))


def _error_body(exc: urllib.error.HTTPError) -> str:
    """Summarized error body: read bounded, redacted and truncated."""
    try:
        raw = exc.read(ERROR_BODY_READ_BYTES)
    except TypeError:  # body object without a size argument
        try:
            raw = exc.read()
        except Exception:
            return ""
        # Keep the fallback bounded too: never feed more than the byte budget.
        if isinstance(raw, str):
            raw = raw[:ERROR_BODY_READ_BYTES]
        elif isinstance(raw, (bytes, bytearray)):
            raw = bytes(raw)[:ERROR_BODY_READ_BYTES]
    except Exception:
        return ""
    if isinstance(raw, bytes):
        return summarize_body(raw.decode("utf-8", errors="replace"))
    return summarize_body(raw)


def request_jev(payload: dict[str, Any], *, timeout_s: Optional[float] = None) -> JevSignal:
    """One HTTP call. Timeout defaults to the 3 s call timeout (card #1028).

    The late refusal stays at ``JEV_LATE_MS`` (1.5 s): a reply between 1.5 s and
    3 s now arrives, is mapped and recorded, and the cycle is still refused as
    late. The explicit ``timeout_s`` override keeps working for tools/tests.
    """
    timeout = float(timeout_s if timeout_s is not None else (JEV_CALL_TIMEOUT_MS / 1000.0))
    key = jev_api_key()
    if not key:
        # No key: no HTTP call leaves the process, so no diagnostic record —
        # the stand-in is not a Jev call.
        started = time.perf_counter()
        if _stand_in_enabled():
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return stand_in_signal(latency_ms=max(1, elapsed_ms))
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return _hold_signal(elapsed_ms)

    url = _endpoint_url()
    # Card #1029: the cost that labels the question is the same one the reply
    # is read against, so the band the model sees and the band the decision
    # derives from the credited level agree.
    fee_bp, spread_bp = _payload_cost_bp(payload)
    systemone = _systemone_payload(payload)
    call_id = uuid.uuid4().hex[:12]
    log_call_entry(call_id=call_id, systemone=systemone)
    # Card #1025: the clock opens AFTER the entry registration, so `latency_ms`
    # measures the call and the fail-closed `jev_late` no longer trips on the
    # cost of writing the #1015 entry record.
    started = time.perf_counter()
    body = json.dumps(systemone, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = int(getattr(resp, "status", 200) or 200)
            raw_bytes = resp.read()
    except urllib.error.HTTPError as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        status = int(exc.code or 0)
        logger.warning("Jev HTTP error status=%s latency_ms=%s", status, elapsed_ms)
        log_call_error(call_id=call_id, status=status, latency_ms=elapsed_ms, body=_error_body(exc))
        return _hold_signal(elapsed_ms)
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.warning("Jev request failed latency_ms=%s err=%s", elapsed_ms, _redact(str(exc)))
        log_call_error(
            call_id=call_id, status="transport_error", latency_ms=elapsed_ms, body=str(exc)
        )
        return _hold_signal(
            max(elapsed_ms, JEV_LATE_MS + 1 if elapsed_ms >= JEV_LATE_MS else elapsed_ms)
        )

    # The request already left the process and a status came back: a body that
    # fails to decode/parse is a bad reply, not a transport error, so the real
    # HTTP status is kept in the record.
    try:
        raw = raw_bytes.decode("utf-8")
        parsed = json.loads(raw) if raw else {}
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.warning(
            "Jev bad reply status=%s latency_ms=%s err=%s", status, elapsed_ms, _redact(str(exc))
        )
        log_call_error(
            call_id=call_id,
            status=status,
            latency_ms=elapsed_ms,
            body=f"bad_reply {type(exc).__name__}: {exc}",
        )
        return _hold_signal(
            max(elapsed_ms, JEV_LATE_MS + 1 if elapsed_ms >= JEV_LATE_MS else elapsed_ms)
        )

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    try:
        signal = _map_systemone(parsed, latency_ms=elapsed_ms, fee_bp=fee_bp, spread_bp=spread_bp)
    except Exception:
        signal = _hold_signal(elapsed_ms)
    if raw_payload_enabled():
        # Opt-in (card #1025): where the confidence comes from, raw reply only.
        log_call_raw(call_id=call_id, raw=parsed)
    log_call_return(
        call_id=call_id,
        status=status,
        latency_ms=signal.latency_ms,
        side=signal.side,
        expected_move_bp=signal.expected_move_bp,
        score=_move_score(parsed),
        book_toxic=signal.book_toxic,
        confidence=signal.confidence,
        # Card #1025 (G): noul + the window features the flag was derived from.
        noul=_noul_value(parsed),
        window=_window_features(payload),
        # Card #1028: version that answered, confidence origin and the
        # record-only toxicity label; not gated by SCALP_JEV_RAW_PAYLOAD.
        model=signal.model,
        confidence_origin=signal.confidence_origin,
        noul_label=signal.noul_label,
        # Card #1029: band of the credited level + position on the scale (the
        # exact bp travels in expected_move_bp=). The A/B arm is derived from
        # the effective state window (never ``larger`` with the 900 s window)
        # and the effective window travels in the same record so the invariant
        # is verifiable in the log.
        move_band=signal.move_band,
        move_position=signal.move_position,
        ab_arm=ab_arm(),
        state_window_s=state_window_s(),
    )
    return signal
