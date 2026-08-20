## 1. Resolver

- [x] 1.1 Implementar `scripts/process-fsm/resolve.py` (cwd, path, issue_id opcional → q_git, bound_card, q opcional)
- [x] 1.2 q_git pelo worktree do **path**; mismatch de **ids de card** (cwd card ≠ path card, ou issue_id ≠ path) ⇒ bound_card=⊥; cwd em develop + path em card-<id> ⇒ bound_card=id do path
- [x] 1.3 develop/main/unbound ⇒ bound_card=⊥

## 2. Testes

- [x] 2.1 Fixtures cwd≠path, develop, main, unbound; sem GitHub
- [x] 2.2 `pytest scripts/process-fsm -q` inclui os testes novos

## 3. Fora de escopo

- [x] 3.1 Diff NÃO altera `.cursor/hooks.json`, `backend/`, `frontend/src/`
