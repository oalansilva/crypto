# Design — card-438-release-guard-doc-board-fields

## Context

Fechamento da release 2026-08-09: evidência documental do deploy PROD ficou só no worktree (doc com placeholders em develop/main; dois docs de release da mesma data em paralelo — F-1) e cards do pacote com campos vazios (#413/#416 sem Responsável/Prioridade; #416 título divergente — F-2).

## Escopo

- `release-guard post`:
  - falha se doc do pacote com placeholder não commitada;
  - falha se 2+ docs de release da mesma data com conteúdo divergente;
  - falha se card do pacote sem Responsável/Prioridade/Tipo;
  - consistência título board/issue (vínculo #430).

## UI impact

`UI impact: none` — script bash de guard + docs; nenhuma superfície visual. Prototype: `N/A`.

## Decisões

- **D1 — Placeholder = padrão de template não preenchido.** Detecção por marcadores conhecidos de template (`<!--`, `TBD`, `TODO`, `<...>`, "lorem") na doc do pacote; falha em modo estrito com o caminho da doc. Alternativa (parse semântico do doc) excessiva para o caso.
- **D2 — Doc canônica por data.** O guard detecta múltiplas `docs/release-<data>*.md` na mesma data e compara conteúdo; divergência = blocker instruindo consolidação. Alternativa (convenção de nome rígida) quebraria docs legadas (`-d` sufixo).
- **D3 — Campos do board via `gh project`.** O guard consulta o board (item-list + field-list) para os cards do pacote (lista de issues em `Pronto`/pacote) e valida Responsável/Prioridade/Tipo não vazios; falha em modo estrito. Alternativa (checklist manual no doc) volta à disciplina manual que falhou.

## Riscos

- [Dependência de `gh` autenticado com escopo project no guard] → Mitigação: falha com mensagem clara de auth; guard é de fechamento, ambiente já tem gh.
- [Docs legadas da mesma data quebram o check] → Mitigação: divergência é julgada por conteúdo, não apenas por nome; consolidação guiada pelo output.
- [Campos sem opção válida no board] → Mitigação: o guard apenas exige valor não vazio; semântica do valor é responsabilidade do PO.

## Design Critique

- **Escopo**: fecha F-1/F-2 com validação automatizada no único ponto de fechamento (guard post).
- **Regressão de produto**: nenhuma — guard de processo.
- **Riscos operacionais**: guard mais estrito exige disciplina documental do pacote; mitigado por output com instruções e critérios de aceite explícitos.
- **Pendências não bloqueantes**: docs legadas duplicadas serão tratadas na próxima execução (esperado).
- **Impeccable**: `N/A` — sem superfície visual; justificativa: `UI impact: none`.

**Design Agent verdict: PASS** — evidência completa, sem achado bloqueante.
