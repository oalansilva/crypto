## 1. Paging module

- [x] 1.1 Implementar `scripts/process-fsm/paging.py`: `page()` injetável (`resolve_fn`, `status_provider`, `fsm`); formato da página D2; `UNBOUND_PAGE` quando `bound_card=⊥` ou `q` ausente
- [x] 1.2 Adapter `.cursor/hooks/process-fsm-session-start.sh`: stdin JSON `sessionStart`, stdout `{additional_context}`; fallback unbound se Python falhar; nunca dump de overlay
- [x] 1.3 Registrar `sessionStart` em `.cursor/hooks.json` sem `failClosed`; preservar Guard e Impeccable

## 2. Always-on enxuto

- [x] 2.1 Reescrever `.cursor/rules/harness.mdc` com 8–15 linhas de corpo (D5 **e** spec MODIFIED): `Em Refinamento` é a entrada; não pular Design / Aprovação de Design; Todo ≠ código; sem `diff-reviewer` / `release-guard`; `alwaysApply: true`
- [x] 2.2 Mover o corpo atual de `AGENTS.md` para `docs/crypto-overlay.md`; stub `AGENTS.md` ≤40 linhas apontando o overlay (D6) **e** contendo `github.com/users/oalansilva/projects/1`
- [x] 2.3 Inverter prioridade no topo de `.cursor/skills/alan-workflow/SKILL.md`: δ e Guard > overlay > skill > wording (D7)

## 3. Testes

- [x] 3.1 `test_paging.py`: `status_provider`→Todo omite playbook de release; Homologado sem `release-guard pre`/`post`; unbound ≠ Homologado; provider injetado (não kwarg `q=`); página ≤20 linhas; sem GitHub
- [x] 3.2 Asserts de arquivo: `harness.mdc` 8–15 linhas de corpo com `Em Refinamento` e sem `diff-reviewer`/`release-guard`; stub `AGENTS.md` ≤40 com URL Project 1; âncora de prioridade na skill
- [x] 3.3 `pytest scripts/process-fsm -q` verde (job CI existente)

## 4. Verificação e fora de escopo

- [x] 4.1 Diff NÃO altera `backend/` nem `frontend/src/` de produto. Exceção: `backend/tests/integration/test_release_guard.py` aponta o contrato spawn-vazio para `docs/crypto-overlay.md` (o stub `AGENTS.md` não carrega o playbook).
- [x] 4.2 Diff NÃO altera Guard Write / `process_event` salvo reuso de `resolve` e `github_status_provider`
- [x] 4.3 Diff NÃO substitui `.cursor/hooks/impeccable.sh` nem adiciona `failClosed` em `sessionStart`
- [x] 4.4 Sem autômato de release, sem gate de `git commit`/`./restart`, sem expandir allowlist do `release-guard`
