## ADDED Requirements

### Requirement: Stage child finishes in the host mode where it was spawned
Grill, Design-author, Apply, review, and QA children SHALL reach host `completed` in the Cursor host mode that spawned them (modo terminal on this VM, or modo Desktop+SSH Windows to this VM). The parent MUST NOT execute that stage on Desktop as a substitute for a dead or interrupted child. The operator MUST NOT resume an interrupted child as the passing child. Mixing modes to hide a host kill (grill on terminal, Apply finished by the parent on Desktop) MUST NOT count as the stage passing.

#### Scenario: Parent does not take over a dead Apply child on Desktop
- **WHEN** an Apply child on modo Desktop+SSH is interrupted by the host
- **THEN** the parent does not write product or harness patches for that stage in its own transcript
- **AND** the stage remains failed until a new child reaches `completed` in that same mode

#### Scenario: Operator resume of a corpse is refused
- **WHEN** the operator asks to continue an interrupted Task id as the successful Apply/review/QA child
- **THEN** the parent refuses that resume as acceptance
- **AND** it spawns a new isolated child with a self-contained prompt
