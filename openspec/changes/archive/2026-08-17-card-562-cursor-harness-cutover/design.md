## Context

Alan invertou o destino do #561: o harness ativo passa a ser o Cursor Agent, com o modelo do chat em todos os papéis. O processo Kanban/OpenSpec permanece. O cadeado OpenCode (lease, packet, attestation 1.18.18) não será portado — foi o que travou #555/#559.

## Goals

- Um cliente (Cursor) no contrato ativo.
- OpenSpec via CLI + skills/commands Cursor.
- Design gate auditável sem plugin de isolamento.
- Visão e review no mesmo modelo da sessão.
- Remover OpenCode do estado ativo e da CI.

## Non-Goals

- Publicar em PROD.
- Workflow DB v1 / attestation externa.
- Portar `design-gate-guard`.
- Manter OpenCode como fallback oficial.
- Reescrever OpenSpecs arquivados.

## Decisions

1. **Harness = Cursor.** `.cursor/` é a config versionada. `.opencode/` e `opencode.json` saem do estado ativo.
2. **Modelo = seletor do chat.** Hoje Grok 4.6. Sem Sol/Pro/Qwen obrigatórios. Subagents usam `inherit` salvo pedido explícito.
3. **Gate Design simples.** Author = sessão Cursor. Critics = `Task` isolada, mesmo modelo, instrução de não editar. Isolamento é de processo, não de plugin.
4. **Revogar Sol obrigatório no Design.** Mitigação: crítica isolada + aprovação humana. Se a qualidade cair, o ajuste futuro é “Sol só no Design”, não reconstruir o guard.
5. **Visão na sessão.** Grok 4.6 lê PNG/JPEG via `Read`. Sem `vision-router`. Path-check antes de abrir o arquivo permanece.
6. **Impeccable.** Detector `hook.mjs` inalterado. Adapter Cursor em `.cursor/hooks.json` (`afterFileEdit` + `stop`).
7. **Kaizen.** Transcripts Cursor do projeto, não `opencode.db`.
8. **CI.** Remover job `design-gate-contract`. Se for required no branch protection, remover o required.

## UI impact

`none` — tooling/docs/CI, nenhuma superfície de produto.

## Prototype

N/A. Card de harness sem tela. Justificativa: zero HTML/CSS de produto; Alan valida o contrato (docs + `.cursor/` + ausência de `.opencode` ativo), não um mock.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Risks / Trade-offs

- [Qualidade de spec sem Sol] → Mitigação: crítica em Task + Alan em `Pronto para Dev`. Rollback de processo: voltar Sol só no Design.
- [Critic pode ter tools] → Mitigação: prompt read-only; evidência no `design.md`; não há cadeado.
- [CI vermelha se `design-gate-contract` for required] → Mitigação: inspecionar branch protection e remover o contexto.
- [Kaizen cego sem transcripts] → Mitigação: documentar o path canônico e declarar fonte indisponível se ausente.
- [Worktree suja `unify-strategy-*`] → Fora de escopo; não entra neste commit.

## Migration Plan

1. Publicar OpenSpec no #562.
2. Implementar `.cursor/` + docs.
3. Apagar OpenCode/CI do guard.
4. Copiar skills globais para `~/.cursor/skills/`.
5. Validar `openspec validate` e smoke de sessão nova.

## Open Questions

Nenhuma pendente do brainstorm.

## Design Critique

- Escopo: cutover de harness; processo Kanban intacto.
- Regressão de produto: nenhuma (sem API/UI/banco).
- Riscos operacionais: isolamento do critic é processual; Sol no Design revogado de propósito.
- Superfície visual nova: nenhuma (`UI impact: none`).

## Prototype Validation

N/A — sem protótipo navegável.

Design Agent verdict: PASS
