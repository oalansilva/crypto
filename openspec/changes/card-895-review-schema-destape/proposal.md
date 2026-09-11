## Why

O teto do #893 **cala a pergunta**, mas o review ainda **inventa P1 no wording**. Nesta sessão do #893 a verificação marcou «falta um ramo» no destape como P2; o fecho vs `develop` **subiu o mesmo furo a P1**; o pai classificou prosa à mão. Quem sofre é o Alan na homologação: o relógio gasta-se a caçar cláusula em falta. O teto fez o trabalho certo (residual, card segue). O que falha é **o que conta como achado** e **quem classifica**.

## What Changes

- Cada achado da onda (os dois reviewers) e do fecho sai **já estruturado** no dump: gravidade, classe (mecânico / juízo), conserto óbvio sim/não, conserto proposto, se bloqueia merge. O pai **não** adivinha a classe a reler prosa e **não** sobe a gravidade que o reviewer emitiu.
- Completude de parágrafo / «falta esta frase» no destape **não** é achado. A política de destape deixa de ser um parágrafo que tenta ser máquina: passa a **tabela curta**, visível pelo que acontece (limpo / só juízo / mecânico / após 1+1 / P0). Reviewer de processo **não** pontua cláusula em falta nessa tabela. Se a tabela **errar o que o operador vê** (ex.: P0 deixa de parar a coluna), isso **é** P1 — quebra o aceite, não é «frase em falta».
- Fecho vs `develop` só caça **defeito novo** relativamente ao intervalo pré-commit (ou reusa o SHA se já coberto). Residual já no comentário do card **não** reabre e **não** sobe de gravidade. O pai **não** infla.
- Rubrica estável e observável: P3 = copy / needle / detalhe de Apply; P2 = contrato incompleto que **não** muda o aceite; P1 = o patch **quebra** o aceite observável (Ask no meio, terceiro ciclo, DEV a falar com bot de PROD). P0 continua a parar a coluna.
- Checklist mecânico de processo (script no pai): tasks todas feitas, tokens de Design presentes, dois reviewers no mesmo turno, intervalo colado, máquina de estados do board sem aresta nova. Se o checklist falha: **bloqueio visível**, não commita; **não** volta como prosa de LLM. O reviewer de processo LLM só pergunta: «o diff fura o Entra/não entra?».
- O schema **não** muda o teto do #893: 1 correção + 1 verificação; sem Ask; residual segue para Done; P0 continua a parar a coluna. Um campo «bloqueia merge» num nit **não** autoriza terceiro ciclo nem pergunta.
- Split de papéis permanece: um reviewer caça defeito no intervalo; o outro caça contrato. Independência vale.
- Prova de Done: na próxima sessão, a verificação / o fecho **não** relitiga residual de wording do destape como P1 novo. Sem teste automático extra como aceite.
- App/UI não mudam.

**Não muda / não entra:** reabrir Ask no meio da coluna; ciclar até «sem achados»; fundir os dois reviewers; Guard a negar o N-ésimo spawn (aresta; #884 recusou); destape matcher / sidecar / `loop_count` / poke «concluiu?» (#879); hang Desktop+SSH (#880); spawn-por-task / reviewers em série (#884); teto 1+1 / residual no Done / sem Ask / QA determinístico (já #893); inventar aresta na FSM; agente a arrastar colunas só do Alan; auto-merge / pular homologação; código de produto Cripto (app / UI); dual-write noutros clientes / pin novo só por causa disto; arquivar #893.

## Capabilities

### New Capabilities

- (nenhuma) — o contrato vive nas specs de harness/emissão/review já existentes. Este card não inventa coluna nem capability.

### Modified Capabilities

- `cursor-harness`: o pai **consome** o schema emitido (não reclassifica, não sobe gravidade); `FOLLOWUP_REVIEW` passa a tabela de destape (destino só; máquina #879 intacta); checklist mecânico no pai (falha = bloqueio visível, não prosa); fecho vs `develop` não relitiga residual; teto #893 intacto.
- `llm-flow-emission`: o que o pai **emite** — achados já classificados no dump, sem inflar gravidade; destape como tabela (não parágrafo a pontuar); residual já no comentário não reabre; checklist a falhar = bloqueio visível, não achado de LLM; sem Ask, sem terceiro ciclo.
- `cursor-code-review`: os dois agent files emitem o schema de achado; rubrica P3/P2/P1 estável; reviewer de processo **não** pontua cláusula em falta na tabela de destape e **não** recaça o checklist; fecho vs `develop` só defeito novo (ou reuse SHA); «bloqueia merge» num nit não autoriza terceiro ciclo.

## Impact

- Agent files Cursor: `.cursor/agents/diff-reviewer.md` e `.cursor/agents/code-reviewer.md` (bloco parseável no dump; não JSON schema de API; não reviewer terceiro).
- Skill Cursor: `.cursor/skills/covenant-flow/SKILL.md` (Implementação / Code Review / teto em silêncio / S2 destape espelha a tabela; fecho vs `develop` não relitiga). `openspec-apply-change`: só se um needle existente partir.
- Wording da **ordem** destape: `FOLLOWUP_REVIEW` em `scripts/process-fsm/subagent_stop.py` vira tabela curta (limpo / só juízo / mecânico / após 1+1 / P0). Matcher, sidecar `.cursor/tmp/awaiting-task.json`, `loop_count`, classificação e poke ≠ `concluiu?` permanecem #879.
- Checklist: script no pai em `scripts/process-fsm/` (não pytest novo como aceite). LLM de processo só: «o diff fura o Entra/não entra?».
- Specs acima. Sem produto (`backend/` / UI). Sem `.cursor/process-fsm.yaml`. Sem pin novo. Sem dual-write `.dsh/` / `.grok/` / `.opencode/`. Sem `AGENTS.md` always-on a crescer. Sem overlay `clients.*.auto`. Sem HTML proto. Sem `CONTEXT.md`. Sem `docs/adr/`. Sem arquivar #893 (`openspec/changes/card-893-teto-review-silencio/` permanece activo, não se edita).
- Needles **já existentes** em `scripts/process-fsm/test_*.py` MAY ser retunados se as strings do runbook/ordem se moverem. **Não** é aceite deste card.
- `UI impact: none`. Prototype N/A. Snapshot N/A. Cliente desta sessão é Grok, mas o contrato canónico vive em `.cursor/skills/` e `.cursor/agents/` (como #893). Stubs Grok continuam ponte ≤8 linhas.
