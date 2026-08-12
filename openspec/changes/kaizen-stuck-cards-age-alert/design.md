# Design: Triagem de cards presos + alerta de idade no guard

## Context

Card #195 preso em `Em Refinamento` desde 2026-05-12 (3ª auditoria reportando o mesmo card). Não existe alerta automatizado por idade de coluna; a detecção depende de inspeção manual no `release-guard audit`/kaizen. O guard (`scripts/release-guard`) é um script bash com modos `audit|pre|post`, já usando `gh` e `jq`.

UI impact: **none** (mudança de script de processo + ação pontual de triagem; nenhuma superfície visual).

## Goals / Non-Goals

**Goals**
- Triar o #195 com comentário de decisão.
- `release-guard audit` lista cards por coluna com idade (dias) e emite warn para >30 dias.
- Sem regressão no fluxo pre/post do guard.

**Non-Goals**
- Não automatizar a triagem de cards (decisão continua humana, em board).
- Não mudar os modos `pre`/`post` (warn somente em `audit`).

## Decisions

### D1 — Fonte de idade: `gh project item-list` + campo de atualização do item
O `item-list --format json` já expõe o card com `status` e dados de atualização; a idade é calculada como `(hoje - updated_at)`. Colunas sem timestamp confiável caem no cenário de warn de falha de obtenção (spec).
- Alternativa: GitHub API de issues (`updated_at` da issue) — não cobre cards sem issue vinculada e mistura atualização de issue com atividade do board. Rejeitado.

### D2 — Warn informativo em `audit`, silencioso em `pre`/`post`
O inventário de idade roda apenas em `audit` (modo diagnóstico). Em `pre`/`post` não é executado, preservando o contrato atual do guard (warn só onde Alan usa para diagnóstico).
- Alternativa: incluir em `pre`/`post` como warn — adicionaria ruído ao fechamento de release; rejeitado nesta change (pode ser elevado depois por decisão kaizen).

### D3 — Triagem do #195 manual com evidência no card
A triagem é decisão de produto/processo: avançar para `Todo` com prioridade, cancelar ou transferir — executada por Alan/agente com comentário de decisão registrado (script helper `post-card-evidence-comment.sh` não se aplica; usar `gh issue comment`/comentário no card com motivo e prioridade) e registro em `docs/kaizen-log.md`.

## Risks / Trade-offs

- [Cards com atividade contínua mas sem `updated_at` confiável geram falso positivo] → Mitigação: cenário de falha emite warn de obtenção, não bloqueio; documento limiar de 30 dias como informativo.
- [Warn de idade vira ruído com muitos cards antigos legítimos] → Mitigação: limite por coluna (máx. N por coluna) e mensagem clara; classificação fica no kaizen, não no guard.

## Migration Plan

1. Adicionar bloco `card_age_inventory` ao guard (modo `audit`).
2. Rodar `scripts/release-guard audit` e validar saída com cards reais do board.
3. Executar triagem do #195 (decisão com Alan se necessário) + comentário + kaizen-log.
4. Rollback: remoção do bloco não afeta pre/post.

## Open Questions

- Prioridade/triagem do #195: Alan decide avançar para `Todo`, cancelar ou transferir? (aguarda Alan na aprovação de design — ação só após `Pronto para Dev` ou decisão direta no board).

## Prototype

**N/A** — mudança de script de processo (`release-guard audit`) + ação pontual de triagem no board; nenhuma superfície visual nova ou alterada. Não há tela, componente ou fluxo de UI envolvido.

## Impeccable

- `Impeccable Brief`: N/A — `UI impact: none` (justificativa: script bash de diagnóstico + triagem de card; zero superfície visual).
- `Impeccable Critique`: N/A — sem superfície visual para criticar.
- `Impeccable Audit`: N/A — sem UI para acessibilidade/performance/responsividade/theming.
- `Impeccable Trace`: N/A — nenhum CLI/payload de UI aplicado.

## Design Critique

**Escopo:** 1) triagem do #195 com comentário de decisão; 2) bloco `card_age_inventory` no `release-guard audit` com warn de idade >30 dias por coluna.

**Achados por dimensão:**
- **Escopo:** claro e enxuto (S). Bloco restrito ao modo `audit` — sem regressão em `pre`/`post` (contrato atual preservado). OK.
- **Regressão de produto:** nenhuma superfície de produto afetada; guard é ferramenta operacional. Risco de falso positivo em cards legítimos com atividade contínua mitigado por limiar informativo + limite por coluna. OK.
- **Riscos operacionais:** a triagem do #195 é decisão humana (Alan) — o card não pode ser triado automaticamente por agente sem decisão explícita; o design deixa a triagem como tarefa do card e registra que a ação depende de decisão de Alan (dependência explícita registrada em Open Questions). O guard continua fail-closed apenas em pre/post; o inventário de idade é warn informativo. OK.
- **Superfície visual:** confirmado `UI impact: none` — nenhum componente, rota ou estilo alterado. Nenhuma superfície visual ficou sem classificação. OK.

**Correções realizadas:** nenhuma necessária após a crítica (design já restringia o bloco a `audit` e marcava a triagem como decisão humana).

**Pendências não bloqueantes:** limiar de 30 dias é informativo; pode ser calibrado após uso real (registro kaizen futuro).

**Design Agent verdict: PASS** — `UI impact: none`, sem achados bloqueantes, decisão de triagem dependente de Alan registrada.
