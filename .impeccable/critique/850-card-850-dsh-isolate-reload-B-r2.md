# Snapshot — card #850 `card-850-dsh-isolate-reload` (Assessment B r2)

- Card: #850 — https://github.com/oalansilva/crypto/issues/850 (OPEN, labels `priority:P0` `front:operacao` `type:operacao` `kaizen`)
- Change: `openspec/changes/card-850-dsh-isolate-reload/`
- Critic: isolated Design Critic B r2 (static + live operational detector; inherit de modelo; **sem** transcript do pai; **sem** resultados de Assessment A; **sem** inherit do B-r1 como prova — recheck só no texto r2 + runtime live)
- UTC: 2026-09-05T20:18:27Z
- Tuple: `resolve(cwd=worktree)` → `q=None` `bound_card=850` `q_git=card-850-dsh-isolate-reload`. Board Project 1 **Status=Design** (`PVTI_lAHOAAHtBM4BV8b2zg5mPKs`). Write produto deny. Esta onda só `.impeccable/critique/**`. MUST NOT editar `design.md`.
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-850-dsh-isolate-reload` (branch `card-850-dsh-isolate-reload`)
- Overlay live: `pin: v1.1.9`; `clients.dsh.auto: false`; `overlay_doc: docs/crypto-overlay.md`
- Produto origin tags: `v1.1.9` (latest) … `v1.0.0`. **`v1.1.10` ainda livre**
- UI impact: **none** (harness/ops dsh: helper de bounce + sidecar SHA + goldens + pin; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** confirmed — zero HTML desta change; `frontend/public/prototypes/` sem `card-850*`; Playwright visual **não** correu (Browser N/A; `/login` não conta)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Detector = issue vs OpenSpec r2 vs `dsh_boot.sh` actual vs processo vivo `:3080` vs goldens A7–A9
- `design.md` sha256: `766e1b3c7caa646251cd2aa578088db7adec67c7100faaa69823f6379d2dcdf2` (**2192** palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + 3 spec deltas: `developer-tooling`, `process-harness`, `covenant-flow`)
- `openspec validate card-850-dsh-isolate-reload --type change --strict`: **valid**
- `openspec` tasks: **17** checkboxes
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correcto; este crítico MUST NOT editar `design.md`)
- Git: change **untracked** (`?? openspec/changes/card-850-dsh-isolate-reload/`); zero diff de produto nesta onda
- Clone gate T5: `evaluate_clone_gate` → **True** (ramo `ui==none` + `not existing`). `parse_ui_impact=none`; `parse_live_route=('N/A', '— harness-only; …')`; `parse_surface=None` (linha `surface: new — isento…` falha `SURFACE_RE` que exige EOL após `new`); `is_new_exempt` True via `live_route: N/A` + justificação. Passa porque none, não porque `surface` parseie
- Issue REST: body grelhado (Proposta / Problema / História / Entra / Critérios 1–5 / Relacionados). 0 comments.

P1s r1 tratados como **fechados** só se o pacote r2 (design D1–D4 + Apply contract + tasks 1.1/2.2/3.1–3.3 + spec developer-tooling R7/R8/R9 + sidecar env) os pinarem. Este r2 só reabre um item fechado quando essas superfícies se contradizem. Código ainda ausente (`dsh_isolate_reload.sh` missing; boot sha `bdb01629…` inalterado) **não** reabre P1 de Design — é Apply.

---

## Round 2 — recheck P1 close

Pedido desta onda: P1-1 (A8/A9 + sidecar live) e P1-2 (trap wait) MUST estar no contrato: `DSH_ISOLATE_SIDECAR`, R9, trap mata PID depois `rm`, R7, listen→`--port` R8, predicado cmdline `dsh`+`web`. Código ainda não existe — isso é Apply, não BLOCKED de Design.

| Critério P1 (r1) | Onde no pacote r2 | Live 2026-09-05T20:18Z | Resultado |
| --- | --- | --- | --- |
| P1-1 A8/A9 MUST `DSH_ISOLATE_LISTEN` efémero **e** copiar o sibling | design D4; task 3.3; spec scenario «Pytest A8 A9 and R-star…»; Apply contract | `_boot_tree` ainda copia **só** `dsh_boot.sh`; A8/A9 ainda herdam `os.environ` (sem listen/sidecar). Helper sibling **ausente** | **CLOSED** no contrato; residual = Apply |
| P1-1 override sidecar `DSH_ISOLATE_SIDECAR`; default `/tmp/…` só live | design D3; task 1.2 / 3.2 R3 / 3.3; spec sidecar SHALL + scenario R3 AND «`/tmp/…` is not overwritten»; Apply contract | Sidecar **ausente**. Fake A8/A9 `echo`+`exit 0` | **CLOSED** no contrato |
| P1-1 A8/A9 MUST NOT herdar default 3080 / esperar TCP em 3080 | D4 + task 3.3 «MUST NOT herdar default 3080»; spec THEN ephemeral listen | A8/A9 código actual ainda sem env — pré-Apply | **CLOSED** no contrato |
| P1-1 golden R9: A8/A9 **não** SIGTERM `127.0.0.1:3080` | D4; task 3.3; spec scenario R9 AND MUST NOT SIGTERM operator listener AND MUST NOT overwrite live sidecar; Apply contract lista **R9** | Pytest desta change ainda não tem R9 (pré-Apply) | **CLOSED** no contrato |
| P1-2 trap INT/TERM/EXIT mata `$DSH_PID`, confirma porta livre, **depois** `rm`; MUST NOT `rm` com listener vivo | design D2; task 2.2; spec Trap SHALL + scenario SIGINT; golden **R7**; alternativa rejeitada «trap só `rm`» | Boot actual: `cleanup() { rm -f "$TMP_PATCH"; }; trap cleanup EXIT`. Holding = bash **1010897** foreground espera node **1010906**; trap **não** corre; patch `VIsbNa` ainda no disco | **CLOSED** no contrato; live confirma o furo que R7 vai pinhar |
| P1-2 golden R7: SIGINT mata fake listener, tmp some **depois**, sem órfão | D2; task 3.3; spec «listener is gone and is not reparented as an orphan» AND «tmp patch is removed only after that kill» | Sem R7 no pytest actual | **CLOSED** no contrato |
| listen → `--port` R8 | D4; task 2.1 / 3.1 R8; spec scenario «Listen address maps to dsh web --port»; Apply contract | Live cmdline **já** tem `--no-open --port 3080`; boot git **não** passa esses flags (processo arrancado à mão / freeze de flags no invocador, não no script) | **CLOSED** no contrato |
| predicado cmdline `dsh`+`web` (não `comm`/`ss`/`argv0`) | D1; task 1.1; spec occupant SHALL `/proc/<pid>/cmdline`; R1 + **R5b**; Apply contract | `ss` name **`MainThread`**; cmdline `node …/.bin/dsh web --patch … --no-open --port 3080`; `argv0` ≠ `dsh` | **CLOSED** no contrato (casa com o live) |

---

## Brief

A GUI `http://127.0.0.1:3080` não é o pin `v1.1.9` **como processo gerido pelo helper**. Isolate Node testemunha r1 = PID 223762 desde 2026-08-30; entre r1 e r2 alguém relançou o **mesmo** `dsh_boot.sh` (sha `bdb01629…`) — PID **1010906** desde 2026-09-05 20:08:55, patch novo `VIsbNa`, parent bash **1010897** PPID=1. Isso é one-shot (issue `_Avoid:` / Design alternativa rejeitada), **não** o aceite: sem sibling, sem sidecar, sem `--check`, trap ainda só `rm`.

Audience: operador na GUI dsh e Homologação/Pronto de card de Guard dsh. Outcome: bounce via `dsh_boot.sh` substitui o listener; sidecar PID+SHA; `--check` fail-closed; dump autenticado. Direction r2: sibling `dsh_isolate_reload.sh` (predicado cmdline `dsh`+`web`) **antes** do `mktemp`; boot `&`+TCP wait+sidecar+`wait`; trap mata PID **depois** `rm`; goldens R7/R8/R9 + `DSH_ISOLATE_SIDECAR`; pin próximo patch após `v1.1.9`. Scope: pele `covenant-flow`; zero UI Cripto; MUST NOT reimplementar sanitizer/Diagnostic.

---

## Probes (live, este worktree, r2)

### Isolate vivo `:3080`

| Claim do Design r2 | Live 2026-09-05T20:18Z | Resultado |
| --- | --- | --- |
| Isolates desde 30/08 (PID testemunha 223762, patch `TbJZ2F`) | `ss`: `127.0.0.1:3080` → pid **1010906** (`MainThread`). `ps`: `node …/dsh web --patch /tmp/covenant-flow-dsh-VIsbNa.patch.yml --no-open --port 3080`, lstart **Sat Sep 5 20:08:56 2026**. 223762/223735/**TbJZ2F** **gone** | **LIVE mudou** (one-shot do boot antigo, não o sibling) |
| `dsh_boot.sh` actual lança sem substituir o listener | Boot worktree = source (sha256 `bdb01629…`): `mktemp` + `trap cleanup EXIT` (`rm -f`) + último comando **foreground** `dsh web --patch` — **sem** SIGTERM, **sem** `--no-open`, **sem** `--port`, **sem** sibling | **LIVE** (contrato r2 descreve o Apply) |
| Holding = foreground | Parent **1010897** `bash /srv/apps/dev/criptofarol/source/scripts/process-fsm/dsh_boot.sh`, **PPID=1**. Patch `VIsbNa` **ainda no disco** (trap não disparou) | **LIVE** — o mesmo seam que P1-2 fecha |
| Sidecar `/tmp/covenant-flow-dsh-isolate.json` | **Ausente** | **esperado** pré-Apply |
| `ss` nome vs cmdline | `ss` = `MainThread`; cmdline contém `dsh` **e** `web` | **LIVE** — justifica predicado D1 / R1 / R5b |
| `dsh_isolate_reload.sh` | **Ausente** | Apply, não Design |

O one-shot das 20:08 **não** fecha aceite 1: issue e Design rejeitam «recarregar à mão uma vez». Sem sidecar SHA, Homologação/Pronto de Guard dsh continua sem evidência de pin carregado. ESM do processo novo **pode** ter carregado blobs de 05/09 — `--check` + dump 7.2 continuam o DoD; pytest não substitui.

### Goldens que já invocam o boot (Apply vai estender)

`scripts/process-fsm/test_dsh_adapter.py` **inalterado** (pré-Apply):

- `_boot_tree`: copia **só** `dsh_boot.sh`.
- `test_a7_*`: exit ≠0 **antes** do `mktemp` (hoje). Contrato r2: A7 falha **antes** do sibling — alinhado.
- `test_a8_*` / `test_a9_*`: fake `dsh` `echo`+`exit 0`; **não** setam `DSH_ISOLATE_LISTEN` nem `DSH_ISOLATE_SIDECAR`. Env = `os.environ`.

Único caller de produção = bash 1010897 + receita `docs/crypto-overlay.md`. overlay_doc § dsh **ainda** sem frase bounce-após-pin (task 5.2 MUST; Apply).

### Pin / overlay_doc / AGENTS.md

- Overlay worktree **e** source: `pin: v1.1.9`, `dsh.auto: false`. Origin: `v1.1.10` livre.
- Pin-tests (`test_dsh_adapter.py`, `test_dsh_reasoning_effort.py`) hardcode **`v1.1.9`** — task 3.3 / D7: tag que Apply cravar, não `v1.1.10` no vácuo.
- `AGENTS.md`: 14 linhas não-vazias (≤40). Sem isolate/3080.
- `tmpfiles.d`: `D /tmp 1777 root root 30d`.

---

## Hunt (P0/P1 novos)

| Furo | Pacote r2 | Live | Disposition |
| --- | --- | --- | --- |
| P1-1 reaberto por omissão A8/A9 / sidecar | D3/D4 + 3.3 + spec R9 + `DSH_ISOLATE_SIDECAR` nomeado em design/tasks/spec/Apply contract | código A8/A9 antigo | **não reabre** |
| P1-2 reaberto por trap só `rm` | D2 + 2.2 + spec R7 (kill, porta livre, **then** `rm`; MUST NOT `disown`) | trap actual só `rm`; holding foreground | **não reabre** |
| Contradição D2 vs Apply contract «mata `$DSH_PID` **depois** `rm`» | D2/task 2.2/spec: kill **then** `rm`. Apply contract comprime o mesmo shorthand. R7 AND «removed only after that kill» | — | **não P1** (P3 wording; Apply segue 2.2/R7) |
| Predicado `comm`/`argv0` reabre pin morto | D1 rejeita; R1 MUST NOT verde só `argv0=dsh`; R5b occupant sem o par | live `MainThread` / `argv0=node` | **CLOSED** |
| listen ≠ `--port` | D4 + R8; fake MUST bind `--port` | live já tem flags; boot git não | **CLOSED** no contrato |
| One-shot 20:08 como DoD | Non-goal / alternativa rejeitada; tasks 7.1/7.2 `--check` + dump | bounce do **mesmo** boot, sem sidecar | **não P1** — confirma que o helper ainda falta |
| API inventada / pin cravado `v1.1.10` / dual-write T0–T17 / `AGENTS.md` | D7 `ls-remote`; spec covenant-flow MUST overlay_doc; AGENTS MUST NOT crescer | origin `v1.1.9`; AGENTS 14 linhas | **não P0** |
| Falso UI none | UI none + Prototype N/A + zero HTML `card-850*` + Apply MUST NOT `frontend/src/`/`backend/` | zero superfície Cripto | **CLOSED** |
| Código helper ausente | tasks 1.1–3.3 unchecked | `dsh_isolate_reload.sh` missing | **Apply**, não BLOCKED de Design |

---

## Rubrica (UI none)

- **Escopo:** issue critérios 1–5 sintetizados (bounce após pin/merge; sidecar SHA; 1º turno root sem 400 none; Diagnostic no filho via plugin já pinado; dump `:3080`). Pin neste card. Não reentrevista. Não reabre #817/#839/#837/#793/#846. Não vendorar `@deepseek-ai/dsh*` / `pi-ai`.
- **Regressão:** A7 antes do sibling; A8/A9 + R* com listen **e** sidecar efémeros; E1–E12 / F1–F8 / G1 / write deny. R9 tranca SIGTERM em `:3080`.
- **Riscos operacionais:** holding `&`+`wait` vs foreground vivo (R7); sidecar `/tmp` vs tmpfiles 30d; `--check` proxy disco; `ss` `MainThread`; one-shot ≠ helper.
- **Superfície visual:** nenhuma. Prototype N/A.

---

## Critique (contrato r2 vs live)

`openspec validate --strict` verde. Prototype N/A justificado. Sem HTML. Sem `## Design Critique` pré-preenchido. Clone gate T5 True pelo ramo none; `live_route: N/A` agora parseia; `surface: new — …` **não** parseia (`SURFACE_RE`). Pin origin correcto (`v1.1.10` livre). Canal sibling-via-boot alinhado com o único caller vivo. `AGENTS.md` / T0–T17 / outro script de boot: limpos.

**P1-1 fechado no texto.** O pacote deixou de isolar só R* e deixar A8/A9 no default `:3080` com sidecar canónico. `DSH_ISOLATE_SIDECAR` é o override nomeado; R9 é o golden negativo; A8/A9 MUST set ambos os env e `_boot_tree` copia o sibling; spec AND proíbe overwrite de `/tmp/covenant-flow-dsh-isolate.json`.

**P1-2 fechado no texto.** D2/task 2.2/spec: trap INT/TERM/EXIT SIGTERM/SIGKILL `$DSH_PID`, confirma porta livre, **then** `rm`; MUST NOT `rm` com listener vivo; MUST NOT `disown`/`setsid`; R7 pina SIGINT sem órfão e tmp **depois** do kill. O holding vivo (1010897 foreground → 1010906) continua a testemunhar o seam — o contrato agora assenta nele.

**R8 + predicado cmdline** estão no mesmo pacote (D1/D4, R1/R5b/R8). Live `MainThread` + `dsh web` no cmdline confirma que o matcher `comm`/`ss` fail-closaria o occupant que o card existe para substituir.

P0 de API inventada / pin cravado / dual-write / AGENTS.md: **não**. P1 operacional reaberto: **não**. Código ausente: **Apply**.

---

## Findings

### P0

*(nenhum aberto)*

### P1

*(nenhum aberto — P1-1 e P1-2 do r1 fechados no pacote r2; hunt de A8/A9/sidecar, trap/`rm`, R7/R8/R9, predicado cmdline, UI none, pin `ls-remote` não eleva P1 novo. Helper/goldens ainda inexistentes = Apply)*

### P2

- **`--check` é proxy disco+PID, não ESM.** Bounce no arranque é a mitigação (D5/risk). Residual: TCP listen ≠ plugin `apply()` concluído; SHA não inclui `impeccable-hook.js`. Aceite se o sidecar for escrito **após** listen **e** o bounce for o único writer; dump 7.2 continua obrigatório. Não reabre P1-1.
- **Sidecar `/tmp` × reboot × tmpfiles 30d.** Reboot: fail-closed correcto (isolate morto, sem #793). Isolate >30d: `--check` falha com processo saudável. overlay_doc SHOULD dizer «sidecar some com `/tmp`; bounce de novo».
- **One-shot 20:08 não é o aceite.** PID 1010906 / patch `VIsbNa` / parent 1010897 = o **mesmo** `dsh_boot.sh` foreground. Sem sidecar, sem sibling, trap ainda só `rm`. Homologação = 7.1 `--check` default live + 7.2 dump, não este restart.
- **`surface: new — isento…` fora do `SURFACE_RE`.** `parse_surface=None`. Gate passa porque `ui==none`. SHOULD linha `surface: new` sozinha (forma #839 r2). Não bloqueia T5 none.

### P3

- Proposal overlay_doc **MAY** vs design/task 5.2 / spec covenant-flow **MUST** 1–3 frases — Apply segue tasks; unificar o modal.
- Apply contract comprime D2 como «mata `$DSH_PID` **depois** `rm`»; D2/task 2.2/spec R7 são kill → porta livre → `rm`. Apply MUST seguir 2.2/R7 (não inverter).
- Task 3.3 cabeçalho «R6 / A7–A9»: R6 não tem scenario próprio no spec (R9 cobre A8/A9). Leftover de numeração; não furo de seam.
- Sidecar world-writable em `/tmp` (forge PID/SHA). Aceite para v1; Homologação humana continua o dump.
- 401 billing permanece residual (issue `_Avoid:`). 7.2 «falha, se houver» pode verde sem exercitar aceite 3 se o spawn passar.
- Change #817/#839 Pronto; este card MUST NOT as reabrir. #793 unit MAY `ExecStart` este helper noutro card.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. Browser gate: **N/A (no UI)**.
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM yaml: sem task de estado/evento. T1/T7 Alan; T5 parent. Dual-write T0–T17 **proibido** no pacote — **CLOSED**.
- Product UI: zero `frontend/src/` / `backend/` de app no Apply contract.
- Auto dsh: overlay live `false`; specs MUST NOT reivindicar.
- `CLIENT_KEYS` / `SCHEMA_MAJOR` inalterados.
- Vendor `@deepseek-ai/dsh*` / `pi-ai`: proibido.
- `dsh_boot` noutro script de produto: **CLOSED** (único live = 1010897).
- Pin `v1.1.10` hardcoded no Design: **CLOSED** (esperado se livre; Apply `ls-remote`).
- overlay_doc vs `AGENTS.md`: **CLOSED** no canal (MUST no overlay_doc via tasks/spec; AGENTS não cresce). Proposal MAY = P3.
- Código helper ausente / goldens A8/A9 sem env: **Apply**, não evidência de Design BLOCKED.

---

## Trace

1. Issue #850 REST: 5 aceites; pin morto; 400 none no root t1; 401 filho opaco; #793 não substitui reload-após-pin; one-shot à mão **não** é DoD.
2. Live r2: 1010897 `dsh_boot.sh` (PPID=1) foreground segura 1010906 `dsh web --patch …VIsbNa… --no-open --port 3080` desde 20:08:55; `ss` name `MainThread`; patch tmp ainda no disco; sidecar ausente; sibling ausente. 223762/TbJZ2F gone.
3. Pacote r2 alinha D1 predicado cmdline, D2 trap+R7, D3 `DSH_ISOLATE_SIDECAR`, D4 A8/A9+R8+R9 com o que P1-1/P1-2 pediam.
4. Origin `v1.1.9`; `v1.1.10` livre; AGENTS 14 linhas; overlay_doc § dsh sem bounce; `openspec validate --strict` valid.
5. Clone gate / HTML / Design Critique / outro caller / T0–T17: limpos. `live_route` parseia; `surface` ainda não.

---

## Disposition

Zero P0. Zero P1 aberto. P1-1 (A8/A9 + sidecar live: `DSH_ISOLATE_SIDECAR`, listen efémero, `_boot_tree` copia sibling, R9 não SIGTERM `:3080`) e P1-2 (trap mata `$DSH_PID`, confirma porta, **depois** `rm`; R7; MUST NOT `disown`) **fechados no texto r2**. R8 (listen→`--port`) e predicado cmdline `dsh`+`web` (R1/R5b) também pinados. Código ainda não existe (`dsh_isolate_reload.sh` missing; A8/A9 sem env; trap actual só `rm`) — isso é Apply, não BLOCKED de Design. One-shot 20:08 do boot antigo **não** substitui o aceite. UI none / Prototype N/A / T5 / pin `ls-remote` / overlay_doc vs AGENTS / #817/#839-não-reabrir estão fechados. P2 = `--check` disco≠ESM, sidecar/`tmp` 30d, one-shot≠helper, `surface` regex. P3 = proposal MAY, shorthand Apply contract, R6 leftover. Sem polish visual. MUST NOT editar `design.md` daqui. P2/P3 não bloqueiam T5 desta crítica.

### Verdict

**PASS**
