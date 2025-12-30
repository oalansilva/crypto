# Proposta OpenSpec: Otimização de Estratégias (Grid Search)

**Recurso**: Otimização de Parâmetros de Estratégia
**Status**: PROPOSTO
**Autor**: Antigravity

## Objetivo
Permitir que os usuários encontrem os parâmetros ideais para suas estratégias testando faixas de valores automaticamente. Isso permite responder a perguntas como "Um stop loss de 2% é melhor que 5%?" ou "A SMA 20 funciona melhor que a SMA 50?".

## Motivação
Atualmente, os usuários precisam rodar manualmente vários backtests um por um para comparar diferentes configurações. Isso é tedioso e propenso a erros. Um "Grid Search" (Busca em Grade) automatizado simplifica esse processo, permitindo a melhoria sistemática das estratégias.

## Experiência Proposta (Fluxo do Usuário)

### 1. Wizard - Modo Otimização
- O usuário seleciona "Modo Otimização" em vez de "Execução Única" ou "Comparar".
- **Faixas de Parâmetros**:
    - Em vez de uma única entrada para `Stop Loss`, `Take Profit` ou `Comprimento do Indicador`, o usuário vê uma **Entrada de Faixa**.
    - Campos: **Mín**, **Máx**, **Passo**.
    - Exemplo: Stop Loss -> Mín: 1%, Máx: 5%, Passo: 0.5% (Gera 1.0, 1.5, 2.0, ... 5.0).
- **Segurança**: A interface mostra o número estimado de combinações (ex: "Isso executará 50 backtests"). Aviso se > 100.

### 2. Execução
- O sistema executa todas as combinações em paralelo (ou lote sequencial).
- Barra de progresso em tempo real mostra "Testando combinação 5/50...".

### 3. Resultados - Relatório de Otimização
- **Mapa de Calor / Gráfico de Dispersão**: Visualizando "Parâmetro X vs Lucro Líquido".
- **Tabela de Melhores Desempenhos**: Lista dos top 10 conjuntos de parâmetros classificados por Lucro Líquido ou Sharpe Ratio.
- **Comparação**: Diferença rápida do que mudou (ex: "Melhor execução teve Stop Loss 3% vs Pior teve 1%").

## Deltas de Especificação

### Backend
- Novo modo `optimize` em `BacktestRunCreate`.
- `params` payload corresponde ao `singlestep`, mas os valores podem ser faixas `{min, max, step}`.
- Lógica para gerar o produto cartesiano de todas as faixas.
- Capacidade de pular o salvamento do histórico completo de trades para *cada* execução para economizar espaço? (Talvez salvar apenas os top 5 completos, manter métricas para todos).

### Frontend
- **Novo Componente**: `RangeInput` (Mín, Máx, Passo).
- **Atualização do Wizard**: Alternância para Modo Otimização.
- **Página de Resultados**: Nova visualização para modo `optimize` (Mapa de Calor/Dispersão).

## Riscos e Mitigação
- **Explosão Combinatória**: 3 parâmetros com 10 passos cada = 1000 execuções.
    - *Mitigação*: Limite rígido no máximo de combinações (ex: 100 ou 200) por enquanto.
- **Performance**: Loop em Python pode ser lento para milhares de execuções.
    - *Mitigação*: Backtesting vetorizado é o ideal, mas por enquanto manteremos o motor de loop. Usar limites.
