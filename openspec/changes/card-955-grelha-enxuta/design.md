## Context

Card [#955](https://github.com/oalansilva/crypto/issues/955). Briefing = issue grelhado (3 seções). Q1=A, Q2=A, Q3=B congeladas — este Design não as reabre. Q4=A (*espelho do como*) **substituída**: Gist = *superset* (história copiada do cartão + *como*). Texto integral no `proposal.md`; este Context aponta + resume. Vocabulário, riscos, mecanismo e contrato de Apply nascem aqui.

Resumo da história copiada: Alan paga mais tokens em Em Refinamento do que em Design (grelha ~29%, 2,7 sessões/card a partir de #876). A grelha encolhe para 3 seções, uma passagem (teto 5), skip nítido (Q2=A), sem segunda passagem (Q3=B). O pacote copia Problema / História / Entra; não reentrevista.

Factos live (worktree + pin Cripto **`v1.1.15`**):

- Adapter `.cursor/skills/grill-card/SKILL.md`: DoD vigente = 6 seções; disparo = Em Refinamento e body sem as 6; fronteira vazia = 6 + nenhuma decisão de operador; comentário canónico T1 inalterado. Tecto de linguagem #809 intacto. Vendor `.cursor/skills/grilling/SKILL.md` intacto.
- Runbook `## Grill-card`: disparo nas 6 seções; «cards nítidos podem T1 sem grill» existe como ideia (#809) sem needle/teste do *quando* (quem sofre + entra/não entra) e sem comentário `card nítido; sem grill`.
- `openspec-new-change` / `openspec-ff-change`: briefing = 6 seções (inclui Vocabulário, critérios, Riscos). `covenant-flow` «Card primeiro»: Gist como *superset* do issue. `G_design` (T5) mede ficheiros OpenSpec + clone-gate + comentário — isso fica.
- `/kaizen release` já lê `proxy modelo:`; ainda não reporta sessões de grelha por card nem Em Refinamento vs Design.
- Goldens: `scripts/process-fsm/test_grill_card.py` needleia `6 seções do DoD`. Canal v1 = copiar e commitar (`implantar --pin`). `SCHEMA_MAJOR` 1.

UI impact: none
live_route: N/A harness-only; no product route
surface: new

Mudança de processo/harness; nenhuma tela do produto CriptoFarol. Sem rota de catálogo emprestada.

**Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Vocabulário

- `Grelha enxuta`: 3 seções, 1 passagem, teto 5 perguntas, delta do body. Avoid: grelha de 6 seções; segunda passagem; árvore de desenho completa em Em Refinamento.
- `Card nítido`: o cartão já diz quem sofre e o que entra/não entra; o pai não spawna grelha; Alan prioriza (Q2=A). Avoid: grelhar por hábito.
- `Delta do body`: só as seções que mudaram nesta passagem; o REST PATCH reconstrói o body com o texto das seções intactas byte-idêntico. Avoid: reescrever o body inteiro a cada passagem.
- `História`: quem sofre, o que passa/falha, o que não entra. Decide-se na grelha (cartão). O Design copia para o `proposal.md`. Avoid: reentrevistar; inventar história nova.
- `Gist *superset*`: `proposal.md` = história copiada do cartão (Problema, História, Entra / não entra, Q1–Q3) + *como* (skills, pin, kaizen). Vocabulário e Riscos nascem neste `design.md`. T7 e Apply lêem o Gist como documento único. Avoid: Gist só o *como*; `proposal.md` sem `## Problema` / `## História` / `## Entra`.

## Goals / Non-Goals

**Goals:**

- Encolher o DoD da grelha para 3 seções depois deste card feito; Vocabulário e Riscos passam a viver no Design.
- Uma passagem, no máximo 5 perguntas de produto; filho devolve o delta; PATCH só das seções que mudaram.
- Skip nítido com needle/teste no pai e comentário exacto `card nítido; sem grill`. Pedido explícito para grelhar continua.
- Sem segunda passagem: furo segue para o Design (P0 de produto na crítica aceite).
- Pacote publicado = *superset* do issue (história copiada + *como*). `G_design` continua a exigir pacote + comentário.
- Medida no kaizen de release (proxy transcript): ≤1,5 sessões de grelha por card na janela de 10 cards. Sem parser de usage.
- Produto `oalansilva/covenant-flow` + pin no Cripto. Peles thin MUST Read.

**Non-Goals:**

- Remover Em Refinamento, mover a entrevista para Design, ou tornar o sítio do *como* porta da grelha.
- Mexer em T1, colunas, `process-fsm.yaml`, `enabled_tools`, teto Design 1+1+1, clone da página viva.
- Editar o vendor `grilling`. Reabrir #667 / #755 / #809. Reescrever bodies já grelhados.
- Segunda passagem da grelha. Grelhar sozinho um cartão nítido. Reentrevistar ou inventar história nova no Design.
- Código da aplicação (`backend/` / `frontend/src/`). Parser de usage Cursor/Grok. Dual-write de lei em `.dsh/` / `.grok/` / `.opencode/`. HTML / proto / painel ANTES/DEPOIS. `DESIGN.md`. Schema `grill-driven`.

## Decisions

1. **DoD 3 seções (depois deste card); vigente 6 até o pin.**  
   Headings exactos no body após uma grelha que corre: `## Problema`, `## História`, `## Entra` (e `## Não entra` MAY como irmão). Critérios observáveis vivem **dentro** de Entra. MUST NOT aparecer `## Vocabulário`, `## Critérios de aceite` nem `## Riscos` no body. Fronteira vazia = essas 3 seções **e** nenhuma decisão de operador em aberto. Comentário T1 permanece `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` (idempotente; só o *quando*). Alternativa rejeitada: 4 seções (critérios soltos) — o cartão já mandou critérios dentro de Entra.

2. **Q1=A — uma passagem, teto 5.**  
   O adapter pára depois de uma rodada com no máximo 5 perguntas de produto (teto de linguagem #809 intacto: Qs em português de operador). A árvore Matt MAY continuar no Design e MUST NOT ser exigida em Em Refinamento. Vendor `grilling` intocado: o teto vive no adapter. Alternativa rejeitada: deixar o vendor cortar a árvore.

3. **Q2=A — skip nítido no pai, needle de heading.**  
   Detector pytest (não juízo de LLM): `## Problema` com texto não-vazio **e** (`## Entra` ou `## Não entra`) com texto não-vazio. O pai **não** spawna `grill-card`; posta exactamente `card nítido; sem grill` (idempotente). Pedido explícito grelhar/afiar continua a spawnar. Não é o comentário T1. Alternativa rejeitada: exigir as 3 seções completas para o skip (furaria o *quando* do cartão: quem sofre + entra/não entra). História em falta após skip = furo de produto que o Design pode levantar (Q3=B).

4. **Q3=B — sem segunda passagem.**  
   O que a primeira passagem não fechou segue listado: bullets em Entra marcados para o Design **e/ou** dump do filho para o pai. MUST NOT criar `## Riscos` no issue. Pode reaparecer como P0/P1 de produto na crítica (#854) — aceite. Alternativa rejeitada: segunda rodada «só mais uma Q».

5. **Delta do body = reconstrução, não API de seção.**  
   GitHub REST PATCH substitui o body inteiro. O filho lê o body, reconstrói com o texto das seções inalteradas byte-idêntico, e só reescreve as que mudaram nesta passagem. O dump/handoff para o pai lista os nomes das seções do delta. Golden: dump que reescreve seção inalterada falha. Alternativa rejeitada: sempre reescrever as 3 seções.

6. **Gist = *superset* (substitui Q4=A).**  
   A grelha continua a ser o sítio onde a história se decide (não reentrevistar). `proposal.md` **copia** do body grelhado: Problema, História, Entra / não entra, Q1=A Q2=A Q3=B (texto do issue, não parafrasear até perder Entra). O *como* (skills, pin, kaizen, vocabulário, riscos) continua neste `design.md`. Gist = história copiada + mecanismo. T7 e Apply lêem o Gist como documento único. `G_design` **não** afrouxa: continua a exigir `proposal.md` + `design.md` + `tasks.md` + `specs/**` + clone-gate + comentário no card. `/opsx:apply` lê Gist + `openspec/changes/`, não o body do GitHub como spec paralela. Skills `openspec-new-change` / `openspec-ff-change`: briefing no *issue* = 3 seções (não 6); o *pacote* traz essas 3 + Vocabulário/Riscos neste `design.md`; se faltar seção no issue, comentar o furo e permanecer em Design; MUST NOT inventar história. Frase em `covenant-flow` «Card primeiro»: Gist *superset* do issue (história copiada + *como*) — MUST NOT «só o como». Golden: `proposal.md` sem `## Problema` / `## História` / `## Entra` falha; fixture que copia do issue passa. Alternativa rejeitada: Q4=A (*espelho do como*; história só no GitHub).

7. **Tecto #809: *como* de identificador git vai ao Design, não a `## Riscos` no issue.**  
   Facto continua no body (Problema/Entra). *Como* (path, flag, evento) nasce no pacote de Design. A frase de tecto no bloco Grill-card permanece exacta (já diz «*como* no Design»).

8. **Needles exactos (Apply cola; pytest cobre).**  
   Adapter `grill-card`:
   - disparo: body ainda não diz quem sofre e o que entra/não entra (além do pedido explícito);
   - `uma passagem, no máximo 5 perguntas de produto`;
   - `PATCH só das seções que mudaram`; `handoff lista o delta`;
   - fronteira vazia = `3 seções` + `nenhuma decisão de operador`;
   - MUST NOT exigir Vocabulário/Riscos em Em Refinamento.
   Runbook `## Grill-card` (além do tecto #809 e do relay `todas as options` / `não colapsa`):
   - skip: `card nítido; sem grill`;
   - disparo deixa de dizer `6 seções do DoD`.
   `openspec-new-change` / `openspec-ff-change`: briefing no *issue* = `Problema, História, Entra/não entra`; `proposal.md` MUST copiar essas seções do body (MUST NOT inventar).
   Kaizen: `sessões de grelha por card` e `Em Refinamento vs Design`.
   Peles `.grok` / `.dsh` / `.opencode` MUST NOT ganhar estas frases (≤8 linhas, MUST Read).

9. **Goldens no mesmo `test_grill_card.py` (+ fixtures novas, sem reescrever issues velhos).**  
   - Skill/runbook: needles D8; secção Grill-card já **não** contém `6 seções do DoD` e contém `card nítido; sem grill` + `3 seções`.
   - Fixture body nítido (Problema+Entra preenchidos) → skip; fixture sem esses headings → spawn.
   - Dump com 6 perguntas de produto ou segunda passagem → fail.
   - Dump que reescreve seção inalterada → fail.
   - `proposal.md` de fixture **sem** `## Problema` / `## História` / `## Entra` (ou equivalente observável) → fail. Fixture que copia do issue → passa.
   - Ceiling #809 e N≥2 / D5 / ramos Cursor-Grok vs dsh **permanecem verdes**.
   `test_alan_workflow_d5_ceiling_sentence` hoje asserta `6 seções do DoD` — Apply retuna para o disparo novo.

10. **Kaizen release: 1,5 sessões/card na janela de 10.**  
    Relatório `/kaizen release` (read-only, mesma fonte de transcript já usada: `$CURSOR_TRANSCRIPTS_DIR` / `agent-transcripts`, correlação `#<id>` / `card-<id>`):
    - sessões de grelha por card = count de filhos `grill-card` (título/description com needle `grill-card`); comentário `card nítido; sem grill` conta como **0** sessões de grelha nesse card;
    - Em Refinamento vs Design = count grelha vs count `design-autor` + `design-critic` + `Assessment A`/`Assessment B`.
    Alvo: média ≤ **1,5** sessões de grelha por card nos **próximos 10** cards que saem de Em Refinamento (lote seguinte; se o lote tiver <10, a medida fica aberta até 10 ou o lote seguinte). Justificativa: baseline 2,7 (40 sessões / 15 cards a partir de #876). Uma passagem + skip nítido deve cair perto de 1,0 nos cards típicos; 1,5 é tecto conservador que prova o fim da duplicação sem exigir skip em todos. 10 cards mistura nítido e grelhado e cabe num ou dois lotes. MUST NOT parser de usage Cursor/Grok; MUST NOT dashboard; MUST NOT valores em dinheiro. O número 1,5 **não** é assert de CI — é o que o kaizen de release seguinte olha.

11. **Pin patch `v1.1.16`, canal usual.**  
    Origin live = `v1.1.15`. Apply MUST `gh api repos/oalansilva/covenant-flow/tags` antes de taggar; se `v1.1.16` ocupada, bump patch seguinte (nunca major). `SCHEMA_MAJOR` 1. Ordem: commit no produto → tag → `implantar --pin` no Cripto. Pin-tests que cravam `v1.1.15` (p.ex. `test_subagent_stop.py` na linha S1 do runbook) sobem para a tag deste card — P3 de Apply.

## Apply contract

Ordem (produto primeiro; zero UI Cripto):

1. Canónico `grill-card`: DoD 3, uma passagem teto 5, delta PATCH, fronteira 3 + zero decisão de operador, *quando* do skip no adapter (pai executa o skip). Comentário T1 = linha pinada. Vendor `grilling` intocado. Tecto #809: *como* não gera `## Riscos` no issue.
2. Runbook `covenant-flow`: bloco Grill-card (disparo, skip `card nítido; sem grill`, 3 seções); «Card primeiro» = Gist *superset* (história copiada + *como*); Design/`openspec-new`/`openspec-ff` briefing 3 seções no *issue*; `proposal.md` copia essas 3. Tecto #809 e relay de options intactos. `AGENTS.md` / `process-fsm.yaml` intocados.
3. `kaizen`: `/kaizen release` reporta sessões de grelha por card e Em Refinamento vs Design (D10).
4. Goldens D9 em `test_grill_card.py` + fixtures. Retunar needle `6 seções do DoD`. Ceiling #809 e N1 (#755) verdes. Pin-tests → tag deste card.
5. Stubs Grok/dsh/OpenCode **não** incham (MUST NOT dual-write lei).
6. Commit + tag patch no produto (esperado **`v1.1.16`**; Apply confirma origin).
7. `implantar --pin` no worktree Cripto; overlay `pin:` = essa tag. MUST NOT `backend/**` nem `frontend/src/**`. MUST NOT reabrir #667/#755/#809 nem reescrever bodies já grelhados.

Rollback = pin Cripto `v1.1.15`. Sem migration de banco. Sem rebuild frontend.

## Risks / Trade-offs

- [Skip nítido por heading deixa passar body vago com `## Problema` vazio disfarçado] → D3: texto não-vazio obrigatório; golden de fixture nítido vs oco. Residual P2 aceite: detector não é NLU — um Problema de uma palavra passa o skip; o Design levanta P0 se a história faltar (Q3=B).
- [Q3=B aumenta P0 na crítica] → aceite explícito do cartão. Medir recidiva no kaizen de release (D10), não com segunda passagem.
- [Copiar a história para o Gist vira segunda entrevista] → D6: REST do issue → colar; MUST NOT reentrevistar; MUST NOT inventar. Golden: `proposal.md` sem as 3 seções falha.
- [Delta PATCH é ritual, não Guard] → golden de dump; modelo que reescreve o body inteiro aparece no próximo grill, não em pytest de skill. P2 aceite (mesmo recorte #809: tecto é skill não Guard).
- [Tag `v1.1.16` ocupada] → Apply confirma origin e bump patch seguinte; nunca major.
- [DoD 6 ainda no body deste #955 e em cards já grelhados] → migration: não reescrever; o DoD 3 vale daqui para a frente após o pin.
- [Pele Grok/dsh/OpenCode sem o texto novo] → MUST Read; inchar stubs é regressão do needle ≤8.

## Migration Plan

Aditivo sobre `v1.1.15`. Até este card pinado, o DoD vigente da grelha continua 6 (este body #955 mantém 6). Depois do pin: grelhas novas usam 3; skip nítido no pai; Design briefing 3 seções no *issue*; `proposal.md` copia essas 3 + *como*. Bodies já grelhados **não** se reescrevem. Ordem = Apply contract. Rollback = pin `v1.1.15`. Sem schema overlay. Sem canal novo. Sem aresta FSM.

## Open Questions

Nenhuma bloqueante. Q1=A Q2=A Q3=B congeladas. Q4=A substituída (Gist *superset*). Residuais P2 aceite: detector de nítido é heading+texto, não NLU; delta PATCH e tecto são skill não Guard.

## Prototype

Prototype: N/A — card sem-tela (`UI impact: none`). Harness/runbook; nenhuma tela do produto; sem pasta proto; sem URL HTTP. Sem painel ANTES/DEPOIS. Sem HTML. Sem `frontend/public/prototypes/`. Sem rewrite de `DESIGN.md`. Playwright desta coluna = N/A. Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O filho autor não spawna Assessment A/B. T7 e Aprovação de Design humanas permanecem.

## Design Critique

Crítico isolado pós-rework 1/1 (sem-tela, Grok 4.6, sem transcript). Snapshot: `.impeccable/critique/955-card-955-grelha-enxuta-2026-09-16T194042Z.md`. Prototype: N/A justificado (`UI impact: none`). Teto 1+1+1: rework único (T6 Alan); zero P0/P1 novo → sem segundo rework.

- **P0** — nenhum.
- **P1** — nenhum.
- **P2** (residual aceite) — detector nítido = heading+texto, não NLU; delta PATCH/tecto = skill, não Guard.
- **P3** (aceitos, Apply) — retunar needle `6 seções do DoD`; pin-tests `v1.1.15` → tag deste card; digest stale da crítica anterior.
- **Disposition:** Q1=A Q2=A Q3=B intactos. Q4=A **substituída** (T6): Gist = *superset* — `proposal.md` copia Problema/História/Entra/Não entra do issue; T7 valida o Gist como documento único. `G_design` não afrouxa. Entrega produto + pin.
- **Riscos não bloqueantes:** DoD 6 no adapter live até o pin; skip heading pode passar Problema de uma palavra (Q3=B).

Design Agent verdict: PASS
