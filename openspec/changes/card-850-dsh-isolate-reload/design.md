## Context

Card [#850](https://github.com/oalansilva/crypto/issues/850). Status observado: **Design**. Bound `q_git=card-850-dsh-isolate-reload`. Relacionados e **não** reabertos como trabalho: #817 / #839 (Pronto; sanitizer + attach `agentCtx` + Diagnostic para `turn/end` `kind=error`), #837 (Design, bloqueado nesta sessão), #793 (Em Refinamento; unit systemd no boot da VM), #846 (`rsync --delete`, residual próprio).

Overlay Cripto `.covenant-flow/overlay.yaml`: `pin: v1.1.9`, `clients.dsh.auto: false`. Blobs `#817`/`#839` no git desde 2026-09-04/05. Isolate vivo: `dsh_boot.sh` + `dsh web --patch /tmp/covenant-flow-dsh-TbJZ2F.patch.yml` desde **2026-08-30 08:12** (PID testemunha 223762). Plugin no disco `2026-09-05 12:09`. ESM do isolate cacheia o plugin no arranque; mtime novo no disco **não** actualiza o processo. `dsh_boot.sh` actual materializa patch e lança `dsh web --patch` **sem** substituir o listener já em `127.0.0.1:3080` — um segundo boot deixa o isolate velho a servir (bind falha ou o processo de 30/08 continua).

Factos (sessão `session-968db235-36c5-4d0b-a9a4-ac0355aaa46c`, 2026-09-05):

- Root cwd `canonical_paths.dev`, preset `standard`, provider `opencodealan`, modelo `muse-spark-1.3-contributor-free`.
- Turno 1: `request/header` **sem** `reasoningEffort` → `turn/end` 400 `"reasoning.effort" does not support "none"`.
- Turno 2: config com `reasoningEffort: "high"` → completed.
- Filhos `49a8a428` / `290c1837`: `turn/end` **401** `CreditsError` / `Insufficient balance`; pai viu settlement genérico (`Background subagent … failed` / `It left no closing message.`) **sem** `Diagnostic:`.
- Causa: pin morto (isolate ≠ blobs). Não é furo novo no sanitizer. `#839` já formata Diagnostic para **qualquer** `turn/end` `kind=error` (incl. 401). Bounce faz isso valer.

**UI impact: none.** Harness/ops dsh. Nenhuma rota, shell, componente ou copy de produto.

## Goals / Non-Goals

**Goals:**

- Depois de pin/merge de `.dsh/plugin/**` ou `dsh_plugin_lib.js`, o isolate em `127.0.0.1:3080` corre esses blobs (bounce do helper; não basta o ficheiro no disco).
- Sidecar documentado com PID, start epoch, SHA256 Guard+lib. Homologação/Pronto de card de Guard dsh exige isolate vivo com SHA = blobs do pin (fail-closed).
- Primeiro turno root em modelo que recusa esforço desligado **não** envia `none` / campo ausente — porque o sanitizer pinado está no processo, não só no git.
- Falha de filho (`kind=error`) chega ao pai com `stopReason` + `Diagnostic:` via o plugin `#839` já pinado, após bounce. Este card **não** reimplementa esse plugin.
- Dump autenticado `:3080` (DoD humano, checkbox **não** opcional): turno root que completa **e** spawn isolado cuja falha, se houver, traz Diagnostic. Pytest **não** substitui.
- Pin produto = próximo patch livre após origin check (live overlay `v1.1.9`). `clients.dsh.auto: false`.

**Non-Goals:**

- Reabrir #817 / #839 / #837 / #793 / #846 como trabalho. Vendorar `@deepseek-ai/dsh*` / `pi-ai`. Auto dsh. Trocar o modelo. Pagar/gerir billing OpenCode.
- Cache-bust ESM. Recarregar o isolate à mão **uma vez** como DoD. Unit systemd (#793) como substituto — a unit MAY `ExecStart` este helper depois; este card **não** cria unit.
- `process-fsm.yaml` / `guard.py` `decide()`. `AGENTS.md` a crescer. Dual-write T0–T17. Porta 3080 em `environments.dev.services` ou `./restart` de produto. `backend/` / `frontend/src/`. HTML de protótipo.

## Decisions

1. **Canal = pele `covenant-flow`: sibling `dsh_isolate_reload.sh` chamado por `dsh_boot.sh`.**  
   O boot actual só materializa patch e lança `dsh web --patch`; **não** substitui o listener. Apply MUST: helper irmão `scripts/process-fsm/dsh_isolate_reload.sh` (mesmo dir), invocado por `dsh_boot.sh` **antes** de materializar o patch novo. Predicado de occupant (P1-A, testemunha PID 223762): o PID à escuta em `DSH_ISOLATE_LISTEN` é dsh **sse** o **cmdline** (`/proc/<pid>/cmdline`) contém o token `dsh` **e** o subcomando `web`. Live: `node …/.bin/dsh web --patch … --no-open --port 3080`, `comm=MainThread`, `argv0` ≠ `dsh`. MUST NOT classificar por `comm`, por `ss` name, nem por `argv0==dsh` / `basename(argv0)==dsh`. Occupant **não**-dsh = cmdline **sem** esse par → fail-closed (exit ≠0, stderr nomeia, MUST NOT matar). Porta livre → no-op de kill (cold start). Se o par casar: SIGTERM, espera, SIGKILL se ainda escutar, confirma porta livre. Depois o boot materializa **novo** tmp patch (`mktemp`, nunca reutilizar `/tmp/covenant-flow-dsh-TbJZ2F.patch.yml` de 30/08), `cd "$LAUNCH_DIR"` (`canonical_paths.dev` como hoje; A7–A9 intactos **com** overrides de teste, D3/D4). `dsh plugin add` continua **não** ser o canal. Golden **R1** MUST usar um listener `node …/dsh web --patch` (cmdline com o par); MUST NOT verde só com fake `argv0=dsh`. Golden **R5b** = occupant sem o par. Alternativa rejeitada: **cache-bust ESM**. Alternativa rejeitada: **one-shot kill à mão como DoD**. Alternativa rejeitada: **systemd #793 como substituto**. Alternativa rejeitada: matcher `comm`/`argv0` (fail-closes no pin morto live).

2. **Arranque: `&` + `wait`, trap INT/TERM/EXIT mata o listener e só então `rm` o patch (P1-C).**  
   Hoje o isolate **é** o último comando foreground de `dsh_boot.sh` (bash 223735 espera node 223762; trap EXIT **não** corre). Para gravar PID real o boot MUST lançar `dsh web` em background, esperar TCP no endereço de `DSH_ISOLATE_LISTEN` (timeout fail-closed), gravar o sidecar, e `wait` o PID. Trap INT/TERM/EXIT MUST: SIGTERM/SIGKILL `$DSH_PID` (e o listener se ainda escutar), **confirmar porta livre**, **depois** `rm` o tmp patch. MUST NOT `rm` o patch enquanto o listener viver. MUST NOT `disown`/`setsid`. Ctrl-C / EXIT = fim do isolate (não órfão PPID=1). Golden **R7**: SIGINT no boot mata o fake listener e **não** deixa órfão; o tmp patch some **depois** do kill. Alternativa rejeitada: trap só `rm` (contradiz holding; apaga `--patch` com Node ainda up).

3. **Sidecar: default live `/tmp/covenant-flow-dsh-isolate.json`; goldens MUST `DSH_ISOLATE_SIDECAR` (P1-B).**  
   Campos: `pid`, `start_epoch`, `listen`, `guard_sha256`, `lib_sha256` (SHA-256 hex de `REPO_ROOT/.dsh/plugin/process-fsm-guard.js` e `REPO_ROOT/scripts/process-fsm/dsh_plugin_lib.js` **no disco no bounce**), `launch_dir`, `patch`. Path: `DSH_ISOLATE_SIDECAR` se set; senão `/tmp/covenant-flow-dsh-isolate.json` — este default é **só** live/homologação. Pytest (R* **e** regressão A8/A9) MUST set `DSH_ISOLATE_SIDECAR` para um path efémero (MUST NOT clobber o sidecar de Homologação). MUST NOT viver em `.dsh/`. MUST NOT ir para o git. Alternativa rejeitada: path fixo `/tmp/…` nos goldens (overwrite da evidência humana). Alternativa rejeitada: ficheiro no worktree.

4. **`DSH_ISOLATE_LISTEN` mapeia para `--port` / bind (P1-D). Goldens A8/A9 isolados do live `:3080` (P1-B).**  
   Parse `host:port` de `DSH_ISOLATE_LISTEN` (default `127.0.0.1:3080`). O sibling kill/wait TCP **e** o `dsh web` MUST usar o **mesmo** port: boot passa `--no-open --port <port>` (live testemunha 223762). Goldens: fake `dsh` MUST bind o `--port` recebido (não echo+`exit 0` num porto diferente). `_boot_tree` MUST copiar o sibling. **Todos** os goldens que invocam `dsh_boot.sh` (incl. A8/A9) MUST set `DSH_ISOLATE_LISTEN` efémero **e** `DSH_ISOLATE_SIDECAR` efémero. Golden **R8**: invocação de `dsh web` inclui `--no-open --port <port>` igual ao port de `DSH_ISOLATE_LISTEN`. Golden **R9**: A8/A9 **não** SIGTERM `127.0.0.1:3080`. A7 (não-dir) continua a falhar **antes** do sibling/kill. Alternativa rejeitada: sibling lê 3080 e `dsh web` bind noutro porto.

5. **`--check` fail-closed no mesmo sibling (entrada de Homologação/Pronto de Guard dsh).**  
   `dsh_isolate_reload.sh --check` exit 0 **só** se: há listener em `DSH_ISOLATE_LISTEN` (live default `127.0.0.1:3080`), o sidecar em `DSH_ISOLATE_SIDECAR` (live default `/tmp/covenant-flow-dsh-isolate.json`) existe, `pid` do sidecar **é** o listener, e `guard_sha256`/`lib_sha256` **igualam** os blobs actuais no disco do pin. Qualquer desvio (sidecar ausente, PID morto, SHA ≠ disco = pin morto, porta vazia) → exit ≠0. Homologação/Pronto de card de Guard dsh MUST exigir este check PASS **além** do git/pin (path default live, sem env de teste). Este card NÃO altera o plugin; o check prova que o isolate **carregou** o pin. Alternativa rejeitada: confiar só em mtime do plugin. Alternativa rejeitada: pytest como substituto do dump `:3080`.

6. **MUST NOT reimplementar `sanitizeReasoningEffort` / `attachAgentEffortGuards` / formatter Diagnostic.**  
   O plugin `#839` já sanitiza no `agent.ctx` e formata Diagnostic para **qualquer** `turn/end` `kind=error` (incl. 401 CreditsError). Tasks deste card MUST NOT editar esses helpers como aceite. Bounce + `--check` SHA é o aceite de «o isolate corre o pin». Dump humano prova o 400 none no root turno 1 e o Diagnostic no filho. Alternativa rejeitada: **reimplementar o sanitizer** — residual é isolate/homologação, não outro attach. `_Avoid:` tratar 401 como 400 de esforço.

7. **Pin = próximo patch livre após `v1.1.9`; overlay_doc 1–3 frases MUST; #846 fora.**  
   Origin conferido neste Design: overlay live `pin: v1.1.9`. Apply MUST `git ls-remote --tags` de novo e cravar o próximo patch livre (esperado `v1.1.10` se ainda livre; MUST NOT major; MUST NOT mover `v1.1.9`). Produto primeiro (helper + goldens R*), depois `implantar --pin` no Cripto; overlay `pin` = essa tag; `clients.dsh.auto: false`. `SCHEMA_MAJOR` 1. `CLIENT_KEYS` inalterados. `docs/crypto-overlay.md` (secção dsh) MUST ganhar 1–3 frases: após pin/merge de `.dsh/plugin` ou `dsh_plugin_lib`, bounce via `dsh_boot.sh`; 3080 ≠ systemd; 3080 ≠ `./restart` de produto. `AGENTS.md` MUST NOT crescer. Residual #846 permanece issue própria. Alternativa rejeitada: cravar `v1.1.10` neste Design sem o check do Apply. Alternativa rejeitada: só patch no consumidor sem produto.

## Apply contract

- Ordem, só após `Status=Pronto para Dev` no **mesmo** chat `#850`, filho Apply (pai `iniciar_apply` antes do spawn). Zero produto UI. Design **não** aplica.
- (1) `dsh_isolate_reload.sh`: occupant = cmdline contém `dsh` **e** `web` (não `comm`/`argv0`); stop em `DSH_ISOLATE_LISTEN` (default `127.0.0.1:3080`); fail-closed se sem o par; `--check` lê `DSH_ISOLATE_SIDECAR` (default live `/tmp/covenant-flow-dsh-isolate.json`); (2) `dsh_boot.sh` chama o sibling **antes** do `mktemp`, lança `dsh web --patch <novo> --no-open --port <port de DSH_ISOLATE_LISTEN>`, espera TCP **nesse** port, grava sidecar, `wait`; trap INT/TERM/EXIT mata `$DSH_PID` **depois** `rm` o tmp patch; (3) goldens R1 (node `…/dsh web`, não `argv0=dsh`), R2, R3, R4, R5, **R5b**, R6, **R7** (SIGINT), **R8** (`--port`), **R9** (A8/A9 não SIGTERM `:3080`); A7–A9 + R* MUST `DSH_ISOLATE_LISTEN` **e** `DSH_ISOLATE_SIDECAR` efémeros; `_boot_tree` copia o sibling; fake `dsh` bind no `--port`; (4) origin + tag = próximo patch após `v1.1.9`; (5) `implantar --pin`; (6) overlay_doc **MUST** 1–3 frases.
- MUST NOT editar `sanitizeReasoningEffort` / `attachAgentEffortGuards` / `formatChildRunFailure` como aceite. MUST NOT `import` `@deepseek-ai/dsh*`. MUST NOT editar `guard.py`, `process-fsm.yaml`, `AGENTS.md`, `backend/`, `frontend/src/`, `~/.dsh/settings.yaml`. MUST NOT vendorar DeepSeek. MUST NOT criar unit systemd. MUST NOT ligar `:3080` em `environments.dev.services`. MUST NOT reabrir #817/#839/#837/#793/#846 como trabalho.
- Homologação (DoD humano, **não** substitui R1–R9; **não** opcional; sidecar **default** live, sem env de teste): `--check` PASS (SHA isolate = blobs do pin) **e** dump autenticado da GUI `http://127.0.0.1:3080`: (a) **primeiro** turno duma sessão nova no mesmo tipo de modelo (testemunha `muse-spark-*`) completa **sem** `INVALID_REQUEST` desta classe; (b) um spawn isolado cuja falha, se houver, traz `stopReason` + `Diagnostic:` (não só settlement genérico). Pytest **não** substitui este dump. Homologação ≠ `./restart`; 3080 ≠ systemd; cwd = `canonical_paths.dev`.

## Risks / Trade-offs

- [SIGTERM mata sessão GUI a meio do turno] → aceite: pin morto é pior; bounce é explícito após pin/merge. overlay_doc avisa. Sem `--force` silencioso noutro porto.
- [Occupant live `comm=MainThread` / `argv0=node`] → predicado cmdline `dsh`+`web` (R1); occupant sem o par = R5b fail-closed. Matcher `comm`/`argv0` **reabre** o pin morto.
- [A8/A9 + sidecar canónico a tocar `:3080`] → **todo** golden que corre `dsh_boot.sh` seta `DSH_ISOLATE_LISTEN` **e** `DSH_ISOLATE_SIDECAR` efémeros; R9 prova que A8/A9 **não** SIGTERM `127.0.0.1:3080`.
- [`&`+`wait` + trap só `rm`] → trap INT/TERM/EXIT mata `$DSH_PID` **depois** `rm` o patch (R7). MUST NOT `disown`.
- [Wait TCP e kill em portas diferentes] → `DSH_ISOLATE_LISTEN` → `--no-open --port` no `dsh web`; fake bind nesse port (R8).
- [`--check` SHA no disco ≠ SHA carregado no ESM] → o bounce **substitui o processo**; o sidecar grava SHA **no momento do arranque**. Sem bounce, `--check` falha (PID velho ou SHA disco ≠ sidecar). Não é cache-bust.
- [401 CreditsError continua se o saldo OpenCode estiver vazio] → fora deste card (não entra: pagar billing). Aceite = Diagnostic visível, não saldo.
- [Homologação `:3080` ≠ worktree] → cwd canónico DEV; dump é Apply/homologação. R* verdes não dispensam o dump nem o `--check` live.
- [#793 ExecStart deste helper] → MUST permanecer idempotente (SIGTERM + start). Este card não cria a unit.
- [P2 rebase no tip `v1.1.9`] → não reverter haystacks #817/#839. Apply rebase. Não é trabalho desses cards.

## Migration Plan

Aditivo sobre `v1.1.9`. Ordem Apply: (1) sibling predicado cmdline + `--check` + R1/R5b/R4/R5; (2) boot `--port` + trap INT/TERM/EXIT + R7/R8; (3) sidecar env + R2/R3/R9 + A7–A9 com ambos overrides; (4) origin tags + rebase + tag próxima livre; (5) pin Cripto + overlay_doc MUST 1–3 frases. Rollback = pin `v1.1.9`. Sem migration de banco. Sem rebuild frontend. Homologação = `--check` default live + dump `:3080`, não `./restart`.

## Open Questions

Nenhuma bloqueante. P1-A/B/C/D fechados neste r2 (predicado cmdline; sidecar/listen efémeros incl. A8/A9; trap mata PID depois `rm`; listen→`--port`). Residuais P3 (não reabrir como P1): SHA disco ≠ heap ESM (bounce substitui processo); `impeccable-hook.js` fora do SHA; dump 7.2 «se houver»; billing OpenCode; #793 unit; #846 `rsync --delete`.

## UI impact

UI impact: none — harness/ops dsh. Zero rota, shell, componente ou copy de produto CriptoFarol. Nenhuma superfície visual nova ou alterada.

## live_route

live_route: N/A — harness-only; no product route. Clone gate isento (sem HTML, sem catálogo). Não há página viva autenticada nem `landing` a clonar.

## surface

surface: new — isento de catálogo/`copied`. Não há tela Cripto; o aceite é bounce do isolate `:3080`, sidecar SHA e dump autenticado.

## Prototype

N/A — `UI impact: none`. Não há tela Cripto a prototipar; o aceite é o helper a substituir o isolate, o sidecar SHA = pin, o primeiro turno root sem 400 `none`, e o Diagnostic no spawn isolado. Sem HTML. Sem `frontend/public/prototypes`. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A (não há UI de produto a exercitar). Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL de produto, viewport nem assert de UI. A evidência de aceite é o dump dsh `:3080` mais `--check` live e os goldens R1–R9 (regressão A7–A9 isolada), não um protótipo HTML.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. Detector Impeccable da pele dsh permanece o de #782/#822; este card não o altera.

## Design Critique

- P0: nenhum
- P1 r1 (fechados no r2): predicado occupant cmdline `dsh`+`web` (não argv0/`MainThread`); A8/A9+sidecar com `DSH_ISOLATE_LISTEN`/`DSH_ISOLATE_SIDECAR` efémeros + R9 ¬SIGTERM `:3080`; trap INT/TERM/EXIT mata `$DSH_PID` depois `rm` (R7); listen → `--no-open --port` (R8); R5b não-dsh; overlay_doc MUST
- P2 (aceites): `--check` proxy disco+PID ≠ heap ESM (bounce substitui o processo; dump backstop); sidecar `/tmp` × reboot/tmpfiles 30d; bounce one-shot do boot antigo ≠ aceite
- P3 (aceites): `proposal.md` overlay_doc MAY vs tasks/spec MUST; hook.js fora do SHA; dump 7.2 «se houver»; billing OpenCode; #793/#846
- Prototype: N/A — `UI impact: none` (bounce isolate `:3080` + sidecar SHA + dump; sem HTML)
- Snapshot: `.impeccable/critique/850-card-850-dsh-isolate-reload-A-r2.md` e `.impeccable/critique/850-card-850-dsh-isolate-reload-B-r2.md` (r1 BLOCKED; r2 PASS)
- Design Agent verdict: PASS
