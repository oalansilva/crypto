# multiclass-discovery Specification

## Purpose
TBD - created by archiving change card-1121-descoberta-acoes-etfs. Update Purpose after archive.
## Requirements
### Requirement: Discovery accepts crypto, ações and ETFs in one sweep
The Discovery Preflight SHALL accept crypto pairs, ações and ETFs from the Binance catalog in the same sweep and MUST NOT leave an ação or ETF out because of its class. Assets marked by Binance (suspended, off market, no trading, no rules, removed) and symbols outside the catalog SHALL stay out with the reason, as defined by #1117. Every Discovery timeframe (15m, 1h, 4h, 1d) SHALL be offered to the three classes. The reason "ação e ETF por enquanto rodam no Combo e na Otimização (1 ativo ou lote); a Descoberta vem depois" MUST NOT appear in the Discovery.

#### Scenario: Mixed selection is accepted
- **WHEN** the draft selects BTC/USDT, NVDA and SPY with one template, 1d and Long
- **THEN** the Preflight SHALL report 3 valid combinations, state "Pronto para iniciar" and list no asset out of the sweep
- **AND** the Preflight SHALL show the selection by class and currency ("1 cripto (USDT) · 1 ação · 1 ETF (USD)")

#### Scenario: Marked asset stays out
- **WHEN** the selection includes an ação marked by Binance as off market
- **THEN** that ação SHALL stay out of the sweep with the Binance state and reason, and the other assets SHALL run

### Requirement: Each asset is acquired and evaluated with its own class
Each combination SHALL acquire and freeze candles through the source of its asset: crypto through the unified history path, and ação or ETF through the Binance equity history (`binance_equity`). The equity history covers the timeframe series and, with intrabar precision, the 5m that builds the 15m. The optimizer SHALL receive the asset's source, never a fixed `ccxt`. Each result SHALL record its class, source, session, adjustment, currency (USDT for crypto, USD for ação and ETF), requested window and effective window. No combination SHALL read candles from another market or another adjustment.

#### Scenario: NVDA uses the equity history
- **WHEN** a combination for NVDA in 1d runs
- **THEN** its sample SHALL be frozen from the `binance_equity` series of NVDA, adjusted by split, in the New York regular session
- **AND** the result SHALL record class "stock", currency "USD" and the effective window of the candles

#### Scenario: Crypto keeps today's path
- **WHEN** a combination for BTC/USDT runs
- **THEN** it SHALL use the same source, sample and metrics as the crypto Discovery before this change

### Requirement: One frozen sample with a temporal split
Training, every optimization attempt and the final evaluation of a combination SHALL read only from the same frozen sample. The sample SHALL be acquired once per asset, timeframe and window of the sweep and reused by every combination of that asset and timeframe. A retried attempt SHALL reuse the frozen sample and SHALL NOT download history again. Training SHALL use the oldest 70% of the candles and the evaluation the latest 30%, with no overlap. The minimum of 30 trades and GO only with walk-forward SHALL stay as today. Eligibility coverage SHALL count the expected candles with the calendar of the class: 24/7 for crypto, and NYSE sessions for ação and ETF. Closed-market hours MUST NOT count as missing candles.

#### Scenario: Retry reads the same sample
- **WHEN** a combination for SPY fails on a worker after the sample was frozen and is retried
- **THEN** the retry SHALL read the same `snapshot_id` and the result SHALL record it

#### Scenario: Equity coverage is not penalized by closed hours
- **WHEN** NVDA in 1d has every NYSE session of the window
- **THEN** its coverage SHALL be 100% and the result SHALL be eligible when it has at least 30 trades

### Requirement: Daily precision is visible and never silent
When an ação or ETF has no 15m covering the whole window, the combination SHALL run with the timeframe candle and produce a valid result. That result SHALL carry the amber mark "Precisão diária · sem 15m de <início> a <fim>" in Acompanhar ("Por ativo"), the promotion dialog and the favorite. In the compact candidate row of Decidir and the partials the mark SHALL read "Precisão diária (<ano início>–<ano fim>)", with the exact stretch on hover and for assistive technology. The Preflight SHALL say before the start which assets and timeframes are expected to fall back to daily precision, with the stretch. A result with intrabar precision SHALL show "Precisão intrabar (15m)".

#### Scenario: NVDA in all history
- **WHEN** a sweep with NVDA, 1d and "Todo o histórico" completes
- **THEN** the NVDA row SHALL show the amber "Precisão diária (2003–2025)", with "Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025" (stretch from the execution) for assistive technology and in the promotion dialog, and stay in the ranking

#### Scenario: Forecast before the start
- **WHEN** the draft has NVDA and SPY in 1d with "Todo o histórico"
- **THEN** the Preflight SHALL show "Precisão diária prevista" naming NVDA and SPY in 1d and the stretch without 15m

### Requirement: Asset without enough candles has an explicit state
An asset whose window has no candles, or fewer candles than the training minimum, SHALL end its combinations as "Amostra insuficiente" with the reason. The reason SHALL include "sem candles de <tempo> de <ativo> nessa janela" when Binance has no candles there. These combinations SHALL appear in Acompanhar and Decidir with that state. They MUST NOT have a rank, a Promover action or a favorite. A history failure (rate limit, unavailable, business error) SHALL be retried within the attempt budget and, when the budget ends, SHALL end as "Falha" with the reason. A failure MUST NOT become a candidate or a sufficient sample.

#### Scenario: Past window without intraday for equities
- **WHEN** a sweep runs NVDA in 4h from 1 jan. 2019 to 31 dez. 2020
- **THEN** the combination SHALL end as "Amostra insuficiente" with "sem candles de 4h de NVDA nessa janela (o 5m da Binance começa em 2 jan. 2026)"
- **AND** it SHALL have no rank and no Promover

#### Scenario: Collection keeps failing
- **WHEN** the Binance equity history keeps answering with errors for SPY until the 3 attempts end
- **THEN** SPY's combinations SHALL end as "Falha" with the reason and SHALL NOT appear as candidates

### Requirement: Per-asset state while the sweep runs
The Acompanhar mode SHALL show a "Por ativo" list with, for each asset of the sweep: symbol, class and currency, combinations done of total, one state with icon and text, and a detail. The states are: "Na fila", "Coletando histórico · <série> · página N de M", "Pausado na coleta · <série> · página N de M · retoma daqui", "Rodando · <tempo>", "Concluído", "Concluído · precisão diária", "Amostra insuficiente: <motivo>", "Falha: <motivo>" and "Não rodou · varredura cancelada". When the combinations of one asset end with different outcomes, the state SHALL show the count of each outcome (for example "1 concluída · 1 amostra insuficiente") and the detail SHALL give the reason per timeframe; it MUST NOT read "Concluído" alone. The columns Ativo · Combinações · Estado · Detalhe SHALL have a visible header row when the list is wider than 620 px, and each cell SHALL carry its column name for assistive technology; below 620 px each asset becomes a card. The list SHALL put the asset in progress first, then failures and insufficient samples, then the others in sweep order, and SHALL show 50 assets at a time with "Mostrar mais 50". The aggregated counters (processadas = sucesso + falha + ignoradas + amostra insuficiente) SHALL stay. Only the asset and stage in progress SHALL be announced to assistive technology.

#### Scenario: NVDA collecting history
- **WHEN** the sweep is collecting the 1d history of NVDA
- **THEN** the NVDA line SHALL be first and read "Coletando histórico · 1d · página 3 de 6", and BTC/USDT SHALL read "Concluído" with "1 de 1 combinação"

#### Scenario: Mixed outcome per asset
- **WHEN** NVDA runs 1d and 4h from 1 jan. 2019 to 31 dez. 2020 and only 1d has candles
- **THEN** the NVDA line SHALL read "1 concluída · 1 amostra insuficiente" with "2 de 2 combinações"
- **AND** its detail SHALL say "4h: Amostra insuficiente — sem candles de 4h de NVDA nessa janela" and the 1d daily-precision stretch

#### Scenario: Failure stays visible in Decidir
- **WHEN** SPY ends as "Falha" and the page moves to Decidir at the end of the sweep
- **THEN** the Decidir header SHALL show the real sweep state ("falha parcial") and the note "Sem resultado: SPY — Falha: <motivo>" with a "ver Por ativo" action
- **AND** after a cancel the note SHALL list the assets that did not run ("Não rodou · varredura cancelada") and the header SHALL read "cancelada"

### Requirement: The 1,000-combination ceiling counts ações and ETFs
The ceiling of 1,000 valid combinations per sweep (template × asset × timeframe × direction) SHALL count ações and ETFs like crypto. Above the ceiling, the Preflight SHALL refuse before the start, show the valid total and the assets by class, and ask to narrow the selection. The start action SHALL stay disabled. No sweep SHALL be created above the ceiling.

#### Scenario: All ações of the filter
- **WHEN** the draft selects BTC/USDT, SPY and "Todos do filtro" in Ações (2,431) with one template, 1d and Long
- **THEN** the Preflight SHALL show "2.433 combinações válidas passam do limite de 1.000" with "1 cripto · 2.431 ações · 1 ETF" and "Estreite a seleção"
- **AND** "Iniciar varredura" SHALL stay disabled and the server SHALL reject a start with the same snapshot

### Requirement: Budget, progress, cancel and resume with ações and ETFs
History collection for an ação or ETF SHALL run inside its combination's attempt, under the same lease, heartbeat, attempt budget (3 attempts) and resource limits as the optimization. It SHALL report page progress, so a long collection is not mistaken for a stalled worker. Pause and Cancel SHALL take effect at the same boundaries as today. Results already completed SHALL stay. Resume SHALL continue with the next pending combinations. History already stored SHALL NOT be collected again, and a frozen sample SHALL NOT be frozen again. The Preflight SHALL say how many assets need history collection before the start ("Precisam de coleta de histórico: N de M — <ativos e séries>"). It counts only what Binance has for the window and is not stored yet.

#### Scenario: Pause during collection
- **WHEN** the operator pauses while SPY's history is being collected
- **THEN** the collection page in progress SHALL finish, the sweep SHALL show "Varredura pausada" and resume SHALL continue SPY without collecting the stored pages again

#### Scenario: Cancel keeps finished results
- **WHEN** the operator cancels after BTC/USDT and NVDA finished
- **THEN** their results SHALL stay in the ranking and the pending combinations SHALL become ignored

### Requirement: Survivorship bias is explicit
The Preflight and the Decidir header SHALL warn that the sweep uses only the assets of today's catalog, so assets that left Binance before today are not included. Every Discovery window ends in the past or today, so the warning SHALL appear in every sweep, with the window of the sweep.

#### Scenario: Warning in the Preflight
- **WHEN** the draft has any selection and period
- **THEN** the Preflight SHALL show "Viés de sobrevivência: a varredura usa só os ativos do catálogo de hoje. Ativos que saíram da Binance antes de hoje não entram."

### Requirement: Crypto Discovery regression
A sweep with only crypto pairs SHALL produce the same combinations, the same frozen-sample identity per asset and timeframe, and the same metrics, eligibility and ranking as before this change. The only exceptions are the new class, currency, conventions and precision fields of each row.

#### Scenario: Crypto-only sweep
- **WHEN** a sweep runs BTC/USDT and ETH/USDT in 1d and 4h
- **THEN** its results and ranking SHALL match the same sweep before this change

