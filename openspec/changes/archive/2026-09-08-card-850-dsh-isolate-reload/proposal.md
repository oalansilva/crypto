## Why

A GUI `http://127.0.0.1:3080` que Alan usa **não é o pin homologado**. O isolate vivo `dsh web` arrancou 2026-08-30; os blobs `#817`/`#839` (pin `v1.1.9`) estão no git desde 2026-09-04/05 e o processo Node **não** os carregou (ESM cacheia no arranque). Testemunha `session-968db235`: root turno 1 = 400 `reasoning.effort` `none`; filhos 401 CreditsError com settlement genérico. Faltou a última milha (reload + dump `:3080`), não outro sanitizer. Card [#850](https://github.com/oalansilva/crypto/issues/850).

## What Changes

- Depois de pin/merge de `.dsh/plugin/**` ou `scripts/process-fsm/dsh_plugin_lib.js`, o `dsh web` que escuta `127.0.0.1:3080` **passa a correr esses blobs** (bounce do helper de boot; fail-closed se o isolate for mais velho que os blobs).
- Evidência de isolate: sidecar documentado com PID, start epoch, SHA256 dos blobs Guard+lib. Homologação/Pronto de card de Guard dsh exige isolate vivo com SHA = blobs do pin — não só git.
- Primeiro turno do root com modelo que recusa esforço desligado **não** envia `none` / campo ausente — porque o sanitizer do pin está no isolate, não só no disco.
- Falha de filho (`turn/end` `kind=error`, testemunhas 400 none **e** 401 CreditsError) sobe ao pai com `stopReason` + `Diagnostic:` — bounce faz valer o plugin `#839`; este card **não** reimplementa `sanitizeReasoningEffort` / `attachAgentEffortGuards`.
- Dump autenticado `:3080` desta classe (DoD humano, **não** opcional): um turno root que completa **e** um spawn isolado cujo erro (se houver) traz Diagnostic visível. Pytest **não** substitui.
- Pin produto = **próximo patch livre após origin check** (live overlay `pin: v1.1.9`). MUST NOT major. MUST NOT mover tag ocupada. `implantar --pin` no Cripto; overlay `pin` = essa tag; `clients.dsh.auto: false`. Residual #846 (`rsync --delete`) permanece issue própria.
- `overlay_doc` (`docs/crypto-overlay.md`) MAY ganhar 1–3 frases: após pin/merge de plugin/lib, bounce via o helper; 3080 ≠ systemd; 3080 ≠ `./restart` de produto. Sem T0–T17. `AGENTS.md` MUST NOT crescer.

**Não entra:** reabrir apply/SHA/PR de #817 / #839 / #837; vendorar `@deepseek-ai/dsh*` / `pi-ai`; Auto dsh; pôr `:3080` em `environments.dev.services` ou no `./restart` de produto; pagar/gerir billing OpenCode; recarregar o isolate à mão **uma vez** como DoD; #793 (unit systemd) como substituto; cache-bust ESM; editar `process-fsm.yaml` / `guard.py` `decide()`; produto `backend/` / `frontend/src/`.

## Capabilities

### New Capabilities

- (nenhuma) — o isolate `dsh web` e o Guard pinado já são pele do quarto adapter; este card fecha reload-após-pin + evidência SHA + homologação `:3080`, não um quinto cliente nem spec de produto.

### Modified Capabilities

- `developer-tooling`: `dsh_boot.sh` (e/ou helper irmão no mesmo dir, chamado pelo boot) **substitui** o isolate vivo em `127.0.0.1:3080` (SIGTERM o listener dsh, materializar patch novo, `dsh web --patch` de `canonical_paths.dev`); grava sidecar PID/epoch/SHA256 Guard+lib; status fail-closed se isolate ≠ blobs do pin. Goldens pytest do boot/reload. Sem cache-bust ESM. Sem unit systemd neste card.
- `process-harness`: homologação/Pronto de card de Guard dsh exige isolate vivo com SHA = blobs do pin (fail-closed), não só git. Bounce faz valer o sanitizer/`Diagnostic` já pinados; MUST NOT reimplementar esses helpers. Dump autenticado `:3080` permanece DoD humano (primeiro turno root sem 400 none; spawn isolado cuja falha, se houver, traz Diagnostic). `guard.py` `decide()` **não** ganha esta regra.
- `covenant-flow`: pin **próximo patch livre após `v1.1.9`** (Apply confere origin; Design não crava tag) copia o helper de bounce + goldens; `install.sh --pin` continua a copiar `.dsh/`; `SCHEMA_MAJOR` / `CLIENT_KEYS` inalterados; `clients.dsh.auto: false`. Sem reabrir #817 / #839 / #837 / #793 como trabalho. Sem linha nova no `AGENTS.md`. Residual #846 permanece issue própria.

## Impact

- Altera (Apply, após Pronto para Dev): produto `oalansilva/covenant-flow` — `scripts/process-fsm/dsh_boot.sh` e/ou helper irmão no mesmo dir, goldens pytest `scripts/process-fsm` do boot/reload, pin-tests para a tag que Apply cravar. Depois `implantar --pin` no Cripto. `docs/crypto-overlay.md` MAY 1–3 frases (3080 ≠ systemd; 3080 ≠ `./restart`; bounce após pin/merge de plugin/lib).
- Não toca `backend/` / `frontend/src/` de produto, `process-fsm.yaml`, `guard.py` `decide()`, `sanitizeReasoningEffort` / `attachAgentEffortGuards` / formatter Diagnostic (#839 permanece o código), `AGENTS.md` (substância/tamanho), perfil `~/.dsh/settings.yaml`, monorepo DeepSeek, Clara/Hermes, board/issue #817/#839/#837/#793/#846 como trabalho deste card.
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A. Clone gate isento (`surface: new` / `live_route: N/A`).
- Origem: issue #850. Homologação: dump autenticado `:3080` + sidecar SHA = pin; goldens pytest **não** substituem o dump; 3080 ≠ systemd; homologação ≠ `./restart`.
