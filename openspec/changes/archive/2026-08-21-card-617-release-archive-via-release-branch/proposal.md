# Proposal: card-617-release-archive-via-release-branch

## Why

Na release 2026-08-19 (kaizen F-1), o push do archive OpenSpec para `develop` foi recusado pela branch protection (`Required status check "qa-gate" is expected`), mesmo com `develop` contendo só conteúdo Homologado. O lote saiu por `release-*` → `main`, mas o runbook ainda descreve `release-*` quase só para “develop com não-homologado”, e o closeout não deixa explícito o sync `main → develop` para o `post` ver árvores idênticas. Recidivas nas releases seguintes (F-3) confirmam a lacuna documental/operacional.

## What Changes

- Documentar no runbook on-demand (`docs/crypto-overlay.md`) e na skill `alan-workflow` o caminho canônico de closeout via `release-*` quando o push em `develop` é recusado por proteção (ex.: `qa-gate`), **mesmo** se `develop` só tiver conteúdo Homologado do pacote.
- Garantir (normativo + evidência) que `scripts/release-guard pre` executado com HEAD em `release-*` PASS sem exigir que o archive já esteja em `origin/develop`.
- Tornar explícito no closeout o sync `main → develop` (PR ou merge) após o merge em `main`, para que `release-guard post` veja árvores idênticas.
- `AGENTS.md` permanece stub; aponta overlay on-demand — sem dual-write de playbook de release no always-on.

## UI impact

`none`

## Capabilities

### New Capabilities

- `release-archive-via-release-branch`: closeout documental e operacional do archive OpenSpec via `release-*` quando `develop` está protegida; sync pós-merge `main → develop`.

### Modified Capabilities

- `release-worktree-hygiene`: `pre` em branch `release-*` MUST NOT exigir archive (nem equivalente documental do pacote) já presente em `origin/develop` como condição de PASS.

## Impact

- Docs/runbook: `docs/crypto-overlay.md`, `.cursor/skills/alan-workflow/` (e stub `AGENTS.md` só se precisar reforçar o ponteiro on-demand).
- Guard: `scripts/release-guard` (modo `pre`, tratamento `release-*`); testes/evidência de regressão se o comportamento atual já for suficiente.
- Sem alteração de produto (`backend/**`, `frontend/src/**`).
- Card irmão #618 (local `develop` no `pre`) permanece fora de escopo.
