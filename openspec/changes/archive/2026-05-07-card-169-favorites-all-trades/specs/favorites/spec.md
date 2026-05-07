## ADDED Requirements

### Requirement: Favorites analysis preserves all recoverable trades
The Favorites page SHALL preserve all saved or regenerated trades when opening a full analysis result from a favorite, even when Monitor synchronization returns a shorter `signal_history`.

#### Scenario: Monitor sync has fewer trades than favorite history
- **WHEN** the user opens full analysis from a favorite with saved or regenerated trades
- **AND** Monitor synchronization returns fewer trades for the same strategy
- **THEN** the result trade list SHALL include the saved or regenerated favorite trades
- **AND** the Monitor synchronization SHALL NOT replace the favorite trade list with the shorter Monitor set

#### Scenario: Monitor sync adds a missing current trade
- **WHEN** the user opens full analysis from a favorite
- **AND** Monitor synchronization returns a trade not already present in the saved or regenerated favorite history
- **THEN** the result trade list SHALL include that additional Monitor trade
- **AND** duplicate trades from both sources SHALL appear only once

#### Scenario: Protected favorite remains redacted for common user
- **WHEN** a common user opens full analysis for a protected favorite
- **THEN** the result SHALL preserve the protected favorite's available trades
- **AND** the result SHALL NOT expose protected parameters, indicators, moving-average overlays, or moving-average values
