"""Lab graph with mandatory upstream + implementation/tests phases.

This module keeps a single LangGraph workflow and introduces a deterministic
upstream contract before implementation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph


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


@dataclass
class LabGraphDeps:
    persona_call: Any  # callable
    append_trace: Any  # callable
    now_ms: Any  # callable
    inc_budget: Any  # callable
    budget_ok: Any  # callable


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
            if verdict in ("approved", "rejected", "metrics_invalid"):
                return verdict
        except Exception:
            pass

    if "rejected" in lower or "reprovado" in lower:
        return "rejected"
    if "approved" in lower or "aprovado" in lower:
        return "approved"
    if "metrics_invalid" in lower:
        return "metrics_invalid"

    return "unknown"


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

    response = deps.persona_call(
        run_id=run_id,
        session_key=state.get("session_key"),
        persona=persona,
        system_prompt=system_prompt,
        message=msg,
        thinking=state.get("thinking") or "low",
    )

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
        "status": "implementation_running" if bool(contract.get("approved")) else "needs_user_input",
    }


def _after_upstream(state: LabGraphState) -> str:
    contract = state.get("upstream_contract") or {}
    return "implementation" if bool(contract.get("approved")) else "end"


def _implementation_node(state: LabGraphState) -> LabGraphState:
    deps: LabGraphDeps = state.get("deps")
    if deps is None:
        raise RuntimeError("missing deps")

    run_id = state.get("run_id")
    deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "implementation_started", "data": {}})

    state["phase"] = "implementation"

    budget, outputs, ok = _run_persona(
        state=state,
        persona="coordinator",
        output_key="coordinator_summary",
        system_prompt=COORDINATOR_PROMPT,
    )
    state["budget"] = budget
    state["outputs"] = outputs

    if ok:
        budget, outputs, ok = _run_persona(
            state=state,
            persona="dev_senior",
            output_key="dev_summary",
            system_prompt=DEV_SENIOR_PROMPT,
        )
        state["budget"] = budget
        state["outputs"] = outputs

    completed = bool(outputs.get("coordinator_summary") and outputs.get("dev_summary"))

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
        "status": "implementation_running" if completed else "needs_user_confirm",
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
    verdict = _verdict_label(verdict_obj)
    status = "needs_adjustment"
    if verdict == "approved":
        status = "approved"
    elif verdict == "rejected":
        status = "rejected"

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
    }



def _after_trader_validation(state: LabGraphState) -> str:
    status = state.get("status") or ""
    if status == "approved" or status == "rejected":
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
        lambda state: "trader_validation" if bool((state.get("outputs") or {}).get("dev_summary")) else "end",
        {
            "trader_validation": "trader_validation",
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
    "  \"backtest_summary\": { all, in_sample, holdout },\n"
    "  \"iterations_done\": N,\n"
    "  \"technical_notes\": \"...\",\n"
    "  \"ready_for_trader\": true\n"
    "}\n\n"
    "Regras estruturais:\n"
    "- Máximo de 4 indicadores\n"
    "- Cada indicador: type, alias, params\n"
    "- Use apenas colunas válidas (bb_upper, adx, atr, close, etc.)\n\n"
    "IMPORTANTE: Se strategy_draft presente no contexto, USE-O como base.\n"
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
    "  \"feedback_for_dev\": \"...\"\n"
    "}\n\n"
    "Idioma: pt-BR."
)
