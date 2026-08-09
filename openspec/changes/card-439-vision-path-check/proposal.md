## Why

A delegação visual do #413 delegou ao subagent vision 4× com `File not found: /tmp/opencode/bl413/...` + re-delegações do mesmo prompt sem gerar os crops, e fez 3× webfetch 404 em URLs inexistentes (F-3 da auditoria 2026-08-09). Cada respawn desperdiça custo e atrasa o QA visual.

## What Changes

- Skill/regra versionada: antes de passar arquivos ao vision, confirmar existência (`ls`/glob).
- Em falha de leitura do subagent, gerar o artefato antes de respawnar.
- Registrar orientação no fluxo de QA visual (proibido respawn por arquivo inexistente).

## Capabilities

### New Capabilities

- `vision-path-validation`: validação de existência de paths/URLs antes de delegar análise visual, sem respawn por arquivo inexistente.

### Modified Capabilities

- `developer-tooling`: o fluxo de QA visual exige path-check antes da delegação ao vision e geração do artefato antes de respawn.

## Impact

- Skills/regras de QA visual (`AGENTS.md`, skill `impeccable`/`playwright-cli` conforme aplicável).
- Fluxo de delegação ao subagent `vision`.
- Sem mudanças de runtime, banco ou frontend.
