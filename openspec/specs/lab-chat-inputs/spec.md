---
id: lab-chat-inputs
name: "Lab: inputs via chat (remover Symbol/Timeframe/Template base da UI)"
status: draft
owner: Alan
created_at: 2026-02-08
updated_at: 2026-02-08
---

## Context
Hoje a tela do Strategy Lab em `http://31.97.92.212:5173/lab` expõe campos de entrada explícitos:
- **Symbol (Binance)**
- **Timeframe**
- **Template base**

A intenção do produto é o fluxo ser **conversa-first**: o usuário fornece esses parâmetros **na conversa** ao solicitar um run.
Se faltar algum parâmetro essencial, o bot deve **perguntar** antes de iniciar o run.

## Purpose
Simplificar a UI do Lab removendo campos redundantes e garantir que a coleta de inputs obrigatórios aconteça via chat com validação determinística.

## Requirements

### Requirement: Remover inputs de Symbol/Timeframe/Template base do /lab
O frontend MUST NOT exibir campos de formulário na página `/lab` para:
- Symbol (Binance)
- Timeframe
- Template base

#### Scenario: Usuário acessa a página /lab
- **WHEN** o usuário abre `GET /lab` no frontend
- **THEN** não existem inputs/fields para Symbol, Timeframe e Template base

---

### Requirement: Preflight determinístico de inputs obrigatórios antes de iniciar run
O backend MUST validar determinísticamente se o payload possui os campos necessários para iniciar um run.

Campos necessários para iniciar um run:
- `symbol` (ex.: `BTC/USDT`) — **obrigatório**
- `timeframe` (ex.: `1h`, `4h`) — **obrigatório**

Observação: `base_template` NÃO deve mais existir neste fluxo. A cada solicitação os agentes devem criar um template novo (não depende de template base escolhido pelo usuário).

#### Scenario: Payload sem symbol/timeframe
- **WHEN** o cliente solicita criação de run sem `symbol` e/ou sem `timeframe`
- **THEN** o backend NÃO inicia o run
- **AND** responde JSON com:
  - `status = "needs_user_input"`
  - `missing = [...]` listando os campos faltantes
  - `question = "..."` com uma pergunta curta e objetiva

Exemplo de resposta:
```json
{
  "status": "needs_user_input",
  "missing": ["symbol", "timeframe"],
  "question": "Quais são o symbol (ex: BTC/USDT) e o timeframe (ex: 1h, 4h) para rodarmos o Lab?"
}
```

#### Scenario: Payload completo
- **WHEN** o cliente solicita criação de run com `symbol` e `timeframe`
- **THEN** o backend aceita a criação e retorna `status = "accepted"` e `run_id`

Exemplo de resposta:
```json
{
  "status": "accepted",
  "run_id": "...",
  "inputs": {"symbol": "BTC/USDT", "timeframe": "1h"}
}
```

---

### Requirement: UI deve lidar com needs_user_input
O frontend MUST exibir a `question` retornada pelo backend quando `status = "needs_user_input"`.

#### Scenario: Backend pede input
- **WHEN** o frontend recebe `status = "needs_user_input"`
- **THEN** exibe a pergunta `question` ao usuário
- **AND** não tenta iniciar polling de run_id inexistente

## Non-goals
- NLP avançado para extrair symbol/timeframe de texto livre (neste ciclo, basta suportar envio explícito)
- Autenticação/contas

## Implementation plan (alto nível)
1) Frontend: remover inputs e ajustar payload/UX para lidar com `needs_user_input`.
2) Backend: adicionar função de preflight (ex.: `_inputs_preflight`) e alterar rota de criação para retornar `needs_user_input` antes de iniciar qualquer job.
3) Testes.

## Acceptance checks
- [ ] Em `http://31.97.92.212:5173/lab`, não existem mais campos/inputs para Symbol (Binance), Timeframe e Template base.
- [ ] Se faltar `symbol` e/ou `timeframe` (e `base_template` se aplicável), o backend retorna `needs_user_input` com `missing` e `question`.
- [ ] Se todos os campos necessários estiverem presentes, o backend retorna `accepted` e `run_id`.
- [ ] Há teste(s) cobrindo a validação de campos faltantes (unit ou teste de rota).

## Evidence (preencher após implementar)
- Commit(s):
- URL testada:
- Notas:
