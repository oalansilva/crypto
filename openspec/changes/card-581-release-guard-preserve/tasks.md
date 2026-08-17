# Tasks: card-581-release-guard-preserve

## Design (este turno)

- [x] 0. OpenSpec superset do issue #581 (crítica + Gist; WIP de código não conta como apply)

## Apply (após Pronto para Dev)

- [x] 1. Worktrees + Local branches no `pre`: `PRESERVED_BRANCHES` com trim, zero GraphQL; extra mergeada = warn; dirty só `docs/release-${RELEASE_DATE}.md` em mergeada = permitido; porcelain rename = blocker
- [x] 2. Descartar rascunho com `ensure_board_snapshot`; extrair `branch_is_preserved` com trim também para o `post`
- [x] 3. `AGENTS.md`: exportar `PRESERVED_BRANCHES` já no `pre`
- [x] 4. Evidência: PASS extra+dirty-preserve; PASS local unmerged+lista; PASS extra mergeada + dirty só release-doc da data; FAIL extra/local sem lista; FAIL dirty de código
