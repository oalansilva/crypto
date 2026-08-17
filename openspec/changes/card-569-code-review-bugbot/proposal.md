## Why

O gate `Status=Code Review` já existe e corre antes do commit, mas o agente ainda usa um `Task` genérico e o `AGENTS.md` restringe Bugbot a pedido explícito. A documentação oficial do Cursor (2026) recomenda `/review-bugbot` e `/review-security` no diff local **antes do push**, com regras em `.cursor/BUGBOT.md` — arquivos `.mdc` não valem para o Bugbot. Sem essa troca, o revisor nativo quase nunca roda e o contrato do Cripto não entra no review.

## What Changes

- Em `Status=Code Review`, o agente **sempre** dispara `/review-bugbot` no diff não commitado (`uncommitted changes`, sem `Base Branch`).
- Depois do commit de implementação, um `/review-bugbot` `branch changes` + `Base Branch: develop` é obrigatório no SHA de fechamento.
- `/review-security` obrigatório quando o diff casa com os globs de auth/credencial/trading/wallet/API.
- `Task` genérico só após spawn falho + 1 retry (erro explícito; sem fallback silencioso).
- Criar `.cursor/BUGBOT.md` na raiz e aninhados `backend/` e `frontend/` com o contrato que o Bugbot lê.
- Criar `.cursor/agents/code-reviewer.md` (`readonly: true`, `model: inherit`) só para contrato de processo (OpenSpec, Design gate, não regressão de status).
- Bugbot no PR para `develop` é complemento de **QA**, não substituto do Code Review: Incremental Review ligado; Autofix Off (proibido Commit to Existing Branch).
- Agent Review automático pós-commit permanece desligado (inverte o gate pré-commit).
- Comentário de Done cita o resultado do `/review-bugbot`.
- **Não é BREAKING** para produto/API/UI. É mudança de contrato operacional do harness.

## Capabilities

### New Capabilities

- `cursor-code-review`: gate de Code Review no Cursor usando `/review-bugbot` (pré-commit `uncommitted changes`; fechamento `branch changes` vs `develop`) e `/review-security` no caminho quente, com `BUGBOT.md` e Task de processo read-only.

### Modified Capabilities

- `cursor-harness`: o Code Review deixa de ser `Task` genérico por padrão; Bugbot/Security Review são produtos gerenciados do Cursor (modelo próprio); o subagent de processo continua `inherit`.
- `delivery-qa-stage`: evidência de Code Review inclui o resultado do Bugbot; Bugbot no PR é QA; Autofix na mesma branch é proibido.
- `developer-tooling`: versionar `.cursor/BUGBOT.md`, aninhados e `.cursor/agents/code-reviewer.md`.

## Impact

- Docs/contrato: `AGENTS.md`, `rules.md`, `docs/backlog-operating-model.md`, comentário canônico de Done, `docs/kaizen-log.md` (entrada do card).
- Tooling: `.cursor/BUGBOT.md`, `backend/.cursor/BUGBOT.md`, `frontend/.cursor/BUGBOT.md`, `.cursor/agents/code-reviewer.md`.
- Runtime de produto (API, UI, banco): nenhum.
- Configuração de Automations/Bugbot no dashboard Cursor (Autofix Off) é evidência operacional, não código.
