"""Composition with the frozen #1091 Cache/BUDGET API, in a fresh subprocess."""

import os
from pathlib import Path
import subprocess
import sys


def test_cache_1091_is_reused_without_independent_budgets():
    fixture = Path(__file__).parents[1] / "fixtures/discovery_memory/cache_1091_reference.py"
    source = """
import importlib.util, sys
spec=importlib.util.spec_from_file_location("app.services.combo_cache", sys.argv[1])
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
from app.services import discovery_budget_cache as bridge
from app.services import combo_optimizer as opt
assert bridge.BUDGET is module.BUDGET
assert opt.BUDGET is module.BUDGET
assert opt._WORKER_INDICATOR_CACHE.namespace == "indicators"
import numpy as np, pandas as pd
frame=pd.DataFrame({"open":[1.,2.],"high":[2.,3.],"low":[0.,1.],"close":[1.,2.],"volume":[1.,1.]},index=pd.date_range("2026-01-01",periods=2,tz="UTC"))
snapshot=module.Snapshot(frame)
resolved=module.resolve(snapshot)
np.testing.assert_array_equal(resolved.to_numpy(), frame.to_numpy())
module.BUDGET.clear()
for namespace in ("snapshots","indicators","intraday","coverage","indices"):
    cache=bridge.Cache(namespace)
    for i in range(1000): cache[i]=np.arange(8)
assert module.BUDGET.bytes <= 64*1024**2
assert len(module.BUDGET.entries) <= 4096
assert module.BUDGET.snapshots <= 32
@bridge.bounded_execution
def execute():
    opt._WORKER_COVERAGE_CACHE["key"]=(True,True)
    return 7
assert execute()==7
assert module.BUDGET.bytes == 0
"""
    result = subprocess.run(
        [sys.executable, "-c", source, str(fixture)],
        env=os.environ.copy(),
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
