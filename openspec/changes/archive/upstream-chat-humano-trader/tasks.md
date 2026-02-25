## 1. Backend — upstream chat + persistência

- [x] 1.1 Adicionar estrutura `run.upstream.messages[]` no JSON do run (criação + load/save).
- [x] 1.2 Criar endpoint para enviar mensagem no upstream (ex.: `POST /api/lab/runs/{run_id}/upstream/message`).
- [x] 1.3 Implementar chamada da persona **Trader** (reuso do `validator` internamente por enquanto) para:
  - gerar pergunta
  - atualizar `upstream_contract`
  - marcar aprovado
- [x] 1.4 Emitir trace events por turno (`upstream_message`, `upstream_contract_updated`, `upstream_approved`).

## 2. Frontend — UI de chat upstream

- [x] 2.1 Em `/lab/runs/:run_id`, adicionar seção **Upstream (chat)** com histórico + input + enviar.
- [x] 2.2 Quando `upstream_contract.approved=true`, mostrar CTA **Iniciar execução**.
- [x] 2.3 Renomear na UI/copy `validator` → **Trader**.

## 3. Spec delta + validate

- [x] 3.1 Criar delta spec(s) em `specs/lab/...` e/ou `specs/ui/...`.
- [x] 3.2 `openspec validate upstream-chat-humano-trader --type change`.

## Test plan

- Manual:
  - Criar run com inputs incompletos → ver pergunta do Trader, responder, ver histórico.
  - Aprovar upstream → ver CTA e iniciar execução.

- Automated (mínimo):
  - Teste de endpoint: postar mensagem upstream grava no run e retorna contrato atualizado.
