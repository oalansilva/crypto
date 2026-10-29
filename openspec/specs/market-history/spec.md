# market-history Specification

## Purpose
TBD - created by archiving change card-1118-historico-binance. Update Purpose after archive.
## Requirements
### Requirement: Série identificada por ativo, fonte, sessão, ajuste e timeframe

Todo histórico de candles SHALL pertencer a uma série identificada por ativo (identidade estável do catálogo #1117), fonte, sessão, ajuste e timeframe. Duas séries que diferem em qualquer um desses campos MUST NOT ser lidas, gravadas, deduplicadas nem cacheadas como se fossem a mesma. Cripto usa sessão 24/7 e ajuste "não se aplica"; ação e ETF usam sessão "pregão regular" e ajuste explícito.

#### Scenario: Ajustado e bruto não se misturam

- **WHEN** existem candles de NVDA 1d ajustados e alguém consulta NVDA 1d sem ajuste
- **THEN** a consulta não devolve nenhum candle da série ajustada
- **AND** a cobertura informada é a da série sem ajuste

#### Scenario: Mesmo símbolo, fontes diferentes

- **WHEN** há candles antigos de BTC/USDT gravados por um provedor legado
- **THEN** eles não entram na série Binance de BTC/USDT

### Requirement: Uma autoridade de candles para gráfico e análises

O histórico guardado no PostgreSQL SHALL ser a única autoridade dos candles. Gráfico, backtest, combo, otimização e descoberta SHALL ler pelo mesmo serviço de histórico. Para a mesma série, versão e período, todos MUST receber os mesmos candles. Nenhum consumidor MAY baixar da exchange e gravar uma cópia própria fora dessa autoridade.

#### Scenario: Gráfico e backtest de cripto

- **WHEN** o gráfico e um backtest pedem BTC/USDT 1h no mesmo período e na mesma versão
- **THEN** os dois recebem candles idênticos (mesmos horários e valores OHLCV)

#### Scenario: Ação no mesmo serviço

- **WHEN** uma consulta pede NVDA 1d ajustado no pregão regular
- **THEN** ela é atendida pelo mesmo serviço e pela mesma autoridade que atendem cripto

### Requirement: Consulta informa o período pedido, o coberto, lacunas e atualização

Toda consulta de histórico SHALL devolver, junto com os candles: período pedido, período efetivamente coberto, lista de lacunas, momento da última atualização, versão dos dados, se o timeframe é nativo ou derivado e se o histórico é insuficiente para o pedido. Falha de coleta MUST aparecer como falha ou cobertura incompleta, nunca como lista vazia sem explicação nem como período completo.

#### Scenario: Binance começa depois do pedido

- **WHEN** a consulta pede um ETF desde 2019 e a Binance só tem candles desde 2024
- **THEN** a resposta diz o período pedido, o coberto a partir de 2024 e marca o histórico como insuficiente

#### Scenario: Limite de requisições no meio da coleta

- **WHEN** a Binance responde 429 depois de duas páginas
- **THEN** a resposta traz as duas páginas, a cobertura incompleta e o motivo da falha
- **AND** não diz que o período está completo

### Requirement: Coleta sob demanda e só do trecho que falta

A coleta de uma ação ou ETF SHALL começar só quando o ativo é pedido numa consulta ou numa análise que aceite a classe. Até o #1119, as análises recusam ação e ETF, e só a consulta direta coleta essas classes (decisão de Alan, 23/10/2026): análise recusada por classe MUST NOT disparar coleta. O que já foi coletado SHALL ser reaproveitado e só o trecho que falta SHALL ser buscado. Abrir, filtrar, pesquisar ou selecionar o catálogo (inclusive "Todos do filtro") MUST NOT disparar coleta. Não há coleta em segundo plano de favoritos de ação ou ETF nem lote diário do catálogo de ações e ETFs.

#### Scenario: Repetir no mesmo período

- **WHEN** a mesma consulta de NVDA 1d é repetida sem candle novo na Binance
- **THEN** nenhuma página de histórico é pedida à Binance além da verificação do trecho mais recente

#### Scenario: Selecionar todos os ETFs

- **WHEN** Alan seleciona "Todos do filtro" na classe ETFs
- **THEN** nenhuma coleta de histórico começa

#### Scenario: Análise recusada não coleta

- **WHEN** Alan seleciona os ETFs do filtro e tenta iniciar uma descoberta antes do #1119
- **THEN** a análise é recusada com `asset_class_not_supported`
- **AND** nenhuma coleta de histórico começa

#### Scenario: Consulta coleta

- **WHEN** uma consulta autenticada pede SPY 1d e a série nunca foi coletada
- **THEN** a coleta de SPY 1d começa e a resposta traz a cobertura atual

### Requirement: Coleta que retoma sem duplicar nem pular

A coleta paginada SHALL gravar cada página de forma idempotente e registrar onde parou. Depois de reinício ou falha passageira, a coleta SHALL continuar desse ponto. Duas coletas da mesma série MUST NOT rodar ao mesmo tempo, e o resultado final MUST NOT ter candles duplicados nem buracos criados pela retomada.

#### Scenario: Reinício no meio

- **WHEN** o serviço reinicia depois da página 2 de 3 do NVDA 1d
- **THEN** a próxima coleta começa na página 3 e o histórico final tem 3.000 candles sem repetição

#### Scenario: Dois workers pedem a mesma série

- **WHEN** dois workers pedem SPY 5m ao mesmo tempo
- **THEN** só um coleta e o outro espera ou lê o que já foi gravado

### Requirement: Calendário da bolsa de Nova York

Ação e ETF SHALL seguir o calendário da NYSE: pregões, feriados, meio-pregões, fuso de Nova York e horário de verão. Mercado fechado MUST NOT virar lacuna nem candle inventado. Lacuna SHALL ser só a falta de candle esperado dentro de um pregão. Cripto continua 24/7.

#### Scenario: Fim de semana e feriado

- **WHEN** a cobertura de SPY 1d atravessa um sábado e o feriado de Ação de Graças
- **THEN** esses dias não aparecem como lacuna

#### Scenario: Virada do horário de verão

- **WHEN** NVDA 5m atravessa a mudança de horário de março e a de novembro
- **THEN** cada pregão tem 78 candles de 5 minutos, sem buraco e sem candle a mais

### Requirement: Só pregão regular para ação e ETF

A série de ação e ETF SHALL conter só candles do horário normal de negociação de Nova York (09:30 às 16:00, ou o fechamento antecipado do calendário). Candles de pré e pós-mercado MUST NOT ser gravados na série.

#### Scenario: Página com pós-mercado

- **WHEN** a Binance devolve um candle de NVDA às 16:05 de Nova York
- **THEN** ele não entra na série e não conta como lacuna

### Requirement: 15 minutos de ação e ETF montado do 5 minutos

O 15m de ação e ETF SHALL ser montado a partir dos candles de 5m do mesmo pregão: abertura do primeiro, máxima e mínima do grupo, fechamento do último, soma do volume, em blocos ancorados às 09:30 de Nova York. Um bloco MUST NOT atravessar mercado fechado. Bloco com 5m faltando SHALL ser marcado como incompleto e aparecer como lacuna do 15m herdada do 5m; o resumo de cobertura do ativo MUST NOT contá-la de novo. A série SHALL aparecer marcada como derivada, com a versão do 5m e da regra.

#### Scenario: Bloco completo

- **WHEN** existem os três candles de 5m de 09:30, 09:35 e 09:40
- **THEN** o candle de 15m das 09:30 tem a abertura das 09:30, o fechamento das 09:40 e o volume somado

#### Scenario: Meio-pregão

- **WHEN** o pregão fecha às 13:00
- **THEN** o último bloco de 15m termina às 13:00 e nenhum bloco usa candles do dia seguinte

#### Scenario: Bloco incompleto

- **WHEN** falta o candle de 5m das 10:05 de um pregão
- **THEN** o bloco de 15m das 10:00 sai incompleto, como lacuna herdada do 5m
- **AND** a cobertura do ativo conta uma lacuna só

### Requirement: Correções e eventos corporativos viram nova versão

Cada atualização SHALL rebuscar uma janela já guardada e compará-la ao que existe. Se a Binance mudou candles antigos (split, dividendo ou correção), a série SHALL ser recoletada e ganhar nova versão. As próximas consultas SHALL usar a nova versão; execuções em andamento MUST manter a amostra que já têm.

#### Scenario: Split do NVDA

- **WHEN** a série ajustada do NVDA atravessa o split de 10 por 1 de junho de 2024
- **THEN** não há salto falso de preço entre 7 e 10 de junho de 2024

#### Scenario: Correção durante uma execução

- **WHEN** a Binance corrige um candle de SPY enquanto uma execução com SPY roda
- **THEN** a execução termina com a amostra que congelou no início
- **AND** a consulta seguinte usa a versão corrigida

### Requirement: Apagar o cache de leitura não perde histórico

O cache de leitura (Parquet) SHALL ser derivado da autoridade e identificado pela série e pela versão. Apagá-lo e refazê-lo MUST devolver os mesmos candles e MUST NOT apagar nada do histórico guardado.

#### Scenario: Cache refeito

- **WHEN** o diretório do cache é apagado e BTC/USDT 15m é pedido de novo
- **THEN** o cache é refeito a partir do PostgreSQL sem chamar a Binance
- **AND** os candles são idênticos aos de antes

### Requirement: Migração preserva a cripto já guardada

A troca para a autoridade única SHALL consolidar no PostgreSQL o histórico de cripto já guardado em `market_ohlcv` e no cache Parquet, sem perder candles nem sobrescrever divergências sem registro. Favoritos e resultados existentes MUST continuar abrindo com os números que já têm.

#### Scenario: Parquet mais antigo que a tabela

- **WHEN** o Parquet de BTC/USDT 15m começa em 2017 e a tabela só tem os últimos 2 anos
- **THEN** os candles de 2017 em diante passam a existir na autoridade antes de o cache ser refeito

#### Scenario: Divergência entre as duas cópias

- **WHEN** o mesmo candle tem valores diferentes no Parquet e na tabela
- **THEN** a migração registra a divergência, mantém o valor da tabela e não vira a chave enquanto houver divergência acima do limite

### Requirement: Equity 1h and 4h are built from 5m inside the session

The history service SHALL serve 1h and 4h of ação and ETF built on read from the 5m of the same series, by the same rule as the 15m of #1118: blocks anchored at 09:30 New York time (1h: 12 blocks of 5m; 4h: 48 blocks), cut at the session close (16:00, or 13:00 on a half session), never crossing closed market. A block missing an expected 5m SHALL NOT become a candle and SHALL be reported as a gap inherited from the 5m. The version of 1h and 4h SHALL be (version of the 5m, version of the rule). They SHALL NOT be stored as native series. Coverage SHALL list them as "montado do 5m".

#### Scenario: Full session on 4h

- **WHEN** NVDA 4h is read for a full session
- **THEN** there are two candles: 09:30–13:30 and 13:30–16:00 New York time

#### Scenario: Missing 5m inside an hour

- **WHEN** the 5m of 10:05 is missing on a session
- **THEN** the 1h block 09:30–10:30 is not returned as a candle and appears as a gap inherited from the 5m

#### Scenario: Coverage lists derived 1h and 4h

- **WHEN** the coverage of NVDA is read after a backtest on 1h
- **THEN** 1h and 4h appear with origin "montado do 5m" and the same covered period as the 5m

