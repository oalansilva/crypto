Skills canónicas: `.cursor/skills/` (e, no Grok, a ponte em `.grok/skills/` que manda ler o canónico). Não marcar estas tasks durante o Design.

## 1. Mapa compartilhado

- [x] 1.1 Em `.cursor/model-map.yaml`, acrescentar `juizo.grok` (label `Grok 4.7`, slug `grok-4.7`, `effort: high`) e `execucao.grok` (label `Grok 4.6`, slug `grok-4.6`, `effort: high`) como irmãos de `codex`, conforme a D1 de `design.md`
- [x] 1.2 Não alterar label/slug de topo do Cursor, os blocos `codex` (`gpt-6-sol` / high, `gpt-6-luna` / max) nem `forbid`. `codex_models.py` `PIN_PAIRS` / `resolve_pair` / `pin_codex_map` não passam a ler nem a apagar `.grok`

## 2. Runbook canónico

- [x] 2.1 Em `.cursor/skills/covenant-flow/SKILL.md`, apagar a frase exacta `Revisores no Grok MUST NOT neste card.`
- [x] 2.2 No mesmo skill: no Grok, juízo lê `juizo.grok` e execução lê `execucao.grok`; `spawn_subagent` passa `model`; não omite `model`; não herda o picker; os dois revisores e `fecho-lote` são execução (`grok-4.6`); fechar release no Grok exige pai `grok-4.6` e recusa pai `grok-4.7` ou outro slug; retomada de execução noutro modelo que não `grok-4.6`, inclusive `grok-4.7-build-fast`, falha e nasce de novo em `grok-4.6`
- [x] 2.3 Manter a agulha `composer-2.5-fast` MUST NOT. Não crescer `AGENTS.md`. Não dual-write do runbook em `.grok/rules/`, `.opencode/` ou `.dsh/`. Não subir o pin `v1.1.19`. Não mexer em `clients.*.auto`

## 3. Stubs Grok

- [x] 3.1 Em `scripts/process-fsm/grok_stubs.py`, a ponte deixa de mapear Task `inherit` para `spawn_subagent` inherit e passa a mandar `model` de `juizo.grok` ou `execucao.grok` (D6). Regenerar `.grok/skills/**/SKILL.md`. Corpo ≤8 linhas. Sem tabela de papéis
- [x] 3.2 Stubs OpenCode e dsh continuam inherit. Não copiam o par do Grok

## 4. Specs

- [x] 4.1 Aplicar o delta `specs/cursor-harness/spec.md` (par `grok`, papéis, fecho, revisores, retomada)
- [x] 4.2 Aplicar o delta `specs/covenant-flow/spec.md`
- [x] 4.3 Aplicar o delta `specs/process-harness/spec.md`
- [x] 4.4 Aplicar o delta `specs/cursor-code-review/spec.md` (pin YAML dos agent files Cursor permanece `composer-2.5`)
- [x] 4.5 Aplicar o delta `specs/llm-flow-emission/spec.md`
- [x] 4.6 Aplicar o delta `specs/impeccable-design-gate/spec.md` (este card não corre A/B)
- [x] 4.7 Aplicar o delta `specs/kaizen-continuous-improvement/spec.md`

## 5. Kaizen

- [x] 5.1 Em `.cursor/skills/kaizen/SKILL.md`, `/kaizen release` compara `proxy modelo:` do Grok a `juizo.grok` / `execucao.grok` e o do Cursor às faixas de topo. Um revisor Grok em `grok-4.6` não é achado por diferir de `composer-2.5`. Sem parser de usage e sem dashboard

## 6. Goldens

- [x] 6.1 Se asserts já existentes partirem (frase `Revisores no Grok MUST NOT neste card` ou `spawn_subagent` inherit nos stubs Grok), retunar para a ponte nova e para o par `grok`. Não criar `test_card_1061_*` como aceite. Não editar `process-fsm.yaml`, Guard nem `subagent_stop.py`

## 7. Verify

- [x] 7.1 `openspec validate "card-1061-grok-mapa" --type change --strict` (o Design já corre o validate; o Apply repete depois das edições)
- [x] 7.2 Zero produto / UI / HTML. Zero aresta FSM. Zero push forçado de `b2cac2d5`. Zero mover Status para Todo. Pares Cursor e Codex intactos. OpenCode e dsh continuam inherit
- [x] 7.3 `pytest` focado dos goldens alterados, se 6.1 mexer
