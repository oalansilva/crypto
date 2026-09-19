## ADDED Requirements

### Requirement: Acompanhar reconstitutes itself for the live sweep

When an authenticated operator opens `/combo/discovery` and a Discovery sweep is still non-terminal on the server, the Descoberta UI SHALL reconstitute **by itself** the Acompanhar of that sweep: the mode tab SHALL show a real `sweep_id` prefix (not `Acompanhando #—`) and the progress of that run. The operator SHALL NOT need to click and SHALL NOT need to log out. The red verification-failure banner («Não foi possível verificar a varredura ativa») SHALL NOT be the happy path.

Montar empty + «Acompanhando #—» SHALL NOT remain the stable state of this verification failure while the sweep is still live. The three modes remain Montar / Acompanhar / Decidir; this card SHALL NOT invent a new mode screen.

#### Scenario: Live sweep reconstitutes Acompanhar without a click

- **GIVEN** a non-terminal Discovery sweep exists for the authenticated operator and the screen would otherwise show the red verification banner, empty Montar, and «Acompanhando #—»
- **WHEN** the automatic reconstitution runs
- **THEN** the operator sees Acompanhar of that sweep with a real number and progress
- **AND** they did not click «Tentar novamente»
- **AND** they did not log out

#### Scenario: Retry click is not the happy path

- **GIVEN** the automatic reconstitution succeeded
- **WHEN** the operator looks at Descoberta
- **THEN** «Tentar novamente» is not required to see Acompanhar
- **AND** the red banner «Não foi possível verificar a varredura ativa» is not shown
