## Context

O opencode deste repo roteia toda análise de imagem para o subagent `vision` (`.opencode/agent/vision.md`) com `model: opencode-go/gpt-5.6-luna` fixo — exceção única e registrada à herança de modelo da sessão (`deepseek-v4-flash` sem visão). O plugin `vision-router` (`.opencode/plugin/vision-router.ts`) detecta imagens no contexto, substitui pixels por placeholder com caminho do arquivo e instrui a delegação ao `vision`; evidência em `.impeccable/vision-router.jsonl`. O comando `/vision` (`.opencode/commands/vision.md`) aciona o mesmo agente para análise explícita.

Alan decidiu trocar o modelo de referência para `opencode-go/qwen3.7-plus` (card #416). O provider `opencode-go` expõe o ID `opencode-go/qwen3.7-plus` no mesmo formato do Luna, permitindo substituição direta.

**UI impact: none** — mudança de infraestrutura de roteamento LLM; nenhuma superfície visual de produto é criada, alterada ou removida. Não há superfície nova nem alteração de comportamento de UI observável.

## Goals / Non-Goals

**Goals:**
- Trocar o ID de referência do roteamento visual para `opencode-go/qwen3.7-plus` em todos os pontos ativos (agente, plugin, comando, docs, spec).
- Preservar integralmente o comportamento do roteamento: detecção de imagem, placeholder, delegação, log em `.impeccable/vision-router.jsonl`.
- Deixar o repo sem referências ativas a `gpt-5.6-luna` (histórico arquivado pode reter).

**Non-Goals:**
- Não alterar o modelo default da sessão (`deepseek-v4-flash`).
- Não mudar regras de herança de modelo dos demais subagents (exceto a exceção visual).
- Não mexer em UI/UX, banco, API ou frontend.
- Não refatorar o plugin `vision-router` além da troca de ID/textos.

## Decisions

1. **Alvo: `opencode-go/qwen3.7-plus`** — mesmo provider do Luna, formato de ID idêntico, substituição direta sem mudança de auth/infra. Alternativa considerada: `opencode-go/mimo-v2.5` (descartado por decisão de Alan em 2026-08-09).
2. **Único ponto de verdade do ID no plugin:** manter a constante `VISION_MODEL_ID` em `.opencode/plugin/vision-router.ts` — textos de delegação usam o mesmo valor; nada hardcoded fora da constante (quando possível) e docs referenciando o ID canônico.
3. **Suporte a imagens (`attachment: true`) do `qwen3.7-plus`:** não verificável via models.dev (provider fora da base pública); será validado em runtime na implementação com delegação real de uma imagem ao subagent `vision`. Se `attachment: false` for observado, bloquear e reportar antes de fechar (registrado em tasks).
4. **Docs de processo:** atualizar `AGENTS.md` e `rules.md` nas seções de exceção de roteamento visual para refletir `opencode-go/qwen3.7-plus`, mantendo o texto de comportamento (delegação automática, `/vision`, evidência `.impeccable/vision-router.jsonl`).
5. **Spec:** delta spec em `openspec/changes/card-416-substituir-luna-por-qwen3/specs/visual-analysis-routing/spec.md` alterando o requirement de modelo de referência; sincronização em `openspec/specs/` no archive.

## Risks / Trade-offs

- [Modelo novo sem suporte a imagens (`attachment: false`)] → Mitigação: task de validação runtime obrigatória antes de qualquer conclusão; se falhar, bloquear e reportar a Alan (troca de alvo).
- [Qualidade de julgamento visual diferente do Luna em `diff.png`/baselines] → Mitigação: smoke com uma imagem real (`/vision`) e validação do fluxo no QA do próprio card; ajustes de prompt ficam em card futuro se necessário.
- [Referência residual a `gpt-5.6-luna` em docs/código ativo] → Mitigação: grep de bloqueio no QA (`gpt-5\.6-luna` sem ocorrência em arquivos ativos, exceto histórico em `openspec/changes/archive/`).
- [Plugin com texto de delegação desatualizado confunde a sessão] → Mitigação: atualizar todas as strings de delegação na mesma rodada da constante (unit do plugin cobre).

## Prototype

**N/A** — `UI impact: none`: mudança de infraestrutura de roteamento LLM sem superfície visual nova, alterada ou removida. Não há tela, componente, estado ou interação a prototipar; validação será técnica (runtime + testes).

## Design Critique

Crítica independente (escopo enxuto, sem UI):

- **Escopo:** correta a classificação como infraestrutura/roteamento; todos os pontos ativos de referência ao Luna mapeados (agente, plugin, comando, `AGENTS.md`, `rules.md`, spec). Sem superfície visual nova — não há risco de fidelidade/delta.
- **Regressão de produto:** roteamento automático, placeholder de imagem e log `.impeccable/vision-router.jsonl` são comportamento existente e ficam intactos; único delta é o ID do modelo. Risco de regressão baixo, mitigado por unit do plugin + teste real de delegação.
- **Riscos operacionais:** (a) `attachment: true` do `qwen3.7-plus` não verificado — tratado como pré-requisito de runtime na implementação, com bloqueio explícito se falhar; (b) referências residuais ao Luna — grep de bloqueio no QA.
- **UI/UX:** sem impacto; nenhuma tela/estado afetado. `Impeccable` registrado como `N/A` (infraestrutura, sem pipeline visual aplicável).

Achados bloqueantes: nenhum. Pendências não bloqueantes: validar suporte a imagem em runtime (task 1.3) e conferir unit do plugin com o novo ID (task 2.2).

**Design Agent verdict: PASS** — evidência enxuta completa para `UI impact: none`; aguardando aprovação humana de Alan.
