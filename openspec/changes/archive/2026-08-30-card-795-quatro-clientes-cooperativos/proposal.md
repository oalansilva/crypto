## Why

Alan opera quatro clientes com a mesma lei de 12 colunas, mas o Cursor é a única exceção no *claim* Auto (overlay Cripto `clients.cursor.auto: true` + stub «Auto permitido»). Grok, OpenCode e dsh já são cooperativos até ensaio deny. Quem sofre é Alan: dois jeitos de trabalhar sem diferença de Guard. Card [#795](https://github.com/oalansilva/crypto/issues/795).

## What Changes

- **Q1=A:** contrato yaml+stub cooperativo. Overlay Cripto `clients.cursor.auto: false` (grok/opencode/dsh continuam `false`). Cursor deixa de ser a exceção Auto.
- **Q2=A:** `render_agents()` **hardcode** quatro cooperativos — o stub **nunca** diz «Auto permitido» no Cursor. `clients.*.auto` permanece no schema yaml e **não** conduz o texto do stub.
- **Q3=A:** Auto da IDE/CLI Cursor (`approvalMode` / Run Everything) **fora de escopo**. Este card não toca config local.
- **Q4=A:** README do produto — bloco do estranho **neste** card, no mesmo tag/pin. Não reabre #787 como Apply.
- Tag **patch** do produto (não major; `SCHEMA_MAJOR` 1, `CLIENT_KEYS` três) + `implantar --pin` no Cripto, que regenera `AGENTS.md` a partir do novo `render_agents`.
- Cláusula «até ensaio deny» no stub continua **só** em Grok, OpenCode e dsh (Cursor é cooperativo por contrato, não por ensaio pendente).
- Specs MODIFIED neste card: `covenant-flow` (bloco Auto = Cursor `true`, herdado de #787) e `process-harness` (Always-on ainda SHALL «Cursor Auto is allowed»).
- Sem **BREAKING**. Sem pular colunas. Sem herdar Auto para Grok/OpenCode/dsh. Sem alterar Guard, T0–T17, `CLIENT_KEYS`, `SCHEMA_MAJOR`. Sem código de app do Cripto.

## Capabilities

### New Capabilities

- (nenhuma) — o quarto cliente e o README PT-BR já existem; este card só retira a exceção Auto do Cursor.

### Modified Capabilities

- `covenant-flow`: bloco do estranho no README deixa de afirmar que Auto é Cursor `clients.cursor.auto: true`; os quatro clientes são nomeados cooperativos; Auto **não** autoriza cruzar colunas; MUST NOT reivindicar Auto em Grok/OpenCode/dsh. Overlay Cripto grava `clients.cursor.auto: false`. Pin patch (não major) + `implantar --pin` regenera `AGENTS.md`. #787 não reabre como Apply.
- `process-harness`: Always-on `AGENTS.md` / `render_agents()` nomeia Cursor Agent, Grok Build, OpenCode e dsh; **não** contém «Auto permitido»; **não** afirma «Cursor Auto is allowed»; ensaio deny só em Grok, OpenCode e dsh; yaml `clients.*.auto` não interpola o stub.

## Impact

- Altera (Apply, após Pronto para Dev): produto `oalansilva/covenant-flow` — `scripts/process-fsm/overlay.py` `render_agents()`, README bloco **Clientes**, exemplo `--pin` da tag deste card; depois `implantar --pin` no Cripto (overlay `clients.cursor.auto: false`, `AGENTS.md` regenerado).
- Não toca `backend/` / `frontend/src/`, Guard, `process-fsm.yaml`, tabela T0–T17, `CLIENT_KEYS`, `SCHEMA_MAJOR`, `docs/crypto-overlay.md`, config local IDE/CLI Cursor, #787 como Apply, #784/#782 (peles).
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A. Snapshot N/A.
- Origem: issue #795. Facto live (pin `v1.1.4`): overlay ainda `clients.cursor.auto: true`; `render_agents()` ainda emite «Cursor Agent (Auto permitido)»; `validate_overlay` não lê o boolean `auto`.
