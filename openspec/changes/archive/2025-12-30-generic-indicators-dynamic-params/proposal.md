# Proposta: Sistema Genérico de Indicadores e Estratégias Dinâmicas

## Objetivo
Implementar um sistema flexível de backtesting que exponha automaticamente toda a biblioteca de indicadores `pandas-ta`, permita a configuração dinâmica de parâmetros via interface (sem UI hardcoded) e suporte a comparação paralela de N estratégias.

## Por Quê
Atualmente, cada nova estratégia ou indicador exige alterações manuais no backend (Python) e no frontend (React). Isso limita a experimentação.
O usuário deseja um "Laboratório de Estratégias" onde possa combinar qualquer indicador do `pandas-ta` (ex: MACD, ADX, Supertrend) com lógica de entrada/saída, ajustando parâmetros dinamicamente, e comparar múltiplas variações simultaneamente.

## O Que Muda

### Backend
1.  **API de Metadados (`/api/strategies/metadata`)**:
    -   Novo endpoint que introspecta a biblioteca `pandas-ta`.
    -   Retorna lista de indicadores disponíveis, categorias e seus argumentos esperados (nome, tipo, default).
2.  **Motor de Execução Genérico**:
    -   Refatorar `run_backtest` para aceitar um payload de "Estratégia Composta".
    -   Exemplo de Payload:
        ```json
        {
          "strategies": [
            {
              "name": "My MACD Strat",
              "indicators": [
                { "kind": "macd", "params": { "fast": 12, "slow": 26 } }
              ],
              "entry": "macd > macdsignal",
              "exit": "macd < macdsignal"
            }
          ]
        }
        ```
    -   Uso de `pandas_ta.Strategy` ou execução sequencial dinâmica.

### Frontend
1.  **Dynamic Strategy Builder**:
    -   Nova interface que consulta a API de metadados.
    -   Dropdown pesquisável de todos os indicadores.
    -   Geração automática de formulários (inputs numéricos, selects) baseada nos metadados do indicador escolhido.
2.  **Multi-Strategy Runner**:
    -   Permitir adicionar múltiplas configurações à fila de execução.
    -   Visualização comparativa de resultados (Tabela de Métricas + Gráficos sobrepostos de Equidade).

## Verificação
- O usuário deve conseguir selecionar "ADX" (que não existe hoje) na UI, configurar seus parâmetros e rodar um backtest sem que eu precise escrever código novo para o ADX.
- Comparar 3 estratégias de RSI com períodos diferentes (14, 21, 7) na mesma execução.
