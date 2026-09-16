## ADDED Requirements

### Requirement: Grid tells the truth after a favorite is deleted

On `/combo/discovery`, Decidir and Acompanhar (when the same row is still visible) SHALL show the same current classification. After the referenced favorite has been deleted, an eligible row that used to show **Já existe** / **Equivale ao favorito ativo N** or **Favorito tier 3** SHALL show **Promover** (if the rest of the row still allows it). That row SHALL NOT show **Já existe**, SHALL NOT show **Equivale ao favorito ativo N**, SHALL NOT show **Favorito tier 3**, and SHALL NOT show a note that it used to be a favorite. The row SHALL remain on the sweep; deleting the favorite SHALL NOT hide it. A row whose equivalent favorite still exists SHALL keep **Já existe** / **Equivale ao favorito ativo N**. **Excluir** on the grid still discards only that sweep result and SHALL NOT delete a favorite.

#### Scenario: Orphan Já existe row returns to Promover

- **GIVEN** a completed sweep whose row showed **Já existe** / **Equivale ao favorito ativo N**
- **AND** favorite N has been deleted
- **WHEN** the administrator opens Decidir on that sweep
- **THEN** the row shows **Promover** if otherwise eligible
- **AND** it does not show **Já existe**
- **AND** it does not show **Equivale ao favorito ativo N**
- **AND** it does not show a historical-favorite note
- **AND** the row is still on the sweep

#### Scenario: Orphan Favorito tier 3 row returns to Promover

- **GIVEN** a sweep row that showed **Favorito tier 3** because it created favorite N
- **AND** favorite N has been deleted
- **WHEN** the administrator opens that sweep
- **THEN** the row does not show **Favorito tier 3**
- **AND** it shows **Promover** if otherwise eligible

#### Scenario: Acompanhar matches Decidir

- **GIVEN** the same orphan or live-duplicate row is still visible on Acompanhar
- **WHEN** the administrator opens Acompanhar
- **THEN** that surface shows the same Promover / Já existe / Favorito tier 3 truth as Decidir

#### Scenario: Live favorite is not a regression

- **GIVEN** a favorite that still exists
- **WHEN** an equivalent candidate is shown
- **THEN** the row still shows **Já existe** and **Equivale ao favorito ativo N**
