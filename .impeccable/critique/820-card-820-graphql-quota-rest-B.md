# Snapshot — card #820 `card-820-graphql-quota-rest` (Assessment B)

- Card: #820 — https://github.com/oalansilva/crypto/issues/820 (OPEN)
- Change: `openspec/changes/card-820-graphql-quota-rest/`
- Critic: isolated Design Critic B (detector; inherit de modelo; **sem** transcript do pai; **sem** resultados de Assessment A)
- UTC: 2026-09-04T20:34:58Z
- Tuple (sessão do crítico): hooks `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`.
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-820-graphql-quota-rest` (`q_git=card-820-graphql-quota-rest`, HEAD `0ebf55ea`)
- Board: issue #820 OPEN; `design.md` declara Status observado **Design**. `UI impact: none` não saltou coluna.
- UI impact: **none** (harness/CLI/skills de processo: cota GraphQL vs REST, paging, evidência, fecho de lote). Nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol.
- Prototype: **N/A** confirmed (sem HTML desta change; `frontend/public/prototypes/` sem `card-820-*` / `graphql-quota`; Playwright visual **não** correu)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Detector desta onda = issue vs OpenSpec vs código vivo vs goldens G1–G18 (ainda não materializados; pré-Apply). Impeccable visual / `DESIGN.md` / Playwright = N/A.
- `design.md` sha256: `a338dd2c57d51b83e184cdc6e8d9c0c8a614459401c947513a885547667db58d` (17459 bytes, 2425 palavras) — **bate o esperado**
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + 7 spec deltas: `process-fsm-guard`, `process-fsm-paging`, `process-fsm-event`, `grill-card`, `release-worktree-hygiene`, `kaizen-continuous-improvement`, `documental-board-evidence-validation`)
- `openspec validate card-820-graphql-quota-rest --type change --strict`: **valid**
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto; este crítico MUST NOT editar `design.md`)
- Q1=A, Q2=A congeladas no issue (não reabrir). Fronteira vazia. #509 / #516 / #790 relacionadas e **não** reabertas no contrato.
- Goldens G1–G18: **especificados** em `design.md` + tasks; **ausentes** no pytest live (pré-Apply esperado).

---

## Brief

Operador do board (Alan + pai Cursor/Grok + root dsh + loop `aceitar_sha` 300s): com cota GraphQL a 0 o harness trata o card como fora do Project, enquanto REST `GET /rate_limit` mente `resources.graphql.remaining=5000`. Card #820: superfície issue em REST; cota que manda = cabeçalhos GraphQL; Status pontual; falha na hora com reset (Q1=A); diagnóstico de lote pelos cabeçalhos da fotografia que falhou (Q2=A); cache de reset sem sleep/retry/auto-dsh. `UI impact: none`.

Audience: operador do board e o harness (`guard` / `paging` / `process_event` / evidência / `release-guard` / skills). Outcome: grelha REST vive com GraphQL a 0; coluna/mover falham na hora com reset; paging bound+unread ≠ unbound. Direction: helper de parse+cache; `GraphQLQuotaError` no lugar de `None`; skills REST+pontual. Scope: `scripts/process-fsm/*`, `post-card-evidence-comment.sh`, `release-guard` diagnóstico, três skills canónicas; zero produto UI; sem pin novo; sem REST de coluna.

---

## Gates estáticos

| Gate | Resultado |
| --- | --- |
| `design.md` sha256 | `a338dd2c57d51b83e184cdc6e8d9c0c8a614459401c947513a885547667db58d` MATCH |
| HTML proto desta change | **ausente** (`frontend/public/prototypes/` sem slug 820) |
| `## Design Critique` em `design.md` | **ausente** |
| `openspec validate … --strict` | **valid** (exit 0) |
| `UI impact` | **none** — harness/CLI/skills; classificação **correcta** (não misclassified) |
| Browser / Playwright produto | **N/A (no UI)** |

---

## Issue vs OpenSpec (síntese)

Issue #820 (Q1=A, Q2=A, Entra/Não entra, vocabulário, critérios 1–6) está sintetizado: `proposal.md` What Changes = Entra; Non-Goals = Não entra; D1–D8 decidem os residuais (parser, paging bound+unread, cache do loop, REST das skills, sem bypass de coluna, cabeçalhos no lote). Tasks 1.1–6.6 mapeiam D1–D8 ↔ G1–G18. Specs ADDED/MODIFIED cobrem as 7 capabilities da proposal. Sem reentrevista. Sem HTML. Sem rewrite `DESIGN.md`.

---

## Probes (live, este worktree, pré-Apply)

Estado pré-Apply **esperado**: os furos do incidente ainda existem no produto; o contrato é que os feche.

### GET /rate_limit (REST remaining como cota GraphQL)

- `scripts/release-guard` `snapshot_fail_diagnose` linhas 88–96: `gh api rate_limit --jq '.resources.graphql | … remaining … reset'`. Uma vez por run (`RATE_LIMIT_DIAGNOSED`).
- `backend/tests/integration/test_release_guard.py` `test_rate_limit_diagnostic_absent_on_success_and_once_on_failure`: sucesso `CALL api rate_limit == 0`; falha **`== 1`** (D5 do #509 ainda vigente).
- Nenhum helper `graphql_quota.py`. Nenhuma env `PROCESS_FSM_GRAPHQL_QUOTA_CACHE`.

### `github_status_provider` → `None` (HTTP 200 + RATE_LIMIT)

`scripts/process-fsm/guard.py` `github_status_provider` (L411–470):

- Query pontual issue→`projectItems`→Status (**não** `item-list`) — já pontual.
- `gh api graphql` **sem** `--include` / `-i` (cabeçalhos descartados).
- `returncode != 0` **ou** stdout vazio → `return None` (L451–452) **sem** ler `errors[].type`.
- JSON parse + nodes vazios → `return None` (L470). HTTP 200 + `errors[0].type=RATE_LIMIT` cai aqui se o `gh` sair 0; se o `gh` sair 1 por `errors[]`, cai no ramo returncode.
- Sem `GraphQLQuotaError`. Sem cache.

### Paging: Status unread → stub unbound

`scripts/process-fsm/paging.py` L57–61: `if _unbound(bound) or q is None or q not in context_files` → `stub = UNBOUND_PAGE` (`bound_card=⊥. Write produto deny…`), `events=(unbound)`. Header pode manter `bound_card=N` (`bound_display`), mas o stub **contém** `bound_card=⊥`.

`test_paging.py` `test_missing_status_is_unbound_stub`: bound=N + provider `None` **afirma** `UNBOUND_PAGE in ctx`. Spec main vigente ainda diz `bound_card=⊥` **or** `q` missing → unbound; o delta MODIFIED desta change inverte G6/G8.

### `_item_id_for_issue` / mover

`process_event.py` L120–159: `gh api graphql` sem `--include`. `returncode != 0` → `RuntimeError(stderr)`. Nodes vazios → `RuntimeError(f"issue {n} not on Project {board}")`. `GhBoardMover.set_status` chama isto antes de `item-edit`. `_safe_move` captura como `reason=move_failed`. Sem reject `graphql_quota`.

`process_event` L294–295: se `q is None`, chama `github_status_provider` (não o `status_provider` injectável). Bound N + provider `None` **não** rejeita `unbound` (só se `_unbound(bound)`). O unbound-as-missing é o paging + a mensagem not-on-Project no mover.

### `gh issue view`

| Sítio | Live |
| --- | --- |
| `.cursor/skills/**` | **zero** `gh issue view` |
| `.grok/skills/**`, `.agents/skills/**` | **zero** |
| `scripts/post-card-evidence-comment.sh` L129–136 | **`gh issue view "$card" --json comments`**; fail-closed |
| `grill-card/SKILL.md` | escrita `gh issue edit` (REST); leitura do body = «buscar com tools» (não proíbe view) |
| Guard fixture `test_process_event.py` | payload `gh issue view 612` = allow de CLI (não é o furo) |

### `item-list` para operar um card

- `github_status_provider`: **não** lista o board (já pontual).
- `.cursor/skills/github-project-board/SKILL.md` Quick start: `gh project item-list` para listar **e** filtrar título (achar um card).
- `references/project-board-commands.md`: snippet «Mapear Item ID / titulo» = `item-list \| jq`; falha comum «IDs vêm no JSON de `item-list`».
- `.cursor/skills/kaizen/SKILL.md` fonte 1: `gh project view` / `item-list` (sem ramo `/kaizen card N` pontual).
- `scripts/release-guard` `ensure_board_snapshot` L117: **uma** `gh project item-list 1 --owner oalansilva --limit 500` (fotografia #509). Sem `--include`.

### Sleep / retry GraphQL

- `github_status_provider` / `_item_id_for_issue` / `snapshot_fail_diagnose`: **uma** chamada; **sem** `time.sleep`; **sem** loop de retry.
- `t14.py` tem `sleep=time.sleep` (outro recorte; G17 não o nomeia).
- Loop citado no PO: invocações periódicas `aceitar_sha` (fora do processo); cada wake hoje volta a GraphQL (sem cache).

### REST de coluna / #509 / UI

- Nenhum REST de campo Status no live (só GraphQL `item-edit` + query pontual). Contrato **proíbe** inventar.
- Fotografia: uma `item-list` por run em `ensure_board_snapshot`; contrato MUST NOT reabrir.
- UI: zero diff exigido em `frontend/src/` / `backend/` produto. Teste `backend/tests/integration/test_release_guard.py` só diagnóstico (task 5.2 / 6.6).

---

## Hunt (furos pedidos) — contrato vs live

| Furo | Contrato (issue + OpenSpec + G#) | Live / artefacto | Disposition |
| --- | --- | --- | --- |
| still using GET `/rate_limit` | D7 / spec `release-worktree-hygiene` MUST NOT `GET /rate_limit`; G15 zero `CALL api rate_limit`; G4 REST 5000 não autoriza | `snapshot_fail_diagnose` **ainda** `gh api rate_limit`; golden #509 exige `== 1` na falha | **CLOSED** no contrato (pré-Apply live) |
| wait/sleep until reset | Q1=A; D2/D3; spec guard/event MUST NOT sleep; G17 grep `time.sleep`; task 2.3 | callers alvo **já** sem sleep; o furo vivo é fail-as-None, não hang | **CLOSED** |
| unbound when Status unread | D4; paging MODIFIED; G6/G8/G11; task 3.1–3.2 inverte `test_missing_status_is_unbound_stub` | paging UNBOUND_PAGE se `q is None`; fixture afirma unbound; mover «not on Project» | **CLOSED** no contrato |
| `gh issue view` remaining in skills | D5; G13 script; G14 skills MUST NOT view; grill-card spec REST GET/PATCH | skills **já** sem a string; script evidência **ainda** view; grill não pinou GET REST | **CLOSED** no contrato; G14 view-needle já verde nas skills (P3) |
| `item-list` to operate one card | D6; G14; kaizen spec `/kaizen card N` MUST NOT; guard spec pontual | provider já pontual; **skill board + references** ainda listam para achar ITEM_ID; kaizen só fotografia | **CLOSED** em D6/task 4.3; G14 needles **fracos** (P2) |
| inventing REST for Project column | Não entra; D6; task 6.6 MUST NOT | não existe REST de coluna; mover continua GraphQL | **CLOSED** (proibido) |
| reopening #509 photograph | Q2=A; D7; spec hygiene MUST NOT segunda fotografia; task 5.1 | uma `item-list` por run; D7 captura cabeçalhos **na mesma** chamada | **CLOSED** |
| retry GraphQL loop | Q1=A; G12 segunda `aceitar_sha` cache 0; G17 | sem retry interno; loop 300s sem cache (D3) | **CLOSED** |
| treating REST remaining as GraphQL quota | vocabulário; D1/D3; G4; G15 imprime 0+reset GraphQL | diagnose imprime REST `.resources.graphql` | **CLOSED** no contrato |
| UI misclassified | issue `UI impact: none`; design Prototype N/A; zero rota | sem proto 820; sem `frontend/src/` no Apply contract produto | **CLOSED** (none correcto) |

---

## Goldens G1–G18 vs live

| # | Pin no design | Live pytest | Nota detector |
| --- | --- | --- | --- |
| G1 | parser HTTP 200 + RATE_LIMIT + headers 0 / Reset ISO | ausente | injectável; ver P2 transporte `gh` |
| G2 | Reset epoch | ausente | |
| G3 | `data.rateLimit` só se query OK sem headers | ausente | |
| G4 | REST 5000 não escreve cache / não autoriza | ausente | fecha o incidente |
| G5 | provider + G1 → `GraphQLQuotaError` **não** `None` | provider devolve `None` | |
| G6 | `page()` bound=N + G1 → keep N, unread+reset, não `⊥` | `test_missing_status_is_unbound_stub` **inverte** | |
| G7 | bound=`⊥` → UNBOUND_PAGE | `test_unbound_*` intacto | |
| G8 | bound=N + provider `None` (timeout) → unread, não unbound | mesma fixture unbound | |
| G9 | cache 0 + `now < reset_at` → zero GraphQL | cache inexistente | |
| G10 | cache expirado → uma GraphQL | ausente | |
| G11 | `_item_id` / mover + G1 → reject+reset, não unbound/not-on-Project, mover não chamado | `not on Project` / `move_failed` | |
| G12 | `aceitar_sha` ×2 cache 0 → 2ª sem GraphQL | sem cache | |
| G13 | evidência REST comments; MUST NOT `gh issue view --json comments` | script **tem** view | |
| G14 | skills MUST NOT view; REST issue; Status pontual ≠ item-list dum card | view já ausente nas skills; item-list **presente** no board skill | |
| G15 | diagnose: GraphQL 0+reset; zero `CALL api rate_limit`; REST 5000 no fake | golden vigente exige `CALL == 1` | |
| G16 | caminho feliz sem diagnóstico | já `== 0` no sucesso | |
| G17 | sem `time.sleep` / retry nos três callers | já sem sleep nesses callers | grep não pina exit≠0 / `--include` |
| G18 | `pytest scripts/process-fsm -q` sem GitHub | já injecta provider nos unitários | regressão |

---

## Critique (contrato vs live)

Issue #820 sintetizado (Q1=A / Q2=A congeladas). Pacote OpenSpec 7 deltas + G1–G18 + Apply contract D1–D8. Prototype N/A justificado. Sem HTML. Sem `## Design Critique` pré-preenchido. sha256 do `design.md` confere. `openspec validate --strict` valid. T7 humana permanece.

O detector **não** trata os furos live como P0/P1 desta coluna: são o ponto de partida do Apply. Os hunt items estão **proibidos** no contrato. Residuais = ouro G5/G11/G14 podem passar com fixtures já parseadas / needles de `gh issue view` enquanto o transporte `gh` e o recipe `item-list`→ITEM_ID do skill board ficam iguais.

---

## Findings

### P0

(nenhum)

### P1

(nenhum)

### P2

- **Transporte `gh api graphql` vs G1/G5/G11 injectados.** Live: `github_status_provider` e `_item_id_for_issue` chamam `gh api graphql` **sem** `--include`; `returncode != 0` curto-circuita para `None` / `RuntimeError(stderr)` **antes** de `errors[].type` e dos cabeçalhos. `gh` costuma sair ≠0 quando o JSON traz `errors[]`, mesmo com HTTP 200. G1 descreve um objecto já com headers; G5/G11 podem injectar `GraphQLQuotaError` sem o stdout real. Q1=A precisa do reset dos cabeçalhos. Disposition: Apply MUST parse RATE_LIMIT no stdout **mesmo com exit ≠0**, MUST capturar headers (`gh api graphql --include` / `-i`, split header-block+JSON) nestes dois callers — não só no loader da fotografia (D7). MUST NOT deixar `returncode != 0 → None`.

- **G14 needles vs `item-list` para operar um card.** D6 / task 4.3 / spec kaizen proíbem listar o board para um card. G14 pina «MUST NOT `gh issue view`» (já verdadeiro nas skills) e «Status pontual **não** `item-list`». O Quick start e `references/project-board-commands.md` ainda ensinam `item-list \| jq` e «IDs vêm no JSON de `item-list`» como único caminho para ITEM_ID/`item-edit`. Needle de `gh issue view` **não** apanha isto. Disposition: G14 MUST falhar enquanto o recipe de um card N for `item-list`; MUST apontar a query pontual (id+Status, a mesma família de `_item_id_for_issue`); `item-list` fica só fotografia #509 e `/kaizen` completo.

- **Fotografia #509 e cabeçalhos.** `ensure_board_snapshot` é `gh project item-list` sem headers (Risks já nomeia). G15 com fake RATE_LIMIT+headers pode ficar teatro se o loader real não os capturar. Disposition: Apply MUST ligar captura na **mesma** chamada (D7) **ou** imprimir «cota GraphQL desconhecida» — **nunca** remaining=5000 do REST. MUST NOT segunda query GraphQL só para cota. MUST NOT segunda `item-list`.

### P3

- Skills canónicas **já** não contêm `gh issue view`; o Context do `design.md` («ainda mandam `gh issue view`») exagera o live. O restante é o script de evidência (G13) e a leitura do body no grill («buscar com tools») que task 4.2 MUST NOT deixar em view.
- `github-project-board` não é capability OpenSpec; não há spec delta — só task 4.3 + G14 + ficheiros no Apply contract. Aceitável se o Apply seguir as tasks.
- G17 como grep de `time.sleep` não apanha `for`/`while` de retry sem sleep; G12 cobre a segunda invocação `aceitar_sha`.
- `design.md` duplica o bloco `UI impact: none` / `live_route: N/A` (Context e secção UI). Cosmético.
- `process_event(..., status_provider=)` é ignorado: se `q is None` chama sempre `github_status_provider`. Tests injectam `status=`. Residual de teste, não do DoD.
- `release-guard` ainda tem `gh api graphql` de idade (orçamento #509). Fora; MUST NOT reabrir nesse recorte.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. **Browser gate: N/A (no UI).**
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM: sem task de estado/evento/`enabled_tools` novo. Sem pin `covenant-flow`. Sem dual-write T0–T17. Sem auto-dsh / troca de token.
- Product UI Cripto: zero `frontend/src/` / `backend/` produto / HTML no Apply. `backend/tests/integration/test_release_guard.py` só G15/G16.
- Q1=A / Q2=A: pinados em D2/D3/D7 e specs; não reabertos.
- #509 / #516 / #790: Non-Goals; fotografia uma por run; HTML/apply do #790 fora.
- P0/P1 desta onda: **nenhum**. Hunt list fechada no contrato; live pré-Apply ainda doente (esperado).

---

## Trace

1. Live: `GET /rate_limit` no diagnose; provider `None` em RATE_LIMIT; paging UNBOUND_PAGE se `q is None`; `_item_id` not-on-Project; evidência `gh issue view --json comments`; board skill `item-list` para ITEM_ID; sem cache; sem proto 820.
2. Issue #820 Q1=A / Q2=A + Entra mapeados em proposal/design/tasks/7 specs.
3. sha256 `design.md` MATCH; validate strict valid; sem Design Critique; sem HTML.
4. G1–G18 especificados, não materializados.
5. Hunt 10/10 CLOSED no contrato; 3× P2 de ouro/transporte/recipe skill; 0× P0/P1.
6. UI none correcto; browser N/A.

---

## Verdict

- P0: (nenhum)
- P1: (nenhum)
- P2: transporte `gh` (exit≠0 / `--include`) vs G5/G11 injectados; G14 needles vs recipe `item-list`→ITEM_ID; fotografia sem headers vs G15 fake
- P3: view já ausente nas skills; sem spec `github-project-board`; G17 grep estreito; UI block duplicado; `status_provider` ignorado
- Disposition: contrato fecha os hunt items; Apply MUST pinar transporte real e G14 contra `item-list` dum card; T7 Alan
- Design Agent verdict: **PASS**
- Snapshot: `.impeccable/critique/820-card-820-graphql-quota-rest-B.md`

Este crítico MUST NOT editar `design.md` / HTML / produto. O pai sintetiza `## Design Critique` após A/B.
