## MODIFIED Requirements

### Requirement: Versioned juízo/execução map file
The shared `.cursor/model-map.yaml` SHALL keep exactly the two bands `juizo` and `execucao` plus `forbid`, not a per-role map. At pin time, the installer SHALL read the **current target consumer file** and preserve each band's top-level `label` and `slug` and every `forbid` entry; values from the product source or Design worktree MUST NOT overwrite them. Each band SHALL additionally contain `codex.label`, `codex.slug`, and `codex.effort`. `juizo.codex` SHALL be `GPT-6 Sol` / `gpt-6-sol` / `high`, and `execucao.codex` SHALL be `GPT-6 Luna` / `gpt-6-luna` / `max` until Alan changes the shared map. The target `forbid` list SHALL continue to include `composer-2.5-fast` and `inherit` while retaining any other current entries. A conflict with a locally changed target map MUST cause visible refusal or an explicit, inspected merge, never silent overwrite. Cursor isolated Task children SHALL continue to pass their top-level band slug as the Task `model` on both spawn paths. Codex children SHALL pass the nested band slug and effort explicitly on each spawn. Missing file, unreadable YAML, missing required key, invalid or forbidden value, or host rejection SHALL cause a visible refusal; no child SHALL silently inherit picker, default effort, or retry with another pair.

#### Scenario: Cursor values remain unchanged
- **WHEN** a Cursor parent spawns a juízo or execução child after the shared map gains Codex fields
- **THEN** it reads `.cursor/model-map.yaml` and requests the top-level `juizo.slug` or `execucao.slug`
- **AND** the Codex fields do not change Cursor's selected model
- **AND** no forbidden slug is used

#### Scenario: Pin preserves locally changed Cursor values
- **WHEN** the target consumer map has top-level Cursor `label`/`slug` values or `forbid` entries different from the product source or Design worktree
- **THEN** the pin preserves those target values and adds only the Codex subblocks
- **AND** a conflicting map change causes visible refusal or an explicitly inspected merge
- **AND** no silent overwrite reports success

#### Scenario: Codex values resolve per request
- **WHEN** a Codex parent spawns a juízo or execução child
- **THEN** it reads the same map immediately before the spawn
- **AND** it explicitly requests the nested `codex.slug` and `codex.effort` of the correct band
- **AND** a later map edit affects the next spawn of that band, not an already running child

#### Scenario: Missing or forbidden map is refused
- **WHEN** the shared map is absent, unreadable, missing a required Cursor or Codex key, or selects a forbidden or unavailable value
- **THEN** the operator-facing chat shows a visible refusal
- **AND** the child MUST NOT run under the parent picker or a default effort
- **AND** the parent MUST NOT retry with `inherit` or another model
