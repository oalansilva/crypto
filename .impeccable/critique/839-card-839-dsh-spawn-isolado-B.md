# Snapshot — card #839 `card-839-dsh-spawn-isolado` (Assessment B)

- Card: #839 — https://github.com/oalansilva/crypto/issues/839 (OPEN, label `bug`)
- Change: `openspec/changes/card-839-dsh-spawn-isolado/`
- Critic: isolated Design Critic B (static detector; inherit de modelo; **sem** transcript do pai; **sem** resultados de Assessment A)
- UTC: 2026-09-05T03:20:18Z
- Tuple: hooks `resolve()` → `q=None` `bound_card=839` `q_git=card-839-dsh-spawn-isolado`. Board Project 1 **Status=Design** (`PVTI_lAHOAAHtBM4BV8b2zg5iAXk`). Write produto deny. Esta onda só `.impeccable/critique/**`. MUST NOT editar `design.md`. `.grok/rules/process-fsm-page.md` ausente; tuple via `scripts/process-fsm/resolve.py` + GraphQL do item.
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-839-dsh-spawn-isolado` (branch `card-839-dsh-spawn-isolado`)
- Overlay live: `pin: v1.1.8`; `clients.dsh.auto: false`
- Produto origin tags: `v1.1.8` (latest) … `v1.0.0`. **`v1.1.9` ainda livre** (`gh api repos/oalansilva/covenant-flow/tags`)
- UI impact: **none** (harness/plugin dsh + goldens + pin; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** confirmed — zero HTML desta change; `frontend/public/prototypes/` sem `card-839*`; Playwright visual **não** correu (Browser N/A; `/login` não conta)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Detector = issue vs OpenSpec vs runtime live dsh/cordis vs plugin/lib
- `design.md` sha256: `c8f26caac9bbb9e2344da32aa1a1fe59056030334fe0fda780ee937cd77a301b` (**1861** palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + 2 spec deltas: `process-harness`, `covenant-flow`)
- `openspec validate card-839-dsh-spawn-isolado --type change --strict`: **valid**
- `openspec` tasks: **21** checkboxes
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto; este crítico MUST NOT editar `design.md`)
- Git: change **untracked** (`?? openspec/changes/card-839-dsh-spawn-isolado/`); zero diff de produto nesta onda
- Clone gate T5: `evaluate_clone_gate` → **True** (`UI impact: none` + not existing). Parser **não** lê `live_route: N/A` (heading `## live_route` + `N/A — …`) nem `surface: new` (`surface: new (harness)` falha o `$`); isenção passa pelo ramo `ui==none`
- Grill comment: `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`

---

## Brief

Spawn isolado dsh (`subagent` / `subagent_fork`) nasce, `turn/start`, morre no step 1 com 400 `"reasoning.effort" does not support "none"`. Pai persiste `reasoningEffort: "high"`; filho só `{provider, model}`. Pai vê `Error: subagent run failed` sem `Diagnostic`. Residual live do #817 (Homologado, pin `v1.1.8`): sanitizer/retry no `ctx` do plugin host não ganha no filho. #837 parado com `ERROR` de spawn — efeito, não trabalho deste card.

Audience: operador no cliente dsh (Design/Apply/Review/QA). Outcome: sonda `PROBE_OK` bg+fg; `send_message` devolve resultado; falha real sobe `stopReason`+`Diagnostic`+classe `dsh_reasoning_effort_none`. Direction: attach no `agent.ctx` via `agent/created` `{ global: true }` + `{ prepend: true }`, *outer* a `installModelSelection`; pin próximo patch após `v1.1.8`. Scope: pele `covenant-flow` (Guard + `dsh_plugin_lib.js`) + goldens F*; zero UI Cripto.

---

## Probes (live, este worktree, pré-Apply)

### Cordis / dsh-scope — APIs que o Design invoca

| Claim do Design | Live | Resultado |
| --- | --- | --- |
| `agent/created` existe, payload `{ agent }` | `dsh-agent` Events + `AgentRegistry.announce` emite `{ agent }` **depois** do setup; scoped (`scopedSubjectResolvers["agent/created"]` = `args[0].agent`) | **LIVE** |
| `{ global: true }` | Cordis `EventOptions.global`; `dispatch` admite `hook.global \|\| !filter \|\| filter(hook.ctx)`; dsh-scope: global bypassa o predicado | **LIVE** |
| `{ prepend: true }` | Cordis `EventOptions.prepend` → `unshift`; boolean shorthand = prepend | **LIVE** |
| `agent.ctx.on("agent/request", sanitize(await next()), { prepend: true })` | `agent.ctx` = `createScope(loopCtx, agent).ctx.extend({ agent })`; `installModelSelection` regista no mesmo `agentCtx` **sem** prepend, **depois** de `next()` strip se `selected.reasoningEffort` ausente | **LIVE** (attach *outer* ao strip se prepend após setup) |
| `session/event` “unscoped” | `dsh-scope`: `null` resolver = **presence-only** (exige carrier; **não** casa subject). Dispatch: `entry.carrier` + `collectSessionCallbacks` → `events.dispatch("emit", args)`. Filter de tag **ainda aplica** | **LIVE, impreciso** (“unscoped” ≠ sem filtro) |
| `tools/execute` rewrite de throw genérico | Waterfall live; `next()` = `dispatchToolBody` que **catch** e devolve `toolErrorResult` (`isError: true`, `content` `Error: ${message}`). Wrapper que só `catch` o throw do `next()` **não dispara**. Tipos: wrapper MAY mutar só `exec.signal`; devolver outro result é o que o timeout policy faz | **LIVE waterfall; throw-mock ≠ live** |
| `source.kind="plugin"` inject | `MessageSourceMap.plugin` exige `{ kind: "plugin", plugin: string }` (+ `ContextFormed`). `Agent.inject()` existe e **não acorda** o driver | **LIVE, incompleto no Design** |

Testemunha de `agent/created` sem global: `dsh-file-reference-local` faz `ctx.on("agent/created", ({ agent }) => installPrompt(agent))` e `ctx.on("session/event", …)` — padrão untagged no root. O Guard `--patch` com `inject=["systemPrompt","skills"]` é o mesmo tipo de fiber **se** permanecer untagged; o furo #817 é exactamente que o host `agent/request` **não** sanitizou o filho.

### Runtime do 400 (confirma o issue, não o Design)

- `installModelSelection` (`dsh-agent/lib/index.js`): após `next()`, apaga esforço herdado se a selecção não traz `reasoningEffort`.
- `buildRequest` (`dsh-agent-loop`): seed do filho = route `{provider, model}` (descriptor sem esforço); waterfall `agent/request`; **depois** `llm.prepareCall` (não clamp/alias).
- Adapter `pi-ai` openai-responses: se `model.reasoning` e **sem** `options.reasoningEffort`, `effort: (model.thinkingLevelMap?.off ?? "none")`. Perfil `off: null` **omite** a chave do mapa → `"none"`. Confirma o Design.
- `toStopReason`: só `kind` → `"error"`. `readResult` **não** copia mensagem para `diagnostic`.
- `stopReasonError`: `"error"` → `"subagent run failed"`. `withDiagnosticAndPartialText` só acrescenta `Diagnostic:` se `result.diagnostic` existir.

### Continuable / `send_message` (incidente live)

- `dsh-tool-subagent`: continuable start devolve `{ kind: "continuable", subagentId }` → `started subagent <id>` **sem esperar** o turno.
- Settlement (`dsh-subagent` `notifySettlement`): `Background subagent <id> failed before it finished.` + `It left no closing message.` Fonte `kind: "subagent-settled"`. Entrega: `followup` se pai idle, `steer` se busy, `inject` **só** se a linhagem do pai já está a fechar.
- `send_message` (`dsh-tool-subagent-control`): “returns no answer from the subagent — only confirmation that the message was delivered”. `execute` → `ctx.subagents.followup(...)` → `{ messageId }`. **Não lança** `subagent run failed` / `no closing message`. Turno 2 do filho (`c2f3f1a7` / `b6299032` no issue) é outro `agent/request` com o mesmo config partido.

### Plugin / lib live (pré-Apply, pin `v1.1.8`)

- Guard: `inject=["systemPrompt","skills"]`; `ctx.on("agent/request", sanitize(await next()))` **sem** `global`/`prepend`; `agent/request-error` retry; `tools/pre-execute` = grill → `dsh_reasoning_effort_spawn` → cordis → `runGuard`. **Sem** `agent/created`, **sem** `session/event`, **sem** `tools/execute`.
- `collectFailureFacts`: `Object.keys` — `Error.message` / `code` não enumeráveis **omitidos**. D3 do Design acerta o furo do retry #817.
- Goldens E3–E8: um `mockWaterfallCtx` (`events[name]` encadeado, **same-ctx**). Não há F* isolado. Esperado pré-Apply.

### #817 residual (change ainda em `openspec/changes/card-817-dsh-reasoning-effort/`, não archive)

D4 #817: host `ctx.on("agent/request", sanitize(await next()))`. Risks #817 já nomeavam: “se o host plugin não receber o evento, Apply MUST registar no agente-scope”. F1 deste card MUST falhar esse desenho (bus distinto). **Não** reabre #817 como trabalho.

### Superfície visual / clone gate

Zero `card-839*` em `frontend/public/prototypes/`. Zero `frontend/src/` / `backend/` no Apply contract. `UI impact: none` **não** está mal classificado. Prototype N/A justificado (aceite = spawn dsh + dump `:3080`, não tela Cripto).

---

## Hunt (furos pedidos) — issue vs Design vs live

| Furo | Issue / aceite | Design | Live | Disposition |
| --- | --- | --- | --- | --- |
| PROBE_OK bg+fg | Critério 1 | Goals + homologação 7.1 (Design-autor **ou** `PROBE_OK`) | Sanitizer no `agent.ctx` *outer* ao strip (D2) — APIs reais | **CLOSED** no contrato D2 **se** attach ganhar; bg continuable não espera o turno no `tools/execute` |
| `send_message` vs `failed … no closing message` | Critério 2 | Goals + task 2.3 (`tools/execute` + inject) | `send_message` só entrega; o texto genérico é o **settlement notice**; turno 2 reusa o config se D2 falhar | **P1** — inject **não** tapa aceite 2; D2 sim; task/spec fingem que execute vê a falha |
| `stopReason` + `Diagnostic` | Critério 3 | D4 `session/event` + `tools/execute` rewrite + inject | Foreground: `next()` de execute **não throw**; continuable: settlement `followup`/`steer`, `inject()` não acorda | **P1** |
| #837 desbloqueado como efeito | Critério 4 | Non-goal board; homologação dump de **um** spawn | Não toca issue/board #837 | **CLOSED** (efeito de D2, não Apply de #837) |
| Classe 400 nomeada | Critério 5 | `class=dsh_reasoning_effort_none` via `formatChildRunFailure` | Formatter no plugin é pele válida; o **veículo** até o pai é o P1 acima | **P1** (veículo); classe em si **CLOSED** no contrato |
| API Cordis inventada | Hunt P0 | `agent/created`, prepend, global, execute, session/event | Todas existem; “session/event unscoped” é presence-only; execute rewrite-as-throw é o mock errado | **não P0**; P1 no *uso* |
| UI none / Prototype N/A / clone gate T5 | Hunt | UI none + N/A justificado | Zero HTML; clone_gate True | **CLOSED** |
| Host listener #817 MAY ficar vs F1 | Hunt | D2: aceite = attach `agentCtx`; F1 host-only **sem** `high` | F1 falha o desenho antigo por contrato | **CLOSED** |
| Continuable start devolve id antes do 400 | Issue facto | D4 (c) inject; task 2.3 MAY | Confirmado live | **P1** (inject ≠ settlement) |
| Segredo de provider no Diagnostic | Avoid do issue | “Sem segredo além do `turn/end` já logado” | 400 `INVALID_REQUEST` no log do filho não é secret; risco se stringify do `failure` | **P2** aceite se o formatter copiar só a mensagem já logada |
| Proposal vs design vs tasks vs spec | Hunt | Canal = `agentCtx`; pin próximo após `v1.1.8`; `guard.py` sem needles | Alinhados no feliz (D2). Divergem no veículo de Diagnostic/`send_message` (task 2.3 / spec “would throw”) | **P1** nessa fatia; resto **CLOSED** |
| Pin `v1.1.8` / próximo livre | Proposal/Design | Apply `git ls-remote`; esperado `v1.1.9` se livre; MUST NOT major; rebase tip #817/#818 | Origin `v1.1.8` ocupado; `v1.1.9` livre | **CLOSED** no contrato |

---

## Rubrica (UI none)

- **Escopo:** issue critérios 1–5 sintetizados (PROBE_OK bg/fg; send_message; Diagnostic; #837 como efeito; classe nomeada). Pin neste card. Não reentrevista. Não reabre #817/#818/#837 como trabalho. Não vendorar `@deepseek-ai/dsh*` / `pi-ai`.
- **Regressão:** E1–E12 #817 same-ctx permanecem; F1 MUST falhar host-only; grill → `dsh_reasoning_effort_spawn` → cordis → `runGuard`; `guard.py` `decide()` sem needles novos.
- **Riscos operacionais:** veículo Diagnostic no modo **continuable** (incidente); `inject()` vs `followup`/`steer`; `session/event` sem `{ global: true }`; F5 throw-only.
- **Superfície visual:** nenhuma. Prototype N/A.

---

## Critique (contrato vs live)

`openspec validate --strict` verde. Prototype N/A justificado. Sem HTML. Sem `## Design Critique` pré-preenchido. Clone gate T5 passaria. Pin origin correcto.

**D2 não assenta em API inventada.** `agent/created` + `{ global: true }` + `{ prepend: true }` no `agent.ctx` são Cordis/dsh live; `installModelSelection` é inner sem prepend; F1/F3 tornam prepend load-bearing. Isso é o caminho feliz dos aceites 1/4 e (se o attach persistir no mesmo `agent.ctx`) do aceite 2.

**D4/task 2.3/spec F5 assentam no veículo errado para o incidente live (continuable).** O pai não recebe a falha como throw de `subagent`/`send_message`. Recebe o settlement notice. `tools/execute` vê um **result** `isError` no foreground e um **sucesso** `started subagent <id>` no background. `Agent.inject()` não é o que o runtime usa para acordar o pai. Aceites 3 e 5, e o fallback se D2 falhar no turno 2, ficam por cumprir com o texto actual.

P0 de API inventada: **não**. P1 de aceite vs live: **sim**.

---

## Findings

### P0

*(nenhum aberto — `agent/created`, `{ global: true }`, `{ prepend: true }`, `tools/execute`, `session/event`, `Agent.inject`, `source.kind="plugin"` existem no checkout dsh/cordis)*

### P1

- **P1-1 — Aceites 2/3/5 no modo live continuable usam o veículo errado.** Incidente: start devolve `started subagent <id>` **antes** do 400; `send_message` só confirma entrega (`message queued…`); o texto `failed before it finished` / `It left no closing message.` é o settlement (`followup` idle / `steer` busy). Design D4 + task 2.3 + spec “Foreground generic throw” / “send_message after the same broken child” pedem `tools/execute` a relançar throw genérico + `inject` `source.kind="plugin"`. Live: `tools/execute` `next()` **não throw** (`dispatchToolBody` → `toolErrorResult`); `send_message` **não falha** quando o filho 400; `Agent.inject()` **não acorda** o pai e **não reescreve** o notice. **Inject no pai não é suficiente: aceite 2 continua partido no mesmo config se D2 não ganhar no turno 2.** F5 (throw `subagent run failed`) MUST NOT verde como prova do incidente. Fechar: (a) aceite 2 = D2 no mesmo `agent.ctx` em **todo** turno (F* de segundo `agent/request` no filho continuable); (b) aceite 3/5 = observar `turn/end` e **seguir o settlement** (`followup`/`steer`, ou reescrever o result `isError` no foreground via `tools/post-execute` / inspect de `next()`); (c) MUST NOT vender `inject()` como o erro que o pai vê.

- **P1-2 — `session/event` “unscoped” sem `{ global: true }` é o mesmo furo de filtro que o Design atribui ao #817.** `agent/created` leva `{ global: true }` precisamente porque o evento é agent-scoped. `session/event` é presence-only **com carrier**; o predicado de tag ainda corre. Task 2.2 / D4 registam `ctx.on("session/event")` sem global. Se o fiber do Guard estiver tagged (explicação residual do host `agent/request` não ver o filho), o store de `turn/end` **não vê** o filho — Diagnostic/F5 sem factos. Fechar: o mesmo `{ global: true }` (ou attach no `agent.ctx` do pai **e** do filho) no listener de `session/event`; golden com bus/filtro distinto, não só um `ctx.on` no mock same-ctx.

### P2

- **`source.kind="plugin"` incompleto.** Live exige `plugin: string` (e `form: "notice"` + `summary` se for notice). Design só diz `source.kind="plugin"`.
- **F1 mock “segundo bus” vs Cordis partilhado.** Live `_hooks` é um `EventsService`; o isolamento é **filtro de tag**, não `childCtx.events` distinto. F1 ainda falha o #817 se o mock filtrar o host; um mock de EventEmitter separado pode passar attach e **não** reproduzir `{ global: true }`. Apply MUST ouro no predicado `scopeTarget` (untagged admitido; tagged só key/ancestral; global bypass).
- **`live_route` / `surface` fora do regex T5.** Passa hoje porque `ui==none`. SHOULD `live_route: N/A` na mesma forma que #817 (`live_route: N/A harness-only`) e `surface: new` sem sufixo na linha.
- **Segredo no Diagnostic.** Contrato “só o `turn/end` já logado” é o tecto certo. Formatter MUST NOT `JSON.stringify(failure)` (headers / apiKey). Aceite se copiar `reason.error.message` já no log.
- **“Qual fallback aplicar” (critério 5).** Classe `dsh_reasoning_effort_none` nomeada; o fallback (gate `dsh_reasoning_effort_spawn` / não re-spawn) fica implícito no #817. SHOULD uma linha no texto ao pai.
- **`tasks.md` 2.3** junta execute rewrite + inject continuable no mesmo bullet — o Apply pode implementar só o catch de throw e dar F5 verde.

### P3

- Inject + settlement duplicam aviso (Design já aceita wording verboso).
- `agent/created` sync throw **veta** publicação do filho — `attachAgentEffortGuards` MUST NOT lançar.
- Host listener #817 MAY ficar (idempotente se o evento chegar).
- `dsh-llm-retry` no mesmo `agent.ctx` — prepend do nosso `request-error` decide esta classe antes (F4). Residual ordem de outros plugins.
- Homologação `:3080` cwd canónico ≠ worktree; 3080 ≠ systemd; ≠ `./restart`.
- Change #817 ainda em `openspec/changes/` (não archive); este card MUST NOT a reabrir.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. Browser gate: **N/A (no UI)**.
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM yaml: sem task de estado/evento. T1/T7 Alan; T5 parent. Dual-write T0–T17 **proibido** no pacote.
- Product UI: zero `frontend/src/` / `backend/` de app no Apply contract.
- Auto dsh: overlay live `false`; specs MUST NOT reivindicar; pin não injeta a chave.
- `CLIENT_KEYS` / `SCHEMA_MAJOR` inalterados.
- Vendor `@deepseek-ai/dsh*` / `pi-ai`: proibido; leitura de runtime só nesta crítica.

---

## Trace

1. Issue #839 REST: 5 aceites; continuable `started subagent <id>` antes do 400; `send_message` turno 2 = mesmo 400; Diagnostic no `turn/end` do filho.
2. Runtime: `agent/created` + prepend/global **reais**; `installModelSelection` strip após `next()`; pi-ai `thinkingLevelMap.off ?? "none"`; `readResult` sem `diagnostic`; `send_message` não espera; settlement `followup`/`steer`.
3. Design D2 (attach `agentCtx`) alinha com o feliz e com F1 a falhar o #817. D4/task 2.3/spec F5 alinham com um throw que o live **não** faz no incidente.
4. Plugin live `v1.1.8` = host `agent/request` sem global/prepend; `collectFailureFacts` sem `Error.message`.
5. Clone gate / HTML / Design Critique / pin origin: limpos.

---

## Disposition

Zero P0 de API inventada. Dois P1 abertos no **veículo** dos aceites 2/3/5 (continuable settlement vs `tools/execute` throw + `inject()`; `session/event` sem `{ global: true }`). D2 (attach prepend no `agent.ctx` via `agent/created` global) é API live e é o único caminho que tapa aceite 1/2/4 se ganhar em **todos** os turnos do filho — F* MUST cobrir o segundo `agent/request` continuable, não só o first-step one-shot. UI none / Prototype N/A / T5 / #837-como-efeito / pin `v1.1.9` livre / F1 contra o #817 estão fechados. Sem polish visual. MUST NOT editar `design.md` daqui. Filho autor MUST fechar P1-1 e P1-2 no pacote OpenSpec antes de T5.

### Verdict

**BLOCKED**
