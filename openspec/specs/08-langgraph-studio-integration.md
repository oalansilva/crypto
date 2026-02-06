---
spec: openspec.v1
id: crypto.lab.langgraph.studio.v1
title: Strategy Lab — integração com LangGraph Studio (debug/traces) + link run_id → trace
status: draft
owner: Alan
created_at: 2026-02-06
updated_at: 2026-02-06
depends_on:
  - crypto.lab.langgraph.v2
---

# 0) One-liner

Adicionar uma camada de **dev/observabilidade** para que execuções disparadas pelo **/lab** (FastAPI) possam ser **inspecionadas no LangGraph Studio**, com correlação por `run_id` e um link direto “ver trace”.

# 1) Context

- Problema:
  - O Strategy Lab roda um workflow LangGraph, mas hoje o debug fica espalhado entre logs e o UI do /lab.
  - Para iterar rápido em nós (ingest/enrich/validate/backtest/validator) precisamos de uma forma visual de inspecionar **state**, inputs/outputs e erros por nó.
- Por que agora:
  - O /lab já existe e já tem o conceito de `run_id` + página de runs.
  - LangGraph Studio acelera validação e reduz tempo de diagnóstico.
- Restrições:
  - O Studio é uma ferramenta de **desenvolvimento**: não precisa (e não deve) ser embedado no /lab para usuário final.
  - Produção não pode depender do Studio estar “no ar”.
  - Não assumir serviços pagos; suportar fluxo gratuito/local.

# 2) Goal

## In scope

- Habilitar execução do LangGraph no backend FastAPI com:
  - **correlação** (`run_id` ↔ `thread_id`/`trace_id`) persistida.
  - persistência mínima de eventos por nó (start/end + erros) para UI.
- Adicionar no UI `/lab/runs/:run_id`:
  - um campo/CTA “**Abrir no Studio**” quando a integração estiver habilitada.
- Definir um “modo dev”:
  - Rodar Studio apontando para o grafo do projeto.
  - Executar runs via UI e conseguir rastrear a mesma execução no Studio.
- Documentar custos:
  - Studio local: sem custo de licença.
  - Custos variáveis: tokens de LLM + infra.
  - Opcional: tracing hospedado (ex.: LangSmith), se Alan decidir.

## Out of scope

- Builder visual (drag-and-drop) para criar o grafo.
- Expor o Studio publicamente na internet sem autenticação.
- Multi-tenant / auth do produto.

# 3) User stories

- Como Alan (dev), quero abrir uma execução do Lab no LangGraph Studio para ver o state e outputs por nó, para debugar rápido.
- Como Alan, quero que o `run_id` do /lab seja correlacionável com o trace, para não perder tempo procurando execuções.
- Como Alan, quero que em produção o sistema continue funcionando mesmo sem Studio, para evitar dependência de ferramenta de dev.

# 4) UX / UI

- Entry points:
  - `/lab/runs/:run_id` → seção “Debug/Trace”.
- States:
  - Loading: carrega status do run e metadados (trace id/link).
  - Empty: run ainda não tem `trace_url` (ex.: modo prod sem integração habilitada).
  - Error: mensagem “Integração Studio indisponível” (sem quebrar a página).
- Copy (PT-BR):
  - Botão: “Abrir no Studio”
  - Tooltip/nota: “Disponível apenas em modo dev.”

# 5) API / Contracts

## Backend endpoints

### POST /api/lab/run

- Request: (já existente) + opcional
  - `debug_trace`: boolean (default: `false` em produção; `true` em dev)
- Response (success):
  - `{ "run_id": "..." }`
- Response (error):
  - `{ "detail": "..." }`

### GET /api/lab/runs/{run_id}

- Response (success):

```json
{
  "run_id": "...",
  "status": "queued|running|done|error",
  "created_at": "...",
  "updated_at": "...",
  "graph": {
    "name": "strategy_lab",
    "version": "v2"
  },
  "trace": {
    "enabled": true,
    "provider": "langgraph_studio|langsmith|none",
    "trace_id": "...",
    "thread_id": "...",
    "trace_url": "http://... (optional)"
  },
  "events": [
    { "ts": "...", "type": "node_started", "node": "coordinator" },
    { "ts": "...", "type": "node_done", "node": "coordinator" },
    { "ts": "...", "type": "error", "node": "validator", "message": "..." }
  ],
  "result": { "summary": "..." }
}
```

- Response (error):
  - `404` se `run_id` não existe.

## Security

- Auth:
  - Produção: manter o padrão atual do projeto (sem introduzir acesso público ao Studio).
  - O `trace_url` só deve ser retornado se `TRACE_PUBLIC_URL` estiver configurado (ou se estiver em ambiente dev).
- Rate limits:
  - `POST /lab/run`: manter limite do job manager (se existir) ou aplicar limite simples por IP em dev.

# 6) Data model changes

- DB:
  - Tabela/registro de runs deve armazenar:
    - `run_id`
    - `status`
    - `trace_provider`
    - `trace_id` (opcional)
    - `thread_id` (opcional)
    - `trace_url` (opcional)
- Migrations:
  - adicionar colunas (ou tabela auxiliar) sem quebrar runs existentes.

# 7) VALIDATE (mandatory)

## Proposal link

- Proposal URL (filled after viewer exists): http://31.97.92.212:5173/openspec/crypto.lab.langgraph.studio.v1
- Status: draft → validated → approved → implemented

Before implementation, complete this checklist:

- [ ] Scope is unambiguous (in-scope/out-of-scope are explicit)
- [ ] Acceptance criteria are testable (binary pass/fail)
- [ ] API/contracts are specified (request/response/error) when applicable
- [ ] UX states covered (loading/empty/error)
- [ ] Security considerations noted (auth/exposure) when applicable
- [ ] Test plan includes manual smoke + at least one automated check
- [ ] Open questions resolved or explicitly tracked

# 8) Acceptance criteria (Definition of Done)

- [ ] Executar um run via `/lab` e ver `trace.provider != none` no `GET /api/lab/runs/{run_id}` quando `debug_trace=true`.
- [ ] A página `/lab/runs/:run_id` exibe “Abrir no Studio” quando `trace.trace_url` existir.
- [ ] Em modo prod (debug_trace=false), o Lab continua funcionando e a página não quebra (mostra estado Empty).
- [ ] Documentação adicionada: como rodar Studio local e como habilitar/desabilitar trace.

# 9) Test plan

## Automated

- Teste unitário: `trace_url` só aparece quando env/flag habilitados.
- Teste de contrato: `GET /api/lab/runs/{run_id}` inclui `trace` com chaves esperadas.

## Manual smoke

1. Rodar backend FastAPI em modo dev com tracing habilitado.
2. Abrir `/lab/`, iniciar um run (BTC/USDT, 1d).
3. Abrir `/lab/runs/:run_id` e verificar CTA “Abrir no Studio”.
4. Clicar e confirmar que abre o Studio/trace correspondente.
5. Desabilitar tracing e repetir: CTA não aparece, mas página continua OK.

# 9) Implementation plan

- Step 1: Definir estratégia de correlação (`run_id` ↔ `thread_id`/`trace_id`) no state do LangGraph.
- Step 2: Persistir metadados de trace no registro do run.
- Step 3: Atualizar `GET /api/lab/runs/{run_id}` para retornar `trace` + `events`.
- Step 4: Atualizar UI `/lab/runs/:id` para exibir CTA e estados.
- Step 5: Escrever docs (README) com comando de Studio local + env vars.

# 10) Rollout / rollback

- Rollout:
  - Feature flag via env: `LAB_TRACE_PROVIDER=none|langgraph_studio|langsmith`
  - Default: `none`.
- Rollback:
  - Setar `LAB_TRACE_PROVIDER=none` e remover CTA.

# 11) USER TEST (mandatory)

After deployment/restart, Alan will validate in the UI.

- Test URL(s):
  - http://31.97.92.212:5173/lab/
  - http://31.97.92.212:5173/lab/runs/<run_id>
- What to test (smoke steps):
  - Iniciar run e confirmar presença/ausência do link “Abrir no Studio” conforme flag.
- Result:
  - [ ] Alan confirmed: OK

# 12) ARCHIVE / CLOSE (mandatory)

Only after Alan confirms OK:

- [ ] Update spec frontmatter `status: implemented`
- [ ] Update `updated_at`
- [ ] Add brief evidence (commit hash + URL tested) in the spec

# 13) Notes / open questions

- Qual provider de tracing o projeto vai usar?
  - (A) Apenas Studio local (dev) + persistência mínima no DB
  - (B) LangSmith (hospedado) para histórico/colaboração
- Onde será hospedado o Studio em dev (local do Alan vs VPS) e como será protegido (VPN/basic auth)?
- Qual o formato final de `trace_url` (depende do provider e do modo de execução do Studio).
