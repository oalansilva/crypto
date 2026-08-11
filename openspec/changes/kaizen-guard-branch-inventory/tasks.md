## 1. Guard: inventário de branches

- [x] 1.1 Estender seção "Orphan refs and preserve worktrees" do `scripts/release-guard` (post/audit) para inventariar branches locais `refs/heads/change-*|card-*|release-*` e remotas `refs/remotes/origin/change-*|card-*|release-*`, mostrando SHA e estado de merge (mergeado em origin/develop/origin/main ou não)
- [x] 1.2 Em `post` estrito: branch não mergeada ou mergeada mas não classificada como deletável/preservada = blocker; em `audit`: warn
- [x] 1.3 Validar que nenhuma branch do inventário tem PR aberto como head antes de sugerir deleção (`gh pr list --head <branch>`)
- [x] 1.4 Adicionar sub-seção "Package branch cleanup": com `RELEASE_BRANCHES` (env opcional), valida deleção local+remota das branches do pacote após `Pronto`; sem env, lista todas como pendência de classificação

## 2. Closeout e dívida

- [x] 2.1 Atualizar `AGENTS.md` (higiene Git/worktree/stash + release em lote): deleção das branches do pacote obrigatória após `Pronto`, com verificação pelo guard
- [x] 2.2 Rodar `scripts/release-guard audit` e classificar/limpar a dívida identificada: branches locais/remotas `change-*`/`card-*` já mergeadas em origin/develop/origin/main deletadas com evidência; `preserve/*` preservada
- [x] 2.3 Registrar limpeza da dívida (08-03 e mai-jul) com lista de branches deletadas: deletadas `change-413-wallet-zebra` (card #413 Pronto, PR #375 merged) e `change-impeccable-design-gate` (integrada, sem PR aberto); preservadas `card-463`/`card-464`/`change-456` (cards em fluxo) e `card-464` (worktree ativa); refs de 08-03/mai-jul já inexistentes após `git fetch --prune`

## 3. Validação

- [x] 3.1 `bash -n scripts/release-guard` sem erros
- [x] 3.2 Rodar `scripts/release-guard audit` e `scripts/release-guard post` (com env de evidência) validando o novo inventário
- [x] 3.3 `openspec validate --all` sem novos blockers
