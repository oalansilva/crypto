## Context

The workflow-state-db change changed the operational model:
- workflow DB is the runtime source of truth
- Kanban is the main consultation/handoff interface
- OpenSpec remains as artifact/documentation
- work items are typed (`change`, `story`, `bug`)
- multiple stories and agents may run in parallel under locks/dependencies

Agent instructions must reflect this or the system will keep carrying old behaviors.

## Goals / Non-Goals

**Goals**
- Align agent instructions with the new workflow model.
- Remove outdated assumptions about `docs/coordination/*.md` being the runtime source.
- Make agent handoff rules explicit through Kanban comments and DB-backed state.
- Clarify when agents may work in parallel and how locks/dependencies should be respected.

**Non-Goals**
- Rebuilding the workflow DB itself.
- Changing Alan's approval/homologation gates.
- Rewriting every generic workspace instruction unrelated to this project.

## Proposed scope

Update the instruction layers in order:
1. Project-level `crypto/AGENTS.md`
2. Memory/workflow rules that still mention old runtime behavior
3. Any agent-specific docs that encode serialized/file-first assumptions

## Review checklist

- Does every agent know Kanban/DB is the runtime source?
- Do agents know OpenSpec is artifact/documentation?
- Do agents know `story` and `bug` semantics?
- Do agents know bugs block story completion?
- Do agents know multiple stories/agents may run in parallel with locks/dependencies?
