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
                "Papel: Coordinator (Agilista / Scrum Master)\n"
                "Você atua como COORDINATOR (Agilista/Scrum Master) do Strategy Lab. Seu papel facilitar a colaboração, organizar o trabalho e destravar o fluxo do time.\n\n"
                "Responsabilidades\n"
                "1. Resumo do run\n"
                "- Sintetize objetivamente o que aconteceu no último run (máx. 1–2 parágrafos).\n"
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
            ),
        ),
    )

    g.add_node(
        "dev_senior",
        _node_factory(
            persona="dev_senior",
            output_key="dev_summary",
            system_prompt=(
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
                "- Bollinger Bands: type bbands/bollinger, alias bb → colunas bb_upper, bb_middle, bb_lower\n"
                "- ADX: alias adx → coluna adx (além de ADX_<length>)\n"
                "- ATR: alias atr → coluna atr (além de ATR_<length>)\n"
                "- Também disponíveis: close, open, high, low, volume\n"
                "Exemplo válido: close > bb_upper AND adx > 18\n\n"
                "Sanity check obrigatório\n"
                "Antes de finalizar a resposta: verifique que todas as referências usadas em entry/exit correspondem a colunas realmente existentes no engine. Se alguma coluna não existir, corrija antes de responder.\n\n"
                "Diretrizes finais\n"
                "- Idioma: pt-BR\n"
                "- Foco: execução, robustez e geração de trades\n"
                "- Não explique o JSON fora do campo description ou notes."
            ),
        ),
    )

    g.add_node(
        "validator",
        _node_factory(
            persona="validator",
            output_key="validator_verdict",
            system_prompt=(
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
                "Decisão final (obrigatória)\n"
                "Declare explicitamente um veredito: approved ou rejected. O veredito deve estar claramente presente no texto.\n\n"
                "Justificativa\n"
                "Explique sua decisão em bullets objetivos. Se o veredito for rejected, deixe claro: o que falhou e o que precisaria mudar para aprovar no próximo ciclo.\n\n"
                "Regras de resposta\n"
                "- Baseie o veredito principalmente no HOLDOUT.\n"
                "- Idioma: pt-BR.\n"
                "- Tom criterioso, técnico e decisório (sem sugestão de edge novo)."
            ),
        ),
    )

    g.set_entry_point("coordinator")
    g.add_edge("coordinator", "dev_senior")
    g.add_edge("dev_senior", "validator")
    g.add_edge("validator", END)

    return g.compile()
