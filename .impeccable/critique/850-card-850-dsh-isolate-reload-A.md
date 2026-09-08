# Snapshot — Assessment A · card #850 `card-850-dsh-isolate-reload`

- Card: #850 — kaizen: pin do Guard dsh não recarrega o isolate vivo `:3080` (400 none no 1º turno; 401 do filho opaco)
- Change: `card-850-dsh-isolate-reload`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested agent)
- Modelo: inherit
- UTC: 2026-09-05T20:03:47Z
- Tuple (este isolado): prompt do pai `Status=Design` `bound_card=#850` worktree `card-850-dsh-isolate-reload`. Hook desta sessão: `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit/push. Não editar `design.md` / proposal / tasks / specs / HTML / `backend/` / `frontend/src/`.
- Board: Status observado **Design** (prompt). Issue OPEN `kaizen` + `priority:P0` + `type:operacao`. REST `GET /repos/oalansilva/crypto/issues/850` (não `gh issue view`). `comments: 0`.
- Digest `design.md` **medido**: sha256 `00e7079115770e90735fe527c06ddb9d60c92f8475b939eaff6fbee966140f1a` · **1966** palavras (`str.split`) · 14057 bytes · 104 linhas.
- `openspec validate card-850-dsh-isolate-reload --type change --strict`: **valid**
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correcto)
- UI impact: **none** (harness/ops dsh — sibling reload + sidecar + `--check` + goldens + pin; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*850*`; sem rewrite de `DESIGN.md`; sem pipeline Impeccable visual; Playwright desta coluna = N/A. Justificativa no `design.md` não vazia (aceite = bounce do isolate, sidecar SHA = pin, dump autenticado `:3080`). Este ficheiro é o snapshot git-tracked da crítica de processo (T7).
- Overlay live: `pin: v1.1.9`; `clients.dsh.auto: false`. Origin `oalansilva/covenant-flow` topo `v1.1.9`; `v1.1.10` **livre** neste instante (Design não crava; Apply confere).
- `live_route: N/A` / `surface: new` parseiam na forma do helper. Clone gate isento via `UI impact: none`.
- Method: issue #850 REST; proposal / design D1–D6 + Apply contract / Risks; tasks 1–7 (17 checkboxes); deltas `developer-tooling` + `process-harness` + `covenant-flow`; boot live `scripts/process-fsm/dsh_boot.sh`; occupant TCP `127.0.0.1:3080` (PID testemunha **223762**); fake `_fake_dsh_bin` em `test_dsh_adapter.py`; A7–A9 no mesmo ficheiro. MUST NOT vendorar `@deepseek-ai/dsh*`. Adversário = Apply TDD que verdeia R1–R6 no fake `argv0=dsh` e fail-closes no isolate live `node …/.bin/dsh web`.

---

## Surfaces lidas

| Superfície | Classificação |
| --- | --- |
| `openspec/changes/card-850-dsh-isolate-reload/{proposal,design,tasks}.md` | lido |
| `openspec/changes/card-850-dsh-isolate-reload/specs/{developer-tooling,process-harness,covenant-flow}/spec.md` | lido |
| Issue #850 body (REST) | lido |
| `scripts/process-fsm/dsh_boot.sh` + A7–A9 / `_fake_dsh_bin` | lido (o que o Design muda) |
| Isolate vivo `:3080` PID 223762 (`ss` + `/proc/pid/cmdline`) | lido (testemunha do pin morto; não prototipar) |
| `docs/crypto-overlay.md` secção dsh | lido (1–3 frases a acrescentar) |
| `frontend/src/**`, `backend/` de app, proto HTML 850 | **none** / ausente |
| GUI dsh `:3080` | **vendor** — homologação dump; não prototipar |

Nenhuma superfície de produto nova/alterada ficou sem classificação. Prototype N/A justificado.

---

## Brief (só neste snapshot)

Incidente live (`canonical_paths.dev`, modelo `muse-spark-1.3-contributor-free`, sessão `session-968db235`): overlay `pin: v1.1.9` e blobs `#817`/`#839` no git; isolate `dsh web --patch /tmp/covenant-flow-dsh-TbJZ2F.patch.yml` desde 2026-08-30 (PID 223762) **não** carregou o pin (ESM cacheia no arranque). Root turno 1 = 400 `reasoning.effort` `none`; filhos 401 CreditsError com settlement genérico. Não é furo novo no sanitizer.

Direction: (1) sibling `dsh_isolate_reload.sh` — SIGTERM do listener `dsh web` em `DSH_ISOLATE_LISTEN` (default `127.0.0.1:3080`), fail-closed se occupant não-dsh, no-op se porta livre; (2) `dsh_boot.sh` chama o sibling **antes** do `mktemp`, patch novo, `dsh web --patch` background só para TCP+sidecar, `wait`; (3) sidecar estável `/tmp/covenant-flow-dsh-isolate.json` com PID/epoch/SHA Guard+lib; (4) `--check` fail-closed PID+SHA vs disco; (5) dump `:3080` DoD humano **não** opcional; (6) pin = próximo patch livre após `v1.1.9`. Fora: cache-bust ESM; kill manual como DoD; unit #793; re-sanitizer; #817/#839/#837/#793/#846 como trabalho; Auto dsh; produto UI.

---

## Critique

### P0

(nenhum aberto)

O *como* (substituir o processo + sidecar `/tmp` + `--check` SHA + dump) é o canal certo para fechar pin morto. Cache-bust ESM, one-shot kill à mão, e systemd #793 como substituto estão rejeitados com alternativa nomeada. Bounce **substitui** o V8; `--check` não precisa de introspecção ESM se o PID do sidecar **é** o listener e o SHA foi gravado no arranque.

### P1

- **P1 — predicado «occupant = `dsh web`» não casa o isolate vivo; R1 no fake verdeia o seam errado.**  
  Testemunha live (`ss` `127.0.0.1:3080`, 2026-09-05T20:03Z): PID **223762**, `comm=MainThread`, `exe=…/cursor-agent/…/node`, cmdline `node /home/ubuntu/.npm/_npx/1e7f6d9597241db0/node_modules/.bin/dsh web --patch /tmp/covenant-flow-dsh-TbJZ2F.patch.yml --no-open --port 3080`. Pai ainda vivo: `bash …/dsh_boot.sh` PID **223735** (PPID 1).  
  Tasks 1.1 / spec developer-tooling: «se occupant for `dsh web`» / «if a `dsh web` process is listening». Não pinam *como* classificar. R1 = fake `_fake_dsh_bin` (`#!/usr/bin/env bash`, `argv0=dsh`, echo + `exit 0`) — `comm`/`argv0` **são** `dsh`. Apply TDD que testa `comm==dsh` ou `basename(argv0)==dsh` verdeia R1 e trata o PID 223762 como **não-dsh** → fail-closed → MUST NOT matar → **o pin morto que o card existe para substituir sobrevive**.  
  MUST no Design/spec/tasks: occupant do listen = processo cujo **cmdline** contém o token de path/`dsh` **e** o subcomando `web` (testemunha 223762), não `comm` nem `argv0==dsh`. Occupant sem esses tokens → fail-closed (stderr nomeia). Golden **nomeado** (R5b / R7): (a) listener `node …/dsh web --patch` → SIGTERM e porta livre; (b) listener `python -m http.server` (ou equivalente sem `dsh`+`web`) → exit ≠0, processo intacto. Sem (a), o *como* não fecha o pin morto no único isolate que Alan usa.

### P2

- **P2 — goldens vs isolate live `:3080`.** Default `DSH_ISOLATE_LISTEN=127.0.0.1:3080`. Contrato (task 3.1 / spec «Pytest does not kill») é explícito: efémero + fake. Helper **não** tem guarda `PYTEST_CURRENT_TEST` contra o default. Um R* que esqueça o env SIGTERM o PID 223762 no meio do pytest. Não é P1: o aceite está escrito; é footgun de Apply.

- **P2 — A8/A9 fake `exit 0` sem listen vs TCP wait.** `_fake_dsh_bin` actual imprime `DSH_CWD` e sai. Decision 2 / task 2.2 exigem esperar TCP fail-closed antes do sidecar. Sem fake que **bind** no endereço efémero, A8/A9 ou penduram/timeout ou Apply saltam o wait para os manter verdes. Task 3.3 pede regressão A7–A9; MUST pinar que o fake de R2/A8/A9 escuta em `DSH_ISOLATE_LISTEN` (não reutilizar o echo-only).

- **P2 — occupant não-dsh sem R\* próprio.** Spec tem cenário; task 3.2 cola a frase no fim de R3–R5. Apply pode shippar R1–R6 nomeados e omitir o assert «processo intacto». Menos grave que o P1 se o R7 node-wrapper existir; até lá é o mesmo buraco.

### P3

- **P3 — `--check` SHA disco ≠ heap ESM.** Risks D já o diz: bounce substitui o processo; sidecar grava SHA **no arranque**; sem bounce PID velho ou SHA ≠ disco → exit ≠0. Não é cache-bust. Dump `:3080` é o backstop humano. Aceite residual honesto — MUST NOT vender `--check` como leitura do V8.

- **P3 — sidecar não hasheia `impeccable-hook.js`.** Entra do issue é `.dsh/plugin/**`; aceite deste card é Guard+lib (400 none / Diagnostic). Hook-only pin morto passaria `--check`. Residual de fronteira, não o incidente.

- **P3 — trap EXIT só apaga tmp; SIGINT→filho não tem golden.** Decision 2: Ctrl-C/EXIT = fim do isolate; MUST NOT daemonizar. Task 2.2 pina `wait` + trap apaga patch, não o forward SIGINT/TERM ao child. Live já é boot-bash pai do node. Apply que `disown`/`setsid` daemoniza contra o MUST. Sem R de sinal.

- **P3 — overlay_doc MAY (proposal/spec) vs MUST (design Apply contract / task 5.2).** 1–3 frases não são o aceite do bounce. Apply segue a task.

- **P3 — dump 7.2(b) «se houver».** Herdado do issue. (a) primeiro turno root é sempre obrigatório; (b) Diagnostic só se o spawn falhar. Não torna o dump opcional (7.1+7.2 MUST NOT residual). 401 billing continua fora (não classificar como `dsh_reasoning_effort_none`).

---

## Cobertura do prompt (perguntas fechadas)

| Pergunta | Achado |
| --- | --- |
| Sibling SIGTERM + sidecar `/tmp` + `--check` SHA fecha o pin morto? | **Fecha se o predicado de occupant casar o node/npx live.** Arquitectura certa; P1 no match. SHA-at-start + PID=listener + dump fecham disco≠ESM sem cache-bust. |
| Reimplementar sanitizer escondido nas tasks? | **Não.** Task 1.3 / spec process-harness / D5 MUST NOT editar `sanitizeReasoningEffort` / `attachAgentEffortGuards` / `formatChildRunFailure`. Zero checkbox a tocá-los. |
| Dump `:3080` ainda opcional? | **Não.** Goals, Apply contract, spec «Human dump remains mandatory», tasks **7.1 e 7.2** «MUST NOT ser residual opcional nem Done só com golden». Recidiva #839 7.1 `[ ]` fechada no contrato. |
| Goldens a matarem o isolate live 3080? | Contrato **proíbe** (R1/R2 + spec). Footgun default 3080 = P2, não aceite. |
| Occupant não-dsh? | Fail-closed + stderr + MUST NOT roubar: D1 / task 1.1 / spec. P1 = o live dsh parece não-dsh se o matcher for `comm`. |
| SHA disco ≠ ESM? | Aceite residual P3: bounce substitui processo; `--check` não lê heap; dump backstop. |
| #793 / #846 reabertos? | **Não.** Non-Goals; task 4.1; spec covenant-flow. #793 MAY `ExecStart` noutro card; este **não** cria unit. #846 `rsync --delete` issue própria. |
| Prototype N/A justificado? | **Sim.** UI none; harness-only; sem HTML; aceite = bounce+sidecar+dump. |

Não entra (e não foi alargado): vendor runtime; Auto dsh; `process-fsm.yaml` / `guard.py` `decide()`; `backend/` / `frontend/src/`; 3080 em `environments.dev.services` / `./restart`; pagar billing OpenCode; reabrir #817/#839/#837; cache-bust ESM; kill manual como DoD.

---

## Disposition

- P0: (nenhum). Canal bounce+sidecar+`--check` é o *como* correcto.
- P1 occupant cmdline vs fake `argv0=dsh`: **aberto / must-fix**. Design/spec/tasks MUST pinar o match à testemunha 223762 (`node …/dsh web`) + golden nomeado desse seam. Sem isto o sibling fail-closes no pin morto.
- P2 default 3080 sob pytest / fake A8–A9 sem listen / occupant golden colado em 3.2: **aberto**, fechar no mesmo r2 que o P1 (não aceites residual enquanto o P1 viver).
- P3 SHA≠ESM, hook fora do sidecar, trap SIGINT, MAY vs MUST overlay_doc, dump «se houver»: **aceite residual**.
- Sanitizer reimplementado nas tasks: **fora**.
- Dump opcional: **fora**.
- #793/#846 reabertos: **fora**.
- Prototype N/A: **fora** (justificado).

Pai: **não** `submeter_design` enquanto o P1 estiver aberto (mesmo que B PASS). MUST NOT editar `design.md` daqui. MUST NOT `process_event`. Sem polish neste transcript.

---

## Verdict

**BLOCKED** — P1 aberto (predicado de occupant / seam do golden ≠ isolate vivo `node …/dsh web` PID 223762). Zero P0. Dump não opcional. Sanitizer não reentrado. #793/#846 não reabertos. Prototype N/A justificado.

Snapshot: `.impeccable/critique/850-card-850-dsh-isolate-reload-A.md`
