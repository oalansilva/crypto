# Snapshot — card #801 `card-801-t14-qa-closeout` (Assessment B)

- Card: #801 — https://github.com/oalansilva/crypto/issues/801
- Change: `openspec/changes/card-801-t14-qa-closeout/`
- Critic: isolated Design Critic B (detector; no transcript inherit; no Assessment A)
- UTC: 2026-08-30T00:03:59Z
- Tuple (sessão unbound): hooks `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`.
- Board: `oalansilva` Project 1 — **Status=Design** (não Todo; `UI impact: none` não saltou coluna).
- UI impact: **none** (harness/CLI/Guard/Moore/skill; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: N/A confirmed (sem HTML desta change; `frontend/public/prototypes/` sem `card-801-*`; Playwright visual **não** correu)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Detector desta onda = sondas live de `process_event` T11/T14, `measure_checks_green`, `T14Error`, Guard `checkout -b`, `EVENT_GUARDS`, dirty throwaway. Impeccable visual / `DESIGN.md` / Playwright desta coluna = N/A.
- `design.md` sha256: `3dc8a262bfddf6eefd350e656802a2a22df21c4631b83f50d09b9dbd0fe44a82` (~1445 palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + 6 spec deltas)
- `openspec validate card-801-t14-qa-closeout --type change --strict`: **valid**
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto).
- Browser gate: **N/A (no UI)**.
- Q1=A, Q2=A, Q3=A congeladas (não reabrir).

---

## Brief

Operador do harness (pai Cursor e root dsh): unit/`openspec validate`/filho QA verde não fecha Done. Live: T11 (`aceitar_sha`) entra em QA sem PR; T14 colapsa causas em `guard:checks_green` / `I8` mudo; `sync_dev_source` aborta dirty sem path; `checkout -b card-*` no canónico é allow. Card #801: T11 `no_pr`, classificador T14, `T14Error` visível, Guard canónico, Moore/skill mesmo turno. Não reabre #632/#729. Não mede `reviewers_ok`. `UI impact: none`.

Audience: pai Cursor e root/script dsh no closeout QA. Outcome: reject parseável + Done só com PR + qa-gate verde + canónico limpo, no mesmo turno. Direction: `reason` token + `message` humano; Guard `decide()` é a lei. Scope: `process_event` / `t14` / `guard` / stub QA / skill; sem produto UI; sem Σ/yaml T11–T14.

---

## Probes (live, este worktree, pré-Apply)

Invocações injectadas (FakeMover / runner scripted). Sem `process_event` live contra o board. Sem `git checkout -b` no canónico. Dirty = throwaway `/tmp`.

### T11 `aceitar_sha` sem PR

`process_event("aceitar_sha", q=Code Review, q_git=card-792-x, bound=792)` → **`transition` `to=QA` `reason=T11`**. Mover `[(792, "QA")]`. Sem `message`. Nenhum `_pr_list_json`. `EVENT_GUARDS["aceitar_sha"] = {reviewers_ok: True, open_p0_p1: False}` — True só pelo nome. Fixture `test_aceitar_sha_moves_qa` reproduz isto sem PR. Q1=A / spec / task 1.2–1.3 fecham o furo.

### T14 `integrar_develop` + `measure_checks_green`

| Sonda | Resultado live |
| --- | --- |
| `checks_green=None`, measurer omitido | `reject` `reason=guard:checks_green`; mover vazio |
| measurer `lambda: False` | `reject` `reason=guard:checks_green` (causa colapsada) |
| CLI `--checks-green` | `unrecognized arguments` (já morto) |
| `classify_qa_gate` | **ausente** |

`measure_checks_green` é **bool**. Scripted: `no_q_git` / PR vazio / sem head / pending / failure / gate ausente / API erro → `False`; `completed`+`success` → `True`. `_pr_list_json` com `returncode != 0` devolve `[]` (fail-closed).

### `T14Error` engolido como I8

`except T14Error:` em `process_event.py` devolve só `reason=I8` — **sem `message`**. Live:

- runner `T14Error("sync: dirty")` → `{result: reject, reason: I8}` — chave `message` ausente
- runner `T14Error("squash: no PR")` → idem `I8`

`_payload` já aceita `message` se truthy. O swallow não passa `str(exc)`.

### Guard `checkout -b` no canónico

`extract_paths("git checkout -b card-*")` = `[]` → early-return **allow** (depois de `status_item_edit`). Overlay injectado `environments.dev.source=/tmp/canonical-dev`:

| Comando | cwd | permission live |
| --- | --- | --- |
| `git checkout -b card-801-t14-qa-closeout` | canónico | **allow** |
| `git switch -c card-792-x` | canónico | **allow** |
| `git checkout --track -b card-801-x` | canónico | **allow** |
| `git checkout -B card-801-x` | canónico | **allow** |
| `git checkout -b card-801-…` | worktree | allow (regra ainda não existe) |
| `git checkout develop` | canónico | allow |
| `git worktree add …` | canónico | allow |
| `git -C /tmp/canonical-dev checkout -b card-801-x` | worktree | **allow**, `paths=[]` |

Fallback `.cursor/hooks/process-fsm-guard.sh`: sem matcher `checkout -b` / `canonical_card_branch`. `status_item_edit` já corre **antes** do early-return sem path — o ouro do D6.

### Dirty throwaway (não canónico)

`LiveT14Runner.sync_dev_source` em repo tmp sujo (`dirt.txt` untracked): `T14Error('sync: dirty')`. Texto **sem** path e **sem** porcelain. Só `git status --porcelain`. Sem `checkout` / `merge` / `reset`. Q2=A live já segura; falta visibilidade.

Canónico `/srv/apps/dev/criptofarol/source`: porcelain **0** neste turno (o #798 foi sujo; o invariante não depende do dirty actual).

### Spec viva vs archive #632

Main `openspec/specs/process-fsm-event/spec.md:73` ainda: `T10-T13 events imply exclusive-group guards; T14 stays reject live` + «`integrar_develop` MUST reject in live (`checks_green` unset)». Archive #632 já RENAMED o leftover e ADDED T14 atómico (dirty → `reason=I8`). Código live **já** mede e corre runner. Drift de spec, não regressão de #632.

Issues GitHub #632 / #729: `state=OPEN` (board ≠ `gh issue close`). Issue #801: #632/#729 **Pronto** no board — este card não os arrasta.

### Superfície visual / Moore / skill

Nenhuma rota/HTML. `context_file[QA]` live = uma linha: «Não mexer fonte. CI. T13 volta a Em desenvolvimento.» Skill `covenant-flow` já diz «filho QA (checks), T14» no pai, sem mesmo-turno / pending / ramo dsh. Plugin dsh já tem `runPage` / `covenant-flow:moore`.

---

## Hunt (furos pedidos) — contrato vs live

| Furo | Contrato | Live | Disposition |
| --- | --- | --- | --- |
| T11 sem PR | Q1=A; D3; spec `no_pr` + mover vazio + Status Code Review; tasks 1.2 / 1.3 | `aceitar_sha` → QA sem PR; fixture move QA | **CLOSED** no contrato (live é o bug) |
| `measure_checks_green` bool | D2 `classify_qa_gate`; wrapper `ok`; tokens `no_pr` / `qa-gate pending` / `qa-gate failed`; task 2.1–2.2 | bool; 7 causas → `False`; `guard:checks_green` | **CLOSED** |
| `T14Error` → I8 mudo | D4; spec dirty `sync: dirty` + `message` path+porcelain; outro runner `I8`+`message`; tasks 2.3 / 2.4 | swallow sem `message`; dirty sem path | **CLOSED** |
| `checkout -b` canónico | D6; spec `canonical_card_branch` **antes** empty-path; tasks 3.1–3.3 | allow; `paths=[]`; bash sem matcher | **CLOSED** |
| `EVENT_GUARDS reviewers_ok` | Q3=A; D3; spec «true from the event name»; Non-Goal medir | `aceitar_sha` → True pelo nome | **CLOSED** (intacto) |
| Reabrir #632 / #729 | Non-Goals; D8; Apply 6; spec MUST NOT Task matcher; dirty sem mutate | leftover spec ≠ código; archive #632 dirty=`I8`; #729 OPEN no GitHub | **CLOSED no contrato** |
| Dirty throwaway / mutate | Q2=A; D4; spec AND sem checkout/merge/reset; Non-Goal throwaway | throwaway: raise antes de mutate; sem path no texto | **CLOSED** |
| `--checks-green` | D2; spec CLI MUST NOT; task 2.1 | argparse recusa | **CLOSED** |
| `UI impact: none` bypass | Prototype N/A; T7 permanece | Status **Design**; sem HTML; sem `## Design Critique` | **CLOSED** |

---

## Critique (contrato vs live)

Issue #801 sintetizado (Q1–Q3 no body, congeladas). Pacote OpenSpec MODIFIED/ADDED; leftover #612 RENAMED (igual ao archive #632) + ADDED closeout estruturado.

| Entra | Onde |
| --- | --- |
| T11 `no_pr`, não cria PR | D3; spec T11; tasks 1.2 / 1.3; Apply 1 |
| Classificador + tokens; bool só yaml | D1/D2; spec T14; tasks 1.1 / 2.1–2.2 |
| Dirty visível; I8 = fica QA | D4; spec dirty + I8 runner; tasks 2.3 / 2.4 |
| Pending = turno espera e repete; `process_event` one-shot | D5; spec MUST NOT poll; cursor-harness; task 4.1 |
| Guard canónico `cwd` ou `git -C` | D6; spec SHALL; task 3.1 |
| Moore núcleo + skill Cursor/dsh | D7; process-fsm + covenant-flow + process-harness; tasks 4.1–4.3 |
| `reviewers_ok` pelo nome; sem #632/#729 | D3/D8; Non-Goals; Apply 6–7 |
| Sem produto / HTML / `DESIGN.md` / Σ T11–T14 | Apply 7; tasks 5.3 |

`## Open Questions` = nenhuma bloqueante. Prototype N/A justificado. Sem HTML. Sem rewrite `DESIGN.md`. Sem `## Design Critique` pré-preenchido. T7 humana permanece.

Aceite observável pós-Apply: T11 sem PR = `no_pr` + Status Code Review; T14 pending/failed/no_pr visíveis; dirty = `sync: dirty` + path + porcelain sem mutate; `checkout -b`/`switch -c` no source = deny `canonical_card_branch`; `reviewers_ok` continua pelo nome; yaml T11/T14/Σ/I8 texto intactos.

---

## Findings

### P0

(nenhum)

### P1

(nenhum)

### P2

- **Cenários Guard só testam `cwd`.** O SHALL e a task 3.1 exigem deny quando `git -C` resolve para `environments.dev.source`. Live: `git -C /tmp/canonical-dev checkout -b card-801-x` a partir de worktree → `paths=[]` → **allow**. Se Apply implementar só o cenário «cwd = source», o #792 sobrevive com `-C`. Disposition: Apply MUST golden `git -C <source> checkout -b card-*` / `switch -c` com cwd ≠ source → deny `canonical_card_branch`; o empty-path early-return não pode ganhar.

### P3

- `git checkout -B` / `git switch -C` (create-or-reset) são allow live e estão fora da lista do spec (`-b`, `--track -b`, `-c`). O issue «equivalente» pinou `switch -c`. Residual: bypass por `-B`/`-C` no canónico.
- `git branch card-*` + `git checkout card-*` (branch já existente) é allow por desenho. Fora do recorte.
- D4 «se o texto/atributo for dirty»: `RecordingT14Runner(fail_at="sync_dev_source")` levanta `T14Error("sync_dev_source")`, não `"sync: dirty"`. Task 2.4 mantém I8+`message`; fixture #798 MUST usar dirty real com path+porcelain. Apply MUST NOT classificar `"sync_dev_source"` como `sync: dirty`.
- `_pr_list_json` com `returncode != 0` → `[]` (T11 falharia closed = `no_pr` se usar o mesmo helper). `json.loads` sem catch pode rebentar o evento. T14 classificador já mapeia JSON erro → `qa-gate failed`. T11 MUST injectar lister e MUST NOT chamar GitHub (task 5.1).
- Stub QA + header/footer do `page()` tem de caber em 20 linhas (spec). Stub live = 1 linha; o novo texto D7 cabe se for curto. Task 4.1 / 4.3.
- Task 5.2 `openspec validate --all`; canónico desta sonda: `openspec validate card-801-t14-qa-closeout --type change --strict` (valid).
- Issues #632/#729 continuam OPEN no GitHub; Status de board é que não se arrasta. Apply MUST NOT `gh issue close`.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. **Browser gate: N/A (no UI).**
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM: sem task de estado/evento/`enabled_tools`. Status já Design; T7 Alan; T5 parent. `UI impact: none` não pulou Design nem Aprovação de Design. Yaml T11/T14/Σ/I8 texto MUST permanecer (Apply 7).
- Product UI Cripto: zero `frontend/src/` / `backend/` / HTML no Apply contract.
- Q3=A: `EVENT_GUARDS` intacto; este card não abre o irmão `reviewers_ok` medido.
- Q2=A: dirty throwaway não mutou; contrato proíbe throwaway/checkout limpo.
- Q1=A: T11 não cria PR; cliente abre e re-chama.
- #632 atómico (squash → sync → restart → comment_done; dirty sem mutate; I8 = fica QA) restated, não revertido. Reason dirty passa de `I8` (archive) para `sync: dirty` (visibilidade). #729: filho QA continua sem `process_event`; sem matcher Task em `decide()`.

---

## Trace

1. Live: T11 sem PR → QA; T14 `guard:checks_green` / `I8` sem `message`; `measure_checks_green` bool; dirty `T14Error("sync: dirty")` sem path, sem mutate; Guard allow em `checkout -b`/`-C` no canónico; leftover spec «T14 stays reject live»; `reviewers_ok` pelo nome.
2. Issue #801 DoD = T11 `no_pr`, tokens T14, dirty visível, Guard canónico, mesmo turno, dsh sem filho QA; Q1=A Q2=A Q3=A; não reabrir #632/#729.
3. Design D1–D8 + Apply contract 1–7 pinam o DoD; leftover RENAMED; yaml T11–T14 intactos.
4. Specs cobrem T11 PR, classificador, dirty, Guard, Moore, skill, dsh Moore; `openspec validate --strict` verde.
5. Tasks 1.1–1.3 / 2.1–2.4 / 3.1–3.3 / 4.1–4.3 / 5.1–5.3 são o ouro que o Apply falha se deixar T11 sem PR, I8 mudo, mutate dirty, allow `checkout -b` no source, ou medir `reviewers_ok`.

---

## Disposition

Zero P0/P1 abertos. Os sete furos pedidos estão fechados no contrato (T11/T14 live, bool `measure_checks_green`, `T14Error`→I8 mudo, `checkout -b` canónico, `EVENT_GUARDS reviewers_ok` intacto, não reabrir #632/#729, dirty sem throwaway). Residual P2 (golden `git -C` além de cwd) não colapsa o DoD se Apply seguir o SHALL/task 3.1, não só o cenário cwd. Dual-write Σ/yaml, medir `reviewers_ok`, throwaway, `--checks-green`, UI/HTML, e bypass de coluna estão fechados no texto. Detector/browser visual **N/A (no UI)**. Prototype N/A. `files_g_design` passa. Design Critique **não** pré-preenchido.

Pai: com A também PASS e zero P0/P1, colar `## Design Critique` e `process_event submeter_design`. Sem polish neste transcript. MUST NOT editar `design.md` daqui. MUST NOT `process_event` neste filho.

### Verdict

**PASS**
