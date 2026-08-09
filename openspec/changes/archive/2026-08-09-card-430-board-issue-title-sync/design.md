# Design — card-430-board-issue-title-sync

## Context

Card #416: título do board "Substituir gpt-5.6-luna por MiMo-V2.5" vs issue "…Qwen3.7 Plus" vs implementação `qwen3.7-plus` (F-3). E após o merge #419 (00:39Z) definir `vision.md = qwen3.7-plus`, spawns de vision às 00:41/00:44Z ainda usaram `gpt-5.6-luna` — a configuração do subagent é lida no spawn a partir da sessão/worktree antiga (F-4).

## Escopo

- Regra de fechamento: título board == título issue no `Done` (ou comentário registrando divergência aprovada).
- Documentação: troca de modelo de subagent exige nova sessão; auditoria kaizen adiciona sinal "modelo antigo pós-merge".
- Fora de escopo: renomear o título do #416 no board (ação pontual de Alan/PO).

## UI impact

`UI impact: none` — regras/fluxo/auditoria; nenhuma superfície visual. Prototype: `N/A`.

## Decisões

- **D1 — Sync no fechamento, não contínuo.** No momento do `Done`, o agente sincroniza o título do board com a issue (via `gh issue edit`/board) ou registra divergência aprovada em comentário. Alternativa (validação a cada movimentação) custosa e barulhenta.
- **D2 — Sinal de auditoria "modelo antigo pós-merge".** O subagent kaizen compara o modelo reportado em sessões/spawns da release com a configuração vigente dos arquivos de agente no commit HEAD; divergência após merge do modelo = sinal reportado. Alternativa (bloquear spawns) inviável tecnicamente — configuração é lida no spawn.
- **D3 — Documentação de "troca de modelo exige nova sessão".** Regra no AGENTS.md: após merge que altera modelo de subagent, iniciar nova sessão/worktree para que a configuração nova seja carregada.

## Riscos

- [Sync automático sobrescrever título aprovado do board] → Mitigação: o sync usa o título da issue como canônico; divergência aprovada exige comentário explícito.
- [Sinal de auditoria impreciso em sessões legadas] → Mitigação: sinal é informativo na auditoria, sem bloqueio; janela de comparação = release atual.

## Design Critique

- **Escopo**: cobre os dois sintomas (título divergente e modelo antigo pós-merge) com regras leves de fechamento/auditoria.
- **Regressão de produto**: nenhuma — fluxo de processo.
- **Riscos operacionais**: troca de modelo em sessões em voo é limitação da ferramenta; a regra documenta o comportamento real em vez de prometer propagação.
- **Pendências não bloqueantes**: renomeação do #416 fica para Alan/PO (fora de escopo).
- **Impeccable**: `N/A` — sem superfície visual; justificativa: `UI impact: none`.

**Design Agent verdict: PASS** — evidência completa, sem achado bloqueante.
