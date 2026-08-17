# Design: card-581-release-guard-preserve

Este arquivo é o **refinamento do card #581**. O issue veio primeiro; o Dev implementa **a partir daqui** (Gist). OpenSpec SHALL ser superset do issue.

## UI impact

`none` — `scripts/release-guard` e higiene de worktree. **Não** autoriza pular colunas de Design. Código/`release-guard` só após `Pronto para Dev`.

## Prototype

**N/A** — sem superfície visual do produto.

## Impeccable

**N/A** — `UI impact: none`.

## Origem

- Issue: [#581](https://github.com/oalansilva/crypto/issues/581)
- Tipo: story (processo) · Frente: Operacao · Prioridade: P2 · label `kaizen`
- Change: `card-581-release-guard-preserve`
- Incidente: `pre` 2026-08-17 lote 2; worktrees extras; branch local `card-569-code-review-bugbot`

## Card primeiro, OpenSpec mais completo

Issue = intenção. Gist = contrato do Dev.

## Problema

O `pre` falha em dois lugares distintos:

1. Seção **Worktrees**: qualquer extra ⇒ blocker; qualquer dirty ⇒ blocker.
2. Seção **Local branches** (~1013): **toda** ref local não mergeada em `origin/develop`/`origin/main` ⇒ `issue "local branch not merged..."`. Este foi o segundo blocker do #569.

`PRESERVED_BRANCHES` só é lido no inventário de branches do **`post`/`audit`**. Cards em Design/Aprovação de Design e worktrees de cards já mergeados com checklist `docs/release-<data>.md` derrubam o `pre`. O operador é forçado a commit vazio ou a apagar WIP in-flight.

## Decisões

### D1 — Sem GraphQL no `pre`

O spec vigente exige `pre` com **zero** `item-list`. Classificar “card não terminal no board” **dentro do `pre`** exigiria snapshot — **proibido**.

Aceite do issue: não bloquear quando listada em `PRESERVED_BRANCHES`.

- In-flight = operador exporta `PRESERVED_BRANCHES` **já no `pre`**.
- `pre` MUST NOT chamar `ensure_board_snapshot` / `ensure_snapshots` / `item-list` / `card_lookup`.
- Unknown de board nunca constitui preserve — irrelevante no `pre` sem snapshot.

**WIP nesta worktree (`scripts/release-guard` modificado):** rascunho inválido (`ensure_board_snapshot` no `pre` + preserve via board). **Não commitar.** Apply reescreve: preserve só via `PRESERVED_BRANCHES` (trim, match exato) nas seções Worktrees **e** Local branches.

### D2 — Extra worktree e branch local

**Worktrees** (`wt != repo_root`):

| Classificação | `pre` |
| --- | --- |
| `wt_branch` ∈ `PRESERVED_BRANCHES` | não blocker; log classified preserved |
| branch mergeada em `origin/develop` (`branch_merged` no HEAD da worktree) | não blocker; **warn** para remover no closeout (sem commit vazio) |
| demais / detached | blocker extra worktree |

Extra mergeada = warn **independente** da lista. Lista cobre in-flight **não** mergeado.

**Local branches** (a lacuna do incidente):

| Classificação | `pre` |
| --- | --- |
| `branch` ∈ `PRESERVED_BRANCHES` | **não** emitir `local branch not merged...`; log/warn classified preserved |
| `branch_merged` | ok (hoje) |
| demais | blocker atual |

Zero `card_lookup` nesta seção também. Current branch continua excluída como hoje. `release-*` current no `pre` continua skip.

### D3 — Dirty worktree

| Caso | `pre` |
| --- | --- |
| Dirty + `PRESERVED_BRANCHES` | **warn**, não blocker |
| Branch mergeada e **todos** os paths sujos/untracked = exatamente `docs/release-${RELEASE_DATE}.md` | permitido (checklist da data); log explícito |
| Dirty com qualquer outro path | blocker, mesmo se mergeada |
| Dirty sem classificação | blocker |

Parse porcelain fail-closed: path = `${line:3}` após status codes; rename (` -> `) **não** conta como checklist — blocker. Não alargar a `docs/**` nem `docs/kaizen-log.md`. Não usar glob `docs/release-*.md` (qualquer data) nem o padrão frouxo do rascunho `docs/release-*-*.md`.

Reutilizar `branch_merged` no HEAD da worktree para extra **e** dirty.

### D4 — Closeout

Cards já em `origin/develop`: remover worktree no closeout **sem** commit vazio. Guard permanece read-only (não apaga). `post` continua fail-closed para dirty não classificado.

Extrair `branch_is_preserved` **com trim** e reutilizar no `post` (hoje `card-569, card-581` com espaço pode falhar o match).

### Fora de escopo

- Autodelete de worktree pelo guard.
- Relaxar dirty de código in-flight.
- Dual-write / mudar orçamento GraphQL do `pre`.
- #579, #580.

## Critérios de aceite (do issue)

- `pre` não bloqueia **branch/worktree** de card em Design/Aprovação de Design quando listada em `PRESERVED_BRANCHES`.
- Worktree de card já em `origin/develop` pode ser considerada não-dirty se o único delta for `docs/release-${RELEASE_DATE}.md`; extra mergeada = warn, não blocker.

## Implementação (somente `Status=Pronto para Dev`)

1. `branch_is_preserved` com trim; usar no `pre` (Worktrees + Local branches) e no `post`.
2. D2/D3; glob canônico da data; porcelain fail-closed.
3. Descartar rascunho com snapshot no `pre`.
4. `AGENTS.md`: exportar `PRESERVED_BRANCHES` já no `pre`.
5. Evidência: PASS extra+dirty-preserve; PASS local unmerged+lista; PASS extra mergeada + dirty só release-doc da data; FAIL extra/local sem lista; FAIL dirty de código em mergeada.

## Design Critique

Crítica isolada: **BLOCKED** inicial — P0 seção Local branches fora do contrato (`pre` ainda falharia o #569); P1 glob `docs/release-*.md` largo demais.

**Resolução:** D2 inclui Local branches; D3 glob = `docs/release-${RELEASE_DATE}.md` + porcelain fail-closed.

Re-crítica isolada: P0/P1 fechados. WIP com `ensure_board_snapshot` no `pre` permanece rascunho inválido e MUST ficar uncommitted. Prototype/Impeccable N/A. P2 proposal (glob/Impact) alinhado na republicação.

## Design Agent verdict

**PASS** — UI N/A; OpenSpec superset do issue #581. Pronto para Aprovação de Design (Alan). Código do rascunho **não** entra até Pronto para Dev.
