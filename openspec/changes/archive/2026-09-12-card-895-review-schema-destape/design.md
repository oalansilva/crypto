## Context

Card [#895](https://github.com/oalansilva/crypto/issues/895) (kaizen, Operação, P1). Briefing = issue grelhado. Sucessor de #893 (Homologado). Este Design não reabre Qs do grill nem o teto 1+1.

Facto: o teto **já** está escrito (#893 em `develop` 284a61b2): 1 correção + 1 verificação; sem Ask; residual no Done; card segue; P0 pára a coluna. Quem sofre é o Alan na homologação: o review ainda **inventa P1 no wording**. Nesta sessão do #893 a verificação marcou «falta um ramo» no destape como P2; o fecho vs `develop` **subiu o mesmo furo a P1**; o pai classificou prosa à mão. O parágrafo do destape (`FOLLOWUP_REVIEW`) tenta ser máquina de estados e sempre falta um ramo.

O teto fez o trabalho certo (residual, card segue). Este card muda **o que conta como achado** e **quem classifica**.

UI impact: none
live_route: N/A harness-only; orquestração do pai Cursor (Code Review + destape + fecho vs develop); no product route
surface: new

Harness-only: orquestração do pai Cursor (Code Review + destape + fecho vs `develop`). Sem rota de produto, sem HTML, sem pasta de protótipos. Nunca `/monitor` `/favorites` `/combo/*` `landing`.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Goals / Non-Goals

**Goals:**

- Cada achado da onda e do fecho nasce **já estruturado** no dump (schema de achado). O pai **não** classifica a reler prosa e **não** sobe a gravidade emitida.
- «Falta esta frase» no destape **não** entra no pacote. Política de destape = tabela curta (limpo / só juízo / mecânico / após 1+1 / P0). Reviewer de processo **não** pontua cláusula em falta. Tabela a errar o que o operador vê (P0 deixa de parar) = P1 de aceite.
- Fecho vs `develop` só caça **defeito novo** vs intervalo pré-commit (ou reuse SHA). Residual já no comentário do card **não** reabre e **não** sobe de gravidade.
- Rubrica estável: P3 copy/needle/detalhe Apply; P2 contrato incompleto que não muda aceite; P1 patch quebra aceite observável. P0 pára a coluna.
- Checklist mecânico no pai: falha = bloqueio visível, não commita, não volta como prosa de LLM. LLM de processo só: «o diff fura o Entra/não entra?».
- Teto #893 intacto: 1+1; sem Ask; residual segue; «bloqueia merge» num nit não autoriza terceiro ciclo.
- Prova de Done = próxima sessão sem relitigar residual de wording do destape como P1 novo. Sem teste automático extra.

**Non-Goals:**

- Reabrir Ask; ciclar até «sem achados»; fundir os dois reviewers.
- Guard a negar o N-ésimo spawn (aresta; #884 recusou).
- Destape matcher / sidecar / `loop_count` / poke ≠ `concluiu?` (#879). Hang Desktop+SSH (#880). Spawn-por-task / reviewers em série (#884).
- Mudar o número do teto #893 (1 correção + 1 verificação). Residual preso em Code Review. Pytest extra como aceite. Arquivar #893.
- Aresta FSM; pin; dual-write noutros clientes; `AGENTS.md` always-on a crescer; overlay `clients.*.auto`.
- Auto-merge / pular homologação. Produto Cripto / UI. JSON schema de API. Reviewer terceiro. HTML proto. `CONTEXT.md`. `docs/adr/`.

## Decisions

1. **Schema de achado = bloco parseável no dump dos dois agent files.** Não JSON schema de API. Não reviewer terceiro. Cada achado é um bloco de linhas próprias:

   ```
   FINDING
   gravidade: P0|P1|P2|P3
   classe: mecanico|juizo
   conserto_obvio: sim|nao
   conserto_proposto: <uma linha ou n/a>
   bloqueia_merge: sim|nao
   file: <path:line ou n/a>
   summary: <uma linha>
   ```

   Dump vazio: exactamente `No findings.` Valores ASCII (`mecanico`/`juizo`, `sim`/`nao`) para o pai copiar campos sem reler prosa. `classe: mecanico` = mecânico; `classe: juizo` = juízo. O pai **copia** gravidade e classe; MUST NOT reclassificar; MUST NOT subir gravidade. `bloqueia_merge: sim` num P3 nit **não** autoriza terceiro ciclo nem Ask; P0 continua a parar a coluna. Residual de juízo e P3 continua residual classificado.

   Rejeitado: JSON schema de API. Rejeitado: o pai a classificar mecânico vs juízo a reler prosa (#893 D1). Rejeitado: terceiro reviewer de classificação.

2. **Tabela de destape vive em `FOLLOWUP_REVIEW`; o runbook espelha.** A política deixa de ser um parágrafo que tenta ser máquina. Copy exacto de destino (máquina #879 intacta — matcher, sidecar `.cursor/tmp/awaiting-task.json`, `loop_count`, classificação, poke ≠ `concluiu?`):

   ```
   O filho reviewer já devolveu. Se o par da onda ainda não devolveu: espera (não commitas, não spawnes o outro reviewer agora).
   Tabela destape (não pontues cláusula em falta):
   limpo → commit
   só juízo → residual, card segue (não gasta correção)
   mecânico → no máximo um conserto + uma verificação
   após 1+1 → residual, card segue
   P0 → a coluna pára
   MUST NOT «autorizar extra / aceitar residual». Não perguntes se concluiu.
   ```

   `.cursor/skills/covenant-flow/SKILL.md` (S2 destape + teto em silêncio) espelha as cinco linhas. Reviewer de processo MUST NOT pontuar «falta esta frase» / cláusula em falta nessa tabela. Se a tabela **errar o que o operador vê** (P0 deixa de parar a coluna) isso **é** P1 de aceite, não wording.

   Rejeitado: deixar o parágrafo #893 (sempre falta um ramo). Rejeitado: matcher / sidecar / `loop_count` / poke «concluiu?» (#879). Rejeitado: goldens de destape como aceite deste card.

3. **Fecho vs `develop` só defeito novo; residual colado no spawn.** O pai cola o residual já no comentário do card sob `## Residual já no card` no prompt da onda de fecho. Os filhos MUST NOT re-emitir esses itens e MUST NOT subir a gravidade deles. Só entra defeito **novo** relativamente ao intervalo pré-commit (ou reuse do SHA se já coberto). O pai MUST NOT inflar a gravidade emitida. Fecho continua **uma** onda, fora do teto 1+1.

   Rejeitado: o fecho a relitigar «falta um ramo» como P1 novo (testemunha #893). Rejeitado: o pai a subir P2→P1 à mão.

4. **Rubrica estável, observável, nos dois agent files.**

   - P3 = copy / needle / detalhe de Apply
   - P2 = contrato incompleto que **não** muda o aceite
   - P1 = o patch **quebra** o aceite observável (Ask no meio da coluna, terceiro ciclo, DEV a falar com bot de PROD)
   - P0 = a coluna pára (já #893 / #884)

   Nit de copy ≠ aceite partido. «Falta esta frase» no destape **não** é achado (nem P2).

   Rejeitado: gravidade por «completude de parágrafo». Rejeitado: o pai a remapear P2→P1.

5. **Checklist = script no pai, não teste como aceite.** Path: `scripts/process-fsm/review_process_checklist.py`. O pai corre **depois** dos dois reviewers e **antes** de commit / de tratar cerimónia de processo como achado. Exit 0 = segue. Exit ≠ 0 = `ERROR: process-checklist failed: <item>` (bloqueio visível, **não** commita, **não** volta como prosa de LLM).

   O script confirma (disco):

   - `tasks.md` da change bound: nenhum `- [ ]` pendente
   - `design.md` bound: tokens `UI impact:` / `live_route:` / `surface:` parseáveis (reusa `design_clone_gate.parse_*`)
   - `.cursor/tmp/review-diff.patch` existe e não está vazio (intervalo colado)
   - o intervalo colado **não** adiciona estado, evento ou `enabled_tools` a `.cursor/process-fsm.yaml`

   Item de sessão (pai, não disco): os dois reviewers nasceram no mesmo turno. Se o pai não os emitiu neste turno, o mesmo bloqueio visível (já #884). Flag opcional `--wave-same-turn yes` para o pai atestar; ausência ou `no` = falha.

   LLM de processo (`code-reviewer`) MUST NOT recaçar estes itens. Só pergunta: «o diff fura o Entra/não entra da change bound?». MUST NOT: pytest novo como aceite; `test_card_895_*` como Done. Needles `FOLLOWUP_*` já existentes MAY ser retunados se as strings se moverem (higiene, não aceite).

   Rejeitado: checklist só como prosa no runbook (volta a ser achado de LLM). Rejeitado: teste automático extra como aceite. Rejeitado: o reviewer de processo a pontuar tasks/tokens/onda/intervalo/aresta.

6. **Teto #893, split de papéis e sinal determinístico intactos.** 1 correção + 1 verificação; sem Ask; residual no Done; card segue; P0 pára a coluna. Um `bloqueia_merge: sim` num nit **não** autoriza terceiro ciclo. `diff-reviewer` caça defeito no intervalo; `code-reviewer` caça contrato. Independência vale. Sinal determinístico de QA fica no Apply/QA, fora da onda de juízo. Humano uma vez (T7/T15). `openspec-apply-change` fora salvo needle partido. Predecessor `openspec/changes/card-893-teto-review-silencio/` **não** se arquiva e **não** se edita.

   Rejeitado: alargar o teto. Rejeitado: fundir reviewers. Rejeitado: Guard a negar o N-ésimo spawn.

## Prototype

N/A — card sem tela: orquestração do pai Cursor (Code Review + destape + fecho vs `develop`), harness-only. Sem HTML, sem clonar rota de catálogo, sem `frontend/public/prototypes/`. Impeccable / Playwright / `DESIGN.md` = N/A justificado. Nunca emprestar `/monitor` `/favorites` `/combo/*` `landing`.

## Impeccable

N/A — sem superfície visual; não há pipeline context → shape → prototype → critique → browser-gate. Gates de Design e aprovação humana (Aprovação de Design → Pronto para Dev) permanecem.

## Apply contract

- Editar `.cursor/agents/diff-reviewer.md` e `.cursor/agents/code-reviewer.md`:
  - Substituir «Report findings first, severity P0–P3, with file:line» pelo bloco `FINDING` (D1) + rubrica (D4). Dump vazio = `No findings.`
  - `diff-reviewer`: fecho só defeito novo; residual sob `## Residual já no card` MUST NOT re-emitir nem subir gravidade.
  - `code-reviewer`: MUST NOT pontuar cláusula em falta na tabela de destape; MUST NOT recaçar o checklist; só «o diff fura o Entra/não entra da change bound?».
- Editar `.cursor/skills/covenant-flow/SKILL.md`:
  - Implementação / Code Review: pai **copia** schema (não reclassifica, não infla); cola `## Residual já no card` no fecho; corre o checklist antes do commit; falha = bloqueio visível.
  - Prompts autocontidos / teto em silêncio: schema no dump; teto 1+1 intacto; `bloqueia_merge` num nit ≠ terceiro ciclo.
  - S2 destape: espelhar as cinco linhas da tabela; MUST NOT pontuar cláusula em falta.
- Retunar `FOLLOWUP_REVIEW` em `scripts/process-fsm/subagent_stop.py` para o copy exacto da tabela (D2). MUST NOT mudar matcher, sidecar, `loop_count`, classificação, nem perguntas `concluiu?`.
- Criar `scripts/process-fsm/review_process_checklist.py` (D5). MUST NOT pytest novo como aceite.
- `openspec-apply-change`: não editar salvo needle partido.
- Aplicar deltas OpenSpec `cursor-harness`, `llm-flow-emission`, `cursor-code-review`.
- MUST NOT: produto, `.cursor/process-fsm.yaml`, `AGENTS.md` always-on a crescer, overlay `clients.*.auto`, pin, dual-write `.dsh/` `.grok/` `.opencode/`, HTML de protótipo, `CONTEXT.md`, `docs/adr/`, teste automático extra como aceite, arquivar ou editar `openspec/changes/card-893-teto-review-silencio/`.
- Needles existentes: só retune se as strings deste contrato as partirem. Não criar `test_card_895_*`.

## Risks / Trade-offs

- [Pai continua a classificar prosa e a inflar] → schema no dump + runbook «copia, não relê»; prova = próxima sessão, não pytest.
- [Reviewer ainda pontua «falta esta frase»] → tabela visível + spec: esse achado **não entra** no pacote; não é P1 novo no fecho.
- [Tabela a errar o operador (P0 não pára)] → isso **é** P1 de aceite, não wording; crítico/review de processo caça aceite partido, não cláusula.
- [`bloqueia_merge: sim` num nit tratado como ciclo extra] → campo informativo para T15; teto 1+1 e P0-pára prevalecem.
- [Checklist script vs sessão] → disco no script; dois reviewers no mesmo turno = facto do pai (já #884); falha = bloqueio visível.
- [Destape wording vs #879] → só o texto de destino; máquina destape intocada.
- [Needles `FOLLOWUP_*`] → retune mecânico no Apply, P3, não aceite.

## Migration / Rollout

1. Apply na branch do card (agent files + runbook + FOLLOWUP tabela + checklist script + deltas OpenSpec). Integração em `develop` no T14 habitual.
2. Sem pin, sem dual-write, sem HTML.
3. Rollback: reverter agent files + SKILL + FOLLOWUP destino + script; specs voltam no archive do lote. Máquina destape #879 não entra no rollback. #893 não se desarquiva porque nunca foi arquivado.
4. Prova: próxima sessão neste cliente em que verificação / fecho **não** relitiga residual de wording do destape como P1 novo.

## Open Questions

Nenhuma. Decisões *como* (schema / tabela / checklist) fechadas acima. Teto, onda, destape-máquina e hang não reabertos.

## Design Critique

Crítico isolado (sem-tela, 1 critic, inherit, sem transcript). Prototype: N/A justificado (`UI impact: none`). Teto 1+1+1: sem rework (zero P0/P1 de produto/escopo).

Token check:
- `UI impact: none` — linha própria.
- `live_route: N/A harness-only; orquestração do pai Cursor (Code Review + destape + fecho vs develop); no product route` — ausência + justificativa; nunca `/monitor` `/favorites` `/combo/*` `landing`.
- `surface: new` — linha própria; isenta catálogo (par `live_route: N/A`).
- Prototype N/A justificado. Impeccable N/A justificado. clone_gate PASS.

- **P0** — nenhum.
- **P1** — nenhum.
- **P3** (aceitos, Apply) — copy exacto de `FOLLOWUP_REVIEW` (5 linhas da tabela; matcher/sidecar/`loop_count`/classificador/`concluiu?` ficam #879); path `scripts/process-fsm/review_process_checklist.py`, ASCII `mecanico`/`juizo`/`sim`/`nao`, flag `--wave-same-turn`; needles `FOLLOWUP_*` já existentes se as strings partirem (sem `test_card_895_*` como aceite); runbook «Teto em silêncio»: pai **copia** dump, não deixar o «classificar prosa» do #893 no sítio; agent files: substituir «Report findings first…» pelo bloco `FINDING` + rubrica; `code-reviewer` deixa de tratar checkbox/token/onda/intervalo/aresta como achado.
- **Disposition:** D1–D6 honram Entra/não entra. Schema no dump dos dois reviewers (pai copia, não sobe gravidade); destape = tabela de 5 linhas; «falta esta frase» não é achado; tabela a errar o operador (P0 não pára) = P1 de aceite; fecho vs `develop` só defeito novo ou reuse SHA, residual colado sob `## Residual já no card`; rubrica P3/P2/P1/P0 estável; checklist mecânico = bloqueio visível, LLM só Entra/não entra; split de papéis intacto; prova = próxima sessão, sem pytest extra. Teto #893 intacto (1+1, sem Ask, residual no Done, P0 pára, `bloqueia_merge` num nit ≠ terceiro ciclo). Destape-máquina #879 intocada. Sem aresta FSM. Sem UI de produto.
- **Riscos não bloqueantes:** pai pode continuar a classificar prosa (prova = próxima sessão); reviewer ainda pontuar «falta esta frase» (spec: não entra no pacote).

Design Agent verdict: PASS
