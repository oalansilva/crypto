## Context

Alan passa a usar opencode como ferramenta principal de desenvolvimento no lugar do Codex. **Decisão revisada: opencode será a ferramenta única** — Codex e Cursor deixam de ser usados, e seus adaptadores no repo são removidos. A migração precisa preservar as capacidades operacionais que hoje existem no Codex: MCP `openaiDeveloperDocs`, subagents de exploração/revisão (code-mapper, pr-explorer, reviewer, browser-debugger), slash commands `/opsx-*`, hook de proteção de design system (impeccable) e skills globais de operação (alan-workflow, GitHub Project, gh-address-comments, gh-fix-ci).

O opencode carrega automaticamente as skills do projeto em `.agents/skills/` (design-critic, impeccable, playwright-cli) e `.opencode/skills/` (openspec-*, regeneradas com a CLI 1.5.0).

## Decisions

- `UI impact: none` — mudança exclusivamente de ferramenta de desenvolvimento e documentação de processo; nenhuma tela, componente ou comportamento de produto é alterado.
- **opencode-only:** Codex e Cursor deixam de ser usados; `.codex/`, `.cursor/` e `.claude/` (adaptadores openspec de clientes legados) são removidos do repo. `AGENTS.md` e `rules.md` passam a referenciar apenas o opencode.
- Config versionada: `opencode.json` na raiz (schema, model, MCP, plugin) + `.opencode/` (agents, commands, plugin, skills openspec). Config global fora do git: `~/.config/opencode/opencode.jsonc` (model default e MCP) e `~/.config/opencode/skills/` (symlinks).
- Skills openspec: fonte única em `.opencode/skills/openspec-*` (geradas por `openspec init --tools opencode --force`), sem duplicação de nomes com outras localizações.
- Subagents: converter os 4 TOML do Codex para `.opencode/agent/*.md` com `mode: subagent`; read-only mantém `permission: edit: deny`; browser-debugger mantém escrita restrita a diagnósticos.
- Commands `/opsx-*`: adaptadores oficiais gerados pela CLI em `.opencode/commands/opsx-*.md`.
- Plugin impeccable: adapter em `.opencode/plugin/impeccable-hook.ts` mapeando `tool.execute.after` (≈ PostToolUse) e `session.idle` (≈ Stop) para o detector `.agents/skills/impeccable/scripts/hook.mjs`, sem alterar o contrato canônico da skill.
- Skills globais: symlinks de `~/.codex/skills/` e `/srv/knowledge/hermes-second-brain/skills/` para `~/.config/opencode/skills/`, mesmo padrão já usado pelo Codex.
- Não migrar: `.agent/` legado, skills genéricas do Codex (api/backend/frontend/etc.), `~/.codex/rules/default.rules` (permissões hermes/legado) e `~/.codex/auth.json` (opencode já tem auth própria no provider `opencode-go`).

## Goals / Non-Goals

**Goals:**
- opencode com paridade operacional ao Codex para o fluxo de cards do cripto.
- Config e skills versionadas/documentadas no repo.
- Proteção impeccable ativa no opencode.

**Non-Goals:**
- Manter Codex/Cursor como clientes — decisão opencode-only; adaptadores legados removidos.
- Alterar runtime, banco, API ou UI de produto.
- Migrar credenciais do Codex para o opencode.

## Risks

- Config inválida quebra o startup do opencode — mitigado validando contra `https://opencode.ai/config.json` antes do commit.
- Hook impeccable fora do padrão de payload do Codex — mitigado com adapter no plugin e teste real pós-restart.
- Commands convertidos divergirem das skills — mantém corpo fiel ao `.cursor/commands/` original e referência às skills como fonte de verdade.

## Prototype

`N/A` — sem superfície visual nova ou alterada (migração de ferramenta de desenvolvimento, `UI impact: none`). Não há protótipo, HTML navegável, nem mudança em `frontend/**`.

## Design Critique

Sem UI, a crítica cobre escopo, regressão de produto e riscos operacionais:

- **Escopo:** adequado — apenas configuração de ferramenta dev, docs de processo e arquivos `.opencode/`; zero impacto em runtime de produto.
- **Regressão de produto:** nenhuma — nenhum arquivo de backend/frontend/banco é alterado; as mudanças de `AGENTS.md`/`rules.md` já existentes (remoção da skill `caveman`) são de processo e entram no mesmo pacote.
- **Riscos operacionais:** (1) restart do opencode necessário para ativar plugin/MCP; (2) validação manual pós-restart obrigatória (skills, MCP, plugin, agents, commands); (3) symlinks globais dependem de caminhos de conhecimento (hermes-second-brain) que já são padrão no Codex.
- **Achados bloqueantes:** nenhum.
- **Pendências não bloqueantes:** execução da validação pós-restart fica registrada no card antes do `Done`; criação do card/issue já feita (#395, Status=Design).

`Design Agent verdict: PASS` — sem achados bloqueantes, `UI impact: none`, Prototype `N/A` justificado.
