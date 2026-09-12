## 1. Runbook que o pai vê (Cursor)

- [x] 1.1 Em `.cursor/skills/covenant-flow/SKILL.md` (Implementação / Code Review): classificar cada achado **mecânico** vs **juízo**; mecânicos juntos num único Apply de correção **sem Ask**; juízo vai a residual e **não** ocupa o slot
- [x] 1.2 No mesmo skill: após 1 correção + 1 onda, P1 restante **ou P1 novo** = residual no handoff de Done **e** no comentário do card; o card **segue** (commit, PR, QA); MUST NOT terceiro ciclo; MUST NOT perguntar «autorizar extra / aceitar residual»; pai MUST NOT corrigir no próprio transcript; fecho pós-commit continua uma onda
- [x] 1.3 Prompts autocontidos (secção do mesmo skill): bloco «teto em silêncio» (classificar; 1+1; residual no Done; sem Ask)
- [x] 1.4 QA closeout no mesmo skill: sinal determinístico (inventário de teste, formatação, skip de ficheiro novo) fica no Apply/QA até verde ou teto; MUST NOT reabrir onda de juízo
- [x] 1.5 `openspec-apply-change`: não editar salvo um needle existente partir com as strings deste contrato

## 2. Wording da ordem destape (máquina #879 intacta)

- [x] 2.1 `FOLLOWUP_REVIEW`: classificar mecânico vs juízo; mecânicos → no máximo um Apply com a lista + uma onda; juízo → residual (não ocupa o slot); se após o ciclo restar P1 ou nascer P1 novo → residual no Done, card segue, não terceiro ciclo, MUST NOT «autorizar extra / aceitar residual»; poke continua ordem, nunca `concluiu?`
- [x] 2.2 `FOLLOWUP_QA`: verde → integrar_develop; falhou → evidência visível; sinal determinístico fica no Apply/QA até verde ou teto; não reabras onda de juízo; nunca `concluiu?`
- [x] 2.3 MUST NOT neste grupo: matcher, sidecar path, `loop_count`, classificação por `description` curta, goldens de destape como aceite deste card

## 3. Specs

- [x] 3.1 Aplicar deltas `openspec/changes/card-893-teto-review-silencio/specs/cursor-harness/spec.md`
- [x] 3.2 Aplicar deltas `openspec/changes/card-893-teto-review-silencio/specs/llm-flow-emission/spec.md`
- [x] 3.3 Aplicar deltas `openspec/changes/card-893-teto-review-silencio/specs/cursor-code-review/spec.md` (happy path após a onda de verificação = residual + continuar, não Ask e não terceiro ciclo)

## 4. Higiene de needles existentes (não é aceite)

- [x] 4.1 Se as strings de `FOLLOWUP_*` ou do runbook se moverem, retunar só os asserts **já existentes** (`test_subagent_stop.py`, `test_card_729_activity_children.py`). Não criar teste novo. Prova de Done = próxima sessão sem Ask de teto e sem terceiro ciclo, não pytest

## 5. Verify (harness Cursor)

- [x] 5.1 `openspec validate "card-893-teto-review-silencio" --type change --strict`
- [x] 5.2 Zero produto / UI; zero `.cursor/process-fsm.yaml`; zero pin / dual-write noutros clientes; zero `AGENTS.md` always-on a crescer
- [x] 5.3 Q4/#884/#879/#880 intactos no runbook: grelha, crítico, intervalo colado, os dois reviewers no mesmo turno, QA nos checks, destape máquina, hang Desktop+SSH, spawn-por-task
