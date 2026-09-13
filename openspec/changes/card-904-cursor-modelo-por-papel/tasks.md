## 1. Harness always-on (Cursor)

- [x] 1.1 Substituir o corpo de `.cursor/rules/harness.mdc` pelo texto exacto da D2 em `design.md` (5 linhas não-vazias após o frontmatter; orçamento 4–12; `alwaysApply: true` intacto)
- [x] 1.2 Confirmar que o corpo aponta juízo/execução e skill `covenant-flow`, não diz que todo Task herda, não cola a tabela, não menciona `diff-reviewer` / `release-guard` / `T1/T7/T15`

## 2. Runbook Cursor

- [x] 2.1 Em `.cursor/skills/covenant-flow/SKILL.md`: deixar de mandar inherit de modelo; lei = parâmetro `model` do Task nos dois caminhos; colar o mapa da D1 (juízo `cursor-grok-4.6-high`, execução `composer-2.5`; fast FORA; revisores no Grok FORA)
- [x] 2.2 No mesmo skill, prompts autocontidos: o pai passa o slug; silêncio sobre picker do pai; ensaio do pai em Composer fora
- [x] 2.3 No mesmo skill, filho isolado `fecho-lote`: `description` canónica `fecho-lote kaizen`; `model: composer-2.5`; MUST NOT `process_event`; pai chama T16 no mesmo turno; MUST NOT sidecar; MUST NOT needle novo no classificador de destape
- [x] 2.4 No mesmo skill, handoff: uma linha `proxy modelo: <papel> → <rótulo> (<slug>)` por spawn
- [x] 2.5 MUST NOT crescer `AGENTS.md`. MUST NOT dual-write `.grok/` / `.opencode/` / `.dsh/`. Pin citado = `v1.1.15` (se o Apply tocar a linha S1 que ainda diz `v1.1.14`, corrigir — detalhe de Apply)

## 3. Agent files e kaizen

- [x] 3.1 `.cursor/agents/diff-reviewer.md` e `.cursor/agents/code-reviewer.md`: `model: composer-2.5`; `readonly: true` intacto; corpo (intervalo, FINDING, teto) intacto
- [x] 3.2 `.cursor/skills/kaizen/SKILL.md`: `/kaizen release` lê `proxy modelo:` nos comentários REST do pacote e compara com a tabela vigente; sem parser de usage; sem dashboard

## 4. Specs

- [x] 4.1 Aplicar delta `specs/cursor-harness/spec.md`
- [x] 4.2 Aplicar delta `specs/cursor-code-review/spec.md`
- [x] 4.3 Aplicar delta `specs/developer-tooling/spec.md`
- [x] 4.4 Aplicar delta `specs/covenant-flow/spec.md`
- [x] 4.5 Aplicar delta `specs/llm-flow-emission/spec.md`
- [x] 4.6 Aplicar delta `specs/impeccable-design-gate/spec.md`
- [x] 4.7 Aplicar delta `specs/kaizen-continuous-improvement/spec.md`

## 5. Higiene de goldens (não é aceite)

- [x] 5.1 Se asserts já existentes em `scripts/process-fsm/test_*.py` partirem (`model: inherit` nos agent files, `Task inherit` no harness), retunar só esses needles. MUST NOT `test_card_904_*`. MUST NOT editar `subagent_stop.py` / `process-fsm.yaml` / Guard
- [x] 5.2 Stubs Grok/OpenCode/dsh: verificar que continuam inherit, ≤8 linhas, sem a tabela

## 6. Verify (harness Cursor)

- [x] 6.1 `openspec validate "card-904-cursor-modelo-por-papel" --type change --strict`
- [x] 6.2 Zero produto / UI / HTML proto; zero aresta FSM; zero pin a subir; zero dual-write noutros clientes; zero `AGENTS.md` a crescer; isolamento/destape/Q2–Q6/teto 1+1 dos filhos já existentes intactos
- [x] 6.3 Prova viva (não pytest): Apply-coluna #904 com `composer-2.5` + Design-crítico ou grill com `cursor-grok-4.6-high`, host `completed`, nos dois modos Cursor (terminal e Desktop+SSH). Cloud / Auto / `composer-2.5-fast` fora

## 7. T18 — destape/resume slug + release chat Composer (prova 2026-09-12)

- [x] 7.1 `design.md`: decisões T18 (destape/resume keep-slug; release chat = Composer 2.5) + `## Apply contract`
- [x] 7.2 Deltas `openspec/changes/.../specs/cursor-harness` e `covenant-flow` (requisitos ADDED T18)
- [x] 7.3 Fundir o mesmo texto em `openspec/specs/cursor-harness` e `openspec/specs/covenant-flow`
- [x] 7.4 `.cursor/skills/covenant-flow/SKILL.md`: mapa intacto; duas leis T18; `composer-2.5-fast` FORA inclusive destape/resume; excepção picker só no chat de release/lote
- [x] 7.5 `.cursor/skills/kaizen/SKILL.md`: `/kaizen release` nota picker pai Composer para T16/fecho-lote
- [x] 7.6 Goldens `scripts/process-fsm/test_paging.py` e/ou `test_subagent_stop.py` (needles destape/resume + recusa T16 em pai Grok). MUST NOT `test_card_904_*`
- [x] 7.7 `openspec validate "card-904-cursor-modelo-por-papel" --type change --strict`
- [x] 7.8 `pytest` focado dos goldens alterados
