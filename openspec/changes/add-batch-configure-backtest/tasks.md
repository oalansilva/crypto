## 1. Backend – Batch backtest orchestration
- [x] 1.1 Definir endpoint para disparar batch a partir da configuração atual (ex.: `POST /api/combos/backtest/batch`).
- [x] 1.2 Implementar serviço que, dado um payload de configuração (template, ranges, flags, timeframe **e lista de símbolos alvo**), itera sobre essa lista e agenda/roda os backtests um a um (ou via fila),
      reutilizando **exatamente a mesma lógica já existente** de backtest/otimização (mesmos serviços como `AutoBacktestService` / `ComboOptimizer`, mesmos critérios de seleção de best result),
      apenas orquestrando múltiplas execuções em sequência ou em paralelo controlado.
- [x] 1.3 Para cada ativo, ao finalizar, **criar sempre um novo registro** em `favorite_strategies` (sem sobrescrever existentes) contendo:
  - parâmetros efetivos usados
  - métricas principais (Sharpe, retorno, DD, trades, etc.)
  - `notes` contendo um texto específico, por exemplo `\"gerado em lote\"` (podendo incluir timestamp ou id de batch)
  - `tier = 3` para todas as estratégias geradas pelo batch.
- [x] 1.4 Registrar erros por ativo (ex.: falha em baixar dados, erro no backtest) sem interromper o batch completo.

## 2. Frontend – Configure Backtest UI
- [x] 2.1 Adicionar controles de ação na tela `Configure Backtest` para disparar batch com escopo configurável:
  - opção para rodar **apenas o símbolo atual**
  - opção para rodar **vários símbolos selecionados** (ex.: multi‑select ou checklist)
  - opção para rodar **todos** os símbolos disponíveis/filtrados.
- [x] 2.2 Garantir que o payload enviado para o endpoint de batch use a **mesma configuração** visível na tela (template, ranges, flags de deep backtest, timeframe, data range se houver) + a lista de símbolos escolhida.
- [x] 2.3 Exibir feedback de progresso **em tempo quase real**:
  - contador de ativos processados / totais (ex.: `3 de 200` ativos)
  - tempo já decorrido desde o início do batch (ex.: `tempo decorrido: 2m30s`)
  - **estimativa de término** baseada no ritmo atual (ex.: `estimado: 18m restantes` ou horário previsto de conclusão)
  - indicativo visual de execução em andamento (spinner / banner fixo na tela Configure).
- [x] 2.4 Exibir resumo ao final:
  - quantos ativos concluídos com sucesso
  - quantos falharam
  - link ou CTA para abrir `Strategy Favorites` / `Opportunity Board` e revisar os favoritos gerados em lote (todos marcados como Tier 3 e com o comentário padrão).

## 3. Regras de favoritos (sem sobrescrita)
- [x] 3.1 Definir que o modo batch **nunca sobrescreve** favoritos existentes; cada execução gera novas entradas em `favorite_strategies`.
- [x] 3.2 (Opcional) Incluir um identificador de batch ou timestamp em `notes` para facilitar o filtro/agrupamento dessas estratégias geradas em lote.

## 4. Observabilidade e UX
- [x] 4.1 Adicionar logs estruturados no backend para cada ativo processado no batch (sucesso/falha + motivo).
- [x] 4.2 Adicionar tratamento de erro amigável no frontend caso o batch falhe imediatamente (erro 500, validação, etc.).
- [x] 4.3 Atualizar documentação de uso (ou help inline na tela Configure Backtest) explicando:
  - o que o botão de batch faz
  - que os favoritos criados terão nota `\"gerado em lote\"`
  - que o batch usa a configuração atual da tela.

