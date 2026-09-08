Ponto de partida Apply (após Pronto para Dev no mesmo chat `#821`): `openspec/changes/card-821-dsh-unbound-t16-moore/design.md` Apply contract (D1–D7, G1–G8). Skills: `.cursor/skills/openspec-apply-change`, `covenant-flow`. Zero produto UI. Sem `process_event` neste ficheiro. Design **não** aplica.

## 1. Stub unbound (`UNBOUND_PAGE`)

- [x] 1.1 `scripts/process-fsm/paging.py`: substituir `UNBOUND_PAGE` pelo texto pinado em D2 (`Write produto deny`; `suba a release` / `fechar release` / `subir lote`; overlay + T16; MUST NOT `Não carregue playbook de release.`)
- [x] 1.2 **Não** editar `unread_page()`; o stub Status unread com `bound_card=N` mantém `Não carregue playbook de release.`
- [x] 1.3 **Não** listar `fechar_release` em `enabled_events` unbound; **não** editar `process-fsm.yaml` / `process_event.py` / `t16.py` / `fsm.py` / `guard.py` `decide()`

## 2. Fallback Cursor

- [x] 2.1 `.cursor/hooks/process-fsm-session-start.sh`: o fallback fail-open emite o **mesmo** texto que `UNBOUND_PAGE` (G5)
- [x] 2.2 Grok SessionStart / OpenCode transform / dsh `covenant-flow:moore` continuam a chamar `page()`; MUST NOT hardcode um segundo stub

## 3. Skill canónica (uma linha Release)

- [x] 3.1 `.cursor/skills/covenant-flow/SKILL.md` secção Release: `bound_card=⊥` / `enabled_events: (unbound)` são display, não deny de T16; pedido explícito unbound em `develop`/`release-*` carrega overlay + `covenant-flow-environments` e segue T16; Write de produto continua deny
- [x] 3.2 `AGENTS.md` **não** cresce. Stubs `.dsh/` `.grok/` `.opencode/` de `covenant-flow` intactos (≤8, MUST Read). Sem dual-write T0–T17

## 4. Goldens pytest `scripts/process-fsm`

- [x] 4.1 G1/G2: `page()` unbound `q_git=develop` — `UNBOUND_PAGE` no ctx; `Write produto deny`; sem Homologado stub; sem `release-guard`; sem `deploy PROD`; sem `Não carregue playbook de release.`; contém `suba a release` e `fechar release`; ≤20 linhas; `enabled_events: (unbound)`; dump ausente **e** excepção presente. Unbound MUST NOT usar `subir lote` como needle de dump
- [x] 4.2 G3: `unread_page` / bound N unread — ainda contém `Não carregue playbook de release.`; `UNBOUND_PAGE` ausente; header sem `bound_card=⊥`
- [x] 4.3 G4: Todo e Homologado — needles de dump (`release-guard`, `deploy PROD`) ausentes; Todo MAY continuar a proibir `subir lote` na página Todo; stubs yaml intactos
- [x] 4.4 G5: fallback `process-fsm-session-start.sh` sem Python — `UNBOUND_PAGE` no JSON; sem `docs/crypto-overlay.md`; sem `release-guard`; sem a ordem absoluta antiga
- [x] 4.5 G6: `test_fechar_release_unbound_develop_evaluates` verde **sem** diff em `process_event.py` / `t16.py`. G7: `AGENTS.md` ≤40; sem T0–T17. `pytest scripts/process-fsm -q` sem GitHub

## 5. Produto covenant-flow + pin Cripto

- [x] 5.1 Commit no repo `oalansilva/covenant-flow` (`paging.py` + fallback + linha Release + goldens) após rebase no tip. Tag = próximo patch livre após `v1.1.13` (`git ls-remote --tags`); não major; não mover `v1.1.13`; não vendorar DeepSeek. Irmãos que tocam o mesmo nucleus — MUST NOT reverter haystacks; se já landed, a tag pinada MUST conter os deltas
- [x] 5.2 `implantar --pin` da tag de 5.1 no Cripto; overlay `pin` = essa tag; `clients.dsh.auto: false` (G8). `install.sh --pin` continua a copiar `.dsh/`; `SCHEMA_MAJOR` 1; `CLIENT_KEYS` três
- [x] 5.3 Não ligar Auto dsh; não systemd 3080; não reabrir #613/#652/#812/#782/#784/#786/#817; não executar lote PROD; não editar `backend/` / `frontend/src/`

## 6. Verificação

- [x] 6.1 `openspec validate card-821-dsh-unbound-t16-moore --type change --strict` verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)
- [x] 6.2 Stubs `.dsh/skills/` ≤8; `.dsh/` sem T0–T17; `AGENTS.md` ≤40; sem Auto dsh; `unread_page()` intacto; Σ/`fechar_release`/`M_lote` intactos

## 7. Homologação humana (Design especifica; Apply/homologação executa; **não** opcional)

- [ ] 7.1 Dump autenticado da GUI dsh web `http://127.0.0.1:3080` de um turno `suba a release` **ou** `fechar release` unbound (`q=None`, `bound_card=⊥`, `q_git=develop`, cwd = `canonical_paths.dev`): ≥1 `tool/call` do playbook T16 (overlay / `covenant-flow-environments` / `release-guard` / board / `process_event fechar_release`); **não** deny textual por `bound_card=⊥`. Só `skill` + `read` do runbook **falha** (recidiva `session-35e78019`). Pytest G1–G8 **não** substituem este dump. Dump Cursor/Grok/OpenCode **não** é critério. Homologação ≠ `./restart`; 3080 ≠ systemd. MUST NOT tratar como residual opcional nem como Done só com golden. MUST NOT executar o lote PROD neste card.
