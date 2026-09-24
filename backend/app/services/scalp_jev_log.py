"""Diagnostic log for the directional scalp Jev calls (card #1015).

One dedicated file, a fixed ceiling of 200 MB and tail truncation: when the
file fills, the oldest records are dropped inside the same file, always on a
line boundary, so everything left in the file stays readable. No
``RotatingFileHandler``, no ``backupCount``, no ``.1``/``.2`` backups and no
time based rotation.

The tail truncation shifts bytes with ``os.pread``/``os.pwrite`` and
``os.ftruncate``, so this handler is POSIX/Linux-only: it is installed on the
Linux DEV runtime-worker, and ``start.ps1`` (Windows dev) is not a supported
runtime for it — there every ``emit`` falls into ``handleError``.

The record never carries the TypeSafe key, any other secret or the exact
account values: the account is summarized to ``has_position``/``has_balance``
and error bodies are redacted and truncated.

DEV-only in this delivery: the file handler is installed only when the scalp
loop runs in the DEV runtime-worker (``RUN_SCALP_LOOP=1``). The PROD unit does
not set that flag — nor ``SCALP_JEV_LOG_ENABLED`` — so production keeps no
handler and no records.
"""

from __future__ import annotations

import json
import logging
import os
import re
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Optional

from app.services.runtime_status import env_flag_enabled

DIAG_LOGGER_NAME = "app.services.scalp_jev_diag"
DEFAULT_LOG_FILE_NAME = "scalp_jev_diagnostic.log"
DEFAULT_LOG_LEVEL = "INFO"

# Single file ceiling fixed by the owner: 200 MB = 209_715_200 bytes.
MAX_LOG_BYTES = 200 * 1024 * 1024

# Summarized (truncated) error body kept in the error record.
ERROR_BODY_CHARS = 300
ERROR_BODY_READ_BYTES = 4096

# Card #1028: bounded single-token rendering for a free reply field written as
# ``k=v`` (the model version that answered). Short: the value is a version id.
RECORD_TOKEN_CHARS = 64

# When the ceiling is hit the file is trimmed back to this share of the
# ceiling, so trimming stays rare at ~1 record/s. A record is never split;
# with bounded records (~1-2 KB) the 200 MB ceiling always holds.
TRIM_KEEP_RATIO = 0.9
_SHIFT_CHUNK_BYTES = 1 << 20
_NEWLINE_SCAN_BYTES = 4096

REDACTED = "<redacted>"

# Every env whose value must never reach a record. ``_redact`` replaces each
# configured value; headers (``Authorization``) are never logged at all.
SENSITIVE_ENV_NAMES = (
    "JEV_API_KEY",
    "TYPESAFE_API_KEY",
    "JEV_TOKEN",
    "TYPESAFE_TOKEN",
    "BINANCE_API_KEY",
    "BINANCE_API_SECRET",
    "BINANCE_SPOT_API_KEY",
    "BINANCE_SPOT_API_SECRET",
    "SPOT_API_KEY",
    "SPOT_API_SECRET",
)

_BEARER_RE = re.compile(r"(?i)\bbearer\s+[^\s,;\"']+")

logger = logging.getLogger(DIAG_LOGGER_NAME)
logger.propagate = False
if not any(isinstance(handler, logging.NullHandler) for handler in logger.handlers):
    # Keeps the diagnostic records off every other handler (and off the
    # ``lastResort`` stderr writer) while the file handler is not installed.
    logger.addHandler(logging.NullHandler())


def log_file_path() -> Path:
    raw = (os.getenv("SCALP_JEV_LOG_FILE") or "").strip()
    if raw:
        return Path(raw)
    return Path(__file__).resolve().parents[2] / DEFAULT_LOG_FILE_NAME


def log_level() -> int:
    raw = (os.getenv("SCALP_JEV_LOG_LEVEL") or DEFAULT_LOG_LEVEL).strip().upper()
    level = logging.getLevelName(raw or DEFAULT_LOG_LEVEL)
    return level if isinstance(level, int) else logging.INFO


def diagnostic_enabled() -> bool:
    """DEV-only gate: the DEV runtime-worker runs the loop with RUN_SCALP_LOOP=1."""
    raw = (os.getenv("SCALP_JEV_LOG_ENABLED") or "").strip()
    if raw:
        return env_flag_enabled("SCALP_JEV_LOG_ENABLED")
    return env_flag_enabled("RUN_SCALP_LOOP")


def raw_payload_enabled() -> bool:
    """Opt-in (card #1025): record the raw reply fields that carry confidence.

    Disabled by default, so with the flag off the #1015 record set stays
    exactly as it is.
    """
    return env_flag_enabled("SCALP_JEV_RAW_PAYLOAD")


def redact(message: Any) -> str:
    """Replace every configured secret and any bearer token by ``<redacted>``."""
    text = str(message or "")
    for name in SENSITIVE_ENV_NAMES:
        value = (os.getenv(name) or "").strip()
        if value:
            text = text.replace(value, REDACTED)
    return _BEARER_RE.sub(REDACTED, text)


def summarize_body(body: Any, *, limit: int = ERROR_BODY_CHARS) -> str:
    """Single-line, redacted, truncated view of an error body."""
    flat = " ".join(redact(body).split())
    if len(flat) > limit:
        return flat[:limit] + "…"
    return flat


def record_token(value: Any, *, default: str = "unknown") -> str:
    """Single-line, redacted, bounded token for a free ``k=v`` record field.

    Card #1028: the reply ``model`` is the only free vendor field that reached
    a record without a summarizer. Flattening it here keeps one record per line
    and the ``\\S+`` shape the suffix declares, so a reply can inject neither a
    newline (a false line to the read-only ruler) nor a configured secret.
    """
    return summarize_body(value, limit=RECORD_TOKEN_CHARS) or str(default)


def position_token(value: Any) -> str:
    """Record token of the scale position; ``unknown`` when there is none.

    Card #1029: ``record_token`` maps a falsy value to its default, which would
    turn the valid level **0** into ``unknown``. The position is an internal
    integer (never a free vendor field), so it is rendered directly.
    """
    if value is None:
        return "unknown"
    return str(value)


class TailTruncatingFileHandler(logging.FileHandler):
    """Append-only handler that drops the oldest records once the ceiling is hit.

    Trimming cuts on a line boundary (the partial leading line is discarded)
    and never splits the record that was just written, so every record kept in
    the file is a complete, readable line.
    """

    def __init__(
        self,
        filename: str | os.PathLike[str],
        *,
        max_bytes: int = MAX_LOG_BYTES,
        encoding: str = "utf-8",
        delay: bool = False,
    ) -> None:
        if int(max_bytes) <= 0:
            raise ValueError("max_bytes must be positive")
        self.max_bytes = int(max_bytes)
        self.trim_keep_bytes = max(1, int(self.max_bytes * TRIM_KEEP_RATIO))
        super().__init__(filename, mode="a", encoding=encoding, delay=delay)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            self._write_and_trim(message)
        except Exception:
            self.handleError(record)

    def _write_and_trim(self, message: str) -> None:
        self.acquire()
        try:
            if self.stream is None:
                self.stream = self._open()
            start = self._size()
            self.stream.write(message + self.terminator)
            self.flush()
            self.trim(record_start=start)
        finally:
            self.release()

    def _size(self) -> int:
        try:
            return int(os.fstat(self.stream.fileno()).st_size)
        except (AttributeError, OSError, ValueError):  # pragma: no cover - defensive
            return int(self.stream.tell())

    def trim(self, *, record_start: Optional[int] = None) -> None:
        """Drop the oldest bytes until the file fits the ceiling again."""
        size = self._size()
        if size <= self.max_bytes:
            return
        floor = max(1, size - self.trim_keep_bytes)
        fd = os.open(self.baseFilename, os.O_RDWR)
        try:
            cut = self._line_boundary_after(fd, floor, size)
            if record_start is not None and cut > record_start:
                # A single record bigger than the ceiling is kept whole rather
                # than split: the newest records are the ones worth keeping.
                cut = record_start
            if cut <= 0:
                return
            remaining = size - cut
            written = 0
            while written < remaining:
                chunk = os.pread(fd, min(_SHIFT_CHUNK_BYTES, remaining - written), cut + written)
                if not chunk:
                    break
                moved = 0
                while moved < len(chunk):
                    # ``pwrite`` may write fewer bytes than asked: add up the
                    # return and retry the rest instead of dropping them.
                    step = os.pwrite(fd, chunk[moved:], written + moved)
                    if step <= 0:  # pragma: no cover - defensive, regular files always progress
                        raise OSError("os.pwrite made no progress while trimming the log")
                    moved += step
                written += moved
            os.ftruncate(fd, written)
        finally:
            os.close(fd)

    @staticmethod
    def _line_boundary_after(fd: int, start: int, size: int) -> int:
        """First offset after ``start`` that begins a line (past a newline)."""
        offset = max(0, start)
        while offset < size:
            chunk = os.pread(fd, _NEWLINE_SCAN_BYTES, offset)
            if not chunk:
                return size
            index = chunk.find(b"\n")
            if index != -1:
                return offset + index + 1
            offset += len(chunk)
        return size


def installed_handler() -> Optional[TailTruncatingFileHandler]:
    for handler in logger.handlers:
        if isinstance(handler, TailTruncatingFileHandler):
            return handler
    return None


def install_diagnostic_log(
    *, path: Optional[str | os.PathLike[str]] = None, max_bytes: int = MAX_LOG_BYTES
) -> Optional[TailTruncatingFileHandler]:
    """Install the DEV diagnostic file handler once. ``None`` when disabled."""
    if not diagnostic_enabled():
        return None
    existing = installed_handler()
    if existing is not None:
        return existing
    target = Path(path) if path is not None else log_file_path()
    handler = TailTruncatingFileHandler(target, max_bytes=max_bytes)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.setLevel(log_level())
    logger.addHandler(handler)
    logger.info(
        "scalp jev diagnostic log enabled file=%s level=%s ceiling_bytes=%s",
        target,
        logging.getLevelName(logger.level),
        handler.max_bytes,
    )
    return handler


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _is_positive(value: Any) -> bool:
    try:
        return Decimal(str(value)) > Decimal("0")
    except Exception:
        return False


def summarize_account(account: Any) -> dict[str, bool]:
    """Booleans only: «is there a position?» / «is there balance?»."""
    data = _as_dict(account)
    return {
        "has_position": _is_positive(data.get("inventory_btc")),
        "has_balance": _is_positive(data.get("t")),
    }


def summarize_state(systemone: Any) -> dict[str, Any]:
    """The wire ``state`` with the exact account replaced by its summary."""
    payload = _as_dict(systemone)
    state = dict(_as_dict(payload.get("state")))
    state["account"] = summarize_account(state.get("account"))
    return state


def summarize_questions(systemone: Any) -> dict[str, str]:
    """Question names with their answer type (the criteria are static constants)."""
    questions = _as_dict(_as_dict(systemone).get("questions"))
    return {str(name): str(_as_dict(spec).get("type") or "") for name, spec in questions.items()}


def _compact(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)
    except Exception:  # pragma: no cover - defensive
        return str(value)


def log_call_entry(*, call_id: str, systemone: Any) -> None:
    """Entry record.

    Card #1028: the entry is written before the reply, so it carries the fixed
    version **requested** (``model_requested=``), not the one that answered.
    """
    logger.info(
        "scalp jev call entry id=%s state=%s questions=%s model_requested=%s",
        call_id,
        _compact(summarize_state(systemone)),
        _compact(summarize_questions(systemone)),
        _as_dict(systemone).get("model"),
    )


def log_call_return(
    *,
    call_id: str,
    status: Any,
    latency_ms: Any,
    side: Any,
    expected_move_bp: Any,
    score: Any = None,
    book_toxic: Any = None,
    confidence: Any = None,
    noul: Any = None,
    window: Any = None,
    model: Any = None,
    confidence_origin: Any = None,
    noul_label: Any = None,
    move_band: Any = None,
    move_position: Any = None,
    ab_arm: Any = None,
) -> None:
    """Return record: the reply plus the drivers of the ``book_toxic`` flag.

    Card #1025 (G): the ``noul`` returned by the model and the window features
    the decision used (``ret_bp``, ``vol_bp``, ``aggressor_flow``,
    ``spread_bp_mean``, ``trade_count``) go into the same #1015 record, so the
    model's own opinion can be told apart from a wrong mapping. Log only.

    Card #1028: the same record carries the version that **answered**
    (``model=``, ``unknown`` when the reply has no identifier), the origin of
    the confidence used (``confidence_origin=``) and the record-only toxicity
    label (``noul_label=``), independent of ``SCALP_JEV_RAW_PAYLOAD``.

    Card #1029: the reply is a **position on the scale** — the record shows the
    band of the level already reached (``move_band=``) and that position
    (``move_position=``), and ``expected_move_bp=`` is the exact bp of that
    level (never interpolated). ``ab_arm=`` declares the A/B arm of the run.
    All fields are additive: the read-only ruler keeps matching the prefix.
    """
    features = _as_dict(window)
    logger.info(
        "scalp jev call return id=%s status=%s latency_ms=%s side=%s "
        "expected_move_bp=%s score=%s move_band=%s move_position=%s ab_arm=%s "
        "book_toxic=%s confidence=%s "
        "noul=%s model=%s confidence_origin=%s noul_label=%s "
        "window_ret_bp=%s window_vol_bp=%s window_aggressor_flow=%s "
        "window_spread_bp_mean=%s window_trade_count=%s",
        call_id,
        status,
        latency_ms,
        side,
        expected_move_bp,
        score,
        record_token(move_band),
        position_token(move_position),
        record_token(ab_arm),
        book_toxic,
        confidence,
        noul,
        record_token(model),
        confidence_origin,
        noul_label,
        features.get("ret_bp"),
        features.get("vol_bp"),
        features.get("aggressor_flow"),
        features.get("spread_bp_mean"),
        features.get("trade_count"),
    )


def log_call_error(*, call_id: str, status: Any, latency_ms: Any, body: Any) -> None:
    logger.warning(
        "scalp jev call error id=%s status=%s latency_ms=%s body=%s",
        call_id,
        status,
        latency_ms,
        summarize_body(body),
    )


def _cycle_suffix(
    *,
    gate_verdicts: Optional[Mapping[str, str]] = None,
    model: Any = None,
    confidence: Any = None,
    confidence_origin: Any = None,
    noul: Any = None,
    noul_label: Any = None,
    book_toxic: Any = None,
    move_band: Any = None,
    move_position: Any = None,
    ab_arm: Any = None,
) -> str:
    """Additive ``k=v`` fields of a cycle record; empty when there is no reply.

    The fields come **after** ``user=``/``skip_reason=`` so the #1025 read-only
    ruler (``RefusalRe`` / ``KVRe``) keeps matching the prefix and tolerates
    the extra keys. Values are single tokens (``\\S+``).

    Card #1029: the cycle record also carries the band of the level already
    reached (``move_band=``), the position on the scale (``move_position=``)
    and the A/B arm of the run (``ab_arm=``) — additive, same record.
    """
    parts: list[str] = []
    if gate_verdicts:
        parts.extend(f"{name}={verdict}" for name, verdict in gate_verdicts.items())
    if model is not None:
        parts.append(f"model={record_token(model)}")
    if confidence is not None:
        parts.append(f"confidence={confidence}")
    if confidence_origin is not None:
        parts.append(f"confidence_origin={confidence_origin}")
    if noul_label is not None:
        parts.append(f"noul={'unknown' if noul is None else noul}")
        parts.append(f"noul_label={noul_label}")
    if book_toxic is not None:
        parts.append(f"book_toxic={book_toxic}")
    if move_band is not None:
        parts.append(f"move_band={record_token(move_band)}")
    if move_position is not None:
        parts.append(f"move_position={position_token(move_position)}")
    if ab_arm is not None:
        parts.append(f"ab_arm={record_token(ab_arm)}")
    return (" " + " ".join(parts)) if parts else ""


def log_cycle_refusal(
    *,
    user_id: Any,
    skip_reason: Any,
    gate_verdicts: Optional[Mapping[str, str]] = None,
    model: Any = None,
    confidence: Any = None,
    confidence_origin: Any = None,
    noul: Any = None,
    noul_label: Any = None,
    book_toxic: Any = None,
    move_band: Any = None,
    move_position: Any = None,
    ab_arm: Any = None,
) -> None:
    """A cycle closed without an order.

    ``skip_reason`` is the raw token of the **first** gate that closed the
    cycle and stays immediately after ``user=`` (card #1015 contract). Card
    #1028 appends, in the same record, the verdict of every reply-fed gate plus
    the reply diagnostics when the cycle had a model reply. Card #1029 appends
    the band, the position and the A/B arm (additive).
    """
    token = str(skip_reason or "").strip()
    if not token:
        return
    logger.info(
        "scalp cycle refused user=%s skip_reason=%s%s",
        user_id,
        token,
        _cycle_suffix(
            gate_verdicts=gate_verdicts,
            model=model,
            confidence=confidence,
            confidence_origin=confidence_origin,
            noul=noul,
            noul_label=noul_label,
            book_toxic=book_toxic,
            move_band=move_band,
            move_position=move_position,
            ab_arm=ab_arm,
        ),
    )


def log_cycle_sent(
    *,
    user_id: Any,
    gate_verdicts: Optional[Mapping[str, str]] = None,
    model: Any = None,
    confidence: Any = None,
    confidence_origin: Any = None,
    noul: Any = None,
    noul_label: Any = None,
    book_toxic: Any = None,
    move_band: Any = None,
    move_position: Any = None,
    ab_arm: Any = None,
) -> None:
    """A cycle that passed every entry gate and sent an order (card #1028).

    Same record shape as the refusal, with ``skip_reason=none`` and the same
    additive fields (card #1029 adds band, position and A/B arm); the #1025
    ruler ignores this prefix, so it is additive.
    """
    logger.info(
        "scalp cycle sent user=%s skip_reason=none%s",
        user_id,
        _cycle_suffix(
            gate_verdicts=gate_verdicts,
            model=model,
            confidence=confidence,
            confidence_origin=confidence_origin,
            noul=noul,
            noul_label=noul_label,
            book_toxic=book_toxic,
            move_band=move_band,
            move_position=move_position,
            ab_arm=ab_arm,
        ),
    )


def log_aggressive_exit(
    *,
    user_id: Any,
    side: Any,
    quantity: Any,
    order_type: Any = "MARKET",
    reason: Any = "hold_window_end",
    status: Any = None,
    executed_qty: Any = None,
    avg_price: Any = None,
    client_order_id: Any = None,
    order_id: Any = None,
) -> None:
    """Visible WARNING for the aggressive exit (card #1025).

    Its own reason token (``hold_window_end``), never the ``stuck`` token, and
    it carries the exit data: side, order type, quantity, status, executed
    quantity, the price the escape actually got and the order identifiers.
    Log only — the Monitor panel and the scalp status gain nothing.
    """
    logger.warning(
        "scalp aggressive exit user=%s reason=%s side=%s order_type=%s price_cap=none "
        "quantity=%s status=%s executed_qty=%s avg_price=%s client_order_id=%s order_id=%s",
        user_id,
        reason,
        side,
        order_type,
        quantity,
        status,
        executed_qty,
        avg_price,
        client_order_id,
        order_id,
    )


_RAW_PROBABILITY_LIMIT = 8


def _raw_value(value: Any) -> str:
    """Compact, redacted, truncated rendering of one raw reply field."""
    return summarize_body(_compact(value), limit=200)


def log_call_raw(*, call_id: str, raw: Any) -> None:
    """Opt-in raw reply fields (card #1025): where ``confidence`` comes from.

    Whitelisted fields only — the model's own answer values
    (``side_answer.confidence`` and ``probabilities[choice]``, the raw
    ``expected_move_bp`` score and the ``noul``) — so no secret, no
    ``Authorization`` header and no exact account value can reach the record.
    """
    replies = _as_dict(raw)
    answers = _as_dict(replies.get("answers"))
    side_answer = _as_dict(answers.get("side"))
    choice = str(side_answer.get("choice") or "")
    probabilities = _as_dict(side_answer.get("probabilities"))
    probabilities = {
        str(name): probabilities[name] for name in list(probabilities)[:_RAW_PROBABILITY_LIMIT]
    }
    choice_probability = probabilities.get(choice)
    if choice_probability is None and choice:
        upper = choice.upper()
        choice_probability = probabilities.get(upper)
    move_answer = _as_dict(answers.get("expected_move_bp"))
    noul = _as_dict(answers.get("book_toxic")).get("noul")
    logger.info(
        "scalp jev call raw id=%s model=%s choice=%s side_confidence=%s "
        "probabilities=%s choice_probability=%s expected_move_score=%s noul=%s",
        call_id,
        _raw_value(replies.get("model")),
        _raw_value(choice),
        _raw_value(side_answer.get("confidence")),
        _raw_value(probabilities),
        _raw_value(choice_probability),
        _raw_value(move_answer.get("score")),
        _raw_value(noul),
    )
