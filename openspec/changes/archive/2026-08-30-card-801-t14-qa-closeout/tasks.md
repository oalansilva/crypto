## 1. Classificador e T11 no_pr

- [x] 1.1 Em `t14.py`, adicionar `classify_qa_gate` com tokens `no_pr` | `qa-gate pending` | `qa-gate failed`; `measure_checks_green` passa a wrapper de `ok`
- [x] 1.2 Em `process_event aceitar_sha`, listar PR `q_git`→develop; vazio ⇒ `reason=no_pr`, mover vazio, Status Code Review; não criar PR; `reviewers_ok` continua pelo nome do evento
- [x] 1.3 Atualizar `test_aceitar_sha_moves_qa` para injetar PR presente; fixture #792 (push sem PR) MUST reject `no_pr`

## 2. T14 reasons visíveis

- [x] 2.1 `integrar_develop` live usa o classificador; se `evaluate()` recusar com `guard:checks_green`, substituir `reason` pelo token; CLI sem `--checks-green`
- [x] 2.2 Fixtures: sem PR ⇒ `no_pr`; qa-gate não completed ⇒ `qa-gate pending`; missing/skipped/cancelled/failure/API erro ⇒ `qa-gate failed`; verde + runner ok ⇒ Done
- [x] 2.3 `T14Error` dirty inclui path + porcelain; `process_event` devolve `reason=sync: dirty` + `message`; sem checkout/merge/reset/restart/move; fixture #798
- [x] 2.4 Outras falhas de runner (restart/comment/squash merge) ⇒ `reason=I8` com `message` não vazio; runner omitido continua `I8`

## 3. Guard canónico

- [x] 3.1 Em `guard.py` `decide()`, antes do early-return sem path, deny `git checkout -b card-*` / `git switch -c card-*` / `--track -b` quando cwd ou `git -C` é `environments.dev.source`; reason `canonical_card_branch`
- [x] 3.2 Fallback `.cursor/hooks/process-fsm-guard.sh` deny a mesma classe; allow checkout existente e `checkout -b` em worktree que não é o canónico
- [x] 3.3 pytest `test_guard.py` com overlay/cwd/command injetados; sem GitHub

## 4. Moore e skill

- [x] 4.1 Atualizar só `context_file[QA]` em `.cursor/process-fsm.yaml`: filho QA sem `process_event`; pai T14 no mesmo turno do verde; pending ⇒ espera e repete; `no_pr`/`sync: dirty` visíveis; paging ≤20 linhas
- [x] 4.2 Atualizar `.cursor/skills/covenant-flow/SKILL.md`: ramo Cursor (filho QA + pai T14) e ramo dsh (sem filho QA; PR antes de T11; wait qa-gate; T14); stubs thin; `AGENTS.md` sem crescimento
- [x] 4.3 Needle de paging/skill: stub QA e linhas client-labeled; `decide()` MUST NOT ganhar matcher de Task/QA spawn

## 5. Verificação

- [x] 5.1 `pytest scripts/process-fsm -q` cobre T11 `no_pr`, classificador T14, dirty visível, Guard canónico; sem rede GitHub
- [x] 5.2 `openspec validate --all` (ou validate desta change) verde
- [x] 5.3 Confirmar que yaml T11/T14/Σ/I8 texto, `backend/`, `frontend/src/` e `DESIGN.md` não foram editados
