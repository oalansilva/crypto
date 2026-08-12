## Why

Card #195 ("Backup de ambiente") está preso em `Em Refinamento` desde 2026-05-12 sem decisão de triagem — terceira auditoria reportando o mesmo card sem nenhum alerta automatizado por idade de coluna. O fluxo depende de inspeção manual para detectar cards presos, e a repetição do mesmo achado a cada release indica que a fricção não foi resolvida por processo.

## What Changes

- Triagem do #195 (avançar para `Todo` com prioridade, cancelar ou transferir) com comentário de decisão no card.
- `scripts/release-guard audit` ganha inventário de cards por coluna com idade (dias desde última atualização), emitindo warn para cards com >30 dias sem atualização por coluna.
- Nenhuma regressão no fluxo normal do guard (pre/post inalterados, warn apenas em audit).

## Capabilities

### New Capabilities
- `kaizen-stuck-card-age-alert`: alerta de idade por coluna no `release-guard audit`, com warn informativo para cards presos.

### Modified Capabilities
- `kaizen-continuous-improvement`: o guard passa a incluir inventário de cards presos por coluna como fonte de achados de auditoria.

## Impact

- **Scripts**: `scripts/release-guard` (novo sub-inventário de idade de cards, somente em `audit`).
- **Board**: triagem do card #195 com comentário de decisão (uma ação pontual, não automatizada).
- **Docs**: `docs/kaizen-log.md` registra a triagem.
- **Dependências**: `gh` e `jq` (já utilizados pelo guard).
