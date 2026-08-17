## Why

O Cripto Farol ainda trata o OpenCode como harness único (#561/#555), mas Alan passou a trabalhar no Cursor Agent e invertou o destino: o cliente ativo deve ser o Cursor, com o modelo selecionado no chat. Manter OpenCode, Sol/Pro/Qwen e o design-gate-guard no contrato ativo gera docs mentirosas, CI acoplada a `opencode-ai@1.18.18` e um cadeado que já travou o #555/#559.

## What Changes

- **BREAKING:** Cursor Agent vira o único harness operacional. OpenCode sai do contrato ativo.
- Cancelar #561 (feito) e entregar o cutover neste card (#562).
- Modelo: o selecionado no chat (hoje Grok 4.6) executa Design, código, review e visão. Sem Sol/Pro/Qwen obrigatórios, sem `design-planner` de modelo fixo, sem `vision-router`.
- Gate Design simples: board + skill `design-critic` + crítica em `Task` isolada (mesmo modelo) + hook Impeccable. Sem lease, packet selado, `design_artifact_write` ou attestation OpenCode 1.18.18.
- Adicionar `.cursor/rules`, skills/commands OpenSpec+kaizen e `hooks.json`.
- Skills globais ativas em `~/.cursor/skills/`.
- Remover `.opencode/`, `opencode.json`, job CI `design-gate-contract` e `.agent/workflows/opsx-*`.
- Kaizen passa a auditar transcripts Cursor, não `opencode.db`.
- Revogar a regra de 2026-08-14 que exigia GPT 5.6 Sol como autor do Design.

## Capabilities

### New Capabilities

- `cursor-harness`: contrato do cliente Cursor (rules, skills, commands, hooks, modelo do chat).

### Modified Capabilities

- `developer-tooling`: config versionada deixa de ser OpenCode e passa a ser Cursor.
- `visual-analysis-routing`: visão na sessão principal (Read de imagem); Qwen/vision-router deixam de ser obrigatórios.
- `impeccable-design-gate`: hook Cursor no detector existente; critics herdam o modelo do chat.
- `kaizen-continuous-improvement`: `/kaizen` no Cursor; sessões = transcripts Cursor.
- `workflow-state-db`: um harness (Cursor), não Codex+Cursor.
- `card-close-evidence-integrity`: todos/títulos de sessão deixam de depender de `opencode.db`.
- `vision-path-validation`: path-check antes de `Read` de imagem, sem subagent `vision` obrigatório.

## Impact

- Docs/contrato: `AGENTS.md`, `rules.md`, `.agents/skills/design-critic/SKILL.md`, `docs/decision-log.md`, `docs/backlog-operating-model.md`, README do Project 1.
- Tooling: nova árvore `.cursor/`; remoção de `.opencode/` e `opencode.json`.
- CI: job `design-gate-contract` removido; conferir branch protection.
- Runtime de produto (API, UI, banco): nenhum.
- OpenSpecs arquivados e evidence do #550/#555: não reescritos.
