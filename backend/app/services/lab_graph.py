"""Lab v2: LangGraph workflow (CP7 minimal).

This module defines a small LangGraph that runs 3 nodes:
- coordinator
- dev_senior
- validator

Each node delegates to OpenClaw via the existing gateway client.

We intentionally keep it minimal for CP7:
- sequential nodes
- trace events for node start/end
- updates run outputs + budget

CP8+ will add template patch tools, job pipeline, etc.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph


class LabGraphState(TypedDict, total=False):
    run_id: str
    session_key: str
    thinking: str
    context: Dict[str, Any]

    budget: Dict[str, Any]
    outputs: Dict[str, Any]


@dataclass
class LabGraphDeps:
    persona_call: Any  # callable
    append_trace: Any  # callable
    now_ms: Any  # callable
    inc_budget: Any  # callable
    budget_ok: Any  # callable


def _node_factory(*, persona: str, system_prompt: str, output_key: str):
    def _node(state: LabGraphState, config: Dict[str, Any]) -> LabGraphState:
        deps: LabGraphDeps = (config or {}).get("deps")
        if deps is None:
            raise RuntimeError("missing deps")

        run_id = state.get("run_id")
        budget = state.get("budget") or {}
        outputs = state.get("outputs") or {}

        if outputs.get(output_key):
            return {"budget": budget, "outputs": outputs}

        if not deps.budget_ok(budget):
            deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "budget_limit", "data": budget})
            return {"budget": budget, "outputs": outputs}

        deps.append_trace(run_id, {"ts_ms": deps.now_ms(), "type": "node_started", "data": {"node": persona}})

        msg = (
            "Contexto do run (JSON):\n"
            + json.dumps(state.get("context") or {}, ensure_ascii=False, indent=2)
            + "\n"
        )

        r = deps.persona_call(
            run_id=run_id,
            session_key=state.get("session_key"),
            persona=persona,
            system_prompt=system_prompt,
            message=msg,
            thinking=state.get("thinking") or "low",
        )

        outputs[output_key] = r.get("text")
        budget = deps.inc_budget(budget, turns=1, tokens=r.get("tokens", 0) or 0)

        deps.append_trace(
            run_id,
            {
                "ts_ms": deps.now_ms(),
                "type": "node_done",
                "data": {"node": persona, "tokens": r.get("tokens", 0) or 0},
            },
        )

        return {"budget": budget, "outputs": outputs}

    return _node


def build_cp7_graph() -> CompiledStateGraph:
    g = StateGraph(LabGraphState)

    g.add_node(
        "coordinator",
        _node_factory(
            persona="coordinator",
            output_key="coordinator_summary",
            system_prompt=(
                "Você é o Coordenador do Strategy Lab. Resuma o que foi feito e proponha próximos passos. "
                "Responda em pt-BR, curto e objetivo."
            ),
        ),
    )

    g.add_node(
        "dev_senior",
        _node_factory(
            persona="dev_senior",
            output_key="dev_summary",
            system_prompt=(
                "Você é um Dev Sênior focado em templates/estratégias do Crypto Backtester. "
                "Sugira melhorias de template sem quebrar o sistema. Responda em pt-BR."
            ),
        ),
    )

    g.add_node(
        "validator",
        _node_factory(
            persona="validator",
            output_key="validator_verdict",
            system_prompt=(
                "Você é um Trader/Validador. Avalie robustez e riscos (sem lookahead, custos, overfit). "
                "Use principalmente o HOLDOUT (30% mais recente) para o veredito. "
                "Dê veredito 'approved' ou 'rejected' com motivos. Responda em pt-BR."
            ),
        ),
    )

    g.set_entry_point("coordinator")
    g.add_edge("coordinator", "dev_senior")
    g.add_edge("dev_senior", "validator")
    g.add_edge("validator", END)

    return g.compile()
