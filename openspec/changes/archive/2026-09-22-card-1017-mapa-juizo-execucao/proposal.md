## Why

A lei juízo/execução do spawn Cursor está cravada em skill, harness, specs e testes. Trocar rótulo ou slug exige reescrever esses sítios em vez de um ficheiro versionado.

## Problema

Hoje a lei do spawn Cursor está cravada em três sítios que dizem a mesma coisa: juízo = Grok 4.6 (`cursor-grok-4.6-high`), execução = Composer 2.5 (`composer-2.5`), sem `inherit` do picker. Trocar slug exige editar skill, harness, specs e testes.

Fontes cravadas hoje:

- Tabela em `.cursor/skills/covenant-flow/SKILL.md` (fonte que o pai lê no spawn)
- Ponteiro curto em `.cursor/rules/harness.mdc`
- Specs: `openspec/specs/cursor-harness/spec.md`, `openspec/specs/llm-flow-emission/spec.md`, `openspec/specs/impeccable-design-gate/spec.md`, `openspec/specs/kaizen-continuous-improvement/spec.md`

## História

Como operador do harness Cursor, quero que juízo e execução leiam rótulo e slug de um ficheiro versionado, para eu mudar o mapa sem reescrever a skill.

## Entra

- Ficheiro Cursor-only versionado: `.cursor/model-map.yaml`
- Duas faixas (não mapa por papel). Os papéis ficam na skill; o ficheiro só resolve rótulo + slug:

```yaml
juizo:
  label: Grok 4.6
  slug: cursor-grok-4.6-high
execucao:
  label: Composer 2.5
  slug: composer-2.5
forbid:
  - composer-2.5-fast
  - inherit
```

- Grupo juízo (lê `juizo`): grill-card, design-autor, design-critic, Assessment A, Assessment B
- Grupo execução (lê `execucao`): apply-coluna, qa-gate, diff-reviewer, code-reviewer, busca no mesmo card, fecho-lote
- T16 / chat pai de lote usa o slug de `execucao` (única exceção ao silêncio do picker)
- Runbook `covenant-flow` deixa de cravar slugs; aponta para o ficheiro e lista só o agrupamento de papéis
- `harness.mdc` continua 4–12 linhas; aponta para o ficheiro + skill
- Agent files `diff-reviewer` / `code-reviewer`: pin YAML continua redundante; lei = Task `model` + ficheiro
- Specs Cursor (não as dos outros clientes) e kaizen comparam proxy ao mapa vigente
- Testes que assertam o literal na skill passam a ler o ficheiro; needle `composer-2.5-fast` MUST NOT permanece
- Lei que não muda: sem `inherit`; slug inválido ou ficheiro em falta = recusa visível; destape/resume de execução permanece no slug vigente; host a facturar fast = aborto + spawn novo; troca de modelo = sessão nova (#430); git não força picker do pai

## Não entra

- Grok Build, OpenCode, dsh (continuam inherit)
- Overlay (`.covenant-flow/overlay.yaml`); `clients.*.auto` fica `false`
- Dual-write em `.grok/`, `.dsh/`, `.opencode/`
- Crescimento de `AGENTS.md` ou aresta nova na FSM
- Mapa por papel (grill ≠ design-autor)
- Env var / picker / `clients.cursor.auto`
- Parser de usage Cursor nem dashboard

## What Changes

- Nasce `.cursor/model-map.yaml` (Cursor-only, versionado) com duas faixas `juizo` / `execucao` (rótulo + slug) e `forbid` (`composer-2.5-fast`, `inherit`). Não é mapa por papel.
- O runbook `covenant-flow` deixa de cravar slugs: aponta para o ficheiro e lista só o agrupamento de papéis (juízo vs execução).
- `harness.mdc` permanece 4–12 linhas e aponta para o ficheiro + skill.
- Spawn Cursor lê o slug vigente do ficheiro no parâmetro `model` do Task. Agent files `diff-reviewer` / `code-reviewer`: pin YAML continua redundante; lei = Task `model` + ficheiro.
- Specs Cursor e kaizen passam a comparar o proxy `proxy modelo:` ao mapa vigente (o ficheiro), não a literais cravados na skill.
- Testes que assertam o literal na skill passam a ler o ficheiro; o needle `composer-2.5-fast` MUST NOT permanece.
- Lei intacta: sem `inherit`; ficheiro em falta ou slug inválido = recusa visível; destape/resume de execução permanece no slug vigente; host a facturar fast = aborto + spawn novo; T16 / chat pai de lote usa `execucao.slug`; troca de modelo = sessão nova (#430); git não força picker do pai.

**Não muda / não entra:** Grok Build, OpenCode, dsh (continuam inherit); overlay / `clients.*.auto`; dual-write `.grok/` `.dsh/` `.opencode/`; crescimento de `AGENTS.md`; aresta nova na FSM; mapa por papel; env var / picker; parser de usage Cursor nem dashboard; produto / HTML / protótipo.

## Capabilities

### New Capabilities

- (nenhuma) — o contrato vive nas specs Cursor/emissão/review/kaizen já existentes. Este card não inventa coluna nem capability.

### Modified Capabilities

- `cursor-harness`: nascem `.cursor/model-map.yaml` (duas faixas + `forbid`) e o ponteiro curto em `harness.mdc`; spawn Cursor lê `juizo`/`execucao` do ficheiro; ficheiro em falta ou slug em `forbid` = recusa visível; destape/resume e T16 usam o slug vigente de `execucao`; stubs dos outros clientes continuam inherit.
- `covenant-flow`: o runbook Cursor deixa de cravar slugs; aponta para o ficheiro e lista só o agrupamento de papéis; `AGENTS.md` always-on não cresce.
- `cursor-code-review`: os dois revisores pedem o slug vigente de `execucao` nos dois caminhos de spawn; pin YAML continua redundante; isolamento/intervalo colado/onda no mesmo turno intactos.
- `developer-tooling`: agent files mantêm pin YAML redundante igual a `execucao.slug` do ficheiro; lei = Task `model` + ficheiro; MUST NOT `inherit`.
- `llm-flow-emission`: críticos usam `juizo` vigente; revisores usam `execucao` vigente; o proxy `proxy modelo:` compara-se ao mapa vigente, não à tabela cravada na skill.
- `impeccable-design-gate`: Assessment A/B leem `juizo` do ficheiro, iguais ao Design-autor; MUST NOT herdar o picker.
- `kaizen-continuous-improvement`: `/kaizen release` compara `proxy modelo:` ao mapa vigente em `.cursor/model-map.yaml`.

## Impact

- Cursor: `.cursor/model-map.yaml` (novo); `.cursor/rules/harness.mdc` (orçamento 4–12; aponta ficheiro + skill); `.cursor/skills/covenant-flow/SKILL.md` (agrupamento de papéis, sem slugs cravados); `.cursor/agents/diff-reviewer.md` e `.cursor/agents/code-reviewer.md` (pin YAML redundante, alinhado ao ficheiro); `.cursor/skills/kaizen/SKILL.md` (compara proxy ao ficheiro).
- Specs acima. Goldens em `scripts/process-fsm/test_*.py` que assertam o literal na skill passam a ler o ficheiro; needle `composer-2.5-fast` MUST NOT permanece.
- Sem produto (`backend/` / UI). Sem `.cursor/process-fsm.yaml`. Sem aresta/evento/hook/`enabled_tools` novos. Sem dual-write `.dsh/` / `.grok/` / `.opencode/`. `AGENTS.md` always-on não cresce. Overlay `clients.*.auto` intocado.
- `UI impact: none`. Prototype N/A. Cliente desta sessão é Cursor; Grok/OpenCode/dsh fora do mapa.
