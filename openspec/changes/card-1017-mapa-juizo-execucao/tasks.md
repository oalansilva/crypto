## 1. Mapa e harness always-on

- [x] 1.1 Criar `.cursor/model-map.yaml` com o conteúdo exacto da D1 em `design.md` (`juizo` / `execucao` / `forbid`)
- [x] 1.2 Substituir o corpo de `.cursor/rules/harness.mdc` pelo texto exacto da D2 (5 linhas não-vazias após o frontmatter; orçamento 4–12; `alwaysApply: true` intacto; aponta ficheiro + skill; sem slugs)

## 2. Runbook Cursor e kaizen

- [x] 2.1 Em `.cursor/skills/covenant-flow/SKILL.md`: remover a tabela `| Papel | Rótulo | Slug |`; apontar para `.cursor/model-map.yaml`; listar só o agrupamento juízo/execução (D3)
- [x] 2.2 No mesmo skill: destape/resume e T16/fecho-lote leem `execucao.slug` vigente; needle `composer-2.5-fast` MUST NOT permanece; MUST NOT cravar `cursor-grok-4.6-high` nem `composer-2.5` como mapa
- [x] 2.3 MUST NOT crescer `AGENTS.md`. MUST NOT dual-write `.grok/` / `.opencode/` / `.dsh/`. Overlay e `clients.*.auto` intocados. Pin citado permanece `v1.1.16`
- [x] 2.4 `.cursor/skills/kaizen/SKILL.md`: `/kaizen release` compara `proxy modelo:` a `.cursor/model-map.yaml`; sem parser de usage; sem dashboard

## 3. Agent files

- [x] 3.1 `.cursor/agents/diff-reviewer.md` e `.cursor/agents/code-reviewer.md`: pin YAML = `execucao.slug` do ficheiro; `readonly: true` intacto; corpo (intervalo, FINDING, teto) intacto; MUST NOT `inherit`

## 4. Specs

- [x] 4.1 Aplicar delta `specs/cursor-harness/spec.md`
- [x] 4.2 Aplicar delta `specs/covenant-flow/spec.md`
- [x] 4.3 Aplicar delta `specs/cursor-code-review/spec.md`
- [x] 4.4 Aplicar delta `specs/developer-tooling/spec.md`
- [x] 4.5 Aplicar delta `specs/llm-flow-emission/spec.md`
- [x] 4.6 Aplicar delta `specs/impeccable-design-gate/spec.md`
- [x] 4.7 Aplicar delta `specs/kaizen-continuous-improvement/spec.md`

## 5. Goldens (não é aceite)

- [x] 5.1 Se asserts já existentes em `scripts/process-fsm/test_*.py` partirem (literal de slug na skill), retunar para `yaml.safe_load` de `.cursor/model-map.yaml`. Needle `composer-2.5-fast` MUST NOT permanece. Pin dos agent files compara-se a `execucao.slug`
- [x] 5.2 MUST NOT `test_card_1017_*`. MUST NOT editar `subagent_stop.py` / `process-fsm.yaml` / Guard. Stubs Grok/OpenCode/dsh: verificar inherit, ≤8 linhas, sem copiar o mapa

## 6. Verify (harness Cursor)

- [x] 6.1 `openspec validate "card-1017-mapa-juizo-execucao" --type change --strict`
- [x] 6.2 Zero produto / UI / HTML proto; zero aresta FSM; zero pin a subir; zero dual-write noutros clientes; zero `AGENTS.md` a crescer; isolamento/destape/Q2–Q6/teto 1+1 dos filhos já existentes intactos
- [x] 6.3 `pytest` focado dos goldens alterados (se 5.1 mexer). Skills canónicas: `.cursor/skills/`
