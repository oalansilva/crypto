## ADDED Requirements

### Requirement: Individual backtest accepts one ação or ETF

The system SHALL run an individual backtest of exactly one Binance ação or ETF from Combo (`/combo/configure` with one asset left to run), from the Otimização screen (`/combo/optimize` with one asset left to run) and from `POST /api/combos/backtest` (decision of Alan in Design, 23/10/2026). The crypto individual backtest SHALL keep working as today. A request with more than one asset (Combo or Otimização lote, `POST /api/combos/backtest/batch`) and Descoberta SHALL keep refusing ação and ETF with the `asset_class_not_supported` code and the reason "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois", which replaces today's reason (decision of Alan in Design). Ativo marcado pela Binance SHALL keep the refusal of #1117.

#### Scenario: NVDA alone in Combo runs

- **WHEN** Alan selects only NVDA in Combo, picks 1d and runs
- **THEN** the backtest runs for NVDA and opens the result page
- **AND** nothing is saved to favorites

#### Scenario: Crypto alone in Combo is unchanged

- **WHEN** Alan selects only BTC/USDT in Combo without walk-forward and runs
- **THEN** the run optimizes, saves to favorites and opens Favoritos, as today

#### Scenario: NVDA alone in Otimização runs

- **WHEN** Alan selects only NVDA in Otimização, keeps 1d and runs
- **THEN** the optimization runs for NVDA on the fixed window of the screen and the result appears beside it with the identity of the execution
- **AND** nothing is saved to favorites

#### Scenario: Mixed selection runs only the crypto pair

- **WHEN** the Combo or Otimização selection has BTC/USDT and NVDA
- **THEN** only BTC/USDT runs
- **AND** the warning names NVDA as left out with "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois"

#### Scenario: Batch and Descoberta keep refusing

- **WHEN** an ação or ETF is sent to a lote with more than one asset or to a Descoberta sweep
- **THEN** the request is refused with `asset_class_not_supported` and the reason "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois"
- **AND** nothing runs and nothing is collected for that asset

### Requirement: Individual backtest collects only what it uses

An individual backtest of an ação or ETF SHALL call the history service of #1118 (`ensure`) for that asset only, for the chosen timeframe source and, when intrabar precision is requested, for the 5m that builds the 15m. It SHALL wait for a collection already running for the same series up to the limit of #1118 and then run with what is covered. A collection failure with part of the window already stored SHALL run on the covered part and say so; a failure with nothing stored SHALL refuse the run with the reason. Opening, filtering, searching or selecting in the catalog SHALL NOT collect.

#### Scenario: First backtest of AAPL collects its history

- **WHEN** AAPL has no stored history and Alan runs an individual backtest of AAPL on 1h
- **THEN** the 1d and 5m of AAPL are collected for the requested window before the run
- **AND** no other ação or ETF is collected

#### Scenario: Binance rate limit with nothing stored

- **WHEN** the collection of AAPL fails by Binance rate limit and nothing of AAPL is stored
- **THEN** the run is refused with "Histórico de AAPL indisponível agora: limite de requisições da Binance. Tente de novo em alguns minutos."
- **AND** no empty result is shown

#### Scenario: Partial history runs on the covered window

- **WHEN** Alan asks for AAPL since 2010 and the Binance has AAPL since 2014
- **THEN** the run uses the covered window and the result shows the requested and the covered window

#### Scenario: Collection stops with part stored

- **WHEN** the collection of NVDA 1d stops by Binance rate limit after storing up to 2 Oct 2026 and Alan asked up to 22 Oct 2026
- **THEN** the run uses the stored stretch
- **AND** the result shows a warning "Janela coberta menor que a pedida" saying where the collection stopped, the stretch that ran and the stretch left out

#### Scenario: Collection in progress is visible

- **WHEN** Alan runs Combo or Otimização with one ação or ETF and the history is being collected
- **THEN** the screen shows a status line that it is collecting the history of that asset before optimizing

### Requirement: Equity timeframes follow the regular session

For ação and ETF the individual backtest SHALL offer only 15m, 1h, 4h and 1d. 1d SHALL be the native session candle of #1118; 15m, 1h and 4h SHALL be built from the 5m inside the regular session of New York. No candle SHALL cross the session close, and closed market (night, weekend, holiday) SHALL NOT produce candles. 1m and 5m (and 30m in Otimização) SHALL be refused for ação and ETF with a visible reason, shown before the run.

#### Scenario: Last 1h candle of the day ends at the close

- **WHEN** NVDA runs on 1h on a full session
- **THEN** the candles start at 09:30, 10:30 … 15:30 New York time and the last one ends at 16:00

#### Scenario: Half session

- **WHEN** a session closes at 13:00 New York time
- **THEN** the last 1h candle is 12:30–13:00 and the 4h candle is 09:30–13:00

#### Scenario: Daylight saving change

- **WHEN** the window crosses the daylight saving change in New York
- **THEN** every session still starts at 09:30 New York time, with no missing and no extra candle

#### Scenario: 5m left from a crypto selection

- **WHEN** 5m was chosen while BTC/USDT and NVDA were selected and Alan removes BTC/USDT, leaving only NVDA
- **THEN** the timeframe stays 5m and, before any run, the screen says ação and ETF run on 15m, 1h, 4h or 1d
- **AND** the run is not started
- **AND** 1m and 5m stay available while the mixed selection runs only the crypto pair

#### Scenario: 30m in Otimização with an ação

- **WHEN** NVDA alone is selected in Otimização
- **THEN** 1m, 5m and 30m are unavailable and marked "só cripto"

### Requirement: Equity simulation discloses fraction, short and currency

The individual backtest of ação and ETF SHALL use the whole capital in each trade, allowing fractional quantity, like crypto today. The result SHALL say that the simulation used fraction and that this does not confirm fractional trading in the account. A short simulation SHALL say it does not mean the account can sell short. Prices and returns of ação and ETF SHALL be in USD, without conversion to USDT, and the result and the trade list SHALL show USD.

#### Scenario: Fraction warning

- **WHEN** an individual backtest of NVDA finishes
- **THEN** the result says the simulation used fraction of shares and that this does not confirm fraction in the Binance account

#### Scenario: Short on an ETF

- **WHEN** SPY runs short
- **THEN** the result says the short is simulated and does not mean the account can sell short

#### Scenario: Currency in the trade list

- **WHEN** the result of NVDA shows the trade list
- **THEN** prices and position values are shown in USD, never USDT

### Requirement: Trade list uses the currency and the clock of the class

The trade list SHALL show every money column (price, position value, profit, maximum favorable and adverse, cumulative result) in the currency of the class: USDT for crypto, USD for ação and ETF. For ação and ETF on 15m, 1h and 4h, each entry and exit SHALL show date and time in New York time with the time zone indicated (EDT or EST); on 1d only the date (decisions of Alan in Design, 23/10/2026).

#### Scenario: Crypto list in USDT

- **WHEN** the BTC/USDT result shows the trade list
- **THEN** price, position value and profit are shown in USDT, never USD

#### Scenario: SPY 1h list with New York time

- **WHEN** the SPY 1h result shows the trade list
- **THEN** the date column says "Nova York" and the exit of 27 Aug 2026 shows "09:30 EDT"

#### Scenario: NVDA 1d list with date only

- **WHEN** the NVDA 1d result shows the trade list
- **THEN** entries and exits show only the date

### Requirement: Costs, calendar and annualization by class

Each result SHALL state the costs and the annualization it used. Crypto SHALL keep the fee of 0,075% per side and the slippage table by timeframe. Ação and ETF SHALL use the fee of Binance Ações confirmed in the Apply; while not confirmed, the same 0,075% per side marked "assumida". The slippage table by timeframe SHALL apply to every class. Years of a window SHALL be calendar days / 365 for every class. Per-period annualization SHALL use 365 days × candles per day for crypto and 252 sessions × candles per session for ação and ETF (1d = 1, 4h = 2, 1h = 7, 15m = 26).

#### Scenario: NVDA 1h costs shown

- **WHEN** NVDA runs on 1h
- **THEN** the result shows the fee per side, whether it is confirmed or assumida, and 0,03% of slippage per side

#### Scenario: Crypto costs unchanged

- **WHEN** BTC/USDT runs on 4h
- **THEN** the fee is 0,075% per side and the slippage 0,02% per side, as today

### Requirement: Result carries the identity of the execution

The individual backtest result SHALL carry and show: asset, class, source, session, adjustment, currency, timeframe and its origin (native or built from 5m), requested window, covered window, sample version and how long the sample is kept. Ação and ETF results are never favorites, so the sample SHALL follow the 30-day rule of #1118.

#### Scenario: NVDA result identity

- **WHEN** the NVDA result opens
- **THEN** it shows "NVDA · Ação · Binance Ações · pregão regular de Nova York · ajustado por split · USD", the requested and covered windows and the sample version with the date it is kept until

#### Scenario: Split inside the window

- **WHEN** the window of NVDA contains the 10:1 split of June 2024
- **THEN** the series is adjusted and there is no false price jump nor a false stop on the split day

### Requirement: Combo shows what changes for ação and ETF

In Combo (`/combo/configure`), with one ação or ETF selected, the screen SHALL say before the run that it runs the individual backtest and opens the result without saving to favorites; the market data box SHALL name Binance Ações and the regular session, with text contrast of at least 4.5:1; the class note SHALL say ação and ETF for now run only with one asset (Combo or Otimização) and that the lote comes later; the on-demand history text of ação and ETF SHALL say the collection happens when the backtest of one asset runs (Combo and Otimização). Descoberta SHALL keep its current history text and change only the refusal reason.

#### Scenario: Copy before the run

- **WHEN** only NVDA is selected in Combo
- **THEN** the run copy says "1 ação (NVDA): otimiza e abre o resultado, sem salvar em favoritos: ações e ETFs ainda não podem ser favoritados."
- **AND** the market data box says "Binance Ações · pregão regular de Nova York · ajustado por split"
- **AND** 1m and 5m are unavailable in the timeframe list, with the hint that ação and ETF run on 15m, 1h, 4h or 1d

### Requirement: Otimização shows what changes for ação and ETF

In Otimização (`/combo/optimize`), with one ação or ETF selected, the screen SHALL show the fixed window it uses ("Período: 1 a 31 jan. 2024, fixo nesta tela."), SHALL say before the run that it optimizes that asset on that window and shows the result beside it, and SHALL show the result with the block "Dados e execução" of the result page. When the catalog coverage shows that the 5m of the asset does not cover the fixed window, 15m, 1h and 4h SHALL be refused before the run with the reason and the way out (1d here, or Combo, which has a period).

#### Scenario: NVDA 1h in Otimização

- **WHEN** NVDA alone is selected in Otimização with 1h and its 5m starts on 19 May 2026
- **THEN** before running the screen says the 5m of NVDA does not cover 1 a 31 jan. 2024, the fixed period of the screen
- **AND** "Run Optimization" does not start the run
