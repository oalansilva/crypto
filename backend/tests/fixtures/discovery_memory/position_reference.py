"""Frozen event loop at #1093 baseline99a3070; independent of runtime binding."""

import numpy as np


def signals(df, entry_mask, exit_mask, stop_loss, direction="long"):
    if not entry_mask.any():
        return df.assign(signal=0, signal_reason="")
    open_arr = np.ascontiguousarray(df["open"].to_numpy(dtype=np.float64))
    low_arr = np.ascontiguousarray(df["low"].to_numpy(dtype=np.float64))
    entry_bits = np.ascontiguousarray(entry_mask.fillna(False).to_numpy(dtype=bool))
    exit_bits = np.ascontiguousarray(exit_mask.fillna(False).to_numpy(dtype=bool))
    n = len(df)
    result = np.zeros(n, dtype=int)
    reasons = np.full(n, "", dtype=object)
    i = 1
    in_position = False
    entry_price = None
    while i < n:
        if not in_position:
            rel = np.flatnonzero(entry_bits[i:])
            if rel.size == 0:
                break
            k = i + int(rel[0])
            e = k + 1
            if e >= n:
                break
            result[e] = 1
            reasons[e] = "entry"
            in_position = True
            entry_price = float(open_arr[e])
            i = e + 1
            continue
        s = None
        if direction == "long" and entry_price is not None:
            lows = low_arr[i:]
            low_pnl = (lows - entry_price) / entry_price
            hits = np.flatnonzero(low_pnl <= -stop_loss)
            if hits.size:
                s = i + int(hits[0])
        ex = np.flatnonzero(exit_bits[i:])
        i_exit = i + int(ex[0]) if ex.size else None
        if s is not None and (i_exit is None or s <= i_exit):
            result[s] = -1
            reasons[s] = "stop_loss"
            in_position = False
            entry_price = None
            i = s + 1
            continue
        if i_exit is not None:
            x = i_exit + 1
            if x >= n:
                break
            result[x] = -1
            reasons[x] = "exit_logic"
            in_position = False
            entry_price = None
            i = x + 1
            continue
        break
    return df.assign(signal=result, signal_reason=reasons)
