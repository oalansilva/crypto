## MODIFIED Requirements

### Requirement: MVP operational flows are crypto-only
The system SHALL run MVP analyses and trading flows only with crypto assets, except the individual backtest of exactly one Binance ação or ETF (Combo with one asset, Otimização with one asset and `POST /api/combos/backtest`), enabled by #1119. Ação e ETF da Binance MAY be chosen in the asset selector of Combo, Descoberta and Otimização, but a lote with more than one asset (Combo or Otimização) and descoberta MUST keep refusing them with the explicit reason "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois" until #1120 and #1121 enable those flows. Favorites and Monitor stay crypto-only until #1122.

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

#### Scenario: User runs Combo Optimize with ações or ETFs only
- **WHEN** the user runs Combo Optimize or Combo Configure with more than one asset and all of them are ações or ETFs
- **THEN** the system MUST NOT execute the analysis
- **AND** the user MUST see, before and after running, a warning naming the assets with "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois", never a generic error

#### Scenario: User runs a mixed batch
- **WHEN** the selection of Combo Configure or Combo Optimize has more than one asset and at least one ação or ETF
- **THEN** the batch MUST run only the crypto pairs, one optimization per pair
- **AND** the warning MUST list the ações and ETFs left out, with the reason "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois"

#### Scenario: User views favorites
- **WHEN** the user opens Favorites
- **THEN** the list MUST only include favorites whose symbol is a crypto pair containing `/`

#### Scenario: User views monitor
- **WHEN** the user opens Monitor
- **THEN** opportunities and dashboard symbols MUST only include crypto pairs containing `/`
