# Kanban Runtime API

Use these examples as the default request patterns for the standalone Kanban runtime.

## List Projects

```bash
curl -fsS http://127.0.0.1:8004/api/workflow/projects
```

## List Cards For A Project

```bash
curl -fsS 'http://127.0.0.1:8004/api/workflow/kanban/changes?project_slug=crypto'
curl -fsS 'http://127.0.0.1:8004/api/workflow/kanban/changes?project_slug=kanban'
```

## Read A Card Checklist

```bash
curl -fsS 'http://127.0.0.1:8004/api/workflow/kanban/changes/separar-kanban-do-crypto/tasks?project_slug=crypto'
```

Response notes:
- `path`: canonical `tasks.md` file in the target project's `root_directory`
- `sections`: actionable checklist
- `context_sections`: dependencies / notes / priority context

## Read Card Comments

```bash
curl -fsS 'http://127.0.0.1:8004/api/workflow/kanban/changes/separar-kanban-do-crypto/comments?project_slug=crypto'
```

## Move Or Edit A Card

```bash
curl -fsS -X PATCH \
  -H 'Content-Type: application/json' \
  -d '{"status":"DEV"}' \
  'http://127.0.0.1:8004/api/workflow/projects/crypto/changes/separar-kanban-do-crypto'
```

## Add A Comment

```bash
curl -fsS -X POST \
  -H 'Content-Type: application/json' \
  -d '{"author":"Alan","body":"Handoff para DEV"}' \
  'http://127.0.0.1:8004/api/workflow/kanban/changes/separar-kanban-do-crypto/comments?project_slug=crypto'
```

## Create A Bug Or Task

```bash
curl -fsS -X POST \
  -H 'Content-Type: application/json' \
  -d '{"type":"bug","state":"queued","parent_id":"<story-id>","title":"Broken mobile menu","description":"Logout is not reachable on mobile","priority":0}' \
  'http://127.0.0.1:8004/api/workflow/projects/crypto/changes/separar-kanban-do-crypto/tasks'
```

## Project Selection Rule

Use:
- `project_slug=kanban` for work about the Kanban platform itself
- `project_slug=crypto` for work about the crypto application

If the user is ambiguous, list projects first and state the chosen project before mutating anything.
