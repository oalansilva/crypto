"""Lab graph with mandatory upstream + implementation/tests phases.

This module keeps a single LangGraph workflow and introduces a deterministic
upstream contract before implementation.
"""

from __future__ import annotations

import concurrent.futures
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class LabGraphState(TypedDict, total=False):
    run_id: str
    session_key: str
    thinking: str
    context: Dict[str, Any]

    # runtime deps (in-process only)
    deps: Any

    budget: Dict[str, Any]
    outputs: Dict[str, Any]

    upstream_contract: Dict[str, Any]
    phase: str
    status: str
    implementation_complete: bool
    tests_result: Dict[str, Any]
    implementation_rounds: int
    trader_retry_count: int
    diagnostic: Dict[str, Any]


@dataclass
class LabGraphDeps:
    persona_call: Any  # callable
    append_trace: Any  # callable
    now_ms: Any  # callable
    inc_budget: Any  # callable
    budget_ok: Any  # callable


class LabGraphNodeTimeoutError(TimeoutError):
    def __init__(self, *, node: str, timeout_s: int):
        super().__init__(f"node '{node}' exceeded timeout of {timeout_s}s")
        self.node = node
        self.timeout_s = timeout_s


class TraderVerdictOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    verdict: Literal["approved", "rejected", "needs_adjustment", "metrics_invalid"]
    reasons: List[str] = Field(default_factory=list)
    required_fixes: List[str] = Field(default_factory=list)
    feedback_for_dev: Optional[str] = None
    notes: Optional[str] = None


class DevTemplateOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    indicators: List[Dict[str, Any]] = Field(default_factory=list)
    entry_logic: str
    exit_logic: str
    stop_loss: Optional[float] = None


class DevBacktestSummaryOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    all: Dict[str, Any] = Field(default_factory=dict)
    in_sample: Dict[str, Any] = Field(default_factory=dict)
    holdout: Dict[str, Any] = Field(default_factory=dict)


class DevSummaryOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    template_data: DevTemplateOutput
    backtest_job_id: str
    backtest_summary: DevBacktestSummaryOutput
    ready_for_trader: Optional[bool] = None


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(str(raw).strip())
    except Exception:
        return default
    return max(minimum, value)


def _node_timeout_s(state: LabGraphState) -> int:
    default = _env_int("LAB_NODE_TIMEOUT_S", 180, minimum=1)
    context = state.get("context") or {}
    inp = context.get("input") if isinstance(context.get("input"), dict) else {}
    if not isinstance(inp, dict):
        return default
    try:
        raw = int(inp.get("node_timeout_s") or default)
    except Exception:
        return default
    return max(1, raw)


def _mk_output_diag(*, node: str, reason: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "type": "invalid_output",
        "scope": "persona",
        "node": node,
        "reason": reason,
    }
    if isinstance(details, dict) and details:
        payload["details"] = details
    return payload


def _parse_json_object(value: Any) -> tuple[str, Dict[str, Any], Optional[str]]:
    raw = _normalize_str(value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False), value, None
    if not raw:
        return raw, {}, "empty_output"
    if not raw.startswith("{"):
        return raw, {}, "not_json_object"
    try:
        obj = json.loads(raw)
    except Exception:
        return raw, {}, "malformed_json"
    if not isinstance(obj, dict):
        return raw, {}, "not_json_object"
    return raw, obj, None


def _normalize_str(value: Any) -> str:
    return str(value or "").strip()


def _ensure_str_list(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []

    out: List[str] = []
    for item in values:
        s = _normalize_str(item)
        if s:
            out.append(s)
    return out


def _missing_question(missing: List[str]) -> str:
    if missing == ["symbol", "timeframe"]:
        return "Quais são o symbol (ex: BTC/USDT) e o timeframe (ex: 1h, 4h) para rodarmos o Lab?"
    if missing == ["symbol"]:
        return "Qual é o symbol (ex: BTC/USDT) para rodarmos o Lab?"
    return "Qual é o timeframe (ex: 1h, 4h) para rodarmos o Lab?"


def build_upstream_contract(*, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create deterministic upstream contract from the current context."""

    ctx = context or {}
    inp = ctx.get("input") or {}
    if not isinstance(inp, dict):
        inp = {}

    symbol = _normalize_str(ctx.get("symbol") or inp.get("symbol"))
    timeframe = _normalize_str(ctx.get("timeframe") or inp.get("timeframe"))
    objective = _normalize_str(ctx.get("objective") or inp.get("objective"))

    if not objective:
        objective = "Executar o Strategy Lab com foco em robustez, risco controlado e critérios claros de aceite."

    acceptance_criteria = _ensure_str_list(ctx.get("acceptance_criteria") or inp.get("acceptance_criteria"))
    if len(acceptance_criteria) < 2:
        acceptance_criteria = [
            "Gerar saída de implementação sem erros estruturais.",
            "Concluir validação determinística com resultado explícito.",
        ]

    constraints = inp.get("constraints") or {}
    if not isinstance(constraints, dict):
        constraints = {}

    risk_notes = _ensure_str_list(ctx.get("risk_notes") or inp.get("risk_notes"))
    if not risk_notes:
        if constraints.get("max_drawdown") is not None:
            risk_notes.append(f"Respeitar max_drawdown <= {constraints.get('max_drawdown')}.")
        if constraints.get("min_sharpe") is not None:
            risk_notes.append(f"Buscar min_sharpe >= {constraints.get('min_sharpe')}.")
        if not risk_notes:
            risk_notes.append("Sem limites explícitos; aplicar guardrails de risco padrão do Lab.")

    missing: List[str] = []
    if not symbol:
        missing.append("symbol")
    if not timeframe:
        missing.append("timeframe")

    approved = len(missing) == 0

    return {
        "approved": approved,
        "missing": missing,
        "question": "" if approved else _missing_question(missing),
        "inputs": {
            "symbol": symbol,
            "timeframe": timeframe,
        },
        "objective": objective,
        "acceptance_criteria": acceptance_criteria,
        "risk_notes": risk_notes,
    }


def _verdict_label(text: Optional[str]) -> str:
    raw = _normalize_str(text)
    lower = raw.lower()
    if not lower:
        return "unknown"

    if raw.startswith("{"):
        try:
            obj = json.loads(raw)
            verdict = _normalize_str(obj.get("verdict")).lower()
            if verdict in ("approved", "rejected", "needs_adjustment", "metrics_invalid"):
                return verdict
        except Exception:
            pass

    if "rejected" in lower or "reprovado" in lower:
        return "rejected"
    if "approved" in lower or "aprovado" in lower:
        return "approved"
    if "needs_adjustment" in lower or "needs adjustment" in lower:
        return "needs_adjustment"
    if "metrics_invalid" in lower:
        return "metrics_invalid"

    return "unknown"


def _parse_trader_verdict_payload(value: Any) -> tuple[str, List[str], List[str], Optional[Dict[str, Any]]]:
    raw, parsed, parse_error = _parse_json_object(value)
    if parse_error:
        fallback = _verdict_label(raw)
        if fallback == "unknown":
            fallback = "needs_adjustment"
        diag = _mk_output_diag(
            node="trader",
            reason=parse_error,
            details={"raw_preview": raw[:600]},
        )
        return fallback, [], [], diag

    try:
        payload = TraderVerdictOutput.model_validate(parsed)
    except ValidationError as exc:
        fallback = _verdict_label(raw)
        if fallback == "unknown":
            fallback = "needs_adjustment"
        diag = _mk_output_diag(
            node="trader",
            reason="schema_validation_error",
            details={"errors": exc.errors()[:8], "raw_preview": raw[:600]},
        )
        return fallback, [], [], diag

    verdict = _normalize_str(payload.verdict).lower()
    if verdict not in ("approved", "rejected", "needs_adjustment", "metrics_invalid"):
        verdict = _verdict_label(raw)
        if verdict == "unknown":
            verdict = "needs_adjustment"

    reasons = _ensure_str_list(payload.reasons)
    required_fixes = _ensure_str_list(payload.required_fixes)
    if not required_fixes and reasons:
        # Hardening: reasons become retry guidance when required_fixes is absent.
        required_fixes = list(reasons)

    return verdict or "needs_adjustment", required_fixes, reasons, None


def _run_persona(
    *,
    state: LabGraphState,
    persona: str,
    system_prompt: str,
    output_key: str,
    message: Optional[str] = None,
) -> tuple[Dict[str, Any], Dict[str, Any], bool]:
    deps: LabGraphDeps = state.get("deps")
    if deps is None:
        raise RuntimeError("missing deps")

    run_id = state.get("run_id")
    budget = state.get("budget") or {}
    outputs = state.get("outputs") or {}

    if outputs.get(output_key):
        return budget, outputs, True

    if not deps.budget_ok(budget):
        deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "budget_limit", "data": budget})
        return budget, outputs, False

    if persona == "validator":
        ctx = state.get("context") or {}
        pre = ctx.get("metrics_preflight") or {}
        if isinstance(pre, dict) and pre.get("ok") is False:
            deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "node_started", "data": {"node": persona}})
            payload = {
                "verdict": "metrics_invalid",
                "reasons": ["metrics_preflight_failed"],
                "required_fixes": (pre.get("errors") or [])[:8],
                "notes": "Preflight determinístico falhou; bloqueando chamada ao validator LLM.",
            }
            outputs[output_key] = json.dumps(payload, ensure_ascii=False)
            deps.append_trace(
                run_id,
                {
                    "ts_ms": deps.now_ms(),
                    "type": "node_done",
                    "data": {"node": persona, "tokens": 0, "blocked_by": "metrics_preflight"},
                },
            )
            return budget, outputs, True

    deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "node_started", "data": {"node": persona}})

    msg = message or ("Contexto do run (JSON):\n" + json.dumps(state.get("context") or {}, ensure_ascii=False, indent=2) + "\n")
    timeout_s = _node_timeout_s(state)

    def _call_persona() -> Dict[str, Any]:
        try:
            return deps.persona_call(
                run_id=run_id,
                session_key=state.get("session_key"),
                persona=persona,
                system_prompt=system_prompt,
                message=msg,
                thinking=state.get("thinking") or "low",
                timeout_s=timeout_s,
            )
        except TypeError as exc:
            # Backward-compatible fallback for older test doubles/callables
            # that do not accept timeout_s.
            if "timeout_s" not in str(exc):
                raise
            return deps.persona_call(
                run_id=run_id,
                session_key=state.get("session_key"),
                persona=persona,
                system_prompt=system_prompt,
                message=msg,
                thinking=state.get("thinking") or "low",
            )

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_call_persona)
            response = future.result(timeout=timeout_s)
    except concurrent.futures.TimeoutError as exc:
        deps.append_trace(
            run_id,
            {
                "ts_ms": deps.now_ms(),
                "type": "node_timeout",
                "data": {"node": persona, "timeout_s": timeout_s},
            },
        )
        raise LabGraphNodeTimeoutError(node=persona, timeout_s=timeout_s) from exc
    except Exception as exc:
        deps.append_trace(
            run_id,
            {
                "ts_ms": deps.now_ms(),
                "type": "node_error",
                "data": {"node": persona, "error": str(exc)},
            },
        )
        raise

    outputs[output_key] = response.get("text")
    budget = deps.inc_budget(budget, turns=1, tokens=response.get("tokens", 0) or 0)

    deps.append_trace(
        run_id,
        {
            "ts_ms": deps.now_ms(),
            "type": "node_done",
            "data": {"node": persona, "tokens": response.get("tokens", 0) or 0},
        },
    )

    return budget, outputs, True


def _upstream_node(state: LabGraphState) -> LabGraphState:
    deps: LabGraphDeps = state.get("deps")
    if deps is None:
        raise RuntimeError("missing deps")

    run_id = state.get("run_id")
    deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "upstream_started", "data": {}})

    contract = build_upstream_contract(context=state.get("context") or {})

    deps.append_trace(
        run_id,
        {
            "ts_ms": deps.now_ms(),
            "type": "upstream_done",
            "data": {
                "approved": bool(contract.get("approved")),
                "missing": contract.get("missing") or [],
                "question": contract.get("question") or "",
            },
        },
    )

    if not contract.get("approved"):
        deps.append_trace(
            run_id,
            {
                "ts_ms": deps.now_ms(),
                "type": "final_decision",
                "data": {
                    "status": "needs_user_input",
                    "reason": "upstream_not_approved",
                    "missing": contract.get("missing") or [],
                },
            },
        )

    return {
        "upstream_contract": contract,
        "phase": "upstream",
        "status": "ready_for_execution" if bool(contract.get("approved")) else "needs_user_input",
    }


def _after_upstream(state: LabGraphState) -> str:
    contract = state.get("upstream_contract") or {}
    return "implementation" if bool(contract.get("approved")) else "end"


def _build_dev_retry_message(
    *,
    context: Dict[str, Any],
    required_fixes: List[str],
    trader_reasons: List[str],
) -> str:
    """Build a custom message for Dev Senior including Trader feedback."""
    fixes_text = "\n".join([f"{i+1}. {fix}" for i, fix in enumerate(required_fixes)]) or "(nenhum)"
    reasons_text = "\n".join([f"{i+1}. {reason}" for i, reason in enumerate(trader_reasons)]) or "(não informado)"

    message = f"""O Trader rejeitou a estratégia anterior pelos seguintes motivos:
{reasons_text}

AJUSTES REQUERIDOS (implemente no novo template):
{fixes_text}

Contexto completo do run:
"""
    message += json.dumps(context, ensure_ascii=False, indent=2)
    message += "\n\nGere um NOVO template de estratégia implementando os ajustes acima. NÃO apenas otimize parâmetros - faça as mudanças estruturais solicitadas."

    return message


def _implementation_node(state: LabGraphState) -> LabGraphState:
    deps: LabGraphDeps = state.get("deps")
    if deps is None:
        raise RuntimeError("missing deps")

    run_id = state.get("run_id")
    deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "implementation_started", "data": {}})

    state["phase"] = "implementation"
    state["implementation_rounds"] = int(state.get("implementation_rounds") or 0) + 1

    budget, outputs, ok = _run_persona(
        state=state,
        persona="coordinator",
        output_key="coordinator_summary",
        system_prompt=COORDINATOR_PROMPT,
    )
    state["budget"] = budget
    state["outputs"] = outputs

    if ok:
        # Check if this is a retry with trader feedback
        outputs = state.get("outputs") or {}
        context = state.get("context") or {}
        
        if outputs.get("dev_needs_retry") and outputs.get("trader_verdict"):
            # Extract trader feedback
            verdict_obj = outputs.get("trader_verdict")
            verdict, required_fixes, reasons, trader_diag = _parse_trader_verdict_payload(verdict_obj)
            if trader_diag:
                state["diagnostic"] = trader_diag
                deps.append_trace(
                    run_id,
                    {
                        "ts_ms": deps.now_ms(),
                        "type": "invalid_output",
                        "data": trader_diag,
                    },
                )

            # Build custom message with trader feedback
            message = _build_dev_retry_message(
                context=context,
                required_fixes=required_fixes,
                trader_reasons=reasons,
            )
            
            deps.append_trace(
                run_id,
                {
                    "ts_ms": deps.now_ms(),
                    "type": "dev_retry_with_trader_feedback",
                    "data": {
                        "verdict": verdict,
                        "required_fixes": required_fixes,
                        "reasons": reasons,
                    },
                },
            )
            
            budget, outputs, ok = _run_persona(
                state=state,
                persona="dev_senior",
                output_key="dev_summary",
                system_prompt=DEV_SENIOR_PROMPT,
                message=message,  # Custom message with trader feedback
            )
        else:
            # Normal flow
            budget, outputs, ok = _run_persona(
                state=state,
                persona="dev_senior",
                output_key="dev_summary",
                system_prompt=DEV_SENIOR_PROMPT,
            )
        
        state["budget"] = budget
        state["outputs"] = outputs

    completed = bool(outputs.get("coordinator_summary") and outputs.get("dev_summary"))

    # Require real backtest metrics and a job_id before trader validation.
    needs_retry = False
    context = state.get("context") or {}
    wf = context.get("walk_forward") or {}

    def _ctx_trades(metrics: Any) -> int:
        if not isinstance(metrics, dict):
            return 0
        return int(metrics.get("total_trades") or 0)

    in_sample = wf.get("metrics_in_sample") or {}
    holdout = wf.get("metrics_holdout") or {}
    if _ctx_trades(in_sample) == 0 or _ctx_trades(holdout) == 0:
        needs_retry = True

    backtest_job_id = str(context.get("backtest_job_id") or "").strip()
    backtest_job_status = str(context.get("backtest_job_status") or "").strip().upper()
    if not backtest_job_id or (backtest_job_status and backtest_job_status != "COMPLETED"):
        needs_retry = True

    if needs_retry:
        completed = False
        outputs["dev_needs_retry"] = True

    # Ensure dev used the same backtest job id from context and template is valid.
    ctx_job_id = str(context.get("backtest_job_id") or "").strip()
    dev_job_id = ""
    diagnostic = state.get("diagnostic") if isinstance(state.get("diagnostic"), dict) else None
    dev_summary_raw = outputs.get("dev_summary")
    if dev_summary_raw:
        raw, dev_obj_raw, parse_error = _parse_json_object(dev_summary_raw)
        dev_obj: Dict[str, Any] = {}
        if parse_error:
            dev_job_id = ""
            completed = False
            outputs["dev_needs_retry"] = True
            outputs["dev_summary"] = None
            diagnostic = _mk_output_diag(
                node="dev_senior",
                reason=parse_error,
                details={"raw_preview": raw[:600]},
            )
            deps.append_trace(
                run_id,
                {"ts_ms": deps.now_ms(), "type": "dev_summary_rejected", "data": {"reason": parse_error}},
            )
        else:
            try:
                parsed_dev = DevSummaryOutput.model_validate(dev_obj_raw)
                dev_obj = parsed_dev.model_dump()
            except ValidationError as exc:
                dev_job_id = ""
                completed = False
                outputs["dev_needs_retry"] = True
                outputs["dev_summary"] = None
                diagnostic = _mk_output_diag(
                    node="dev_senior",
                    reason="schema_validation_error",
                    details={"errors": exc.errors()[:8], "raw_preview": raw[:600]},
                )
                deps.append_trace(
                    run_id,
                    {
                        "ts_ms": deps.now_ms(),
                        "type": "dev_summary_rejected",
                        "data": {"reason": "schema_validation_error"},
                    },
                )
            else:
                dev_job_id = str(dev_obj.get("backtest_job_id") or "").strip()
                template_data = dev_obj.get("template_data") or {}
                entry_logic = template_data.get("entry_logic")
                exit_logic = template_data.get("exit_logic")
                if not isinstance(entry_logic, str) or not isinstance(exit_logic, str):
                    completed = False
                    outputs["dev_needs_retry"] = True

                # Reject if dev did not provide a job_id.
                if not dev_job_id:
                    completed = False
                    outputs["dev_needs_retry"] = True
                    outputs["dev_summary"] = None
                    deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "dev_summary_rejected", "data": {"reason": "missing_job_id"}})

                # Validate that dev used real metrics from context (not invented).
                dev_metrics = dev_obj.get("backtest_summary") or {}
                ctx_metrics = (context.get("walk_forward") or {})
                ctx_all = (ctx_metrics.get("metrics_all") or {})
                ctx_is = (ctx_metrics.get("metrics_in_sample") or {})
                ctx_holdout = (ctx_metrics.get("metrics_holdout") or {})

                def _mt(m):
                    try:
                        return int((m or {}).get("total_trades") or 0)
                    except Exception:
                        return 0

                if not dev_metrics:
                    completed = False
                    outputs["dev_needs_retry"] = True
                    outputs["dev_summary"] = None
                    deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "dev_summary_rejected", "data": {"reason": "missing_backtest_summary"}})
                else:
                    dev_all = dev_metrics.get("all") or {}
                    dev_is = dev_metrics.get("in_sample") or {}
                    dev_holdout = dev_metrics.get("holdout") or {}
                    if _mt(dev_all) != _mt(ctx_all) or _mt(dev_is) != _mt(ctx_is) or _mt(dev_holdout) != _mt(ctx_holdout):
                        completed = False
                        outputs["dev_needs_retry"] = True
                        outputs["dev_summary"] = None
                        deps.append_trace(
                            run_id,
                            {
                                "ts_ms": deps.now_ms(),
                                "type": "dev_summary_rejected",
                                "data": {
                                    "reason": "metrics_mismatch",
                                    "ctx_trades": {"all": _mt(ctx_all), "is": _mt(ctx_is), "holdout": _mt(ctx_holdout)},
                                    "dev_trades": {"all": _mt(dev_all), "is": _mt(dev_is), "holdout": _mt(dev_holdout)},
                                },
                            },
                        )

    if ctx_job_id and dev_job_id and dev_job_id != ctx_job_id:
        completed = False
        outputs["dev_needs_retry"] = True
        outputs["dev_summary"] = None
        deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "dev_summary_rejected", "data": {"reason": "job_id_mismatch", "ctx_job_id": ctx_job_id, "dev_job_id": dev_job_id}})

    deps.append_trace(
        run_id,
        {
            "ts_ms": deps.now_ms(),
            "type": "implementation_done",
            "data": {
                "completed": completed,
                "budget_ok": deps.budget_ok(budget),
            },
        },
    )

    return {
        "budget": budget,
        "outputs": outputs,
        "phase": "implementation",
        "implementation_complete": completed,
        "implementation_rounds": int(state.get("implementation_rounds") or 0),
        "status": "running" if completed else "needs_adjustment",
        "diagnostic": diagnostic or {},
    }


def _after_implementation(state: LabGraphState) -> str:
    return "tests" if bool(state.get("implementation_complete")) else "end"


def _build_trader_validation_message(
    *,
    strategy_draft: Optional[Dict[str, Any]],
    dev_summary: Optional[str],
    context: Dict[str, Any],
) -> str:
    payload = {
        "strategy_draft": strategy_draft,
        "dev_summary": dev_summary,
        "metrics": context.get("walk_forward") or {},
        "template": context.get("template"),
        "symbol": context.get("symbol"),
        "timeframe": context.get("timeframe"),
    }
    return "Contexto para validação do Trader (JSON):\n" + json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _trader_validation_node(state: LabGraphState) -> LabGraphState:
    deps: LabGraphDeps = state.get("deps")
    if deps is None:
        raise RuntimeError("missing deps")

    run_id = state.get("run_id")
    deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "trader_validation_started", "data": {}})

    budget = state.get("budget") or {}
    outputs = state.get("outputs") or {}
    context = state.get("context") or {}
    upstream = state.get("upstream_contract") or {}

    message = _build_trader_validation_message(
        strategy_draft=upstream.get("strategy_draft"),
        dev_summary=outputs.get("dev_summary"),
        context=context,
    )

    budget, outputs, ok = _run_persona(
        state=state,
        persona="trader",
        output_key="trader_verdict",
        system_prompt=TRADER_VALIDATION_PROMPT,
        message=message,
    )

    state["budget"] = budget
    state["outputs"] = outputs

    verdict_obj = outputs.get("trader_verdict")
    verdict, required_fixes, reasons, verdict_diag = _parse_trader_verdict_payload(verdict_obj)
    diagnostic = state.get("diagnostic") if isinstance(state.get("diagnostic"), dict) else {}
    if verdict_diag:
        diagnostic = verdict_diag
        deps.append_trace(
            run_id,
            {"ts_ms": deps.now_ms(), "type": "invalid_output", "data": verdict_diag},
        )
    status = "needs_adjustment"
    if verdict == "approved":
        status = "approved"
    elif verdict == "rejected":
        status = "rejected"

    try:
        trader_retry_count = int(state.get("trader_retry_count") or outputs.get("trader_retry_count") or 0)
    except Exception:
        trader_retry_count = 0
    if trader_retry_count < 0:
        trader_retry_count = 0
    outputs["trader_retry_count"] = trader_retry_count
    outputs.pop("dev_needs_retry", None)

    try:
        max_retries = int(((context.get("input") or {}).get("max_retries") or 2))
    except Exception:
        max_retries = 2
    if max_retries < 0:
        max_retries = 0

    retry_fixes = required_fixes or reasons
    if verdict in ("rejected", "needs_adjustment") and retry_fixes:
        if trader_retry_count < max_retries:
            trader_retry_count += 1
            outputs["trader_retry_count"] = trader_retry_count
            outputs["dev_needs_retry"] = True
            deps.append_trace(
                run_id,
                {
                    "ts_ms": deps.now_ms(),
                    "type": "trader_retry_started",
                    "data": {
                        "attempt": trader_retry_count,
                        "limit": max_retries,
                        "required_fixes": retry_fixes,
                        "reasons": reasons,
                    },
                },
            )
            status = "needs_adjustment"
        else:
            deps.append_trace(
                run_id,
                {
                    "ts_ms": deps.now_ms(),
                    "type": "trader_retry_limit",
                    "data": {
                        "attempt": trader_retry_count,
                        "limit": max_retries,
                        "required_fixes": retry_fixes,
                        "reasons": reasons,
                    },
                },
            )
            status = "needs_adjustment"

    # Auto-save when approved (no human confirmation needed)
    if verdict == "approved":
        try:
            # Import and call autosave function from lab.py
            import importlib.util
            spec = importlib.util.spec_from_file_location("lab", "/root/.openclaw/workspace/crypto/backend/app/routes/lab.py")
            lab_module = importlib.util.module_from_spec(spec)
            # Use the existing autosave logic via a simplified approach
            # The autosave will be handled by the graph completion in lab.py
            deps.append_trace(
                run_id,
                {
                    "ts_ms": deps.now_ms(),
                    "type": "trader_approved_autosave",
                    "data": {"verdict": verdict},
                },
            )
        except Exception as e:
            deps.append_trace(
                run_id,
                {
                    "ts_ms": deps.now_ms(),
                    "type": "trader_approved_autosave_error",
                    "data": {"error": str(e)},
                },
            )

    deps.append_trace(
        run_id,
        {
            "ts_ms": deps.now_ms(),
            "type": "trader_validation_done",
            "data": {"verdict": verdict, "budget_ok": deps.budget_ok(budget)},
        },
    )

    return {
        "budget": budget,
        "outputs": outputs,
        "phase": "trader_validation",
        "status": status,
        "trader_retry_count": trader_retry_count,
        "diagnostic": diagnostic,
    }



def _after_trader_validation(state: LabGraphState) -> str:
    status = state.get("status") or ""
    if status in ("approved", "rejected", "needs_user_confirm"):
        return "end"
    if status == "needs_adjustment":
        outputs = state.get("outputs") or {}
        if bool(outputs.get("dev_needs_retry")):
            return "dev_implementation"

        context = state.get("context") or {}
        try:
            max_retries = int(((context.get("input") or {}).get("max_retries") or 2))
        except Exception:
            max_retries = 2
        if max_retries < 0:
            max_retries = 0
        try:
            trader_retry_count = int(state.get("trader_retry_count") or outputs.get("trader_retry_count") or 0)
        except Exception:
            trader_retry_count = 0
        if trader_retry_count >= max_retries:
            return "end"
    return "dev_implementation"



def _tests_node(state: LabGraphState) -> LabGraphState:
    deps: LabGraphDeps = state.get("deps")
    if deps is None:
        raise RuntimeError("missing deps")

    run_id = state.get("run_id")
    outputs = state.get("outputs") or {}
    context = state.get("context") or {}

    deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "tests_started", "data": {}})

    preflight = context.get("metrics_preflight") or {}
    preflight_ok = not isinstance(preflight, dict) or bool(preflight.get("ok", True))
    verdict = _verdict_label(outputs.get("trader_verdict") or outputs.get("validator_verdict"))

    tests_pass = bool(preflight_ok)
    if verdict == "metrics_invalid":
        tests_pass = False

    tests_result = {
        "pass": tests_pass,
        "preflight_ok": preflight_ok,
        "validator_verdict": verdict,
        "errors": (preflight.get("errors") if isinstance(preflight, dict) else []) or [],
    }
    outputs["tests_done"] = tests_result

    deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "tests_done", "data": tests_result})

    return {
        "outputs": outputs,
        "phase": "tests",
        "tests_result": tests_result,
    }


def _final_decision_node(state: LabGraphState) -> LabGraphState:
    deps: LabGraphDeps = state.get("deps")
    if deps is None:
        raise RuntimeError("missing deps")

    run_id = state.get("run_id")
    outputs = state.get("outputs") or {}

    tests_result = state.get("tests_result") or outputs.get("tests_done") or {}
    tests_pass = bool((tests_result or {}).get("pass"))
    status = "done" if tests_pass else "failed"

    decision = {
        "status": status,
        "tests_pass": tests_pass,
        "upstream_approved": bool((state.get("upstream_contract") or {}).get("approved")),
    }
    outputs["final_decision"] = decision

    deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "final_decision", "data": decision})

    return {
        "outputs": outputs,
        "phase": "done",
        "status": status,
    }


def build_trader_dev_graph() -> CompiledStateGraph:
    """Build the trader-driven lab graph (Trader → Dev → Trader)."""

    graph = StateGraph(LabGraphState)

    graph.add_node("upstream", _upstream_node)
    graph.add_node("dev_implementation", _implementation_node)
    graph.add_node("trader_validation", _trader_validation_node)

    graph.set_entry_point("upstream")

    graph.add_conditional_edges(
        "upstream",
        _after_upstream,
        {
            "implementation": "dev_implementation",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "dev_implementation",
        lambda state: (
            "trader_validation"
            if bool((state.get("outputs") or {}).get("dev_summary"))
            and not bool((state.get("outputs") or {}).get("dev_needs_retry"))
            else ("dev_implementation" if int(state.get("implementation_rounds") or 0) < int((state.get("context") or {}).get("input", {}).get("max_iterations") or 3) else "end")
        ),
        {
            "trader_validation": "trader_validation",
            "dev_implementation": "dev_implementation",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "trader_validation",
        _after_trader_validation,
        {
            "dev_implementation": "dev_implementation",
            "end": END,
        },
    )

    return graph.compile()


def build_cp7_graph() -> CompiledStateGraph:
    """Deprecated: kept for backward compatibility."""

    return build_trader_dev_graph()


COORDINATOR_PROMPT = (
    "Papel: Coordinator (Agile Coach)\n"
    "Você NÃO gera resumos automáticos.\n\n"
    "Só intervém quando:\n"
    "- Dev ou Trader reportam explicitamente uma dúvida/impasse\n"
    "- Contexto indica bloqueio (ex: 3+ iterações sem progresso)\n\n"
    "Quando intervir:\n"
    "- Facilite comunicação entre Dev e Trader\n"
    "- Sugira compromissos técnicos vs negócio\n"
    "- Mantenha foco nos critérios de aceite do upstream\n\n"
    "Responda JSON:\n"
    "{\n"
    "  \"needs_intervention\": true | false,\n"
    "  \"facilitation\": \"...\"\n"
    "}\n\n"
    "Default: needs_intervention=false.\n"
    "Idioma: pt-BR."
)

DEV_SENIOR_PROMPT = (
    "Papel: Dev (Dev Sênior)\n"
    "Você implementa estratégias de trading propostas pelo Trader.\n\n"
    "Workflow:\n"
    "1. Ler strategy_draft do contexto.\n"
    "2. Criar template técnico (schema do engine).\n"
    "3. Rodar backtest usando funções disponíveis.\n"
    "4. Diagnosticar problemas (0 trades, colunas inválidas, bugs).\n"
    "5. Iterar até ter resultado tecnicamente válido (máx. 5 iterações).\n"
    "6. Entregar template + métricas para Trader validar.\n\n"
    "Entregável (JSON válido):\n"
    "{\n"
    "  \"template_name\": \"...\",\n"
    "  \"template_data\": { indicators, entry_logic, exit_logic, stop_loss },\n"
    "  (entry_logic e exit_logic DEVEM ser strings, nunca dict)\n"
    "  \"backtest_job_id\": \"...\",\n"
    "  \"backtest_summary\": { all, in_sample, holdout },\n"
    "  \"iterations_done\": N,\n"
    "  \"technical_notes\": \"...\",\n"
    "  \"ready_for_trader\": true\n"
    "}\n\n"
    "Regras estruturais (obrigatórias):\n"
    "- Máximo de 4 indicadores\n"
    "- Cada indicador: type, alias, params\n"
    "- Use apenas colunas válidas (bb_upper, adx, atr, close, etc.)\n"
    "- entry_logic/exit_logic DEVEM ser expressões booleanas válidas\n"
    "  (ex: rsi14 > 55 AND close > ema50).\n"
    "- NÃO use texto livre (ex: 'cruza acima', 'quando', 'retorna').\n"
    "- stop_loss DEVE ser número (float), nunca string.\n\n"
    "Auto-checagem obrigatória:\n"
    "Antes de responder, valide sua própria saída. Se houver qualquer\n"
    "palavra de texto livre em entry/exit (ex: cruza, quando, retorna),\n"
    "reescreva para comparação numérica válida.\n\n"
    "IMPORTANTE: Se strategy_draft presente no contexto, USE-O como base.\n"
    "PROIBIDO inventar métricas. Use somente os resultados reais do backtest do contexto.\n"
    "Ferramentas disponíveis para você: criar templates, codificar, rodar backtests e testar.\n"
    "O backtest já é executado pelo sistema e o backtest_job_id + métricas estão no contexto — use-os.\n"
    "Se o backtest_job_id estiver vazio ou não bater com o contexto, sua resposta será descartada.\n"
    "Se as métricas não baterem com o contexto, sua resposta será descartada.\n"
    "NUNCA diga que não tem acesso às ferramentas.\n"
    "Responda sempre com JSON válido no schema acima (sem texto fora do JSON).\n"
    "Se não houver trades, explique isso e marque ready_for_trader=false.\n"
    "Idioma: pt-BR."
)

TRADER_VALIDATION_PROMPT = (
    "Papel: Trader (Profissional de Mercado Financeiro)\n"
    "Você é o MESMO trader que propôs a estratégia no upstream.\n\n"
    "Contexto:\n"
    "- Você propôs uma estratégia (strategy_draft).\n"
    "- User aprovou.\n"
    "- Dev implementou e rodou backtest.\n\n"
    "Agora você deve validar o resultado:\n"
    "1. Alinhamento com a proposta original\n"
    "2. Métricas de holdout (Sharpe, drawdown)\n"
    "3. Robustez (sem overfitting grave)\n\n"
    "Responda EXCLUSIVAMENTE com JSON válido:\n"
    "{\n"
    "  \"verdict\": \"approved\" | \"needs_adjustment\" | \"rejected\",\n"
    "  \"reasons\": [\"...\"],\n"
    "  \"required_fixes\": [\"...\"],\n"
    "  \"feedback_for_dev\": \"...\"\n"
    "}\n\n"
    "Idioma: pt-BR."
)
