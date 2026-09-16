## ADDED Requirements

### Requirement: New draft Time Frames default to 1 day only

A new Discovery draft in modo Montar (first opening **or** «Novo rascunho») SHALL mark Time Frames **1 dia** and SHALL leave **4 horas** unmarked. The operator MAY still mark 4 horas afterwards. Direction, period, and ranking SHALL remain as they are today. Start SHALL remain blocked while Templates or Symbols are empty; the existing «Falta fazer» copy SHALL name the missing axes and SHALL NOT start an empty sweep.

#### Scenario: First opening marks only 1 day

- **WHEN** the administrator opens `/combo/discovery` on a new draft
- **THEN** Time Frames has **1 dia** marked and **4 horas** unmarked
- **AND** «Falta fazer» is visible because Templates and Symbols are empty
- **AND** start does not create a sweep

#### Scenario: Novo rascunho applies the same Time Frames default

- **WHEN** the administrator activates «Novo rascunho»
- **THEN** Time Frames has only **1 dia** marked
- **AND** **4 horas** is unmarked and remains markable

### Requirement: Restore does not overlay new-draft defaults

Reopening a saved sweep SHALL restore the recorded template, symbol, and timeframe axes. The new-draft defaults SHALL NOT be applied on top of that restored selection. If the saved sweep has an empty timeframes axis, the client SHALL NOT fall back to 4 hours + 1 day.

#### Scenario: Saved sweep keeps its marks

- **WHEN** the administrator reopens a saved sweep whose snapshot has templates, symbols, and timeframes recorded
- **THEN** the screen shows those recorded marks
- **AND** it does not clear templates/symbols or force Time Frames to only 1 day

#### Scenario: Saved sweep without timeframe does not invent 4h+1d

- **WHEN** the administrator reopens a saved sweep whose snapshot has no timeframes
- **THEN** Time Frames does not fall back to 4 hours + 1 day
