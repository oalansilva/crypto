#!/usr/bin/env python3
"""Run issue #262 candidate search by reusing the card #261 evaluator against #262 T0."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-262-hard-mode-v5"
BENCHMARK_PATH = ARTIFACT_DIR / "benchmark-revalidation-latest.json"
ADAPTER_T0_PATH = ARTIFACT_DIR / "candidate-search-t0-adapter.json"
CARD_261_SCRIPT = ROOT / "scripts" / "card_261_candidate_search.py"


def _load_card_261_module():
    spec = importlib.util.spec_from_file_location("card_261_candidate_search", CARD_261_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {CARD_261_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _adapt_t0() -> None:
    source = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    rows = []
    for row in source["results"]:
        rows.append(
            {
                "favorite_id": row["favorite_id"],
                "name": row["name"],
                "strategy_name": row["strategy_name"],
                "metrics": row["metrics_summary"],
                "execution_mode": row["execution_mode"],
                "parameters": row.get("saved_parameters") or {},
            }
        )
    benchmarks = {}
    for key in ["BENCHMARK_RETURN", "BENCHMARK_DD", "BENCHMARK_SHARPE", "BENCHMARK_PF"]:
        value = source["benchmarks"][key]
        benchmarks[key] = {
            "favorite_id": value["favorite_id"],
            "strategy_name": value["strategy_name"],
            "metrics": value["metrics_summary"],
        }
    benchmarks["BENCHMARK_PARETO_SET"] = [
        {
            "favorite_id": value["favorite_id"],
            "strategy_name": value["strategy_name"],
            "metrics": value["metrics_summary"],
        }
        for value in source["benchmarks"]["BENCHMARK_PARETO_SET"]
    ]
    adapter = {
        "card": 262,
        "revalidated_favorites": rows,
        "benchmarks": benchmarks,
    }
    ADAPTER_T0_PATH.write_text(json.dumps(adapter, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    _adapt_t0()
    module = _load_card_261_module()
    module.ARTIFACT_DIR = ARTIFACT_DIR
    module.T0_PATH = ADAPTER_T0_PATH
    module.FULL_START = "2017-08-17"
    module.FULL_END = "2026-06-07"
    module.main()


if __name__ == "__main__":
    main()
