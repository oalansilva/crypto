# Change: Suporte a backtest em Short (template multi_ma_crossover)

## Why

Hoje o sistema executa backtests apenas em **long**: os sinais de entrada (ex.: crossover short/medium com short > long no template `multi_ma_crossover`) abrem posição comprada e os sinais de saída fecham essa posição. Não é possível testar a mesma lógica em **short** (venda a descoberto), o que limita a avaliação de estratégias em mercados em queda ou em templates que fazem sentido invertidos. Permitir teste em short, começando pelo template `multi_ma_crossover`, amplia a utilidade do sistema sem alterar o comportamento long atual.

## What Changes

- Adicionar **modo de direção** do backtest: **long** (atual, inalterado) ou **short**.
- Para modo **short**:
  - Usar a **mesma** lógica de entrada/saída do template (ex.: `multi_ma_crossover`): quando a estratégia gera sinal de "entrada" (1), interpretar como **abertura de short**; quando gera sinal de "saída" (-1), interpretar como **fechamento de short**.
  - Ajustar cálculo de PnL, stop loss e take profit para posição short (preço de entrada vs preço de saída, stop acima do preço de entrada, etc.).
- O **long atual não deve sofrer alterações**: default permanece long; código e fluxos existentes para long seguem iguais.
- Escopo inicial: utilizar e validar com **template `multi_ma_crossover`**; a solução deve ser extensível para outros templates depois.
- Opção de direção (long/short) deve ser configurável na tela de configuração do backtest (Configure Backtest) e enviada nas requisições de backtest/otimização.

## Capabilities

### New Capabilities

- **backtest-direction**: Capacidade de escolher a direção do backtest (long ou short), executar simulação em short com a mesma lógica de sinais do template (invertendo apenas a interpretação: entrada = abrir short, saída = fechar short) e calcular métricas/PnL/stop/take-profit corretos para short.

### Modified Capabilities

- **backtest-config**: Incluir na configuração do backtest um parâmetro de direção (long | short), exposto na UI (ex.: dropdown ou toggle na tela Configure Backtest) e repassado ao backend nas chamadas de backtest e otimização.

## Impact

- **Backend**
  - Serviços de backtest (`BacktestService`, `ComboOptimizer`, `extract_trades_from_signals`, `simulate_execution_with_15m` em `deep_backtest`): interpretar parâmetro de direção e, quando short, tratar sinal 1 como abertura de short e -1 como fechamento; aplicar stop/take-profit e PnL para short.
  - Engine de backtest (`src/engine/backtester.py`): hoje só modela posição long; pode ser estendido para suportar posição short (ou camada de tradução de sinais + PnL short nos serviços).
- **Frontend**
  - Tela Configure Backtest (ex.: `ComboOptimizePage.tsx` ou equivalente): novo controle para seleção de direção (long/short), valor enviado no payload de backtest/otimização.
- **API**
  - Payloads de backtest/otimização e batch: novo campo opcional (ex.: `direction`: `"long"` | `"short"`), default `"long"`.
- **Templates**
  - Nenhuma alteração no conteúdo do template `multi_ma_crossover` (entry/exit logic permanecem iguais); apenas a interpretação dos sinais no modo short é invertida na execução.
