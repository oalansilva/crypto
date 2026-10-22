## MODIFIED Requirements

### Requirement: MVP operational flows are crypto-only
The system SHALL run MVP analyses and trading flows only with crypto assets. Ação e ETF da Binance MAY be chosen in the asset selector of Combo, Descoberta and Otimização, but backtest, combo, otimização, lote and descoberta MUST refuse them with an explicit reason until the following stories of epic #1116 enable those classes.

#### Scenario: User configures a combo
- **WHEN** the user opens Combo Configure
- **THEN** the asset selection MUST offer the Binance catalog with crypto pairs quoted in USDT, ações and ETFs, each identified by class
- **AND** the request payload MUST NOT send stock data-source overrides

#### Scenario: User runs a combo with an ação or ETF
- **WHEN** the user runs Combo Configure or Combo Optimize with an ação or ETF selected
- **THEN** the system MUST NOT execute the analysis for that asset
- **AND** the user MUST see, before and after running, a warning naming the asset and stating that the analysis is not yet available for ações and ETFs, never a generic error

#### Scenario: User runs a mixed batch
- **WHEN** the selection of Combo Configure or Combo Optimize has crypto pairs and an ação or ETF
- **THEN** the batch MUST run only the crypto pairs, one optimization per pair
- **AND** the warning MUST list the ações and ETFs left out, with the reason

#### Scenario: User views favorites
- **WHEN** the user opens Favorites
- **THEN** the list MUST only include favorites whose symbol is a crypto pair containing `/`

#### Scenario: User views monitor
- **WHEN** the user opens Monitor
- **THEN** opportunities and dashboard symbols MUST only include crypto pairs containing `/`
