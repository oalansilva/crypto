## ADDED Requirements

### Requirement: Candle fechado pelo calendário da classe
O sistema SHALL decidir o último candle fechado de uma série pelo calendário da classe. A cripto é 24/7: o candle fecha em início + duração. Ação e ETF usam os pregões regulares da NYSE (#1118): o candle 1d fecha no fechamento do pregão (inclusive meio pregão), e o bloco de 15m, 1h ou 4h fecha no fim do bloco ancorado às 09:30 de NY ou no fechamento do pregão, o que vier antes. A leitura do Monitor e do Telegram de ação e ETF MUST usar só candles fechados por essa regra. Sem candle em formação na série, o último candle fechado MUST entrar na leitura; ele MUST NOT ser descartado como se estivesse em formação.

#### Scenario: Terça antes da abertura
- **WHEN** a varredura roda terça às 08:05 BRT (antes da abertura de NY) para NVDA 1d
- **THEN** a leitura MUST usar o candle de segunda como o último fechado

#### Scenario: Durante o pregão
- **WHEN** o Monitor lê NVDA 1h às 12:10 de NY
- **THEN** o bloco 11:30–12:30 MUST ficar fora da leitura, e o último fechado MUST ser 10:30–11:30

#### Scenario: Meio pregão
- **WHEN** o pregão fecha às 13:00 de NY (dia seguinte à Ação de Graças)
- **THEN** o candle 1d daquele dia MUST contar como fechado a partir das 13:00

### Requirement: Estado do mercado por ativo
Para cada ativo monitorado, o sistema SHALL calcular o estado do mercado no instante da leitura:
- `open`: pregão aberto, com o horário de fechamento;
- `closed`: fora do pregão, fim de semana ou feriado, com o motivo (fora do pregão, fim de semana, feriado em NY) e a próxima abertura;
- `stale`: atraso real.

A cripto é sempre `open`, exceto quando `stale`. Os horários MUST ser mostrados em BRT, com o horário de NY entre parênteses para ação e ETF.

#### Scenario: Sábado
- **WHEN** o Monitor lê NVDA no sábado, 24 out. 2026, às 11:05 BRT
- **THEN** o estado MUST ser `closed`, com motivo fim de semana e próxima abertura "seg., 26 out., 10:30 (09:30 em NY)"

#### Scenario: Feriado
- **WHEN** o Monitor lê SPY na quinta, 26 nov. 2026 (Ação de Graças)
- **THEN** o estado MUST ser `closed`, com motivo "feriado em Nova York" e próxima abertura "sex., 27 nov., 11:30 (09:30 em NY)"

#### Scenario: Pregão aberto
- **WHEN** o Monitor lê NVDA na segunda, 26 out. 2026, às 15:00 BRT
- **THEN** o estado MUST ser `open`, com fechamento "17:00 (16:00 em NY)"

### Requirement: Atraso real sem falso positivo
Atraso real é faltar o candle de um pregão ou bloco que o calendário diz que já fechou; ele é detectado na varredura seguinte, mesmo com o mercado fechado. Um ativo SHALL estar com atraso real (`stale`) quando, para alguma das séries monitoradas dele (fonte, símbolo, tempo), o último candle recebido é anterior ao último candle que o calendário da classe diz que já fechou, passada uma tolerância por tempo gráfico. Fim de semana, feriado, horário fora do pregão e o candle em formação MUST NOT contar como atraso. Falha de leitura da fonte sem nenhum candle MUST contar como atraso, com o motivo. O estado `stale` MUST registrar o último candle recebido, o candle esperado e o início do episódio.

#### Scenario: Segunda sem dado na terça
- **WHEN** na terça às 08:05 BRT o último candle 1d de NVDA é o de sexta
- **THEN** NVDA MUST estar `stale`, com o último "sex., 23 out." e o esperado "seg., 26 out."

#### Scenario: Segunda de manhã
- **WHEN** na segunda às 08:05 BRT o último candle 1d de NVDA é o de sexta
- **THEN** NVDA MUST NOT estar `stale`

#### Scenario: Cripto atrasada
- **WHEN** às 08:05 BRT o último candle 1d de BTC/USDT é de dois dias antes
- **THEN** BTC/USDT MUST estar `stale`

### Requirement: Dado insuficiente é estado próprio
Quando a série de um favorito tem menos candles fechados do que a análise precisa (ativo novo ou histórico curto), o sistema SHALL tratar como dado insuficiente, com a contagem disponível e a necessária, e não como atraso nem como falha. Dado insuficiente MUST NOT gerar alerta de sinal nem aviso de atraso. O Monitor o mostra como estado próprio (`monitor-multiclass`) e Favoritos como "Aguardando dados: N de M candles" (`favorite-backtest-refresh`).

#### Scenario: Ticker recém-listado
- **WHEN** um favorito de um ticker listado há 40 pregões usa uma média de 200
- **THEN** o favorito MUST ficar como dado insuficiente "40 de 200 candles"
- **AND** nenhum aviso MUST sair no Telegram
