## 1. Schema nos agent files (Cursor)

- [x] 1.1 Em `.cursor/agents/diff-reviewer.md`: substituir «Report findings first, severity P0–P3, with file:line» pelo bloco `FINDING` (gravidade, classe mecanico|juizo, conserto_obvio, conserto_proposto, bloqueia_merge, file, summary); dump vazio = `No findings.`; colar a rubrica P3/P2/P1/P0
- [x] 1.2 No mesmo ficheiro: fecho vs `develop` só defeito novo relativamente ao intervalo pré-commit (ou reuse SHA); residual sob `## Residual já no card` MUST NOT re-emitir nem subir gravidade
- [x] 1.3 Em `.cursor/agents/code-reviewer.md`: o mesmo bloco `FINDING` + rubrica; MUST NOT pontuar cláusula em falta na tabela de destape; MUST NOT recaçar o checklist (tasks, tokens, dois reviewers no turno, intervalo colado, sem aresta nova); só «o diff fura o Entra/não entra da change bound?»
- [x] 1.4 Split de papéis intacto: `diff-reviewer` caça defeito no intervalo; `code-reviewer` caça contrato; MUST NOT fundir os dois

## 2. Runbook que o pai vê (Cursor)

- [x] 2.1 Em `.cursor/skills/covenant-flow/SKILL.md` (Implementação / Code Review): pai **copia** schema do dump (não reclassifica, não infla gravidade); `bloqueia_merge` num nit ≠ terceiro ciclo; P0 continua a parar a coluna; teto #893 (1+1, sem Ask, residual no Done) intacto
- [x] 2.2 No mesmo skill: fecho vs `develop` cola `## Residual já no card`; residual já no comentário **não** reabre e **não** sobe; só defeito novo (ou reuse SHA)
- [x] 2.3 No mesmo skill: depois da onda, correr `scripts/process-fsm/review_process_checklist.py` **antes** do commit; falha = `ERROR: process-checklist failed:` + item (bloqueio visível, não commita, não prosa de LLM)
- [x] 2.4 Prompts autocontidos / teto em silêncio: schema no dump; tabela destape; teto 1+1 intacto
- [x] 2.5 S2 destape: espelhar as cinco linhas (limpo / só juízo / mecânico / após 1+1 / P0); reviewer de processo MUST NOT pontuar cláusula em falta
- [x] 2.6 `openspec-apply-change`: não editar salvo um needle existente partir com as strings deste contrato

## 3. Wording da ordem destape (máquina #879 intacta)

- [x] 3.1 `FOLLOWUP_REVIEW` em `scripts/process-fsm/subagent_stop.py`: copy exacto da tabela (D2 em `design.md`); espera o par; MUST NOT «autorizar extra / aceitar residual»; poke continua ordem, nunca `concluiu?`
- [x] 3.2 MUST NOT neste grupo: matcher, sidecar path, `loop_count`, classificação por `description` curta, goldens de destape como aceite deste card

## 4. Checklist mecânico (script no pai, não aceite)

- [x] 4.1 Criar `scripts/process-fsm/review_process_checklist.py`: tasks.md sem `- [ ]` pendente; tokens de Design parseáveis (reusa `design_clone_gate.parse_*`); `.cursor/tmp/review-diff.patch` não vazio; intervalo sem aresta nova em `.cursor/process-fsm.yaml`; `--wave-same-turn yes` opcional (ausência/`no` = falha)
- [x] 4.2 Exit ≠ 0 imprime `ERROR: process-checklist failed: <item>` e o pai não commita. MUST NOT pytest novo como aceite; MUST NOT `test_card_895_*`

## 5. Specs

- [x] 5.1 Aplicar deltas `openspec/changes/card-895-review-schema-destape/specs/cursor-harness/spec.md`
- [x] 5.2 Aplicar deltas `openspec/changes/card-895-review-schema-destape/specs/llm-flow-emission/spec.md`
- [x] 5.3 Aplicar deltas `openspec/changes/card-895-review-schema-destape/specs/cursor-code-review/spec.md`

## 6. Higiene de needles existentes (não é aceite)

- [x] 6.1 Se as strings de `FOLLOWUP_REVIEW` ou do runbook se moverem, retunar só os asserts **já existentes** (`test_subagent_stop.py`, `test_card_729_activity_children.py`). Não criar teste novo. Prova de Done = próxima sessão sem relitigar residual de wording do destape como P1 novo, não pytest

## 7. Verify (harness Cursor)

- [x] 7.1 `openspec validate "card-895-review-schema-destape" --type change --strict`
- [x] 7.2 Zero produto / UI; zero `.cursor/process-fsm.yaml`; zero pin / dual-write noutros clientes; zero `AGENTS.md` always-on a crescer; zero HTML proto; zero `CONTEXT.md` / `docs/adr/`; zero arquivo/edição de `openspec/changes/card-893-teto-review-silencio/`
- [x] 7.3 #893/#884/#879/#880 intactos no runbook: teto 1+1 sem Ask, dois reviewers no mesmo turno, intervalo colado, destape máquina, hang Desktop+SSH, spawn-por-task
