# Snapshot — Assessment A · card #839 `card-839-dsh-spawn-isolado`

- Card: #839 — dsh: spawn de filho isolado falha opaco e bloqueia Design/Apply/Review/QA
- Change: `card-839-dsh-spawn-isolado`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested agent)
- Modelo: inherit
- UTC: 2026-09-05T03:17:22Z
- Tuple (este isolado, medido `scripts/process-fsm/resolve.py` + `paging.py` neste cwd): `q=Design` `bound_card=839` `q_git=card-839-dsh-spawn-isolado`. `.grok/rules/process-fsm-page.md` ausente. Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit/push. Não editar `design.md` / proposal / tasks / specs / HTML / `backend/` / `frontend/src/`.
- Board: Status observado **Design** (prompt). Issue OPEN `bug`. Comentário T1 canónico `issuecomment-5548773005`: `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`
- Digest `design.md` **medido**: sha256 `c8f26caac9bbb9e2344da32aa1a1fe59056030334fe0fda780ee937cd77a301b` · **1861** palavras (`str.split`) · 13696 bytes · 102 linhas.
- `openspec validate card-839-dsh-spawn-isolado --type change --strict`: **valid**
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correcto)
- UI impact: **none** (harness/plugin dsh + goldens + pin; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*839*`; sem rewrite de `DESIGN.md`; sem pipeline Impeccable visual; Playwright desta coluna = N/A. Snapshot visual N/A no `design.md` (T7 visual). Este ficheiro é o snapshot git-tracked da crítica de processo.
- Overlay live: `pin: v1.1.8`; `clients.dsh.auto: false`. Origin `oalansilva/covenant-flow` tags até `v1.1.8` (`v1.1.9` **livre** neste instante).
- Residual #817: change **não** está em `openspec/changes/archive/2026-09-05-card-817-dsh-reasoning-effort/` (caminho do prompt); lido `openspec/changes/card-817-dsh-reasoning-effort/` (Homologado no issue; pin live `v1.1.8`).
- `files_g_design` medido neste change: **true** (`proposal.md` + `design.md` + `tasks.md` + `specs/process-harness/spec.md` + `specs/covenant-flow/spec.md`). Clone gate: `parse_ui_impact=none`; `parse_live_route=(None,'')`; `parse_surface=None`; `is_new_exempt=False`; `clone_gate_ok=True` via short-circuit `ui==none && !existing` (`design_clone_gate.py` L228–229). YAML T5 `guard: G_design` intocado.
- Method: issue #839 REST `GET /repos/oalansilva/crypto/issues/839` (não `gh issue view`); proposal / design D1–D6 + Apply contract / Risks; tasks 1–7; deltas `process-harness` + `covenant-flow`; plugin live `.dsh/plugin/process-fsm-guard.js`; lib `scripts/process-fsm/dsh_plugin_lib.js` (`collectFailureFacts` / `sanitizeReasoningEffort` / `isReasoningEffortRejection`); goldens E1–E12 `test_dsh_reasoning_effort.py` (mock `_waterfall_ctx_prelude` wrap-as-outer, `on(name, fn)` ignora opts); runtime npx `@deepseek-ai/dsh-*` (leitura, não vendorar): `dsh-scope` scoped-events, `installModelSelection`, `toStopReason`/`readResult`, `dsh-tool-subagent` `stopReasonError`/`withDiagnosticAndPartialText`, `notifySettlement`, `send_message` execute. Adversário = Apply TDD que verdeia **os asserts listados** (F1–F6 / E3 same-ctx / execute-throw F5) sem o inject no settlement continuable.

---

## Surfaces lidas

| Superfície | Classificação |
| --- | --- |
| `openspec/changes/card-839-dsh-spawn-isolado/{proposal,design,tasks}.md` | lido |
| `openspec/changes/card-839-dsh-spawn-isolado/specs/{process-harness,covenant-flow}/spec.md` | lido |
| Issue #839 body + comentário T1 | lido (REST) |
| `.dsh/plugin/process-fsm-guard.js` + `scripts/process-fsm/dsh_plugin_lib.js` | lido (o que o Design muda) |
| Residual #817 `openspec/changes/card-817-dsh-reasoning-effort/` (não o archive 2026-09-05 pedido) | lido |
| `.cursor/process-fsm.yaml` T5 + `files_g_design` / `design_clone_gate.py` | lido |
| Runtime dsh (`agent/created` scoped, `session/event` presence-only, `tools/execute` scoped ao `exec.agent`, `prepend`/`global` Cordis, `installModelSelection` no setup **antes** de `announce`/`agent/created`, `toStopReason` só `kind`, `send_message` não espera o turno, settlement `source.kind="subagent-settled"`) | lido (evidência de API; MUST NOT vendorar) |
| `frontend/src/**`, `backend/` de app, proto HTML 839 | **none** / ausente |
| GUI dsh `:3080` | **vendor** — homologação dump; não prototipar |
| Reason / `Diagnostic` / `dsh_reasoning_effort_none` | processo (string de erro, não ecrã Cripto) |

Nenhuma superfície de produto nova/alterada ficou sem classificação. `live_route` / `surface` no `design.md` estão em prosa de heading (regex do gate **não** casa — ver P3); T5 mesmo assim passa. Prototype N/A justificado: aceite = filho com esforço aceite + sonda `PROBE_OK` + `Diagnostic` no pai + dump `:3080`; sem HTML; sem `DESIGN.md`; Impeccable visual N/A.

---

## Brief (só neste snapshot)

Incidente live (cwd `canonical_paths.dev`, modelo `muse-spark-1.3-contributor-free`): pai completa com `reasoningEffort: "high"`; filho isolado nasce, `turn/start`, um step, header `{provider, model}` **sem** esforço, `turn/end` 400 `"reasoning.effort" does not support "none"`. Continuable devolve `started subagent <id>` **antes** do 400; `send_message` enfileira e o turno 2 repete o 400; o pai vê settlement genérico (`Background subagent … failed before it finished` / `It left no closing message`) ou, em foreground, `Error: subagent run failed`. #817 (pin `v1.1.8`) sanitiza no `ctx` do plugin host; goldens E3–E8 same-ctx; live do filho não ganhou.

Direction: (1) sanitizer no **`agent.ctx` do filho** via `agent/created` `{ global: true }` + `{ prepend: true }` (seam **diferente** do host `agent/request` do #817 — não é o mesmo desenho com nome novo); (2) `collectFailureFacts` lê `Error.message`/`code`/`status` não enumeráveis — aceite do **retry**, não do header; (3) opacidade sem vendorar `toStopReason`: store `session/event` + rewrite `tools/execute` + inject continuable; (4) pin = próximo patch livre após `v1.1.8` (Apply confere; Design **não** crava `v1.1.9`); (5) dump `:3080` DoD humano. Fora: vendor, #817/#818 como trabalho, #837 board, yaml/Σ, Auto dsh, produto UI.

Audience: operador do board no cliente dsh. Personas visuais Impeccable: **N/A**. Personas de processo: (1) pai Design-autor continuable; (2) sonda foreground `PROBE_OK`; (3) `send_message` no mesmo filho.

---

## Critique

### P0

(nenhum aberto)

D2 **não** é o #817 com nome novo. Live: `agent/request` é waterfall **no `agent.ctx`** (`dsh-scope` subject = `payload.agent`); o host `ctx.on("agent/request")` do #817 ou fica inner ao strip ou **não está** no bus do filho. `agent/created` é emit no registry **depois** do setup (`installModelSelection` já está no mesmo `agent.ctx`; api-proxy `installSelection` no `setup` pré-`announce`). `{ global: true }` + filtro `scopeTarget` (untagged admitido) é o padrão host para ver o filho; `{ prepend: true }` unshift → outer ao strip mesmo registado depois. Alternativa rejeitada no Design («só `{ global: true }` no host sem re-registar no `agent.ctx`») fecha o rename. Host listener #817 MAY ficar; aceite = attach.

### P1

- **P1 — inject continuable / `send_message` fora do `tools/execute`; F5 não cobre o caminho live; aceite 3/5 ainda pode ser só o settlement genérico.**  
  Runtime (não vendorar): `toStopReason` mapeia só `kind` → `"error"`; `readResult` **não** copia mensagem para `diagnostic`; foreground `stopReasonError` → `Error: subagent run failed` (`withDiagnosticAndPartialText` só se `result.diagnostic` existir). **Continuable live (Design-autor, factos do issue):** `execute` de `subagent` devolve `{ kind: "continuable", subagentId }` / texto `started subagent <id>` **com sucesso**, *antes* do 400. O 400 chega depois como `notifySettlement`: `source.kind="subagent-settled"`, headline `Background subagent <id> failed before it finished.` + `It left no closing message.` — **não** passa por throw/result de `tools/execute`. `send_message` (`dsh-tool-subagent-control`) `execute` faz `ctx.subagents.followup(...)` e devolve `{ messageId }` («returns no answer from the subagent»); o turno 2 que 400s é outra vez settlement, não throw `subagent run failed`.  
  O Design acerta o *mecanismo* em D4(c) (inject `source.kind="plugin"` com pai vivo) mas: (1) task 2.3 cola o inject no checkbox de `tools/execute` — Apply TDD pode injectar *depois* de `next()` do start/`send_message`, quando ainda **não** há `turn/end`; (2) spec process-harness manda o wrapper de `tools/execute` **reescrever** headlines `failed before it finished` / `no closing message` que no live **não estão** no execute — estão no aviso `subagent-settled`; (3) cenário spec `send_message` THEN «rather than only `subagent run failed`» é o headline **errado** para este seam; (4) F5 = store `turn/end` + **throw** `subagent run failed` (foreground one-shot). Zero golden: `next()` de start/`send_message` **sucede** → `session/event` `turn/end` 400 → pai recebe mensagem plugin com `stopReason` + `Diagnostic:` + `dsh_reasoning_effort_none` (e o settlement genérico sozinho MUST falhar). Sem isso, F5 verde e o pai live continua a ver só o aviso genérico — a mesma classe de furo #817 (golden no seam errado). `session/event` unscoped + store **é** necessário; **não basta**. Inject MUST disparar no `session/event` (ou `subagent/end`) quando o `turn/end` desta classe está no store, com `parent = ctx.agents.get(header.parentSession)` e `parent.inject` / `followup` se idle (padrão `dsh-tool-jobs` / `notifySettlement`), não dentro do `execute` do start.

### P2

- **P2 — contrato do mock `on(name, fn, opts)` não pinado; E3 wrap-as-outer.**  
  `_waterfall_ctx_prelude` em `test_dsh_reasoning_effort.py`: listener **novo** envolve o anterior (later = **outer**) e ignora `{ prepend, global }`. F1 em bus **distinto** (host `apply` ausente do waterfall do filho) **não** verde no E3 same-ctx — isto está bem pinado (task 3.1 / spec scenario Isolated child bus). F3 («sem prepend após o strip → sem `high`») é **inimplementável** nesse mock (sem prepend ainda seria outer → `high`); Apply é forçado a um mock append-inner + `prepend` unshift, **ou** a inverter F3. F2 pode verde por wrap-as-outer sem provar prepend. Disposition: o THEN de F3 é claro; falta pinar no Design/spec que o mock F* MUST ser append-inner por omissão e honrar `{ prepend: true }` — MUST NOT reutilizar o wrap E3.

- **P2 — F2 MAY chamar `attachAgentEffortGuards(childCtx)` sem `apply(host)` + dispatch `agent/created` `{ agent: { ctx: childCtx } }`.**  
  Decision 5 diz `import { apply }` + helper; task 3.2 é a seta `agent/created` → attach. Se F2 for só o helper, F1 ainda prova o furo host-only e 2.1 continua a ser o wiring, mas o golden **não** falha visível se `agent/created` não disparar o attach (o mitigação nomeada em Risks). Menos grave que o P1: `ctx.on("agent/created")` é o padrão live (`dsh-file-reference-local`, presets) e untagged+`global` casa com `scopeTarget`.

### P3

- **P3 — `live_route` / `surface` não parseiam o gate.**  
  `## live_route` + linha `N/A — harness-only…` ≠ `live_route: N/A …`. `surface: new (harness). …` ≠ `SURFACE_RE` (`new` tem de ser fim de linha). `is_new_exempt=False`. T5 mesmo assim **passa** (`ui=none && !existing`). Isenção **válida** por UI none; os tokens que o prompt pede como prova (`surface: new` / `live_route: N/A`) não estão na forma que o helper lê. Comparar #817 (`live_route: N/A harness-only` na mesma linha).

- **P3 — aceite 3 do issue admite `Partial output`; o Design só pina `Diagnostic`.** Filhos morrem no step 1 sem tools — parcial vazio é o live. `withDiagnosticAndPartialText` já formata parcial **se** houver output; este card não o reexpõe.

- **P3 — `agent/request-error` prepended só em Risks, não em task 1.1.** Task prepend só `agent/request`. Residual `dsh-llm-retry` aceite (retry ≠ aceite do header).

- **P3 — inject duplica o aviso de settlement.** Já aceite em Risks; wording verboso.

---

## Escopo vs issue grelhado #839 (não reentrevista)

| Aceite / Entra | Design | Tasks / spec | Nota |
| --- | --- | --- | --- |
| Sonda `PROBE_OK` bg+fg | Goals; homologação 7.1 | 7.1 dump Design-autor **OU** `PROBE_OK` | sanitizer D2 — ok |
| `send_message` devolve resultado, não `failed … no closing message` | Goals | 2.3 execute rewrite | **P1**: live não throw; é settlement |
| Falha real → `stopReason` + `Diagnostic` (aceite 3) | D4 | F5 throw + inject 2.3 | **P1** no seam continuable |
| Classe 400 nomeada (aceite 5) | D4 class token | F5/F6 | F5 só throw; F6 ok |
| Residual #817 no **filho** | D1–D2 attach `agent.ctx` | F1–F3; host MAY | **não** rename |
| #837 board / issue como trabalho | Non-Goals | 5.2 | ok (aceite 4 = consequência do spawn, não recorte de board) |
| Sem vendor `toStopReason` / `@deepseek-ai/dsh*` | D4 alt. rejeitada | 1.1 / 1.4 | ok |
| `collectFailureFacts` Error não enumerável | D3; **não** aceite do header | 1.2 / F4 | ok |
| Pin próximo patch após `v1.1.8`; não cravar `v1.1.9` | D6 | 3.6 / 4.1 | origin medido: `v1.1.8` topo; `v1.1.9` livre — Apply confere |
| yaml/Σ / Auto dsh / UI produto / #817/#818 trabalho | Non-Goals | 1.4 / 2.4 / 5.2 / 6.x | ok |
| Clone gate isento UI none | `surface: new` / `live_route` N/A / Prototype N/A | — | T5 `files_g_design` true; parse fields frouxos = P3 |
| Dump `:3080` DoD humano | Apply contract | 7.1 MUST NOT residual | ok |

Não entra (e não foi alargado): isolamento; pai escreve artefacto; `submeter_design` sem crítica; vendor runtime; perfil `~/.dsh/settings.yaml`; trocar modelo; `process-fsm.yaml`; `guard.py` `decide()`; Auto dsh; `backend/` / `frontend/src/`; 3080 systemd; reabrir #817/#818/#837.

---

## Disposition

- P0: (nenhum). D2 é attach no `agent.ctx` (created+prepend), não o host `agent/request` do #817.
- P1: inject/Diagnostic no caminho **continuable + `send_message` live** não está no seam que F5/`tools/execute` exercitam. **must-fix** — Design/spec/tasks MUST: (a) gatilho = `session/event` (ou `subagent/end`) **após** persistir `turn/end`, não o `next()` do start; (b) `parent = ctx.agents.get(parentSession)`; inject/followup se idle; (c) golden F7 (ou F5b): start/`send_message` `next()` **sucede** + `turn/end` 400 → mensagem plugin no pai com `stopReason` + `Diagnostic:` + `dsh_reasoning_effort_none`; settlement genérico sozinho MUST falhar; (d) rewrite `tools/execute` fica **foreground** `subagent run failed` (F5). Sem isto, aceite 3/5 falha no caminho que o issue mediu.
- P2 mock `on()` / F2 sem `apply`+created: **accepted-residual** só se o P1 fechar; senão Apply ainda pode verdear F* no mock errado. Preferível pinar o mock append-inner no r2.
- P3 parse `live_route`/`surface`, Partial output, request-error prepend, aviso duplicado: **accepted-residual**.
- Prototype N/A justificado. UI classificada. T5 `files_g_design` terá proposal+design+tasks+spec (medido). Pin não cravado. `collectFailureFacts` não substitui o sanitizer.

Pai: **não** `submeter_design` enquanto o P1 estiver aberto (mesmo que B PASS). MUST NOT editar `design.md` daqui. MUST NOT `process_event`. Sem polish neste transcript.

---

## Verdict

**BLOCKED** (P1 aberto: Diagnostic/inject continuable vs F5 execute-throw; zero P0; Prototype N/A justificado; UI impact none classificado; crítica isolada Assessment A; snapshot não vazio; digest `design.md` `c8f26caac9…` / 1861)

## Snapshot

`.impeccable/critique/839-card-839-dsh-spawn-isolado-A.md`
