"""Bridge to #1091's shared Cache/BUDGET; bounded legacy fallback until integration."""

from collections import OrderedDict
from functools import wraps
import sys


def retained(value, seen=None):
    """Conservative strong-reference size, including backing arrays and indices."""
    seen = set() if seen is None else seen
    if id(value) in seen:
        return 0
    seen.add(id(value))
    total = sys.getsizeof(value)
    if hasattr(value, "memory_usage"):
        size = value.memory_usage(deep=True)
        return total + int(size.sum() if hasattr(size, "sum") else size)
    if hasattr(value, "nbytes"):
        return total + value.nbytes + (retained(value.base, seen) if value.base is not None else 0)
    if isinstance(value, dict):
        total += sum(retained(k, seen) + retained(v, seen) for k, v in value.items())
    elif isinstance(value, (list, tuple)):
        total += sum(retained(v, seen) for v in value)
    return total


try:
    from app.services.combo_cache import Cache, BUDGET
except ImportError:

    class Budget:
        max_bytes = 64 * 1024 * 1024
        max_entries = 4096
        max_snapshots = 32

        def __init__(self):
            self.entries = OrderedDict()
            self.bytes = 0
            self.evictions = 0

        def clear(self):
            self.entries.clear()
            self.bytes = 0

        def get(self, namespace, key):
            full = (namespace, key)
            item = self.entries.get(full)
            if item is None:
                return None
            self.entries.move_to_end(full)
            return item[0]

        def put(self, namespace, key, value):
            full = (namespace, key)
            size = retained((full, value))
            old = self.entries.pop(full, None)
            if old:
                self.bytes -= old[1]
            if size > self.max_bytes:
                return
            self.entries[full] = (value, size)
            self.bytes += size
            while (
                self.bytes > self.max_bytes
                or len(self.entries) > self.max_entries
                or sum(k[0] == "snapshots" for k in self.entries) > self.max_snapshots
            ):
                _, (_, amount) = self.entries.popitem(last=False)
                self.bytes -= amount
                self.evictions += 1

    BUDGET = Budget()

    class Cache:
        def __init__(self, namespace):
            self.namespace = namespace

        def get(self, key, default=None):
            result = BUDGET.get(self.namespace, key)
            return default if result is None else result

        def __getitem__(self, key):
            result = self.get(key)
            if result is None:
                raise KeyError(key)
            return result

        def __setitem__(self, key, value):
            BUDGET.put(self.namespace, key, value)

        def clear(self):
            for key in list(BUDGET.entries):
                if key[0] == self.namespace:
                    BUDGET.bytes -= BUDGET.entries.pop(key)[1]


def bounded_execution(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        BUDGET.clear()
        try:
            return function(*args, **kwargs)
        finally:
            BUDGET.clear()

    return wrapped
