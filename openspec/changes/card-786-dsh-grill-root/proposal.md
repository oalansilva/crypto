## Why

No dsh, grelha em Em Refinamento copia o ritual Cursor (`subagent` `grill-card`); o filho é `DELEGATED_CALLER` e **não** pode `ask_user_question`, e o `subagent` web é `continuable` (background por omissão). Sessão `5a6c8c5c` (pedido “refine o card 701”) fez 0× ask no root e no child `0be27c63`, reescreveu o body e postou o comentário canónico T1. #784 já entrega always-on (stub + catálogo, pin `v1.1.1`); a falha é o **loop da grelha** contra a lei do deepseek-harness: só o runtime root fala com o humano. Card [#786](https://github.com/oalansilva/crypto/issues/786).

## What Changes

- **Q1=A:** no dsh o **runtime root** executa `skill` `grill-card` + `grilling`, faz `gh issue edit` do body e chama `ask_user_question` (Qs fechadas: N≥2, recomendada primeiro com `(Recommended)`; Other não conta). **MUST NOT** `subagent` / `subagent_fork` cujo trabalho seja grelha — **nem** com `run_in_background: false`. Sem dump D5 filho→pai no dsh.
- **Q4=A:** lei dsh no **canónico** com **dois** headings. N2 via `_plain` (lowercase; whitespace; strip `*`/`**`/`_word_`; strip backticks; keep `_` em `ask_user_question`; fixtures **não** + RED contíguo em D10/4.6). Frases spawn/pai-host/D5/host-prohibition MUST viver **somente** sob `## Cliente: Cursor e Grok`. `## Precondição` só Status+id N (após `_plain` sem `filho`/`spawna`/`relaying`/`dump d5`/`ask_user_question`/`askuserquestion`/`não chama`). H2 Perguntas (host) **não** fica partilhado no topo. `## Cliente: dsh` após `_plain` tem substring **contígua** `root chama ask_user_question` e **não** tem `não chama ask_user_question` / `não chama a ferramenta do host`. Uma linha `Cliente dsh:` em covenant-flow. Rótulo de cliente, não “nunca spawnar”. Cursor/Grok continuam pai spawn isolado + dump D5 + host tool. Stubs `.dsh/skills/*` permanecem thin (`dsh_stubs.py` intacto, ≤8 linhas).
- **Q5=A:** `AGENTS.md` **não** cresce. Sem linha de grelha dsh no stub always-on.
- **Q6=A:** Guard dsh `tools/pre-execute` **deny** `subagent` e `subagent_fork` quando `description` **ou** `prompt` contém `grill-card` (case-insensitive), além do texto da skill. Deny no plugin `.dsh/plugin/process-fsm-guard.js` (e lib se preciso). **Não** no hook Cursor/Grok. **Não** regra nova em `guard.py` `decide()`. OpenCode `runGuard` em todo `tool.execute.before` e Cursor `preToolUse` (não faz match de `Task`) ficam fora. Deny grill-shaped **além** do write deny; listener **antes** de `registerProvider`; try/catch do provider não salta o deny. `isCordisRestricted` continua só `cordis_*`.
- **Q3=A:** needles / spec Cursor-Grok do #755 continuam verdes. Sem sessão live Cursor/Grok neste card. Sem editar `grok_stubs.py` nem nomear host tool em `.grok/skills/*`. Frontmatter `grill-card` ainda fala em spawn prompt.
- **Q2=A:** DoD humano = dump autenticado da GUI dsh web `http://127.0.0.1:3080` de **um turno** «refine/grelha o card N» (N em Em Refinamento, fronteira com decisão, plugin pinado, cwd = canonical DEV, preset `standard`) com `tool/call` `ask_user_question` no **root** **antes** do comentário canónico T1, e **sem** `subagent`/`subagent_fork` grill-shaped. Fixture `5a6c8c5c` = regressão negativa. Homologação ≠ `./restart`; 3080 ≠ systemd. Pytest goldens do deny **também** são exigidos no Apply (não substituem o dump).
- Fonte no produto `oalansilva/covenant-flow` tag **`v1.1.2`**; Cripto pin depois. Mesma ordem que #784. Sem vendorar `deepseek-harness`. Sem reabrir #608/#720/#773/#782/#784/#755. Sem `process-fsm.yaml` / Σ / colunas. Sem produto UI. Sem Auto dsh. Sem deny global de todo `subagent`.

## Capabilities

### New Capabilities

- (nenhuma) — grelha dsh no root é pele do quarto adapter já descrito em `process-harness`; este card fecha o loop da grelha, não um quinto cliente nem spec de produto.

### Modified Capabilities

- `grill-card`: no dsh o runtime root executa a skill, pergunta com `ask_user_question` e MUST NOT spawn `subagent`/`subagent_fork` grill-shaped; comentário canónico T1 só depois das respostas (ou fronteira só-fato). Cursor/Grok: pai spawn isolado + dump D5 + filho MUST NOT chamar host tool **inalterados** (#755).
- `process-harness`: plugin dsh `tools/pre-execute` deny grill-shaped `subagent`/`subagent_fork` (fail-closed nesse match; fail-open para subagent não-grelha). Write deny #782/#784 não regride. `guard.py` `decide()`, Cursor `preToolUse` e Grok hooks **não** ganham esta regra. Quarto cliente nomeado no ritual de grelha; sem dual-write T0–T17.
- `covenant-flow`: pin **`v1.1.2`** (patch após `v1.1.1`) copia plugin/lib + skills canónicas; `install.sh --pin` continua a copiar `.dsh/`; `SCHEMA_MAJOR` / `CLIENT_KEYS` inalterados; `clients.dsh.auto: false`.

## Impact

- Altera (Apply, após Pronto para Dev): produto `oalansilva/covenant-flow` (tag `v1.1.2`) — `.cursor/skills/grill-card/SKILL.md`, uma linha em `.cursor/skills/covenant-flow` secção Grill-card, `.dsh/plugin/process-fsm-guard.js` + `scripts/process-fsm/dsh_plugin_lib.js` (helper deny), goldens `test_grill_card.py` / `test_dsh_adapter.py`. Depois `implantar --pin v1.1.2` no Cripto.
- Não toca `backend/` / `frontend/src/` de produto, `process-fsm.yaml`, `guard.py` `decide()`, `.cursor/hooks.json` matcher, `grok_stubs.py`, `dsh_stubs.py`, `AGENTS.md` (substância/tamanho), stubs Grok/host tools, monorepo DeepSeek, Clara/Hermes.
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A. Snapshot N/A.
- Origem: issue #786. Homologação: dump autenticado `:3080` (Q2); não bloqueia T14 merge; bloqueia Auto dsh.
