## 1. Medir checks_green

- [x] 1.1 `measure_checks_green(bound_card, q_git)`: PR `q_git`→`develop`, check `qa-gate` success no head; pending/skip/cancel/fail/ausente/erro ⇒ False
- [x] 1.2 `process_event integrar_develop` live chama o measurer quando `checks_green` não foi injetado; CLI **sem** `--checks-green`
- [x] 1.3 Fixture: unset + measurer False/ausente ⇒ reject, mover vazio, runner não chamado (preserva o teste atual)

## 2. Runner T14 atômico (I8)

- [x] 2.1 Protocolo injetável: `squash` → `sync_dev_source` → `restart` → `comment_done`; mover Done só no fim
- [x] 2.2 Live squash: `gh pr merge --squash` se PR aberto; skip se já em `origin/develop`; sem PR e sem SHA ⇒ reject
- [x] 2.3 Live sync: `git status --porcelain` no source canônico **antes** de mutar; dirty (tracked ou untracked) ⇒ I8 sem checkout/merge/reset; clean ⇒ `fetch` + `ff-only`; non-FF ⇒ I8 sem `reset --hard`
- [x] 2.4 Live restart: exec `/srv/apps/dev/criptofarol/source/restart` (não worktree, não PROD, não `stop`/`start`); depois retry `https://dev.criptofarol.com.br/api/health`; falha ⇒ I8
- [x] 2.5 Live comment: `scripts/post-card-evidence-comment.sh --transition done` com SHA de develop; falha ⇒ I8
- [x] 2.6 `--dry-run` não chama runner nem mover; live `main()` injeta measurer+runner reais; runner/`measurer` None ⇒ reject, nunca `_safe_move`
- [x] 2.7 Fixtures: measurer True + runner ok ⇒ mover Done na ordem; `restart` falha ⇒ reject `I8`; runner omitido ⇒ mover vazio; porcelain não vazio ⇒ I8 sem mutar o source; `comment_done` falha ⇒ I8
- [x] 2.8 Testes **não** chamam GitHub, systemd nem o `restart` real

## 3. Invariantes e fora de escopo

- [x] 3.1 `homologar` / `fechar_release` continuam reject Agent; T10–T13 inalterados
- [x] 3.2 Diff NÃO altera `.cursor/process-fsm.yaml` T14, `backend/`, `frontend/src/`, nem o Guard de `./restart`
- [x] 3.3 `pytest scripts/process-fsm -q` verde
