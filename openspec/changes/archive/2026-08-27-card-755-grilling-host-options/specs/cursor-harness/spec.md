## ADDED Requirements

### Requirement: Parent grill relay presents all host options
`.cursor/skills/alan-workflow/SKILL.md` SHALL include, in the Grill-card section, a line that the **parent** calls the host tool with **all** `options[]` of each closed question and MUST NOT collapse the card to the recommended option. The parent SHALL map the child's listed alternatives 1:1 into `options[]` in the same order, recommended first (Cursor `AskUserQuestion`, Grok `ask_user_question`). The isolated grill child MUST NOT call the host tool. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry, MUST NOT edit `.cursor/process-fsm.yaml`, and MUST NOT name the host tool in `.grok/skills/*` stubs.

#### Scenario: Parent relays every closed-question option
- **WHEN** the grill child returns closed questions with listed options on Grok or Cursor
- **THEN** the parent SHALL call the host tool and re-present all of those options
- **AND** MUST NOT present only the `➡️` / recommended option
- **AND** `alan-workflow` SHALL contain that relay line in the Grill-card section

#### Scenario: No FSM change for host-option relay
- **WHEN** this change is applied
- **THEN** `.cursor/process-fsm.yaml` is unchanged
- **AND** `AGENTS.md` always-on does not grow with this rule
