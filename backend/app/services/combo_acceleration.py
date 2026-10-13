"""Internal, optional #1091 numerical kernels. Business errors stay in Python."""
from __future__ import annotations

import logging
import os
import numpy as np

logger = logging.getLogger(__name__)


def enabled():
    return not (os.getenv("COMBO_OPTIMIZER_1091_DISABLED") == "1"
                or os.getenv("COMBO_OPTIMIZER_LEGACY") == "1")


def position_kernel(opens, lows, entry, exit_bits, stop, is_long):
    n = len(opens)
    signals = np.zeros(n, np.int64)
    reasons = np.zeros(n, np.int64)
    i = 1
    while i < n:
        while i < n and not entry[i]:
            i += 1
        e = i + 1
        if e >= n:
            break
        signals[e] = 1
        reasons[e] = 1
        price = opens[e]
        i = e + 1
        while i < n:
            if is_long and np.divide(lows[i] - price, price) <= -stop:
                signals[i] = -1
                reasons[i] = 2
                i += 1
                break
            if exit_bits[i]:
                x = i + 1
                if x >= n:
                    i = n
                    break
                signals[x] = -1
                reasons[x] = 3
                i = x + 1
                break
            i += 1
    return signals, reasons


def deep_kernel(times, opens, closes, signals, intraday, lows, highs, stop, short):
    entries = np.flatnonzero(signals == 1)
    exits = np.flatnonzero(signals == -1)
    # Never store timestamps or indices in float64.
    indices = np.empty((len(entries), 3), np.int64)
    prices = np.empty(len(entries), np.float64)
    count = 0
    last = np.iinfo(np.int64).min
    for e in entries:
        t = times[e]
        if t < last:
            continue
        price = opens[e]
        sp = price * (1 + stop) if short else price * (1 - stop)
        p = np.searchsorted(times[exits], t, side="right")
        x = exits[p] if p < len(exits) else -1
        # Python's fallback boundary may exceed int64 near Timestamp.max.
        # Such a boundary includes every remaining intraday row; avoid the
        # signed overflow of the compiled arithmetic without changing it.
        beyond_int64 = x < 0 and times[-1] > np.iinfo(np.int64).max - 86400000000000
        xt = times[x] if x >= 0 else (np.iinfo(np.int64).max if beyond_int64
                                      else times[-1] + 86400000000000)
        xp = opens[x] if x >= 0 else closes[-1]
        hit = -1
        if stop > 0:
            start = np.searchsorted(intraday, t)
            end = len(intraday) if beyond_int64 else np.searchsorted(intraday, xt)
            for j in range(start, end):
                if (short and highs[j] >= sp) or (not short and lows[j] <= sp):
                    hit = j
                    xp = sp
                    xt = intraday[j]
                    break
        if x < 0 and hit < 0:
            continue
        last = xt
        indices[count, 0] = e
        indices[count, 1] = x
        indices[count, 2] = hit
        prices[count] = xp
        count += 1
    return indices[:count], prices[:count]


class OptionalKernel:
    """Compile eligible arrays only; cache failure permits in-memory JIT."""
    def __init__(self, python, dtypes):
        self.python = python
        self.dtypes = dtypes
        self.compiled = None
        self.unavailable = False
        self.warned = False

    def diagnostic(self, exc):
        if not self.warned:
            logger.warning("#1091 %s using Python fallback: %s", self.python.__name__, exc)
            self.warned = True

    def __call__(self, *args):
        if not enabled():
            return self.python(*args)
        eligible = all(isinstance(a, np.ndarray) and a.ndim == 1
                       and a.dtype == dtype and a.flags.c_contiguous
                       for a, dtype in zip(args, self.dtypes))
        if not eligible:
            self.diagnostic("ineligible numerical signature")
            return self.python(*args)
        # pandas and snapshots expose read-only arrays. Normalize view flags so
        # warmup and real execution share the same Numba signature, without
        # changing a caller's buffers or creating another numeric copy.
        inputs = []
        for array in args[:len(self.dtypes)]:
            view = array.view()
            view.flags.writeable = False
            inputs.append(view)
        args = (*inputs, *args[len(self.dtypes):])
        if not self.unavailable and self.compiled is None:
            try:
                from numba import njit
                try:
                    self.compiled = njit(cache=True, fastmath=False, nogil=True,
                                         error_model="numpy")(self.python)
                except RuntimeError:
                    self.compiled = njit(cache=False, fastmath=False, nogil=True,
                                         error_model="numpy")(self.python)
            except (ImportError, OSError, RuntimeError) as exc:
                self.unavailable = True
                self.diagnostic(exc)
        if self.compiled is not None:
            # Only compiler/cache failures trigger fallback. Runtime business
            # exceptions such as ValueError or IndexError must propagate.
            from numba.core.errors import NumbaError
            try:
                return self.compiled(*args)
            except (NumbaError, OSError) as exc:
                self.unavailable = True
                self.compiled = None
                self.diagnostic(exc)
        return self.python(*args)


positions = OptionalKernel(position_kernel, (np.dtype("float64"), np.dtype("float64"),
                                             np.dtype("bool"), np.dtype("bool")))
deep_execution = OptionalKernel(deep_kernel, (np.dtype("int64"), np.dtype("float64"),
                                             np.dtype("float64"), np.dtype("int64"),
                                             np.dtype("int64"), np.dtype("float64"),
                                             np.dtype("float64")))


def warm_kernels():
    a = np.ones(3, np.float64)
    b = np.array([False, True, False])
    t = np.arange(3, dtype=np.int64)
    positions(a, a, b, b, .05, True)
    deep_execution(t, a, a, np.array([0, 1, -1], np.int64), t, a, a, .05, False)
