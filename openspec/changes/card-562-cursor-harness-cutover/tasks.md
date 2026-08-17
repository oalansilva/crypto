## 1. Board e OpenSpec

- [x] 1.1 Cancelar #561 com comentário de substituição
- [x] 1.2 Criar #562 no Project 1 (P0, Operação, Código, Codex) com `qa-visual-skip`
- [x] 1.3 Publicar proposal/design/specs/tasks no card (Gist)

## 2. Camada Cursor

- [x] 2.1 Criar `.cursor/rules/` alwaysApply (harness, modelo do chat, Design gate, review, visão)
- [x] 2.2 Gerar/copiar skills OpenSpec e commands `/opsx-*` + `/kaizen` em `.cursor/`
- [x] 2.3 Criar `.cursor/hooks.json` + adapter para `hook.mjs` (`afterFileEdit`, `stop`)
- [x] 2.4 Copiar skills globais para `~/.cursor/skills/`

## 3. Contrato

- [x] 3.1 Reescrever `AGENTS.md` e `rules.md` (Cursor único, sem Sol/Qwen/guard)
- [x] 3.2 Atualizar `.agents/skills/design-critic/SKILL.md`
- [x] 3.3 Atualizar `docs/decision-log.md` e `docs/backlog-operating-model.md`
- [x] 3.4 Atualizar README do Project 1 (roteamento Codex/Luna/OpenCode obsoleto)

## 4. Cutover OpenCode

- [x] 4.1 Remover `.opencode/` e `opencode.json`
- [x] 4.2 Remover job CI `design-gate-contract` e conferir branch protection
- [x] 4.3 Remover `.agent/workflows/opsx-*`

## 5. Kaizen

- [x] 5.1 Trocar fonte de sessão para transcripts Cursor no command/skill kaizen

## 6. Verify

- [x] 6.1 `openspec validate --change card-562-cursor-harness-cutover` (e `--all` se o card quebrar o global)
- [x] 6.2 Confirmar que sessão Cursor descobre rules/skills/commands sem `.opencode`
- [x] 6.3 Checklist de gates no PR (change, design verdict, UI impact, evidência de aprovação)
