# Δ ui Specification — Lab run chat view

## ADDED Requirements

### Requirement: Chat view for agent conversation

On `/lab/runs/:run_id`, the UI MUST provide a **Chat (simplified)** view that renders the run `trace_events` in a linear, readable format.

The Chat view MUST:
- Render `persona_done` events as chat messages (one bubble per persona output).
- Support filtering messages by persona (`coordinator`, `dev_senior`, `validator`, `system`).
- Hide technical/debug events by default, with a toggle to reveal them.
- Show clear phase markers:
  - `Upstream` when `upstream_started`/`upstream_done` exists.
  - `Execução` (downstream) when the run proceeds to persona execution.
- Keep an **Eventos (debug)** section/tab that shows raw trace events JSON for dev inspection.

#### Scenario:

User opens a run page and can understand the agent conversation without opening LangGraph Studio.

- Given a run that contains `trace_events`, the user sees a chat timeline with persona messages.
- Given `upstream_done.approved=false`, the upstream summary shows missing fields and the question.
- Given no trace events, the UI displays a clear empty state.

### Requirement: Viewer MUST support change artifacts

The `/openspec/*` viewer MUST support loading **change artifacts** under a stable URL prefix:
- `/openspec/changes/<change_id>/proposal`
- `/openspec/changes/<change_id>/design`
- `/openspec/changes/<change_id>/tasks`

(These are backed by read-only API endpoints and map to `openspec/changes/<change_id>/{proposal,design,tasks}.md`.)

#### Scenario:

User opens a change proposal link and the viewer renders the markdown instead of returning 404.

#### Scenario:

User opens the design/tasks links for the same change and the viewer renders the correct markdown files.
