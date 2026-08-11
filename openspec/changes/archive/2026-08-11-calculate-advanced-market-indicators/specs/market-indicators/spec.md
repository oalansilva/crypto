## ADDED Requirements

### Requirement: Sistema calcula indicadores avançados em todos os timeframes ativos

The system SHALL compute Bollinger Bands, ATR, Stochastic, OBV, and Ichimoku values for each configured `symbol`/`timeframe` pair processed by the dedicated market indicator pipeline.

#### Scenario: Indicadores avançados gerados por candle fechado

- **GIVEN** candles OHLCV fechados para um `symbol`/`timeframe` ativo
- **WHEN** o pipeline dedicado de indicadores roda
- **THEN** o sistema SHALL calcular Bollinger Bands, ATR, Stochastic, OBV e Ichimoku para cada candle elegível
- **AND** valores SHALL permanecer nulos durante a fase de aquecimento quando a janela mínima ainda não existir

#### Scenario: Indicadores avançados disponíveis para scoring

- **GIVEN** um run de scoring precisa de features técnicas avançadas
- **WHEN** o scoring lê indicadores técnicos
- **THEN** o sistema SHALL ler Bollinger Bands, ATR, Stochastic, OBV e Ichimoku do armazenamento dedicado de indicadores
- **AND** o scoring MUST NOT recalcular esses indicadores em linha

### Requirement: Sistema persiste indicadores avançados com integridade e metadados

The system SHALL persist advanced indicator values in the dedicated market indicator storage while preserving uniqueness by `symbol`, `timeframe`, and candle timestamp.

#### Scenario: Persistência idempotente de indicadores avançados

- **GIVEN** um registro técnico para `symbol`, `timeframe` e `ts`
- **WHEN** indicadores avançados são persistidos
- **THEN** o sistema SHALL armazenar os valores avançados no mesmo registro lógico do candle
- **AND** retries/replays MUST update the existing row instead of creating duplicates
- **AND** metadata such as `provider`, `source_window`, `row_count`, `is_recomputed`, and `updated_at` MUST remain populated

#### Scenario: Recompute incremental preserva consistência

- **GIVEN** indicadores avançados já persistidos para um `symbol`/`timeframe`
- **WHEN** um novo candle chega e o recompute incremental roda
- **THEN** o sistema SHALL recalculate only the required lookback window for all basic and advanced indicators
- **AND** rows outside the recompute window MUST remain unchanged

### Requirement: Fórmulas de indicadores avançados são documentadas

The system SHALL document the formulas, default parameters, and displacement semantics used for each advanced indicator.

#### Scenario: Fórmulas disponíveis para revisão técnica

- **WHEN** um reviewer consulta a documentação da change
- **THEN** ela MUST define Bollinger Bands as SMA plus/minus standard-deviation bands
- **AND** ATR as Wilder-style average true range over true range values
- **AND** Stochastic as close position within the rolling high-low range plus `%K`/`%D` smoothing
- **AND** OBV as cumulative volume adjusted by close direction
- **AND** Ichimoku as Tenkan, Kijun, Senkou A, Senkou B, and Chikou using highest-high/lowest-low windows and documented displacement

### Requirement: Indicadores avançados usam parâmetros padrão explícitos

The system SHALL use explicit default parameters for advanced indicators unless a later capability introduces configurable indicator parameter sets.

#### Scenario: Parâmetros padrão aplicados no runtime

- **WHEN** o pipeline calcula indicadores avançados sem parâmetros customizados
- **THEN** Bollinger Bands MUST use length 20 and standard deviation multiplier 2
- **AND** ATR MUST use length 14
- **AND** Stochastic MUST use fast `%K` length 14, `%K` smoothing 3, and `%D` smoothing 3
- **AND** Ichimoku MUST use Tenkan 9, Kijun 26, Senkou Span B 52, and displacement 26
- **AND** OBV MUST use close and volume without a lookback period

### Requirement: Validação cruzada usa três fontes de referência

The system SHALL include automated validation evidence for advanced indicator calculations using three independent reference sources where applicable.

#### Scenario: Uso de fixtures TradingView como base de validação

- **GIVEN** fixtures OHLCV exportados da TradingView
- **WHEN** testes de paridade executam
- **THEN** the system SHALL use those candles as reference market input for advanced indicator validation
- **AND** existing TradingView basic indicator reference columns MUST continue to pass within indicator-specific tolerances

#### Scenario: Paridade com TA-Lib para indicadores suportados

- **GIVEN** the runtime has TA-Lib available
- **WHEN** tests compare supported advanced indicators against TA-Lib calculations
- **THEN** Bollinger Bands, ATR, Stochastic, and OBV SHALL match TA-Lib outputs within indicator-specific tolerances
- **AND** Ichimoku MUST be excluded from TA-Lib parity because TA-Lib does not provide an Ichimoku function

#### Scenario: Paridade com pandas-ta para indicadores suportados

- **GIVEN** the runtime has pandas-ta available in the test environment
- **WHEN** tests compare supported advanced indicators against pandas-ta calculations
- **THEN** Bollinger Bands, ATR, Stochastic, and OBV SHALL match pandas-ta outputs within indicator-specific tolerances
- **AND** Ichimoku MUST be treated separately because chart displacement conventions differ from source-candle-aligned storage

#### Scenario: Paridade com implementação independente de fórmulas

- **GIVEN** an independent formula implementation in tests
- **WHEN** tests compare runtime output with documented formulas
- **THEN** Bollinger Bands, ATR, Stochastic, OBV, and Ichimoku SHALL match the independent formula outputs within indicator-specific tolerances

### Requirement: Ichimoku usa fórmulas corretas de midpoint

The system SHALL calculate Ichimoku lines using rolling highest-high and lowest-low midpoints, not independent high-only or low-only rolling values.

#### Scenario: Cálculo correto de Tenkan e Kijun

- **WHEN** Ichimoku is calculated for a candle with enough history
- **THEN** Tenkan MUST equal `(highest_high_9 + lowest_low_9) / 2`
- **AND** Kijun MUST equal `(highest_high_26 + lowest_low_26) / 2`

#### Scenario: Cálculo correto de spans e Chikou

- **WHEN** Ichimoku spans are calculated for a candle with enough history
- **THEN** Senkou Span A MUST equal `(Tenkan + Kijun) / 2`
- **AND** Senkou Span B MUST equal `(highest_high_52 + lowest_low_52) / 2`
- **AND** Chikou MUST represent the close series with the documented 26-period lagging displacement
- **AND** persisted values MUST document whether displacement is represented as metadata or shifted timestamps
