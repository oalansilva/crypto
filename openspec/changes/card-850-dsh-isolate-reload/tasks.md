## 1. Sibling: stop isolate + --check sidecar

- [x] 1.1 Criar `scripts/process-fsm/dsh_isolate_reload.sh` (irmão de `dsh_boot.sh`): `DSH_ISOLATE_LISTEN` default `127.0.0.1:3080`. Occupant dsh **sse** `/proc/<pid>/cmdline` contém `dsh` **e** `web` (testemunha live: `node …/.bin/dsh web --patch … --no-open --port 3080`, `comm=MainThread`). MUST NOT classificar por `comm`, `ss` name, nem `argv0==dsh`. Par casa → SIGTERM, espera, SIGKILL se ainda escutar, porta livre. Porta livre → no-op. Cmdline **sem** o par → exit ≠0, stderr nomeia, MUST NOT matar. MUST NOT cache-bust ESM
- [x] 1.2 Mesmo helper `--check`: path sidecar = `DSH_ISOLATE_SIDECAR` se set, senão `/tmp/covenant-flow-dsh-isolate.json` (default **só** live/homologação). Exit 0 só se listener em `DSH_ISOLATE_LISTEN` existe, sidecar existe, `pid` do sidecar **é** o listener, e `guard_sha256`/`lib_sha256` igualam os blobs no disco. Sidecar ausente, PID morto ou SHA mismatch → exit ≠0
- [x] 1.3 **Não** editar `sanitizeReasoningEffort` / `attachAgentEffortGuards` / `formatChildRunFailure` como aceite; **não** editar `guard.py`, `dsh_stubs.py`, `process-fsm.yaml`, `AGENTS.md`, `backend/` nem `frontend/src/`; não vendorar runtime; não criar unit systemd; não ligar `:3080` em `environments.dev.services`

## 2. Boot: bounce + --port + trap + sidecar

- [x] 2.1 `dsh_boot.sh` chama o sibling **antes** do `mktemp`. Materializa **novo** tmp patch. Parse `host:port` de `DSH_ISOLATE_LISTEN` e lança `dsh web --patch <tmp> --no-open --port <port>` (mesmo port do kill/wait TCP). `LAUNCH_DIR` / A7 intacto (não-dir falha **antes** do sibling)
- [x] 2.2 Background + espera TCP no listen + grava sidecar (`DSH_ISOLATE_SIDECAR` ou default live) + `wait`. Trap INT/TERM/EXIT MUST SIGTERM/SIGKILL `$DSH_PID`, confirmar porta livre, **depois** `rm` o tmp patch. MUST NOT `rm` com listener vivo. MUST NOT `disown`/`setsid`. `dsh plugin add` fora do canal
- [x] 2.3 Sidecar MUST NOT viver em `.dsh/` nem no git. Default `/tmp/covenant-flow-dsh-isolate.json` só no bounce do operador / Homologação

## 3. Goldens pytest `scripts/process-fsm`

- [x] 3.1 **R1:** listener cujo cmdline é `node …/dsh web --patch` (par `dsh`+`web`; MUST NOT verde só com fake `argv0=dsh`) na porta de teste → SIGTERM e novo `dsh web --patch` com tmp **diferente**. MUST NOT cache-bust ESM. **R2:** porta livre → cold start. **R8:** fake/`dsh web` recebe `--no-open --port` igual ao port de `DSH_ISOLATE_LISTEN` e bind nesse port
- [x] 3.2 **R3:** sidecar em `DSH_ISOLATE_SIDECAR` (não o default `/tmp`) contém `pid`, `start_epoch`, SHA Guard+lib. **R4:** `--check` exit ≠0 se SHA ≠ disco. **R5:** `--check` exit ≠0 se sidecar ausente. **R5b:** occupant cmdline **sem** o par `dsh`+`web` → exit ≠0 e processo intacto
- [x] 3.3 **R6 / A7–A9:** `_boot_tree` copia o sibling. A8/A9 MUST set `DSH_ISOLATE_LISTEN` **efémero** e `DSH_ISOLATE_SIDECAR` efémero (MUST NOT herdar default 3080 nem clobber `/tmp/covenant-flow-dsh-isolate.json`). **R7:** SIGINT no boot mata o fake listener, tmp patch some **depois**, sem órfão. **R9:** A8/A9 **não** SIGTERM `127.0.0.1:3080`. E1–E12 / F1–F8 / G1 / write deny #784 passam. Pin-test = tag que Apply cravar (não hardcode `v1.1.10` no vácuo). `pytest scripts/process-fsm` sem GitHub. Stubs `.dsh/skills/` ≤8; `.dsh/` sem T0–T17; `AGENTS.md` inalterado

## 4. Produto covenant-flow (próximo patch após v1.1.9)

- [x] 4.1 Commit no repo `oalansilva/covenant-flow` (sibling + boot + goldens R1–R9 / R5b) após rebase no tip. Tag = próximo patch livre (`git ls-remote --tags`; overlay live `v1.1.9` ocupado; esperado `v1.1.10` se livre; não major; não mover `v1.1.9`; não vendorar DeepSeek). MUST NOT reverter haystacks #817/#839; MUST NOT reabrir #817/#839/#837/#793/#846 como trabalho
- [x] 4.2 `install.sh --pin` continua a copiar `.dsh/` sempre; `CLIENT_KEYS` três; `SCHEMA_MAJOR` 1; sem Auto dsh

## 5. Pin Cripto + overlay_doc

- [x] 5.1 `implantar --pin` da tag de 4.1 no worktree Cripto; overlay `pin:` = essa tag; `clients.dsh.auto: false` permanece
- [x] 5.2 `docs/crypto-overlay.md` secção dsh **MUST** ganhar 1–3 frases — após pin/merge de `.dsh/plugin` ou `dsh_plugin_lib`, bounce via `dsh_boot.sh`; 3080 ≠ systemd; 3080 ≠ `./restart` de produto. `AGENTS.md` MUST NOT crescer. Não ligar porta 3080 em `environments.dev.services`; não systemd neste card; não dual-write T0–T17; não editar `backend/` / `frontend/src/`

## 6. Verificação

- [x] 6.1 `openspec validate card-850-dsh-isolate-reload --type change --strict` verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)
- [x] 6.2 Stubs `.dsh/skills/` ≤8 linhas; `.dsh/` sem T0–T17; `AGENTS.md` ≤40; sem Auto dsh; `.cursor/hooks.json` matcher Write inalterado

## 7. Homologação humana (Design especifica; Apply/homologação executa; **não** opcional)

- [x] 7.1 `dsh_isolate_reload.sh --check` PASS no isolate vivo `127.0.0.1:3080` com sidecar **default** `/tmp/covenant-flow-dsh-isolate.json` (sem env de teste; SHA = blobs do pin). Pytest R1–R9 **não** substitui este check
- [ ] 7.2 Dump autenticado da GUI dsh web `http://127.0.0.1:3080` (plugin pinado, cwd = `canonical_paths.dev`): (a) **primeiro** turno duma sessão nova no mesmo tipo de modelo que recusa esforço desligado (testemunha `muse-spark-*`) completa **sem** `INVALID_REQUEST` desta classe; (b) um spawn isolado cuja falha, se houver (`turn/end` `kind=error`, testemunhas 400 none **e** 401 CreditsError), traz `stopReason` + `Diagnostic:` — não só `failed before it finished` / `no closing message`. Pytest **não** substitui este dump. Homologação ≠ `./restart` de produto; 3080 ≠ systemd. Estes checkboxes são o DoD humano — MUST NOT ser residual opcional nem Done só com golden
