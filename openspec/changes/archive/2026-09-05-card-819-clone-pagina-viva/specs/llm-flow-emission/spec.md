## MODIFIED Requirements

### Requirement: Agent token sheet does not replace DESIGN.md
The repository SHALL contain an operational token sheet at `.agents/skills/impeccable/references/cripto-farol-token-sheet.md` for clone+delta chrome (shell width, CSS variables `--bg-*` / `--accent-primary`, Inter, real nav items, density). Human `DESIGN.md` and its visual YAML MUST remain intact and MUST NOT be rewritten by this sheet. The sheet is not the YAML of `DESIGN.md`. The sheet and chrome tokens MUST NOT replace a clone of the live page; Design MUST point at the live authenticated route (`/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, or another `/` catalog key) **or** at catalogued public HTML (`landing` = `https://criptofarol.com.br/`) when the surface already exists. Absence of the sheet file on disk MUST NOT authorize a gallery, BEFORE/AFTER panel, or chrome-only prototype.

#### Scenario: Clone+delta loads the sheet, not a DESIGN.md rewrite
- **WHEN** Design clones an existing product surface
- **THEN** the agent uses the token sheet plus the live/current screen as the visual base
- **AND** `DESIGN.md` is not overwritten
- **AND** the sheet does not claim to be the visual YAML

#### Scenario: Token sheet does not pass fidelity alone
- **WHEN** a prototype copies sidebar 224px and `--bg-*` from the token sheet but omits the live-route listing landmarks
- **THEN** fidelity MUST fail
- **AND** the missing token-sheet file MUST NOT be treated as permission to skip the route clone

#### Scenario: Public landing clone is not a token-sheet mock
- **WHEN** Design changes visible copy on the public landing
- **THEN** the canonical prototype is the cloned v4 page plus delta, not a token-sheet or ANTES/DEPOIS panel
- **AND** the token sheet MUST NOT replace catalog landmarks for key `landing`
