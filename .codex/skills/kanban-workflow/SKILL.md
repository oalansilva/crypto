---
name: kanban_workflow
description: Use when the user wants to operate the standalone Kanban runtime: list projects, inspect cards, move cards between columns, comment on cards, locate a card by number or change_id, or review tasks.md from each project's own root_directory.
---

Use the standalone Kanban as the runtime source of truth.

## Scope

Use this skill when the task involves:
- listing Kanban projects
- choosing the correct project for a workflow action
- finding a card by `card_number`, `change_id`, or title
- creating a project inside the Kanban system
- creating a new card
- reading or updating card workflow state
- editing a card title, description, or images
- reordering cards up/down
- reading `tasks.md` / OpenSpec checklist for a card
- toggling synced checklist items
- commenting on a card
- creating bugs, stories, and tasks
- distinguishing between the `kanban` app and the target project stored inside it
- validating the Kanban UI in the browser with Playwright

Do not use this skill as the primary workflow for:
- editing application code unless the card work explicitly requires implementation
- treating `docs/coordination/*.md` as the live runtime source

## Runtime Rules

- Registry API: `http://127.0.0.1:8004/api/workflow/projects`
- Kanban API base: `http://127.0.0.1:8004/api/workflow`
- Kanban UI: `http://127.0.0.1:5174/`
- Workflow DB + Kanban runtime wins over mirrored markdown docs
- Each project's OpenSpec files live in that project's own `root_directory`
- `kanban` is the orchestration app; `crypto`, `kanban`, or future projects are runtime projects inside it

Read [references/api.md](references/api.md) for concrete request patterns.
Read [references/ui-playwright.md](references/ui-playwright.md) for browser validation flows.

## Default Flow

1. List projects:
   `curl -fsS http://127.0.0.1:8004/api/workflow/projects`

2. Choose the target project.
   - If the user names a project, use it.
   - If the task is about the standalone board system itself, prefer project `kanban`.
   - If the task is about the trading product, prefer project `crypto`.
   - If ambiguous, state which project you are using before mutating anything.

3. List cards for the chosen project:
   `curl -fsS 'http://127.0.0.1:8004/api/workflow/kanban/changes?project_slug=<slug>'`

4. Resolve card references in this order:
   - `card_number`
   - exact `change_id`
   - exact title
   - fuzzy title match only as fallback

5. For checklist / OpenSpec context:
   `curl -fsS 'http://127.0.0.1:8004/api/workflow/kanban/changes/<change_id>/tasks?project_slug=<slug>'`
   - use `path` as the canonical `tasks.md`
   - use `sections` as actionable checklist
   - use `context_sections` as supporting context only

6. For comments:
   `curl -fsS 'http://127.0.0.1:8004/api/workflow/kanban/changes/<change_id>/comments?project_slug=<slug>'`

7. For card changes:
   - update card: `PATCH /api/workflow/projects/<slug>/changes/<change_id>`
   - create comment: `POST /api/workflow/kanban/changes/<change_id>/comments?project_slug=<slug>`
   - create bug/story/task: `POST /api/workflow/projects/<slug>/changes/<change_id>/tasks`
   - create card: `POST /api/workflow/kanban/changes?project_slug=<slug>`
   - create project: `POST /api/workflow/projects`

8. For UI validation:
   - use Playwright against `http://127.0.0.1:5174/`
   - prefer one single run that opens the page, performs the interaction, and saves a screenshot
   - validate both desktop and mobile when the task is visual or responsive

## When To Stop Using This Skill

Use `kanban_workflow` while the task is about runtime workflow operations.

Examples:
- "Find card #66 and move it to DEV" -> stay in this skill
- "Read the tasks.md for change X and summarize blockers" -> stay in this skill
- "Create a bug under card #72" -> stay in this skill

Switch to code implementation workflow when the request becomes product/code work.

Examples:
- "Fix the bug described by card #66 in the crypto frontend"
- "Implement the feature described by card #72"
- "Refactor the backend route used by this card"

In those cases:
- use this skill first to resolve project/card/checklist
- then switch to implementation in the target repo
- return to this skill at the end to update the card, tasks, and comments

## Browser Validation Rules

Use Playwright when:
- the user asks to compare visual behavior
- the task involves responsive/mobile layout
- the task concerns card drawer, search, create/edit flows, comments, or board rendering

Default validation path:
- desktop: open Kanban UI, locate the target card, open drawer, capture screenshot
- mobile: resize to mobile width, repeat the same flow, capture screenshot

Validate at least:
- project selector
- card search by number/id
- drawer open/close
- task/checklist rendering
- comments area
- responsive layout for mobile when relevant

## Guardrails

- Always confirm the target project before moving, reclassifying, or deleting workflow data when multiple projects exist.
- Do not assume `kanban` and `crypto` share the same OpenSpec directory.
- Prefer `card_number` and `change_id` over title matching.
- If Kanban exposes a task toggle, let Kanban sync it back to the project's `tasks.md`.
- If the user asks to move cards between projects, preserve comments and work items together with the card.
- If the task is a UI validation, prefer Playwright evidence over assumptions.
- If the task crosses from workflow operation into product implementation, state the handoff clearly in your own reasoning/output.

## Typical Outcomes

- "Project `crypto`, card `#66`, `change_id=fazer-uma-an-lise...`, current column `Pending`"
- "The canonical checklist is `/root/.openclaw/workspace/crypto/openspec/changes/<change>/tasks.md`"
- "The card belongs in project `kanban`, not `crypto`, because it describes Kanban-system work"
- "UI validated in desktop and mobile with Playwright screenshots"
