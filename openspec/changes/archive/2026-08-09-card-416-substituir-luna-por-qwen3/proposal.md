## Why

O roteamento visual do opencode usa `opencode-go/gpt-5.6-luna` como modelo fixo do agente `vision` (única exceção à herança de modelo da sessão). Alan definiu a troca para `opencode-go/qwen3.7-plus`, disponível no mesmo provider `opencode-go` com o mesmo formato de ID, garantindo substituição direta sem mudança de infraestrutura.

## What Changes

- Trocar o ID do modelo de referência do roteamento visual de `opencode-go/gpt-5.6-luna` para `opencode-go/qwen3.7-plus` em:
  - `.opencode/agent/vision.md` (frontmatter `model` e descrição)
  - `.opencode/plugin/vision-router.ts` (constante `VISION_MODEL_ID` e textos de delegação)
  - `.opencode/commands/vision.md` (comando `/vision`)
  - `AGENTS.md` e `rules.md` (exceção de roteamento visual)
  - `openspec/specs/visual-analysis-routing/spec.md` — sync da spec canônica no archive do fechamento (fluxo canônico OpenSpec; delta spec fica em `openspec/changes/<change>/specs/` durante a change)
- Atualizar a descrição do subagent `vision` no sistema (`description`) para refletir o novo modelo.
- Sem mudança de comportamento do plugin: roteamento automático, placeholder de imagem e evidência em `.impeccable/vision-router.jsonl` permanecem iguais.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `visual-analysis-routing`: o modelo fixo de referência do roteamento visual muda de `opencode-go/gpt-5.6-luna` para `opencode-go/qwen3.7-plus` (requirement de roteamento automático e agente `vision` com modelo fixo).

## Impact

- Infraestrutura/roteamento LLM do opencode (`.opencode/`): agente, plugin, comando e docs de processo (`AGENTS.md`, `rules.md`).
- Spec OpenSpec `visual-analysis-routing` (delta spec) e archive da change no fechamento.
- Sem impacto em produto, banco, API ou frontend. `UI impact: none`.
