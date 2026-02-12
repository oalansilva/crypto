# Design: Auto-retry do Dev após feedback do Trader

## Overview
Quando o Trader retorna required_fixes, o Dev deve aplicar correções, re-rodar backtest e reenviar para validação. Esse ciclo é limitado por max_retries (default 2).

## Fluxo
1. Trader retorna verdict com required_fixes.
2. Dev aplica correções e reexecuta backtest.
3. Resultado volta para o Trader.
4. Se ainda rejeitado, repetir até max_retries.
5. Ao atingir limite, encerrar com needs_adjustment.

## Componentes

### 1) Loop de retry pós-Trader
- Nova lógica no lab_graph para detectar required_fixes.
- Incrementa contador trader_retry_count no run.

### 2) Limite de tentativas
- max_retries default = 2 (pode vir do input).
- Ao exceder, marca status needs_adjustment.

### 3) Trace
- Eventos: trader_retry_started, trader_retry_applied, trader_retry_limit.

## Riscos
- Aumento de tempo/custo em runs longos.
- Necessário garantir que o Dev use métricas reais do contexto.
