## Why

Alan sofre nas Qs de grelha: escolhe entre alternativas que só fazem sentido com identificadores do git, e «A» na recomendada ratifica desenho em vez de decidir produto — no Monitor tanto quanto num card de harness. O tecto de linguagem no adapter `grill-card` deixa o body como história negociável e o *como* no Design.

## What Changes

- **Q1=A:** o mesmo tecto em **todos** os cards em Em Refinamento — histórias de produto e cards de processo/harness. Qs e options em português de operador. Se a pergunta precisa de identificador do git (nome de função, path, flag yaml, evento de fluxo, hash) para ser inteligível, **não é Q** de Em Refinamento: facto → body; *como* → Riscos para Design, não option no cartão do host.
- **Q2=A:** Other vazio, silêncio e «não percebi» / «isto é técnico» **reclassificam** (facto no body ou *como* no Design). **Nunca** contam como aceite da opção recomendada. A linha Other do host (#755) é automática e não é alternativa listada.
- **Q3=A:** o comentário de handoff permanece a linha exacta já pinada: `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` Só muda o *quando* (tecto de operador, não árvore Matt inteira). Idempotente: já exacto → não duplica; texto canónico errado → edita/minimiza.
- Paragem do adapter: 6 seções DoD escritas **e** sem decisão de operador em aberto. A árvore de desenho completa continua no **Design**.
- Contrato de opções do host intacto (N≥2, todas as alternativas, recomendada primeiro — #755). T1 continua só Alan. Disparo «oferecer grill» continua a ser body sem as 6 seções; o tecto **não** obriga a re-grelhar um DoD já escrito.
- Entrega no produto `oalansilva/covenant-flow` e pin no Cripto (canal usual, tag patch). Spec delta `grill-card` + uma linha no bloco Grill-card de `covenant-flow`. Golden em `test_grill_card.py`. `UI impact: none`.
- Sem **BREAKING** de produto CriptoFarol. Sem coluna nova. Sem arrastar Status.

## Capabilities

### New Capabilities

- (nenhuma) — a porta `grill-card` já existe; este card acrescenta o tecto de linguagem no adapter.

### Modified Capabilities

- `grill-card`: tecto de linguagem em todo card em Em Refinamento; facto no body e *como* no Design; Other vazio / silêncio / «não percebi» reclassificam e nunca aceitam a recomendada; fronteira vazia = 6 seções + nenhuma decisão de operador em aberto (comentário canónico inalterado); golden fail/pass de dumps (scanner apertado: Qs de operador com `priorizar` / `acabada` / `20260830` passam); disparo «oferecer grill» permanece body sem as 6 seções.
- `covenant-flow`: o bloco Grill-card da skill nomeia o tecto (além da linha já existente de relay de options); pin patch do produto + `implantar --pin` no Cripto.

## Impact

- Altera (Apply, após Pronto para Dev): produto `oalansilva/covenant-flow` — `.cursor/skills/grill-card/SKILL.md` (adapter), uma frase no bloco Grill-card de `.cursor/skills/covenant-flow/SKILL.md`, goldens em `scripts/process-fsm/test_grill_card.py` (+ fixtures); depois `implantar --pin` no Cripto.
- Peles `.grok` / `.dsh` / `.opencode` de `grill-card` permanecem stubs thin MUST Read do canónico; **não** incham.
- Não toca o vendor `grilling`; não promove `/opsx:explore` a porta de Em Refinamento; não reabre #667 / #755 / #786; não reescreve bodies já grelhados (#795, #799, #801); não mexe na máquina de estados / colunas / T1; não instala skill de marketplace; não escreve `CONTEXT.md` / ADR / schema `grill-driven`; não toca `backend/` / `frontend/src/`.
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A. Snapshot N/A.
- Origem: issue [#809](https://github.com/oalansilva/crypto/issues/809). Q1=A, Q2=A, Q3=A congeladas. Pin Cripto live `v1.1.5`. Adapter live **sem** tecto.
