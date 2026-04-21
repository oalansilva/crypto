## ADDED Requirements

### Requirement: System records admin user-management actions
The system SHALL persist an immutable audit record for each admin action affecting users.

#### Scenario: Record user lifecycle change
- **WHEN** an admin performs create, update, ban, suspend, or reactivate actions
- **THEN** the system SHALL append a log entry with actor user ID, target user ID, action, reason, UTC timestamp, and correlation ID when available

#### Scenario: Record non-destructive admin actions
- **WHEN** an admin only views a user record
- **THEN** the system SHALL optionally record a view action when query indicates `audit=true`

### Requirement: Audit log preserves privacy baseline
The system SHALL expose logs with minimal personal data while maintaining accountability.

#### Scenario: PII-minimized audit response
- **WHEN** support staff calls `GET /api/admin/user-actions`
- **THEN** each entry MUST include action metadata and actor/target identifiers
- **AND** MUST NOT expose credential fields or raw password hashes

#### Scenario: Retention and export boundaries
- **WHEN** logs are queried beyond retention policy window
- **THEN** entries outside retention MUST be removed or archived according to deployment policy

### Requirement: Audit log is filterable and paginated
The system SHALL support filtering and pagination for operational triage.

#### Scenario: Filter by actor and action
- **WHEN** admin queries `GET /api/admin/user-actions` with `actorUserId`, `action`, `from`, `to`
- **THEN** the system SHALL return matching entries only and apply pagination consistently

#### Scenario: Sort and inspect chronological list
- **WHEN** admin calls `GET /api/admin/user-actions` without filters
- **THEN** the system SHALL return entries ordered by newest first

### Requirement: Audit log supports frontend support context
The system SHALL provide an admin-facing endpoint suitable for in-app review inside the user-management panel.

#### Scenario: Panel opens audit panel for a user
- **WHEN** admin opens the audit tab for a selected user
- **THEN** the system SHALL return recent actions filtered by `targetUserId`
- **AND** include action reason and operator metadata for each record
