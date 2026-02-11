---
id: lab-two-phase-graph
name: "Lab: grafo em 2 etapas (Upstream humano+trader → Implementação+testes)"
status: draft
owner: Alan
created_at: 2026-02-09
updated_at: 2026-02-09
---

## Purpose
Separar o fluxo do Strategy Lab em duas etapas explícitas (Upstream e Implementação+Testes), reduzindo retrabalho e garantindo um contrato determinístico (`upstream_contract`) antes da execução.

## Requirements

## ADDED Requirements

### Requirement: Grafo único MUST ter branch entre Upstream e Implementação
O backend MUST executar um único grafo (LangGraph) com branch condicional:
- Se `upstream_contract.approved == true` → segue automaticamente para Implementação+Testes
- Caso contrário → encerra/pausa com `status = needs_user_input` ou `status = rejected`

#### Scenario: Upstream aprovado
- **WHEN** o usuário fornece inputs suficientes no `/lab` e o trader aprova
- **THEN** o grafo avança automaticamente para Implementação+Testes
- **AND** o run transita para um status equivalente a `implementation_running`

#### Scenario: Upstream precisa de mais inputs
- **WHEN** faltarem informações obrigatórias
- **THEN** o backend responde/atualiza o run com `status = needs_user_input`
- **AND** inclui `missing: string[]` e uma pergunta curta `question`
- **AND** o grafo NÃO avança para Implementação

### Requirement: Upstream MUST produzir upstream_contract como fonte de verdade
O backend MUST produzir e persistir um objeto JSON `upstream_contract` que seja a fonte de verdade para a etapa 2.

Campos mínimos do `upstream_contract`:
- `approved: boolean`
- `missing: string[]` (se não aprovado)
- `question: string` (se não aprovado)
- `inputs: { symbol: string, timeframe: string }`
- `objective: string`
- `acceptance_criteria: string[]`
- `risk_notes: string[]`

#### Scenario: Upstream aprovado gera contrato
- **WHEN** Upstream termina com aprovação
- **THEN** `upstream_contract.approved == true`
- **AND** `upstream_contract.inputs.symbol/timeframe` estão preenchidos
- **AND** `acceptance_criteria` contém ao menos 2 itens

### Requirement: UI do /lab MUST suportar ciclo de perguntas/respostas
O frontend MUST suportar o ciclo de conversa:
- usuário solicita run
- backend retorna `needs_user_input` com `question`
- usuário responde na própria tela e reenvia

#### Scenario: Backend pede input
- **WHEN** o frontend recebe `status = needs_user_input`
- **THEN** exibe `question` de forma destacada
- **AND** permite reenvio do texto do usuário (resposta)

### Requirement: Etapa 2 MUST executar implementação e testes com trace
Quando `upstream_contract.approved == true`, o backend MUST:
- executar a etapa de implementação
- rodar testes determinísticos
- registrar eventos no trace

Eventos mínimos:
- `upstream_started`, `upstream_done`
- `implementation_started`, `implementation_done`
- `tests_started`, `tests_done`
- `final_decision`

#### Scenario: Testes passam
- **WHEN** a etapa 2 termina
- **THEN** `tests_done.pass == true`
- **AND** o run finaliza com `status = done`

#### Scenario: Testes falham
- **WHEN** os testes falham
- **THEN** `tests_done.pass == false`
- **AND** o run finaliza com `status = failed`
