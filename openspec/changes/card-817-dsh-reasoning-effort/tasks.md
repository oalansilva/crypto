## 1. Lib: sanitize + classify this-class 400 (JS only)

- [x] 1.1 Em `scripts/process-fsm/dsh_plugin_lib.js`, exportar `sanitizeReasoningEffort(config)`: tokens recusados (case-insensitive, trim) `none` / `off` / `""` / `null` e nested `reasoning.effort` → `reasoningEffort: "high"`; valor já aceite ∈ {minimal, low, medium, high} keep; campo ausente → `high`; nested `none` MUST NOT sobreviver
- [x] 1.2 Exportar `isReasoningEffortRejection(failure)`: needles `reasoning.effort` / `reasoningEffort` / `UNSUPPORTED_REASONING_EFFORT` **e** `none` / `off` / `does not support`, ou `INVALID_REQUEST` / `400` com esses needles; 401 / rate-limit / deny Guard → false
- [x] 1.3 **Não** editar `guard.py` (fonte MUST NOT conter `reasoningEffort` / `dsh_reasoning_effort`); não editar `dsh_stubs.py`, `process-fsm.yaml`, `AGENTS.md`, `backend/` nem `frontend/src/`; não vendorar `deepseek-harness`; não editar `~/.dsh/settings.yaml` como canal de pin

## 2. Plugin Guard: agent/request, request-error, spawn gate

- [x] 2.1 `.dsh/plugin/process-fsm-guard.js`: `ctx.on("agent/request", async (payload, next) => sanitizeReasoningEffort(await next()))` no mesmo `apply` do Guard; `inject` permanece `["systemPrompt", "skills"]`
- [x] 2.2 `ctx.on("agent/request-error")`: 1ª recusa desta classe no **mesmo agente** (session id de `payload.agent`, **não** `payload.turn` sozinho) → `{ kind: "retry" }` sem `next()`; 2ª → `next()`. Retry = mesmo agente, **não** spawn novo. `payload.provider` é o LLM (`opencodealan`) e MUST NOT decidir filho vs root
- [x] 2.3 Filho = `payload.agent.session.header.delegationDepth >= 1` **ou** `header.origin === "subagent"` **ou** `header.parentSession` presente. MUST NOT `payload.provider === "spawn"` (live nunca é `"spawn"`). MUST NOT `import` `@deepseek-ai/dsh-subagent`. Gate = `Set` de `header.parentSession` (fallback: session id do caller/root), **não** `Map(payload.turn)` do filho. 400 desta classe num filho adiciona a `parentSession` ao Set; `tools/pre-execute` **do root** (outro agente, outro `turn`) lê o Set e deny `subagent` / `subagent_fork` com reason `dsh_reasoning_effort_spawn` sem `next()`. Root depth 0 / sem `parentSession` **não** fecha o gate
- [x] 2.4 Ordem `tools/pre-execute`: (1) `isGrillShapedSpawn` (2) gate `dsh_reasoning_effort_spawn` (3) `isCordisRestricted` (4) `runGuard`. Listener deny **antes** de `registerProvider`; try/catch do provider intacto. **Não** alterar `.dsh/cordis.patch.yml` nem `.cursor/hooks.json`

## 3. Skill canónica (uma linha dsh)

- [x] 3.1 `.cursor/skills/covenant-flow/SKILL.md`: **uma** linha no ramo dsh — após 400 desta classe num filho, MUST NOT spawnar mais o mesmo preset (incl. retry 1/1 #518); registar `ERROR: subagent spawn failed/empty` e continuar no root com residual explícito. `AGENTS.md` **não** cresce. Stubs `.dsh/skills/*` intactos (≤8)
- [x] 3.2 Não alongar peles `.grok` / `.opencode`. Não dual-write T0–T17. Não deny global de `subagent`

## 4. Goldens pytest `scripts/process-fsm`

- [x] 4.1 E1/E2/E10: unitário JS de `sanitizeReasoningEffort` (`none`/`off`/nested/`medium`/ausente) e `isReasoningEffortRejection` negativos (401 / rate-limit / Guard)
- [x] 4.2 E3–E8: `import { apply }` from `.dsh/plugin/process-fsm-guard.js` + waterfall que **encadeia** inner stripper estilo `installModelSelection` (o mock overwrite-on esconde o furo). E3 ganha ao strip; E4 filho só provider+model → `high`; E5 root `turn: 9` `provider: "opencodealan"` depth 0 → retry; E6 2ª no mesmo agente → `next()`; E7 MUST: filho `turn: 1` + `provider: "opencodealan"` + `header.delegationDepth: 1` + `origin: "subagent"` + `parentSession: <rootSession>` **depois** `tools/pre-execute` no root `turn: 9` (≠ 1) `subagent` Apply e reviewer → deny `dsh_reasoning_effort_spawn` (MUST NOT verde com `provider: "spawn"` nem com o mesmo `turn` nos dois lados); E8 root `turn: 9` `provider: "opencodealan"` sem `parentSession` → `subagent` Apply `next()` e grill-shaped ainda deny
- [x] 4.3 E9: mesmo `apply` ainda deny grill-shaped + cordis + write ilegal; `registerProvider` throw não salta. G1–G9 #786 e D13/D16/D20 #784 passam
- [x] 4.4 E11: fonte de `guard.py` sem `reasoningEffort` / `dsh_reasoning_effort`; `dsh_stubs.py` / `process-fsm.yaml` / `AGENTS.md` inalterados nesta change; stubs `.dsh/skills/` ≤8; `.dsh/` sem T0–T17
- [x] 4.5 E12: pin-test (quando `install.sh` existe) espera `v1.1.7` (ou o patch livre cravado no origin); `clients.dsh.auto: false`. `pytest scripts/process-fsm` sem GitHub

## 5. Produto covenant-flow (tag v1.1.7)

- [x] 5.1 Commit no repo `oalansilva/covenant-flow` (plugin + lib + linha covenant-flow + goldens) após rebase no tip do produto. Tag = próximo patch livre (`git ls-remote --tags`; esperado `v1.1.7` se livre; não major; não mover `v1.1.6`; não vendorar DeepSeek). Irmão #818 (`card-818-dsh-grill-spawn-cite`) partilha os mesmos ficheiros de pele — MUST NOT reverter haystacks dele; se ambos landed, a tag pinada MUST conter os dois deltas
- [x] 5.2 `install.sh --pin` continua a copiar `.dsh/` sempre; `CLIENT_KEYS` três; `SCHEMA_MAJOR` 1; skill `implantar` / README não reivindicam Auto dsh

## 6. Pin Cripto

- [x] 6.1 `implantar --pin` da tag de 5.1 no Cripto; overlay `pin` = essa tag; `clients.dsh.auto: false` permanece. Se #818 já tiver pinado uma tag, o `--pin` mais novo MUST incluir ambos os deltas
- [x] 6.2 Não ligar porta 3080 em `environments.dev.services`; não systemd; não reabrir #790/#782/#784/#786/#518/#569; não dual-write T0–T17; não editar `backend/` / `frontend/src/`

## 7. Verificação

- [x] 7.1 `openspec validate card-817-dsh-reasoning-effort --type change --strict` verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)
- [x] 7.2 Stubs `.dsh/skills/` ≤8 linhas; `.dsh/` sem T0–T17; `AGENTS.md` ≤40; sem Auto dsh; `.cursor/hooks.json` matcher Write inalterado

## 8. Homologação humana Q3=A (Design especifica; Apply/homologação executa; **não** opcional)

- [ ] 8.1 Dump autenticado da GUI dsh web `http://127.0.0.1:3080` de **um** spawn Apply **ou** reviewer isolado no mesmo tipo de modelo que recusa esforço desligado (testemunha `muse-spark-*`): plugin pinado, cwd = `canonical_paths.dev`, preset da evidência (`danger-full-access` / `standard`). O dump MUST mostrar o filho a entrar em `turn/start`, ≥1 `tool/call`, mensagem de fecho, e **zero** recusa desta classe nesse spawn. Pytest E1–E12 **não** substitui este dump. Homologação ≠ `./restart` de produto; 3080 ≠ systemd. Este checkbox é o DoD humano Q3=A — MUST NOT ser tratado como residual opcional nem como Done só com golden.
