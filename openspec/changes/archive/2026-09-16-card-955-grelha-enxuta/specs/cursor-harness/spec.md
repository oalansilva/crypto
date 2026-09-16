## MODIFIED Requirements

### Requirement: Card first; OpenSpec is the complete refinement for Dev
The GitHub issue MAY originate the work. The grill SHALL remain the place the story is decided (who suffers, what entra/não entra). OpenSpec artifacts and the published Gist SHALL be a **superset** of the issue: history copied from the grilled body plus the *como* (mechanism, vocabulary, risks, tasks, observable harness behavior). `proposal.md` MUST contain `## Problema`, `## História`, and `## Entra` (or an observable equivalent) copied from the issue and MUST NOT invent a new story. `/opsx:apply` SHALL use OpenSpec/Gist as the implementation contract, not the issue body as a parallel spec. `G_design` SHALL continue to require the OpenSpec package files plus the clone gate plus a Gist comment on the card.

#### Scenario: Issue richer than OpenSpec
- **WHEN** the GitHub issue body contains *como* / mechanism decisions missing from `design.md` / specs
- **THEN** the agent SHALL merge those mechanism decisions into OpenSpec, republish the same Gist, and MUST NOT move to `Aprovação de Design` until the Gist is the superset
- **AND** MUST copy Problema, História, and Entra into `proposal.md` from the grilled issue (MUST NOT invent)

#### Scenario: Dev implements
- **WHEN** `Status=Pronto para Dev` and `/opsx:apply` runs
- **THEN** the agent SHALL follow `openspec/changes/<change>/` and the published Gist
- **AND** SHALL NOT treat a richer issue body as authorization to skip a task missing from `tasks.md`

#### Scenario: Gist is the superset
- **WHEN** a Design package is published
- **THEN** the Gist SHALL contain proposal, design, tasks, and specs
- **AND** `proposal.md` SHALL contain `## Problema`, `## História`, and `## Entra` copied from the GitHub issue
- **AND** a `proposal.md` without those headings SHALL fail the golden
