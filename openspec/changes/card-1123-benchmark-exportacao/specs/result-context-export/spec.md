## ADDED Requirements

### Requirement: One set of context columns for the three spreadsheets

The Favorites spreadsheet, the result trades spreadsheet and the Discovery ranking spreadsheet SHALL be built by the server from one shared context builder and SHALL carry, besides today's metrics, these context fields in this order: Classe, Moeda, Fonte, Sessão, Ajuste, Período pedido, Período efetivo, Modo de execução, Versão da amostra, Referência, Tipo de retorno da referência, Período comum, Fora do período comum, Retorno da estratégia no período comum, CAGR da estratégia no período comum, Retorno da referência, CAGR da referência, Diferença de CAGR (p.p.), Situação da comparação, Aviso de moeda, Versão da amostra da referência, Comparação gravada em. Each workbook SHALL include a "Legenda" sheet explaining "deduzido", "não registrado", "USDT tratado como USD" and "retorno de preço, sem dividendos". "Tipo de retorno da referência" SHALL carry "Retorno de preço, sem dividendos" for an ação or ETF reference and "Retorno de preço" for a crypto reference, in every workbook. Context values SHALL come from the recorded result, favorite or Discovery result and from the recorded comparison; exporting SHALL NOT collect data or recompute a comparison.

#### Scenario: Same headers in every spreadsheet

- **WHEN** Alan exports the Favorites list, the trades of a result and a Discovery ranking
- **THEN** the three workbooks carry the same context headers in the same order and a "Legenda" sheet

#### Scenario: Insufficient reference in the spreadsheet

- **WHEN** the recorded comparison is insufficient
- **THEN** "Situação da comparação" carries "Histórico insuficiente: <motivo>" and the four return/CAGR cells and the difference are empty, never zero

#### Scenario: Currency warning in the spreadsheet

- **WHEN** a BTC/USDT row has SPY as reference
- **THEN** "Aviso de moeda" carries "USDT tratado como USD, sem conversão. A comparação é só em percentual."

### Requirement: Favorites spreadsheet exports the visible list with context

"Exportar" in Favorites SHALL download, from the server, one row per favorite of the current filtered list in the current order, keeping today's columns and adding the context fields. The reference fields SHALL come from the favorite's recorded comparison. The download SHALL keep the admin-only access of today. Its "Legenda" sheet SHALL also say that the Favorites screen shows the class convention (source and session) while the spreadsheet carries only what was recorded, marking the rest "não registrado", and that a favorite's comparison is redone only when its backtest is refreshed, with the same reference.

#### Scenario: Legend explains screen versus spreadsheet

- **WHEN** an old favorite shows "Binance Spot · 24/7" on the Favorites screen and "não registrado" in Fonte and Sessão in the spreadsheet
- **THEN** the "Legenda" sheet explains that the screen shows the class convention and the spreadsheet only what was recorded

#### Scenario: Favorite with SPY reference

- **WHEN** a favorite has SPY recorded as reference and Alan exports
- **THEN** its row shows "SPY" in Referência with the recorded common period, returns, CAGRs and recording time

### Requirement: Old favorites export with "deduzido" and "não registrado"

A favorite without recorded context SHALL still export. Classe and Moeda SHALL be deduced from the symbol and carry "(deduzido)". Fonte, Sessão, Ajuste and Versão da amostra SHALL carry "não registrado" when not recorded. Without a recorded comparison, Referência SHALL carry "Próprio ativo" and Situação da comparação SHALL carry "não registrado", with the numeric reference cells empty.

#### Scenario: Old crypto favorite

- **WHEN** a BTC/USDT favorite saved before #1118 is exported
- **THEN** its row shows "Cripto (deduzido)", "USDT (deduzido)" and "não registrado" in Fonte, Sessão, Ajuste, Versão da amostra and Situação da comparação

### Requirement: Trades spreadsheet carries the result context

"Exportar para Excel" on the result screen SHALL send the result's context and the id of the recorded comparison, and the server SHALL return a workbook with the "Trades" sheet (today's columns plus Moeda), a "Contexto" sheet (one line per context field, with its value and state "registrado", "deduzido" or "não registrado") and the "Legenda" sheet. The request SHALL use the authenticated client.

#### Scenario: BTC/USDT trades with SPY reference

- **WHEN** Alan exports the trades of a BTC/USDT result whose reference is SPY
- **THEN** the "Contexto" sheet shows Referência SPY, the common period, what was left out, both returns and CAGRs, the difference, the currency warning and both sample versions

### Requirement: Discovery ranking spreadsheet

The Discovery spreadsheet SHALL follow the requirement in `discovery-leaderboard` and use the same context fields, with Referência fixed to the own asset. When the Decidir has an extra reference column recorded, the spreadsheet SHALL add, after the 22 context fields, the extra comparison under the same field names followed by " (extra)" (from Referência to Comparação gravada em, 13 columns), with the same "registrado" rules, "Histórico insuficiente: <motivo>" and empty numeric cells for insufficient rows, and the same currency warning text.

#### Scenario: Discovery export uses the shared context

- **WHEN** Alan exports a Discovery ranking
- **THEN** every row carries the 22 shared context fields, with the same names and order as the other two workbooks, and "Próprio ativo (buy-and-hold, long-only)" in Referência
- **AND** an ação or ETF row carries "Retorno de preço, sem dividendos" in "Tipo de retorno da referência"

#### Scenario: Discovery export with an extra reference

- **WHEN** the Decidir has "Contra SPY" recorded and Alan exports the ranking
- **THEN** the headers are today's columns, the 22 context fields and then Referência (extra) through Comparação gravada em (extra)
- **AND** the "Legenda" sheet explains "(extra)"
