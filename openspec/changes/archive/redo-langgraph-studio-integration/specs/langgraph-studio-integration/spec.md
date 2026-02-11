# Spec — LangGraph Studio integration (Strategy Lab)

## ADDED Requirements

### Requirement: Backend MUST persist trace correlation metadata

The backend MUST persist metadata that correlates a Lab `run_id` to the LangGraph execution identity.

#### Scenario: Create run returns run_id and stores trace metadata
- Given the client calls `POST /api/lab/run` with `debug_trace=true`
- When the backend schedules/starts the LangGraph run
- Then the system stores `run_id` plus trace identifiers (`thread_id` and/or `trace_id`) for later retrieval

#### Scenario: Production run does not require tracing
- Given the client calls `POST /api/lab/run` with `debug_trace=false` (or omitted)
- When the backend schedules/starts the LangGraph run
- Then the run still executes successfully
- And `trace.provider` is `none` (or `enabled=false`) in `GET /api/lab/runs/{run_id}`

### Requirement: Runs API MUST expose trace info without breaking UI

The runs endpoint MUST return a stable `trace` object and minimal `events` list.

#### Scenario: GET run returns trace object
- Given an existing `run_id`
- When the client calls `GET /api/lab/runs/{run_id}`
- Then the response includes a `trace` object with:
  - `enabled` (boolean)
  - `provider` (enum: `langgraph_studio|langsmith|none`)
  - optional `thread_id`, `trace_id`, `trace_url`

#### Scenario: Missing trace_url does not break frontend
- Given a run where tracing is disabled or unsupported
- When the frontend loads `/lab/runs/:run_id`
- Then it shows an empty/disabled state for “Abrir no Studio”
- And the rest of the page continues to work

### Requirement: Frontend MUST show Studio link (dev-only) when available

When trace_url is available, the frontend MUST render a button/CTA.

#### Scenario: CTA appears when trace_url exists
- Given `GET /api/lab/runs/{run_id}` returns `trace.trace_url`
- When the frontend renders the run page
- Then it displays a button “Abrir no Studio” that opens `trace_url`

## MODIFIED Requirements

### Requirement: Validation MUST run via OpenSpec CLI

Validation MUST be performed via OpenSpec CLI.

#### Scenario: Validation uses CLI
- When preparing to share the proposal/spec
- Then run `openspec validate redo-langgraph-studio-integration --strict`
- And resolve any errors before sharing the viewer link

## Notes

- This change documents requirements; implementation comes only after Alan sends “implementar”.
