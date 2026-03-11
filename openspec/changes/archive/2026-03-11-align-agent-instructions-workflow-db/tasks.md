## 1. PO / Discovery

- [x] 1.1 Capture the need: all agent instructions must align with the workflow DB model
- [x] 1.2 Identify which files still reflect the old runtime model
- [x] 1.3 Define the canonical wording for runtime source / handoff / parallelism / typed work items

## 2. DEV

> Tracking note: `crypto/AGENTS.md` and the change artifacts (`proposal.md`, `design.md`, `specs/agent-instruction-alignment/spec.md`) already reflect the canonical workflow DB / Kanban model discovered in PO. Do not advance DEV before Alan approval; after approval, DEV should only make any remaining delta edits still needed in runtime instruction layers.

- [x] 2.1 Update any remaining runtime instruction files that still conflict with the new workflow DB / Kanban model after approval
- [x] 2.2 Update workspace/global memory/instruction docs that still conflict with the new model after approval
- [x] 2.3 Update any agent-specific instruction files if needed after approval
- [x] 2.4 Validate there are no contradictory rules left across instruction layers after the approved edits

## 3. QA

- [x] 3.1 Review updated instruction files for consistency with the approved workflow-state-db model
- [x] 3.2 Confirm no old file-first runtime assumptions remain in the active project instructions

> Closure note: this change was completed administratively via direct instruction/memory edits already applied across the workspace and agent layers, then closed as superseded-by-direct-edits rather than requiring a separate product-style DEV/QA pass.
