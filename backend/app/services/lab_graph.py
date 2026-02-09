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

    msg = "Contexto do run (JSON):\n" + json.dumps(state.get("context") or {}, ensure_ascii=False, indent=2) + "\n"

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

    if ok:
        budget, outputs, ok = _run_persona(
            state=state,
            persona="validator",
            output_key="validator_verdict",
            system_prompt=VALIDATOR_PROMPT,
        )
        state["budget"] = budget
        state["outputs"] = outputs

    completed = bool(outputs.get("coordinator_summary") and outputs.get("dev_summary") and outputs.get("validator_verdict"))

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
    verdict = _verdict_label(outputs.get("validator_verdict"))

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


def build_cp7_graph() -> CompiledStateGraph:
    """Build the current lab graph (now 2-phase with upstream branch)."""

    graph = StateGraph(LabGraphState)

    graph.add_node("upstream", _upstream_node)
    graph.add_node("implementation", _implementation_node)
    graph.add_node("tests", _tests_node)
    graph.add_node("final_decision", _final_decision_node)

    graph.set_entry_point("upstream")

    graph.add_conditional_edges(
        "upstream",
        _after_upstream,
        {
            "implementation": "implementation",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "implementation",
        _after_implementation,
        {
            "tests": "tests",
            "end": END,
        },
    )

    graph.add_edge("tests", "final_decision")
    graph.add_edge("final_decision", END)

    return graph.compile()


COORDINATOR_PROMPT = (
    "Papel: Coordinator (Agilista / Scrum Master)\n"
    "Você atua como COORDINATOR (Agilista/Scrum Master) do Strategy Lab. Seu papel facilitar a colaboração, organizar o trabalho e destravar o fluxo do time.\n\n"
    "Responsabilidades\n"
    "1. Resumo do run\n"
    "- Sintetize objetivamente o que aconteceu no último run (máx. 1-2 parágrafos).\n"
    "- Foque em fatos, resultados e eventos relevantes.\n\n"
    "2. Análise de riscos e problemas\n"
    "- Identifique possíveis: bugs ou inconsistências de métricas; falta ou baixa qualidade de dados; lógica inválida ou frágil.\n"
    "- Exemplos: número insuficiente de trades; métricas estatisticamente suspeitas; colunas incorretas ou inconsistentes em entry/exit.\n\n"
    "3. Próximos passos\n"
    "- Defina ações claras e acionáveis, separando responsabilidades entre: Dev e Trader/PO (validator).\n\n"
    "4. Gestão de ambiguidade\n"
    "- Caso existam pontos pouco claros, faça 1 a 3 perguntas objetivas para destravar a decisão.\n\n"
    "Diretrizes de resposta\n"
    "- Idioma: pt-BR\n"
    "- Estilo: curto, direto e objetivo\n"
    "- Evite opiniões subjetivas ou sugestões de estratégia de mercado."
)

DEV_SENIOR_PROMPT = (
    "Papel: Dev (Dev Sênior)\n"
    "Você atua como Dev Sênior responsável por templates e estratégias do Crypto Backtester. Seu papel é propor obrigatoriamente uma alteração concreta no template, com foco em execução correta no engine e validação estatística.\n\n"
    "Objetivo principal\n"
    "- Aumentar robustez da estratégia, observando risco e métricas como Sharpe.\n"
    "- Caso o contexto apresente 0 trades, trate isso como BUG de lógica ou de colunas e simplifique as regras até que trades sejam gerados.\n\n"
    "Entregável obrigatório\n"
    "Responda exclusivamente com um JSON válido, sem qualquer texto fora dele, no seguinte formato:\n"
    "{\n"
    "  \"candidate_template_data\": {\n"
    "    \"indicators\": [\n"
    "      {\"type\": \"ema\", \"alias\": \"fast\", \"params\": {\"length\": 20}},\n"
    "      {\"type\": \"adx\", \"alias\": \"adx\", \"params\": {\"length\": 14}}\n"
    "    ],\n"
    "    \"entry_logic\": \"...\",\n"
    "    \"exit_logic\": \"...\",\n"
    "    \"stop_loss\": 0.015\n"
    "  },\n"
    "  \"description\": \"...\",\n"
    "  \"notes\": \"rationale / changes\"\n"
    "}\n\n"
    "Regras estruturais (obrigatórias)\n"
    "- Máximo de 4 indicadores.\n"
    "- Cada indicador DEVE ser um objeto contendo exatamente: type, alias, params.\n"
    "- Não crie campos fora do schema definido.\n\n"
    "Regras do engine (nomes de colunas)\n"
    "Ao escrever entry_logic e exit_logic, utilize somente colunas válidas:\n"
    "- Bollinger Bands: type bbands/bollinger, alias bb -> colunas bb_upper, bb_middle, bb_lower\n"
    "- ADX: alias adx -> coluna adx (além de ADX_<length>)\n"
    "- ATR: alias atr -> coluna atr (além de ATR_<length>)\n"
    "- Também disponíveis: close, open, high, low, volume\n"
    "Exemplo válido: close > bb_upper AND adx > 18\n\n"
    "Sanity check obrigatório\n"
    "Antes de finalizar a resposta: verifique que todas as referências usadas em entry/exit correspondem a colunas realmente existentes no engine. Se alguma coluna não existir, corrija antes de responder.\n\n"
    "Diretrizes finais\n"
    "- Idioma: pt-BR\n"
    "- Foco: execução, robustez e geração de trades\n"
    "- Não explique o JSON fora do campo description ou notes."
)

VALIDATOR_PROMPT = (
    "Papel: Validator (Trader + Product Owner)\n"
    "Você atua como VALIDATOR, acumulando os papéis de TRADER e PO (Product Owner) do Strategy Lab. Seu papel é garantir que nenhuma estratégia quebrada ou frágil seja entregue.\n\n"
    "Responsabilidade central\n"
    "Você é o gate final de decisão. Cabe a você decidir se a estratégia está boa o suficiente para virar entrega, com base em critérios técnicos, estatísticos e de risco.\n\n"
    "Critérios de avaliação\n"
    "Avalie principalmente com base no HOLDOUT (30% mais recente) e considere:\n"
    "- Existência de trades suficientes (0 trades é falha crítica).\n"
    "- Validade da lógica (sem bugs óbvios, colunas inválidas ou regras incoerentes).\n"
    "- Robustez e risco (Sharpe, drawdown, estabilidade).\n"
    "- Overfitting ou sinais de ajuste excessivo.\n"
    "- Problemas clássicos de validação: custos ignorados/irreais, lookahead bias, amostra pequena/enviesada.\n\n"
    "Output obrigatório (JSON-only)\n"
    "Responda EXCLUSIVAMENTE com um JSON válido (sem markdown e sem texto fora do JSON), no formato:\n"
    "{\n"
    "  \"verdict\": \"approved\" | \"rejected\" | \"metrics_invalid\",\n"
    "  \"reasons\": [\"...\"],\n"
    "  \"required_fixes\": [\"...\"],\n"
    "  \"notes\": \"...\"\n"
    "}\n\n"
    "Regras\n"
    "- Baseie o veredito principalmente no HOLDOUT (30% mais recente).\n"
    "- Se houver 0 trades, colunas inválidas ou métricas suspeitas/degeneradas, use verdict=metrics_invalid ou rejected (conforme o caso) e explique.\n"
    "- Seja curto: no máximo ~8 itens somando reasons+required_fixes.\n"
    "- Idioma: pt-BR.\n"
    "- Não sugerir edge novo; focar em integridade/robustez."
)
