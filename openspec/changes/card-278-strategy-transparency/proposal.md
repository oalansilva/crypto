## Why

Nomes públicos genéricos ou divergentes e gráficos que ocultam os indicadores realmente usados impedem o trader de compreender como cada estratégia produz sinais. O card #278 substitui a decisão de ocultação do #210 e estabelece transparência funcional consistente, sem expor código, credenciais ou diagnósticos internos.

## What Changes

- Criar um manifesto público único por estratégia com nome e descrição em PT-BR, indicadores efetivamente executados, parâmetros relevantes, função, painel/escala, participação em entrada/saída/risco e lógicas não plotáveis.
- Eliminar fallback genérico para toda estratégia ativa/visível e corrigir identidades enganosas, incluindo `ema_rsi_fibonacci`, que deve comunicar apenas EMA + RSI enquanto Fibonacci não fizer parte da execução.
- Expor nas APIs de Favoritos e Monitor somente o manifesto e as séries timestampadas dos indicadores usados pela estratégia, sem aliases duplicados, colunas diagnósticas, código ou segredos.
- Renderizar os indicadores no gráfico compartilhado de Favoritos e Monitor: médias e Bandas sobre preço, média de volume junto ao volume e osciladores em painéis/escala adequados.
- Exibir legenda acessível com nome, configuração, cor, valor no candle sob o cursor e referências relevantes; unir candles e séries por timestamp.
- Recalcular ou ocultar explicitamente os indicadores ao trocar timeframe, sem manter dados de outro período.
- Preservar candles, operações, marcadores, zoom, `Analisar`, `Abrir Gráfico`, `Ver Trades`, linhas de entrada/stop e demais fluxos atuais.
- Adicionar matriz auditável e testes tabulares, de API, componente e E2E contra drift entre execução, metadados e visualização.

## Capabilities

### New Capabilities

- `strategy-transparency`: Define o manifesto público canônico da estratégia, sua derivação da execução e o contrato seguro de séries/explicações funcionais.

### Modified Capabilities

- `strategy-template-descriptions`: Exige identidade única, fiel e específica para todas as estratégias ativas, sem fallback ou indicador inexistente.
- `strategy-secret-visibility`: Permite transparência funcional para trader comum enquanto mantém código, credenciais e dados internos protegidos.
- `chart-visualization`: Restaura indicadores reais no gráfico compartilhado com painéis, legenda, crosshair, referências e sincronização por timestamp/timeframe.
- `favorites`: Entrega e exibe a mesma identidade, manifesto e séries usadas pelo gráfico de análise de Favoritos.
- `monitor`: Entrega e exibe a mesma identidade, manifesto e séries no Monitor, preservando contexto operacional e ações existentes.

## Impact

- Catálogo/manifesto de estratégias e serialização das APIs de Favoritos e Monitor.
- Resultados de backtest/refresh e transformação segura de `indicator_data` em séries timestampadas.
- Tipos e componentes React compartilhados de gráfico, legenda, painéis e explicação da estratégia.
- Testes backend tabulares/integração, testes frontend e E2E desktop/mobile.
- Sem alteração de regras, sinais, stops, ranking ou performance das estratégias; sem migração de banco obrigatória.

## Correção pós-validação DEV

O teste de Alan em `/combo/results` mostrou somente candles e marcadores para um favorito legado. A investigação confirmou dois gaps:

- o frontend novo foi servido junto de um backend DEV ainda carregado com código anterior ao card;
- favoritos legados com candles e arrays de indicadores alinhados, mas sem `analysis_strategy_transparency`, usam um atalho de cache que não consulta a resposta de análise capaz de reconstruir as séries.

A correção passa a hidratar o manifesto legado pela API de análise quando o cache não contém séries timestampadas utilizáveis e torna o `./restart` do source DEV canônico restrito aos serviços `criptofarol-dev-*`, sem atingir PROD.
