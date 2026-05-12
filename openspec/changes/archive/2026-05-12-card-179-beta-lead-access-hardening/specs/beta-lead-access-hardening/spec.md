## ADDED Requirements

### Requirement: Landing lead creates temporary beta access safely
The system SHALL create beta access for a new landing lead without exposing temporary password material in API responses, logs, issue evidence, or project fields.

#### Scenario: New lead receives automatic beta access
- **WHEN** a new lead submits valid name, email, and contact fields to `POST /api/leads`
- **THEN** the system SHALL return the same neutral accepted response used for all eligible submissions
- **AND** the system SHALL create an active user for that email only when access instructions can be delivered
- **AND** SHALL hash the generated temporary password before persistence
- **AND** SHALL mark the user as requiring a password change
- **AND** SHALL set a temporary password expiry timestamp
- **AND** SHALL NOT include the temporary password in the HTTP response
- **AND** SHALL NOT reveal whether the email already belongs to an account

#### Scenario: Welcome delivery unavailable
- **WHEN** a new lead submits valid fields but welcome email delivery is unavailable or fails
- **THEN** the system SHALL NOT persist an active user with an unknown temporary password
- **AND** SHALL record the processing result in audit
- **AND** SHALL return the same neutral accepted response

#### Scenario: Existing user lead does not overwrite credentials
- **WHEN** a lead submits an email that already belongs to a user
- **THEN** the system SHALL NOT overwrite the user's password hash
- **AND** SHALL NOT reset password-change state automatically
- **AND** SHALL return a safe accepted response
- **AND** SHALL NOT reveal account existence or temporary-access state

### Requirement: Temporary password cannot be reused indefinitely
The system SHALL prevent indefinite use of temporary beta passwords.

#### Scenario: Temporary password before expiry can log in with forced change
- **WHEN** a temporary-access user submits the correct temporary password before expiry
- **THEN** login SHALL succeed
- **AND** the auth response SHALL include `mustChangePassword=true`

#### Scenario: Expired temporary password cannot log in
- **WHEN** a temporary-access user submits the correct temporary password after expiry
- **THEN** login SHALL be rejected
- **AND** no token SHALL be issued

#### Scenario: Password change clears temporary state
- **WHEN** a temporary-access user successfully changes password
- **THEN** the system SHALL clear the forced password-change flag
- **AND** SHALL clear temporary password expiry
- **AND** SHALL record password-change timestamps

### Requirement: Lead access is audit recorded
The system SHALL record minimal audit events for automatic beta access processing.

#### Scenario: New access audit
- **WHEN** the system creates beta access for a lead
- **THEN** it SHALL record an audit event with email, user id, source, action, result, and timestamp
- **AND** the audit metadata SHALL NOT include temporary password material

#### Scenario: Existing user audit
- **WHEN** the system receives a lead for an existing user
- **THEN** it SHALL record an audit event showing that credentials were not overwritten
