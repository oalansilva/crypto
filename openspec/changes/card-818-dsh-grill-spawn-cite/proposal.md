## Why

No dsh, o primeiro spawn do Design-autor (e o mesmo furo espera Apply e review) cai no deny `dsh_grill_spawn` só porque o briefing cita o ritual de grelha já fechado. A sessão `session-679a762b` (#790, turno 2) bloqueou um filho que **não** ia grelhar; o retry sem a palavra passou. O modelo não pode aprender a omitir o ritual no briefing, nem a grelhar no filho (proibido no dsh). Card [#818](https://github.com/oalansilva/crypto/issues/818).

## What Changes

- No dsh, o deny de spawn grelha distingue **papel** (trabalho = grelhar/afiar a história) de **citação** (facto já fechado: DoD no body, fronteira vazia, não reentrevistar).
- Design-autor isolado cujo briefing cita `grill-card fronteira vazia` (ou o DoD grelhado) **passa** este deny. O Guard normal ainda pode recusar por outro motivo.
- Apply e reviewer isolados que citam o DoD grelhado **passam** este deny.
- Spawn cujo trabalho é grelhar (description `grill-card 701`, prompt «Please run Grill-Card», «grelha a história», skill grill) **continua deny**. Contrato #786 não reabre: no dsh a grelha corre no root; MUST NOT spawnar filho grill.
- Goldens dos dois lados: citação allow (novo); papel deny (G1 do #786 permanece). G2/G6/G10 de papel permanecem deny.
- O Guard Python continua **sem** este matcher (`decide()` inalterado; senão o OpenCode passa a deny Task com o mesmo texto).
- Canal produto `oalansilva/covenant-flow` + pin no Cripto (como #786). Tag = a deste card **após** `gh api` tags **e** rebase no tip existente (irmão #817 disputa `v1.1.7` no mesmo nucleus). Pin-tests sobem para essa tag, não `v1.1.7` no vácuo.
- Classificação: change, frente Operação, P0. `UI impact: none`. Sem **BREAKING** de produto CriptoFarol.

## Capabilities

### New Capabilities

- (nenhuma) — o deny grill-shaped já vive em `process-harness`; este card aperta o match papel vs citação, não cria um quinto cliente nem spec de produto.

### Modified Capabilities

- `process-harness`: `isGrillShapedSpawn` deixa de tratar qualquer substring `grill-card` em `description`/`prompt`/JSON aninhado como papel. Papel (description com `grill-card`, prompt de trabalho grill sem marcador de citação) continua deny `dsh_grill_spawn`. Citação do ritual já fechado no briefing de Design/Apply/review passa este deny. Nested: só chaves `description`/`prompt` (recursivo); MUST NOT `JSON.stringify` o objecto inteiro. `guard.py` `decide()` continua sem o matcher. Cursor `Task` / Grok `spawn_subagent` / OpenCode `task` continuam fora deste deny.
- `covenant-flow`: pin patch deste card (após rebase no tip; live `v1.1.6`; #817 no mesmo nucleus) copia o helper JS + goldens **sem** clobber `dsh_reasoning_effort_spawn`; `SCHEMA_MAJOR` / `CLIENT_KEYS` inalterados; `clients.dsh.auto: false`. Sem linha nova no `AGENTS.md`. Sem trocar o texto do comentário canónico T1.

## Impact

- Altera (Apply, após Pronto para Dev): produto `oalansilva/covenant-flow` — rebase no tip/tag existente (#817), depois `scripts/process-fsm/dsh_plugin_lib.js` (`isGrillShapedSpawn` / haystacks), goldens `scripts/process-fsm/test_dsh_grill_spawn.py` (G12 citação allow; G1/G2/G6/G10 intactos), pin-tests para **esta** tag. Depois `implantar --pin` dessa tag no Cripto. Listener: grill primeiro, reason `dsh_grill_spawn`, sem `next()` — **não** bytes de `v1.1.6`; MUST NOT reverter #817.
- Não toca `backend/` / `frontend/src/`, `guard.py` `decide()`, `.cursor/hooks.json`, `dsh_stubs.py`, `grok_stubs.py`, `process-fsm.yaml`, `AGENTS.md`, texto canónico T1, skills Cursor/Grok de grill (spawn de grill nesses clientes continua permitido), Design do #790, recorte do #786 (root grelha; fail-closed de **papel**; matcher fora do Guard Python).
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A. Snapshot N/A.
- Origem: issue [#818](https://github.com/oalansilva/crypto/issues/818). Fronteira vazia. Pin Cripto live `v1.1.6`. Change #786 já arquivada em disco (`openspec/changes/archive/2026-09-03-card-786-dsh-grill-root/`); este card não a reabre.
