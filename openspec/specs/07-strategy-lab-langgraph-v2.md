---
spec: openspec.v1
id: crypto.lab.langgraph.v2
title: Strategy Lab v2 (LangGraph + tool-driven template edits + job pipeline)
status: draft
owner: Alan
created_at: 2026-02-05
updated_at: 2026-02-05
depends_on: crypto.lab.langgraph.v1
---

# 0) One-liner

Evoluir o Strategy Lab MVP (CP1–CP6) para um fluxo **LangGraph** real, com ferramentas (tools) que **leem/alteram templates de verdade**, disparam backtests via **pipeline assíncrono** e produzem auditoria/observabilidade por nó.

# 1) Contexto

O MVP atual já entrega:
- /lab e /lab/runs/:id
- backtest + walk-forward 70/30
- 3 personas via OpenClaw Gateway
- budget + continue
- autosave (somente aprovado)

Faltam partes do escopo original da v1 que foram propositalmente “simplificadas” para acelerar entrega.

# 2) Objetivo (v2)

## In scope

### 2.1 LangGraph (workflow real)
- Implementar um grafo com nós:
  - Coordinator → decide objetivo e orquestra
  - Dev Senior → propõe/aplica mudanças em template
  - Validator → aprova/reprova com foco em holdout
- Estado do grafo persistido no trace (node start/end, inputs/outputs).

### 2.2 Tool-driven template edits (não só texto)
- O Dev deve conseguir:
  - ler template atual
  - produzir um patch estruturado (ex.: JSON patch ou novo template_data)
  - salvar como “candidate template” (ainda não é autosave final)
- Guardrails:
  - max 4 indicadores
  - naming + versionamento (candidate_1, candidate_2…)

### 2.3 Integração com pipeline assíncrono existente
- Disparar backtests via o mecanismo de jobs do sistema (status/result) ao invés de somente BackgroundTasks.
- Permitir múltiplos candidatos (ex.: 3–5) com fila e rate limit.

### 2.4 Métricas e seleção baseada em holdout
- Critério primário: holdout
- Regras mínimas (a definir):
  - min trades no holdout
  - limites de DD
  - custos/slippage sempre ligados

### 2.5 Observabilidade / auditoria
- Persistir:
  - mensagens por persona
  - tool calls
  - usage por nó/persona
  - decisão final (approved/rejected) + porquê

## Out of scope
- UI avançada (builder visual do grafo)
- Multi-tenant / auth

# 3) API (rascunho)

- POST /api/lab/run
  - aceita `candidates_max`
  - aceita `walk_forward=true` (default)
- GET /api/lab/runs/{run_id}
  - retorna status do grafo + candidatos + jobs

# 4) DoD

- [ ] LangGraph executa end-to-end (mínimo: 1 candidato)
- [ ] Dev aplica mudança real no template (não só sugestões em texto)
- [ ] Backtest via job pipeline (status/result)
- [ ] Validator decide usando holdout
- [ ] Autosave somente se aprovado

# 5) Test plan

- Smoke manual:
  - Criar run, ver nós do grafo, ver candidato aplicado, ver backtest job, ver decisão.
- Automatizado:
  - backend unit tests para validação de patch e enforcement max-4-indicators

# 6) Notas

- Reavaliar o problema atual: ATR/ADX = 0 (provável pipeline/feature). Ideal corrigir antes de tentar automatizar filtros de regime.
