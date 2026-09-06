# Snapshot — card #839 `card-839-dsh-spawn-isolado` (Assessment B r2)

- Card: #839 — https://github.com/oalansilva/crypto/issues/839 (OPEN, label `bug`)
- Change: `openspec/changes/card-839-dsh-spawn-isolado/`
- Critic: isolated Design Critic B r2 (static detector; inherit de modelo; **sem** transcript do pai; **sem** resultados de Assessment A; **sem** inherit do B-r1 como prova — recheck só no texto r2 + runtime live)
- UTC: 2026-09-05T03:37:12Z
- Tuple: `.grok/rules/process-fsm-page.md` ausente. `scripts/process-fsm/resolve.py` neste cwd → `q=None` `bound_card=839` `q_git=card-839-dsh-spawn-isolado`. Board Project 1 **Status=Design** (`PVTI_lAHOAAHtBM4BV8b2zg5iAXk`). Write produto deny. Esta onda só `.impeccable/critique/**`. MUST NOT editar `design.md`.
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-839-dsh-spawn-isolado` (branch `card-839-dsh-spawn-isolado`)
- Overlay live: `pin: v1.1.8`; `clients.dsh.auto: false`
- Produto origin tags: `v1.1.8` (latest) … `v1.0.0`. **`v1.1.9` ainda livre**
- UI impact: **none** (harness/plugin dsh + goldens + pin; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** confirmed — zero HTML desta change; `frontend/public/prototypes/` sem `card-839*`; Playwright visual **não** correu (Browser N/A; `/login` não conta)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Detector = issue vs OpenSpec r2 vs runtime live dsh/cordis vs plugin/lib
- `design.md` sha256: `ab009056f6fb06b90c20d427a678ce41d585db597019545f66ec78fd0955de32` (**2330** palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + 2 spec deltas; clone gate True)
- Clone gate T5: `evaluate_clone_gate` → **True**. Tokens agora parseiam: `parse_ui_impact=none`; `parse_live_route=('N/A','harness-only; …')`; `parse_surface=new`; `is_new_exempt` via `live_route: N/A` + `surface: new` na forma do regex
- `openspec validate card-839-dsh-spawn-isolado --type change --strict`: **valid**
- `openspec` tasks: **23** checkboxes
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correcto; este crítico MUST NOT editar `design.md`)
- Git: change **untracked** (`?? openspec/changes/card-839-dsh-spawn-isolado/`); zero diff de produto nesta onda
- Runtime lido (não vendorar): `@deepseek-ai/dsh-agent` Agent `followup`/`steer`/`inject`; `dsh-agent-loop` `ReactLoopAgent`; `dsh-subagent` `notifySettlement`; `dsh-scope` `session/event` presence-only; Cordis `EventOptions.global`/`prepend`; `dsh-llm` `MessageSourceMap.plugin` + `createUserMessage`

P1s r1 tratados como **fechados** só se o pacote r2 (proposal + design D4/D5 + tasks 2.2/2.4/3.5/3.6 + spec process-harness settlement) os pinarem. Este r2 só reabre um item fechado quando essas superfícies se contradizem ou o runtime desmente o veículo.

---

## Round 2 — recheck P1 close

Pedido desta onda: P1-1 settlement `subagent-settled` + F7 (`next` sucede → `turn/end` global → `followup`/`steer` Diagnostic; `inject` NÃO aceite). P1-2 `session/event` `{ global: true }`; listener sem global falha F7. Caçar P0/P1 novos (API inventada, contradição proposal/design/tasks/spec, falso UI none, F7 verde no throw-mock, `followup`/`steer` plugin vs runtime).

| Critério P1 (r1) | Onde no pacote r2 | Live | Resultado |
| --- | --- | --- | --- |
| P1-1 veículo = settlement `subagent-settled`, não throw de `tools/execute` | proposal What Changes; design Goals + D4 + Apply contract; task **2.4** (checkbox separado de 2.3); spec «dsh parent sees stopReason… on the live settlement seam» | Continuable: `execute` devolve `started subagent <id>` **antes** do 400; `notifySettlement` `source.kind="subagent-settled"`; `send_message` só `{ messageId }` | **CLOSED** |
| P1-1 F7: `next()` sucede → `turn/end` global → pai `followup`/`steer` com Diagnostic | design D5 F7; task 3.6; spec scenario «Continuable start succeeds then settlement carries Diagnostic» + «send_message execute succeeds then settlement names the class» | Mesmo seam que `notifySettlement` | **CLOSED** |
| P1-1 `inject` NÃO é o aceite | D4 alternativa rejeitada; task 2.4 MUST NOT vender `inject()`; spec AND «`Agent.inject()` as the only delivery MUST NOT make this scenario pass»; inject residual **só** se linhagem do pai já fecha (igual live `closingTeardownFor`) | `Agent.inject` = `send(..., wakeup=false)` — não acorda | **CLOSED** |
| P1-1 F5 ≠ incidente continuable; throw-only MUST falhar F5 | D5 F5; task 3.5; spec «Foreground isError result…» AND throw-only MUST fail | `tools/execute` `next()` devolve `isError`, não throw (`dispatchToolBody` → `toolErrorResult`) | **CLOSED** |
| P1-1 aceite 2 = D2 em **todo** turno (F8) | Goals; D4(b); task 3.6 F8; spec «Second continuable agent/request… still has high» | Turno 2 (`c2f3f1a7` / `b6299032`) reusa o mesmo `agent.ctx` | **CLOSED** |
| P1-2 `session/event` `{ global: true }` | D4(a); task 2.2; spec SHALL observe with `{ global: true }`; proposal Modified `process-harness` | Presence-only (`resolver=null`) **ainda** filtra por tag; Cordis `hook.global \|\| !filter \|\| filter(hook.ctx)`; `dsh-tools` invariant live já usa `{ global: true }` neste evento; `collectSessionCallbacks(emitCtx, [carrier, "session/event", session, event])` | **CLOSED** |
| P1-2 listener sem global falha F7 | D5 F7; task 3.6; spec AND «host `session/event` listener without `{ global: true }` MUST NOT make this scenario pass»; Risks | Tagged host sem global excluído pelo `scopeTarget`; untagged ainda é admitido (ver P2) | **CLOSED** no contrato (plugin MUST passar global; F7 negativa pinada) |

---

## Brief

Incidente live inalterado: pai `reasoningEffort: "high"`; filho isolado `{provider, model}`; `turn/end` 400 `"reasoning.effort" does not support "none"`; continuable devolve `started subagent <id>` antes do 400; `send_message` confirma entrega; o pai lê settlement genérico (`Background subagent … failed` / `It left no closing message.`), não throw `subagent run failed`.

r2 (intenção cumprida no texto): (1) sanitizer no `agent.ctx` via `agent/created` `{ global: true }` + `{ prepend: true }` — D2; (2) Diagnostic no seam **live** `subagent-settled` via `parent.followup`/`parent.steer` após `session/event` `{ global: true }` guardar `turn/end` — F7; (3) `inject` residual só teardown; (4) F5 = foreground `isError` inspect, não throw-mock; (5) F8 segundo `agent/request` ainda `high`. `UI impact: none`.

Audience: operador no cliente dsh. Outcome: sonda `PROBE_OK` bg+fg; `send_message` devolve resultado; falha real sobe `stopReason`+`Diagnostic`+classe `dsh_reasoning_effort_none`. Direction: pele `covenant-flow` + goldens F1–F8. Scope: zero UI Cripto.

---

## Probes (runtime live, este r2)

### `followup` / `steer` — plugin vs Agent live

| Claim do Design r2 | Live | Resultado |
| --- | --- | --- |
| `parent.followup` se idle | `Agent.followup(message: UserMessage)` em `dsh-agent` + `ReactLoopAgent.followup` = `send(input, "next-turn", true)` | **LIVE** no **Agent**, não no `ctx` do plugin |
| `parent.steer` se busy | `Agent.steer(message: UserMessage)` = `send(input, "next-step", true)` | **LIVE** no **Agent** |
| `inject` só se linhagem fecha | `Agent.inject` = `send(input, "next-step", false)` (não acorda). `notifySettlement`: `parent.inject` se `closingTeardownFor(parent)`; senão `followup` idle / `steer` busy | **LIVE** (residual alinhado) |
| `ctx.get("agents")?.get(header.parentSession)` | Cordis `ctx.get("agents")` (peek); `AgentRegistry.get(id)` devolve o `Agent`. `session.header.parentSession` existe | **LIVE** (não inventado) |
| `source = { kind: "plugin", plugin: "…", form: "notice" }` | `MessageSourceMap.plugin` = `{ kind: "plugin", plugin: string } & ContextFormed`. `form: "notice"` **exige** `summary: string`. `dsh-tool-jobs` manda `createUserMessage({ content: [{type:"text",text}], source: { kind:"plugin", plugin, form:"notice", summary } })` depois `owner.followup(message)` | **LIVE, envelope incompleto no contrato** (P2) |
| Plugin `ctx.followup` / `ctx.steer` | **Não existem.** `ctx.subagents.followup(parent, childId, …)` entrega **ao filho**, não ao pai | Design **não** reivindica isto — usa `parent.followup` |

Conclusão do hunt pedido: `followup`/`steer` **existem no Agent live**. O plugin alcança-os pelo registry. Não é API inventada. Não é o `followup` do serviço `dsh-subagent` (esse é o `send_message` para o filho).

### `session/event` + `{ global: true }`

- Resolver `null` = presence-only (exige carrier; **não** casa subject).
- Dispatch: `hook.global || !filter || filter(hook.ctx)`. `scopeTarget`: untagged admitido; tagged só key/ancestral.
- Store: `collectSessionCallbacks(entry.emitCtx, [carrier, "session/event", session, event])` — **dois** args `(session, event)`.
- `turn/end` data: `{ turn, reason: { kind: "error", error: { message, code } } }` — `event.data.reason`, não um `header` no evento.

### F7 vs throw-mock

Spec F7 WHEN: continuable `next()` **sucede** com `started subagent <id>` **e** `session/event` global grava `turn/end` 400. Throw-only de `tools/execute` **não** entra neste WHEN. F5 (separado) AND: wrapper que só `catch` throw MUST fail. F7 AND: settlement genérico sozinho MUST fail; `inject`-only MUST fail; host sem global MUST NOT passar. **F7 não pode verde só com throw-mock** se o Apply seguir os ANDs listados.

---

## Hunt (P0/P1 novos)

| Furo | Pacote r2 | Live | Disposition |
| --- | --- | --- | --- |
| API inventada (`agent/created`, global, prepend, `session/event`, `followup`/`steer`, `ctx.get("agents")`) | D2/D4/D5 | Todas no checkout dsh/cordis | **não P0** |
| Contradição proposal / design / tasks / spec no veículo | proposal + D4 + 2.3/2.4 + spec settlement alinhados (`inject` rejeitado; F7 settlement; F5 `isError`) | igual | **não P1** |
| Falso UI none | UI none + Prototype N/A + zero `card-839*` HTML + Apply MUST NOT `frontend/src/`/`backend/` | zero superfície Cripto | **CLOSED** |
| F7 verde no throw-mock | F5 throw-only MUST fail; F7 WHEN `next()` sucede | execute live não throw no incidente | **CLOSED** no contrato |
| `followup`/`steer` só no plugin, ausentes no Agent | D4 `parent.followup`/`steer` | Agent live tem os três métodos | **CLOSED** |
| P1-1 / P1-2 reabertos por omissão | 2.4 + 3.6 + spec ANDs | settlement + global | **não reabrem** |

---

## Rubrica (UI none)

- **Escopo:** issue critérios 1–5; pin neste card; não reentrevista; não reabre #817/#818/#837 como trabalho; não vendorar `@deepseek-ai/dsh*` / `pi-ai`.
- **Regressão:** E1–E12 same-ctx; F1 host-only sem `high`; F7 settlement; F5 `isError`; grill → `dsh_reasoning_effort_spawn` → cordis → `runGuard`; `guard.py` `decide()` sem needles novos.
- **Riscos operacionais:** envelope `UserMessage` + `summary` no notice; mock F7 vs untagged-admitido; `session/event` dois args vs `sessionHeaderOf`.
- **Superfície visual:** nenhuma. Prototype N/A.

---

## Critique (contrato r2 vs live)

`openspec validate --strict` verde. Prototype N/A justificado. Sem HTML. Sem `## Design Critique` pré-preenchido. Clone gate T5 passaria **e** os tokens `live_route`/`surface` agora parseiam. Pin origin correcto (`v1.1.8` ocupado, `v1.1.9` livre). `files_g_design` True.

**P1-1 fechado no texto.** O pacote deixou de vender `tools/execute` throw + `Agent.inject()` como o erro que o pai lê no incidente continuable. F7 é o golden do aceite 3/5 nesse seam. F5 ficou foreground `isError`. Aceite 2 ficou D2+F8 (segundo `agent/request`), não rewrite de `send_message` execute.

**P1-2 fechado no texto.** `session/event` leva `{ global: true }` em D4/task 2.2/spec; F7 negativa sem global está escrita. Live confirma que global é load-bearing para fiber tagged (o mesmo predicado Cordis).

**P0 de API inventada: não.** `followup`/`steer` são métodos do Agent live, não do plugin host.

P1 novo de aceite vs live: **não**. Residuais de envelope/mock = P2.

---

## Findings

### P0

*(nenhum aberto)*

### P1

*(nenhum aberto — P1-1 e P1-2 do r1 fechados no pacote r2; hunt de API / UI none / F7-throw / followup-steer-live não eleva P1 novo)*

### P2

- **Envelope `UserMessage` + `summary` no notice.** Live `Agent.followup`/`steer` exigem `UserMessage` (`id`, `role: "user"`, `content[]`, `source`). `form: "notice"` exige `summary: string` (`CONTEXT_SUMMARY_MAX_CHARS` 120). `dsh-tool-jobs` usa `createUserMessage` (em `@deepseek-ai/dsh-llm`, que este card MUST NOT importar). Task 1.3 devolve **texto**; task 2.4 manda esse texto por `parent.followup`/`steer` e pina `source` **sem** `summary`. F7 pode verde se o mock aceitar uma string. Apply MUST mint à mão `{ id, role, content: [{type:"text", text}], source: { kind:"plugin", plugin, form:"notice", summary } }` — sem `import` dsh. Não reabre P1-1 (o veículo está certo).

- **F7 negativa vs mock 3.1 untagged-admitido.** Task 3.1 pina `scopeTarget` live (untagged admitido; tagged só key/ancestral; `global` bypass). Guard fiber untagged **receberia** `session/event` sem global. A AND «host sem global MUST NOT passar» só é falsa no mock live-accurate se o host da negativa estiver **tagged**. Apply MUST tagged o host no caso negativo (ou o F7 não tranca o `{ global: true }`). Plugin 2.2 mesmo assim MUST passar global.

- **`session/event` é `(session, event)`, não um payload com `header`.** Live: `event.type === "turn/end"`; `event.data.reason.kind === "error"`; `event.data.reason.error.message`; `session.id` (filho); `session.header.parentSession` (pai). `sessionHeaderOf` da lib actual lê `payload.agent.session.header` — **não** casa com o primeiro arg. Reutilizar esse helper no handler 2.2 deixa `parent` `undefined` no live e F7 verde no mock com envelope `{ agent }`. Spec/task dizem `header.parentSession` sem os dois args.

- **`inject` do Guard permanece `["systemPrompt","skills"]`.** `ctx.get("agents")` é peek Cordis válido (não inventado); `dsh-file-reference-local` faz `inject = ["agents"]` + `ctx.agents`. Sem `agents` no inject, apply não espera o serviço; `?.get` falha fechado em silêncio. SHOULD listar `agents` no `inject` (ou documentar o peek). Não é P1: o get existe no ctx pai típico do `--patch`.

### P3

- `followup`/`steer` do plugin **duplica** o aviso `subagent-settled` do runtime (já aceite em Risks; wording verboso).
- `live_route` / `surface` agora na forma do regex T5 (P3 r1 de parse **fechado**).
- `agent/created` sync throw veta o filho — attach MUST NOT lançar (já tasked).
- Host listener #817 MAY ficar.
- Homologação `:3080` cwd canónico ≠ worktree; 3080 ≠ systemd; ≠ `./restart`.
- Change #817 ainda em `openspec/changes/` (não archive); este card MUST NOT a reabrir.
- `ctx.subagents.followup` ≠ `parent.followup` — o primeiro fala com o filho (`send_message`). Design não os mistura; Apply MUST NOT.

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
2. Runtime: `Agent.followup`/`steer`/`inject` **reais** (UserMessage); `notifySettlement` `subagent-settled`; `session/event` presence-only + `{ global: true }` load-bearing para tagged; `turn/end` `{ reason: { kind, error } }`.
3. Pacote r2 alinha D4/task 2.4/spec F7 com esse seam. F5 throw-only separado. F8 cobre aceite 2 no segundo request.
4. Envelope notice/`UserMessage` e arity `(session, event)` ficam P2 (não desmentem o veículo).
5. Clone gate / HTML / Design Critique / pin origin / UI none: limpos. `live_route`/`surface` agora parseiam.

---

## Disposition

Zero P0. Zero P1 aberto. P1-1 (settlement `subagent-settled` + F7 `next` sucede → `turn/end` global → `followup`/`steer`; `inject` não aceite) e P1-2 (`session/event` `{ global: true }`; sem global falha F7) **fechados no texto r2** e confirmados no runtime Agent/dsh-scope. `followup`/`steer` existem no Agent live; não existem como API do plugin host. UI none / Prototype N/A / T5 / F7-não-é-throw-mock / pin `v1.1.9` livre / F1 contra o #817 estão fechados. P2 = envelope `UserMessage`+`summary`, F7 negativa vs untagged, arity `(session, event)` vs `sessionHeaderOf`, `inject` sem `agents`. Sem polish visual. MUST NOT editar `design.md` daqui. P2 não bloqueia T5 desta crítica.

### Verdict

**PASS**
