# Design — card-423-publish-helper-gist-update

## Context

Republicações de artefatos OpenSpec criaram 3 Gists e 3 comentários quase idênticos por card (#361, #399 — F-3), e ajustes pós-review commitados um a um geraram PRs fragmentados e commit vazio de retrigger de CI (F-4, #384: 5 PRs; #399: 4 PRs; #395: 2 PRs).

## Escopo

- Helper `publish-openspec-card-artifacts.sh`: aceitar `--gist-id <id>` e atualizar o Gist existente (criar só na primeira publicação); manter instrução no AGENTS.md.
- Retrigger de CI via `workflow_dispatch` (`gh workflow run`) documentado/scriptado — sem commit vazio.
- Orientação de agrupar ajustes pós-review em um único commit/PR.
- Fora de escopo: correção retroativa dos Gists já criados.

## UI impact

`UI impact: none` — script bash + docs; nenhuma superfície visual. Prototype: `N/A`.

## Decisões

- **D1 — `--gist-id` explícito, sem auto-busca.** O chamador informa o Gist da change em republicações; o helper atualiza arquivos via `gh gist edit`. Alternativa (buscar por description `crypto openspec <change>`) mais propensa a colisões com mudanças de slug/descrição; o id explícito é auditable.
- **D2 — Comentário do card: atualizar em vez de duplicar.** Na republicação com `--gist-id`, o helper não cria novo comentário; registra a atualização do Gist (via edição do comentário anterior quando o `--comment-id` for informado, senão apenas reporta gist atualizado). Mantém 1 comentário OpenSpec por card.
- **D3 — Retrigger via `gh workflow run` com workflow/ref explícitos.** Documentar o comando real no AGENTS.md; commit vazio fica proibido como retrigger.
- **D4 — Agrupamento de ajustes pós-review em 1 commit/PR.** Regra de fluxo no AGENTS.md (docs) — sem script adicional.

## Riscos

- [Edição do Gist errado por id incorreto] → Mitigação: o id é fornecido pelo chamador a partir da publicação anterior; helper valida `gh gist view <id>` antes de editar.
- [`gh gist edit` indisponível em algum ambiente] → Mitigação: fallback documentado via `gh gist edit` padrão do CLI; teste manual no fechamento.

## Design Critique

- **Escopo**: ataca diretamente o sprawl de Gists/comentários e os commits vazios de retrigger, ambos com evidência de 2+ cards.
- **Regressão de produto**: nenhuma — helper de processo.
- **Riscos operacionais**: alteração de comportamento do helper exige revisão do fluxo de publicação; mitigado por testes manuais na primeira republicação pós-implementação.
- **Pendências não bloqueantes**: comentários antigos duplicados não serão corrigidos retroativamente (fora de escopo).
- **Impeccable**: `N/A` — sem superfície visual; justificativa: `UI impact: none`.

**Design Agent verdict: PASS** — evidência completa, sem achado bloqueante.
