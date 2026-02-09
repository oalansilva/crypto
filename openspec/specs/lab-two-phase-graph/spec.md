---
id: lab-two-phase-graph
name: "Lab: grafo em 2 etapas (Upstream humano+trader → Implementação+testes)"
status: draft
owner: Alan
created_at: 2026-02-09
updated_at: 2026-02-09
---

## Context
Hoje o `/lab` executa um grafo sequencial simples (CP7): `coordinator → dev_senior → validator`.

Queremos melhorar o fluxo para ficar **claramente em 2 etapas**:
1) **Upstream**: humano + “validator” (na prática um especialista financeiro/trader) para clarificar requisitos, levantar riscos e produzir um contrato objetivo.
2) **Implementação e testes**: executar a implementação e rodar testes/validações determinísticas.

O humano acontece **no próprio `/lab`** (UI mostra perguntas; usuário responde ali).
O Upstream deve rodar **sempre**.
A etapa 2 pode ser **automática** após upstream aprovado.

## Purpose
Reduzir retrabalho e custo, melhorar a qualidade das decisões e tornar o Lab determinístico onde possível, separando:
- clarificação/validação de requisitos (Upstream)
- execução (Implementação + testes)

## Requirements

### Requirement: Grafo único com branch entre Upstream e Implementação
O backend MUST executar um **único grafo** (LangGraph), com branch condicional:
- Se `upstream_contract.approved == true` → segue para Implementação+Testes
- Caso contrário → encerra com `status = needs_user_input` ou `status = rejected`

#### Scenario: Upstream aprovado
- **WHEN** o usuário fornece inputs suficientes no `/lab` e o trader aprova
- **THEN** o grafo avança automaticamente para Implementação+Testes
- **AND** o run transita para um status equivalente a `implementation_running`

#### Scenario: Upstream precisa de mais inputs
- **WHEN** faltarem informações obrigatórias
- **THEN** o backend responde/atualiza o run com `status = needs_user_input`
- **AND** inclui uma pergunta curta (`question`) e lista `missing`
- **AND** o grafo NÃO avança para Implementação

---

### Requirement: Contrato Upstream como fonte de verdade
O backend MUST produzir e persistir um objeto JSON `upstream_contract` que seja a fonte de verdade para a etapa 2.

Campos mínimos do `upstream_contract`:
- `approved: boolean`
- `missing: string[]` (se não aprovado)
- `question: string` (se não aprovado)
- `inputs: { symbol: string, timeframe: string }`
- `objective: string` (texto do usuário)
- `acceptance_criteria: string[]` (checklist)
- `risk_notes: string[]` (observações do trader)

#### Scenario: Upstream aprovado gera contrato
- **WHEN** Upstream termina com aprovação
- **THEN** `upstream_contract.approved == true`
- **AND** `upstream_contract.inputs.symbol/timeframe` estão preenchidos
- **AND** `acceptance_criteria` contém ao menos 2 itens

---

### Requirement: UI do /lab deve suportar perguntas/respostas do Upstream
O frontend MUST suportar o ciclo:
- usuário solicita run
- backend retorna `needs_user_input` com `question`
- usuário responde na própria tela e reenvia

#### Scenario: Backend pede input
- **WHEN** o frontend recebe `status = needs_user_input`
- **THEN** exibe `question` de forma destacada
- **AND** permite reenvio do texto do usuário (resposta)

---

### Requirement: Etapa 2 executa implementação e testes com rastreio
Quando `upstream_contract.approved == true`, o backend MUST:
- executar a etapa de implementação
- rodar testes determinísticos
- registrar eventos no trace

Eventos sugeridos (mínimo):
- `upstream_started`, `upstream_done`
- `implementation_started`, `implementation_done`
- `tests_started`, `tests_done` (com pass/fail)
- `final_decision`

#### Scenario: Testes passam
- **WHEN** a etapa 2 termina
- **THEN** `tests_done.pass == true`
- **AND** o run finaliza com `status = done`

#### Scenario: Testes falham
- **WHEN** os testes falham
- **THEN** `tests_done.pass == false`
- **AND** o run finaliza com `status = failed`

## Non-goals
- NLP avançado (extração livre de entidades) além do necessário para o ciclo upstream.
- Autenticação multi-tenant.

## Implementation plan (alto nível)
1) Backend:
   - estender/alterar `backend/app/services/lab_graph.py` para um grafo único com branch:
     - sub-etapa Upstream (humano + trader)
     - sub-etapa Implementação+Testes
   - persistir `upstream_contract` no run JSON.
   - adicionar/ajustar endpoint `/api/lab/runs/{id}/continue` para retomar após inputs (se aplicável).
2) Frontend `/lab`:
   - suportar `needs_user_input` como um ciclo de conversa.
3) Testes:
   - testes cobrindo transições: missing → needs_user_input; approved → avança para etapa 2.

## Acceptance checks
- [ ] Upstream roda sempre e produz `upstream_contract`.
- [ ] `needs_user_input` funciona no `/lab` com pergunta e reenvio.
- [ ] Após upstream aprovado, etapa 2 roda automaticamente.
- [ ] Trace contém eventos das duas etapas.
- [ ] Testes automatizados cobrindo o fluxo.

## Evidence (preencher após implementar)
- Commit(s):
- URL testada:
- Notas:
