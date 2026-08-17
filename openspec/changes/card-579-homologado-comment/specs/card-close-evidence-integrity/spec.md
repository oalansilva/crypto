## ADDED Requirements

### Requirement: Homologation helper runs in the same turn as the Status change
When a card enters `Status=Homologado` (Alan drag on the board or explicit confirmation in chat), the agent SHALL run `scripts/post-card-evidence-comment.sh --transition homologado` in that same turn even if no lote/release action follows. `--commit` SHALL be the card's integration SHA on `develop`, or `origin/develop` HEAD when that SHA is not at hand. Helper failure SHALL block treating the card as evidenced and SHALL block closeout. The canonical comment text SHALL remain `Homologado por Alan na develop.` Lote actions (`release-guard pre`, PR to `main`, archive) MAY run only after the helper in that turn.

#### Scenario: Drag without lote
- **WHEN** Alan drags a card to Homologado (or confirms homologation in chat)
- **AND** there is no lote/release in that turn
- **THEN** the helper still runs in that turn

#### Scenario: Drag then lote
- **WHEN** Alan drags a card to Homologado
- **AND** a lote action follows in the same turn
- **THEN** the helper runs before `release-guard pre` or a PR to `main`

#### Scenario: Helper fails
- **WHEN** the helper exits non-zero (gh failure, fail-closed list, invalid args)
- **THEN** the agent MUST NOT proceed with lote/release closeout
- **AND** MUST NOT treat Homologado as evidenced
