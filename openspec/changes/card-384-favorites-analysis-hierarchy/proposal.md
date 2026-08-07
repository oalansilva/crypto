## Why

A análise gráfica aberta por Favoritos repete indicadores e parâmetros em até três blocos, mistura resumo, regras e detalhes técnicos no mesmo nível visual e dificulta identificar rapidamente tese, risco, desempenho e evidências da estratégia. A tela precisa de uma hierarquia única e progressiva que preserve a transparência conquistada no card #361 sem transformar transparência em redundância.

## What Changes

- Reorganizar a análise completa em uma sequência de leitura: identidade e resumo, regras da estratégia, gráfico, detalhes técnicos e operações.
- Definir um único bloco visual como fonte de apresentação dos indicadores e parâmetros efetivos, removendo repetições entre resumo, painel de transparência e superfície do gráfico.
- Manter no gráfico apenas o contexto necessário para interpretar candles, indicadores, valores no ponto de referência, sinais e controles de navegação.
- Apresentar conteúdo técnico detalhado por divulgação progressiva, com estados indisponíveis e divergências exibidos uma única vez no contexto apropriado.
- Padronizar os rótulos visíveis da análise em português e garantir leitura responsiva sem corte ou rolagem horizontal.
- Aplicar a mesma linguagem clara nos componentes compartilhados por Favoritos e Monitor, sem preservar defaults legados que reintroduzam a cópia removida.
- Remover a ação e o conteúdo expansível de decisão por operação; a lista preserva somente os fatos operacionais já visíveis, evitando uma segunda camada explicativa abaixo das regras da estratégia.
- Preservar os contratos, métricas, regras, séries, operações, permissões e fontes de dados existentes; a mudança é de arquitetura de informação e apresentação.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `favorites`: a análise completa aberta por Favoritos passa a ter hierarquia responsiva explícita, sem duplicação de informações técnicas e com divulgação progressiva.
- `strategy-transparency`: a transparência funcional continua completa, mas cada informação canônica deve aparecer uma única vez por contexto de análise, com resumo e detalhe coordenados em vez de blocos concorrentes.

## Impact

- Frontend React: `ComboResultsPage`, `StrategyTransparencyPanel`, `StrategyChartSurface`, Monitor e componentes compartilhados de resumo/operações.
- Testes unitários e Playwright da jornada Favoritos → análise completa, incluindo desktop e mobile.
- Sem alteração planejada de API, banco de dados, cálculo de indicadores, backtest ou permissões.
- `UI impact: affected`; exige protótipo navegável e aprovação humana de Design antes de qualquer alteração no código de produção.
