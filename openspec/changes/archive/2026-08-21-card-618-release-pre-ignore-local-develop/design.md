# Design: card-618-release-pre-ignore-local-develop

Este arquivo é o **refinamento do card #618**. O issue veio primeiro; o Dev implementa **a partir daqui** (Gist). OpenSpec SHALL ser superset do issue.

## UI impact

`none` — apenas `scripts/release-guard` (seção Local branches) e teste de integração. **Não** autoriza pular colunas de Design. Código só após `Pronto para Dev`.

## Prototype

**N/A** — sem superfície visual do produto; mudança de gate operacional de release.

## Impeccable

**N/A** — `UI impact: none` (Brief / Critique / Audit / Trace não aplicáveis).

## Context

- Issue: [#618](https://github.com/oalansilva/crypto/issues/618)
- Tipo: Kaizen · Frente: Operação · Prioridade: P2 · origem F-3
- Change: `card-618-release-pre-ignore-local-develop`
- Incidente: closeout 2026-08-19; `pre` em `release-*` bloqueou com `local branch not merged: develop` enquanto `origin/develop` era a base canônica; workaround `git branch -f develop origin/develop`

Hoje, em **Local branches** (~1120–1140), `pre` já faz skip da branch atual quando ela é `release-*`, mas ainda itera `refs/heads/develop`. Se `branch_merged develop` falha (local ahead / commits locais não publicados), emite `issue "local branch not merged..."`. `PRESERVED_BRANCHES=develop` contornaria via card #581, mas é o mecanismo errado: `develop` não é WIP de card.

Paralelamente (~438–447), divergência `develop` ≠ `origin/develop` já gera **warn** (não blocker) quando a branch atual não é `develop` — inclusive em `release-*`. O BLOCKER da seção Local branches contradiz essa política.

## Goals / Non-Goals

**Goals:**

- Em `mode=pre` e `current_branch` matching `release-*`, não emitir blocker de local-branch-unmerged para a ref local `develop`.
- Não exigir `PRESERVED_BRANCHES=develop` (nem qualquer lista) para esse caso.
- Manter o warn existente quando local `develop` diverge de `origin/develop`.
- Fixture/teste de integração cobrindo: `HEAD=release-*`, `develop` local ahead de `origin/develop`, `PRESERVED_BRANCHES` unset ⇒ sem BLOCKER para `develop`.

**Non-Goals:**

- Alterar `post` / `audit` (inventário fail-closed permanece).
- Alterar comportamento quando `current_branch == develop` (strict blocker de diverge permanece).
- Auto-reset/`git branch -f` pelo guard (permanece read-only).
- Relaxar blockers de outras local branches (`card-*`, `change-*`, etc.).
- Mudar GraphQL budget, `RELEASE_CARDS`, ou dirty/worktree rules do #581.
- UI / produto / board Status.

## Decisions

### D1 — Skip incondicional de `develop` no inventário Local branches (pre + release-*)

**Escolha:** quando `mode == pre` **e** `current_branch` casa `release-*` **e** `branch == develop`, `continue` (não chamar `branch_merged` / não emitir issue).

**Alternativa A (rejeitada):** só skip se `origin/develop` for ancestral ou “aligned” com algum critério extra — ambíguo; o warn de diverge já cobre divergência; `branch_merged` é exatamente o que falha no incidente.

**Alternativa B (rejeitada):** exigir/`sugerir` `PRESERVED_BRANCHES=develop` — contradiz aceite PO; mistura integração canônica com preserve de WIP.

**Alternativa C (rejeitada):** sempre ignorar `develop` em qualquer `pre` (também em `main`/`develop`) — fora do escopo do incidente; em `develop` o strict diverge já protege.

**Rationale:** em closeout o operador está em `release-*`; a autoridade de merge-base já é `origin/develop`. Ref local stale/ahead é ruído operacional, não risco de publicar conteúdo errado.

### D2 — Não classificar via warn “PRESERVED”; skip silencioso ou log mínimo

Skip sem exigir log de `PRESERVED_BRANCHES`. Opcional: uma linha informativa (`Skipping local develop on release-* pre; release decisions use origin/develop`) — não é blocker nem warn de preserve. Preferir log curto se o teste precisar de âncora; senão, ausência do BLOCKER basta.

### D3 — Warn de diverge permanece

Não remover/alterar o bloco ~438–447. Continua: warn se local ≠ origin quando não estamos em strict+`develop`. Assim o operador ainda vê que a ref local está desalinhada, sem falhar o `pre`.

### D4 — Teste / fixture

Em `backend/tests/integration/test_release_guard.py`:

1. Repo fixture padrão (`_init_repo`).
2. Criar `release-2026-08-19` (ou similar) a partir de `main`/`develop` alinhados.
3. Em `develop`: commit extra **não** pushed (ahead de `origin/develop`).
4. Checkout `release-*`.
5. `_run_guard(repo, "pre")` **sem** `preserved_branches`.
6. Assert: ausência de `BLOCKER: local branch not merged...: develop` (e idealmente `Result: PASS` se demais seções ok).
7. Controle negativo opcional (mesmo turno ou task separada): outra branch local unmerged (`card-999-wip`) **ainda** bloqueia.

### D5 — Spec delta

Capability existente `release-worktree-hygiene` — **ADDED** requirement (não inflar o bloco PRESERVED do #581). Sem capability nova `release-pre-local-develop`.

## Risks / Trade-offs

| Risk | Mitigation |
| --- | --- |
| Operador interpreta skip como “local develop está ok para push” | Warn de diverge permanece; copy do log (se houver) aponta `origin/develop` |
| Esconder diverge real que deveria falhar o lote | Authority já é `origin/*`; conteúdo do pacote vem de `release-*` / PRs, não da tip local de `develop` |
| Regressão: outras branches deixam de bloquear | Skip **somente** nome exato `develop` + pre + `release-*`; teste negativo com `card-*` |
| `post` ainda reclama de develop local | Aceito / Non-Goal; closeout `post` tem regras próprias |

## Migration Plan

Nenhuma migração de dados. Após merge em `develop`: closeouts em `release-*` param de precisar de `git branch -f develop origin/develop` só por causa deste blocker. Rollback = reverter o skip no script.

## Open Questions

Nenhuma bloqueante. Aceite PO fecha a escolha D1.

## Design Critique

**Crítico:** Task isolada (inherit, read-only) · 2026-08-21  
**Artefatos:** `proposal.md`, `design.md`, `tasks.md`, `specs/release-worktree-hygiene/spec.md`  
**Código de referência (não alterado):** `scripts/release-guard` Local branches ~1119–1141; warn diverge ~438–447  
**Prototype:** N/A — sem superfície visual; mudança só em release-guard + teste de integração  
**Impeccable Brief / Critique / Audit / Trace:** N/A — `UI impact: none`

### Escopo
- Decisão D1 (skip incondicional de `develop` em `pre` + `HEAD=release-*`) resolve o incidente F-3 sem misturar com `PRESERVED_BRANCHES` (D2).
- Non-goals claros: `post`/`audit`, strict em `develop`, auto-`branch -f`, outras locals, GraphQL/#581.
- Spec ADDED na capability existente; três cenários alinhados ao aceite PO.

### Regressão operacional
- Warn de diverge (~438–447) permanece → operador ainda vê desalinhamento local vs `origin/develop`.
- Skip só com nome exato `develop` + `pre` + `release-*` → risco de mascarar WIP de card controlado por teste negativo.
- Autoridade de release continua em `origin/*`; tip local de `develop` não alimenta o pacote.

### UI
- Confirmado: nenhuma superfície visual nova/alterada; Prototype/Impeccable N/A justificados.

### Achados
| Sev | Dimensão | Achado | Disposição |
|-----|----------|--------|------------|
| P2 | Coerência | D4 marca controle negativo como opcional; tasks 2.2 + spec exigem | Aceito no design; Apply deve implementar o negativo (já em tasks) |
| P2 | Teste | Garantir `PRESERVED_BRANCHES` unset de verdade no fixture (pop de env) | Aceito; Apply |
| nit | Spec | MAY no warn vs D3 “não remover” | Aceito; preferência de implementação = manter warn |

**P0/P1 abertos:** nenhum

**Design Agent verdict: PASS**
