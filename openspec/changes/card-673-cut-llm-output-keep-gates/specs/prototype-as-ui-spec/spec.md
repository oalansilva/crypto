## ADDED Requirements

### Requirement: Published Design context does not dump prototype HTML
For `UI impact: affected`, Design and isolated critics SHALL treat the navigable prototype URL, screenshot, and digest as the review surface. Chat and `design.md` MUST NOT include the prototype HTML source. `/opsx:apply` MUST still load the approved prototype files from `frontend/public/prototypes/<change-or-card-slug>/` as the UI specification before any product UI code is written. This requirement does not reopen or weaken the existing apply-loads-prototype rule.

#### Scenario: Design comment links the screen, not the source
- **WHEN** a UI-affected Design handoff is published
- **THEN** the card has a **Protótipo navegável** HTTP URL plus digest/path
- **AND** neither the Gist nor `design.md` contains the prototype HTML source

#### Scenario: Apply still uses the file on disk
- **WHEN** apply proceeds for `UI impact: affected`
- **THEN** the implementer reads the prototype directory from disk
- **AND** absence of that path still blocks apply

### Requirement: Polish patches the prototype file
After critique, prototype edits SHALL be patches against the cloned file. The agent MUST NOT emit a full-file HTML rewrite as the polish/LLM step when a patch can express the delta.

#### Scenario: Polish does not rewrite the whole file in the LLM
- **WHEN** a P0/P1 prototype finding is fixed
- **THEN** the change is a patch to the existing prototype file
- **AND** the Design session MUST NOT paste a complete replacement HTML document into chat as the fix
