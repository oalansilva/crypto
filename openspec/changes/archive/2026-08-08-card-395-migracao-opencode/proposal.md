## Why

Alan passa a usar o opencode como ferramenta principal no lugar do Codex. Sem migração, o opencode perde acesso a subagents (code-mapper, pr-explorer, reviewer, browser-debugger), slash commands /opsx-*, hook de proteção de design (impeccable) e skills globais de operação (alan-workflow, GitHub Project, gh-*).

## What Changes

- Adicionar `opencode.json` versionado na raiz (model, plugin impeccable).
- Converter os 4 subagents de `.codex/agents/*.toml` para `.opencode/agent/*.md`.
- Converter os 10 commands `/opsx-*` do Cursor/Claude para `.opencode/command/opsx-*.md`.
- Portar os hooks `PostToolUse`/`Stop` do Codex para o plugin opencode `.opencode/plugin/impeccable-hook.ts`.
- Registrar skills globais via symlink em `~/.config/opencode/skills/` (alan-workflow, alan-workflow-ambientes, github-project-board, gh-address-comments, gh-fix-ci).
- Atualizar `AGENTS.md`/`rules.md` com a camada opencode (de-para `/opsx:*`, invocação de skills, regra Impeccable).

## Capabilities

### New Capabilities

- `developer-tooling`: requisitos para a configuração de ferramenta de desenvolvimento (opencode) versionada no repo — config, agents, commands, plugin e skills — sem segredos e sem impacto em runtime de produto.

### Modified Capabilities

None.

## Impact

- Affected files: `opencode.json`, `.opencode/**`, `AGENTS.md`, `rules.md`, `openspec/changes/card-395-migracao-opencode/**`.
- Affected workflow: ferramenta de desenvolvimento de agentes (opencode), fluxo OpenSpec `/opsx:*`, gate de design e hook impeccable.
- Fora do git: `~/.config/opencode/opencode.jsonc` e `~/.config/opencode/skills/`.
- Sem mudança de runtime: nenhuma API, banco, worker ou tela de produto é alterada.
