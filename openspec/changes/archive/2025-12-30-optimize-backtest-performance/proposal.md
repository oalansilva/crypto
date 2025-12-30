# Proposta OpenSpec: Otimização de Performance do Backtest

**Status**: PROPOSTO
**Autor**: Antigravity
**Criado**: 29/12/2025

## 1. Descrição do Problema
O motor de backtest atual executa tarefas de otimização (Grid Search) sequencialmente em um único processo. Isso leva a tempos de execução lentos, especialmente ao testar milhares de combinações de parâmetros ou múltiplos timeframes. Além disso, cálculos de indicadores redundantes são realizados mesmo quando apenas parâmetros de execução (stop loss/take profit) são alterados.

## 2. Objetivo
Maximizar a velocidade de execução do motor de backtest para permitir iteração rápida de estratégias.
**Meta**: Atingir um aumento de velocidade de 5x-10x para tarefas típicas de otimização.

## 3. Escopo
*   **Backend**: `BacktestService` e `JobManager`.
*   **Lógica Principal**: Implementação de processamento paralelo e cache de sinais.
*   **Armazenamento**: Otimização da persistência de resultados.

## 4. Solução Proposta

### 4.1. Execução Paralela (Multi-processamento)
Refatorar o loop principal de otimização para utilizar `ProcessPoolExecutor` (ou `joblib`). Isso permite utilizar todos os núcleos da CPU para executar iterações de backtest independentes em paralelo.

### 4.2. Cache Inteligente de Sinais (Memoização)
Separar parâmetros de estratégia (ex: comprimento do RSI) de parâmetros de execução (ex: % de Stop Loss).
*   Se os parâmetros da estratégia não mudarem em relação à iteração anterior, reutilizar o `df` com sinais gerados em cache.
*   Reexecutar apenas o loop de execução do `Backtester` (rápido) em vez do cálculo completo de indicadores (lento).

### 4.3. Armazenamento Serializado
*   Substituir a lista `opt_results` em memória (que cresce indefinidamente) por uma solução de armazenamento em fluxo (streaming).
*   Gravar resultados em `SQLite` ou arquivos `JSON Lines` (`.jsonl`) do tipo append-only para manter o uso de memória baixo e evitar overhead massivo de dump JSON ao final.

## 5. Critérios de Sucesso
*   Grid search com 1000 combinações completando em < 20% do tempo atual.
*   Uso de memória permanece estável independentemente do tamanho do grid.
*   Funcionalidade de Pausar/Retomar continua funcionando (requer gerenciamento de estado cuidadoso com workers paralelos).
