"""Private execution snapshots and a shared retained-byte/entry LRU budget."""
from __future__ import annotations

from collections import OrderedDict
import hashlib
import sys
import uuid
from functools import wraps
import numpy as np
import pandas as pd


def index_identity(index):
    data = index._data
    key = (id(data), repr(index.dtype), repr(index.names))
    known = BUDGET.get("indices", key)
    if known is not None and known[0] is data:
        return known[1]
    return _hash_index(index)


def _hash_index(index):
    h = hashlib.sha256()
    h.update(repr(index.dtype).encode())
    h.update(repr(index.names).encode())
    h.update(pd.util.hash_pandas_object(index, index=True).to_numpy().tobytes())
    return h.hexdigest()


def frame_identity(frame):
    h = hashlib.sha256()
    h.update(index_identity(frame.index).encode())
    h.update(repr([(c, repr(d)) for c, d in zip(frame.columns, frame.dtypes)]).encode())
    h.update(pd.util.hash_pandas_object(frame, index=False).to_numpy().tobytes())
    return h.hexdigest()


def protect(frame, *, register_index=True):
    for block in frame._mgr.blocks:
        values = block.values
        if isinstance(values, np.ndarray):
            values.flags.writeable = False
        elif hasattr(values, "_ndarray"):
            values._ndarray.flags.writeable = False
    data = frame.index._data
    if hasattr(data, "_ndarray"):
        data._ndarray.flags.writeable = False
    elif isinstance(data, np.ndarray):
        data.flags.writeable = False
    if register_index:
        # pandas shallow copies create another Index around the same frozen
        # backing data. Retain that private data strongly and include wrapper
        # metadata; external mutable indices never receive this memo token.
        key = (id(data), repr(frame.index.dtype), repr(frame.index.names))
        BUDGET.put("indices", key, (data, _hash_index(frame.index)))
    return frame


class Snapshot:
    """Created only at internal execution boundaries, never from DataFrame attrs."""
    def __init__(self, frame, *, generation=None, source=(), role="train", limits=()):
        owned = frame.copy(deep=True)
        owned.index = frame.index.copy(deep=True)
        self._frame = protect(owned)
        self.identity = (generation or uuid.uuid4().hex, tuple(source), role,
                         tuple(limits), frame_identity(self._frame))

    def __getstate__(self):
        return self._frame, self.identity

    def __setstate__(self, state):
        self._frame, self.identity = state
        # Restore immutability immediately; memoize only when resolve() uses
        # this snapshot, rather than retaining redundant deserialized indices.
        protect(self._frame, register_index=False)

    def copy_frame(self):
        return self._frame.copy(deep=True)


def retained_bytes(value, seen=None):
    seen = set() if seen is None else seen
    if id(value) in seen:
        return 0
    seen.add(id(value))
    if isinstance(value, Snapshot):
        return retained_bytes(value._frame, seen) + retained_bytes(value.identity, seen)
    if isinstance(value, pd.DataFrame):
        # Walk owned buffers directly: DataFrame.memory_usage constructs a
        # Series for every column on every cache insertion, which dominates
        # shorter searches. Include metadata and complete backing allocations.
        return (object.__sizeof__(value) + sys.getsizeof(value.__dict__)
                + sys.getsizeof(value._mgr) + sys.getsizeof(value._flags)
                + retained_bytes(value.attrs, seen)
                + retained_bytes(value.index, seen) + retained_bytes(value.columns, seen)
                + sum(sys.getsizeof(block) + retained_bytes(block.values, seen)
                      for block in value._mgr.blocks))
    if isinstance(value, pd.Index):
        return object.__sizeof__(value) + int(value.memory_usage(deep=True))
    if isinstance(value, np.ndarray):
        if value.base is not None:
            return sys.getsizeof(value) + retained_bytes(value.base, seen)
        return sys.getsizeof(value) + (sum(retained_bytes(x, seen) for x in value.flat)
                                      if value.dtype.hasobject else 0)
    if isinstance(value, pd.api.extensions.ExtensionArray):
        if hasattr(value, "_ndarray"):
            return object.__sizeof__(value) + retained_bytes(value._ndarray, seen)
        if hasattr(value, "_pa_array"):
            return object.__sizeof__(value) + int(value._pa_array.get_total_buffer_size())
        return object.__sizeof__(value) + int(value.nbytes)
    if isinstance(value, dict):
        return sys.getsizeof(value) + sum(retained_bytes(k, seen) + retained_bytes(v, seen)
                                        for k, v in value.items())
    if isinstance(value, (tuple, list)):
        return sys.getsizeof(value) + sum(retained_bytes(x, seen) for x in value)
    return sys.getsizeof(value)


class Budget:
    def __init__(self, max_bytes=64 * 1024 * 1024, max_entries=4096, max_snapshots=32):
        self.max_bytes, self.max_entries, self.max_snapshots = max_bytes, max_entries, max_snapshots
        self.entries = OrderedDict()
        self.bytes = 0
        self.generation = None
        self.evictions = 0
        self.snapshots = 0

    def clear(self):
        self.entries.clear()
        self.bytes = 0
        self.snapshots = 0

    def begin(self, generation):
        if generation != self.generation:
            self.clear()
            self.generation = generation

    def get(self, namespace, key):
        full = (namespace, key)
        item = self.entries.get(full)
        if item is None:
            return None
        self.entries.move_to_end(full)
        return item[0]

    def put(self, namespace, key, value):
        full = (namespace, key)
        size = retained_bytes((full, value))
        if full in self.entries:
            self.bytes -= self.entries.pop(full)[1]
            self.snapshots -= namespace == "snapshots"
        if size > self.max_bytes:
            return
        self.entries[full] = (value, size)
        self.bytes += size
        self.snapshots += namespace == "snapshots"
        while (self.bytes > self.max_bytes or len(self.entries) > self.max_entries
               or self.snapshots > self.max_snapshots):
            old_key, (_, old_size) = self.entries.popitem(last=False)
            self.bytes -= old_size
            self.snapshots -= old_key[0] == "snapshots"
            self.evictions += 1


BUDGET = Budget()


class Cache:
    def __init__(self, namespace):
        self.namespace = namespace

    def get(self, key, default=None):
        value = BUDGET.get(self.namespace, key)
        return default if value is None else value

    def __setitem__(self, key, value):
        BUDGET.put(self.namespace, key, value)

    def __getitem__(self, key):
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def clear(self):
        for key in list(BUDGET.entries):
            if key[0] == self.namespace:
                BUDGET.bytes -= BUDGET.entries.pop(key)[1]
                BUDGET.snapshots -= key[0] == "snapshots"


def resolve(snapshot):
    BUDGET.begin(snapshot.identity[0])
    known = BUDGET.get("snapshots", snapshot.identity)
    if known is None:
        protect(snapshot._frame)
        BUDGET.put("snapshots", snapshot.identity, snapshot)
        known = snapshot
    return known._frame


def execution_lifecycle(function):
    @wraps(function)
    def run(*args, **kwargs):
        from app.services.combo_acceleration import enabled
        active = enabled()
        try:
            return function(*args, **kwargs)
        finally:
            if active:
                BUDGET.clear()
    return run
