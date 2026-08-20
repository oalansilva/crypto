## Context

Card [#610](https://github.com/oalansilva/crypto/issues/610), filho 2/5, após [#609](https://github.com/oalansilva/crypto/issues/609) em `develop` (`ff85eb71`). Fecha cwd≠path. O Guard (#611) consome este resolver.

**UI impact: none.** Prototype N/A. Impeccable N/A.

## Goals / Non-Goals

**Goals:**

- Função `resolve(cwd, path, issue_id=None, status=None)` → `{q, bound_card, q_git}`.
- `q_git` pelo `git` do diretório do **arquivo**, não do cwd da sessão.
- `bound_card=⊥` se ids de card divergem (cwd card ≠ path card, ou `issue_id` ≠ path), ou se o path não é `card-<id>-*`.
- Testes com worktrees fake, sem `gh`.

**Non-Goals:**

- Deny de Write / hook (#611).
- `process_event` (#612), paging (#613).
- Consulta paginada ao Project 1. `q` nos unitários é injetado (`status=`) ou `None`; live Status é do Guard com query pontual.

## Decisions

1. **Reusar `scripts/process-fsm/`** do #609 (não novo top-level). `resolve.py` ao lado de `fsm.py`.
2. **`q_git`:** `git -C <dir do path absoluto> rev-parse --abbrev-ref HEAD` **verbatim** (não colapsar `card-*` num enum). Falha/detached ⇒ `⊥`. Path relativo resolve contra cwd **antes** de `git -C`; se o path for diretório, `git -C` nesse diretório (não no pai).

3. **`bound_card` vs `q_git` (tabela canônica).** `q_git` é sempre a branch do worktree **do path**. `bound_card` = id `card-<id>` **do path**, salvo conflito de ids — aí `⊥`. `cwd≠path` nas tasks = **ids de card diferentes**, não cwd em `develop`.

| cwd branch | path branch | issue_id | bound_card | q_git |
| --- | --- | --- | --- | --- |
| `card-610-*` | `card-610-*` | 610 ou omitido | `610` | branch do path |
| `card-605-*` | `card-610-*` | qualquer | `⊥` | branch do path |
| `develop`/`main` | `card-610-*` | — | `610` | branch do path |
| qualquer | `develop`/`main` | — | `⊥` | `develop`/`main` |
| qualquer | `change-<id>-*` / detached / sem git | — | `⊥` | `⊥` (detached/sem git) ou nome cru se ainda for branch |
| `card-610-*` | `card-610-*` | 605 | `⊥` | branch do path |

`⊥` canônico na API Python: string `"⊥"` (o #609 já trata `None`/`""`/`"⊥"`). `q` é pass-through do argumento `status=` (ou `None`); sem `gh` neste card.

## Risks / Trade-offs

- [Detached HEAD] → `q_git=⊥`, `bound_card=⊥`.
- [Branch `change-<id>`] → I1 do yaml só casa `card-*`; resolver não inventa id.
- [Live Status] → fora; sem `gh` no unitário.

## Migration Plan

Aditivo. Rollback = reverter o módulo.

## Open Questions

Nenhuma bloqueante.

## UI impact

**none** — resolver/harness. Prototype N/A. Impeccable N/A.

## Prototype

N/A — `UI impact: none`.

## Prototype Validation

N/A.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Design Critique

Recrítica isolada (read-only) após P1 de `bound_card`. Fontes: `proposal.md`, `design.md` (Decision 3 + tabela), `tasks.md`, `specs/process-fsm-resolver/spec.md`. Card #610, change `card-610-process-fsm-resolver`. Prototype: N/A. Impeccable: N/A (`UI impact: none`).

### Dimensões

- **Escopo:** resolver `(q, bound_card, q_git)` em `scripts/process-fsm/`; yaml #609 só lido; hook/`preToolUse` (#611), `process_event` (#612), paging (#613) e produto fora. Sem superfície visual nova/alterada.
- **Produto / processo:** I1 do yaml continua exigindo `q_git=card-<id>` ∧ `bound_card=id` ∧ path desse worktree; o resolver classifica pelo worktree do **arquivo**, não pelo cwd da sessão.
- **Operação:** unitários com worktrees fake; `q` injetado (`status=`) ou `None`; sem `gh`/board.
- **UI / a11y / responsivo / estados visuais:** N/A — harness.

### P1 anterior (fechado)

Contrato de `bound_card` era não-determinístico (`cwd≠path` vs cwd `develop` + path `card-610-*`). Agora a tabela canônica (Decision 3) + spec SHALL + task 1.2 pinam:

- `q_git` = `rev-parse --abbrev-ref HEAD` do worktree do **path** (verbatim; falha/detached ⇒ `⊥`).
- `bound_card` = id `card-<id>` **do path**, salvo conflito de ids (cwd card ≠ path card, ou `issue_id` ≠ path) — aí `⊥`. Path não-`card-<id>-*` ⇒ `⊥`.
- cwd `develop`/`main` + path `card-610-*` ⇒ `bound_card=610`, `q_git` = branch do path.
- path em `develop`/`main` ⇒ `bound_card=⊥`, `q_git` = `develop`/`main`.

### Achados desta rodada

- **P0 / P1:** nenhum.
- **P2 (aceitos, não bloqueiam):** task 1.3 ainda diz `develop/main/unbound ⇒ bound_card=⊥` sem dizer *path* — a 1.2 e o spec desambiguam.

### Pendências não bloqueantes

Apply implementa a tabela; #611 consome o triple. Aprovação humana permanece de Alan.

Design Agent verdict: PASS

## Design Agent verdict

PASS — crítica isolada inherit (recrítica após P1 de `bound_card`). Prototype N/A. Impeccable N/A.
