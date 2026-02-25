# Change Proposal: Auto-retry do Dev após feedback do Trader

## Why

Hoje o fluxo encerra quando o Trader retorna problemas, mas o Dev não corrige automaticamente. Isso interrompe a iteração natural do Lab e aumenta o trabalho manual do usuário.

## What Changes

- Adicionar ciclo Dev → correção → backtest quando o Trader retornar required_fixes.
- Limitar o número de tentativas (default 2) para evitar loops infinitos.
- Registrar no trace cada retry e o motivo das correções.

## Capabilities

### New Capabilities
- dev-retry-after-trader: Auto-retry do Dev após feedback do Trader, com limite de tentativas e rastreio.

### Modified Capabilities
- backend: fluxo do Lab passa a reexecutar o Dev após feedback do Trader.

## Impact

- Backend (Lab graph e execução do Dev)
- Logs/trace do run
- UX do Lab (mais iterações automáticas antes de nova validação)
