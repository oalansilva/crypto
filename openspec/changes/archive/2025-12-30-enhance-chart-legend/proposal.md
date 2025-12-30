# Proposta: Configurar Parâmetros de Estratégia e Melhorar Legenda do Gráfico

## Objetivo
1. Permitir que o usuário configure os parâmetros da estratégia SMA Cross (valores de fast e slow) no formulário Custom Backtest.
2. Exibir esses parâmetros no gráfico com cores personalizadas e legenda estilo TradingView.

## Por Quê
Atualmente, os parâmetros das estratégias são fixos (fast=20, slow=50). O usuário deve poder experimentar diferentes configurações (ex: fast=10, slow=30) para otimizar sua estratégia. Além disso, a visualização deve mostrar claramente quais valores foram utilizados.

## O Que Muda

### Frontend - Formulário
#### [MODIFICAR] [CustomBacktestForm.tsx](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/frontend/src/components/CustomBacktestForm.tsx)
- Adicionar campos de entrada para parâmetros de estratégia quando SMA Cross estiver selecionada:
  - Input numérico para "Fast SMA" (padrão: 20)
  - Input numérico para "Slow SMA" (padrão: 50)
- Enviar esses parâmetros customizados para o backend no objeto `params` da requisição.

### Backend
#### [MODIFICAR] [backtest_service.py](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/backend/app/services/backtest_service.py)
- Atualizar para incluir metadados dos indicadores na resposta:
  - Nome do indicador com parâmetros (ex: "sma_fast" → "SMA(20)")
  - Cor sugerida para cada indicador
- Garantir que os parâmetros customizados sejam passados para a estratégia.

### Frontend - Gráfico
#### [MODIFICAR] [CandlestickChart.tsx](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/frontend/src/components/CandlestickChart.tsx)
- Mapear cores específicas:
  - `sma_fast` → Vermelho (`#ef4444`)
  - `sma_slow` → Azul (`#3b82f6`)
- Adicionar legenda acima do gráfico mostrando:
  - "SMA(20)" em vermelho
  - "SMA(50)" em azul
  - (valores dinâmicos baseados nos parâmetros usados)

## Verificação
- **Configuração**: No formulário Custom Backtest, alterar Fast SMA para 10 e Slow SMA para 30.
- **Execução**: Rodar o backtest e verificar que os valores corretos foram usados.
- **Visualização**: No gráfico de resultados, confirmar:
  - Linha vermelha para SMA(10)
  - Linha azul para SMA(30)
  - Legenda mostrando "SMA(10)" e "SMA(30)" com cores correspondentes
