## Tasks

## 1. Config global (fora do git)

- [x] 1.1 Atualizar `~/.config/opencode/opencode.jsonc` com model `opencode-go/deepseek-v4-flash`.
- [x] 1.2 Criar symlinks de `~/.codex/skills/` e `/srv/knowledge/hermes-second-brain/skills/` para `~/.config/opencode/skills/` (alan-workflow, alan-workflow-ambientes, github-project-board, gh-address-comments, gh-fix-ci).

## 2. Config do projeto

- [x] 2.1 Criar `opencode.json` na raiz ($schema, model, instructions, plugin impeccable).
- [x] 2.2 Converter 4 subagents `.codex/agents/*.toml` para `.opencode/agent/*.md` (code-mapper, pr-explorer, reviewer, browser-debugger).
- [x] 2.3 Regenerar adaptadores oficiais com `openspec init --tools opencode --force` (skills em `.opencode/skills/`, commands em `.opencode/commands/`).
- [x] 2.4 Criar `.opencode/plugin/impeccable-hook.ts` (adapter tool.execute.after + session.idle para hook.mjs).
- [x] 2.5 Remover MCP `openaiDeveloperDocs` do `opencode.json` e do `~/.config/opencode/opencode.jsonc` (decisão de Alan: MCP da OpenAI não faz mais sentido).

## 3. opencode-only (remover Codex/Cursor/Claude)

- [x] 3.1 Remover `.codex/`, `.cursor/` e `.claude/` do repo (git rm).
- [x] 3.2 Reescrever menções a Codex/Cursor em `AGENTS.md` e `rules.md` para opencode-only.

## 4. Documentação

- [x] 4.1 Atualizar `AGENTS.md` com camada opencode (de-para `/opsx:*`, skills auto, agents/commands/plugin, regra Impeccable).
- [x] 4.2 Atualizar `rules.md` quando aplicável.

## 5. Validação e integração

- [x] 5.1 Validar `opencode.json` contra o schema e config global com `jq`.
- [ ] 5.2 Restart do opencode e conferir skills, MCP, plugin, agents e commands carregados. (Depende do restart da sessão do opencode — Alan reinicia e confirma.)
- [x] 5.3 Commit na branch `change-395-migracao-opencode`, push e PR para `develop`.
- [x] 5.4 Checks verdes e merge em `develop`.
