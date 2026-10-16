"""Bridge exposing #1091's shared Cache/BUDGET (app.services.combo_cache) to discovery code.

Also provides `retained` (conservative strong-reference size) and `bounded_execution`
(clears the shared BUDGET around an execution).
"""

from functools import wraps
import sys

from app.services.combo_cache import Cache, BUDGET  # noqa: F401  (re-exported)


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


def bounded_execution(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        BUDGET.clear()
        try:
            return function(*args, **kwargs)
        finally:
            BUDGET.clear()

    return wrapped
