## MODIFIED Requirements

### Requirement: MVP operational flows are crypto-only
The system SHALL run MVP analyses and trading flows only with crypto assets, with three exceptions. The first is the individual backtest of exactly one Binance ação or ETF (Combo with one asset, Otimização with one asset and `POST /api/combos/backtest`), enabled by #1119. The second is the lote of Combo and Otimização, which accepts crypto, ações and ETFs together, enabled by #1120. The third is the Descoberta, which accepts crypto, ações and ETFs in the same sweep, enabled by #1121. Ação e ETF da Binance MAY be chosen in the asset selector of Combo, Descoberta and Otimização. Favorites MUST list crypto, ações and ETFs (#1120); Monitor stays crypto-only until #1122.

#### Scenario: User configures a combo
- **WHEN** the user opens Combo Configure
- **THEN** the asset selection MUST offer the Binance catalog with crypto pairs quoted in USDT, ações and ETFs, each identified by class
- **AND** the request payload MUST NOT send stock data-source overrides

#### Scenario: User runs Combo with one ação or ETF
- **WHEN** the user runs Combo Configure with only one ação or ETF selected
- **THEN** the system MUST run the individual backtest for that asset and open the result page
- **AND** the result MUST NOT be saved to favorites

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
- **AND** the reason "ação e ETF por enquanto rodam no Combo e na Otimização (1 ativo ou lote); a Descoberta vem depois" MUST NOT appear

#### Scenario: User views favorites
- **WHEN** the user opens Favorites
- **THEN** the list MUST include crypto, ação and ETF favorites, each with its class and currency

#### Scenario: User views monitor
- **WHEN** the user opens Monitor
- **THEN** opportunities and dashboard symbols MUST only include crypto pairs containing `/`
