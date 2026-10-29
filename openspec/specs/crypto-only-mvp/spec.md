# crypto-only-mvp Specification

## Purpose
TBD - created by archiving change issue-107-remover-acoes. Update Purpose after archive.
## Requirements
### Requirement: MVP operational flows are crypto-only
The system SHALL run MVP analyses and trading flows only with crypto assets, with these exceptions:
- The individual backtest of exactly one Binance ação or ETF (Combo with one asset, Otimização with one asset and `POST /api/combos/backtest`), enabled by #1119.
- The lote of Combo and Otimização, which accepts crypto, ações and ETFs together, enabled by #1120.
- The Descoberta, which accepts crypto, ações and ETFs in the same sweep, enabled by #1121.
- Favorites, Monitor and Telegram alerts, which accept favorites of crypto, ações and ETFs, enabled by #1122.

Ação e ETF da Binance MAY be chosen in the asset selector of Combo, Descoberta and Otimização. Trading flows (Operar, protective stop) MUST stay crypto-only.

#### Scenario: User configures a combo
- **WHEN** the user opens Combo Configure
- **THEN** the asset selection MUST offer the Binance catalog with crypto pairs quoted in USDT, ações and ETFs, each identified by class
- **AND** the request payload MUST NOT send stock data-source overrides

#### Scenario: User runs Combo with one ação or ETF
- **WHEN** the user runs Combo Configure with only one ação or ETF selected
- **THEN** the system MUST run the individual backtest for that asset and open the result page
- **AND** the result page MUST offer "Salvar nos Favoritos" for that asset

#### Scenario: User runs Combo Optimize with one ação or ETF
- **WHEN** the user runs Combo Optimize with only one ação or ETF selected
- **THEN** the system MUST run the individual backtest for that asset on the fixed window of the screen and show the result beside it

#### Scenario: User runs a mixed batch
- **WHEN** the selection of Combo Configure or Combo Optimize has more than one asset, with crypto, ações or ETFs
- **THEN** after the user confirms the lote, the batch MUST run every asset of the selection, one optimization per asset, each with its class, source, session, adjustment and currency
- **AND** ações and ETFs MUST be left out before the lote starts, with the reason, only when the timeframe does not serve them (1m and 5m; also 30m in Combo Optimize, and 15m, 1h or 4h in Combo Optimize when their 5m does not cover the fixed window)

#### Scenario: User runs a batch of ações or ETFs only
- **WHEN** the selection has more than one asset and all of them are ações or ETFs, on a timeframe that serves them
- **THEN** the batch MUST run all of them and save the best result of each to favorites with the note "gerado em lote"

#### Scenario: User runs Descoberta with ação or ETF
- **WHEN** the Descoberta selection includes an ação or ETF that Binance does not mark
- **THEN** the system MUST include it in the sweep with its class, source, session, adjustment and currency

#### Scenario: User views favorites
- **WHEN** the user opens Favorites
- **THEN** the list MUST include crypto, ação and ETF favorites, each with its class, currency and configuration

#### Scenario: User views monitor
- **WHEN** the user opens Monitor
- **THEN** opportunities MUST include the user's rated favorites of crypto, ações and ETFs, each with its class, currency, configuration and market state
- **AND** Operar MUST stay available only for crypto pairs quoted in USDT

### Requirement: MVP market APIs reject stocks
The system SHALL reject stock market operations while the MVP is crypto-only.

#### Scenario: Request stock candle data
- **WHEN** a client requests `/api/market/candles` with a stock ticker
- **THEN** the API MUST return a 400 response explaining that the MVP supports only crypto pairs

#### Scenario: Request stock universe
- **WHEN** a client requests `/api/markets/us/nasdaq100`
- **THEN** the API MUST return an unavailable response explaining that stocks are disabled for the MVP

