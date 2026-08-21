# Tasks: card-618-release-pre-ignore-local-develop

## Design (este turno)

- [x] 0.1 OpenSpec proposal + design + delta `release-worktree-hygiene` + tasks (UI none; Prototype/Impeccable N/A; Design Critique placeholder)
- [x] 0.2 Crítica independente (Task isolada) e preencher `## Design Critique` / veredito antes do handoff para Aprovação de Design
- [x] 0.3 Publicar Gist OpenSpec no card #618 (após crítica PASS)

## Apply (após Pronto para Dev)

## 1. release-guard Local branches

- [x] 1.1 Em `scripts/release-guard`, na seção Local branches: se `mode=pre` e `current_branch` casa `release-*` e `branch == develop`, skip (não emitir unmerged blocker); sem exigir `PRESERVED_BRANCHES=develop`
- [x] 1.2 Confirmar que o warn existente de `develop` ≠ `origin/develop` permanece; não alterar `post`/`audit` nem skip de outras branches

## 2. Teste / fixture

- [x] 2.1 Em `backend/tests/integration/test_release_guard.py`: fixture com `HEAD=release-*`, local `develop` ahead de `origin/develop`, `PRESERVED_BRANCHES` unset ⇒ assert ausência de BLOCKER `local branch not merged...: develop`
- [x] 2.2 Controle negativo no mesmo arquivo: outra local unmerged (`card-*`) sem lista ainda bloqueia em `pre` + `release-*`

## 3. Verificação

- [x] 3.1 Rodar o(s) teste(s) novos (e regressão mínima dos testes PRESERVED/local-branch existentes) — 2 passed
- [x] 3.2 `/opsx:verify` contra aceite PO antes de Code Review
