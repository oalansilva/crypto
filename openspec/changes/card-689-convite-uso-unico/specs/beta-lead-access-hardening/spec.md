## MODIFIED Requirements

### Requirement: Landing lead creates temporary beta access safely
The system SHALL validate the single-use invite for the submitted address before any account decision, and SHALL NOT create or modify any user account from `POST /api/leads`, with or without an `inviteToken`. `POST /api/leads` SHALL remain a funnel event that returns the same neutral accepted response for every eligible submission. Without a valid invite the submission SHALL remain a neutral funnel event with no account, no generated temporary password, and no burned address. With a valid single-use invite issued for that same address the submission SHALL still create no account, SHALL NOT consume the invite, and SHALL leave the invite open so its holder consumes it on the invite link's own `POST` (`${BETA_INVITE_BASE_URL}/beta-invite/<token>`), which is the only surface where the owner defines the password and where the account is created or its password reset. When the submitted address already owns an account, `POST /api/leads` SHALL NOT touch that account, SHALL NOT overwrite its password hash, and SHALL NOT create a second account. Generated temporary password, forced password-change state, and temporary-password expiry SHALL belong only to the legacy path without an invite of `beta_access.py`, which still runs until enforcement. The system SHALL NOT expose temporary password material, invite tokens, or account existence in API responses, logs, issue evidence, or project fields.

#### Scenario: Lead with a valid invite does not consume it and creates no account
- **WHEN** a new lead submits valid name, email, and contact fields to `POST /api/leads` together with an `inviteToken` that is a valid single-use invite for that same address
- **THEN** the system SHALL return the same neutral accepted response used for all eligible submissions
- **AND** the system SHALL NOT create a user for that address and SHALL NOT modify any existing account
- **AND** the system SHALL NOT consume the invite: it SHALL remain open and still consumable on the invite link's own `POST` (`${BETA_INVITE_BASE_URL}/beta-invite/<token>`), where the owner defines the password
- **AND** the system SHALL NOT burn the address
- **AND** the system SHALL NOT generate or persist a temporary password, SHALL NOT mark the account as requiring a password change, and SHALL NOT set a temporary password expiry timestamp
- **AND** no account SHALL receive administrator role as a result of the submission

#### Scenario: Legacy temporary-password semantics stay out of the invite path
- **WHEN** a lead submission is processed by the legacy path without an invite while `beta_access.py` still carries that behavior before enforcement
- **THEN** the generated temporary password, the forced password-change state, and the temporary password expiry SHALL apply only to that legacy path
- **AND** the account created or recovered through a single-use invite link SHALL NOT carry any of those temporary-password semantics

#### Scenario: Welcome delivery unavailable
- **WHEN** a new lead is processed by the legacy path and welcome delivery is unavailable or fails
- **THEN** the system SHALL NOT persist an active user with an unknown temporary password
- **AND** SHALL record the processing result in audit
- **AND** SHALL return the same neutral accepted response

#### Scenario: Existing user lead does not overwrite credentials
- **WHEN** a lead submits an email that already belongs to a user
- **THEN** the system SHALL NOT overwrite the user's password hash
- **AND** SHALL NOT reset password-change state automatically
- **AND** SHALL NOT create a second account for that address
- **AND** SHALL return a safe accepted response
- **AND** SHALL NOT reveal account existence or temporary-access state
- **AND** when that submission also carries a valid invite for the same address, the owner's access SHALL be restored only through the invite's own password-definition flow, never by an anonymous landing submission, and that submission SHALL NOT consume the invite
- **AND** the system SHALL NOT burn the address for the invite's own password-definition flow

#### Scenario: Lead without a valid invite creates no account
- **WHEN** a lead submits valid fields to `POST /api/leads` without a valid single-use invite issued for that same address
- **THEN** the system SHALL return the same neutral accepted response used for all eligible submissions
- **AND** the system SHALL NOT create a user for that address
- **AND** the system SHALL NOT generate or persist a temporary password for that address
- **AND** the system SHALL NOT burn the address, so the same address MAY still register later through a single-use invite

#### Scenario: Burned address recovers through a new invite
- **WHEN** an address was previously submitted to `POST /api/leads` without an invite, the legacy path already created an account for it, and the operator later issues a single-use invite for that same address
- **THEN** the legitimate owner SHALL be able to enter through that invite
- **AND** the previously submitted address SHALL NOT remain permanently blocked
- **AND** the system SHALL NOT create a second account for that address
- **AND** the invite SHALL authorize only the owner's password reset through the invite's own password-definition flow
- **AND** the invite SHALL NOT change the existing role, SHALL NOT grant administrator role, and SHALL NOT rehabilitate a banned or suspended account

#### Scenario: Lead without invite does not reveal account existence
- **WHEN** `POST /api/leads` is called without a valid invite for an address that already belongs to a user
- **THEN** the response SHALL be the same neutral accepted response used for an address without an account
- **AND** the response SHALL NOT reveal whether the address already exists

### Requirement: Lead access is audit recorded
The system SHALL record minimal audit events for beta access processing on the landing lead endpoint, including when the submission carries a single-use invite that the landing validates without consuming it.

#### Scenario: New access audit
- **WHEN** the system creates beta access for a lead through the legacy path without an invite
- **THEN** it SHALL record an audit event with email, user id, source, action, result, and timestamp
- **AND** the audit metadata SHALL NOT include temporary password material

#### Scenario: Existing user audit
- **WHEN** the system receives a lead for an existing user
- **THEN** it SHALL record an audit event showing that credentials were not overwritten
- **AND** when that submission also carries a valid invite for the same address, it SHALL record that the invite was validated and left open, SHALL NOT consume it and SHALL NOT record administrator role or token material

#### Scenario: Lead with a valid invite audit
- **WHEN** the system receives a lead carrying a valid single-use invite for that address
- **THEN** it SHALL record an audit event with email, source, action, result, and timestamp
- **AND** the audit metadata SHALL NOT include invite token material
- **AND** the result SHALL classify the submission as received with the invite validated but not consumed

#### Scenario: Lead without invite audit
- **WHEN** the system receives a lead without a valid invite for that address and therefore creates no account
- **THEN** it SHALL record an audit event with email, source, action, result, and timestamp
- **AND** the audit metadata SHALL NOT include invite token material
- **AND** the result SHALL classify the submission as received without account creation

## ADDED Requirements

### Requirement: Landing lead never consumes an invite and never creates an account
The landing lead endpoint SHALL NOT be an account-creation surface and SHALL NOT consume a single-use invite, so the invite stays open for its holder to consume on the invite link's own `POST` and define the password there. Consuming the invite in `POST /api/leads` and creating the account before a password exists SHALL be a rejected alternative: it would persist an account with no usable password (`users.password_hash` is `NOT NULL`) whose only route to a password is an invite already spent.

#### Scenario: Rejected alternative — landing consumes the invite and creates the account before a password exists
- **WHEN** `POST /api/leads` carried a valid single-use invite and, instead of leaving it open, consumed it and created the active account for that address before any password was defined
- **THEN** that behavior SHALL be rejected because the account would hold no usable password while the invite needed to define one is already spent
- **AND** the submitted address would be burned for the invite link, so the owner could no longer define a password
- **AND** the account would be left active without a usable credential
- **AND** the invite SHALL instead stay open for the invite link's own `POST`, which creates the account or resets the owner's password

#### Scenario: Only the invite link's own posting consumes the invite
- **WHEN** a single-use invite exists for an address and the holder has not yet posted the invite link's own password-definition form
- **THEN** no call to `POST /api/leads` SHALL consume that invite or create the account for that address
- **AND** the invite SHALL be consumed exactly once by the invite link's own `POST`, where the owner defines the password

