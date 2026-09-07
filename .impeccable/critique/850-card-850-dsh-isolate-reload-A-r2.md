# Snapshot — Assessment A r2 · card #850 `card-850-dsh-isolate-reload`

- Card: #850 — kaizen: pin do Guard dsh não recarrega o isolate vivo `:3080` (400 none no 1º turno; 401 do filho opaco)
- Change: `card-850-dsh-isolate-reload`
- Critic: Assessment A recritique (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested agent)
- Modelo: inherit
- UTC: 2026-09-05T20:16:12Z
- Round: 2 — P1 r1 MUST confirmar fechados ou reabrir no **Apply contract** (Design não aplica código): (1) occupant = cmdline contém `dsh` **e** `web` (não `argv0`/`comm`); (2) A8/A9 + R* usam `DSH_ISOLATE_LISTEN` e `DSH_ISOLATE_SIDECAR` efémeros; R9 não SIGTERM `127.0.0.1:3080`; (3) trap INT/TERM/EXIT mata `$DSH_PID` depois `rm` patch; R7; (4) `DSH_ISOLATE_LISTEN` mapeia `--no-open --port`; R8; (5) R5b occupant não-dsh; overlay_doc MUST
- Tuple (este isolado): prompt do pai `Status=Design` `bound_card=#850` worktree `card-850-dsh-isolate-reload`. Hook desta sessão: `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit/push. Não editar `design.md` / proposal / tasks / specs / HTML / `backend/` / `frontend/src/`.
- Digest `design.md` **medido r2**: sha256 `766e1b3c7caa646251cd2aa578088db7adec67c7100faaa69823f6379d2dcdf2` · **2192** palavras (`str.split`) · 15989 bytes · 107 linhas. (r1 era `00e7079115…` / 1966 — o autor reescreveu D1–D4/D7 + Apply contract + tasks R5b/R7/R8/R9 + specs.)
- `openspec validate card-850-dsh-isolate-reload --type change --strict`: **valid**
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correcto)
- UI impact: **none** (harness/ops dsh — sibling reload + sidecar + `--check` + goldens + pin; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*850*`; sem rewrite de `DESIGN.md`; sem pipeline Impeccable visual; Playwright desta coluna = N/A. Justificativa no `design.md` não vazia. Este ficheiro é o snapshot git-tracked da crítica de processo (T7).
- `live_route: N/A` / `surface: new` parseiam na forma do helper. Clone gate isento via `UI impact: none`.
- Tasks: **17** checkboxes (mesmo teto r1; R5b/R7/R8/R9 enterrados em 3.1–3.3, não checkboxes extra).
- Overlay live (não recarregado nesta onda; facto do r1 + D7): `pin: v1.1.9`; `clients.dsh.auto: false`. Design não crava tag.
- Method: proposal / design D1–D7 + Apply contract / Risks / Open Questions; tasks 1–7; deltas `developer-tooling` + `process-harness` + `covenant-flow`. r1 snapshots lidos **só** para identificar os P1 (não copiar veredito): `.impeccable/critique/850-card-850-dsh-isolate-reload-A.md`. Live `:3080` (testemunha operacional, não prototipar): `ss` `127.0.0.1:3080` → `MainThread` pid **1010906** (r1 citava 223762; `comm` continua não-dsh).

---

## Surfaces lidas (r2)

| Superfície | Classificação |
| --- | --- |
| `openspec/changes/card-850-dsh-isolate-reload/{proposal,design,tasks}.md` | lido (r2) |
| `openspec/changes/card-850-dsh-isolate-reload/specs/{developer-tooling,process-harness,covenant-flow}/spec.md` | lido (r2) |
| r1 A snapshot (P1 a re-checar) | lido (identidade dos P1, não veredito) |
| Isolate vivo `:3080` (`ss` name `MainThread`) | lido (testemunha do predicado; não prototipar) |
| `frontend/src/**`, `backend/` de app, proto HTML 850 | **none** / ausente |
| GUI dsh `:3080` | **vendor** — homologação dump; não prototipar |

Nenhuma superfície de produto nova/alterada ficou sem classificação. Prototype N/A justificado.

---

## Re-check P1 r1 (obrigatório)

### P1-1 — occupant = cmdline contém `dsh` **e** `web` (não `argv0`/`comm`) — **FECHADO**

Contrato r2 (D1 P1-A; Apply contract (1); task **1.1**; spec developer-tooling «Occupant classification SHALL use `/proc/<pid>/cmdline`» + cenário «Node-wrapper cmdline» + MUST NOT `argv0=dsh` / `comm=dsh`; golden **R1**):

- Predicado **sse** cmdline contém token `dsh` **e** subcomando `web`.
- Testemunha nomeada: `node …/.bin/dsh web --patch … --no-open --port 3080`, `comm=MainThread`, `argv0` ≠ `dsh`.
- MUST NOT classificar por `comm`, `ss` name, `argv0==dsh` / `basename(argv0)==dsh`.
- R1 MUST NOT verde só com fake `argv0=dsh`. Matcher `comm`/`argv0` **reabre** o pin morto (Risks).

Live r2: listener ainda `MainThread` (pid 1010906). O *como* casa esse seam. Não reabrir.

### P1-2 — A8/A9 + R* usam `DSH_ISOLATE_LISTEN` e `DSH_ISOLATE_SIDECAR` efémeros; R9 não SIGTERM `127.0.0.1:3080` — **FECHADO**

Contrato r2 (D3 P1-B; D4; Apply contract (3); task **3.3**; spec cenário «Pytest A8 A9 and R-star do not kill the operator isolate on 3080»):

- **Todos** os goldens que invocam `dsh_boot.sh` (incl. A8/A9 **e** R*) MUST set ambos env efémeros.
- MUST NOT herdar default 3080 nem clobber `/tmp/covenant-flow-dsh-isolate.json`.
- Golden **R9**: A8/A9 **não** SIGTERM `127.0.0.1:3080`.
- `_boot_tree` copia o sibling; fake `dsh` bind no `--port`.

Não reabrir. Footgun `PYTEST_CURRENT_TEST` ausente no helper = P3 (contrato já obriga o env + R9).

### P1-3 — trap INT/TERM/EXIT mata `$DSH_PID` depois `rm` patch; R7 — **FECHADO**

Contrato r2 (D2 P1-C; Apply contract (2); task **2.2**; spec cenário «SIGINT on boot kills the listener then removes the tmp patch»; golden **R7**):

- Trap INT/TERM/EXIT MUST SIGTERM/SIGKILL `$DSH_PID`, confirmar porta livre, **depois** `rm` o tmp patch.
- MUST NOT `rm` com listener vivo. MUST NOT `disown`/`setsid`.
- R7: SIGINT no boot mata o fake listener, tmp some **depois**, sem órfão.
- Alternativa rejeitada: trap só `rm`.

Apply contract comprime «mata `$DSH_PID` **depois** `rm`»; D2/task/spec pinam a ordem kill → porta livre → `rm`. Não é inversão. Não reabrir.

### P1-4 — `DSH_ISOLATE_LISTEN` mapeia `--no-open --port`; R8 — **FECHADO**

Contrato r2 (D4 P1-D; Apply contract (2)+(3); task **2.1** / **3.1**; spec cenário «Listen address maps to dsh web --port»; golden **R8**):

- Parse `host:port`; kill, TCP wait e bind usam o **mesmo** port.
- Boot lança `dsh web --patch <novo> --no-open --port <port de DSH_ISOLATE_LISTEN>`.
- Fake MUST bind o `--port` recebido (não echo+`exit 0`).

Não reabrir.

### P1-5 — R5b occupant não-dsh; overlay_doc MUST — **FECHADO**

Contrato r2 (D1 R5b; D7; Apply contract (3)+(6); task **3.2** R5b; task **5.2** MUST; spec developer-tooling «Non-dsh occupant cmdline fails closed»; spec covenant-flow «overlay_doc MUST gain 1–3 sentences» + cenário «Overlay doc records bounce after pin»):

- R5b nomeado: cmdline **sem** o par → exit ≠0, processo intacto, stderr nomeia.
- overlay_doc **MUST** 1–3 frases (bounce após pin/merge; 3080 ≠ systemd; 3080 ≠ `./restart`). `AGENTS.md` MUST NOT crescer.

Proposal.md linha «overlay_doc MAY» **não** reabre: Apply lê Apply contract + tasks + spec (MUST). Residual P3 de wording no proposal. Não reabrir.

---

## Brief (só neste snapshot)

Incidente inalterado: overlay `pin: v1.1.9` e blobs `#817`/`#839` no git; isolate `dsh web` (ESM cacheia no arranque) não carregou o pin. Root turno 1 = 400 `reasoning.effort` `none`; filhos 401 CreditsError com settlement genérico. Não é furo novo no sanitizer.

Direction r2: (1) sibling `dsh_isolate_reload.sh` — predicado cmdline `dsh`+`web`; (2) boot chama sibling antes do `mktemp`, `dsh web --no-open --port`, trap mata `$DSH_PID` depois `rm`; (3) sidecar/listen efémeros nos goldens; R5b/R7/R8/R9; (4) `--check` fail-closed; (5) dump `:3080` DoD humano; (6) pin = próximo patch livre após `v1.1.9`; overlay_doc MUST. Fora: cache-bust ESM; kill manual como DoD; unit #793; re-sanitizer; #817/#839/#837/#793/#846 como trabalho; Auto dsh; produto UI.

Audience: operador do isolate dsh. Personas visuais Impeccable: **N/A**.

---

## Critique

### P0

(nenhum aberto)

Canal bounce+sidecar+`--check` continua o *como* correcto. Cache-bust ESM, one-shot kill, systemd #793 como substituto, matcher `comm`/`argv0` estão rejeitados com alternativa nomeada.

### P1

(nenhum aberto — P1-1…P1-5 r1 fechados no pacote OpenSpec r2 / Apply contract; sem P1 novo)

### P2

(nenhum aberto que reabra o veículo. Tightness de Apply abaixo = P3.)

### P3

- **Proposal `overlay_doc` MAY vs Apply contract/task 5.2/spec MUST.** Drift só no `proposal.md`. Apply segue MUST. Unificar o modal no Gist se republicar; não bloqueia.
- **Apply contract omite «confirmar porta livre» na linha do trap** (D2/task 2.2/spec têm). Compressão, não inversão.
- **Helper sem guarda `PYTEST_CURRENT_TEST` contra default 3080.** Contrato já obriga env efémero + R9. Footgun se Apply criar golden novo sem os dois env.
- **`--check` SHA disco ≠ heap ESM.** Risks: bounce substitui o processo; sidecar grava SHA no arranque; dump `:3080` é backstop. MUST NOT vender `--check` como leitura do V8.
- **Sidecar não hasheia `impeccable-hook.js`.** Aceite = Guard+lib. Residual de fronteira.
- **Dump 7.2 «se houver».** (a) primeiro turno root sempre obrigatório; (b) Diagnostic só se o spawn falhar. Não torna o dump opcional. 401 billing continua fora.
- **Sidecar `/tmp` × tmpfiles 30d / world-writable.** Reboot = fail-closed correcto. Isolate >30d pode falhar `--check` com processo saudável; Homologação humana continua o dump.
- **Substring `dsh`+`web` sem word-boundary.** Testemunha live casa; R5b cobre occupant sem o par. Apply tightness, não o predicado.

---

## Cobertura do prompt (perguntas fechadas)

| P1 pedido | Achado |
| --- | --- |
| occupant cmdline `dsh`+`web`, não argv0/comm | **FECHADO** Apply contract (1) + D1 + task 1.1 + spec + R1 |
| A8/A9 + R* listen+sidecar efémeros; R9 ¬SIGTERM `:3080` | **FECHADO** Apply contract (3) + D3/D4 + task 3.3 + spec |
| trap INT/TERM/EXIT mata `$DSH_PID` depois `rm`; R7 | **FECHADO** Apply contract (2) + D2 + task 2.2 + spec + R7 |
| `DSH_ISOLATE_LISTEN` → `--no-open --port`; R8 | **FECHADO** Apply contract (2)(3) + D4 + task 2.1/3.1 + spec + R8 |
| R5b occupant não-dsh; overlay_doc MUST | **FECHADO** Apply contract (3)(6) + D1/D7 + tasks 3.2/5.2 + specs; proposal MAY = P3 |

Não entra (e não foi alargado): vendor runtime; Auto dsh; `process-fsm.yaml` / `guard.py` `decide()`; `backend/` / `frontend/src/`; 3080 em `environments.dev.services` / `./restart`; pagar billing OpenCode; reabrir #817/#839/#837/#793/#846; cache-bust ESM; kill manual como DoD; sanitizer reimplementado.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. Browser gate: **N/A (no UI)**.
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica. Este crítico MUST NOT editar `design.md`.
- FSM yaml: sem task de estado/evento. T1/T7 Alan; T5 parent. Dual-write T0–T17 **proibido** no pacote.
- Product UI: zero `frontend/src/` / `backend/` de app no Apply contract.
- Auto dsh: overlay live `false`; specs MUST NOT reivindicar; pin não injeta a chave.
- `CLIENT_KEYS` / `SCHEMA_MAJOR` inalterados.
- Vendor `@deepseek-ai/dsh*` / `pi-ai`: proibido.
- Dump `:3080` / `--check` live: MUST NOT residual opcional (7.1+7.2).
- Design **não** aplica código (pré-Apply). Goldens A8/A9 live ainda sem env — esperado até Pronto para Dev.

---

## Trace

1. r1 A BLOCKED: predicado occupant / seam do golden ≠ isolate vivo `node …/dsh web`.
2. r2 design D1–D4/D7 + Apply contract (1)–(6) + tasks 1.1/2.1–2.2/3.1–3.3/5.2 + specs developer-tooling/covenant-flow — fecham os cinco P1.
3. Digest `design.md` mudou `00e70791…`/1966 → `766e1b3c…`/2192. `openspec validate --strict` valid. Sem `## Design Critique`.
4. Proposal MAY overlay_doc residual. Live `:3080` ainda `MainThread` (pid 1010906).
5. Clone gate / HTML / sanitizer / #793/#846: limpos neste digest.

---

## Disposition

- P0: (nenhum).
- P1 r1-1…r1-5: **fechados** no Apply contract + D1–D4/D7 + tasks + specs. Não reabrir.
- P1 novo: (nenhum).
- P2: (nenhum aberto).
- P3: proposal MAY vs MUST; compressão do trap no Apply contract; footgun pytest sem `PYTEST_CURRENT_TEST`; SHA≠ESM; hook fora do sidecar; dump 7.2 «se houver»; `/tmp` 30d. **accepted-residual**.
- Sanitizer reimplementado nas tasks: **fora**.
- Dump opcional: **fora**.
- #793/#846 reabertos: **fora**.
- Prototype N/A: **fora** (justificado).

Pai: P0/P1 desta crítica = zero. MUST NOT editar `design.md` daqui. MUST NOT `process_event`. Sem polish neste transcript. Design não aplica código.

---

## Verdict

**PASS** (zero P0/P1 abertos; P1 r1-1…r1-5 fechados no Apply contract; P3 accepted-residual; Prototype N/A justificado; UI impact none classificado; crítica isolada Assessment A r2; snapshot não vazio; digest `design.md` `766e1b3c7c…` / 2192)

## Snapshot

`.impeccable/critique/850-card-850-dsh-isolate-reload-A-r2.md`
