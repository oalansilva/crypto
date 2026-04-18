## ADDED Requirements

### Requirement: Unified signals must expose freshness metadata per source
The system SHALL include timing metadata for each contributing source so the client can assess recency quickly without breaking when freshness inputs are partial.

#### Scenario: Source freshness is explicit
- **WHEN** a source contributes to a unified signal
- **THEN** that source entry MUST include freshness metadata containing at least `updated_at`, `age_seconds` and a stale indicator

#### Scenario: Freshness degrades safely when timing metadata is incomplete
- **WHEN** a source contributes without a usable timestamp or with incomplete freshness inputs
- **THEN** the unified signal MUST remain renderable with explicit fallback semantics and MUST NOT break the dashboard client

### Requirement: Final conviction must reflect source agreement, conflicts and stale inputs
The system SHALL compute per-source agreement metadata and a final trust summary that explains why a signal has high, medium or low conviction.

#### Scenario: Source alignment is explicit
- **WHEN** a source contributes to a unified signal
- **THEN** that source entry MUST indicate whether it agrees, conflicts or only partially supports the final consolidated action

#### Scenario: High convergence raises conviction
- **WHEN** multiple fresh sources support the same final action
- **THEN** the unified signal MUST expose a higher convergence or conviction summary and a human-readable display reason

#### Scenario: Conflict or stale data lowers conviction with warning
- **WHEN** one or more contributing sources are stale or conflict with the final action
- **THEN** the unified signal MUST expose warning metadata that allows the UI to show reduced trust for that asset
