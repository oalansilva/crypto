## 1. S1 — cola do diff (agentes + runbook)

- [x] 1.1 Em `.cursor/agents/diff-reviewer.md` e `.cursor/agents/code-reviewer.md`: manter `readonly: true` / `model: inherit`; exigir intervalo via `review_diff_path:` e/ou `## Diff`; se ambos vazios, imprimir exactamente `ERROR: review-diff missing` e parar; MUST NOT git; MUST NOT Glob/listar `agent-transcripts`; MUST NOT inventar o intervalo no working tree
- [x] 1.2 Em `.cursor/skills/covenant-flow/SKILL.md` (coluna Code Review): o pai materializa pré-commit (`git diff HEAD` + untracked) e fecho (`git diff origin/develop...HEAD`) em `.cursor/tmp/review-diff.patch` e cola `review_diff_path:` no spawn; MUST NOT pedir git ao filho; pin overlay permanece `v1.1.14`; stubs Grok/dsh/OpenCode sem dual-write da lei

## 2. S2 — destape `subagentStop`

- [x] 2.1 Criar `scripts/process-fsm/subagent_stop.py` com as guardas AND (status=completed, loop_count=0, sidecar matching, classificador das quatro etapas **mais** Design-autor / Design-crítico / Assessment A/B) e os seis `followup_message` exactos do `design.md`; `error`/`aborted` / ainda a trabalhar / explore/shell → `{}`; fail-open; MUST NOT destapar `aborted`
- [x] 2.2 Criar `.cursor/hooks/process-fsm-subagent-stop.sh` (locator cwd-independente + venv/`python3`, padrão sessionStart) que invoca esse módulo
- [x] 2.3 Em `.cursor/hooks.json`: entrada `subagentStop` (command do 2.2, matcher `generalPurpose|diff-reviewer|code-reviewer`, `loop_limit: 32`, sem `failClosed`); MUST NOT `subagentStart`; Guard / sessionStart / Impeccable intactos
- [x] 2.4 No mesmo `covenant-flow` SKILL.md: pai grava `.cursor/tmp/awaiting-task.json` antes do Task das quatro etapas **e** do Task Design-autor / crítico / Assessment A/B, e apaga ao tratar o resultado; poke = ordem (proibido `concluiu?` / `já acabou?`); background, `error`/`aborted` e filho ainda a trabalhar fora; staff não re-prompt enquanto o filho corre; `AGENTS.md` e overlay `clients.*.auto` intocados; sem aresta em `process-fsm.yaml`

## 3. Goldens pytest

- [x] 3.1 `scripts/process-fsm/test_subagent_stop.py`: completed+sidecar para grelha/Apply/review/QA/Design-autor/Design-crítico → ordem certa; sem sidecar / error|aborted / ainda a trabalhar / loop_count>0 / parallel worker → `{}`; MUST NOT golden «Design-autor → {}» como regra
- [x] 3.2 Estender `test_paging.py` e/ou `test_guard.py`: `hooks.json` tem `subagentStop` composto; sem `subagentStart` de destape; Guard failClosed e Impeccable permanecem
- [x] 3.3 Asserts nos dois agentes: `ERROR: review-diff missing`, MUST NOT git, MUST NOT transcripts; `pytest scripts/process-fsm/test_subagent_stop.py scripts/process-fsm/test_paging.py scripts/process-fsm/test_guard.py -q` verde

## 4. Fora de escopo (confirmação)

- [x] 4.1 Diff deste card sem `backend/`, `frontend/src/`, `.cursor/process-fsm.yaml`, `AGENTS.md`, overlay `clients.*.auto`, pin, lei em `.dsh/`, protótipo HTML, `subagentStart`
- [x] 4.2 `openspec validate --change card-879-destapar-pai-colar-diff` verde; `UI impact: none` + `live_route: N/A` justificado + `surface: new`, sem proto dir → clone gate local True

## 5. P1 matcher named reviewers + P2 classify sem prompt longo

- [x] 5.1 Matcher `subagentStop`: `generalPurpose|diff-reviewer|code-reviewer`; `loop_limit: 32`; sem `failClosed`; sem `subagentStart`
- [x] 5.2 Skill S1/S2: pai MAY spawnar reviewers como `generalPurpose` (corpo do agent file) **ou** `subagent_type` nomeado; destape cobre os dois; `review_diff_path:` + sidecar `description` exacta
- [x] 5.3 Classificar só sidecar.description ∪ stop.task ∪ `subagent_type`; MUST NOT do prompt longo; golden grill + skill colado com `design-autor`/`diff-reviewer` → FOLLOWUP_GRILL
