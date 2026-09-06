# Snapshot — Assessment A r2 · card #839 `card-839-dsh-spawn-isolado`

- Card: #839 — dsh: spawn de filho isolado falha opaco e bloqueia Design/Apply/Review/QA
- Change: `card-839-dsh-spawn-isolado`
- Critic: Assessment A recritique (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested agent)
- Modelo: inherit
- UTC: 2026-09-05T03:35:39Z
- Round: 2 — P1 r1 MUST confirmar fechados ou reabrir: (1) continuable/`send_message` = execute sucede; 400 = settlement `subagent-settled` / `no closing message`; throw-only / inject NÃO é o veículo; (2) `session/event` presence-only filtra por tag; MUST `{ global: true }`
- Tuple (este isolado, medido `scripts/process-fsm/resolve.py` neste cwd): `q=None` `bound_card=839` `q_git=card-839-dsh-spawn-isolado`. `.grok/rules/process-fsm-page.md` ausente. Board Project 1 **Status=Design** (`PVTI_lAHOAAHtBM4BV8b2zg5iAXk`, GraphQL pontual). Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit/push. Não editar `design.md` / proposal / tasks / specs / HTML / `backend/` / `frontend/src/`.
- Board: Status **Design**. Issue OPEN `bug`. Comentário T1 REST `issuecomment-5548773005`: `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`
- Digest `design.md` **medido r2**: sha256 `ab009056f6fb06b90c20d427a678ce41d585db597019545f66ec78fd0955de32` · **2330** palavras (`str.split`) · 17324 bytes · 105 linhas. (r1 era `c8f26caac9…` / 1861 — o autor reescreveu D4/D5/tasks/spec.)
- `openspec validate card-839-dsh-spawn-isolado --type change --strict`: **valid**
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correcto)
- UI impact: **none** (harness/plugin dsh + goldens + pin; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*839*`; sem rewrite de `DESIGN.md`; sem pipeline Impeccable visual; Playwright desta coluna = N/A.
- Overlay live: `pin: v1.1.8`; `clients.dsh.auto: false`. Origin `oalansilva/covenant-flow` tags até `v1.1.8` (`v1.1.9` **livre**).
- `files_g_design` medido: **true**. Clone gate: `parse_ui_impact=none`; `parse_live_route=('N/A','harness-only; …')`; `parse_surface=new`; `requires_existing_clone=False`; `clone_gate_ok=True`. Tokens `live_route:` / `surface: new` agora na forma do helper (P3 r1 fechado).
- Tasks: **23** checkboxes (r1 tinha 21; r2 separou 2.3/2.4 e F7/F8 em 3.6).
- Plugin/lib live (pré-Apply, pin `v1.1.8`): sem `agent/created`, sem `session/event`, sem `tools/execute`, sem `attachAgentEffortGuards` / `formatChildRunFailure`; `collectFailureFacts` ainda `Object.keys`. Esperado.
- Method: issue #839 REST `GET /repos/oalansilva/crypto/issues/839` (não `gh issue view`); proposal / design D1–D6 + Apply contract / Risks; tasks 1–7; deltas `process-harness` + `covenant-flow`; plugin `.dsh/plugin/process-fsm-guard.js`; lib `dsh_plugin_lib.js`; goldens E3 wrap-as-outer (regressão); runtime npx `@deepseek-ai/dsh-*` (leitura, não vendorar): `dsh-scope` presence-only + `scopeTarget`, `installModelSelection`, `toStopReason`/`readResult`, `notifySettlement` `followup`/`steer`/`inject`, `send_message` execute, `tools/execute` `dispatchToolBody` → `toolErrorResult`, `Agent.followup`/`steer` exigem `UserMessage`, `MessageSourceMap.plugin` ∩ `ContextFormed`.

r1 snapshots lidos **só** para identificar os P1 (não copiar veredito): `.impeccable/critique/839-card-839-dsh-spawn-isolado-A.md` e `-B.md`.

---

## Surfaces lidas (r2)

| Superfície | Classificação |
| --- | --- |
| `openspec/changes/card-839-dsh-spawn-isolado/{proposal,design,tasks}.md` | lido (r2) |
| `openspec/changes/card-839-dsh-spawn-isolado/specs/{process-harness,covenant-flow}/spec.md` | lido (r2) |
| Issue #839 body + comentário T1 | lido (REST) |
| Runtime dsh (scope, settlement, send_message, execute, Agent inbox, session header) | lido (evidência de API; MUST NOT vendorar) |
| Plugin/lib pin `v1.1.8` + goldens E3 | lido (pré-Apply) |
| `frontend/src/**`, `backend/` de app, proto HTML 839 | **none** / ausente |
| GUI dsh `:3080` | **vendor** — homologação dump; não prototipar |

Nenhuma superfície de produto nova/alterada ficou sem classificação. Prototype N/A justificado.

---

## Re-check P1 r1 (obrigatório)

### P1-1 — continuable / `send_message`: execute sucede; 400 = settlement; throw-only / inject NÃO é o veículo — **FECHADO**

Contrato r2 (proposal What Changes; design Goals + D4 + Apply contract + Risks; task **2.3** foreground-only inspect `next()` `isError`; task **2.4** settlement separado; task **3.5** F5 throw-only MUST falhar; task **3.6** F7; spec «dsh parent sees stopReason and Diagnostic on the live settlement seam» + cenários Continuable / send_message):

- Start/`send_message` `next()` **MAY suceder** (`started subagent <id>` / `message queued`) **antes** do 400.
- O 400 live é `notifySettlement` `source.kind="subagent-settled"` / `Background subagent … failed before it finished` / `It left no closing message.`
- Veículo dos aceites 3/5 = **o mesmo que o settlement**: `parent.followup` idle / `parent.steer` busy; `inject` **só** se a linhagem já fecha. `Agent.inject()` **não** é o aceite.
- `send_message` **fora** do wrapper `tools/execute`. Aceite 2 = D2 no mesmo `agent.ctx` em **todo** turno (F8), não rewrite do execute.
- F5 = foreground `isError` inspect, **não** prova do incidente continuable. F7: settlement genérico sozinho MUST falhar; inject-only MUST falhar.

Live (reconfirmado neste r2, não vendorar):

- `dsh-tool-subagent-control` `send_message.execute` → `ctx.subagents.followup(...)` → `{ messageId }`; «returns no answer from the subagent».
- `dsh-subagent` `notifySettlement`: `this.ctx.agents.get(activation.parentSession)` + `parent.followup` idle / `parent.steer` busy / `parent.inject` só `closingTeardownFor`; source `{ kind: "subagent-settled", form: "notice", … }`.
- `dsh-tools` `dispatchToolBody` **catch** → `toolErrorResult` (`isError: true`, `content: [{ type: "text", text: "Error: …" }]`). Wrapper throw-only no `next()` **não dispara**.
- `Agent.inject()` existe e **não acorda** o driver (`runtime-types.d.ts`).

Não reabrir. O desenho r1 (inject no `execute` / F5 throw-only como aceite continuable) **não** está neste digest.

### P1-2 — `session/event` presence-only filtra por tag; MUST `{ global: true }` — **FECHADO**

Contrato r2 (proposal; D4(a); Risks; task **2.2**; F7 «host `session/event` sem `{ global: true }` MUST NOT passar»; spec: «presence-only still filters by carrier tag; a host listener without `global` SHALL NOT be the store»). Alternativa rejeitada em D4: `session/event` sem global.

Live (reconfirmado): `dsh-scope` `scopedSubjectResolvers["session/event"] = null` = presence-only (exige carrier; **não** casa subject). `scopeTarget`: untagged admitido; tagged só key/ancestral; `{ global: true }` bypassa o predicado. Dispatch: `collectSessionCallbacks` → `events.dispatch("emit", [carrier, "session/event", session, event])`. Sem global, fiber tagged do Guard **não** vê o `turn/end` do filho — o mesmo furo #817 no store.

Não reabrir.

---

## Brief (só neste snapshot)

Incidente live inalterado: pai `reasoningEffort: "high"` completa; filho isolado nasce, `turn/start`, header `{provider, model}` sem esforço, `turn/end` 400 `"reasoning.effort" does not support "none"`. Continuable devolve `started subagent <id>` antes do 400; `send_message` enfileira; turno 2 repete o 400; o pai lê settlement genérico ou, em foreground one-shot, `Error: subagent run failed` sem `Diagnostic`. Residual #817: sanitizer no `ctx` host; goldens E3 same-ctx wrap-as-outer.

Direction r2: (1) sanitizer no `agent.ctx` do filho via `agent/created` `{ global: true }` + `{ prepend: true }` (D2; F1–F3/F8); (2) `collectFailureFacts` lê `Error.message` não enumerável (D3; F4); (3) opacidade no seam **settlement** `followup`/`steer` após store `session/event` `{ global: true }` (D4; F7) + foreground inspect `isError` (F5); (4) pin = próximo patch livre após `v1.1.8`; (5) dump `:3080` DoD humano. Fora: vendor, #817/#818/#837 como trabalho, yaml/Σ, Auto dsh, produto UI.

Audience: operador do board no cliente dsh. Personas visuais Impeccable: **N/A**.

---

## Critique

### P0

(nenhum aberto)

D2 continua API live (`agent/created` + prepend/global no `agent.ctx`; `installModelSelection` inner sem prepend). D4 r2 assenta no `notifySettlement` live, não em API inventada.

### P1

(nenhum aberto — P1-1 e P1-2 r1 fechados no pacote OpenSpec r2; sem P1 novo que reabra o veículo ou o filtro)

### P2

- **P2 — `form: "notice"` sem `summary`.** Live `ContextFormed`: `{ form: "notice"; summary: string }`. `dsh-tool-jobs` / `notifySettlement` sempre passam `summary` (jobs via `boundContextSummary`). r2 D4/task 2.4 pinam `source = { kind: "plugin", plugin: "covenant-flow-process-fsm-guard", form: "notice" }` — `plugin`+`form` fecham o P2 r1 B de `kind` só, mas `summary` continua omitido. `createUserMessage` **não** valida em runtime (não throw); a linha colapsada do transcript fica incompleta. Disposition: uma linha `summary` ≤120 chars no source + F7 a exigir essa chave. Não reabre o veículo.

- **P2 — F7 não pina a forma live da mensagem nem o callback `(session, event)`.** `Agent.followup` / `Agent.steer` exigem `UserMessage`. `session/event` live é emit `(session, event)` (`session.id`, `session.header.parentSession`, `event.type === "turn/end"`, `event.data.reason.error`). Task 2.4 fala `header.parentSession` e «entregar `formatChildRunFailure` via `parent.followup`» — um mock que aceita `followup(string)` ou um payload único `{ header }` verdeia F7 e o observer live (throw contido em `invokeContainedSessionObservers`) deixa o pai só com o settlement genérico. Disposition: F7 MUST dispatch `(session, event)` e assertir `UserMessage` com `source.kind="plugin"` + texto Diagnostic; MUST NOT passar com string solta. Mesma classe de tightness do mock, **não** o P1 r1 (o veículo já é followup/steer).

- **P2 — F5 `content` string ≠ live `toolErrorResult`.** Live: `{ isError: true, content: [{ type: "text", text: "Error: …" }], error: { message } }`. Task 3.5 / spec Foreground usam `{ isError: true, content: "Error: subagent run failed" }`. Inspect `isError` (não throw) está certo; Apply que casar string exacta falha o foreground live. Disposition: F5 MUST aceitar blocks `content[].text` (e/ou `error.message`) com o headline; o incidente continuable continua a ser F7.

### P3

- Aviso duplicado (settlement genérico + linha Diagnostic): aceite em Risks.
- `attachAgentEffortGuards` MUST NOT lançar em `agent/created` (já em 1.1 / D2).
- Host listener #817 MAY ficar; aceite do `high` = attach.
- `dsh-llm-retry` no mesmo `agent.ctx`: prepend do nosso `request-error` (F4). Residual ordem de outros plugins.
- Homologação `:3080` cwd canónico ≠ worktree; 3080 ≠ systemd; ≠ `./restart`.
- Change #817 ainda em `openspec/changes/` (não archive); este card MUST NOT a reabrir.
- Aceite 3 do issue admite `Partial output`; Design pina `Diagnostic` (filhos morrem no step 1 sem tools — parcial vazio é o live).
- `notifySettlement` usa `sendWaking` à volta de followup/steer; o Design omite o wrapper. Residual de corrida se o driver se reformar entre o status e o send.
- Guard `inject` permanece `["systemPrompt","skills"]` (task 2.1); lookup `ctx.get("agents")` no handler (não no `apply`) é o caminho. MAY acrescentar `agents` ao inject no Apply sem mudar o aceite.
- Plugin/lib live ainda sem attach/store (pré-Apply).

---

## Escopo vs issue grelhado #839 (não reentrevista)

| Aceite / Entra | Design r2 | Tasks / spec | Nota |
| --- | --- | --- | --- |
| Sonda `PROBE_OK` bg+fg | Goals; homologação 7.1 | 7.1 dump Design-autor **OU** `PROBE_OK` | sanitizer D2 — ok |
| `send_message` devolve resultado, não `failed … no closing message` | Aceite 2 = D2 em **todo** turno (F8) | 2.4 fora do execute; 3.6 F8 | **P1-1 fechado** |
| Falha real → `stopReason` + `Diagnostic` (aceite 3) | D4 settlement `followup`/`steer` | F7 + F5 isError | **P1-1 fechado**; P2 tightness UserMessage/F5 blocks |
| Classe 400 nomeada (aceite 5) | `dsh_reasoning_effort_none` + fallback não re-spawn | 1.3 / F6 | ok |
| Residual #817 no **filho** | D1–D2 attach `agent.ctx` | F1–F3; host MAY | **não** rename |
| `session/event` `{ global: true }` | D4(a) / Risks | 2.2 / F7 | **P1-2 fechado** |
| #837 board / issue como trabalho | Non-Goals | 5.2 | ok |
| Sem vendor `toStopReason` / `@deepseek-ai/dsh*` | D4 alt. rejeitada | 1.1 / 1.4 | ok |
| `collectFailureFacts` Error não enumerável | D3; **não** aceite do header | 1.2 / F4 | ok |
| Pin próximo patch após `v1.1.8`; não cravar `v1.1.9` | D6 | 3.7 / 4.1 | origin: `v1.1.8` topo; `v1.1.9` livre |
| yaml/Σ / Auto dsh / UI produto / #817/#818 trabalho | Non-Goals | 1.4 / 2.5 / 5.2 / 6.x | ok |
| Clone gate isento UI none | `live_route: N/A` / `surface: new` | — | T5 `files_g_design` true; parse r2 **ok** |
| Dump `:3080` DoD humano | Apply contract | 7.1 MUST NOT residual | ok |

Não entra (e não foi alargado): isolamento; pai escreve artefacto; `submeter_design` sem crítica; vendor runtime; perfil `~/.dsh/settings.yaml`; trocar modelo; `process-fsm.yaml`; `guard.py` `decide()`; Auto dsh; `backend/` / `frontend/src/`; 3080 systemd; reabrir #817/#818/#837.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. Browser gate: **N/A (no UI)**.
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica. Este crítico MUST NOT editar `design.md`.
- FSM yaml: sem task de estado/evento. T1/T7 Alan; T5 parent. Dual-write T0–T17 **proibido** no pacote.
- Product UI: zero `frontend/src/` / `backend/` de app no Apply contract.
- Auto dsh: overlay live `false`; specs MUST NOT reivindicar; pin não injeta a chave.
- `CLIENT_KEYS` / `SCHEMA_MAJOR` inalterados.
- Vendor `@deepseek-ai/dsh*` / `pi-ai`: proibido; leitura de runtime só nesta crítica.

---

## Trace

1. Issue #839 REST: 5 aceites; continuable `started subagent <id>` antes do 400; `send_message` turno 2 = mesmo 400; Diagnostic no `turn/end` do filho.
2. r1 A/B P1: veículo throw/inject vs settlement; `session/event` sem global.
3. r2 design D4/D5 + tasks 2.2–2.4 / 3.5–3.6 + spec settlement seam — fecham esses P1.
4. Runtime reconfirmado: `notifySettlement` followup/steer; `session/event` presence-only + tag filter; `dispatchToolBody` isError; `Agent.followup(UserMessage)`.
5. Clone gate / HTML / Design Critique / pin origin: limpos neste digest. Plugin live ainda #817 (pré-Apply).

---

## Disposition

- P0: (nenhum).
- P1 r1-1 e r1-2: **fechados** no pacote OpenSpec r2 (settlement `subagent-settled` + `session/event` `{ global: true }` + F7/F8; throw-only / inject não são o aceite). Não reabrir.
- P1 novo: (nenhum).
- P2: `summary` no `form: "notice"`; F7 pin `(session, event)` + `UserMessage`; F5 content blocks. **accepted-residual** — tightness de Apply/golden, não o veículo.
- P3: aviso duplicado, Partial output, sendWaking, inject sem `agents`, dump `:3080`, #817 não-archive. **accepted-residual**.
- Prototype N/A justificado. UI classificada. T5 `files_g_design` true. Pin não cravado. `collectFailureFacts` não substitui o sanitizer.

Pai: P0/P1 desta crítica = zero. MUST NOT editar `design.md` daqui. MUST NOT `process_event`. Sem polish neste transcript.

---

## Verdict

**PASS** (zero P0/P1 abertos; P1 r1-1 e r1-2 fechados; P2/P3 accepted-residual; Prototype N/A justificado; UI impact none classificado; crítica isolada Assessment A r2; snapshot não vazio; digest `design.md` `ab009056f6…` / 2330)

## Snapshot

`.impeccable/critique/839-card-839-dsh-spawn-isolado-A-r2.md`
