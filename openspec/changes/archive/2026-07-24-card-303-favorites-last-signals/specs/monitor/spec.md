## ADDED Requirements

### Requirement: Monitor signal history remains the canonical last-signal source for Favorites
The Monitor `signal_history` contract SHALL remain the canonical public source of recent confirmed signals reused by Favorites analysis views.

#### Scenario: Favorites reuses Monitor history items
- **WHEN** Favorites renders last signals for a matched opportunity
- **THEN** each item SHALL come from Monitor `signal_history` fields (`timestamp`, `signal`/`type`, optional `price`/`reason`/`explanation`)
- **AND** SHALL keep direction-aware Compra/Venda labeling without changing Monitor generation rules.
