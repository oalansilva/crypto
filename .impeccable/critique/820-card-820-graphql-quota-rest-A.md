# Snapshot — Assessment A · card #820 `card-820-graphql-quota-rest`

- Card: #820 — kaizen: quota GraphQL a 0 bloqueia board/grill; GET /rate_limit remaining=5000 é falso
- Change: `card-820-graphql-quota-rest`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem nested critic; MUST NOT partilhar com B)
- Modelo: inherit
- UTC: 2026-09-04T20:33:11Z
- Round: 1
- Tuple (este isolado): Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não commit. Não editar `design.md`.
- Digest `design.md` **medido**: sha256 `a338dd2c57d51b83e184cdc6e8d9c0c8a614459401c947513a885547667db58d` · **2425** palavras (`wc -w`) · 17459 bytes · 172 linhas — bate com o esperado
- UI impact: **none** (harness/CLI/skills de processo; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*820*`; aceite = REST na superfície issue, fail-immediate com reset, paging bound+unread, lote a imprimir cabeçalhos GraphQL. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Sem Playwright. Sem browser gate.
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correcto; pai cola depois de A/B)
- Method: issue #820 via REST `gh api repos/oalansilva/crypto/issues/820` (GraphQL não usado nesta crítica); comentário [5519742379](https://github.com/oalansilva/crypto/issues/820#issuecomment-5519742379); `proposal.md` / `design.md` D1–D8 + Apply contract / `tasks.md` 1–6; deltas `process-fsm-guard` `process-fsm-paging` `process-fsm-event` `grill-card` `release-worktree-hygiene` `kaizen-continuous-improvement` `documental-board-evidence-validation`; live `github_status_provider`, `paging.py`, `_item_id_for_issue`, `post-card-evidence-comment.sh`, `snapshot_fail_diagnose`; HEAD `0ebf55ea` worktree (untracked só a change).

---

## Brief (só neste snapshot)

Alan quer grelhar e ler a issue por REST com a cota GraphQL a 0, e quer que ler coluna / mover card falhe na hora com a hora de reset — sem esperar no mesmo comando, sem unbound, sem storm no loop 300s, sem tratar o contador REST remaining=5000 como autorização GraphQL. Grelha Q1=A / Q2=A congelada no body; fronteira vazia; Design não reentrevista. `UI impact: none`.

---

## Rubrica (UI none)

### 1. Escopo vs grill #820 (Q1=A, Q2=A no body)

Body live: Qs fechadas, fronteira vazia, comentário canónico T1. Design **não** as reabre — sintetiza. Letras D2/D3/D7 batem com o Entra pós-grelha.

| Q congelada | Onde no pacote |
| --- | --- |
| Q1=A fail-immediate com hora de reset; **não** wait no mesmo comando | D2, D3; Non-Goal Q1≠B; spec guard + event; G1, G5, G6, G9, G11, G12, G17; tasks 2.x / 6.2–6.3 |
| Q2=A remaining/reset do lote = cabeçalhos GraphQL da fotografia que falhou; **não** `GET /rate_limit` | D7; Non-Goal Q2≠B; spec `release-worktree-hygiene`; G15–G16; tasks 5.1–5.2 |

Entra do body mapeado: superfície issue REST; cota que manda = cabeçalhos GraphQL (depois `rateLimit`); REST 5000 não autoriza GraphQL; Status pontual nunca `item-list` para um card; RATE_LIMIT HTTP 200 no corpo = falha na hora; unbound proibido; fotografia #509 uma por run; prova REST=5000 ∧ GraphQL=0 no mesmo instante; PATCH body com GraphQL a 0.

**Não entra — não reaberto:** HTML/apply #790; recorte fotografia #509; Q1=B wait; Q2=B imprimir REST remaining; consertar bug upstream do contador REST; produto `backend/`/`frontend/src/`; auto-dsh / troca de token; REST inventado para coluna do Project; dual-write T0–T17; novo evento FSM; pin `covenant-flow`.

Proposal «New Capabilities: (nenhuma)» correcto.

### 2. Q1/Q2 vs design

Q1=A não é só «não sleep»: é falha observável com `reset_at`, sem retry loop, sem unbound. D2 troca `None` silencioso por `GraphQLQuotaError(remaining, reset_at)`. D3 cache skip até reset (loop 300s acorda; cada wake falha na hora). G17 proíbe `time.sleep` / retry no provider, `_item_id_for_issue`, `snapshot_fail_diagnose`. Alternativa B (wait) rejeitada em Non-Goals e em D2.

Q2=A substitui D5 do #509 (`gh api rate_limit` `.resources.graphql`) sem reabrir a fotografia. Live `snapshot_fail_diagnose` (L88–96 de `scripts/release-guard`) faz exactamente `gh api rate_limit`. G15: fake RATE_LIMIT Remaining=0 + REST remaining=5000 → stdout 0+reset GraphQL; **zero** `CALL api rate_limit`. G16: caminho feliz sem diagnóstico (já o teste actual, linhas 761–762). Cabeçalhos ausentes → «cota desconhecida», **nunca** REST 5000 (risco aceite).

### 3. Unbound bug vs bound+unread (D4)

Live `paging.py` L53–61: `q is None` (provider `None`) **não** põe `bound_card=⊥` no cabeçalho da tupla (`bound_display` fica N), mas **escreve `UNBOUND_PAGE`** cujo texto é `bound_card=⊥. Write produto deny…` e `enabled_events: (unbound)`. Fixture `test_missing_status_is_unbound_stub` afirma `UNBOUND_PAGE in ctx` com bound=613. O *como* do issue compacta isto a «escreve página unbound (`bound_card=⊥`) mesmo com a issue N» — operacionalmente verdadeiro no stub; o header da tupla já guarda N.

D4: `bound_card=⊥` (resolver sem issue) → `UNBOUND_PAGE` intacto (G7). `bound_card=N` + Status unread (cota / RATE_LIMIT / timeout / nodes vazios) → keep N, stub Status unread + reset quando houver; MUST NOT `UNBOUND_PAGE`; MUST NOT Homologado/release; ≤20 linhas; sessionStart continua fail-open. Spec paging cenários «Bound card with GraphQL quota 0 is not unbound» e «Bound card with unread Status is not unbound» + MUST NOT conter `bound_card=⊥`. Tasks 3.1–3.2 actualizam a fixture → G6/G8.

Guard live já nega produto com `q is None` (`fail_closed`, L675–676) e permite `design_globs` em `card-*` (`test_fail_closed_design_allowed_on_card_branch`). D8: `GraphQLQuotaError` = Status unreadable → mesmo assim; `decide()` sem matcher novo de spawn.

`_item_id_for_issue` live (HTTP 200 + RATE_LIMIT, returncode 0, nodes vazios) cai em `RuntimeError("issue N not on Project …")` — o «card fora do board». G11: `reject` com reset; MUST NOT `unbound` / not-on-Project; mover não chamado.

### 4. REST vs GraphQL split

| Superfície | Hoje (HEAD) | Design |
| --- | --- | --- |
| Body/labels | REST `GET /repos/…/issues/N` já funcionou no incidente; grill escreve com `gh issue edit` | D5: GET/PATCH REST canónico; MUST NOT `gh issue view` |
| Comentários evidência | `post-card-evidence-comment.sh` L129: `gh issue view --json comments` (GraphQL); fail-closed | D5/G13: REST `/issues/N/comments`; fail-closed se REST falhar |
| Status Project 1 | `github_status_provider`: `gh api graphql` pontual issue→`projectItems`→Status; falha → `return None` | D1–D2, D6: mesma query pontual; RATE_LIMIT → `GraphQLQuotaError`; nunca `item-list` para um card |
| Mover coluna | `_item_id_for_issue` GraphQL + `gh project item-edit` | D6: continua GraphQL; a 0 falha na hora; **sem bypass REST** (não existe) |
| Cota que manda | ninguém parseia `X-RateLimit-*`; lote lê REST `rate_limit` | D1: headers, depois `rateLimit` se a query passou; REST 5000 MUST NOT cache/autorizar (G4) |
| Fotografia lote | `gh project item-list` uma vez (#509) + diagnose REST | D7: mesma uma fotografia; diagnose = headers dessa chamada |

Parser: `X-RateLimit-Resource` MUST ser `graphql` quando presente; Reset epoch **ou** ISO-8601 `Z` (incidente foi ISO). `rateLimit` sozinho rejeitado (query RATE_LIMITED nem sempre o devolve). REST `GET /rate_limit` MUST NOT alimentar o cache.

### 5. Fail-immediate vs wait

Q1≠B pinado. D2 alternativa rejeitada: sleep até reset no mesmo comando. D3: cache skip; loop `aceitar_sha` a cada 300s **continua a acordar**; cada invocação falha na hora a partir do cache; sem `time.sleep` até reset; sem retry dentro do comando; sem parar o timer systemd/cron (fora). G9: cache 0 + `now < reset_at` → zero chamadas GraphQL. G10: `now >= reset_at` → uma chamada. G12: segunda `aceitar_sha` com cache a 0 não dispara GraphQL. G17: grep sleep/retry.

Live `github_status_provider` não dorme (timeout 2s, `return None`). O furo é `None` → paging unbound-stub + item-id «not on Project», não um wait. O design não inventa wait para «corrigir» o None.

### 6. Skills ainda a mandar `gh issue view` / `item-list`

Medido neste worktree:

| Skill / script | `gh issue view` | `item-list` |
| --- | --- | --- |
| `.cursor/skills/grill-card/SKILL.md` | **ausente**; write já é `gh issue edit` (REST). Leitura do body = «buscar com tools» (não pinada REST) | proíbe `item-edit` Status; não lista o board |
| `.cursor/skills/github-project-board/SKILL.md` + `references/project-board-commands.md` | **ausente** | **ensina** listar, filtrar, e «IDs vêm no JSON de `item-list`» — caminho default para operar um card |
| `.cursor/skills/kaizen/SKILL.md` | **ausente** no SKILL (histórico em `docs/kaizen-log.md`) | fonte 1 do board: `gh project view` / `item-list` |
| `scripts/post-card-evidence-comment.sh` | **`gh issue view --json comments`** | — |
| `covenant-flow` / `AGENTS.md` | sem a string | Preflight «Consultar Status (`github-project-board`)» |

O *como* do issue junta as três skills em «ainda mandam `gh issue view` / `item-list`». Live: `gh issue view` está no script de evidência e no hábito do agente (grill não pinou REST GET); `item-list` está no project-board e no kaizen. D5/D6 + G14 fecham os dois: MUST NOT `gh issue view` (com ou sem `--json`); issue GET/PATCH REST; Status pontual **não** `item-list` para um card; `/kaizen` completo MAY uma fotografia classe #509 sem retry. Peles `.grok`/`.dsh`/`.opencode` thin ≤8 MUST Read. Alternativa rejeitada: `gh issue view` «só quando GraphQL > 0».

### 7. Loop cache (300s, sem storm)

PO: `process_event.py --card 790 aceitar_sha` a cada 300s. Live `process_event` L294–295: se `q is None`, chama **sempre** `github_status_provider` (não o `status_provider` injectado) — um GraphQL por wake. D3: ficheiro JSON `PROCESS_FSM_GRAPHQL_QUOTA_CACHE` ou default `tmp/criptofarol-graphql-quota-<uid>.json`, `{remaining, reset_at, source:"graphql-headers"}`. Antes de qualquer `gh api graphql` / `gh project` neste harness: remaining=0 ∧ `now < reset_at` → MUST NOT rede. Depois da resposta: actualiza pelos cabeçalhos. Sem auto-dsh, sem troca de token, sem flock (risco aceite: um GraphQL extra na corrida ao expirar).

### 8. Mover card impossível a 0 — stated

Non-Goal + D6 + Risks primeiro bullet: coluna Project 1 não tem REST; com GraphQL a 0 **não se move card**; falha na hora com reset; card **continua no board**. Sem bypass neste card. G11. Spec grill cenário «Column move has no REST bypass». Aceite #2 do body.

### 9. Sem produto UI sem classificação

`UI impact: none` com justificativa não vazia (duplicada em Context e secção UI impact — ruído, não furo). Prototype / Prototype Validation / pipeline Impeccable desta coluna = N/A. Apply contract: zero `backend/` produto / `frontend/src/` / `DESIGN.md` / HTML. Task 6.6. Clone/browser gate isento (`live_route: N/A`). Nenhuma superfície visual nova/alterada sem classificação.

### 10. Goldens G1–G18 testáveis sem GitHub vivo

| # | Camada | Rede? |
| --- | --- | --- |
| G1–G4 | parser/cache, fixtures de headers/body | não |
| G5 | provider injecta G1 | não (`github_status_provider` já «Never used by pytest») |
| G6–G8 | `page()` + `status_provider` injectado | não (padrão actual `test_paging.py`) |
| G9–G10, G12 | cache path injectável; contagem de chamadas fake | não |
| G11 | `_item_id_for_issue` / mover injecta G1 | não |
| G13 | fonte do script (needle REST vs `gh issue view`) | não |
| G14 | needles nos SKILL.md | não |
| G15–G16 | `test_release_guard.py` + `_fake_gh` (já existe; actualiza o caso `rate_limit` / headers) | não (fake `gh` no PATH) |
| G17 | grep fonte | não |
| G18 | `pytest scripts/process-fsm -q` | contrato MUST NOT GitHub |

Incidente REST=5000 / GraphQL=0 reproduzido em fixture, não na API viva (Migration Plan).

### 11. *Como* live confirmado (não opção)

- `guard.py` `github_status_provider` L411–470: query GraphQL pontual; timeout/returncode/JSON/nodes vazios/HTTP 200+RATE_LIMIT → **`return None`**. Sem `--include`; headers `X-RateLimit-*` não entram no stdout. Sem `item-list`.
- `paging.py` L57–58: `q is None` → `UNBOUND_PAGE` (texto `bound_card=⊥`) mesmo com bound N no header.
- `process_event.py` `_item_id_for_issue` L120–159: GraphQL pontual; RATE_LIMIT HTTP 200 → nodes vazios → `not on Project`.
- `post-card-evidence-comment.sh` L129–136: `gh issue view --json comments`; fail-closed.
- `release-guard` `snapshot_fail_diagnose` L88–96: `gh api rate_limit` `.resources.graphql` (D5 #509). `ensure_board_snapshot` L117: `gh project item-list` uma vez — **não** reaberto pelo design.
- Skills: ver §6.
- Loop: L294 chama provider live se `q is None`. Trocar token / auto-dsh **não entra**.

### 12. Apply contract vs HEAD

Worktree `card-820-graphql-quota-rest` @ `0ebf55ea`, untracked só `openspec/changes/card-820-graphql-quota-rest/`. Design **não** aplica. Ficheiros previstos nomeados (helper `graphql_quota.py` ou equivalente, guard/paging/process_event + testes, evidence script, release-guard, `test_release_guard.py` só diagnóstico, três skills). Stubs peles só se o gerador exigir. Sem pin novo. Rollback nomeado.

---

## Superfície visual — classificação

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| Rotas Cripto / shell autenticado / componentes / copy | não tocadas |
| HTML protótipo | N/A (`UI impact: none`) |
| Página Moore sessionStart / deny Guard | aceite operacional de harness, não tela de produto |
| `DESIGN.md` / Playwright desta coluna | N/A |

---

## Achados

### P0

(nenhum)

### P1

(nenhum) — Q1=A e Q2=A reflectidas em D2/D3/D7 + specs + G1–G18; unbound vs bound+unread em D4/G6/G8; REST/GraphQL split em D1/D5/D6; fail-immediate vs wait pinado; mover a 0 impossível stated; #509 fotografia não reaberta; sem pin novo; sem produto UI por classificar.

### P2

- **Captura viva de cabeçalhos no provider / `_item_id_for_issue` não está golden.** D1 exige parse de `X-RateLimit-*`; D7 nomeia `--include` só para a fotografia. G1/G5 injectam headers/erro; o `subprocess.run(["gh","api","graphql",…])` live hoje **não** passa `--include`, logo stdout é só JSON. Apply que ligue o parser só às fixtures e esqueça `--include` (ou stderr no exit≠0) perde `reset_at` no caminho de produção enquanto G1/G5 passam. Disposition: **accepted** (D1+aceite #2/#5 obrigam o reset; G17 não testa `--include`; risco de Apply).
- **`decide()` / sessionStart e `GraphQLQuotaError` sem golden próprio.** D8 pede deny produto + allow `design_globs` em `card-*`. Wrapper Guard já fallback-deny produto / allow design se o Python não emitir JSON; sessionStart fallback é **UNBOUND_PAGE** (`bound_card=⊥`) se `page()` rebentar — exactamente o bug, à porta do hook. G6 cobre `page()`; não cobre o adapter shell. Disposition: **accepted** (contrato D4/D8 escrito; G6 falha se `page()` não apanhar o erro).
- **Default do cache é path relativo `tmp/criptofarol-graphql-quota-<uid>.json`.** Guard, paging e o timer 300s podem ter cwd diferentes → duas caches → o loop ainda skip se o timer for estável; o Guard de outra cwd pode dar um GraphQL extra. Sem flock (já residual). Disposition: **accepted** (env injectável; G9/G12 no path de teste; residual operacional).
- **`_fake_gh` de `test_release_guard.py` já trata `api graphql` (paginação) e `api rate_limit`.** G15 exige headers na fotografia e zero `rate_limit`. Trocar o loader para `gh api graphql --include` colide com o case graphql existente; manter `item-list` sem headers viola D7. Disposition: **accepted** (task 5.2 manda actualizar o teste; #509 uma listagem permanece).
- **`process_event` L294 chama `github_status_provider` live, ignora `status_provider` injectado.** G12 precisa desta linha a honrar cache/helper. Disposition: **accepted** (G12 vermelho se Apply não reroute).

### P3

- *Como* do issue atribui `gh issue view` às três skills; live a string está no script de evidência, não nos SKILL.md do grill/project-board/kaizen. G14 ainda é o pin certo (hábito do agente + grill sem REST GET). Disposition: **accepted**.
- Sem spec OpenSpec `github-project-board` (não é capability); cobertura = G14 needles + task 4.3. Disposition: **accepted**.
- `covenant-flow` Preflight continua «Consultar Status (`github-project-board`)» — após G14 o skill deixa de usar `item-list` para um card; o runbook não precisa de needle próprio. Disposition: **accepted**.
- Residual `gh issue edit` futuro a virar GraphQL — já no Risks; G14 falha visível. Disposition: **accepted**.
- `X-RateLimit-Resource` presente mas ≠ `graphql`: D1 MUST, sem cenário. Disposition: **accepted** (incidente Resource=graphql).
- `UI impact: none` / `live_route: N/A` repetidos no Context e na secção UI impact. Disposition: **accepted** (ruído).
- Dois processos sem flock; logs repetidos do loop até o reset; kaizen completo espera o reset no comando seguinte. Já em Risks. Disposition: **accepted**.
- Peles thin só se o gerador exigir. Disposition: **accepted**.

---

## Verdict

**PASS** — zero P0/P1 abertos. Prototype N/A justificado. Snapshot visual Impeccable N/A justificado (`UI impact: none`). Este ficheiro é o relatório da crítica de processo, não o browser gate.
