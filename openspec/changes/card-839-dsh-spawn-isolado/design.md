## Context

Card [#839](https://github.com/oalansilva/crypto/issues/839). Status observado: **Design**. Bound `q_git=card-839-dsh-spawn-isolado`. Relacionado e **não** reaberto como trabalho: #817 (Homologado, pin live `v1.1.8`; sanitizer/retry que não ganhou no filho), #818. #837 continua em Design à espera do spawn — este card não o corrige no board.

Overlay Cripto `.covenant-flow/overlay.yaml`: `pin: v1.1.8`, `clients.dsh.auto: false`. Plugin live `.dsh/plugin/process-fsm-guard.js`: `inject = ["systemPrompt","skills"]`; `ctx.on("agent/request", sanitize após next())` + `agent/request-error` retry + gate `dsh_reasoning_effort_spawn`. Runtime live `@deepseek-ai/dsh-agent` `installModelSelection` (após `next()`, apaga esforço herdado se a selecção não traz esforço); `dsh-agent-loop` `buildRequest`; adapter `pi-ai` openai-responses `thinkingLevelMap.off ?? "none"` (`off: null` no perfil **omite** a chave; ausência ⇒ `"none"`). Driver `dsh-subagent-in-process-driver` `toStopReason` mapeia só `kind` → `"error"` e `readResult` **não** copia a mensagem para `diagnostic`. `dsh-tool-subagent` `stopReasonError` → `"subagent run failed"`; `withDiagnosticAndPartialText` já formata `Diagnostic:` **se** `result.diagnostic` existir. `dsh-scope`: `agent/request` / `agent/request-error` scoped to agent; `session/event` e `subagent/start|end` resolver `null` = **presence-only** (exige carrier; o predicado de tag **ainda filtra** — não é “sempre chega”). Continuable `notifySettlement`: `followup` se pai idle, `steer` se busy, `inject` **só** se a linhagem do pai já fecha; `source.kind="subagent-settled"`. `tools/execute` `next()` devolve `isError` (não throw). `send_message` `execute` só confirma entrega.

Factos live (cwd `canonical_paths.dev`, GUI `http://127.0.0.1:3080`, modelo `muse-spark-1.3-contributor-free` / provider `opencodealan`):

- Pais `session-4f25ae42…` e `session-1b11df11…`: `request/header.config` traz `reasoningEffort: "high"` e completam.
- Filhos `2aba21aa`, `c2f3f1a7`, `ddaa7f25`, `b6299032`, `e8a4a479`: `subagent/descriptor` só `agentProvider`+`agentModel` (continuable) ou nem isso (one-shot probe); `turn/start`; **um** step; `request/header.config` = `{provider, model}` **sem** esforço; `turn/end` 400 `INVALID_REQUEST` `"reasoning.effort" does not support "none"`. Retry do #817 **não** disparou.
- Continuable: `execute` de start **sucede** (`started subagent <id>`) **antes** do 400; `job_list` vazio é esperado. O 400 chega **depois** como settlement `Background subagent … failed before it finished` / `It left no closing message.` (`source.kind="subagent-settled"`). `send_message` `execute` sucede (`message queued`); o turno 2 (`c2f3f1a7` / `b6299032`) é outro `agent/request` com o mesmo config partido, de novo settlement — **não** throw `subagent run failed`.

Causa já fechada no issue (2026-09-05): não é rejeição a child runs, nem infra, nem a tarefa. Residual do #817: o listener host fica inner ao strip **ou** o evento agent-scoped do filho não entra no waterfall do `ctx` do plugin. Goldens E3–E8 testam um único mock `apply(ctx)` (strip **depois** host, same-ctx); **não** o `agentCtx` isolado.

**UI impact: none.** Harness/plugin/docs de processo. Nenhuma rota, shell, componente ou copy de produto.

## Goals / Non-Goals

**Goals:**

- Sonda `PROBE_OK` em background e foreground MUST completar. `send_message` no mesmo filho MUST devolver resultado (aceite 2 = D2 no **mesmo** `agent.ctx` em **todo** turno; sem isso o turno 2 reenvia config partido e o pai só vê o settlement `no closing message`).
- Pedido do filho isolado MUST sair com esforço aceite (`high` se ausente/recusado; keep se já ∈ {minimal,low,medium,high}). MUST NOT enviar `none` nem omitir o campo (omitir = adapter `"none"`).
- Sanitizer MUST ganhar no **filho live**: mesmo `agentCtx` onde `installModelSelection` regista, *outer* ao strip. O desenho #817 (só host `apply(ctx)`, `inject=["systemPrompt","skills"]`) é regressão, não o aceite.
- Falha real MUST chegar ao pai no seam que o pai **lê**: settlement `subagent-settled` (`followup`/`steer`), não throw de `tools/execute`. Texto com `stopReason` + `Diagnostic:` (do `turn/end`) + classe `dsh_reasoning_effort_none`. `Agent.inject()` **não** é esse veículo.
- Pin = próximo patch livre após `v1.1.8`. Dump autenticado `:3080` (DoD humano). Goldens F1–F8 no furo isolado (F7 = settlement; F5 ≠ incidente continuable).

**Non-Goals:**

- Mudar o contrato de isolamento; pai escrever artefato de filho; `submeter_design` sem crítica; bypass de coluna.
- Corrigir produto #837 neste card. Reabrir #817 / #818 como trabalho.
- Vendorar `@deepseek-ai/dsh*` / `pi-ai`. Editar `~/.dsh/settings.yaml`. Trocar o modelo da sessão.
- `process-fsm.yaml` / Σ / colunas. `guard.py` `decide()` com needles. `AGENTS.md` a crescer. Auto dsh. Produto `backend/` / `frontend/src/`. Porta 3080 em systemd / `environments.dev.services`.

## Decisions

1. **Canal = pele `covenant-flow` no `agentCtx` do agente, não o host `apply(ctx)` sozinho.**  
   `installModelSelection` corre em `agent.ctx` no setup (api-proxy `installSelection`, **depois** de `next()`, apaga esforço se `selected.reasoningEffort` está ausente). O plugin host regista no fiber do `--patch` com `inject=["systemPrompt","skills"]`. Live: header do filho sem `high` + um único step ⇒ o waterfall do filho **não** aplicou o sanitizer (listener ausente no `agentCtx`, ou inner ao strip). Alternativa rejeitada: repetir D4 do #817. Alternativa rejeitada: perfil `off: null` (já omite a chave; adapter envia `"none"`). Alternativa rejeitada: vendorar o runtime.

2. **Attach por `agent/created` `{ global: true }` + `prepend: true` no `agent.ctx`.**  
   `agent/created` dispara **depois** do setup (`installModelSelection` já está no mesmo `agent.ctx`). Registar depois sem `prepend` fica *inner*: o strip pós-`next()` apaga o `high`. `prepend: true` unshift → *outer* ao strip mesmo registado depois. Forma: `agent.ctx.on("agent/request", async (p, next) => sanitizeReasoningEffort(await next()), { prepend: true })`. O mesmo attach instala `agent/request-error` **também** `{ prepend: true }` (1 retry; decide esta classe antes de `dsh-llm-retry`). Helper novo `attachAgentEffortGuards(agentCtx)` em `dsh_plugin_lib.js`; o `apply` do Guard chama-o a partir de `agent/created` **sem lançar** (`agent/created` sync throw veta a publicação do filho). `inject` MAY permanecer `["systemPrompt","skills"]` — o furo não se tapa mudando inject. Host `ctx.on("agent/request")` do #817 MAY ficar (idempotente se o evento chegar; inútil se não chegar) e **não** é o aceite. Alternativa rejeitada: só `{ global: true }` no host sem re-registar no `agent.ctx`. Alternativa rejeitada: sanitizar *antes* de `next()` no filho (o strip continua a ganhar se formos inner).

3. **`collectFailureFacts` MUST ler `Error.message` / `Error.code` não enumeráveis.**  
   `Object.keys` numa `Error` omite `message`. Se `finish.failure` for `Error`, `isReasoningEffortRejection` no #817 devolve false e o retry não dispara — cabe no «um único step». O classificador MUST incluir `message`/`code`/`status` próprios mesmo não enumeráveis, além do walk. Alternativa rejeitada: tratar isto como aceite único (não fecha o header sem `high`).

4. **Opacidade: o pai lê o settlement `subagent-settled`, não um throw de `tools/execute`.**  
   Live (Design-autor / `send_message`): `execute` de start e de `send_message` **sucedem**. O 400 chega **depois** como `notifySettlement` (`followup` idle / `steer` busy / `inject` **só** se a linhagem do pai já fecha) com `source.kind="subagent-settled"` e headline `Background subagent … failed before it finished` / `It left no closing message.` `tools/execute` `next()` no foreground devolve `isError` (não throw). `Agent.inject()` **não** acorda o pai nem reescreve esse notice — MUST NOT ser o veículo dos aceites 3/5. Sem vendorar `toStopReason` / `readResult` / `notifySettlement`, o plugin: (a) `ctx.on("session/event", handler, { global: true })` — presence-only **ainda filtra por tag**; sem `{ global: true }` é o mesmo furo #817 no store de `turn/end`. Guarda `reason.error` chaveado pelo session id do filho; o formatter copia **só** `reason.error.message` já no log, MUST NOT `JSON.stringify(failure)`. (b) **Aceite 2** = D2 no mesmo `agent.ctx` em **todo** turno (F8: segundo `agent/request` após followup ainda `high`). (c) **Aceites 3/5 no seam live:** quando o store vê `turn/end` desta classe, `parent = ctx.get("agents")?.get(header.parentSession)` e o plugin entrega `formatChildRunFailure` pelo **mesmo veículo que o settlement** (`parent.followup` se idle, `parent.steer` se busy; `inject` só se a linhagem já fecha). `source` = `{ kind: "plugin", plugin: "covenant-flow-process-fsm-guard", form: "notice" }`. O settlement genérico sozinho MUST falhar o golden F7. Classe `dsh_reasoning_effort_none`; uma linha de fallback no texto ao pai: não re-spawnar o mesmo preset (gate #817 `dsh_reasoning_effort_spawn`). (d) Foreground one-shot: `tools/execute` **inspecciona o result de `next()`** (`isError` / `Error: subagent run failed`) e reescreve o content — MUST NOT ser throw-only. `send_message` **não** entra neste wrapper como aceite (o `execute` dele sucede; o 400 é settlement). Alternativa rejeitada: inject como o erro que o pai vê. Alternativa rejeitada: F5 throw-only como prova do incidente continuable. Alternativa rejeitada: `session/event` sem `{ global: true }`.

5. **Goldens MUST falhar o desenho #817 no furo isolado e o throw-mock no settlement.**  
   Mock F* MUST ser **append-inner** por omissão e honrar `{ prepend: true }` / `{ global: true }` — MUST NOT reutilizar o wrap-as-outer E3 (`on(name, fn)` que ignora opts). Isolamento F1 = predicado estilo `scopeTarget` (untagged admitido; tagged só key/ancestral; `global` bypass), não um `EventEmitter` à parte que esconde o filtro. F1: host-only (#817) + strip no filho → **sem** `high`. F2: `apply(host)` + dispatch `agent/created` `{ agent: { ctx: childCtx } }` `{ global: true }` → attach `prepend` → `high` (MUST NOT verde só com `attachAgentEffortGuards(childCtx)` sem o created). F3: attach **sem** `prepend` após o strip → **sem** `high`. F4: `agent/request-error` prepended no `childCtx` com `Error` não enumerável → `{ kind: "retry" }`. F5: foreground `next()` **sucede** com `{ isError: true, content: "Error: subagent run failed" }` → result reescrito com `stopReason` + `Diagnostic:` + `dsh_reasoning_effort_none`; throw-only MUST falhar F5. F6: 401 / rate-limit / deny Guard **sem** essa classe. **F7 (P1-1):** start/`send_message` `next()` **sucede** → `session/event` `{ global: true }` vê `turn/end` 400 → pai recebe `followup`/`steer` com `stopReason` + `Diagnostic:` + `dsh_reasoning_effort_none`; settlement genérico sozinho MUST falhar; host `session/event` **sem** global MUST NOT fazer F7 passar. **F8:** segundo `agent/request` no mesmo filho continuable ainda `high`. E1–E12 regressão. MUST NOT verde só com E3/F5 throw. Sem GitHub.

6. **Pin = próximo patch livre após `v1.1.8`; #817/#818 não são trabalho.**  
   Origin conferido neste Design (2026-09-05): `v1.1.8` é a tag mais nova. Apply MUST `git ls-remote --tags` de novo e cravar o próximo patch livre (esperado `v1.1.9` se ainda livre; MUST NOT major; MUST NOT mover `v1.1.8`). Rebase no tip do produto para não reverter haystacks #817/#818 já pinados. `clients.dsh.auto: false`. `SCHEMA_MAJOR` 1. Alternativa rejeitada: cravar `v1.1.9` neste Design sem o check do Apply. Alternativa rejeitada: só patch no consumidor.

## Apply contract

- Ordem, só após `Status=Pronto para Dev` no **mesmo** chat `#839`, filho Apply (pai `iniciar_apply` antes do spawn). Zero produto UI. Design **não** aplica.
- (1) `attachAgentEffortGuards` (não lança; `agent/request` **e** `agent/request-error` `{ prepend: true }`) + `formatChildRunFailure` (só `reason.error.message`; sem `JSON.stringify(failure)`) + `collectFailureFacts` em `dsh_plugin_lib.js`; (2) Guard: `agent/created` `{ global: true }` chama o attach; `session/event` `{ global: true }` guarda `turn/end`; **depois** do `turn/end` entrega Diagnostic no pai via `followup`/`steer` (settlement; `inject` só se linhagem fecha); foreground `tools/execute` inspecciona `next()` `isError` (não throw-only; `send_message` **fora** deste wrapper); (3) goldens F1–F8 + E1–E12 regressão; mock F* append-inner; (4) check origin + tag = próximo patch livre após `v1.1.8` + rebase no tip; (5) `implantar --pin` no Cripto, overlay `pin` = essa tag, `clients.dsh.auto: false`.
- MUST NOT `import` `@deepseek-ai/dsh-subagent` / `pi-ai`. MUST NOT editar `guard.py`, `process-fsm.yaml`, `dsh_stubs.py`, `AGENTS.md`, `backend/`, `frontend/src/`, `~/.dsh/settings.yaml`. MUST NOT vendorar DeepSeek. Host listener #817 MAY permanecer; o aceite do `high` é o attach no `agentCtx`. `inject()` MUST NOT ser o aceite 3/5.
- Homologação (DoD humano, **não** substitui F1–F8; bloqueia Auto): dump autenticado da GUI dsh web `http://127.0.0.1:3080` de **um** spawn isolado (Design-autor **ou** sonda `PROBE_OK`) no mesmo tipo de modelo (testemunha `muse-spark-*`): filho `turn/start`, ≥1 tool **ou** mensagem `PROBE_OK`, fecho; **zero** 400 desta classe. Homologação ≠ `./restart`; 3080 ≠ systemd; cwd = `canonical_paths.dev`.

## Risks / Trade-offs

- [`agent/created` também scoped e o host não o vê] → `{ global: true }` + o filtro de `scopeTarget` admite listener untagged. F2 MUST dispatch `agent/created` via `apply(host)` (não só o helper). Residual: se um preset isolar o bus, Apply MUST usar `payload.agent.ctx`.
- [`session/event` presence-only sem `{ global: true }`] → o store de `turn/end` do filho pode não ver o evento (mesmo furo #817). Mitigação: `{ global: true }` + F7 (listener sem global MUST falhar).
- [Throw-only / inject como aceite 3/5] → o incidente é settlement `subagent-settled` + `execute` que sucede. Mitigação: F7; F5 é só foreground `isError`; `inject` residual (linhagem a fechar).
- [`followup`/`steer` duplica o aviso de settlement] → aceite P3: genérico do runtime **mais** a linha Diagnostic; melhor que silêncio.
- [`attachAgentEffortGuards` lança em `agent/created`] → veta a publicação do filho. Mitigação: attach MUST NOT throw (try/catch no created).
- [Mock F* wrap-as-outer E3 / `EventEmitter` separado] → F2/F3/F7 verdes sem prepend/global. Mitigação: mock append-inner + predicado `scopeTarget`.
- [Forçar `high` num modelo que recusa `high`] → outra classe, fora deste card (mesmo residual #817).
- [Store de `turn/end` perde-se no reload] → residual aceite; o preventivo (sanitize no `agentCtx`, F8) é o caminho feliz.
- [P2 rebase no tip #817/#818] → não é trabalho desses cards. Apply rebase.
- [Homologação `:3080`] → cwd canónico DEV ≠ worktree; 3080 ≠ systemd; ≠ `./restart`. Dump é Apply/homologação. Não bloqueia T14 se F* verdes; bloqueia Auto e o aceite humano.
- [`dsh-llm-retry` no mesmo `agent.ctx`] → o nosso `request-error` prepended decide esta classe antes. F4. Residual: ordem live de outros plugins no filho.

## Migration Plan

Aditivo sobre `v1.1.8`. Ordem Apply: (1) lib attach (não lança) + facts + formatter + F4/F5 `isError`/F6; (2) plugin `agent/created` + `session/event` `{ global: true }` + settlement `followup`/`steer` + F1–F3/F7/F8; (3) foreground `tools/execute` inspect `next()`; (4) E1–E12 regressão + G1 grill + write deny; (5) origin tags + rebase + tag próxima livre; (6) pin Cripto. Rollback = pin `v1.1.8`. Sem migration de banco. Sem rebuild frontend. Homologação = dump `:3080`, não `./restart`.

## Open Questions

Nenhuma bloqueante (causa fechada no issue). P1-1/P1-2 da crítica r1 fechados neste r2 (settlement `subagent-settled` + `session/event` `{ global: true }`). Residuais P2/P3: mock vs filtro Cordis (F1 pina predicado, não EventEmitter); rebase #817/#818; aviso duplicado; dump `:3080` ≠ worktree.

## UI impact

UI impact: none — harness/plugin/docs de processo. Zero rota, shell, componente ou copy de produto CriptoFarol. Nenhuma superfície visual nova ou alterada.

## live_route

live_route: N/A harness-only; no product route. Clone gate isento (sem HTML, sem catálogo).

## surface

surface: new

## Prototype

N/A — `UI impact: none`. Não há tela Cripto a prototipar; o aceite é o filho a sair com esforço aceite, a sonda `PROBE_OK` bg+fg, o `Diagnostic` no pai, e o dump autenticado `:3080`. Sem HTML. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A (não há UI de produto a exercitar). Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL de produto, viewport nem assert de UI. A evidência de aceite é o dump dsh `:3080` mais os goldens F1–F8 (e regressão E1–E12), não um protótipo HTML.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. Detector Impeccable da pele dsh permanece o de #782/#822; este card não o altera.

## Design Critique

- P0: nenhum
- P1: nenhum (r1 fechados no r2: settlement `subagent-settled` + F7 `followup`/`steer`; `session/event` `{ global: true }`. Throw-only / `inject` não é o aceite 3/5.)
- P2 (aceites): `form: "notice"` sem `summary`; F7 vs mock untagged; F5 `content` string ≠ blocks live; envelope `UserMessage`; `sessionHeaderOf` vs `(session, event)`; Guard `inject` sem `"agents"`; rebase pin #817/#818
- P3 (aceites): aviso duplicado settlement+Diagnostic; Partial output; dump `:3080` ≠ worktree; `ctx.subagents.followup` ≠ `parent.followup`
- Prototype: N/A — `UI impact: none` (pedido dsh + dump `:3080`; sem HTML)
- Snapshot: `.impeccable/critique/839-card-839-dsh-spawn-isolado-A-r2.md` e `.impeccable/critique/839-card-839-dsh-spawn-isolado-B-r2.md`
- Design Agent verdict: PASS
