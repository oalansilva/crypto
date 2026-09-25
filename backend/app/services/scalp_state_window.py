"""Effective state window of the scalp Jev call (card #1029, decisions 10-12).

The **state window** is the *context* sent to the model — how much trade and
spread history the window aggregates are computed over — not the prediction
horizon. Card #1029 reads it as one product configuration: the same value
extends the retention of the shared stream buffer **and** the horizon of the
window aggregates declared in the payload, and the A/B arm is derived from it.

Before this card the window was suspended at 900 s (``HORIZON_S``) while an
independent env (``SCALP_JEV_AB_ARM``) only changed the record label, so both
arms sent the same payload. Now:

* ``state_window_s()`` is the **single source** of the effective window;
* an invalid value (non-numeric or ``<= 900``) falls back to the current window
  (900 s), so the arm stays ``current``;
* ``ab_arm()`` is a pure function of the effective window: ``larger`` if and
  only if the effective window is greater than 900 s, so a record can never
  carry ``larger`` with the 900 s window.

DEV-only context: no entry decision, gate, threshold, target/stop geometry or
cadence reads this value (decision 12).
"""

from __future__ import annotations

import math
import os
from typing import Optional

# The current window: the 900 s that used to be hard-coded in ``HORIZON_S``.
CURRENT_STATE_WINDOW_S = 900
# Reference of the larger window. The exact value is a P3 detail; any value
# strictly greater than ``CURRENT_STATE_WINDOW_S`` selects the larger arm.
LARGER_STATE_WINDOW_S = 3600

# Product configuration of the effective state window (final name is P3).
STATE_WINDOW_ENV = "SCALP_JEV_STATE_WINDOW_S"

# A/B arms recorded with the diagnostic report.
ARM_CURRENT = "current"
ARM_LARGER = "larger"


def state_window_s() -> int:
    """Effective state window in seconds (card #1029, decision 10).

    Unset/blank, non-numeric, non-finite (``inf``/``nan``, including the
    overflow of ``1e400``) or ``<= CURRENT_STATE_WINDOW_S`` all resolve to the
    current window; only a finite value strictly greater selects the larger one.
    """
    raw = (os.getenv(STATE_WINDOW_ENV) or "").strip()
    if not raw:
        return CURRENT_STATE_WINDOW_S
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return CURRENT_STATE_WINDOW_S
    # ``inf``/``1e400`` must not raise and ``nan`` compares false against every
    # bound, so both are rejected explicitly instead of leaking a bad window.
    if not math.isfinite(value):
        return CURRENT_STATE_WINDOW_S
    if value <= CURRENT_STATE_WINDOW_S:
        return CURRENT_STATE_WINDOW_S
    return int(value)


def state_window_arm(window_s: Optional[int] = None) -> str:
    """A/B arm derived from the effective state window (decision 11).

    ``larger`` if and only if the effective window is greater than the current
    window; otherwise ``current``. Pure function of the value actually sent.
    """
    effective = state_window_s() if window_s is None else int(window_s)
    return ARM_LARGER if effective > CURRENT_STATE_WINDOW_S else ARM_CURRENT
