## Context

Card [#817](https://github.com/oalansilva/crypto/issues/817). Status observado: **Design**. Bound `q_git=card-817-dsh-reasoning-effort`. Q1=A, Q2=A, Q3=A fechadas no issue; este Design não as reabre. Relacionado e **não** reaberto: #782 (adapter), #784 (always-on), #786 (grelha no root), #518 (relato de spawn vazio), #569 (reviewers), #790 (apply/SHA/PR).

Overlay Cripto `.covenant-flow/overlay.yaml`: `pin: v1.1.6`, `clients.dsh.auto: false`. Plugin live `.dsh/plugin/process-fsm-guard.js`: `inject = ["systemPrompt", "skills"]`; `tools/pre-execute` = grill-shaped deny → `isCordisRestricted` → `runGuard`. `subagent` não-grelha continua `next()` (#786). Runtime live `@deepseek-ai/dsh` `0.1.1-rc.2`. Perfil `~/.dsh/settings.yaml`: família muse-spark `reasoningEfforts.off: null` (omitir); `agent-default-model` `muse-spark-1.3-contributor-free` + `reasoningEffort: high`.

Factos live (sessão `http://127.0.0.1:3080/` / `session-679a762b-0a68-49fb-9381-3184f6219d7b`; preset `danger-full-access`; `delegationDepth` 1 nos filhos; `agentPreset` `standard`; modo `continuable`):

- Turno 9 root: `implemente` → `INVALID_REQUEST` 400 `"reasoning.effort" does not support "none"`.
- Turno 10 `implemente` de novo: header passou a trazer `reasoningEffort: high` e completou.
- Filhos Apply/review: descriptor só `agentProvider`+`agentModel` (1.2), **sem** esforço; 21 linhas; 0 `tool/call`. Retry 1/1 repetiu o mesmo 400 e ainda nasceram `diff-reviewer` + `code-reviewer` cadáveres.
- Filho Design `53aeed2b` (mesmo modelo 1.2, mesmo preset) completou mais cedo (726 linhas, 55 tools). A recusa **não** é “todo spawn muse-spark morre”.

Causa no runtime (leitura, **não** vendorar): `@deepseek-ai/dsh-agent` `installModelSelection` em `agent/request` **apaga** `reasoningEffort` herdado quando a selecção do filho não traz esforço (“An absent selected effort clears any inherited effort, restoring the selected model's provider/default behavior”). `prepareCall` **não** faz clamp/alias; valor não anunciado falha `UNSUPPORTED_REASONING_EFFORT` *antes* do I/O — o 400 live chegou ao fornecedor, logo `"none"` saiu no pedido HTTP. Cordis documenta `agent/request` (waterfall, devolve `LlmCallConfig`) e `agent/request-error` (`{ kind: 'retry' }` no mesmo agente). Plugin host já escuta eventos agent-scoped (`agent/turn-stopping` no detector #782). Envelope live `agent/request-error` = `{ agent, turn, step, provider, failure, retryPolicy, signal }`; `payload.provider` é o **LLM** (`opencodealan` no incidente), **nunca** `"spawn"`. `origin: "subagent"` / `delegationDepth` / `parentSession` vivem em `agent.session.header` (`delegationDepthOf` está em `dsh-subagent` — Apply MUST NOT importar esse pacote; lê o header). `payload.turn` é o turno do **agente que falhou** (filho isolado começa em `turn: 1`; root no incidente era turno 9).

**UI impact: none.** Harness/plugin/docs de processo. Nenhuma rota, shell, componente ou copy de produto.

## Goals / Non-Goals

**Goals:**

- Pedido ao modelo (root **e** filho isolado) MUST NOT enviar o valor de esforço que este modelo recusa (testemunha: `none` / esforço desligado). Q2=A: qualquer modelo da sessão, não só `muse-spark-*`.
- Q1=A: a mesma recusa MUST NOT matar o turno do root (`implemente` não acaba em `INVALID_REQUEST` desta classe).
- Caminho feliz: Apply isolado e o par reviewer isolado entram em `turn/start`, correm ≥1 ferramenta, deixam mensagem de fecho. Fallback no root **não** é o caminho feliz.
- Depois do primeiro 400 desta classe **num filho** no turno: MUST NOT spawnar mais filhos com o mesmo preset; `ERROR: subagent spawn failed/empty`; continuar no root com residual explícito. O retry 1/1 do #518 **não** se aplica a esta classe.
- Pin produto `v1.1.7` → Cripto. Goldens pytest do mapper + waterfall + gate de spawn. Dump autenticado `:3080` (Q3=A) — Design especifica; Apply/homologação executa.

**Non-Goals:**

- Trocar o modelo do chat sem pedido do Alan. Reabrir apply/SHA/PR do #790.
- Vendorar `deepseek-ai/deepseek-harness` (nem checkout npm). Auto dsh (`clients.dsh.auto` permanece `false`).
- Reabrir #782 / #784 / #786 / #518 / #569 como trabalho. Deny **global** de todo `subagent`.
- Mudar `process-fsm.yaml` / Σ / colunas. Produto `backend/` / `frontend/src/`. Dual-write Hermes / `~/.codex/skills/`.
- Porta 3080 em `environments.dev.services` / systemd. Tratar o dump como opcional. Recortar só `muse-spark-*`. Deixar o 400 do root fora.
- Editar `~/.dsh/settings.yaml` como canal de pin (já tem `off: null` + default `high` e **não** bastou).
- Alterar `guard.py` `decide()`, `.cursor/hooks.json`, `dsh_stubs.py`, `AGENTS.md`.

## Decisions

1. **O mapeamento vive na pele `covenant-flow`, não no perfil local nem no runtime vendorado.**  
   Helper `sanitizeReasoningEffort(config)` em `scripts/process-fsm/dsh_plugin_lib.js`, chamado de `.dsh/plugin/process-fsm-guard.js`. Perfil `~/.dsh/settings.yaml` já mapeia `off: null` e default `high`; turno 9 e filhos ainda enviaram `none` — o perfil **não** é o canal (não pina, não chega ao filho). Runtime `installModelSelection` é a alavanca da herança; **MUST NOT** vendorar nem patchar `@deepseek-ai/dsh*`. Alternativa rejeitada: “alinhar o perfil”. Alternativa rejeitada: issue upstream-only sem pele (Q1/Q3 exigem o turno e o dump no consumidor pinado).

2. **Forçar valor aceite `high`; não omitir; filhos herdam o aceite do root.**  
   Tokens recusados (case-insensitive, trim): `none`, `off`, string vazia, `null`. Valor aceite já presente ∈ {`minimal`,`low`,`medium`,`high`} → **keep**. Ausente (filho descriptor só provider+model, depois do strip de herança) **ou** token recusado → `reasoningEffort: "high"`. Testemunho: turno 10 com `high` completou; omitir é exactamente a política `off: null` que falhou; `installModelSelection` trata ausência como “volta o default do fornecedor”, que nesta sessão foi `none`. Nested `reasoning.effort` MUST sanitizar-se para o mesmo `high` e MUST NOT ficar `none` ao lado de `reasoningEffort`. Alternativa rejeitada: omitir o campo (Q2 *como*; perfil já omite). Alternativa rejeitada: filhos sem esforço “herdam por omissão” (o runtime **apaga** a herança).

3. **Detectar a classe por token observado + recusa observada, não por catálogo de família.**  
   Preventivo: todo `agent/request` (qualquer `provider`/`model` da sessão) passa em `sanitizeReasoningEffort` — Q2=A não é um allowlist `muse-spark-*`. Reactivo: `isReasoningEffortRejection(failure)` é verdadeiro quando o facto normalizado (mensagem / código / status) contém a recusa de esforço (`reasoning.effort` **ou** `reasoningEffort` **ou** `UNSUPPORTED_REASONING_EFFORT`) **e** um token desta classe (`none` / `off` / `does not support`) **ou** status/código `INVALID_REQUEST` / `400` **junto** com esses needles. MUST NOT classificar rate-limit, 401, nem deny do Guard. Alternativa rejeitada: catálogo hardcoded da família (Q2≠B). Alternativa rejeitada: esperar o 400 para só então mapear (o preventivo é o caminho feliz).

4. **`agent/request` sanitiza *depois* de `await next()`, para ganhar ao strip de herança.**  
   Listener no mesmo `apply(ctx)` do Guard (não um terceiro módulo; crash do detector continua noutro ficheiro). Forma:

   `ctx.on("agent/request", async (payload, next) => sanitizeReasoningEffort(await next()))`

   Inner fake nos goldens: um wrapper que faz o mesmo strip que `installModelSelection` (apaga `reasoningEffort` do `next()` se a selecção não traz esforço). O mock actual `on(name, fn) { events[name] = fn }` **overwrite** esconderia este furo — os goldens E* MUST usar waterfall que encadeia inner strip → sanitize. `inject` permanece `["systemPrompt", "skills"]` (evento runtime, não composição de prompt). Alternativa rejeitada: sanitizar antes de `next()` (model-selection apaga o `high` como “herdado”). Alternativa rejeitada: módulo plugin novo (dois módulos já separam fail-closed vs detector).

5. **Q1=A — `agent/request-error` faz um retry do *mesmo* agente; não é spawn novo.**  
   Se `isReasoningEffortRejection(failure)` e este agente (id de sessão do `payload.agent`, **não** `payload.turn` sozinho) ainda não consumiu o retry desta classe: devolver `{ kind: "retry" }` **sem** `next()`. O retry volta a `agent/request`, que já sanitiza para `high`. Segundo 400 desta classe no **mesmo** agente: `next()` (terminal para esse pedido). Root (`header.delegationDepth` 0, sem `origin: "subagent"`, sem `parentSession`) recupera o turno (`implemente` não morre no primeiro 400). Filho (ver D6) também MAY retry o próprio pedido (caminho feliz: o mesmo filho passa a ter tools). `payload.provider` é o LLM e MUST NOT decidir filho vs root. Isto **não** é o retry de spawn do #518. Alternativa rejeitada: deixar o root morrer e só consertar filhos. Alternativa rejeitada: retry ilimitado. Alternativa rejeitada: `payload.provider === "spawn"` (live nunca é `"spawn"`; no incidente é `opencodealan`).

6. **Primeiro 400 desta classe num filho fecha o gate de spawn visível ao root.**  
   Filho = `payload.agent.session.header.delegationDepth >= 1` **ou** `header.origin === "subagent"` **ou** `header.parentSession` presente. Apply MUST ler o header; MUST NOT `import` `@deepseek-ai/dsh-subagent`. `payload.provider` (LLM) **não** é o teste. `payload.turn` é o turno do agente que falhou (filho isolado = `1`; root no incidente = `9`) — **MUST NOT** ser a chave do gate: um `Map(payload.turn)` no filho **não** é visível ao `tools/pre-execute` do root (outro agente, outro turno). Flag = `Set` in-memory no plugin indexado por `header.parentSession` (fallback: session id do caller/root). `tools/pre-execute` do **root** consulta esse `Set` pela **sessão do agente que está a spawnar** (scope Cordis do caller / header da sessão root; a sessão root ∈ o conjunto porque é o `parentSession` gravado no 400 do filho) — **não** pelo `payload.turn` do filho. Com o gate fechado, `subagent` / `subagent_fork` (grelha ou não) devolve `{ kind: "deny", reason }` contendo `dsh_reasoning_effort_spawn` sem `next()`. Root 400 **não** fecha o gate (header sem parent / depth 0) — depois da recuperação o root MAY spawnar (caminho feliz). Ordem: (1) grill-shaped #786 (2) **este gate** (3) `isCordisRestricted` (4) `runGuard`. O root regista `ERROR: subagent spawn failed/empty` (texto #518) e continua a etapa no root com residual explícito. Uma linha no ramo dsh de `covenant-flow` (não no `AGENTS.md`): após 400 desta classe num filho, não spawnar o mesmo preset; não aplicar o retry 1/1 de spawn. Alternativa rejeitada: honrar o retry 1/1 do overlay nesta classe (incidente: repetiu o 400 e nasceu o par reviewer). Alternativa rejeitada: deny global permanente de `subagent`. Alternativa rejeitada: chave = `payload.turn` «turno do root no envelope» (falso live).

7. **Pin = próximo patch livre após check no origin; colisão nomeada com #818 (P2, não bloqueante).**  
   Overlay live `pin: v1.1.6`. Esperado `v1.1.7` se livre. Patch, não major (`SCHEMA_MAJOR` 1; `CLIENT_KEYS` inalterados; `clients.dsh.auto: false`). Irmão [#818](https://github.com/oalansilva/crypto/issues/818) (`card-818-dsh-grill-spawn-cite`, Status=Design) toca o **mesmo** `dsh_plugin_lib.js` + plugin Guard e também esperava `v1.1.7`. Isto **não** é P1. Apply MUST: (a) `git ls-remote --tags` no produto e cravar o próximo patch livre; (b) rebase/merge no tip do produto para os haystacks do #818 **não** serem revertidos; (c) `--pin` da tag mais nova MUST conter **ambos** os deltas se os dois tiverem landed. Teste pin sobe para essa tag. Alternativa rejeitada: só patch no consumidor sem tag de produto (o próximo `--pin` apagaria a pele). Alternativa rejeitada: mover `v1.1.6` ou major.

8. **Goldens pytest além do dump (Q3=A já exige o dump).**  
   Pytest em `scripts/process-fsm` (ficheiro novo `test_dsh_reasoning_effort.py` **ou** secção em `test_dsh_adapter.py`; MUST `import { apply }` do plugin para E3–E8, não só unitário do helper). Dump autenticado `:3080` **não** é opcional e **não** é substituído pelos goldens. Homologação ≠ `./restart`; 3080 ≠ systemd; cwd = `canonical_paths.dev`.

### Golden cases (pytest `scripts/process-fsm`, sem GitHub)

E1–E2 MAY ser unitário JS do helper. E3–E8 MUST `import { apply }` + waterfall `agent/request` / `agent/request-error` / `tools/pre-execute` (inner stripper estilo `installModelSelection`). E9–E11 regressão. E12 pin.

| # | Caso | Esperado |
| --- | --- | --- |
| E1 | `sanitizeReasoningEffort({ reasoningEffort: "none" })` e `"off"` (mixed-case) e `reasoning: { effort: "none" }` | `reasoningEffort === "high"`; nested `none` ausente |
| E2 | `sanitizeReasoningEffort({ reasoningEffort: "medium" })`; `{}` (ausente) | keep `medium`; ausente → `high` |
| E3 | `apply` + inner strip (apaga esforço do `next()`) + `agent/request` com config `high` herdado | retorno `reasoningEffort === "high"` (ganha ao strip) |
| E4 | `apply` + `agent/request` filho descriptor só `provider`+`model` | retorno traz `reasoningEffort: "high"` |
| E5 | `apply` + `agent/request-error` **root**: `turn: 9`, `provider: "opencodealan"`, `header.delegationDepth: 0`, sem `origin`/`parentSession`, 1ª failure desta classe | `{ kind: "retry" }`, `next` não chamado |
| E6 | 2ª `agent/request-error` desta classe no **mesmo** agente (mesmo session id; `turn` pode repetir 9) | `next()` chamado (não retry infinito) |
| E7 | `request-error` **filho** `turn: 1`, `provider: "opencodealan"`, `header.delegationDepth: 1`, `origin: "subagent"`, `parentSession: <rootSession>` → **depois** `tools/pre-execute` no **root** (`turn: 9` ≠ 1, outro agente, mesma `parentSession`/sessão caller) `subagent` Apply e `subagent` reviewer | ambos `{ kind: "deny" }`, reason `dsh_reasoning_effort_spawn`, `next` false. MUST NOT passar com `provider: "spawn"` nem com o mesmo `turn` nos dois lados |
| E8 | `request-error` **root** `turn: 9`, `provider: "opencodealan"`, depth 0, sem `parentSession` → `tools/pre-execute` no mesmo root `subagent` Apply (sem needle grill) | `next()` chamado (gate **não** fecha no root); grill-shaped continua deny #786 |
| E9 | G1 grill-shaped + D13 cordis + write deny #784 no mesmo `apply` | os três denies intactos; `registerProvider` throw não salta |
| E10 | `isReasoningEffortRejection` 401 / rate-limit / deny Guard / mensagem sem needles | false |
| E11 | `guard.py` fonte **sem** `reasoningEffort` / `dsh_reasoning_effort`; `process-fsm.yaml` / `dsh_stubs.py` / `AGENTS.md` inalterados nesta change | verdes |
| E12 | pin-test `implantar --pin` (quando `install.sh` existe) | espera o patch livre que Apply cravou (`v1.1.7` se origin estiver livre; P2 #818); `clients.dsh.auto: false` |

## Apply contract

- Ordem, só após `Status=Pronto para Dev` no **mesmo** chat `#817`, filho Apply (pai `iniciar_apply` antes do spawn). Zero produto UI. Design **não** aplica.
- (1) commit no produto `oalansilva/covenant-flow` tag = próximo patch livre após `git ls-remote --tags` (esperado `v1.1.7` se livre; MUST NOT major; MUST NOT mover `v1.1.6`); rebase no tip do produto por causa do irmão #818 (P2); (2) `implantar --pin` dessa tag no Cripto. Overlay `pin` = a tag; `clients.dsh.auto: false`. Se #818 já tiver landed, o `--pin` da tag mais nova MUST conter ambos os deltas.
- Helper `sanitizeReasoningEffort` + `isReasoningEffortRejection` + detector de filho (lê `agent.session.header`) **somente** em `dsh_plugin_lib.js`. Plugin Guard: `agent/request` (sanitize após `next()`), `agent/request-error` (1 retry mesmo agente; filho vs root pelo **header**, nunca `payload.provider`), `tools/pre-execute` gate `dsh_reasoning_effort_spawn` chaveado por `parentSession` / sessão do caller **depois** do grill-shaped e **antes** de `isCordisRestricted`. `guard.py` `decide()` MUST NOT ganhar needles (E11). MUST NOT `import` `@deepseek-ai/dsh-subagent`.
- Uma linha no ramo dsh de `.cursor/skills/covenant-flow/SKILL.md` (400 desta classe num filho → não spawnar o mesmo preset; residual #518 no root). Stubs `.dsh/skills/*` intactos (≤8). `AGENTS.md` não cresce.
- Goldens E1–E12. E3–E8 via `import { apply }` + waterfall (inner strip). G1–G9 #786 e D13/D16/D20 #784 passam. **Não** editar `guard.py`, `.cursor/hooks.json`, `dsh_stubs.py`, `process-fsm.yaml`, `backend/`, `frontend/src/`. **Não** vendorar DeepSeek. **Não** tratar dump como Done.
- Homologação (Q3=A, **obrigatória** para o aceite humano; não substitui T14 goldens; bloqueia Auto): dump autenticado da GUI dsh web `http://127.0.0.1:3080` de **um** spawn Apply **ou** reviewer isolado, mesmo tipo de modelo que recusa esforço desligado (testemunha `muse-spark-*`), plugin pinado, cwd = `canonical_paths.dev`, preset de sessão o da evidência (`danger-full-access` / `standard` como no incidente). O dump MUST mostrar: filho `turn/start`, ≥1 `tool/call`, mensagem de fecho; **zero** recusa desta classe nesse spawn. Homologação ≠ `./restart` de produto; 3080 ≠ systemd.

## Risks / Trade-offs

- [Host `ctx.on("agent/request")` ficar *inner* ao `installModelSelection`] → o strip apaga o `high`. Mitigação: D4 `await next()` no plugin **e** golden E3 com inner stripper; dump Q3 falha visível se a ordem live inverter. Residual: se o host plugin não receber o evento, Apply MUST registar no agente-scope que envolve a selecção — ainda pele, ainda sem vendorar.
- [Forçar `high` num modelo que recusa `high`] → outra classe, fora deste card. Recorte Q2=A é esforço **desligado**. Residual aceite.
- [Flag in-memory perde-se se o processo dsh recarregar a meio do turno] → residual aceite; o preventivo (sanitize) é o caminho feliz; o gate é cinto. Chave = `parentSession` (não `payload.turn` do filho) para o `tools/pre-execute` do root ver o Set.
- [P2 colisão de pin com #818] → irmão `card-818-dsh-grill-spawn-cite` (Status=Design) partilha `dsh_plugin_lib.js` + plugin e o mesmo hoped tag `v1.1.7`. Não bloqueia este Design. Apply rebase no tip do produto; tag = próximo patch livre; `--pin` da tag mais nova MUST incluir ambos os deltas se os dois tiverem landed. Sem isto um pin posterior reverte haystacks do outro card.
- [Deny de `subagent` após 400 filho também pega spawns “outro preset”] → grelha pediu mesmo preset; nesta sessão todos os filhos partilham preset. Residual: card futuro se misturar presets no mesmo turno.
- [Plugin omitido / `--patch` ausente] → 400 volta. Residual aceite (#782); DoD humano exige plugin pinado.
- [Homologação `:3080`] → cwd canónico DEV ≠ worktree do card; 3080 ≠ systemd; ≠ `./restart`. Dump é Apply/homologação, não Design. Não bloqueia T14 se E1–E12 verdes; bloqueia Auto e o aceite Q3.
- [Pin-test ainda `v1.1.6`] → Apply actualiza para `v1.1.7` ou o teste falha visível.
- [`dsh-llm-retry` também escuta `agent/request-error`] → o nosso listener MUST decidir esta classe **antes** de delegar; E5 afirma `{ kind: "retry" }` sem `next()`. Residual: ordem live de plugins; dump Q3.

## Migration Plan

Aditivo sobre `v1.1.6`. Ordem Apply: (1) helper JS E1/E2/E10; (2) plugin `agent/request` + E3/E4; (3) `agent/request-error` + gate spawn E5–E8 (E7 turns desiguais + `provider: "opencodealan"`); (4) linha dsh em covenant-flow; (5) E9/E11 regressão; (6) check origin + rebase no tip do produto (P2 #818) + tag = próximo patch livre; (7) pin Cripto + E12. Rollback = pin `v1.1.6`. Sem migration de banco. Sem rebuild frontend. Homologação = dump `:3080` (Q3=A), não `./restart`.

## Open Questions

Nenhuma bloqueante (Q1–Q3 = A). P1 r1 (envelope Cordis / chave do gate) fechado em D6 + E7/E8. Residuais não bloqueantes: ordem exacta host-vs-agent-scope do waterfall (E3 + dump); **P2** colisão de pin com #818 (`card-818-dsh-grill-spawn-cite`) — Apply rebase + próximo patch livre, não é P1.

## UI impact

UI impact: none
live_route: N/A harness-only; no product route. Clone gate isento (sem HTML, sem catálogo). Sem superfície visual de produto.

## Prototype

N/A — `UI impact: none`. Não há tela Cripto a prototipar; o aceite é o pedido dsh sem `reasoning.effort=none`, o filho isolado a trabalhar (≥1 tool + mensagem de fecho) e o dump autenticado `:3080`. Sem HTML. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A (não há UI de produto a exercitar). Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL de produto, viewport nem assert de UI. A evidência de aceite é o dump dsh `:3080` (Q3=A) mais os goldens E1–E12, não um protótipo HTML.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. Detector Impeccable da pele dsh permanece o de #782/#822; este card não o altera.

## Design Critique

- P0: nenhum
- P1: nenhum (P1 r1 envelope Cordis fechado: filho = `header.delegationDepth >= 1` ∨ `origin === "subagent"` ∨ `parentSession`; gate = `Set(parentSession)` visível ao root; E7 turnos desiguais + `provider: "opencodealan"`; MUST NOT `"spawn"`)
- P2 (aceites): pin #818 (nomeado; Apply rebase no tip); E3 só outer ao strip; herança `medium` vs ausente→`high`; `dsh-llm-retry`; proposal «400 no turno» vs D6 só filho; E1 sem `""`/`null`; E4 sem modelo fora muse-spark; E5/E9 gaps de golden; spawn paralelo
- P3 (aceites): `ToolExecution` live sem `turn`; OR `parentSession` em fork; `exec.agent?`; pin-tests ainda `v1.1.6` (pré-Apply)
- Prototype: N/A — `UI impact: none` (pedido dsh + dump `:3080`; sem HTML)
- Snapshot: `.impeccable/critique/817-card-817-dsh-reasoning-effort-A.md` e `.impeccable/critique/817-card-817-dsh-reasoning-effort-B.md`
- Design Agent verdict: PASS
