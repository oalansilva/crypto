## ADDED Requirements

### Requirement: Uma execução usa a mesma amostra do início ao fim

Backtest, combo, otimização e descoberta SHALL congelar a amostra no início da execução: um manifesto com série, versão, janela e segmentos com SHA-256. Todas as tentativas, otimizações e a avaliação final SHALL ler só dessa amostra. Atualização, correção ou reconstrução do cache MUST NOT mudar uma execução em andamento.

#### Scenario: Cache refeito durante a varredura

- **WHEN** o cache Parquet é apagado no meio de uma varredura da Descoberta
- **THEN** as combinações seguintes leem a mesma amostra e dão os mesmos candles

### Requirement: Resultado registra a proveniência dos dados

Cada resultado SHALL registrar fonte, classe, sessão, ajuste, timeframe (nativo ou derivado), período pedido, período coberto e versão dos dados, além da referência ao manifesto da amostra.

#### Scenario: Resultado de cripto

- **WHEN** uma combinação de BTC/USDT 1d termina
- **THEN** o resultado guarda fonte Binance Spot, classe cripto, sessão 24/7, ajuste "não se aplica", 1d nativo, períodos e versão

### Requirement: Favorito guarda a amostra do último refresh; os demais por 30 dias

Resultado favoritado SHALL guardar a amostra do seu último refresh diário bem-sucedido e SHALL poder ser refeito com exatamente os mesmos candles dessa amostra, reproduzindo o número que aparece em Favoritos. Na promoção, o favorito SHALL começar com a amostra do resultado promovido, que vale até o primeiro refresh. Toda amostra que não é a de um favorito SHALL ficar guardada por 30 dias, contados do mais tarde entre o fim da execução e o momento em que deixou de ser a amostra de um favorito (desfavoritar ou ser trocada por um refresh). Passado o prazo, a amostra MAY ser apagada e o resultado SHALL aparecer como "não reproduzível exatamente". Segmentos iguais SHALL ser guardados uma vez só.

#### Scenario: Desfavoritar

- **WHEN** Alan desfavorita um resultado em 22 de outubro de 2026
- **THEN** a amostra fica guardada até 21 de novembro de 2026

#### Scenario: Prazo vencido

- **WHEN** um resultado não favoritado passa de 30 dias
- **THEN** ele aparece como "não reproduzível exatamente"
- **AND** refazê-lo não promete os mesmos candles

### Requirement: Refresh diário do favorito troca a amostra guardada

O refresh diário de favoritos que já existe SHALL congelar a amostra no início, como toda execução. Quando o refresh termina bem, a mesma gravação que atualiza o número do favorito SHALL trocar a amostra do favorito pela nova e registrar a nova amostra no run do refresh. A amostra substituída SHALL seguir a regra dos 30 dias contados da troca. Refresh que falha MUST NOT trocar a amostra nem o número do favorito. Este card MUST NOT criar loop novo de refresh nem coleta em segundo plano de ação ou ETF.

#### Scenario: Refresh troca a amostra

- **WHEN** o refresh de um favorito de BTC/USDT termina bem em 23 de outubro de 2026
- **THEN** o favorito passa a apontar para a amostra desse refresh
- **AND** refazer igual reproduz o número que Favoritos mostra depois do refresh
- **AND** a amostra anterior fica guardada até 22 de novembro de 2026

#### Scenario: Refresh falha

- **WHEN** o refresh de um favorito falha por falta de candles recentes
- **THEN** o favorito continua com a amostra e o número anteriores

### Requirement: Resultados antigos sem amostra

Resultados e favoritos criados antes desta mudança SHALL continuar abrindo com os números que já têm e SHALL ser tratados como sem amostra guardada. Um favorito antigo SHALL ganhar amostra no primeiro refresh bem-sucedido depois desta mudança.

#### Scenario: Favorito antigo

- **WHEN** um favorito criado antes desta mudança é aberto antes do primeiro refresh
- **THEN** ele abre normalmente e não promete reprodução exata

#### Scenario: Favorito antigo depois do refresh

- **WHEN** o primeiro refresh depois desta mudança termina bem
- **THEN** o favorito passa a guardar a amostra desse refresh
