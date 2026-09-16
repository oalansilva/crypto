## Why

Origem: [#955](https://github.com/oalansilva/crypto/issues/955). Gist = *superset* do cartão: a grelha decide a história; o Design **copia** Problema, História, Entra / não entra e Q1–Q3 para este pacote. Não é segunda entrevista. Q1=A, Q2=A, Q3=B congeladas. Q4=A (*espelho do como*, história só no GitHub) **substituída**.

## Problema

Alan paga em Em Refinamento mais tokens do que em Design: nos 17 últimos cards completados (a partir de #876), a grelha foi a etapa que mais escreveu (cerca de 29% do total, 40 sessões para 15 cards, 2,7 por card) e custou mais do que o Design inteiro (autor + crítico + protótipo) em 12 dos 14 cards que passaram pelas duas etapas. A grelha reescreve o body inteiro a cada rodada, produz seções que o Design volta a produzir (vocabulário, riscos, e depois o pacote publicado como «superset» do issue) e dispara até em bug com reprodução clara e em card kaizen com problema já escrito, embora a regra «card nítido pode T1 sem grill» já exista no runbook.

## História

Como operador do board (PO),
quero que a grelha em Em Refinamento só fixe o que **eu** decido — quem sofre, o que passa/falha, o que não entra — em uma rodada curta e escrevendo só o que mudou no body,
para que tudo o que o Design já gera (vocabulário, riscos, mecanismo, specs) deixe de ser tratado duas vezes e a coluna barata antes do T1 volte a ser barata.

## Entra

- As duas colunas ficam (Em Refinamento vs Design). O custo duplicado é trabalho do agente, não das colunas.
- DoD da grelha **neste card, depois de feito**, encolhe para 3 seções no body: Problema, História, Entra / não entra (critérios de aceite observáveis dentro de Entra). Vocabulário e Riscos deixam de ser exigidos em Em Refinamento; passam a viver no Design.
- **Q1=A:** uma passagem, no máximo 5 perguntas de produto. Filho devolve o delta do body, não o body inteiro.
- **Q2=A:** se o cartão já diz quem sofre e o que entra/não entra, o agente **não** pergunta; Alan vê o cartão escrito e prioriza. Pedido explícito para grelhar continua a correr (como neste #955).
- **Q3=B:** não há segunda passagem. O que a primeira passagem não fechou segue com o card para o Design (pode reaparecer como P0 de produto na crítica; aceite explícito).
- **Q4 substituída:** OpenSpec / Gist volta a ser pacote completo (*superset* do cartão). A grelha continua a ser o sítio onde a história se decide (não reentrevistar). O Design **copia** do body grelhado para o pacote: Problema, História, Entra / não entra, Q1–Q3. O *como* continua no `design.md`. T7 e Apply lêem o Gist como documento único.
- Entrega no produto covenant-flow e pin no Cripto pelo canal usual. UI impact: none.
- Medida de sucesso não é parser novo: vive no card de release seguinte, mesmo proxy (sessões de grelha por card e Em Refinamento vs Design). Números 1,5 / 10 cards são *como* no Design / release.

## Não entra

- Remover a coluna Em Refinamento, mover a entrevista para a coluna Design ou tornar o sítio do *como* porta de entrada da grelha.
- Mexer na máquina de estados, nas colunas ou em T1 (continua só Alan).
- Editar o vendor da entrevista (a skill primitiva de grelha).
- Segunda passagem da grelha (Q3=B).
- Grelhar sozinho um cartão que já diz quem sofre e o que entra/não entra (Q2=A).
- Reentrevistar ou inventar história nova no Design. O pacote copia do body grelhado (não parafraseia até perder Entra).
- Reescrever bodies já grelhados; reabrir #667, #755, #809 (tecto de linguagem, contrato de opções do host, «card nítido pode T1» como ideia — este card verifica o *quando*: body já com quem sofre + entra/não entra).
- Reduzir o Design: teto 1+1+1 (#854), clone da página viva (#819) e crítica continuam iguais.
- Código da aplicação (servidor e cliente web).
- Parser de usage do Cursor/Grok ou dashboard de tokens.
- Dual-write de skills no Cripto em vez de produto + pin.
- Pedir ao operador que conheça o nome ou o funcionamento da ferramenta do *como*.

## What Changes

- Adapter `grill-card` (não o vendor): DoD da grelha passa a 3 seções (Problema, História, Entra/não entra, critérios observáveis dentro de Entra). Vocabulário e Riscos deixam de ser exigidos em Em Refinamento. Uma passagem, no máximo 5 perguntas de produto. REST PATCH só reescreve seções que mudaram; o handoff lista o delta. Pedido explícito para grelhar continua.
- Skip nítido no pai: body que já diz quem sofre e o que entra/não entra → comentário exacto `card nítido; sem grill`; não spawna grelha. Needle e teste no runbook do pai.
- Sem segunda passagem: o que a primeira não fechou segue listado para o Design (pode voltar como P0 de produto na crítica).
- Coluna Design: `proposal.md` / Gist = *superset* do cartão (história copiada do body grelhado + *como*). Vocabulário e Riscos nascem no `design.md`. O gate `G_design` continua a exigir pacote OpenSpec + comentário no card. Skills `openspec-new-change` e `openspec-ff-change` passam a tratar o briefing do *issue* como as 3 seções (não as 6); o *pacote* traz essas 3 + Vocabulário/Riscos no `design.md`.
- Kaizen de release: o relatório passa a trazer sessões de grelha por card e a comparação Em Refinamento vs Design (proxy por transcript). Sem parser de usage Cursor/Grok e sem dashboard. Alvo numérico (1,5 / 10) fica no `design.md`.
- Entrega no produto `oalansilva/covenant-flow` + `implantar --pin` no Cripto. `UI impact: none`. Sem **BREAKING** de produto CriptoFarol. Sem coluna nova. Sem arrastar Status. Sem dual-write de lei em `.dsh/` / `.grok/` / `.opencode/`.

## Capabilities

### New Capabilities

- (nenhuma) — a porta `grill-card`, o runbook `covenant-flow` e o kaizen de release já existem.

### Modified Capabilities

- `grill-card`: DoD 3 seções; uma passagem com teto 5; delta do body; skip nítido; fronteira vazia = 3 seções + nenhuma decisão de operador em aberto; goldens no harness.
- `covenant-flow`: bloco Grill-card (disparo, skip nítido, delta); Design / `openspec-new` / `openspec-ff` deixam de exigir Vocabulário/Riscos no body; «Card primeiro» = Gist *superset* (história copiada + *como*); pin patch do produto.
- `cursor-harness`: Gist/OpenSpec = *superset* do issue; `G_design` continua a exigir pacote + comentário; Apply lê Gist + `openspec/changes/`, não o body do GitHub como spec paralela.
- `kaizen-continuous-improvement`: `/kaizen release` reporta sessões de grelha por card e Em Refinamento vs Design (proxy transcript).

## Impact

- Apply (após Pronto para Dev): produto `oalansilva/covenant-flow` — `.cursor/skills/grill-card/SKILL.md`, `.cursor/skills/covenant-flow/SKILL.md`, `.cursor/skills/openspec-new-change/SKILL.md`, `.cursor/skills/openspec-ff-change/SKILL.md`, `.cursor/skills/kaizen/SKILL.md`, goldens em `scripts/process-fsm/test_grill_card.py` (+ fixtures); tag patch; `implantar --pin` no Cripto.
- Peles `.grok` / `.dsh` / `.opencode` continuam stubs thin MUST Read (≤8 linhas); MUST NOT copiar a lei.
- Vendor `grilling` intocado. Máquina de estados / colunas / T1 / teto Design 1+1+1 / clone da página viva intocados. Não reabre #667 / #755 / #809. Não reescreve bodies já grelhados. Zero `backend/` / `frontend/src/`.
- `UI impact: none`. Prototype N/A.
- Origem: [#955](https://github.com/oalansilva/crypto/issues/955). Pin Cripto live `v1.1.15`.
