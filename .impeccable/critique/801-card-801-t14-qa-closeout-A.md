# Snapshot — Assessment A · card #801 `card-801-t14-qa-closeout`

- Card: #801 — Harness: QA verde não fecha Done — T11 sem PR, T14 opaco, source canónico sujo
- Change: `openspec/changes/card-801-t14-qa-closeout/`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested critic)
- Modelo: inherit
- UTC: 2026-08-29T23:59:12Z
- Round: 1
- Tuple (este isolado): worktree `/srv/apps/dev/criptofarol/crypto-worktrees/card-801-t14-qa-closeout`; branch `card-801-t14-qa-closeout`. Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não commit. Não editar `design.md`.
- Digest `design.md` **medido**: sha256 `3dc8a262bfddf6eefd350e656802a2a22df21c4631b83f50d09b9dbd0fe44a82` · **1445** palavras (`str.split`) · 10654 bytes · 136 linhas
- `openspec validate card-801-t14-qa-closeout --type change --strict`: **valid**
- Issue #801: OPEN; fronteira vazia; Q1=A Q2=A Q3=A congeladas
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto; pai cola depois de A/B)
- UI impact: **none** (harness T11/T14 — CLI, Guard, Moore, skill). Nenhuma rota, shell, componente, token ou copy de ecrã CriptoFarol
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*801*`; aceite = payload `reason`/`message` + deny Guard + stub QA. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Sem Playwright desta coluna
- Method: issue #801 (DoD + vocabulário; Q1–Q3 congeladas); `proposal.md` / `design.md` D1–D8 + Apply contract / `tasks.md` 1–5; deltas `process-fsm-event` `process-fsm` `process-fsm-guard` `cursor-harness` `covenant-flow` `process-harness`; live `process_event.py` `t14.py` `guard.py` yaml `context_file[QA]` I8/T11/T14; archive #632; spec viva leftover «T14 stays reject live»; skill `covenant-flow` § QA; plugin dsh `covenant-flow:moore`

---

## Brief (só neste snapshot)

Operador (pai Cursor e dsh): unit / `openspec validate` / filho QA verde não fecha Done. T11 entra em QA sem PR; T14 devolve `guard:checks_green` / `I8` mudo; `sync_dev_source` aborta se o canónico estiver sujo. Evidência #792 (Pronto; `checkout -b` no canónico, sem PR) e #798 (Pronto; PR+qa-gate verde, canónico dirty, I8 mudo). Este card não os reabre. Q1=A T11 reject `no_pr`; Q2=A dirty⇒I8 com `sync: dirty` + path + porcelain; Q3=A `reviewers_ok` pelo nome do evento (card irmão). `UI impact: none`.

---

## Rubrica (UI none)

- **Escopo vs DoD** — seis aceites + Entra mapeados; Não entra não alargado
- **Regressão #632** — medidor bool + dirty⇒I8 sem mutate; este card só classifica causas e fecha drift da spec viva
- **Regressão #729** — filho QA lê checks; T14 no pai; sem matcher Task em `decide()`; dsh sem filho QA já está no Entra
- **Ops** — I8 opaco e `checkout -b` no canónico
- **UI** — nenhuma superfície visual sem classificar

---

## 1. Escopo vs grill #801 (Q1–Q3 congeladas)

Body live: fronteira vazia. Design não reentrevista. Letras D1–D8 batem o Entra.

| Q / aceite | Onde no pacote |
| --- | --- |
| Q1=A T11 reject `no_pr`, não cria PR, Status Code Review | D3; proposal What; spec `aceitar_sha without PR stays Code Review`; tasks 1.2–1.3; fixture #792 |
| Q2=A dirty⇒I8 + `sync: dirty` + path + porcelain; sem throwaway | D1 + D4; spec `dirty canonical DEV source stays QA with visible cause`; task 2.3; fixture #798 |
| Q3=A `reviewers_ok` pelo nome do evento | D3; spec MODIFIED «remains true from the event name»; task 1.2; Non-Goals; card irmão não aberto |
| Aceite 2 `qa-gate pending` + turno repete | D2 + D5; spec pending; cursor-harness + Moore; `process_event` one-shot |
| Aceite 3 verde + limpo → Done | ADDED T14 restata closeout atómico #632; este card garante que o turno chega lá |
| Aceite 4 dirty visível **e** deny `checkout -b` | D4 + D6; specs event + guard; tasks 2.3 / 3.x |
| Aceite 5 dsh: PR antes de T11 + qa-gate + T14 | D7; covenant-flow + process-harness; plugin já injeta Moore |
| Aceite 6 fixtures #792 / #798 | tasks 1.3 / 2.2 / 2.3 |

**Não entra — não reaberto:** medir `reviewers_ok`; T11 cria PR; throwaway / checkout limpo; `--checks-green`; T7/T15; `item-edit` Status; produto `backend/` `frontend/src/`; fechar #792/#798; novo evento/coluna; dual-write da lei; poll dentro de `process_event`; reabrir #632/#729.

Proposal «New Capabilities: (nenhuma)» correcto — closeout de T11/T14/Guard/Moore já existentes.

Residual da grelha (reason vs `message`; classificador vs bool; plugin/moore vs skill; leftover spec; card irmão) está fechado em D1/D2/D7/D8. Sem Open Questions bloqueantes.

---

## 2. Fidelidade live (não é Apply)

### T11

- `EVENT_GUARDS["aceitar_sha"]` seta `reviewers_ok=True` só pelo nome. Yaml T11: `guard: reviewers_ok`, `actions: [diff_vs_develop, push, set_status]`. Intactos no contrato (não mexer Σ/yaml T11).
- `test_aceitar_sha_moves_qa` move QA **sem** PR. D3 + task 1.3: injetar PR presente + fixture #792 `no_pr`. Fiel ao furo.
- Probe **antes** de `evaluate`; alternativa `has_pr` no yaml rejeitada (mudaria Σ). Q3=A.

### T14 / medidor #632

- `measure_checks_green` é bool; False colapsa sem-PR / pending / failed / erro em `guard:checks_green`.
- `LiveT14Runner` levanta `T14Error("sync: dirty")` **sem** path; `process_event` `except T14Error` devolve só `reason=I8` sem `message`. `_payload` já aceita `message` se truthy. D1/D4 fecham o I8 mudo.
- `sync_dev_source` só em `environments.dev.source` (`/srv/apps/dev/criptofarol/source`); porcelain não-vazio ⇒ aborta **antes** de checkout/merge/reset. Q2=A preserva este invariante.
- `main()` injeta `checks_green_measurer=measure_checks_green`; testes injetam bool. D2: `measure_checks_green` = wrapper de `classify.ok`; bool injetado continua; MUST NOT GitHub nos unitários.

### Guard

- `decide()`: `is_status_edit_command` corre **antes** de `if not paths: return _allow()`. `git checkout -b` não casa `MUTATION_RE` → `extract_paths` vazio → **allow**. É o furo #792. D6 coloca o deny no mesmo sítio que `status_item_edit`.
- Fallback bash (`.cursor/hooks/process-fsm-guard.sh`): sem path de produto, ramo `else` **allow**. Task 3.2 + spec exigem a mesma classe. Lei = `guard.py` `decide()` (Cursor/Grok/OpenCode/dsh via `runGuard`).

### Moore / dsh / spec viva

- `context_file[QA]`: «Não mexer fonte. CI. T13 volta a Em desenvolvimento.» — não manda T14 nem «primeiro reject ≠ fim».
- Plugin dsh: `covenant-flow:moore` ← `runPage` (medido). D7: uma mudança no yaml; skill não é o único carrier.
- Spec viva `process-fsm-event` ainda tem «T14 stays reject live» + cenário «rejects without checks_green» quando unset — contradiz o código #632. Archive #632 já RENAMED + ADDED. Drift para este Design (D8), não reabre o medidor.

---

## 3. Regressão #632 (medidor) / #729 (filhos)

| Risco de reabrir | Contrato deste pacote |
| --- | --- |
| #632 `measure_checks_green` True só PR + `qa-gate` completed+success | D2: `ok` só nesse caso; tokens só quando `ok=False`. Outros checks no SHA não entram |
| #632 `--checks-green` proibido | ADDED + proposal + Non-Goals |
| #632 measurer None ⇒ reject; testes injetam | ADDED «classifier or measurer is None»; task 5.1 sem rede |
| #632 dirty ⇒ I8, sem checkout/merge/reset | Q2=A: invariante I8 (Status QA, sem mutate); `reason` passa a `sync: dirty` + `message` path+porcelain — visibilidade, não throwaway |
| #632 closeout atómico squash→sync→restart→comment_done | ADDED restata a ordem; yaml T14/I8 texto intactos |
| Spec leftover #612 no living | D8 RENAMED (igual archive #632) + ADDED classificado. Fecha drift; não religa reject permanente |
| #729 1 filho QA; T14 no pai; sem nested | cursor-harness + covenant-flow Cursor: filho lê checks, MUST NOT `process_event`; pai T14 no mesmo turno |
| #729 `decide()` sem matcher Task | process-harness + task 4.3: MUST NOT deny `Task`/`task` por menção QA/T14 |
| dsh sem filho QA | Entra do issue; não é «zero filhos» no Cursor. Skill SHALL no ramo Cursor |

Não reabrir. `reviewers_ok` medido fica no card irmão (Q3=A).

---

## 4. Riscos operacionais

### I8 opaco (#798)

Live: dirty e squash/restart/comment colapsam em `I8` sem `message`. D1: `reason` = token parseável; `message` = detalhe. Dirty → `sync: dirty` + path + porcelain. Outro runner fail → `I8` + `str(exc)` (deixa de ser mudo sem inventar token). `squash: no PR` → `no_pr` (cinto; classificador corta antes do runner). Missing runner continua `I8` (injeção). Operador/script ramifica no token, não em `guard:checks_green`.

### `checkout -b` no canónico (#792)

Deny **antes** do early-return sem path. Match: `checkout -b card-*` / `switch -c card-*` / `--track -b` quando `cwd` **ou** `git -C` = `environments.dev.source`. Reason `canonical_card_branch`. Allow: mesma criação em worktree `card-<id>-*`; checkout de branch existente; `git worktree add`. Path equality, não substring `card-` no cwd. dsh root no canónico: o deny impede repetir #792; closeout corre no worktree.

### Primeiro reject ≠ fim de turno

`process_event` não faz poll (D5). Pai/script espera `qa-gate pending` e reinvoca. Helper wait+reinvoke é Apply-ok, não evento novo. Risco «pai ignora Moore» está no design: skill + stub QA + fixture #798. Sem novo evento.

---

## 5. Superfície visual — classificação

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, tokens, copy CriptoFarol | **none** — fora |
| `backend/` de app | **none** |
| Protótipo HTML / Playwright / `DESIGN.md` | **N/A** — zero `prototypes/*801*` |
| Rubrica Impeccable visual | **N/A** |
| CLI `process_event` / payload JSON | harness — **entra** (não é UI) |
| Guard deny `canonical_card_branch` | processo |
| Moore `context_file[QA]` / skill `covenant-flow` | runbook operador |
| Plugin dsh `covenant-flow:moore` | já injeta; **não** dual-write T0–T17 |

`UI impact: none` + Prototype N/A justificados. HTML não gerado / não copiado.

---

## Achados

- P0: (nenhum)
- P1: (nenhum)
- P2: Match Guard lista `-b` / `-c` / `--track -b`. `git checkout -B card-*` e `git switch --create`/`-C` não estão no texto. Apply MUST tratar aliases de create/force-create `card-*` no canónico como a mesma classe, senão #792 volta com `-B`. Disposition: **accepted-residual**.
- P2: Fallback bash hoje **allow** quando não há path de produto. Spec/task 3.2 exigem a mesma classe; o snippet tem de resolver overlay `environments.dev.source` e casar o comando **antes** do allow sem path — não só `guard.py`. Disposition: **accepted-residual**.
- P2: Pai que ignora Moore ainda para no primeiro reject. Mitigação = stub + skill + fixture #798; sem evento novo. Disposition: **accepted-residual** (risco 1 do design).
- P2: `cursor-harness` MAY spawn filho QA; skill Cursor SHALL um filho. Compatível com dsh (sem filho) e com pai que já viu `qa-gate`. Apply MUST não apagar o spawn Cursor por causa do MAY. Disposition: **accepted-residual**.
- P2: D2 mapeia erro JSON → `qa-gate failed`. Live `measure_checks_green` faz `continue` em linha JSON má e só falha se não achar `qa-gate`. Wrapper `ok` MUST continuar a procurar o check pelo nome; um decode mau noutro check não pode virar failed se `qa-gate` está success. Disposition: **accepted-residual**.
- P3: Cenário «missing T14 runner» continua `I8` sem exigir `message` (erro de injeção, não o caso #798). Disposition: **accepted-residual**.
- P3: Task 5.2 `openspec validate --all` — CLI medida desta change: `openspec validate card-801-t14-qa-closeout --type change --strict`. Disposition: **accepted-residual**.
- P3: Stub QA novo tem mais frases; paging MUST ≤20 (task 4.1 + spec). Disposition: **accepted-residual**.
- P3: `_pr_list_json --state all` — PR fechado/merged conta como «existe» no T11. Fora do aceite «sem PR». Disposition: **accepted-residual**.
- Dual-write Σ/yaml T11–T14 / `--checks-green` / medir `reviewers_ok` / throwaway / `item-edit` / produto UI / HTML / Design Critique pré-PASS / reabrir #632/#729 / superfície visual sem classificar: **false**.

---

## Disposition

Zero P0/P1 abertos. Recorte Q1=A Q2=A Q3=A congelado; seis aceites mapeados; Não entra não alargado. #632: medidor bool + closeout atómico + dirty sem mutate permanecem; este card torna causas visíveis e fecha o leftover vivo «T14 stays reject live». #729: filho QA Cursor intacto; T14 no pai; `decide()` sem matcher Task; dsh sem filho QA já no Entra. Ops: I8 deixa de ser mudo (`sync: dirty` + path + porcelain; outros fails com `message`); `checkout -b` no canónico deny antes do early-return. Apply contract executável; spec observável (tokens + deny + stub). Residuais P2/P3 são aliases `-B`, fallback bash, pai que ignora Moore, e higiene de wrapper/paging — não bloqueiam.

Não há re-despacho de autor por P0/P1.

---

## Verdict

**PASS** (zero P0/P1 abertos; Prototype N/A justificado; UI impact none classificado; crítica isolada; snapshot não vazio)

## Snapshot

`.impeccable/critique/801-card-801-t14-qa-closeout-A.md`

Prototype: N/A — `UI impact: none`; harness T11/T14; nenhuma tela CriptoFarol.
