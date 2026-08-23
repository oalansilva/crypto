## 1. Skills (porta + primitivo)

- [x] 1.1 Vendor `.cursor/skills/grilling/SKILL.md` from mattpocock/skills `skills/productivity/grilling/SKILL.md` (regular file, no `agents/openai.yaml`, no symlink)
- [x] 1.2 Add `.cursor/skills/grill-card/SKILL.md`: frontmatter `disable-model-invocation: false`; bound_card + Status=Em Refinamento; load grilling; DoD body; canonical T1 comment; deny Status move, CONTEXT.md, docs/adr, /opsx:*
- [x] 1.3 Confirm `.cursor/skills/` has no `grill-with-docs` entry skill

## 2. Runbook

- [x] 2.1 Update `.cursor/skills/alan-workflow/SKILL.md`: Em Refinamento = intake + grill-card; T1 Alan-only; Design synthesizes grilled issue; no to-spec / grill-driven schema
- [x] 2.2 Update `.cursor/skills/github-project-board/SKILL.md` Em Refinamento text: grill on issue, do not drag T1
- [x] 2.3 Update `.cursor/skills/openspec-new-change/SKILL.md` and `openspec-ff-change/SKILL.md`: if bound issue has DoD sections, use as briefing; do not re-interview; do not invoke grill-card to write proposal.md; if DoD incomplete, do not ff, comment gaps, stay Design; `/opsx:explore` only for technical holes
- [x] 2.4 `alan-workflow`: grill when Alan asks or Em Refinamento body lacks DoD; not every T0; not in Todo/Design

## 3. EFSM + OpenSpec config

- [x] 3.1 Update `.cursor/process-fsm.yaml` `context_file` for Em Refinamento, Todo, Design per D5; keep exact Todo substring `Próximo evento = iniciar_design. Não apply. Não /opsx:new ainda.`; do not change states/T0/T1; keep Em Refinamento `enabled_tools: [issue_edit, comment]` (no `write_openspec`)
- [x] 3.2 Update `openspec/config.yaml` proposal/design rules: vocab from issue; no grill skill while generating proposal.md
- [x] 3.3 Apply spec deltas: `grill-card`, `cursor-harness`, `process-fsm`

## 4. Tests

- [x] 4.1 `pytest scripts/process-fsm -q` (paging Todo stub + ≤20 lines)
- [x] 4.2 Assert `grill-card/SKILL.md` and `grilling/SKILL.md` exist, not git symlink; grill-card text contains CONTEXT.md and T1 prohibitions; assert those skills are not added under Hermes or `~/.codex/skills/`
- [x] 4.3 `openspec validate --change card-667-grill-card`

## 5. Verify

- [x] 5.1 UI impact: none — no `frontend/src/` or product `backend/` edits
- [x] 5.2 Comment on #667 after apply: skills paths + reminder Alan still owns T1
- [x] 5.3 Dry-run note: next product T0 may use grill-card; this card does not require a second issue to merge
