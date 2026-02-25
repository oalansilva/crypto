---
spec: openspec.v1
id: combo-create-template-spec
title: Combo template creation
status: draft
owner: Alan
created_at: 2026-02-11
updated_at: 2026-02-11
---

## ADDED Requirements

### Requirement: Create template from strategy draft
**Description:** The system SHALL provide `ComboService.create_template` that accepts a strategy draft (indicators, entry/exit ideas, stop/risk info) and persists a combo template in `combo_templates`.

#### Scenario: Draft converted to template
Given a valid strategy draft with indicators, entry logic, and exit logic
When `ComboService.create_template` is called
Then a new template row is created and the method returns the saved metadata

### Requirement: Stable mapping and validation
**Description:** The system SHALL map the strategy draft into `template_data` with normalized fields (indicators, entry_logic, exit_logic, stop_loss) and validate required fields before saving.

#### Scenario: Missing required fields
Given a strategy draft missing entry logic
When `ComboService.create_template` is called
Then the method returns a clear error and does not create a template

### Requirement: Error handling for upstream conversion
**Description:** The system SHALL surface conversion errors with explicit messages and avoid raising `seed_template_missing` when the draft is invalid.

#### Scenario: Conversion failure
Given an invalid draft
When the upstream conversion runs
Then the run is marked error with a clear conversion message
