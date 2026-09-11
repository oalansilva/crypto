## ADDED Requirements

### Requirement: Already-promoted discovery favorites expose snapshot numbers on GET

For a favorite whose origin is Descoberta and whose stored snapshot already has Sharpe, negócios, win rate, retorno and Max DD, listing or fetching that favorite SHALL return those values on the keys the Favorites grid already reads, without requiring a new promotion. Combo-saved favorites SHALL keep today's contract.

#### Scenario: GET of #193 fills the grid keys from the existing snapshot

- **WHEN** the grade (or GET de favoritos) loads an already-promoted discovery favorite whose snapshot already has the numbers, including `#193`
- **THEN** Sharpe, Trades, Win%, Return and Max DD are present on the keys the grid already reads
- **AND** the administrator does not promote again

#### Scenario: Combo-saved GET is unchanged

- **WHEN** GET de favoritos returns a favorite saved from Combo (not Descoberta)
- **THEN** the payload contract of that row is the current combo-saved contract
- **AND** this card does not rewrite those keys
