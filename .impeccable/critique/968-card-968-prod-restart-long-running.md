# Snapshot — Design critic (sem-tela, 1 crítico, NÃO A/B) · card #968 `card-968-prod-restart-long-running`

- Card: #968 — Release: deploy PROD deve reiniciar todos os units que rodam código (discovery-worker ficou de fora)
- Change: `card-968-prod-restart-long-running`
- Critic: 1 isolado (NOT A/B); sem transcript do pai; sem nested agent; sem Assessment A/B
- Modelo: Grok 4.6 (`cursor-grok-4.6-high`)
- proxy modelo: design-critic → Grok 4.6 (cursor-grok-4.6-high)
- UTC: 2026-09-18T13:10:00Z
- Round: crítico 1/1 (teto D4 sem-tela = 1 autor + 1 crítico + 1 rework; segundo rework só com P0 novo de produto justificado no prompt)
- Tuple (este isolado): Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit/push. Não `move_agent_to_root`. Não editar `design.md` / proposal / tasks / specs / HTML / overlay / produto.
- Board / issue: REST `GET /repos/oalansilva/crypto/issues/968` (não `gh issue view`). OPEN; labels `priority:P1` `type:operacao`. Prompt do pai: Status Project 1 = Design. UI impact: none (sem ecrã). Sem Assessment A/B.
- Digest `design.md`: lido na íntegra (**93** linhas). `## Design Critique` / `Design Agent verdict`: **pendentes** (filho autor correcto; pai cola depois). Este crítico **não** edita `design.md`.
- UI impact: **none** (operação de release/PROD / overlay / `release-guard`; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*968*`; proto dir sem artefacto 968. Justificativa no `design.md` ## Prototype não vazia. Impeccable / Playwright visual / `DESIGN.md` = N/A. Este ficheiro é o snapshot git-tracked da crítica de processo (T7).
- Gate tokens parseáveis (linhas próprias no `design.md`):
  - `UI impact: none`
  - `live_route: N/A operação de release/PROD (units systemd de longa duração); sem tela de produto`
  - `surface: new`
- Clone gate isento via `UI impact: none` + `live_route: N/A` justificado (não é chave de catálogo) + `surface: new` (≠ `existing`; padrão aceite em #821/#854/#859/#893/#927 — **não** é tela Cripto nova). **Nenhuma** rota de catálogo emprestada (`/monitor` `/favorites` `/combo/discovery` `/combo/select` `landing`). Sem proto **ok**.
- Bloco D4 teto: **presente** no `design.md` (texto exacto da skill).
- Method: issue #968 REST (Problema / História / Entra / Não entra; Q2=B Q3=A Q4=A; Q1 sem A/B → *como* no Design); proposal / design Decisions 1–6 + Apply contract / Risks / `tasks.md` 1–6; deltas `oracle-environment-map` + `release-worktree-hygiene` + `prod-discovery-workers`; live overlay PROD (pré-Apply: sem discovery-worker, sem `oneshot_services`); live `scripts/release-guard` `post` (pré-Apply: evidência não vazia, **não** recusa `services=` incompleto).

---

## Surfaces lidas

| Superfície | Classificação |
| --- | --- |
| Issue #968 body (REST `GET /repos/oalansilva/crypto/issues/968`) | lido — Problema / História / Entra / Não entra; Q2=B Q3=A Q4=A; Q1 «não percebi» |
| `openspec/changes/card-968-prod-restart-long-running/{proposal,design,tasks}.md` | lido |
| `openspec/changes/card-968-prod-restart-long-running/specs/{oracle-environment-map,release-worktree-hygiene,prod-discovery-workers}/spec.md` | lido |
| Live `.covenant-flow/overlay.yaml` `environments.prod` | lido — services = backend, frontend, leads, runtime-worker, candle-writer, telegram-alert-scan; **não** lista discovery-worker; **não** há `oneshot_services` (pré-Apply) |
| Live `environments.dev.services` | lido — inclui `criptofarol-dev-discovery-worker` |
| Live `release.restart: ./restart` | lido — fecho DEV canónico; não é o caminho PROD |
| Live `scripts/release-guard` evidência `post` | lido — exige `PROD_DEPLOY_EVIDENCE` não vazio; **não** recusa `services=` incompleto (pré-Apply) |
| `frontend/src/**`, `backend/` de app, proto HTML 968 | **none** / ausente |
| Catálogo `/monitor` `/favorites` `/combo/*` `landing` | **não emprestado** |

Nenhuma superfície de produto nova/alterada ficou sem classificação. Prototype N/A justificado.

Este crítico **não** editou `design.md` / proposal / tasks / specs / overlay / produto.

---

## Brief (só neste snapshot)

Quem sofre é Alan, dono da release: o código homologado chega ao disco de produção, mas um processo de longa duração fica em memória no código velho — e ele só descobre depois, pela lentidão da Descoberta, que a release não valeu por inteiro. Facto no overlay (18/09, pré-Apply): PROD não lista o worker de varredura; DEV lista. Candle-writer e telegram-alert-scan estão na lista PROD como units do produto, mas são oneshot.

Direction do autor: Q1 *como* = lista canónica no overlay, classificada (`services` + `oneshot_services`; janela = diferença), **não** scanner vivo no host. Na mesma janela do publish já existente, `systemctl restart` dos de longa duração. `post` recusa evidência incompleta e unit activo ainda no boot anterior; processo parado + health ok não bloqueia (Q2 B); sem cronómetro da Descoberta (Q3 A); sem desfazer disco (Q4 A). `./restart` DEV intocado. Sem caminho novo de restart fora do fecho.

Q2=B, Q3=A, Q4=A **não reabertas**. Q1 fechada na decisão 1. Não entra permanece Non-Goal.

---

## Critique (rubrica UI none + D4)

### 1. Tokens parseáveis + clone gate + Prototype N/A

Três tokens em linha própria no `design.md` (L7–L9). Sem-tela declara ausência (`none` / `N/A`) + justificativa curta na mesma linha / frase seguinte. `live_route` começa por `N/A` e **não** é rota de catálogo. `surface: new` ≠ `existing` → clone gate isento; sem proto. `## Prototype` e `## Impeccable` N/A com texto não vazio. Zero HTML `frontend/public/prototypes/*968*`. Bloco D4 exacto. Apply contract MUST NOT `backend/` produto / `frontend/src/` / HTML.

Tokens **ok**. D4 **ok**. Clone gate **passa sem proto**. Nenhuma rodada extra para o parser.

### 2. proposal copia Problema / História / Entra / Não entra do issue

Diff REST issue #968 ↔ `proposal.md` nas quatro seções (não `## Why` / `## What Changes`):

| Seção | Resultado |
| --- | --- |
| Problema | **idêntico** ao body REST |
| História | **idêntico** (inclui factos e Q1 «não percebi»; não é história inventada) |
| Entra | **idêntico** (janela, Q1 sem A/B, Q2 B, Q4 A, Q3 A, âmbito só PROD, inventário, nota do dia) |
| Não entra | **idêntico** (DEV restart, caminho novo, PG/proxy, só documentar 16/09, oneshot por simetria, cronómetro Descoberta, desfazer disco) |

`## Why` é ponte OpenSpec (origem + Q2=B Q3=A Q4=A congeladas + Q1 *como* no Design). Não substitui as quatro seções. Gist = *superset* (história copiada + *como*). Sem segunda entrevista.

### 3. Entra observável vs *como* — Q2/Q3/Q4 não reabertos; Q1 = lista classificada

| Aceite do cartão | Pacote |
| --- | --- |
| Q2=B fecho pode PASS se longa duração parado e site/API respondem | Decision 5; spec `release-worktree-hygiene` «Stopped long-running unit…»; task 4.2. Continua a exigir o nome em `services=` (completeness). Não reabre Q2. |
| Q3=A não cronometrar Descoberta / não provar comportamento novo da varredura nesta janela | Non-Goals; specs MUST NOT exigir timing; task 5.2. Não reabre Q3. |
| Q4=A recusa visível se evidência omitir longa duração **ou** longa duração a correr ainda no código velho; não desfazer disco | Decisions 3–4; spec completeness + stale-code; tasks 3.1–4.1. Não reabre Q4. |
| Q1 *como* = lista overlay classificada, **não** scanner vivo | Decision 1: `services` + `oneshot_services`; janela = diferença; rejeitado scanner `Type=simple` fora do overlay. Spec `oracle-environment-map` «Live process outside the overlay is not the publish inventory». |
| Janela do publish: reiniciar site, API, captação, runtime-worker, worker de varredura; oneshot fora | Decision 1–2; spec PROD overlay lists discovery worker; spec classify oneshot. |
| Âmbito só produção | Non-Goals + spec `prod-discovery-workers` DEV `./restart` unchanged; sem comando novo fora do fecho. |
| Nota do dia a partir do inventário | Decision 6; spec release note from overlay. |

Open Questions = nenhuma. P3 do autor são detalhe de Apply, não perguntas de operador.

### 4. Escopo furado? (lista do prompt)

| Risco de furo | Veredito |
| --- | --- |
| Mudar restart DEV / `./restart` | **Não.** Non-Goal, task 2.2, spec DEV path stays unchanged. Overlay `release.restart: ./restart` permanece o fecho DEV. |
| Caminho novo de restart PROD fora do fecho | **Não.** Decision 2: mesmo gesto de setembro (`systemctl restart` no fecho já existente), lista agora completa. Consulta systemd no `post` é predicado de evidência (Q4 A), não entrypoint novo. Spec MUST NOT create a new production restart command. |
| Reiniciar oneshot na janela por simetria | **Não.** `oneshot_services` subtrai candle-writer e telegram-alert-scan. Extra em `services=` = aviso, não blocker. |
| Cronómetro Descoberta | **Não.** Q3 A; specs MUST NOT. |
| Rollback / desfazer disco | **Não.** Q4 A; guard MUST NOT roll back. |
| UI emprestada / catálogo | **Não.** Tokens none/N/A/new; proto ausente; rotas nomeadas como never-lend. |

Nenhum furo de produto/escopo/contrato visível.

### 5. Clone gate

`UI impact: none` + `live_route: N/A` (não catálogo) + `surface: new` (≠ existing) → **passa sem proto**. Impeccable N/A justificado. Sem `DESIGN.md` / Playwright visual.

### 6. Regressão operacional (pré-Apply, não bloqueante)

- Live overlay PROD ainda omite `criptofarol-prod-discovery-worker` e não declara `oneshot_services`. Esperado até Apply. Factos do issue/design confirmados no disco.
- Live `post` ainda só exige evidência não vazia. Evidência estilo 16/09 (quatro units, sem varredura) ainda passaria — é o aceite deste card a inverter, não drift do pacote.
- `AGENTS.md` always-on MUST NOT crescer; skill `covenant-flow-environments` só recorte se o pin ainda mandar reiniciar `services[]` sem subtrair oneshot.

### 7. Apply contract executável

Paths fechados: `.covenant-flow/overlay.yaml` (`prod.services` + `prod.oneshot_services`); `docs/crypto-overlay.md` (janela = inventário longa duração; nota do dia); `scripts/release-guard` `post` (e `pre` quando já exige evidência); testes `backend/tests/integration/test_release_guard.py` (ou equivalente); skill environments MAY recorte. MUST NOT `./restart` DEV, HTML, `backend/` produto, `frontend/src/**`, PG/proxy, caminho novo, cronómetro, rollback de disco, reescrever `docs/release-2026-09-16.md` como entrega.

P3 já nomeados pelo autor (não reabertos como P0/P1): nome exacto da chave YAML; normalização `.service`; campo systemd + âncora temporal; validação `overlay.py`; fixtures `services=app`; recorte pin da skill.

---

## Audit

| Item da rubrica | Resultado |
| --- | --- |
| Tokens parseáveis `UI impact` / `live_route` / `surface` | PASS — três linhas próprias; `live_route` N/A justificado, não catálogo; `surface: new` |
| Prototype N/A justificado | PASS — secção não vazia; zero HTML 968 |
| Clone gate (none + N/A + ≠ existing) | PASS — isento sem proto |
| proposal copia as 4 seções do issue | PASS — idênticas; Why não substitui história |
| Q2=B Q3=A Q4=A não reabertos | PASS |
| Q1 *como* = overlay classificado, não scanner vivo | PASS — Decision 1 + spec |
| Escopo furado (DEV, caminho novo, oneshot, cronómetro, rollback, UI) | PASS — todos Non-Goal / MUST NOT |
| Bloco D4 exacto | PASS |
| Classificação P0/P1 vs P3 | PASS — zero furo visível; yaml/systemd/fixtures = P3 |
| Snapshot não vazio | este ficheiro |

Finding determinístico sem classificação: **nenhum**.

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: (nenhum)
- P3: Nome exacto da chave YAML `oneshot_services` e MUST subconjunto de `services` (validação em `overlay.py` só se o parser já rejeitar extra). Disposition: **aceite** (detalhe de Apply; Decision 1 + Risks).
- P3: Campo systemd exacto (`ExecMainStartTimestamp` ou equivalente) e âncora temporal da janela. Disposition: **aceite**.
- P3: Como o teste injeta timestamp / fixtures sintéticas `services=app` (janela mínima ou overlay de teste). Disposition: **aceite**.
- P3: Recorte pin da skill `covenant-flow-environments` se ainda mandar reiniciar `services[]` sem subtrair oneshot; `pre` quando já exige evidência. Disposition: **aceite**.

Dual-write yaml/`AGENTS.md` / reabrir Q2–Q4 / scanner vivo / DEV `./restart` / HTML / superfície visual sem classificar / rota de catálogo / rollback de disco: **false**.

---

## Disposition

Zero P0/P1 aberto. Residuais P3 são detalhe de Apply já antecipados pelo autor (YAML, systemd, fixtures, pin) — aceitos, não reabertos como P0/P1. Tokens parseáveis presentes; Prototype N/A justificado; clone gate isento; Entra/não entra do issue não reaberto; Q1 fechada como lista classificada. Sem rework.

## Verdict

**PASS**

Prototype: N/A — `UI impact: none`; operação de release/PROD (units systemd); nenhuma tela CriptoFarol; justificativa não vazia em `## Prototype`.

Tokens: **ok** (`UI impact: none` / `live_route: N/A …` / `surface: new` em linha própria). Missing: nenhum.

`design.md` **não** editado por este crítico.

Path: `.impeccable/critique/968-card-968-prod-restart-long-running.md`
