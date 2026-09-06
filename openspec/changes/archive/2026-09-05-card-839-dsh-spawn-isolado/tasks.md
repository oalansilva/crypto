## 1. Lib: attach no agentCtx + facts + Diagnostic

- [x] 1.1 Em `scripts/process-fsm/dsh_plugin_lib.js`, exportar `attachAgentEffortGuards(agentCtx)`: `agent/request` = `sanitizeReasoningEffort(await next())` com `{ prepend: true }`; `agent/request-error` **também** `{ prepend: true }` = 1 retry desta classe no mesmo agente (header filho vs root inalterado). MUST NOT lançar (try/catch: `agent/created` sync throw veta o filho). MUST NOT `import` `@deepseek-ai/dsh*`
- [x] 1.2 `collectFailureFacts` / `isReasoningEffortRejection` MUST ler `Error.message`, `Error.code` e `status` mesmo não enumeráveis; 401 / rate-limit / deny Guard continuam false
- [x] 1.3 Exportar `formatChildRunFailure({ stopReason, failure })`: texto com `stopReason`, `Diagnostic:` + **só** `reason.error.message` já no `turn/end` (MUST NOT `JSON.stringify(failure)`), `class=dsh_reasoning_effort_none` quando `isReasoningEffortRejection` casa, e uma linha de fallback (não re-spawnar o mesmo preset / gate `dsh_reasoning_effort_spawn`)
- [x] 1.4 **Não** editar `guard.py` (fonte MUST NOT conter `reasoningEffort` / `dsh_reasoning_effort` novos além dos haystacks #817 já presentes); não editar `dsh_stubs.py`, `process-fsm.yaml`, `AGENTS.md`, `backend/` nem `frontend/src/`; não vendorar runtime; não editar `~/.dsh/settings.yaml`

## 2. Plugin Guard: agent/created, session/event global, settlement, foreground execute

- [x] 2.1 `.dsh/plugin/process-fsm-guard.js`: `ctx.on("agent/created", ({ agent }) => attachAgentEffortGuards(agent.ctx), { global: true })` no mesmo `apply` (sem lançar). Host `agent/request` do #817 MAY permanecer; o aceite do `high` é o attach no `agent.ctx`. `inject` MAY ficar `["systemPrompt","skills"]`
- [x] 2.2 `ctx.on("session/event", handler, { global: true })`: guardar `turn/end` `reason.kind=error` chaveado pelo session id do filho. Presence-only ainda filtra por tag — **sem** `{ global: true }` o store pode não ver o filho (mesmo furo #817). MUST NOT tratar `session/event` como unscoped
- [x] 2.3 **Foreground only** (`tools/execute`): para `subagent` / `subagent_fork` **one-shot**, inspeccionar o **result de `next()`** (`isError` / content `Error: subagent run failed`) e reescrever com `formatChildRunFailure`. MUST NOT ser throw-only. `send_message` **fora** deste wrapper (o `execute` dele sucede)
- [x] 2.4 **Settlement continuable / `send_message` (veículo live, checkbox separado de 2.3):** **depois** de persistir `turn/end` no store (2.2), `parent = ctx.get("agents")?.get(header.parentSession)` e entregar `formatChildRunFailure` via `parent.followup` se idle / `parent.steer` se busy; `inject` **só** se a linhagem do pai já fecha. `source` = `{ kind: "plugin", plugin: "covenant-flow-process-fsm-guard", form: "notice" }`. Start/`send_message` `next()` MAY suceder (`started subagent <id>` / `message queued`) **antes** do 400 — o Diagnostic MUST **não** viver nesse `execute`. MUST NOT vender `inject()` como o erro que o pai vê. Settlement genérico (`Background subagent … failed` / `It left no closing message.` / `source.kind="subagent-settled"`) sozinho MUST NOT ser o aceite
- [x] 2.5 Ordem `tools/pre-execute` inalterada (grill → `dsh_reasoning_effort_spawn` → cordis → `runGuard`). **Não** alterar `.dsh/cordis.patch.yml` nem `.cursor/hooks.json`. **Não** deny global de `subagent`

## 3. Goldens pytest `scripts/process-fsm`

- [x] 3.1 Mock F* MUST ser **append-inner** por omissão e honrar `{ prepend: true }` / `{ global: true }` (MUST NOT reutilizar `_waterfall_ctx_prelude` wrap-as-outer E3). F1: predicado estilo `scopeTarget` (untagged admitido; tagged só key/ancestral; `global` bypass) + strip estilo `installModelSelection` → retorno **sem** `high`. MUST NOT verde com o mock E3 same-ctx nem com um `EventEmitter` separado que esconde o filtro
- [x] 3.2 F2: `apply(host)` + dispatch `agent/created` `{ agent: { ctx: childCtx } }` `{ global: true }` após o strip → `reasoningEffort === "high"` com descriptor só provider+model. MUST NOT verde só com `attachAgentEffortGuards(childCtx)` sem o created
- [x] 3.3 F3: attach **sem** `prepend` após o strip no `childCtx` → **sem** `high` (prepend load-bearing; exige mock append-inner)
- [x] 3.4 F4: `agent/request-error` prepended no `childCtx` com `Error` não enumerável desta classe → `{ kind: "retry" }`; 2ª no mesmo filho → `next()`. Host-only listener MUST NOT fazer F4 passar
- [x] 3.5 F5: foreground `next()` **sucede** com `{ isError: true, content: "Error: subagent run failed" }` → result reescrito com `stopReason` + `Diagnostic:` + `dsh_reasoning_effort_none`. Throw-only MUST falhar F5. F6: 401 / rate-limit / Guard deny **sem** essa classe
- [x] 3.6 **F7 (P1-1):** start/`send_message` `next()` **sucede** → `session/event` `{ global: true }` vê `turn/end` 400 → pai recebe `followup`/`steer` com `stopReason` + `Diagnostic:` + `dsh_reasoning_effort_none`. Settlement genérico sozinho MUST falhar F7. Host `session/event` **sem** `{ global: true }` MUST NOT fazer F7 passar. **F8:** segundo `agent/request` no mesmo filho continuable ainda `high`
- [x] 3.7 E1–E12 #817, G1 grill-shaped e write deny #784 passam. E11: `guard.py` sem needles novos; stubs `.dsh/skills/` ≤8; `.dsh/` sem T0–T17; `AGENTS.md` inalterado. Pin-test espera a tag que Apply cravar (não hardcode `v1.1.9` no vácuo). `pytest scripts/process-fsm` sem GitHub

## 4. Produto covenant-flow (próximo patch após v1.1.8)

- [x] 4.1 Commit no repo `oalansilva/covenant-flow` (plugin + lib + goldens F1–F8) após rebase no tip. Tag = próximo patch livre (`git ls-remote --tags`; origin neste Design = `v1.1.8` ocupado; esperado `v1.1.9` se livre; não major; não mover `v1.1.8`; não vendorar DeepSeek). MUST NOT reverter haystacks #817/#818; MUST NOT reabrir esses issues como trabalho
- [x] 4.2 `install.sh --pin` continua a copiar `.dsh/` sempre; `CLIENT_KEYS` três; `SCHEMA_MAJOR` 1; sem Auto dsh

## 5. Pin Cripto

- [ ] 5.1 `implantar --pin` da tag de 4.1 no worktree Cripto; overlay `pin:` = essa tag; `clients.dsh.auto: false` permanece
- [x] 5.2 Não ligar porta 3080 em `environments.dev.services`; não systemd; não reabrir #817/#818/#837 como trabalho; não dual-write T0–T17; não editar `backend/` / `frontend/src/`

## 6. Verificação

- [x] 6.1 `openspec validate card-839-dsh-spawn-isolado --type change --strict` verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)
- [x] 6.2 Stubs `.dsh/skills/` ≤8 linhas; `.dsh/` sem T0–T17; `AGENTS.md` ≤40; sem Auto dsh; `.cursor/hooks.json` matcher Write inalterado

## 7. Homologação humana (Design especifica; Apply/homologação executa; **não** opcional)

- [ ] 7.1 Dump autenticado da GUI dsh web `http://127.0.0.1:3080` de **um** spawn isolado (Design-autor **OU** sonda `PROBE_OK`) no mesmo tipo de modelo que recusa esforço desligado (testemunha `muse-spark-*`): plugin pinado, cwd = `canonical_paths.dev`. O dump MUST mostrar o filho a entrar em `turn/start`, ≥1 `tool/call` **OU** mensagem `PROBE_OK`, fecho, e **zero** 400 desta classe nesse spawn. Pytest F1–F8 **não** substitui este dump. Homologação ≠ `./restart` de produto; 3080 ≠ systemd. Este checkbox é o DoD humano — MUST NOT ser residual opcional nem Done só com golden
