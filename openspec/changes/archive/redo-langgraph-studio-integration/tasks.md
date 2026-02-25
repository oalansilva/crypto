# Tasks — LangGraph Studio integration (Strategy Lab)

## Planning / Spec

1. Ensure artifacts exist for this change:
   - [x] proposal.md
   - [x] specs/langgraph-studio-integration/spec.md
   - [x] design.md
   - [x] tasks.md
2. Run CLI validation:
   - [ ] `openspec validate redo-langgraph-studio-integration --strict`

## Implementation (after Alan says “implementar”)

3. Backend: persist trace metadata (`trace_provider`, `thread_id`, `trace_id`, `trace_url`) per run.
4. Backend: extend `GET /api/lab/runs/{run_id}` to return stable `trace` object + minimal `events` list.
5. Frontend: add section/CTA “Abrir no Studio” on `/lab/runs/:run_id`.
6. Tests:
   - unit test for trace_url exposure rules
   - contract test for run payload includes `trace`
7. Deploy/restart, then Alan manual test and OK.

## Archive (after Alan says “ok”)

8. `openspec archive redo-langgraph-studio-integration`
