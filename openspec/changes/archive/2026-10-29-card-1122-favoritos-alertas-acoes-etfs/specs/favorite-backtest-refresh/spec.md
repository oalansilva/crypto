## ADDED Requirements

### Requirement: Atualização de ação e ETF pelo calendário
A atualização diária de favorito de ação ou ETF SHALL medir o frescor pelo calendário da classe (`market-session-awareness`), não pelo tempo corrido. O dado está fresco quando o último candle fechado esperado pelo calendário está presente. Fim de semana, feriado e horário fora do pregão MUST NOT gerar "Falha na atualização". Quando nenhum candle fechou desde a última atualização, o ciclo MUST pular a reexecução e manter o status de sucesso. A cripto MUST manter as regras de hoje.

#### Scenario: Refresh de NVDA 1h no domingo
- **WHEN** a atualização roda no domingo para um favorito NVDA 1h, com o último bloco fechado na sexta
- **THEN** o favorito MUST continuar "Backtest atualizado", sem falha

#### Scenario: Atraso real na atualização
- **WHEN** a atualização roda na terça e falta o pregão de segunda de NVDA
- **THEN** o favorito MUST ficar "Falha na atualização", com o motivo do atraso

### Requirement: Intradiário e precisão de ação e ETF na atualização
A atualização de favorito de ação ou ETF da Binance SHALL coletar a série do tempo gráfico e o 5m do intrabar pelo caminho do #1118 (`prepare_equity_history` com intrabar). Ela MUST rodar com precisão diária, marcada em `analysis_execution`, quando não houver 15m que cubra a janela, como no lote. A falta de 15m MUST NOT ser falha.

#### Scenario: NVDA em todo o histórico
- **WHEN** a atualização de NVDA 1d em todo o histórico roda
- **THEN** o favorito MUST ficar atualizado com "Precisão diária · sem 15m de …" no trecho sem 5m

### Requirement: Aguardando dados e período operacional no último pregão
Quando a série tem menos candles fechados do que a análise precisa, a atualização SHALL gravar o status `INSUFFICIENT`, com a contagem disponível e a necessária. Favoritos MUST mostrar "Aguardando dados: N de M candles", em cinza, e não "Falha". No favorito com período operacional "todo o histórico", o fim do período de ação e ETF MUST ser a data do último pregão fechado, não a data de hoje. A busca do primeiro candle MUST usar a fonte do favorito.

#### Scenario: Ticker novo
- **WHEN** um favorito de um ticker com 40 pregões precisa de 200 candles
- **THEN** a atualização MUST gravar `INSUFFICIENT` "40 de 200 candles", sem falha

#### Scenario: Fim do período no sábado
- **WHEN** a atualização de NVDA com período "todo o histórico" roda no sábado, 24 out. 2026
- **THEN** o fim do período MUST ser 23 out. 2026

### Requirement: Status de atualização mostra o último pregão
Para ação e ETF, o status de sucesso em Favoritos SHALL ser "Backtest atualizado: <data e hora> · último pregão <data>".

#### Scenario: Linha de NVDA
- **WHEN** a atualização de NVDA terminou no sábado às 08:12, com o último pregão em 23 out.
- **THEN** a linha MUST mostrar "Backtest atualizado: 24/10, 08:12 · último pregão 23/10"
