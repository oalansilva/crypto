## ADDED Requirements

### Requirement: Active-sweep restore retries itself while the session is authenticated

When `restoreSession` (or equivalent GET of `/combos/discovery/sweeps/active`) fails while the operator is still authenticated, the client SHALL repeat that verification by itself until it hydrates the live non-terminal sweep into Acompanhar. «Tentar novamente» SHALL appear only after that automatic reconstitution fails again. A 401 SHALL continue to the existing «Sessão expirada» screen (out of this card). This requirement does not replace restore-after-F5 (#664); it covers verification failure with the session still authenticated.

If the active payload already contains a non-terminal sweep, the UI SHALL bind that sweep and show Acompanhar progress from its counters even when snapshot-axis hydration is not yet complete. The failure SHALL NOT cancel or duplicate the sweep on the server. Starting another sweep SHALL stay blocked until the operator can see Acompanhar of the live run.

#### Scenario: Transient active GET recovers without a click

- **GIVEN** a live sweep on the server and an authenticated session
- **WHEN** the first active-sweep verification fails (network / 5xx / timeout) and automatic retry then succeeds
- **THEN** Acompanhar shows that sweep's real id and progress
- **AND** the operator did not click «Tentar novamente»
- **AND** the sweep on the server is neither cancelled nor duplicated

#### Scenario: Known sweep_id does not park on empty Montar

- **GIVEN** the active payload returns a non-terminal sweep whose snapshot axes are missing or hydration of the draft fails
- **WHEN** the UI applies that payload
- **THEN** Acompanhar is still shown with that `sweep_id` and the sweep counters
- **AND** the screen does not stay on empty Montar + «Acompanhando #—»

#### Scenario: Retry is residual after automatic reconstitution exhausts

- **GIVEN** automatic reconstitution of the live sweep has exhausted its attempts and the session is still authenticated
- **WHEN** the operator looks at Descoberta
- **THEN** the red banner and «Tentar novamente» are visible
- **AND** starting another sweep remains blocked
- **AND** the live sweep on the server is still protected
