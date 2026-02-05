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

    # Use full available history by default (user preference). For Binance/ccxt
    # data, the true maximum depends on the loader, but we treat this as:
    # since = inception default (2017-01-01) unless explicitly overridden.
    full_history: bool = True
    since: Optional[str] = None
    until: Optional[str] = None

    # Autonomous search limits
    max_iterations: int = 3


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

    # CP10 selection gate summary
    selection: Optional[Dict[str, Any]] = None

    # CP8
    candidate_template_name: Optional[str] = None

    # CP5
    saved_template_name: Optional[str] = None
    saved_favorite_id: Optional[int] = None


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

    # CP9: job pipeline info for backtest execution
    backtest_job: Optional[Dict[str, Any]] = None

    # CP3/CP6: backtest output (supports walk-forward split)
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


def _cp3_default_since(timeframe: str, full_history: bool = True) -> str:
    """Default since.

    If full_history=True, we always start from a conservative "inception" date.
    """

    if full_history:
        return "2017-01-01 00:00:00"

    # Legacy bounded windows (kept for optional override)
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

    # Newer gateway shape: result.meta.agentMeta.usage
    agent_meta = (res.get("meta") or {}).get("agentMeta") or {}
    usage = agent_meta.get("usage") or {}

    # Common keys
    for k in ("totalTokens", "total_tokens", "tokens_total", "total"):
        v = usage.get(k)
        if isinstance(v, int):
            return v

    # Some providers split in/out
    if isinstance(usage.get("input"), int) and isinstance(usage.get("output"), int):
        return int(usage.get("input")) + int(usage.get("output"))
    if isinstance(usage.get("inputTokens"), int) and isinstance(usage.get("outputTokens"), int):
        return int(usage.get("inputTokens")) + int(usage.get("outputTokens"))

    return 0


def _extract_text_from_gateway_payload(payload: Dict[str, Any]) -> str:
    """Best-effort extraction of assistant text from gateway payload."""

    res = (payload or {}).get("result") or {}

    # Preferred: payloads[0].text
    payloads = res.get("payloads")
    if isinstance(payloads, list) and payloads:
        p0 = payloads[0]
        if isinstance(p0, dict):
            t = p0.get("text") or p0.get("content")
            if isinstance(t, str) and t.strip():
                return t.strip()
        if isinstance(p0, str) and p0.strip():
            return p0.strip()

    # Fallback: meta/message fields
    for k in ("text", "message", "output"):
        t = res.get(k)
        if isinstance(t, str) and t.strip():
            return t.strip()

    # Last resort: stringify compactly
    return json.dumps(res, ensure_ascii=False)[:4000]


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

    text = _extract_text_from_gateway_payload(payload)

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


def _verdict_label(text: Optional[str]) -> str:
    """Extract approval label from the validator output.

    Important: do NOT treat mentions like "para virar approved" as approval.
    Prefer explicit leading verdict markers.
    """

    t = (text or "").strip().lower()
    if not t:
        return "unknown"

    # Strong signals first (explicit markers)
    for pat in (
        "veredito: rejected",
        "veredito: reprovado",
        "veredito: aprovado",  # pt-BR
        "veredito: approved",
    ):
        if pat in t:
            if "rejected" in pat or "reprovado" in pat:
                return "rejected"
            if "approved" in pat or "aprovado" in pat:
                return "approved"

    # Next: heading-ish patterns at start
    if t.startswith("**veredito: rejected") or t.startswith("veredito: rejected"):
        return "rejected"
    if t.startswith("**veredito: approved") or t.startswith("veredito: approved"):
        return "approved"
    if t.startswith("rejected") or t.startswith("**rejected"):
        return "rejected"
    if t.startswith("approved") or t.startswith("**approved"):
        return "approved"

    # Fallback: if both words appear, prefer rejected (safer)
    has_app = "approved" in t or "aprovado" in t
    has_rej = "rejected" in t or "reprovado" in t
    if has_app and has_rej:
        return "rejected"
    if has_rej:
        return "rejected"
    if has_app:
        return "approved"

    return "unknown"


def _make_autosave_name(*, run_id: str, base_template: str, symbol: str, timeframe: str) -> str:
    safe_symbol = (symbol or "").replace("/", "_")
    rid = (run_id or "")[:8]
    return f"lab_{rid}_{base_template}_{safe_symbol}_{timeframe}".strip("_")


def _ensure_unique_template_name(combo, name: str) -> str:
    # combo: ComboService
    base = name
    if not combo.get_template_metadata(base):
        return base
    for i in range(2, 200):
        cand = f"{base}_{i}"
        if not combo.get_template_metadata(cand):
            return cand
    # last resort
    return f"{base}_{uuid.uuid4().hex[:6]}"


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not isinstance(text, str):
        return None
    s = text.strip()
    if not s:
        return None
    # try direct parse
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    # try substring between first { and last }
    a = s.find("{")
    b = s.rfind("}")
    if a >= 0 and b > a:
        try:
            obj = json.loads(s[a : b + 1])
            if isinstance(obj, dict):
                return obj
        except Exception:
            return None
    return None


def _make_candidate_name(*, run_id: str, base_template: str, symbol: str, timeframe: str, n: int) -> str:
    safe_symbol = (symbol or "").replace("/", "_")
    rid = (run_id or "")[:8]
    return f"lab_{rid}_candidate_{n}_{base_template}_{safe_symbol}_{timeframe}".strip("_")


def _cp8_save_candidate_template(run_id: str, run: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """CP8: save a real candidate template based on dev output JSON."""

    if outputs.get("candidate_template_name"):
        return outputs

    dev_text = outputs.get("dev_summary")
    blob = _extract_json_object(dev_text or "")
    if not blob:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": "dev_summary is not valid JSON"}})
        return outputs

    candidate_data = blob.get("candidate_template_data")
    if not isinstance(candidate_data, dict):
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": "missing candidate_template_data"}})
        return outputs

    inds = candidate_data.get("indicators") or []
    if not isinstance(inds, list):
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": "indicators must be a list"}})
        return outputs

    if len(inds) > 4:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": f"too many indicators: {len(inds)}"}})
        return outputs

    # Validate indicator schema (must match ComboStrategy expectation)
    for idx, ind in enumerate(inds):
        if not isinstance(ind, dict):
            _append_trace(
                run_id,
                {
                    "ts_ms": _now_ms(),
                    "type": "candidate_error",
                    "data": {"error": f"indicator[{idx}] must be an object with type/alias/params"},
                },
            )
            return outputs
        if not isinstance(ind.get("type"), str) or not ind.get("type"):
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": f"indicator[{idx}].type missing"}})
            return outputs
        if not isinstance(ind.get("alias"), str) or not ind.get("alias"):
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": f"indicator[{idx}].alias missing"}})
            return outputs
        if not isinstance(ind.get("params"), dict):
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": f"indicator[{idx}].params must be object"}})
            return outputs

    try:
        from app.services.combo_service import ComboService

        inp = run.get("input") or {}
        backtest = run.get("backtest") or {}
        base_template = str(inp.get("base_template") or backtest.get("template") or "")
        symbol = str(backtest.get("symbol") or inp.get("symbol") or "")
        timeframe = str(backtest.get("timeframe") or inp.get("timeframe") or "")

        combo = ComboService()

        # find next available candidate name
        n = 1
        while True:
            name = _make_candidate_name(run_id=run_id, base_template=base_template, symbol=symbol, timeframe=timeframe, n=n)
            if not combo.get_template_metadata(name):
                break
            n += 1
            if n > 50:
                raise RuntimeError("too many candidates")

        # clone base, then overwrite template_data
        combo.clone_template(template_name=base_template, new_name=name)
        desc = blob.get("description")
        if not isinstance(desc, str):
            desc = f"Lab candidate from {run_id}"

        combo.update_template(template_name=name, description=desc, template_data=candidate_data)

        outputs["candidate_template_name"] = name
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_saved", "data": {"template": name}})
        return outputs

    except Exception as e:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "candidate_error", "data": {"error": str(e)}})
        return outputs


def _cp10_selection_gate(run: Dict[str, Any]) -> Dict[str, Any]:
    """CP10: deterministic approval gate based on holdout metrics.

    This gate is evaluated before autosave.
    """

    inp = run.get("input") or {}
    constraints = inp.get("constraints") or {}
    max_dd = constraints.get("max_drawdown")
    min_sharpe = constraints.get("min_sharpe")

    backtest = run.get("backtest") or {}
    wf = backtest.get("walk_forward") or {}
    hold = (wf.get("holdout") or {}).get("metrics") or {}

    total_trades = hold.get("total_trades")
    sharpe = hold.get("sharpe_ratio")
    dd = hold.get("max_drawdown")
    # Some parts store pct; accept both
    dd_pct = hold.get("max_drawdown_pct")

    reasons: list[str] = []

    # Minimum trades on holdout (default 10)
    min_holdout_trades = int(constraints.get("min_holdout_trades") or 10)
    if not isinstance(total_trades, (int, float)) or int(total_trades) < min_holdout_trades:
        reasons.append(f"holdout_total_trades<{min_holdout_trades} ({total_trades})")

    if min_sharpe is not None:
        try:
            if sharpe is None or float(sharpe) < float(min_sharpe):
                reasons.append(f"holdout_sharpe<{min_sharpe} ({sharpe})")
        except Exception:
            reasons.append("holdout_sharpe_invalid")

    if max_dd is not None:
        # compare against decimal dd if available else pct
        try:
            if dd is not None:
                if float(dd) > float(max_dd):
                    reasons.append(f"holdout_max_drawdown>{max_dd} ({dd})")
            elif dd_pct is not None:
                if float(dd_pct) / 100.0 > float(max_dd):
                    reasons.append(f"holdout_max_drawdown_pct>{max_dd} ({dd_pct})")
        except Exception:
            reasons.append("holdout_max_drawdown_invalid")

    return {
        "approved": len(reasons) == 0,
        "reasons": reasons,
        "min_holdout_trades": min_holdout_trades,
        "holdout": {"total_trades": total_trades, "sharpe_ratio": sharpe, "max_drawdown": dd, "max_drawdown_pct": dd_pct},
    }


def _cp5_autosave_if_approved(run_id: str, run: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """CP5/CP10: autosave (template + favorite) only when validator says approved AND selection gate passes."""

    verdict = _verdict_label(outputs.get("validator_verdict"))
    selection = outputs.get("selection") or {}
    if verdict != "approved":
        return outputs
    if not selection or not selection.get("approved"):
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "autosave_blocked", "data": {"reason": "selection_gate", "selection": selection}})
        return outputs

    try:
        from app.services.combo_service import ComboService
        from app.database import SessionLocal
        from app.models import FavoriteStrategy

        inp = run.get("input") or {}
        backtest = run.get("backtest") or {}
        base_template = str(inp.get("base_template") or backtest.get("template") or "")
        # CP10: if we have a candidate template, autosave should be based on it.
        candidate_template = outputs.get("candidate_template_name")
        template_to_save = str(candidate_template or base_template)

        symbol = str(backtest.get("symbol") or inp.get("symbol") or "")
        timeframe = str(backtest.get("timeframe") or inp.get("timeframe") or "")

        combo = ComboService()

        # Guardrail: max 4 indicators
        base_meta = combo.get_template_metadata(template_to_save)
        inds = (base_meta or {}).get("indicators") or []
        if len(inds) > 4:
            raise RuntimeError(f"template has too many indicators (max 4): {len(inds)}")

        new_name = _make_autosave_name(run_id=run_id, base_template=template_to_save, symbol=symbol, timeframe=timeframe)
        new_name = _ensure_unique_template_name(combo, new_name)

        # Clone template
        cloned = combo.clone_template(template_name=template_to_save, new_name=new_name)
        if not cloned:
            raise RuntimeError("failed to clone template")

        # Create favorite pointing to the cloned template
        params = backtest.get("params") or {}
        metrics = backtest.get("metrics")
        since = backtest.get("since")
        until = backtest.get("until")

        period_type = "2y" if str(timeframe).endswith("d") else "6m"

        fav_name = f"{new_name} - {symbol} {timeframe} (lab)"
        notes = f"lab_run_id={run_id}; verdict=approved"

        db = SessionLocal()
        try:
            fav = FavoriteStrategy(
                name=fav_name,
                symbol=symbol,
                timeframe=timeframe,
                strategy_name=new_name,
                parameters=params,
                metrics=metrics,
                notes=notes,
                tier=None,
                start_date=since,
                end_date=until,
                period_type=period_type,
            )
            db.add(fav)
            db.commit()
            db.refresh(fav)
            outputs["saved_template_name"] = new_name
            outputs["saved_favorite_id"] = int(fav.id)
        finally:
            db.close()

        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "autosave_done", "data": {"template": new_name, "favorite_id": outputs.get("saved_favorite_id")}})
        return outputs

    except Exception as e:
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "autosave_error", "data": {"error": str(e)}})
        return outputs


def _cp4_run_personas_if_possible(run_id: str) -> None:
    """CP4/CP7: run personas.

    CP7 (v2) requirement: execute the flow via LangGraph and emit
    `node_started`/`node_done` trace events.
    """

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

    wf = (backtest.get("walk_forward") or {})
    context = {
        "objective": objective,
        "symbol": backtest.get("symbol"),
        "timeframe": backtest.get("timeframe"),
        "template": backtest.get("template"),
        "walk_forward": {
            "split": (wf.get("split") or "70/30"),
            "metrics_all": (backtest.get("metrics") or {}),
            "metrics_in_sample": ((wf.get("in_sample") or {}).get("metrics") or {}),
            "metrics_holdout": ((wf.get("holdout") or {}).get("metrics") or {}),
        },
    }

    # LangGraph CP7
    try:
        from app.services.lab_graph import LabGraphDeps, build_cp7_graph

        graph = build_cp7_graph()
        deps = LabGraphDeps(
            persona_call=_persona_call_sync,
            append_trace=_append_trace,
            now_ms=_now_ms,
            inc_budget=_inc_budget,
            budget_ok=_budget_ok,
        )

        state_in = {
            "run_id": run_id,
            "session_key": session_key,
            "thinking": thinking,
            "context": context,
            "deps": deps,
            "budget": budget,
            "outputs": outputs,
        }

        state_out = graph.invoke(state_in)
        budget = state_out.get("budget") or budget
        outputs = state_out.get("outputs") or outputs

        # Persist partial progress too
        _update_run_json(run_id, {"budget": budget, "outputs": outputs})

    except Exception as e:
        # Fallback to previous behavior (but still keep the run alive)
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "langgraph_error", "data": {"error": str(e)}})

    # Persist
    needs_confirm = not _budget_ok(budget) and not (outputs.get("coordinator_summary") and outputs.get("dev_summary") and outputs.get("validator_verdict"))

    # CP8: persist candidate template after Dev output exists
    if outputs.get("coordinator_summary") and outputs.get("dev_summary"):
        outputs = _cp8_save_candidate_template(run_id, run, outputs)

    # CP10: deterministic selection gate (holdout-based)
    if outputs.get("coordinator_summary") and outputs.get("validator_verdict"):
        sel = _cp10_selection_gate(run)
        outputs["selection"] = sel
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "selection_gate", "data": sel})
        _update_run_json(run_id, {"outputs": outputs})

    # CP5/CP10: autosave only if approved
    if outputs.get("coordinator_summary") and outputs.get("dev_summary") and outputs.get("validator_verdict"):
        outputs = _cp5_autosave_if_approved(run_id, run, outputs)

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


def _run_lab_autonomous(run_id: str, req_dict: Dict[str, Any]) -> None:
    """Autonomous Lab loop.

    Implements:
    1) Backtest candidate inside the same run (not just propose it).
    2) Iterate multiple attempts (bounded) until an interesting result or limits hit.
    3) Quick parameter tuning (tool-based) on the candidate before re-testing.

    Uses the CP9 job pipeline (JobManager state) for each backtest.
    """

    import copy
    import itertools
    import random

    from app.services.job_manager import JobManager
    from app.services.combo_service import ComboService
    from src.data.incremental_loader import IncrementalLoader
    from app.services.combo_optimizer import _run_backtest_logic

    symbol = str(req_dict.get("symbol") or "BTC/USDT")
    timeframe = str(req_dict.get("timeframe") or "1d")
    deep_backtest = bool(req_dict.get("deep_backtest", True))
    direction = str(req_dict.get("direction") or "long")
    if direction not in ("long", "short"):
        direction = "long"

    run = _load_run_json(run_id) or {}
    inp = run.get("input") or {}
    full_history = bool(inp.get("full_history", True))
    since_str = str(inp.get("since") or "").strip() or _cp3_default_since(timeframe, full_history=full_history)
    until_str = str(inp.get("until") or "").strip() or None

    max_iterations = int(inp.get("max_iterations") or 3)
    max_iterations = max(1, min(10, max_iterations))

    jm = JobManager()
    combo = ComboService()

    # Load candles ONCE for the run (full history by default)
    loader = IncrementalLoader()
    df = loader.fetch_data(symbol=symbol, timeframe=timeframe, since_str=since_str, until_str=until_str)
    if getattr(df, "empty", False) or len(df) == 0:
        _update_run_json(run_id, {"status": "error", "step": "error", "error": "no candles loaded"})
        return
    try:
        df = df.sort_index()
    except Exception:
        pass

    n = len(df)
    split_idx = int(n * 0.7)
    split_idx = max(1, min(n - 1, split_idx))
    df_is = df.iloc[:split_idx]
    df_oos = df.iloc[split_idx:]

    def _df_bounds(dfx):
        if len(dfx) == 0:
            return None, None
        try:
            s = dfx.index[0]
            e = dfx.index[-1]
            return (s.isoformat() if hasattr(s, "isoformat") else str(s)), (e.isoformat() if hasattr(e, "isoformat") else str(e))
        except Exception:
            return None, None

    is_since, is_until = _df_bounds(df_is)
    oos_since, oos_until = _df_bounds(df_oos)

    def _context_for_backtest(bt: Dict[str, Any]) -> Dict[str, Any]:
        wf = (bt.get("walk_forward") or {})
        return {
            "objective": (inp.get("objective") or None),
            "symbol": bt.get("symbol"),
            "timeframe": bt.get("timeframe"),
            "template": bt.get("template"),
            "walk_forward": {
                "split": (wf.get("split") or "70/30"),
                "metrics_all": (bt.get("metrics") or {}),
                "metrics_in_sample": ((wf.get("in_sample") or {}).get("metrics") or {}),
                "metrics_holdout": ((wf.get("holdout") or {}).get("metrics") or {}),
            },
        }

    def _run_backtest_job(*, template_name: str, label: str, iteration: int) -> Dict[str, Any]:
        meta = combo.get_template_metadata(template_name)
        if not meta:
            raise RuntimeError(f"template not found: {template_name}")

        template_data = {
            "indicators": meta.get("indicators"),
            "entry_logic": meta.get("entry_logic"),
            "exit_logic": meta.get("exit_logic"),
            "stop_loss": meta.get("stop_loss"),
        }

        job_id = jm.create_job({"kind": "lab_backtest", "run_id": run_id, "iteration": iteration, "label": label, "template": template_name})
        _update_run_json(
            run_id,
            {
                "status": "running",
                "step": "backtest_job",
                "backtest_job": {"job_id": job_id, "status": "RUNNING", "progress": {"step": "init", "pct": 0}},
            },
        )
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "job_created", "data": {"job_id": job_id, "label": label, "template": template_name, "iteration": iteration}})

        # ALL / IS / HOLDOUT metrics
        state = jm.load_state(job_id) or {}
        state.update({"status": "RUNNING", "progress": {"step": "backtest_all", "pct": 35}})
        jm.save_state(job_id, state)
        metrics_all, full_params = _run_backtest_logic(
            template_data=template_data,
            params={"direction": direction},
            df=df,
            deep_backtest=deep_backtest,
            symbol=symbol,
            since_str=since_str,
            until_str=until_str,
        )

        state = jm.load_state(job_id) or {}
        state.update({"status": "RUNNING", "progress": {"step": "backtest_in_sample", "pct": 60}})
        jm.save_state(job_id, state)
        metrics_is, _ = _run_backtest_logic(
            template_data=template_data,
            params={"direction": direction},
            df=df_is,
            deep_backtest=deep_backtest,
            symbol=symbol,
            since_str=is_since or since_str,
            until_str=is_until,
        )

        state = jm.load_state(job_id) or {}
        state.update({"status": "RUNNING", "progress": {"step": "backtest_holdout", "pct": 85}})
        jm.save_state(job_id, state)
        metrics_oos, _ = _run_backtest_logic(
            template_data=template_data,
            params={"direction": direction},
            df=df_oos,
            deep_backtest=deep_backtest,
            symbol=symbol,
            since_str=oos_since or since_str,
            until_str=oos_until,
        )

        out = {
            "symbol": symbol,
            "timeframe": timeframe,
            "template": template_name,
            "since": since_str,
            "until": until_str,
            "deep_backtest": deep_backtest,
            "direction": direction,
            "params": full_params,
            "walk_forward": {
                "split": "70/30",
                "split_idx": split_idx,
                "candles_all": n,
                "candles_in_sample": len(df_is),
                "candles_holdout": len(df_oos),
                "in_sample": {"since": is_since, "until": is_until, "metrics": metrics_is},
                "holdout": {"since": oos_since, "until": oos_until, "metrics": metrics_oos},
            },
            "metrics": metrics_all,
            "candles": n,
            "label": label,
            "iteration": iteration,
        }

        _append_trace(
            run_id,
            {
                "ts_ms": _now_ms(),
                "type": "backtest_done",
                "data": {"label": label, "template": template_name, "metrics_all": metrics_all, "metrics_in_sample": metrics_is, "metrics_holdout": metrics_oos},
            },
        )

        state = jm.load_state(job_id) or {}
        state.update({"status": "COMPLETED", "progress": {"step": "done", "pct": 100}, "final_results": out})
        jm.save_state(job_id, state)

        _update_run_json(
            run_id,
            {
                "status": "running",
                "step": "personas",
                "backtest": out,
                "backtest_job": {"job_id": job_id, "status": "COMPLETED", "progress": {"step": "done", "pct": 100}},
            },
        )
        return out

    def _quick_tune_candidate_params(template_name: str, iteration: int) -> None:
        """Lightweight parameter tuning on IN-SAMPLE using tool backtests.

        We keep it intentionally small/fast: sample a handful of variations.
        """

        try:
            meta = combo.get_template_metadata(template_name)
            if not meta:
                return
            inds = meta.get("indicators") or []
            if not isinstance(inds, list) or not inds:
                return

            # Build candidate value options for numeric params
            per_ind_options: list[list[Dict[str, Any]]] = []
            for ind in inds:
                if not isinstance(ind, dict):
                    continue
                params0 = ind.get("params") or {}
                if not isinstance(params0, dict):
                    params0 = {}

                # For common length/period keys, try +/- 20% and +/- 5
                options = []
                for delta_mul in (0.8, 1.0, 1.2):
                    ind2 = copy.deepcopy(ind)
                    for k in list(params0.keys()):
                        v = params0.get(k)
                        if isinstance(v, (int, float)) and k in ("length", "period"):
                            nv = int(max(2, round(float(v) * delta_mul)))
                            ind2.setdefault("params", {})[k] = nv
                    options.append(ind2)
                per_ind_options.append(options[:3])

            if not per_ind_options:
                return

            # Sample up to 12 combinations
            combos = list(itertools.product(*per_ind_options))
            random.shuffle(combos)
            combos = combos[:12]

            base_template_data = {
                "indicators": meta.get("indicators"),
                "entry_logic": meta.get("entry_logic"),
                "exit_logic": meta.get("exit_logic"),
                "stop_loss": meta.get("stop_loss"),
            }

            best = None
            best_metrics = None

            for c in combos:
                td = copy.deepcopy(base_template_data)
                td["indicators"] = list(c)
                # Tune stop_loss lightly
                sl = td.get("stop_loss")
                if isinstance(sl, dict):
                    sl = sl.get("default")
                if not isinstance(sl, (int, float)):
                    sl = 0.03
                td["stop_loss"] = float(min(0.08, max(0.005, sl)))

                metrics, _ = _run_backtest_logic(
                    template_data=td,
                    params={"direction": direction},
                    df=df_is,
                    deep_backtest=False,
                    symbol=symbol,
                    since_str=is_since or since_str,
                    until_str=is_until,
                )
                sharpe = (metrics or {}).get("sharpe_ratio")
                if best is None or (isinstance(sharpe, (int, float)) and isinstance((best_metrics or {}).get("sharpe_ratio"), (int, float)) and sharpe > (best_metrics or {}).get("sharpe_ratio")):
                    best = td
                    best_metrics = metrics

            if best is not None and best_metrics is not None:
                combo.update_template(template_name=template_name, template_data=best)
                _append_trace(run_id, {"ts_ms": _now_ms(), "type": "param_tuned", "data": {"template": template_name, "iteration": iteration, "best_in_sample": best_metrics}})
        except Exception as e:
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "param_tune_error", "data": {"template": template_name, "iteration": iteration, "error": str(e)}})

    # Loop: propose → backtest candidate → validate → repeat
    current_template = str(req_dict.get("base_template") or "multi_ma_crossover")

    for it in range(1, max_iterations + 1):
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "iteration_started", "data": {"iteration": it, "template": current_template}})

        # Backtest current template
        bt = _run_backtest_job(template_name=current_template, label=f"iter{it}_current", iteration=it)

        # Run CP7 personas (coordinator+dev+validator) on current results to get a candidate
        try:
            from app.services.lab_graph import LabGraphDeps, build_cp7_graph

            run = _load_run_json(run_id) or {}
            budget = run.get("budget") or {}
            outputs = run.get("outputs") or {}

            deps = LabGraphDeps(
                persona_call=_persona_call_sync,
                append_trace=_append_trace,
                now_ms=_now_ms,
                inc_budget=_inc_budget,
                budget_ok=_budget_ok,
            )

            graph = build_cp7_graph()
            state = {
                "run_id": run_id,
                "session_key": run.get("session_key") or f"lab-{run_id}",
                "thinking": inp.get("thinking") or "low",
                "context": _context_for_backtest(bt),
                "deps": deps,
                "budget": budget,
                "outputs": outputs,
            }
            final = graph.invoke(state)
            budget = final.get("budget") or budget
            outputs = final.get("outputs") or outputs
            _update_run_json(run_id, {"budget": budget, "outputs": outputs})

            if not _budget_ok(budget):
                _update_run_json(run_id, {"status": "needs_user_confirm", "step": "budget", "needs_user_confirm": True})
                return

            # CP8 save candidate
            outputs = _cp8_save_candidate_template(run_id, _load_run_json(run_id) or {}, outputs)
            _update_run_json(run_id, {"outputs": outputs})

        except Exception as e:
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "personas_error", "data": {"error": str(e), "iteration": it}})
            _update_run_json(run_id, {"status": "error", "step": "error", "error": str(e)})
            return

        run = _load_run_json(run_id) or {}
        outputs = run.get("outputs") or {}
        cand = outputs.get("candidate_template_name")
        if not cand:
            _update_run_json(run_id, {"status": "error", "step": "error", "error": "candidate not created"})
            return

        # Tool-based quick parameter tuning on candidate (IN-SAMPLE)
        _quick_tune_candidate_params(str(cand), it)

        # Backtest candidate and overwrite run.backtest
        bt2 = _run_backtest_job(template_name=str(cand), label=f"iter{it}_candidate", iteration=it)

        # Re-run validator on the candidate results (so verdict matches the tested candidate)
        try:
            run = _load_run_json(run_id) or {}
            budget = run.get("budget") or {}
            outputs = run.get("outputs") or {}
            if _budget_ok(budget):
                msg = "Contexto do run (JSON):\n" + json.dumps(_context_for_backtest(bt2), ensure_ascii=False, indent=2) + "\n"
                r = _persona_call_sync(
                    run_id=run_id,
                    session_key=run.get("session_key") or f"lab-{run_id}",
                    persona="validator",
                    system_prompt=(
                        "Você é um Trader/Validador. Avalie robustez e riscos (sem lookahead, custos, overfit). "
                        "Use principalmente o HOLDOUT (30% mais recente) para o veredito. "
                        "Dê veredito 'approved' ou 'rejected' com motivos. Responda em pt-BR."
                    ),
                    message=msg,
                    thinking=inp.get("thinking") or "low",
                )
                outputs["validator_verdict"] = r.get("text")
                budget = _inc_budget(budget, turns=1, tokens=r.get("tokens", 0) or 0)
                _update_run_json(run_id, {"budget": budget, "outputs": outputs})
        except Exception as e:
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "validator_error", "data": {"error": str(e), "iteration": it}})

        # Gate + autosave (based on candidate backtest)
        run = _load_run_json(run_id) or {}
        outputs = run.get("outputs") or {}
        sel = _cp10_selection_gate(run)
        outputs["selection"] = sel
        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "selection_gate", "data": sel})
        _update_run_json(run_id, {"outputs": outputs})

        outputs = _cp5_autosave_if_approved(run_id, run, outputs)
        _update_run_json(run_id, {"outputs": outputs})

        if outputs.get("saved_favorite_id"):
            _update_run_json(run_id, {"status": "done", "step": "done", "needs_user_confirm": False})
            _append_trace(run_id, {"ts_ms": _now_ms(), "type": "iteration_done", "data": {"iteration": it, "result": "approved_and_saved"}})
            return

        _append_trace(run_id, {"ts_ms": _now_ms(), "type": "iteration_done", "data": {"iteration": it, "result": "rejected"}})
        current_template = str(cand)

    # If we exit the loop, we're done (rejected after max iterations)
    _update_run_json(run_id, {"status": "done", "step": "done"})


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
            "selection": None,
            "candidate_template_name": None,
            "saved_template_name": None,
            "saved_favorite_id": None,
        },
        "backtest_job": None,
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

    # Autonomous loop: base backtest → propose candidate → backtest candidate → validate → repeat
    background_tasks.add_task(_run_lab_autonomous, run_id, req.model_dump())

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
        backtest_job=data.get("backtest_job"),
        backtest=data.get("backtest"),
        needs_user_confirm=bool(data.get("needs_user_confirm")),
    )


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> Dict[str, Any]:
    """CP9: fetch job state for a backtest job."""

    from app.services.job_manager import JobManager

    jm = JobManager()
    state = jm.load_state(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="job not found")
    return state


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
