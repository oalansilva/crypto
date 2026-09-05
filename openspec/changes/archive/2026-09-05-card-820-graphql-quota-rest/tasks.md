Ponto de partida Apply (após Pronto para Dev no mesmo chat `#820`): `openspec/changes/card-820-graphql-quota-rest/design.md` Apply contract (D1–D8, G1–G18). Skills: `.cursor/skills/openspec-apply-change`, `covenant-flow`. Zero produto UI. Sem `process_event` neste ficheiro. Design **não** aplica.

## 1. Parser e cache da cota GraphQL

- [x] 1.1 Helper partilhado (`scripts/process-fsm/graphql_quota.py` ou equivalente): cabeçalhos `X-RateLimit-Remaining` / `Reset` / `Resource=graphql`; `errors[].type=RATE_LIMIT` mesmo HTTP 200; `data.rateLimit` só se a query passou e faltam cabeçalhos; Reset epoch ou ISO-Z (D1)
- [x] 1.2 Cache JSON injectável via `PROCESS_FSM_GRAPHQL_QUOTA_CACHE`; `source` MUST ser `graphql-headers`; REST `GET /rate_limit` remaining=5000 MUST NOT escrever o cache nem autorizar GraphQL (D3)
- [x] 1.3 Goldens G1–G4: RATE_LIMIT+headers 0; Reset epoch; `rateLimit` em sucesso; REST 5000 não autoriza. Pytest sem GitHub

## 2. Status pontual e fail-immediate

- [x] 2.1 `github_status_provider`: RATE_LIMIT / remaining=0 → `GraphQLQuotaError` (não `None`); consulta pontual issue→Status; MUST NOT `item-list`; skip de rede se cache remaining=0 e `now < reset_at`; actualizar cache após GraphQL (D2–D3, G5, G9–G10)
- [x] 2.2 `_item_id_for_issue` / mover: o mesmo erro; `process_event` `reject` com reset na `message`; MUST NOT `unbound` / not-on-Project; mover não chamado (G11)
- [x] 2.3 Loop `aceitar_sha`: segunda invocação com cache a 0 MUST NOT disparar GraphQL; MUST NOT `time.sleep` até reset; MUST NOT retry loop (G12, G17)

## 3. Paging bound + coluna desconhecida

- [x] 3.1 `paging.py`: `bound_card=⊥` → `UNBOUND_PAGE`; `bound_card=N` + cota 0 / unread → keep N, stub Status unread + reset quando houver; MUST NOT `bound_card=⊥` (D4)
- [x] 3.2 Actualizar `test_missing_status_is_unbound_stub` para G6/G8 (não unbound). G7 intacto. Página ≤20 linhas. Sem playbook de release

## 4. Superfície issue REST

- [x] 4.1 `scripts/post-card-evidence-comment.sh`: REST `GET /issues/N/comments`; MUST NOT `gh issue view --json comments`; fail-closed se REST falhar (G13)
- [x] 4.2 `.cursor/skills/grill-card/SKILL.md`: GET/PATCH REST ou `gh issue edit`; MUST NOT `gh issue view`; PATCH do body funciona com GraphQL a 0; peles thin ≤8 MUST Read (G14)
- [x] 4.3 `.cursor/skills/github-project-board/SKILL.md` + `references/project-board-commands.md`: Status de um card = pontual; MUST NOT `item-list` para operar um card; issue REST; GraphQL a 0 = falha na hora com reset; sem REST de coluna (G14)
- [x] 4.4 `.cursor/skills/kaizen/SKILL.md`: issue REST; `/kaizen card N` pontual; GraphQL a 0 = falha na hora; `/kaizen` completo MAY uma fotografia, sem retry (G14)

## 5. Fecho de lote — cabeçalhos GraphQL (Q2=A)

- [x] 5.1 `snapshot_fail_diagnose`: imprimir remaining/reset dos cabeçalhos da fotografia que falhou; capturar na mesma chamada; MUST NOT `gh api rate_limit`; MUST NOT segunda query GraphQL de cota; MUST NOT reabrir fotografia #509 (D7)
- [x] 5.2 Actualizar `backend/tests/integration/test_release_guard.py` `test_rate_limit_diagnostic_absent_on_success_and_once_on_failure`: G15 (REST remaining=5000 + headers GraphQL 0 → imprime 0+reset; zero `CALL api rate_limit`) e G16 (caminho feliz sem diagnóstico)

## 6. Goldens REST vs GraphQL e verificação

- [x] 6.1 Fixture no mesmo instante REST `resources.graphql.remaining=5000` + cabeçalhos GraphQL remaining=0 → fluxo recusa GraphQL e usa REST no que REST cobre (G4 + G13 + evidência/grelha)
- [x] 6.2 Fail-immediate com reset: G1, G5, G6, G11 — sem espera no mesmo comando
- [x] 6.3 Sem ciclo de retry GraphQL: G12, G17 (grep `time.sleep` / loop no provider, `_item_id_for_issue`, `snapshot_fail_diagnose`)
- [x] 6.4 Sem unbound-as-missing: G6, G8, G11 — bound N + Status unread **não** é `bound_card=⊥` / not-on-Project
- [x] 6.5 `pytest scripts/process-fsm -q` sem GitHub (G18). `openspec validate --change "card-820-graphql-quota-rest" --type change --strict` verde
- [x] 6.6 Zero diff `backend/` produto / `frontend/src/` / `DESIGN.md` / HTML. Sem dual-write T0–T17. Sem auto-dsh. Sem troca de token. Sem sleep até reset. Sem REST de coluna do Project
