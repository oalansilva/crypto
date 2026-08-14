## Why

No card #463, o título do board ("erro ao comprar ativo diz que nao tenho saldo em usdt") divergiu do título da issue ("Bug: compra falha com Saldo livre em USDT insuficiente...") após rename pós-`Done`; o `Title` de item vinculado a issue não é editável via API Projects v2, então foi postada uma nota de sincronização sem aprovação explícita. A regra de renomeação não está documentada e o guard não detecta a divergência, deixando o processo dependente de auditoria manual.

## What Changes

- `AGENTS.md` documenta o fluxo de rename de issue com card no board: renomear a issue exige nota de divergência no card (motivo + aprovação), pois o título do board não é editável via API.
- `scripts/release-guard audit` emite warn quando o título do board difere do título da issue sem nota de divergência registrada no card.
- Nota do #463 mantida como registro histórico (nenhuma ação no card).
- Nenhuma regressão no fluxo normal do guard.

## Capabilities

### New Capabilities
- `kaizen-board-issue-rename-note`: detecção de divergência board/issue sem nota no `release-guard audit`.

### Modified Capabilities
- `board-issue-title-sync`: documenta o fluxo de rename com nota obrigatória no card e passa a ser verificada automaticamente pelo guard (warn).

## Impact

- **Docs**: `AGENTS.md` (regra de rename com nota de divergência).
- **Scripts**: `scripts/release-guard` (novo check de divergência board/issue em `audit`).
- **Dependências**: `gh` e `jq` (já utilizados pelo guard).
