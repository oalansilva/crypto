# Design — LangGraph Studio integration (Strategy Lab)

## Overview

We want a developer-focused debugging/observability layer for Strategy Lab runs.

Key idea:
- `/lab` triggers a `run_id`
- The LangGraph run executes with a `thread_id` (and/or trace id)
- We persist these fields so that the UI can correlate and provide a link to Studio when available.

## Data flow

1. Frontend `/lab` → `POST /api/lab/run` (+ optional `debug_trace=true`)
2. Backend creates `run_id` and schedules execution
3. Graph state is initialized with `run_id` and (when tracing enabled) a stable `thread_id`
4. During execution, node start/end events append to an events stream for `/lab/runs/:id`
5. UI calls `GET /api/lab/runs/{run_id}` and renders:
   - status
   - candidates/jobs/results
   - trace metadata + optional CTA

## Trace providers

We keep the backend provider-agnostic:
- `none` (default)
- `langgraph_studio` (dev)
- `langsmith` (optional future)

`trace_url` should only be returned when configured/allowed.

## Security

- Studio should NOT be exposed publicly by default.
- `trace_url` is only provided when explicitly enabled in config/env.

## Compatibility

- Tracing is optional. Runs must work without it.
- UI must not break when trace metadata is absent.
