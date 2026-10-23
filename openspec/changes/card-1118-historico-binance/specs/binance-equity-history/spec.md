## ADDED Requirements

### Requirement: Adaptador do histórico de ações e ETFs da Binance

O sistema SHALL coletar o histórico de ação e ETF pela rota pública `/bapi/equity/v1/public/equity/kline/chart`, sem credencial, isolada num adaptador próprio. A paginação SHALL ser retroativa com `limit=1000` e `endTime=min(t)-1`, filtrando a janela localmente. O adaptador MUST NOT presumir semântica Spot para `startTime`.

#### Scenario: Histórico de mais de uma página

- **WHEN** NVDA 1d é coletado desde o início
- **THEN** o adaptador pede páginas de 1.000 candles andando para trás até a Binance não ter mais candles
- **AND** o resultado tem candles ordenados e sem duplicata

### Requirement: Validação da resposta e erro de negócio em HTTP 200

Cada página SHALL ser validada antes de gravar: `code` igual a `000000`, `data.bars` como lista, campos `t`, `ct`, `o`, `h`, `l`, `c`, `v` numéricos, duração do candle compatível com o timeframe e OHLC coerente (`l` ≤ `o`,`c` ≤ `h`, preços positivos, volume não negativo). Resposta com outro `code`, mesmo em HTTP 200 (por exemplo `488006`), SHALL virar erro de negócio com o código. Campo obrigatório ausente ou de tipo trocado SHALL virar "formato mudou". Nada de uma página inválida MUST ser gravado.

#### Scenario: Código 488006 em HTTP 200

- **WHEN** a Binance responde HTTP 200 com `code` 488006
- **THEN** a coleta registra erro de negócio 488006 e a cobertura fica incompleta
- **AND** a página não vira lista vazia

#### Scenario: Formato mudou

- **WHEN** os candles chegam sem o campo `c`
- **THEN** a coleta falha com "formato da Binance mudou" e não grava a página

### Requirement: Limite de requisições e concorrência entre workers

As chamadas à Binance de ações SHALL passar por um limitador único compartilhado entre processos e workers, com no máximo 2 requisições por segundo e 2 séries coletando ao mesmo tempo. Respostas 429 e 418 SHALL respeitar `Retry-After`; três falhas seguidas (429, 418 ou 5xx) SHALL pausar a coleta de ações por 5 minutos e marcar a cobertura como falha temporária.

#### Scenario: 429 com Retry-After

- **WHEN** a Binance responde 429 com `Retry-After: 30`
- **THEN** nenhuma requisição de ações sai nos próximos 30 segundos, de nenhum worker

### Requirement: Fim real do histórico e página vazia

Página vazia com `code` `000000` SHALL ser confirmada uma vez antes de ser tratada como início do histórico na Binance. Confirmada, a cobertura SHALL registrar "a Binance não tem candles antes de" a data do primeiro candle.

#### Scenario: Início do ETF

- **WHEN** a página anterior ao primeiro candle de um ETF vem vazia duas vezes
- **THEN** a cobertura diz que a Binance só tem candles desde aquele dia
