## Context

Card [#820](https://github.com/oalansilva/crypto/issues/820). Status observado: **Design**. Bound `q_git=card-820-graphql-quota-rest`. Relacionada e **não** reaberta: #509 / #516 (fotografia completa do board no fecho de lote) e #790 (HTML/apply). Q1=A e Q2=A congeladas no body; fronteira vazia; este Design **não** reentrevista.

Incidente 2026-09-03 (user `oalansilva` id `126212`): REST `GET /rate_limit` reportou `resources.graphql.remaining=5000` / `used=0` **ao mesmo tempo** que o POST GraphQL devolveu cabeçalhos `X-RateLimit-Remaining: 0`, `X-RateLimit-Reset: 2026-09-03T02:55:52Z`, HTTP 200 com `errors[0].type=RATE_LIMIT`. REST da issue (`GET /repos/oalansilva/crypto/issues/N`) leu body/labels. `gh project list` também RATE_LIMIT. `gh issue view` (mesmo sem `--json`) pode cair em GraphQL (Projects classic).

Factos live (código — *como*, não opção):

- `scripts/process-fsm/guard.py` `github_status_provider`: query GraphQL pontual issue→Status; em falha (timeout, returncode, JSON, nodes vazios, HTTP 200+RATE_LIMIT) **return None**.
- `scripts/process-fsm/paging.py`: `q is None` escreve página unbound (`bound_card=⊥`) mesmo com a issue N no prompt.
- `scripts/process-fsm/process_event.py` `_item_id_for_issue`: GraphQL; necessário para `item-edit`.
- `scripts/post-card-evidence-comment.sh`: `gh issue view --json comments` (GraphQL); fail-closed se falhar.
- `scripts/release-guard` `snapshot_fail_diagnose`: imprime `gh api rate_limit` `.resources.graphql` (D5 do #509).
- Skills `grill-card` / `github-project-board` / `kaizen` ainda mandam `gh issue view` / `gh project item-list`.
- Loop vivo citado no PO: `process_event.py --card 790 aceitar_sha` a cada 300s. Trocar token / auto-dsh **não entra**.

UI impact: none
live_route: N/A harness-only; no product route. Clone gate isento (sem HTML, sem catálogo). Sem superfície visual de produto.

## Goals / Non-Goals

**Goals:**

- Superfície issue (body, comentários, labels): REST read/write. Vista JSON da issue só se o REST não cobrir o campo. PATCH REST do body (grelha) funciona com cota GraphQL a 0.
- Cota GraphQL que manda = cabeçalhos da resposta GraphQL (ou campo `rateLimit` quando a query passa). Contador REST remaining=5000 **não** autoriza GraphQL.
- Status de um card N: consulta pontual. Nunca `item-list` do board para operar um card.
- GraphQL a 0 / RATE_LIMIT (HTTP 200 com RATE_LIMIT no corpo): falha na hora com a hora de reset (Q1=A); sem espera no mesmo comando; sem ciclo de retry; sem tratar Status desconhecido como card fora do board.
- Fecho de lote: remaining/reset impressos vêm dos cabeçalhos GraphQL da resposta que falhou (Q2=A). Fotografia completa = uma por execução (#509 intacto).
- Loop periódico deixa de bater GraphQL a 0: lê o reset em cache e falha na hora até essa hora; sem auto-dsh, sem troca de token.
- Prova observável: no mesmo instante REST remaining=5000 e cabeçalhos GraphQL 0 → recusa GraphQL e usa REST no que REST cobre.

**Non-Goals:**

- Reabrir o HTML/apply do #790.
- Reabrir o recorte do #509 (uma fotografia completa do board no fecho de lote).
- Esperar o reset GraphQL dentro do mesmo comando (Q1≠B).
- Deixar o fecho de lote a imprimir o remaining do contador REST (Q2≠B).
- Consertar o bug da API GitHub no contador REST.
- Código de produto (`backend/`, `frontend/src/`). UI / HTML / `DESIGN.md` / Playwright desta coluna.
- Ligar/desligar o dsh sozinho; trocar token ou conta sem pedido do Alan.
- Inventar REST para a coluna do Project (não existe; mover coluna continua GraphQL e **continua impossível** com GraphQL a 0 — este card não inventa bypass).
- Dual-write T0–T17. Novo evento FSM. Pin `covenant-flow`.

## Decisions

1. **Parser único da cota GraphQL = cabeçalhos da resposta GraphQL, depois `rateLimit`, nunca o contador REST.**  
   Apply introduz um helper partilhado em `scripts/process-fsm/` (nome Apply: `graphql_quota.py` ou funções no mesmo módulo que `github_status_provider`) que, dada uma resposta GraphQL, extrai:
   - `X-RateLimit-Remaining` / `X-RateLimit-Reset` / `X-RateLimit-Resource` (Resource MUST ser `graphql` quando presente);
   - `errors[].type == RATE_LIMIT` no JSON mesmo com HTTP 200 (incidente);
   - `data.rateLimit.remaining` / `data.rateLimit.resetAt` **somente** quando a query passou e os cabeçalhos faltam.  
   `X-RateLimit-Reset` MUST aceitar epoch Unix e ISO-8601 `Z`.  
   `GET /rate_limit` `.resources.graphql` MUST NOT autorizar GraphQL e MUST NOT alimentar o cache (D3). Alternativa rejeitada: confiar no contador REST (mentiu remaining=5000). Alternativa rejeitada: campo `rateLimit` sozinho (a query RATE_LIMITED nem sempre o devolve).

2. **`GraphQLQuotaError` (remaining + reset_at) no lugar de `None` silencioso.**  
   `github_status_provider` e `_item_id_for_issue` MUST **não** devolver `None` / “not on Project” quando a causa é cota a 0 ou RATE_LIMIT. MUST levantar (ou devolver tagged) `GraphQLQuotaError` com `remaining=0` e `reset_at` dos cabeçalhos. Pytest injeta o erro; MUST NOT chamar GitHub. Timeout / JSON inválido / nodes vazios **sem** RATE_LIMIT continuam falha de leitura, **não** unbound (D4). Alternativa rejeitada: `return None` (hoje vira `bound_card=⊥`). Alternativa rejeitada: sleep até o reset no mesmo comando (Q1≠B).

3. **Cache de reset para o loop periódico — sem auto-dsh, sem troca de token, sem storm.**  
   Ficheiro JSON (env `PROCESS_FSM_GRAPHQL_QUOTA_CACHE` ou default `tmp/criptofarol-graphql-quota-<uid>.json`) com `{remaining, reset_at, source:"graphql-headers"}`. **Antes** de qualquer `gh api graphql` / `gh project` neste harness: se `remaining==0` e `now < reset_at`, MUST NOT ir à rede; falha na hora com o reset em cache. **Depois** de uma resposta GraphQL: actualiza o cache a partir dos cabeçalhos. O loop `process_event.py --card N aceitar_sha` a cada 300s continua a acordar; cada invocação falha na hora a partir do cache até o reset. Sem retry dentro do mesmo comando. Sem `time.sleep` até o reset. REST da issue continua. Alternativa rejeitada: parar o timer systemd/cron (fora; o timer não é deste card). Alternativa rejeitada: auto-dsh / swap de token.

4. **Paging: bound + coluna desconhecida ≠ unbound.**  
   `page()`: `bound_card=⊥` (resolver sem issue N) → `UNBOUND_PAGE` como hoje. `bound_card=N` e Status não lido (cota / RATE_LIMIT / timeout / nodes vazios) → MUST keep `bound_card=N`, `q=None`, stub curto de **Status unread** + reset quando houver; MUST NOT `UNBOUND_PAGE`; MUST NOT Homologado/release. Página continua ≤20 linhas; `sessionStart` continua fail-open (emite a página, não aborta o hook). Fixture live `test_missing_status_is_unbound_stub` MUST passar a afirmar o stub de unread, não `bound_card=⊥`. Alternativa rejeitada: unbound “para o Guard negar Write” (o Guard já nega produto com Status unreadable — D6).

5. **Skills e evidência: REST na superfície issue; `gh issue view` sai.**  
   Canónico:
   - GET body/labels: `gh api repos/<owner>/<repo>/issues/<n>`
   - PATCH body: `gh api -X PATCH repos/<owner>/<repo>/issues/<n>` **ou** `gh issue edit` (REST). MUST NOT `gh issue view` (GraphQL, inclusive sem `--json`).
   - Comentários: `gh api repos/<owner>/<repo>/issues/<n>/comments` (paginate). MUST NOT `gh issue view --json comments`.
   - Labels: campo `.labels` do GET REST.  
   `post-card-evidence-comment.sh` troca o GET JSON por REST e permanece fail-closed se o REST falhar. `grill-card`: `gh issue edit` / PATCH permanece; leitura do body passa a REST. Peles `.grok` / `.dsh` / `.opencode` continuam thin MUST Read (≤8 linhas). Alternativa rejeitada: `gh issue view` “só quando GraphQL > 0” (o incidente mostrou o comando a cair em GraphQL mesmo para body).

6. **Project 1 coluna: pontual GraphQL; `item-list` não é fallback; sem bypass REST.**  
   Status de um card N = a query pontual já usada por `github_status_provider` (issue→`projectItems`→campo Status do Project 1). Skills `github-project-board` / `kaizen card N` / Guard MUST NOT `gh project item-list` para operar um card. `item-list` permanece **somente** a fotografia única do fecho de lote (#509) e o `/kaizen` completo quando a tarefa é o board inteiro — uma listagem, sem retry. Com GraphQL a 0: falha na hora com reset; **não** há REST para coluna; mover (`item-edit` / `_item_id_for_issue`) falha na hora com o mesmo reset; o card **continua no board**. Alternativa rejeitada: listar o board para achar o item (storm + #509). Alternativa rejeitada: inventar REST de coluna.

7. **Fecho de lote (Q2=A): diagnosticar pelos cabeçalhos da fotografia que falhou, não `GET /rate_limit`.**  
   `snapshot_fail_diagnose` MUST imprimir `remaining`/`reset` parseados da resposta GraphQL da fotografia (#509, uma por run) — loader MUST capturar cabeçalhos (`gh api graphql --include` na mesma chamada, ou equivalente). MUST NOT `gh api rate_limit`. MUST NOT uma segunda query GraphQL só para ler cota. Se os cabeçalhos não vierem: dizer que a cota GraphQL é desconhecida **sem** imprimir remaining=5000 do REST. Golden #509 `test_rate_limit_diagnostic_absent_on_success_and_once_on_failure` MUST deixar de exigir `CALL api rate_limit == 1`; passa a exigir o número dos cabeçalhos GraphQL (0 + reset) quando o fake devolve RATE_LIMIT. Fotografia `item-list` **não** se reabre. Alternativa rejeitada: Q2=B (imprimir REST remaining).

8. **Guard fail-closed de produto intacto; OpenSpec em Design na branch do card continua allow.**  
   `GraphQLQuotaError` = Status unreadable → deny `product_globs`; `design_globs` em `card-<id>-*` continuam allow. `decide()` não ganha matcher novo de spawn. Sem dual-write T0–T17.

### Golden cases (pytest `scripts/process-fsm` + `backend/tests/integration/test_release_guard.py`; sem GitHub de rede)

| # | Caso | Esperado |
| --- | --- | --- |
| G1 | Parser: HTTP 200 + `errors[0].type=RATE_LIMIT` + cabeçalhos Remaining=0 / Reset ISO | `GraphQLQuotaError(remaining=0, reset_at=…)` |
| G2 | Parser: cabeçalhos Remaining=0, Reset epoch | mesmo erro; ISO derivada |
| G3 | Parser: query OK + `data.rateLimit.remaining=12` sem cabeçalhos | remaining=12 (não erro) |
| G4 | REST `resources.graphql.remaining=5000` **não** escreve cache e **não** autoriza GraphQL | cache intacto / skip REST |
| G5 | `github_status_provider` com G1 | levanta `GraphQLQuotaError`; **não** `None` |
| G6 | `page()` bound=N + G1 | `bound_card=N`, stub Status unread + reset; **não** `UNBOUND_PAGE`; **não** `bound_card=⊥`; ≤20 linhas |
| G7 | `page()` bound=`⊥` | `UNBOUND_PAGE` inalterado |
| G8 | `page()` bound=N + provider `None` (timeout sem RATE_LIMIT) | `bound_card=N`, Status unread; **não** unbound |
| G9 | Cache remaining=0, `now < reset_at` | zero chamadas GraphQL; falha na hora com reset |
| G10 | Cache remaining=0, `now >= reset_at` | uma chamada GraphQL permitida |
| G11 | `_item_id_for_issue` / mover com G1 | `reject` com reset; **não** `unbound`; **não** “not on Project”; mover não chamado |
| G12 | `aceitar_sha` duas vezes com cache a 0 | segunda invocação **não** dispara GraphQL (G9) |
| G13 | Evidência: fonte **sem** `gh issue view --json comments`; tem REST `/issues/N/comments` | fail-closed se REST falhar |
| G14 | Skills canónicas `grill-card` / `github-project-board` / `kaizen`: MUST NOT `gh issue view`; issue GET/PATCH REST; Status pontual **não** `item-list` para um card | needles |
| G15 | `snapshot_fail_diagnose`: fake fotografia RATE_LIMIT Remaining=0 + REST remaining=5000 | stdout remaining=0 e reset GraphQL; **zero** `CALL api rate_limit` |
| G16 | `snapshot_fail_diagnose` no caminho feliz | zero diagnóstico de cota (como #509) |
| G17 | Sem sleep/retry: fonte `github_status_provider` / `_item_id_for_issue` / `snapshot_fail_diagnose` **sem** `time.sleep` / loop de retry GraphQL | grep |
| G18 | pytest `scripts/process-fsm -q` sem rede GitHub | verde |

## Apply contract

Apply só após `Status=Pronto para Dev` no **mesmo** chat `#820`, filho Apply (pai `iniciar_apply` antes do spawn). Zero produto UI. Design **não** aplica. Skills Cursor: `openspec-apply-change`, `covenant-flow`.

1. Helper de parse + cache (D1–D3). Goldens G1–G4, G9–G10, G17. Env `PROCESS_FSM_GRAPHQL_QUOTA_CACHE` injectável.
2. `github_status_provider` e `_item_id_for_issue` usam o helper; RATE_LIMIT → `GraphQLQuotaError` (D2). G5, G11, G12.
3. `paging.py`: D4. Actualizar `test_missing_status_is_unbound_stub` → G6/G8. G7 intacto. Página ≤20.
4. `process_event` reject `graphql_quota` (ou equivalente pinado) com `reset_at` na `message`; MUST NOT unbound. Loop: cache D3.
5. `post-card-evidence-comment.sh` REST comments (D5). G13.
6. Skills: `grill-card`, `github-project-board` (SKILL + `references/project-board-commands.md`), `kaizen` — REST issue + Status pontual (D5–D6). Peles thin MUST Read, body ≤8. G14.
7. `snapshot_fail_diagnose` cabeçalhos GraphQL (D7). Actualizar `test_rate_limit_diagnostic_absent_on_success_and_once_on_failure`. G15–G16. **Não** reabrir fotografia #509.
8. Specs deltas desta change. `openspec validate --strict`. MUST NOT `backend/` `frontend/src/` `DESIGN.md`. MUST NOT sleep até reset. MUST NOT REST de coluna.

**Ficheiros previstos (Apply):**

- `scripts/process-fsm/guard.py`
- `scripts/process-fsm/paging.py`
- `scripts/process-fsm/process_event.py`
- `scripts/process-fsm/graphql_quota.py` (ou equivalente no pacote)
- `scripts/process-fsm/test_guard.py`
- `scripts/process-fsm/test_paging.py`
- `scripts/process-fsm/test_process_event.py`
- `scripts/process-fsm/test_graphql_quota.py` (se módulo novo)
- `scripts/post-card-evidence-comment.sh`
- `scripts/release-guard`
- `backend/tests/integration/test_release_guard.py` (só o diagnóstico de cota; zero produto)
- `.cursor/skills/grill-card/SKILL.md`
- `.cursor/skills/github-project-board/SKILL.md`
- `.cursor/skills/github-project-board/references/project-board-commands.md`
- `.cursor/skills/kaizen/SKILL.md`

Stubs `.grok` / `.dsh` / `.opencode` só se o gerador o exigir; corpo thin.

## Risks / Trade-offs

- [Coluna do Project 1 não tem REST] → aceite explícito: com GraphQL a 0, **não se move card**. Falha na hora com reset. Sem bypass neste card.
- [Cache de reset stale se o relógio local atrasar] → `reset_at` em UTC; depois do reset a próxima chamada GraphQL é única (G10). Residual: relógio muito errado adianta/atrasa o skip — visível, não storm.
- [Dois processos (Cursor + dsh + loop 300s) sem flock] → o cache é skip, não lock. Residual aceite: um GraphQL extra na corrida ao expirar o reset; Q1=A proíbe loop **dentro** do comando, não um concorrente.
- [`gh project item-list` não expõe cabeçalhos] → D7: a fotografia passa a capturá-los na mesma chamada (`--include` / graphql equivalente). Residual: se o loader não os tiver, mensagem “cota desconhecida” — **nunca** REST 5000.
- [`gh issue edit` vs `gh api PATCH`] → ambos REST; skill pinada a não usar `gh issue view`. Residual: `gh` futuro muda `issue edit` para GraphQL — golden G14 falha visível.
- [Kaizen `/kaizen` completo ainda fotografa o board] → uma listagem, classe #509, não operar um card. Com cota 0 falha na hora. Residual aceite: auditoria completa espera o reset (comando seguinte, não sleep).
- [Paging stub novo vs teto 20 linhas] → texto curto pinado no Apply. Residual: cliente ignora a página e trata `q=None` como unbound — Guard ainda nega produto.
- [Loop 300s continua a acordar] → cada wake é fail-immediate em cache. Residual: logs repetidos até o reset — melhor que storm GraphQL. Parar o timer **não entra**.

## Migration Plan

Aditivo sobre HEAD desta branch. Ordem = Apply contract. Rollback = reverter helper + paging unbound-on-None + `snapshot_fail_diagnose` REST + `gh issue view --json comments`. Sem migration de banco. Sem rebuild frontend. Sem pin novo. Homologação = G1–G18 verdes; incidente REST=5000 / GraphQL=0 reproduzido em fixture, não na API viva.

## Open Questions

Nenhuma bloqueante. Q1=A e Q2=A congeladas. Residuais decididos em D1–D8 (parser, paging bound+unread, cache do loop, REST das skills, sem bypass de coluna, cabeçalhos no lote).

## UI impact

**none** — harness/CLI/skills de processo (cota GraphQL vs REST, paging, evidência, fecho de lote). Nenhuma rota, shell, componente ou copy de produto. Nenhuma superfície visual nova ou alterada.

UI impact: none
live_route: N/A harness-only; no product route. Clone gate isento (sem HTML, sem catálogo). Sem superfície visual de produto.

## Prototype

N/A — `UI impact: none`. Não há tela CriptoFarol a prototipar; o aceite é REST na superfície issue, falha na hora com reset quando a cota GraphQL está a 0, paging bound+unread (não unbound), e o número impresso no fecho de lote a vir dos cabeçalhos GraphQL. Sem HTML. Sem `frontend/public/prototypes/`. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A (não há UI de produto a exercitar). Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O filho autor não spawna Assessment A/B. T7 e Aprovação de Design humanas permanecem.

## Design Critique

- P0: nenhum
- P1: nenhum
- P2 (aceites): transporte `gh api graphql` (exit ≠0, sem `--include`) — Apply MUST parse RATE_LIMIT no stdout e capturar cabeçalhos nos callers de Status/item-id, não só na fotografia; G14 MUST falhar enquanto operar um card N for `item-list`; fotografia sem cabeçalhos → captura na mesma chamada ou «cota desconhecida», nunca REST 5000; cache default `tmp/…` (cwd Guard ≠ loop); `_fake_gh` vs G15; `process_event` L294 ignora `status_provider` injectado (G12 reroute)
- P3 (aceites): `gh issue view` já ausente nas skills vs G14 view-needle; sem spec delta `github-project-board`; G17 grep de `time.sleep` estreito; bloco UI duplicado; `gh issue edit` futuro GraphQL; Resource ≠ graphql
- Prototype: N/A — `UI impact: none` (harness REST/GraphQL; sem HTML)
- Snapshot: `.impeccable/critique/820-card-820-graphql-quota-rest-A.md` e `.impeccable/critique/820-card-820-graphql-quota-rest-B.md`
- Design Agent verdict: PASS
