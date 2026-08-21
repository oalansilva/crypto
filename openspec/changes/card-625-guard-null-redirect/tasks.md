# Tasks: card-625-guard-null-redirect

## 1. Guard classification (null /tmp allowlist)

- [x] 1.1 Em `scripts/process-fsm/guard.py`, extrair alvos de `>` / `>>` / `tee` e allowlistar quando o alvo for `/dev/null` ou sob `/tmp` (não promover path de produto citado noutro token a `write_produto`)
- [x] 1.2 Preservar deny quando qualquer alvo de redirect/`tee` cair em `product_globs` (relativo ou absoluto mapeado para o repo fora de `/tmp` e `/dev/null`); manter `sed -i` / `cp` / `mv` / `install` / `perl -i` inalterados
- [x] 1.3 Espelhar a mesma allowlist no fallback bash de `.cursor/hooks/process-fsm-guard.sh` antes de promover path de produto

## 2. Fixtures e regressão

- [x] 2.1 Em `test_guard.py`, fixture envelope `beforeShellExecution`: comando que cita `backend/` (ou `frontend/src/`) com redirect só para `/dev/null` e Status fora de I1 ⇒ `allow`
- [x] 2.2 Fixture equivalente com alvo sob `/tmp` ⇒ `allow`
- [x] 2.3 Fixture true deny: redirect/`tee` sobre path de produto fora de I1 ⇒ `deny` (manter/estender `test_shell_redirect_denied` / `test_shell_tee_denied` / colados/absolutos)
- [x] 2.4 Regressão: `pytest backend/ -q` sem mutação ⇒ `allow`

## 3. Verificação

- [x] 3.1 Rodar `pytest scripts/process-fsm -q` e confirmar verde (149 passed)
- [x] 3.2 Confirmar que nenhum arquivo de produto backend/frontend/UI foi alterado neste card
