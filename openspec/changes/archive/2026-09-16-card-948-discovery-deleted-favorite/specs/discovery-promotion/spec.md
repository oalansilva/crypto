## ADDED Requirements

### Requirement: Promotion follows the live favorite list

Promotion SHALL refuse a duplicate only when the equivalent favorite still exists. If the stored state is `duplicate_favorite` or `already_promoted` but that favorite has been deleted, the administrator MAY confirm **Promover a favorito tier 3**; the system SHALL accept and create a new favorite. The UI and the server SHALL tell the same truth: no ghost refusal «já duplica favorito ativo» for a missing N. Other real blocks (baixa amostra, amostra insuficiente, discarded, live duplicate) SHALL remain. Discarding a grid row SHALL NOT delete a favorite.

#### Scenario: Promote after the duplicate favorite is gone

- **GIVEN** an eligible row whose stored duplicate reference N no longer exists
- **WHEN** the administrator confirms Promover
- **THEN** a new tier 3 favorite is created
- **AND** the response is not a duplicate refusal for N

#### Scenario: Promote after the origin favorite is gone

- **GIVEN** an eligible row stored as `already_promoted` for favorite N
- **AND** favorite N has been deleted
- **WHEN** the administrator confirms Promover
- **THEN** a new tier 3 favorite is created
- **AND** the row is not treated as already that favorite

#### Scenario: Live duplicate still refused

- **GIVEN** an equivalent favorite that still exists
- **WHEN** the administrator tries to promote
- **THEN** promotion remains blocked as a live duplicate
