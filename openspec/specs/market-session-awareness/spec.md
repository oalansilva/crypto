# market-session-awareness Specification

## Purpose
TBD - created by archiving change card-1122-favoritos-alertas-acoes-etfs. Update Purpose after archive.
## Requirements
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
Atraso real é faltar o candle de um pregão ou bloco que o calendário diz que já fechou, passada uma tolerância por tempo gráfico; ele é detectado na varredura seguinte, mesmo com o mercado fechado. O atraso de um ativo SHALL ser decidido **por passada**: numa passada, o ativo está atrasado (`stale`) só quando alguma série dele **lida nessa passada** (fonte, símbolo, tempo) tem o último candle recebido anterior ao último candle que o calendário diz que já fechou. O detalhe guardado de uma série que não foi lida na passada MUST NOT decidir a passada atual; o episódio guardado só fecha quando nenhum detalhe segue atrasado, sem reabrir nem repetir o aviso. Fim de semana, feriado, horário fora do pregão e o candle em formação MUST NOT contar como atraso. Tempo esgotado da coleta local (série que não terminou ou não foi entregue dentro do orçamento da passada) MUST NOT contar como atraso: a série fica sem leitura nessa passada, sem sinal, sem episódio e sem aviso. Falha de leitura **da fonte** (a fonte respondeu com erro ou sem nenhum candle) MUST contar como atraso, com o motivo. O estado `stale` MUST registrar o último candle recebido, o candle esperado, o início do episódio e, quando a série atrasada é de outro tempo gráfico, esse tempo gráfico e os horários dela (`stale_timeframe`, `stale_detail`), que MUST NOT virar último e esperado da linha do próprio tempo gráfico.

#### Scenario: Segunda sem dado na terça
- **WHEN** na terça às 08:05 BRT o último candle 1d de NVDA é o de sexta
- **THEN** NVDA MUST estar `stale`, com o último "sex., 23 out." e o esperado "seg., 26 out."

#### Scenario: Segunda de manhã
- **WHEN** na segunda às 08:05 BRT o último candle 1d de NVDA é o de sexta
- **THEN** NVDA MUST NOT estar `stale`

#### Scenario: Cripto atrasada
- **WHEN** às 08:05 BRT o último candle 1d de BTC/USDT é de dois dias antes
- **THEN** BTC/USDT MUST estar `stale`

#### Scenario: Tempo esgotado da coleta
- **WHEN** a série de NVDA 1d não termina dentro do orçamento da passada, sem erro da fonte
- **THEN** NVDA MUST NOT ficar `stale` por isso
- **AND** nenhum episódio MUST abrir e nenhum aviso MUST sair

#### Scenario: Outro tempo gráfico atrasado
- **WHEN** na passada o 15m de NVDA está atrasado e o 1d está em dia
- **THEN** a linha do 1d MUST ficar em espera com `stale_timeframe = 15m` e os horários do 15m em `stale_detail`
- **AND** o último e o esperado da linha do 1d MUST continuar os do 1d

#### Scenario: Passada seguinte com o 15m em dia
- **WHEN** na passada seguinte o 15m chega e o 1d segue em dia
- **THEN** o episódio MUST fechar sem mensagem e o 1d MUST sair da espera

### Requirement: Dado insuficiente é estado próprio
Quando a série de um favorito tem menos candles fechados do que a análise precisa (ativo novo ou histórico curto), o sistema SHALL tratar como dado insuficiente, com a contagem disponível e a necessária, e não como atraso nem como falha. Dado insuficiente MUST NOT gerar alerta de sinal nem aviso de atraso. O Monitor o mostra como estado próprio (`monitor-multiclass`) e Favoritos como "Aguardando dados: N de M candles" (`favorite-backtest-refresh`).

#### Scenario: Ticker recém-listado
- **WHEN** um favorito de um ticker listado há 40 pregões usa uma média de 200
- **THEN** o favorito MUST ficar como dado insuficiente "40 de 200 candles"
- **AND** nenhum aviso MUST sair no Telegram

