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


class LabRunBudget(BaseModel):
    turns_used: int = 0
    turns_max: int = 12
    tokens_total: int = 0
    tokens_max: int = 60000
    on_limit: str = "ask_user"  # ask_user


class LabRunOutputs(BaseModel):
    coordinator_summary: Optional[str] = None
    dev_summary: Optional[str] = None
    validator_verdict: Optional[str] = None


class LabRunStatusResponse(BaseModel):
    run_id: str
    status: str
    step: Optional[str] = None
    created_at_ms: int
    updated_at_ms: int
    trace: Dict[str, str]
    trace_events: List[LabRunTraceEvent] = Field(default_factory=list)

    budget: LabRunBudget = Field(default_factory=LabRunBudget)
    outputs: LabRunOutputs = Field(default_factory=LabRunOutputs)

    # CP3: minimal backtest output for 1 candidate (no autosave yet)
    backtest: Optional[Dict[str, Any]] = None

    # If we hit budget limits, the run waits for user confirmation.
    needs_user_confirm: bool = False


def _load_run_json(run_id: str) -> Dict[str, Any]:
    p = _run_path(run_id)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _update_run_json(run_id: str, patch: Dict[str, Any]) -> None:
    p = _run_path(run_id)
    if not p.exists():
        return
    cur = _load_run_json(run_id)
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


def _extract_tokens_from_gateway_payload(payload: Dict[str, Any]) -> int:
    """Best-effort token extraction from OpenClaw gateway agent payload."""

    # payload: {runId,status,result:{...}}
    res = (payload or {}).get("result") or {}
    usage = res.get("usage") or res.get("usageSummary") or {}
    for k in ("totalTokens", "total_tokens", "tokens_total"):
        v = usage.get(k)
        if isinstance(v, int):
            return v
    # Some providers split in/out
    if isinstance(usage.get("inputTokens"), int) and isinstance(usage.get("outputTokens"), int):
        return int(usage.get("inputTokens")) + int(usage.get("outputTokens"))
    return 0


def _persona_call_sync(*,
                       run_id: str,
                       session_key: str,
                       persona: str,
                       system_prompt: str,
                       message: str,
                       thinking: str,
                       timeout_s: int = 180) -> Dict[str, Any]:
    """Run one persona through OpenClaw gateway and trace it."""

    import asyncio

    from app.services.openclaw_gateway_client import run_agent_via_gateway

    start = _now_ms()
    _append_trace(run_id, {"ts_ms": start, "type": "persona_started", "data": {"persona": persona}})

    payload = asyncio.run(
        run_agent_via_gateway(
            message=message,
            session_key=session_key,
            agent_id="main",
            thinking=thinking,
            timeout_s=timeout_s,
            extra_system_prompt=system_prompt,
        )
    )

    tokens = _extract_tokens_from_gateway_payload(payload)
    end = _now_ms()

    # Best-effort content extraction
    result = (payload or {}).get("result") or {}
    text = result.get("text") or result.get("message") or result.get("output")
    if not isinstance(text, str):
        text = json.dumps(result, ensure_ascii=False)[:4000]

    _append_trace(
        run_id,
        {
            "ts_ms": end,
            "type": "persona_done",
            "data": {"persona": persona, "duration_ms": end - start, "tokens": tokens, "text": text[:2000]},
        },
    )

    return {"text": text, "tokens": tokens, "raw": payload}


def _budget_ok(budget: Dict[str, Any]) -> bool:
    return int(budget.get("turns_used", 0)) < int(budget.get("turns_max", 0)) and int(budget.get("tokens_total", 0)) < int(
        budget.get("tokens_max", 0)
    )


def _inc_budget(budget: Dict[str, Any], *, turns: int = 0, tokens: int = 0) -> Dict[str, Any]:
    b = dict(budget or {})
    b["turns_used"] = int(b.get("turns_used", 0)) + int(turns)
    b["tokens_total"] = int(b.get("tokens_total", 0)) + int(tokens)
    return b


def _cp4_run_personas_if_possible(run_id: str) -> None:
    """CP4: call 3 personas (coordinator/dev/validator) with budgets + UI confirmation."""

    run = _load_run_json(run_id)
    budget = run.get("budget") or {}
    outputs = run.get("outputs") or {}

    # If already waiting, do nothing.
    if run.get("needs_user_confirm"):
        return

    if not _budget_ok(budget):
        _update_run_json(run_id, {"status": "needs_user_confirm", "step": "budget", "needs_user_confirm": True})
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "budget_limit", "data": budget})
        return

    session_key = run.get("session_key") or f"lab-{run_id}"
    thinking = (run.get("input") or {}).get("thinking") or "low"

    backtest = run.get("backtest") or {}
    objective = (run.get("input") or {}).get("objective")

    context = {
        "objective": objective,
        "symbol": backtest.get("symbol"),
        "timeframe": backtest.get("timeframe"),
        "template": backtest.get("template"),
        "metrics": (backtest.get("metrics") or {}),
    }

    # Coordinator
    if not outputs.get("coordinator_summary") and _budget_ok(budget):
        r = _persona_call_sync(
            run_id=run_id,
            session_key=session_key,
            persona="coordinator",
            thinking=thinking,
            system_prompt=(
                "Você é o Coordenador do Strategy Lab. Resuma o que foi feito e proponha próximos passos. "
                "Responda em pt-BR, curto e objetivo."),
            message=f"Contexto do run (JSON):\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\nEscreva um sumário do coordenador.",
        )
        outputs["coordinator_summary"] = r["text"]
        budget = _inc_budget(budget, turns=1, tokens=r.get("tokens", 0))

    # Dev
    if not outputs.get("dev_summary") and _budget_ok(budget):
        r = _persona_call_sync(
            run_id=run_id,
            session_key=session_key,
            persona="dev_senior",
            thinking=thinking,
            system_prompt=(
                "Você é um Dev Sênior focado em templates/estratégias do Crypto Backtester. "
                "Sugira melhorias de template sem quebrar o sistema. Responda em pt-BR."),
            message=f"Contexto do run (JSON):\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\nSugira melhorias no template/parametros.\n", 
        )
        outputs["dev_summary"] = r["text"]
        budget = _inc_budget(budget, turns=1, tokens=r.get("tokens", 0))

    # Validator
    if not outputs.get("validator_verdict") and _budget_ok(budget):
        r = _persona_call_sync(
            run_id=run_id,
            session_key=session_key,
            persona="validator",
            thinking=thinking,
            system_prompt=(
                "Você é um Trader/Validador. Avalie robustez e riscos (sem lookahead, custos, overfit). "
                "Dê veredito 'approved' ou 'rejected' com motivos. Responda em pt-BR."),
            message=f"Contexto do run (JSON):\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\nDê veredito e motivos.",
        )
        outputs["validator_verdict"] = r["text"]
        budget = _inc_budget(budget, turns=1, tokens=r.get("tokens", 0))

    # Persist
    needs_confirm = not _budget_ok(budget) and not (outputs.get("coordinator_summary") and outputs.get("dev_summary") and outputs.get("validator_verdict"))

    patch: Dict[str, Any] = {
        "budget": budget,
        "outputs": outputs,
        "session_key": session_key,
        "needs_user_confirm": bool(needs_confirm),
    }

    if outputs.get("coordinator_summary") and outputs.get("dev_summary") and outputs.get("validator_verdict"):
        patch.update({"status": "done", "step": "done", "needs_user_confirm": False})
    elif needs_confirm:
        patch.update({"status": "needs_user_confirm", "step": "budget"})
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "budget_limit", "data": budget})
    else:
        patch.update({"status": "running", "step": "personas"})

    _update_run_json(run_id, patch)


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
        _update_run_json(run_id, {"status": "running", "step": "personas", "backtest": out})

        # CP4: run personas (may require OPENCLAW_GATEWAY_TOKEN configured)
        try:
            _cp4_run_personas_if_possible(run_id)
        except Exception as e:
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "personas_error", "data": {"error": str(e)}})
            # Don't fail the run hard; keep backtest available.
            _update_run_json(run_id, {"status": "done", "step": "done"})

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
        "session_key": f"lab-{run_id}",
        "budget": {
            "turns_used": 0,
            "turns_max": 12,
            "tokens_total": 0,
            "tokens_max": 60000,
            "on_limit": "ask_user",
            "continue_turns": 3,
            "continue_tokens": 15000,
        },
        "outputs": {
            "coordinator_summary": None,
            "dev_summary": None,
            "validator_verdict": None,
        },
        "needs_user_confirm": False,
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
        budget=data.get("budget") or {},
        outputs=data.get("outputs") or {},
        backtest=data.get("backtest"),
        needs_user_confirm=bool(data.get("needs_user_confirm")),
    )


@router.post("/runs/{run_id}/continue")
async def continue_run(run_id: str) -> Dict[str, Any]:
    """CP4: User-confirmed budget extension.

    Strategy per Alan choice (option 2): extend by +3 turns and +15000 tokens.
    """

    p = _run_path(run_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="run not found")

    run = _load_run_json(run_id)
    budget = run.get("budget") or {}
    inc_turns = int(budget.get("continue_turns", 3))
    inc_tokens = int(budget.get("continue_tokens", 15000))

    budget["turns_max"] = int(budget.get("turns_max", 0)) + inc_turns
    budget["tokens_max"] = int(budget.get("tokens_max", 0)) + inc_tokens

    _append_trace(
        run_id,
        {
            "ts_ms": _now_ms(),
            "type": "user_continue",
            "data": {"inc_turns": inc_turns, "inc_tokens": inc_tokens, "budget": budget},
        },
    )

    _update_run_json(run_id, {"budget": budget, "needs_user_confirm": False, "status": "running", "step": "personas"})

    # Resume personas now.
    try:
        _cp4_run_personas_if_possible(run_id)
    except Exception as e:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "personas_error", "data": {"error": str(e)}})

    return {"status": "ok", "run_id": run_id, "budget": budget}
