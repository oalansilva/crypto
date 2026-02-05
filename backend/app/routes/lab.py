"""Strategy Lab endpoints (CP1 - minimal scaffolding).

CP1 goals:
- Create a lab run and return run_id (accepted)
- Poll run status
- No LangGraph yet

Persistence:
- Writes a small JSON file under backend/logs/lab_runs/<run_id>.json

Security:
- Single-tenant MVP; no auth.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/lab", tags=["lab"])


def _runs_dir() -> Path:
    # backend/app/routes/lab.py -> backend/app/routes -> backend/app -> backend
    base = Path(__file__).resolve().parents[2]
    d = base / "logs" / "lab_runs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _run_path(run_id: str) -> Path:
    return _runs_dir() / f"{run_id}.json"


def _trace_path(run_id: str) -> Path:
    return _runs_dir() / f"{run_id}.jsonl"


def _append_trace(run_id: str, event: Dict[str, Any]) -> None:
    """Append one JSONL trace event for this run."""

    p = _trace_path(run_id)
    line = json.dumps(event, ensure_ascii=False)
    # Atomic-ish append
    with p.open("a", encoding="utf-8") as f:
        f.write(line)
        f.write("\n")


def _read_trace_tail(run_id: str, limit: int = 200) -> List[Dict[str, Any]]:
    """Read up to `limit` events from the tail of the JSONL trace."""

    p = _trace_path(run_id)
    if not p.exists():
        return []

    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    out: List[Dict[str, Any]] = []
    for line in lines[-limit:]:
        line = (line or "").strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue

    return out


def _now_ms() -> int:
    return int(time.time() * 1000)


class LabRunCreateRequest(BaseModel):
    symbol: str = Field(..., min_length=3, max_length=30)
    timeframe: str = Field(..., min_length=1, max_length=10)
    base_template: str = Field(..., min_length=1, max_length=128)
    direction: str = "long"
    constraints: Dict[str, Any] = Field(default_factory=dict)
    objective: Optional[str] = None
    thinking: str = "low"
    deep_backtest: bool = True


class LabRunCreateResponse(BaseModel):
    run_id: str
    status: str
    trace: Dict[str, str]


class LabRunTraceEvent(BaseModel):
    ts_ms: int
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)


class LabRunStatusResponse(BaseModel):
    run_id: str
    status: str
    step: Optional[str] = None
    created_at_ms: int
    updated_at_ms: int
    trace: Dict[str, str]
    trace_events: List[LabRunTraceEvent] = Field(default_factory=list)

    # CP3: minimal backtest output for 1 candidate (no autosave yet)
    backtest: Optional[Dict[str, Any]] = None


def _update_run_json(run_id: str, patch: Dict[str, Any]) -> None:
    p = _run_path(run_id)
    if not p.exists():
        return
    try:
        cur = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        cur = {}
    cur.update(patch)
    cur["updated_at_ms"] = _now_ms()
    p.write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding="utf-8")


def _cp3_default_since(timeframe: str) -> str:
    # Simple default windows to keep runtime bounded.
    tf = (timeframe or "").lower()
    if tf.endswith("h") or tf.endswith("m"):
        # Intraday: 6 months
        return "2025-08-01 00:00:00"
    # Daily+: 2 years
    return "2024-01-01 00:00:00"


def _run_single_candidate_backtest(run_id: str, req_dict: Dict[str, Any]) -> None:
    """CP3: run one backtest in background and persist the result into run json."""

    start_ms = _now_ms()
    _append_trace(
        run_id,
        {
            "ts_ms": start_ms,
            "type": "backtest_started",
            "data": {
                "symbol": req_dict.get("symbol"),
                "timeframe": req_dict.get("timeframe"),
                "template": req_dict.get("base_template"),
                "deep_backtest": bool(req_dict.get("deep_backtest", True)),
            },
        },
    )
    _update_run_json(run_id, {"status": "running", "step": "backtest"})

    try:
        from app.services.combo_service import ComboService
        from src.data.incremental_loader import IncrementalLoader
        from app.services.combo_optimizer import _run_backtest_logic

        symbol = str(req_dict.get("symbol") or "BTC/USDT")
        timeframe = str(req_dict.get("timeframe") or "1d")
        template_name = str(req_dict.get("base_template") or "multi_ma_crossover")
        deep_backtest = bool(req_dict.get("deep_backtest", True))
        direction = str(req_dict.get("direction") or "long")
        if direction not in ("long", "short"):
            direction = "long"

        since_str = _cp3_default_since(timeframe)
        until_str = None

        combo = ComboService()
        meta = combo.get_template_metadata(template_name)
        if not meta:
            raise RuntimeError(f"template not found: {template_name}")

        template_data = {
            "indicators": meta.get("indicators"),
            "entry_logic": meta.get("entry_logic"),
            "exit_logic": meta.get("exit_logic"),
            "stop_loss": meta.get("stop_loss"),
        }

        loader = IncrementalLoader()
        df = loader.fetch_data(symbol=symbol, timeframe=timeframe, since_str=since_str, until_str=until_str)
        if getattr(df, "empty", False) or len(df) == 0:
            raise RuntimeError("no candles loaded")

        params = {"direction": direction}
        metrics, full_params = _run_backtest_logic(
            template_data=template_data,
            params=params,
            df=df,
            deep_backtest=deep_backtest,
            symbol=symbol,
            since_str=since_str,
            until_str=until_str,
        )

        done_ms = _now_ms()
        out = {
            "symbol": symbol,
            "timeframe": timeframe,
            "template": template_name,
            "since": since_str,
            "until": until_str,
            "deep_backtest": deep_backtest,
            "direction": direction,
            "metrics": metrics,
            "params": full_params,
            "candles": len(df),
            "duration_ms": done_ms - start_ms,
        }

        _append_trace(
            run_id,
            {
                "ts_ms": done_ms,
                "type": "backtest_done",
                "data": {
                    "candles": len(df),
                    "duration_ms": done_ms - start_ms,
                    "metrics": metrics,
                },
            },
        )
        _update_run_json(run_id, {"status": "done", "step": "done", "backtest": out})

    except Exception as e:
        err_ms = _now_ms()
        _append_trace(run_id, {"ts_ms": err_ms, "type": "backtest_error", "data": {"error": str(e)}})
        _update_run_json(run_id, {"status": "error", "step": "error", "error": str(e)})


@router.post("/run", response_model=LabRunCreateResponse)
async def create_run(req: LabRunCreateRequest, background_tasks: BackgroundTasks) -> LabRunCreateResponse:
    run_id = uuid.uuid4().hex
    now = _now_ms()
    payload = {
        "run_id": run_id,
        "status": "accepted",
        "step": "init",
        "created_at_ms": now,
        "updated_at_ms": now,
        "input": req.model_dump(),
        "trace": [],
    }

    try:
        _run_path(run_id).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        _append_trace(
            run_id,
            {
                "ts_ms": now,
                "type": "run_created",
                "data": {"input": req.model_dump()},
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to persist run: {e}")

    # CP3: fire one background backtest (1 candidate, no personas yet)
    background_tasks.add_task(_run_single_candidate_backtest, run_id, req.model_dump())

    return LabRunCreateResponse(
        run_id=run_id,
        status="accepted",
        trace={
            "viewer_url": f"http://31.97.92.212:5173/lab/runs/{run_id}",
            "api_url": f"/api/lab/runs/{run_id}",
        },
    )


@router.get("/runs/{run_id}", response_model=LabRunStatusResponse)
async def get_run(run_id: str) -> LabRunStatusResponse:
    p = _run_path(run_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="run not found")

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to read run: {e}")

    trace_events = _read_trace_tail(run_id, limit=200)

    return LabRunStatusResponse(
        run_id=data.get("run_id") or run_id,
        status=data.get("status") or "unknown",
        step=data.get("step"),
        created_at_ms=int(data.get("created_at_ms") or 0),
        updated_at_ms=int(data.get("updated_at_ms") or 0),
        trace={
            "viewer_url": f"http://31.97.92.212:5173/lab/runs/{run_id}",
            "api_url": f"/api/lab/runs/{run_id}",
        },
        trace_events=trace_events,
        backtest=data.get("backtest"),
    )
