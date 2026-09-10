## 1. Runbook que o pai vê (Cursor)

- [x] 1.1 Em `.cursor/skills/covenant-flow/SKILL.md`: tecto de **um** filho Apply por entrada em Em desenvolvimento (loop interno até tasks feitas ou P0 visível); recusa visível se o Apply devolver cedo sem P0 (não abre review nem segundo Apply)
- [x] 1.2 No mesmo skill: Code Review = **dois** Task no **mesmo turno** do pai sobre o intervalo já colado; fila do host não falha; apagar a linha «Após destape de `diff-reviewer`, o pai spawna `code-reviewer`»
- [x] 1.3 No mesmo skill: P1/P2 voltam numa lista a no máximo **um** Apply de correção + **uma** onda; resto = bloqueio visível ao operador; pai MUST NOT corrigir no próprio transcript; fecho pós-commit continua uma onda
- [x] 1.4 Prompts autocontidos (secção do mesmo skill): bloco Apply-coluna com «único filho da coluna / não devolvas entre tasks»; bloco onda com «os dois nascem neste turno / não esperes destape do primeiro»
- [x] 1.5 Em `.cursor/skills/openspec-apply-change/SKILL.md`: o loop interno vai até done ou P0 visível; «Pause / ask parent» entre tasks deixa de ser happy path; permanece MUST NOT `process_event` / commit / push / spawn reviewers

## 2. Wording da ordem destape (máquina #879 intacta)

- [x] 2.1 `FOLLOWUP_APPLY`: se tasks feitas ou P0 visível → materializa o diff e spawna os **dois** reviewers **no mesmo turno**; não spawnes outro Apply; se devolveu cedo sem P0 → bloqueio visível, não abras review
- [x] 2.2 `FOLLOWUP_REVIEW`: se o par da onda ainda não devolveu, espera (não commitas, não spawnes o outro); se os dois devolveram com P1/P2 → no máximo um Apply com a lista; se limpo → commit; poke continua ordem, nunca `concluiu?`
- [x] 2.3 MUST NOT neste grupo: matcher, sidecar path, `loop_count`, classificação por `description` curta, goldens de destape como aceite deste card

## 3. Specs

- [x] 3.1 Aplicar deltas `openspec/changes/card-884-apply-por-coluna-review-onda/specs/cursor-harness/spec.md`
- [x] 3.2 Aplicar deltas `openspec/changes/card-884-apply-por-coluna-review-onda/specs/llm-flow-emission/spec.md`
- [x] 3.3 Aplicar deltas `openspec/changes/card-884-apply-por-coluna-review-onda/specs/cursor-code-review/spec.md` (happy path deixa de ser «sessão principal corrige e re-corre o reviewer afectado»)

## 4. Higiene de needles existentes (não é aceite — Q1)

- [x] 4.1 Se as strings de `FOLLOWUP_*` ou do runbook se moverem, retunar só os asserts **já existentes** (`test_subagent_stop.py`, `test_card_729_activity_children.py`). Não criar teste novo. Prova de Done = próxima sessão, não pytest

## 5. Verify (harness Cursor)

- [x] 5.1 `openspec validate "card-884-apply-por-coluna-review-onda" --type change --strict`
- [x] 5.2 Zero produto / UI; zero `.cursor/process-fsm.yaml`; zero pin / dual-write noutros clientes; zero `AGENTS.md` always-on a crescer
- [x] 5.3 Q4 intacta no runbook: grelha, crítico, intervalo colado, os dois reviewers, QA nos checks
