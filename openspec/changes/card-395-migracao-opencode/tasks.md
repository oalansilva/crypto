## Tasks

## 1. Config global (fora do git)

- [ ] 1.1 Atualizar `~/.config/opencode/opencode.jsonc` com model `opencode-go/deepseek-v4-flash` e MCP `openaiDeveloperDocs`.
- [ ] 1.2 Criar symlinks de `~/.codex/skills/` e `/srv/knowledge/hermes-second-brain/skills/` para `~/.config/opencode/skills/` (alan-workflow, alan-workflow-ambientes, github-project-board, gh-address-comments, gh-fix-ci).

## 2. Config do projeto

- [ ] 2.1 Criar `opencode.json` na raiz ($schema, model, instructions, MCP openaiDeveloperDocs, plugin impeccable).
- [ ] 2.2 Converter 4 subagents `.codex/agents/*.toml` para `.opencode/agent/*.md` (code-mapper, pr-explorer, reviewer, browser-debugger).
- [ ] 2.3 Regenerar adaptadores oficiais com `openspec init --tools opencode --force` (skills em `.opencode/skills/`, commands em `.opencode/commands/`).
- [ ] 2.4 Criar `.opencode/plugin/impeccable-hook.ts` (adapter tool.execute.after + session.idle para hook.mjs).

## 3. opencode-only (remover Codex/Cursor/Claude)

- [ ] 3.1 Remover `.codex/`, `.cursor/` e `.claude/` do repo (git rm).
- [ ] 3.2 Reescrever menções a Codex/Cursor em `AGENTS.md` e `rules.md` para opencode-only.

## 4. Documentação

- [ ] 4.1 Atualizar `AGENTS.md` com camada opencode (de-para `/opsx:*`, skills auto, agents/commands/plugin, regra Impeccable).
- [ ] 4.2 Atualizar `rules.md` quando aplicável.

## 5. Validação e integração

- [ ] 5.1 Validar `opencode.json` contra o schema e config global com `jq`.
- [ ] 5.2 Restart do opencode e conferir skills, MCP, plugin, agents e commands carregados.
- [ ] 5.3 Commit na branch `change-395-migracao-opencode`, push e PR para `develop`.
- [ ] 5.4 Checks verdes e merge em `develop`.
