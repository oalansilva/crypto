## ADDED Requirements

### Requirement: New hard-mode strategy has explicit public copy
Any new `strategy_name` saved by the HARD MODE V3 run SHALL have an explicit `strategy_display_name` and `strategy_description` mapping before the card is reported as technically complete.

#### Scenario: New strategy avoids fallback copy
- **WHEN** `/api/favorites/` returns the saved Favorite
- **THEN** `strategy_display_name` and `strategy_description` are non-empty, strategy-specific, and do not use the generic "Estrategia Cripto Farol" fallback

### Requirement: Public copy mapping is validated
Any new public display or description mapping added by the HARD MODE V3 run SHALL include focused validation that exercises the exact final `strategy_name`.

#### Scenario: Focused mapping test runs
- **WHEN** a new `strategy_name` mapping is added for the saved Favorite
- **THEN** a focused unit test or equivalent validation confirms the expected display name and description
