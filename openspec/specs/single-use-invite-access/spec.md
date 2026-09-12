# single-use-invite-access Specification

## Purpose
TBD - created by archiving change card-689-convite-uso-unico. Update Purpose after archive.
## Requirements
### Requirement: Single-use invite is the only door for a new account
The system SHALL treat a single-use invite as the authorization that lets one specific address create one account during the closed beta. A single-use invite is materialized by an invite token, delivered as a copyable link, bound to exactly one address, and it expires. Neither the beta invited e-mail allowlist nor the `ADMIN_EMAILS` environment list SHALL authorize account creation without a valid invite.

#### Scenario: Invite for the invited address lets the owner create the account
- **WHEN** the owner of the invited address opens the copyable invite link and submits a valid registration payload
- **THEN** the system SHALL create exactly one account for that address
- **AND** the account SHALL use the password chosen by that owner
- **AND** the account SHALL NOT be an administrator

#### Scenario: Invite link is the entry surface where the owner defines the password
- **WHEN** the owner of the invited address opens the copyable invite link (`${BETA_INVITE_BASE_URL}/beta-invite/<token>`)
- **THEN** the invite flow SHALL serve the password-definition form for that address
- **AND** the address of the submission SHALL be the invited one: either pre-filled and locked by the invite, or a field that must match the bound address
- **AND** submitting the form SHALL consume the invite once and define the owner's password
- **AND** that link SHALL NOT be a catalog route (`/monitor`, `/favorites`, `/combo/*`) nor the `landing` surface

#### Scenario: Address present only in the allowlist creates nothing
- **WHEN** an address is present in the beta invited e-mail allowlist or in `ADMIN_EMAILS` and no single-use invite exists for it
- **THEN** the system SHALL NOT create an account for that address
- **AND** the response SHALL NOT reveal whether the address is privileged

### Requirement: Invite token is bound to the invited address
The system SHALL bind every invite token to one normalized address. Consuming an invite with a different address SHALL be refused, so a forwarded link is useless to another address.

#### Scenario: Consuming an invite with another address is refused
- **WHEN** a caller tries to consume an invite using an address different from the invited address
- **THEN** the system SHALL refuse the entry
- **AND** no account SHALL be created for either address
- **AND** the system SHALL record the refusal in audit

#### Scenario: Address comparison is normalization aware
- **WHEN** a caller consumes an invite using the invited address with different letter casing or surrounding whitespace
- **THEN** the system SHALL treat it as the same address and allow the consumption

### Requirement: Invite token can be consumed only once
The system SHALL allow at most one successful consumption per invite token. A second consumption attempt SHALL fail explicitly with a dedicated refusal, not a generic error.

#### Scenario: First consumption succeeds
- **WHEN** the invited address consumes a valid invite token for the first time
- **THEN** the consumption SHALL succeed and the invite SHALL become consumed
- **AND** the account created for that address SHALL be returned to that flow

#### Scenario: Second consumption fails explicitly
- **WHEN** the same invite token is used again after a successful consumption
- **THEN** the system SHALL refuse the entry with a dedicated, actionable refusal
- **AND** the refusal SHALL NOT be a generic server error
- **AND** no account SHALL be created or modified by the second attempt
- **AND** the system SHALL record the attempt in audit

### Requirement: Invite token expires
The system SHALL give every invite token an expiration timestamp. A token past its expiration SHALL NOT be consumable and the refusal SHALL be actionable.

#### Scenario: Expired invite is refused with an actionable message
- **WHEN** a caller tries to consume an invite after its expiration timestamp
- **THEN** the system SHALL refuse the entry
- **AND** the refusal SHALL tell the holder to request a new invite link from the operator
- **AND** no account SHALL be created
- **AND** the system SHALL record the expired attempt in audit

#### Scenario: Invite before expiration is consumable
- **WHEN** a caller consumes an invite before its expiration timestamp
- **THEN** the system SHALL accept the consumption when the address matches and the invite is still open

### Requirement: Invite token is a secret at rest
The system SHALL generate an unpredictable invite token, SHALL persist only a digest of it, and SHALL return the token in clear only in the issuance response. The token SHALL NOT appear in audit records, application logs, or any other response.

#### Scenario: Token is not persisted in clear
- **WHEN** an invite is issued
- **THEN** the persisted record SHALL contain a non-reversible digest of the token and SHALL NOT contain the token in clear

#### Scenario: Token does not leak into audit or logs
- **WHEN** an invite is issued, consumed, refused, or expires
- **THEN** the corresponding audit record and log output SHALL NOT contain the invite token in clear
- **AND** the clear token SHALL be present only in the issuance HTTP response

#### Scenario: Guessing the link is not feasible
- **WHEN** an attacker without the link tries to consume an invite by guessing token values
- **THEN** the system SHALL refuse every guessed value
- **AND** the token space SHALL be large enough that guessing is not a practical path

### Requirement: Invite reissue supersedes open invites for the same address
The system SHALL let an operator reissue an invite for the same address when the previous link is lost. Reissuing SHALL leave at most one open invite token per address, so a lost or forwarded link stops working.

#### Scenario: Reissue for the same address is allowed
- **WHEN** an operator issues a new invite for an address that already has a valid open invite
- **THEN** the system SHALL issue the new invite successfully
- **AND** the response SHALL include the new copyable link

#### Scenario: Previous open token stops working after reissue
- **WHEN** an invite is reissued for the same address
- **THEN** the previously open invite token for that address SHALL be revoked
- **AND** consuming the revoked token SHALL be refused with an actionable message
- **AND** the new invite token SHALL remain consumable

#### Scenario: Consumed or expired invites are left untouched
- **WHEN** an invite is reissued for an address that also has consumed or expired invite records
- **THEN** those records SHALL remain unchanged as audit history
- **AND** the reissuance SHALL be recorded with a link to the new invite

### Requirement: Invite lifecycle is audit recorded
The system SHALL record invite issuance, consumption, and every refusal in `beta_access_audit_logs` with email, user identity when it exists, source, action, result, and timestamp.

#### Scenario: Issuance is audited
- **WHEN** an administrator issues an invite
- **THEN** the system SHALL record an audit event for the issuance with the invited address, the actor, the source, the action, the result, and the timestamp

#### Scenario: Successful consumption is audited
- **WHEN** an invited address consumes an invite and an account is created
- **THEN** the system SHALL record an audit event for the consumption with the address, the created user identity, the source, the action, the result, and the timestamp

#### Scenario: Expired invite is audited
- **WHEN** a caller tries to consume an expired invite
- **THEN** the system SHALL record an audit event classifying the attempt as expired
- **AND** the audit metadata SHALL NOT contain the invite token

#### Scenario: Repeated consumption is audited
- **WHEN** a caller tries to consume an invite token that was already consumed
- **THEN** the system SHALL record an audit event classifying the attempt as repeated consumption

#### Scenario: Address mismatch is audited
- **WHEN** a caller tries to consume an invite using a different address
- **THEN** the system SHALL record an audit event classifying the attempt as an address mismatch

### Requirement: Invite for an address that already has an account restores the owner by password reset
The system SHALL NOT create a second account when a valid invite is consumed for an address that already owns one. For that address the invite SHALL authorize only the owner's password reset through the invite's own password-definition flow, and SHALL NEVER change the existing role or grant administrator role.

#### Scenario: Invite for an existing account does not duplicate and only resets the password
- **WHEN** a valid invite issued for an address that already owns an account is consumed
- **THEN** the system SHALL NOT create a second account
- **AND** the invite SHALL authorize only a password reset by the owner through the invite's own password-definition flow, with the token valid for that address
- **AND** the password hash SHALL change only from the owner's submission in that flow, never as a side effect of an anonymous submission
- **AND** the invite SHALL NOT change the existing role and SHALL NOT grant administrator role

#### Scenario: Invite does not rehabilitate a banned or suspended account
- **WHEN** a valid invite for an address whose account is banned or suspended is consumed
- **THEN** the system SHALL NOT change that account's status or ban state
- **AND** the login refusal for that account SHALL remain in force

#### Scenario: No temporary password is delivered by message
- **WHEN** an account is created or recovered through a single-use invite
- **THEN** no temporary password SHALL be delivered to the holder through a message or e-mail
- **AND** the holder SHALL define the account password through the invite link

