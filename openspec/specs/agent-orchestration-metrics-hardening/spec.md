---
spec: openspec.v1
id: agent-orchestration-metrics-hardening
title: Hardening de métricas + orquestração de agentes (Strategy Lab)
status: draft
owner: Alan
created_at: 2026-02-08
updated_at: 2026-02-08
---

## Purpose

Endurecer o pipeline do Strategy Lab para que:
- métricas (principalmente Sortino / retorno / expectancy) sejam **confiáveis** e auditáveis;
- a decisão do gate seja **consistente** (uma fonte de verdade);
- o sistema pare cedo quando houver falha de instrumentação (pré-validação determinística);
- a orquestração de agentes use menos tokens e gere menos ruído.

## Requirements

### Requirement: Sortino deve ser calculado com guardrails (sem valores absurdos)
O sistema SHALL calcular o Sortino de forma robusta e nunca produzir valores absurdos (ex.: `1e14`) sem explicitar que é um caso degenerado (downside deviation≈0).

#### Scenario: Holdout com downside deviation ~ 0
- **GIVEN** uma série de retornos do holdout sem variância negativa (ou downside deviation ~ 0)
- **WHEN** o sistema calcula Sortino
- **THEN** `sortino_ratio` SHALL ser `null` ou `inf` (conforme política definida)
- **AND** o sistema SHALL registrar `sortino_status: "degenerate"` e `downside_deviation` no output

#### Scenario: Holdout normal com retornos negativos
- **GIVEN** uma série de retornos do holdout com retornos negativos suficientes
- **WHEN** o sistema calcula Sortino
- **THEN** `sortino_ratio` SHALL ser finito e plausível
- **AND** `downside_deviation` e `neg_return_count` SHALL ser logados

### Requirement: Output de métricas deve incluir diagnósticos mínimos
O sistema SHALL incluir no output (backend + JSONL) os diagnósticos mínimos para auditoria de métricas.

#### Scenario: Backtest concluído
- **GIVEN** um backtest concluído com blocos all/in-sample/holdout
- **WHEN** o sistema gera métricas
- **THEN** o bloco holdout SHALL conter pelo menos:
  - `downside_deviation`
  - `neg_return_count`
  - `return_series_kind` (ex.: `daily`, `per_trade`)
  - definições/unidades para `expectancy` e `total_return_pct` (via campos ou docs vinculadas)

### Requirement: Preflight determinístico deve bloquear LLM quando métricas estão inválidas
O sistema SHALL executar uma validação determinística antes de chamar o nó LLM `validator`.

#### Scenario: Métricas inválidas detectadas
- **GIVEN** um run com `sortino_ratio` inválido/absurdo OU campos obrigatórios ausentes
- **WHEN** o preflight roda
- **THEN** o sistema SHALL emitir evento `metrics_preflight` com `ok=false`
- **AND** SHALL terminar a iteração com `result="metrics_invalid"` (ou equivalente)
- **AND** SHALL **não** chamar o LLM `validator`

#### Scenario: Métricas válidas
- **GIVEN** um run com métricas coerentes
- **WHEN** o preflight roda
- **THEN** `metrics_preflight.ok=true`
- **AND** o sistema SHALL chamar o LLM `validator`

### Requirement: Gate decision deve ser consistente e ter uma fonte de verdade
O sistema SHALL consolidar decisão final de forma consistente entre `validator`, `selection_gate` e `iteration_done`.

#### Scenario: Validator rejeita
- **GIVEN** o `validator` retorna JSON com `verdict="rejected"`
- **WHEN** o `selection_gate` consolida a decisão
- **THEN** o evento `gate_decision.verdict` SHALL ser `rejected`
- **AND** `iteration_done.result` SHALL ser `rejected`

#### Scenario: Validator aprova e thresholds passam
- **GIVEN** o `validator` retorna JSON com `verdict="approved"`
- **AND** thresholds numéricos passam
- **WHEN** o `selection_gate` consolida a decisão
- **THEN** `gate_decision.verdict` SHALL ser `approved`

### Requirement: Validator deve responder em JSON-only
O nó LLM `validator` SHALL responder somente em JSON para evitar parsing ambíguo e contradições.

#### Scenario: Execução de validação
- **GIVEN** um run com preflight ok
- **WHEN** o nó `validator` é chamado
- **THEN** a resposta SHALL seguir o contrato:
  `{ "verdict": "approved"|"rejected"|"metrics_invalid", "reasons": [..], "required_fixes": [..], "notes": "..." }`

### Requirement: Orquestração deve reduzir tokens e repetição
O sistema SHALL limitar o tamanho das respostas dos nós e suportar modo detalhado opcional.

#### Scenario: explain=false (padrão)
- **GIVEN** `explain=false`
- **WHEN** `coordinator/dev_senior/validator` executam
- **THEN** a saída SHALL ser curta e estruturada (ex.: bullets/JSON)

#### Scenario: explain=true
- **GIVEN** `explain=true`
- **WHEN** os nós executam
- **THEN** o sistema MAY incluir um relatório mais detalhado

### Requirement: Evidências do holdout devem ser geradas automaticamente
O sistema SHALL gerar evidências básicas do holdout para auditoria (sem depender de LLM).

#### Scenario: Backtest com holdout
- **GIVEN** um run com holdout
- **WHEN** o backtest termina
- **THEN** o sistema SHALL produzir:
  - equity curve do holdout
  - distribuição de retornos por trade (top ganhos/perdas)
- **AND** referenciar esses artefatos no log/trace

### Requirement: Dependências faltantes devem falhar com mensagem acionável
O sistema SHALL detectar ausência de engines parquet (pyarrow/fastparquet) e falhar com instrução clara.

#### Scenario: Ambiente sem pyarrow/fastparquet
- **GIVEN** o ambiente não tem `pyarrow` nem `fastparquet`
- **WHEN** o sistema tenta ler/escrever parquet
- **THEN** SHALL retornar erro `DEPENDENCY_MISSING`
- **AND** SHALL incluir instruções de correção (ex.: `pip install pyarrow`)

---

# Context (detalhe)

Problemas observados nos logs recentes:
- Sortino no holdout com valores na ordem de `1e14` (indicando cálculo degenerado ou bug).
- `validator` diz “REJECTED” enquanto `selection_gate` registra `approved: true` em alguns casos.
- Iterações continuam apesar de falha de instrumentação.
- Alto consumo de tokens com texto repetitivo.
- Erro de parquet engine (pyarrow/fastparquet) causando falha de execução.

# Events / Contracts (JSONL)

## Event: metrics_preflight
- `ok: boolean`
- `errors: string[]`
- `warnings: string[]`
- `metrics_checks: { sortino_finite, downside_deviation, neg_return_count, ... }`

## Event: gate_decision
- `verdict: "approved"|"rejected"|"metrics_invalid"|"error"`
- `reasons: string[]`
- `thresholds: {...}`
- `signals: {...}`

# VALIDATE (mandatory)

- Proposal URL (viewer): http://31.97.92.212:5173/openspec/agent-orchestration-metrics-hardening
- Status: draft → validated → approved → implemented

# Acceptance criteria (Definition of Done)

- [ ] Não existe `sortino_ratio` absurdo (ex.: > 1e6) sem status degenerado (`null/inf` + motivo)
- [ ] Output inclui `downside_deviation`, `neg_return_count`, `return_series_kind`
- [ ] Preflight bloqueia LLM validator quando `metrics_invalid`
- [ ] `gate_decision` e `iteration_done` são consistentes com o `validator.verdict`
- [ ] Validator é JSON-only
- [ ] explain flag controla detalhamento
- [ ] Erros de parquet têm mensagem acionável

# Test plan

## Automated
- Unit tests: Sortino degenerado; gate decision; preflight.

## Manual smoke
1. Rodar Strategy Lab com `debug_trace=true`.
2. Verificar `metrics_preflight` + `gate_decision` no JSONL.
3. Verificar UI/trace mostrando artefatos e motivos.

# Implementation plan (alto nível)

1. Corrigir Sortino + adicionar diagnósticos.
2. Implementar preflight.
3. Tornar validator JSON-only + parser.
4. Unificar gate decision.
5. Reduzir tokens (budgets + explain).
6. Artefatos do holdout.
7. Mensagens de dependência parquet.

# Notes / open questions

- Política: Sortino degenerado deve ser `null` ou `inf`? (e como o UI exibe)
- Persistência: DB vs arquivos por run para equity/distribuição.
