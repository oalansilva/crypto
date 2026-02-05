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

    # runtime deps (in-process only)
    deps: Any

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
    def _node(state: LabGraphState) -> LabGraphState:
        deps: LabGraphDeps = state.get("deps")
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
                "Você é o COORDINATOR (Agilista/Scrum Master) do Strategy Lab. "
                "Seu papel NÃO é propor edge de mercado; é facilitar a colaboração, organizar o trabalho e destravar o fluxo.\n\n"
                "Tarefas:\n"
                "- Resumir o que aconteceu no run de forma objetiva (1-2 parágrafos).\n"
                "- Identificar riscos/bugs de métrica, falta de dados OU lógica inválida (ex.: poucos trades, métricas suspeitas, nomes de colunas errados no entry/exit).\n"
                "- Definir próximos passos acionáveis para Dev e Trader/PO (validator).\n"
                "- Se houver ambiguidade, faça 1-3 perguntas curtas.\n\n"
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
                "Você DEVE propor uma alteração concreta no template. Responda em pt-BR.\n\n"
                "FORMATO OBRIGATÓRIO: responda com um JSON válido (apenas JSON, sem texto fora) no formato:\n"
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
                "REGRAS: no máximo 4 indicadores. Cada indicador DEVE ser objeto com type/alias/params. Não invente campos fora desses.\n\n"
                "IMPORTANTE (nomes de colunas no engine):\n"
                "- Se usar bbands/bollinger com alias 'bb', as colunas ficam: bb_upper, bb_middle, bb_lower.\n"
                "- Se usar adx com alias 'adx', a coluna 'adx' estará disponível (além de ADX_<len>).\n"
                "- Se usar atr com alias 'atr', a coluna 'atr' estará disponível (além de ATR_<len>).\n"
                "Então escreva entry/exit usando essas colunas (ex.: close > bb_upper AND adx > 18)."
            ),
        ),
    )

    g.add_node(
        "validator",
        _node_factory(
            persona="validator",
            output_key="validator_verdict",
            system_prompt=(
                "Você é o VALIDATOR, atuando como TRADER e também como PO (Product Owner) do Strategy Lab.\n\n"
                "Responsabilidades (você decide o que é 'bom o suficiente' para virar entrega):\n"
                "- Tomar a DECISÃO FINAL (approved/rejected) baseada principalmente no HOLDOUT (30% mais recente).\n"
                "- Julgar robustez/risco/overfit e apontar falhas de validação (custos, lookahead, amostra pequena).\n"
                "- Ser criterioso: explique em bullets o porquê e o que precisaria mudar para aprovar.\n\n"
                "Regras:\n"
                "- Use principalmente o HOLDOUT para o veredito.\n"
                "- Dê veredito 'approved' ou 'rejected' (texto deve conter claramente uma dessas palavras).\n"
                "- Responda em pt-BR."
            ),
        ),
    )

    g.set_entry_point("coordinator")
    g.add_edge("coordinator", "dev_senior")
    g.add_edge("dev_senior", "validator")
    g.add_edge("validator", END)

    return g.compile()
