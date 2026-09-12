## MODIFIED Requirements

### Requirement: Closed beta blocks public self-registration
The system SHALL keep public self-registration disabled by default during closed beta. A single-use invite for the requested address SHALL be the only way to create an account through `POST /api/auth/register`: the beta invited e-mail allowlist and the `ADMIN_EMAILS` environment list SHALL NOT be an entrance door, and enabling `BETA_PUBLIC_REGISTRATION_ENABLED` SHALL NOT restore account creation without an invite. The invite SHALL be validated for the requested address **before** any duplicate check. Rejections that do not carry a valid invite SHALL NOT reveal whether the address is privileged — present in `ADMIN_EMAILS` or in the beta invited e-mail allowlist. The explicit duplicate rejection of an existing account (HTTP 400) is preserved by the existing duplicate behavior and only becomes reachable **after** a valid invite for that address; it SHALL NOT consume the invite. No registration path SHALL grant administrator role.

#### Scenario: Visitor tries to register without invitation
- **WHEN** a visitor calls `POST /api/auth/register` and public registration is disabled
- **AND** the request does not carry a valid single-use invite for that address
- **THEN** the system SHALL reject the request with HTTP 403
- **AND** the response SHALL explain that beta access requires invitation
- **AND** the response SHALL NOT reveal whether the address is privileged (in `ADMIN_EMAILS` or in the beta invited e-mail allowlist)
- **AND** no user SHALL be created

#### Scenario: Invited email registers
- **WHEN** a visitor calls `POST /api/auth/register` with a valid single-use invite issued for that address and no account exists for it
- **THEN** the system SHALL create the user when the payload is otherwise valid
- **AND** the user SHALL be able to log in with the created password

#### Scenario: Public registration is explicitly enabled
- **WHEN** `BETA_PUBLIC_REGISTRATION_ENABLED` is enabled
- **THEN** the system SHALL still require a valid single-use invite for that address before creating any user through `POST /api/auth/register`
- **AND** the flag SHALL NOT restore account creation without an invite

#### Scenario: Allowlisted admin address registers without invite
- **WHEN** a visitor calls `POST /api/auth/register` with an address present in `ADMIN_EMAILS` or in the beta invited e-mail allowlist
- **AND** the request does not carry a valid single-use invite for that address
- **THEN** the system SHALL reject the request without creating any account
- **AND** the response SHALL NOT reveal whether that address is privileged
- **AND** no account SHALL receive administrator role

#### Scenario: Address with an existing account tries to register
- **WHEN** a visitor calls `POST /api/auth/register` with an address that already belongs to a user
- **AND** the request carries a valid single-use invite issued for that address
- **THEN** the system SHALL keep the existing duplicate behavior and reject the request with HTTP 400
- **AND** the existing account SHALL NOT be modified and SHALL NOT gain administrator role
- **AND** the rejection SHALL NOT consume the invite, so the owner MAY still define a new password through the invite's own password-definition flow
- **AND** without a valid invite for that address the response SHALL NOT reveal whether the account exists

#### Scenario: Burned address recovers through the invite password-definition flow
- **WHEN** an address previously submitted to the public landing holds an account created by the legacy flow, and the operator issues a single-use invite for that same address
- **THEN** the owner SHALL be able to define a new password through the invite's own password-definition flow
- **AND** the system SHALL NOT create a second account for that address and SHALL NOT grant administrator role
- **AND** the invite SHALL NOT rehabilitate the account if it is banned or suspended

#### Scenario: Registration never grants administrator role
- **WHEN** any visitor completes `POST /api/auth/register` successfully, with or without an invite
- **THEN** the created account SHALL be a non-administrator account
- **AND** administrator role SHALL only be granted by deployment bootstrap, by the persisted-role backfill of the already-configured admin, or by an existing administrator
