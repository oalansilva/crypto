---
name: stage-model-routing
description: Route Cripto Farol delivery stages to fixed Codex models and project-scoped agents. Use whenever a card enters Design, Em desenvolvimento, Code Review, QA, rework, or an explicitly authorized release; also use for OpenSpec new/ff/apply/verify and release-only sync/archive ownership. Enforces static bootstrap acceptance, post-activation runtime evidence, fresh context, and fail-closed Sol High/Luna Max routing.
---

# Stage Model Routing

Run one fixed Codex workflow. Do not route by complexity and do not use this skill outside Codex.

## Fixed map

| Stage or operation | Required executor |
| --- | --- |
| Design, `/opsx:new`, `/opsx:ff`, explore/continue, artifact publication | primary `gpt-5.6-sol` / `high` |
| `Em desenvolvimento`, `/opsx:apply`, implementation, focused tests | `crypto_luna_implementer` |
| `Code Review` | new `crypto_luna_reviewer` |
| `QA`, `/opsx:verify`, acceptance of evidence | primary `gpt-5.6-sol` / `high` |
| sync/archive inside an explicitly authorized release | new `crypto_luna_release_manager` |

Never use Terra, a built-in agent, another effort, or a similarly named profile as fallback.

## Preflight

1. Read `AGENTS.md`, `rules.md`, card Status and the active OpenSpec context.
2. Confirm the stage gate:
   - implementation: Alan already moved the card to `Pronto para Dev`, then the orchestrator moved it to `Em desenvolvimento`;
   - review: card is in `Code Review` and the exact diff plus focused evidence are ready;
   - release, sync or archive: Alan explicitly requested this release and every included card is `Homologado`.
3. After activation, confirm the exact required custom agent is exposed only when its real stage is reached.
4. Spawn a Luna lane only for that real post-activation stage, with the exact `agent_type` and `fork_turns="none"`. Never attach a per-spawn model or reasoning override; the TOML profile owns the pin.

## Bootstrap exception

The change that installs these profiles uses static bootstrap acceptance because later tasks must reload the versioned configuration before the profiles can be enforced.

1. Validate the primary Sol pin and all Luna profiles statically through TOML parsing, exact model/effort/sandbox assertions, this skill's validator, contract tests and OpenSpec validation. Read the official Codex cache at `${CODEX_HOME:-$HOME/.codex}/models_cache.json` and prove that Sol supports `high` while Luna supports `max` in `supported_reasoning_levels`.
2. Use an independent read-only Codex review available to the bootstrap task for the exact diff. It must not edit the reviewed content.
3. Do not pre-spawn the implementer, reviewer or release manager for runtime proof. The release manager must never be spawned without an explicitly authorized release.
4. Do not change AppArmor, sysctl, bubblewrap, user namespaces, sandbox launchers or any other host/server security configuration to make a diagnostic run.
5. A failed pre-activation smoke diagnostic is not acceptance evidence and does not invalidate the reproducible static checks.

After the profiles are versioned and loaded by a new task, the exception ends. Enforce the exact Luna profile and runtime checks when each lane is naturally used; do not apply bootstrap evidence to a later lane.

## Self-contained Luna packet

Every Luna prompt must include all sections. Do not rely on inherited conversation history.

```text
CARD AND GATE
Card/change, Status, approval or release authorization evidence.

WORKSPACE
Repository, branch, worktree and exact base/head when applicable.

OBJECTIVE
Observable outcome and why it matters.

FILES AND OWNERSHIP
Exact files/modules owned. Preserve concurrent and unrelated edits.

INTERFACES
Signatures, schemas, commands and behavior that must remain compatible.

CONSTRAINTS
AGENTS/rules/OpenSpec, safety boundaries, excluded scope and settled decisions.

INPUT EVIDENCE
Relevant artifacts, diff/SHA, tests and handoff evidence.

VERIFICATION
Exact commands and concrete success conditions.

RETURN
Status, file-by-file changes/findings, commands with bounded evidence,
judgment calls and remaining gaps.
```

## Accept post-activation runtime routing

Treat every Luna report as a claim. Collect runtime evidence only when a post-activation Luna lane is naturally used; never create a lane only to collect metadata.

1. Inspect public spawn/details metadata first.
2. Require the exact agent type, `gpt-5.6-luna`, `max`, sandbox policy type and permission profile type.
3. When public details omit any required field—agent type, model, effort, sandbox policy type or permission profile type—and a local rollout is available, resolve `scripts/inspect-agent-runtime.sh` relative to this skill and run it with the exact native thread id.
4. Require public and local values to agree when both expose the same field.
5. Block on missing, stale, conflicting, unavailable, ambiguous or unobservable evidence. Do not fall back.

Public handoffs may report only agent type, model, effort, sandbox policy type and permission profile type. Never publish thread ids, rollout paths, prompts, messages, environment values, tokens or arbitrary runtime payloads.

## Stage contracts

### Development

Spawn `crypto_luna_implementer` with `fork_turns="none"`. Give it the approved OpenSpec and owned files. The orchestrator inspects the actual diff and reruns focused verification before moving to Code Review.

### Code Review

After activation, spawn a new `crypto_luna_reviewer` with `fork_turns="none"`. Require observed `read-only` sandbox. Give it the exact diff and evidence. It returns severity-ordered findings and never edits. A blocking finding returns code to the implementer, followed by another new reviewer. For the bootstrap change only, use the independent read-only Codex review defined above; this exception does not carry into tasks started after activation.

### QA

The Sol High primary session inspects the reviewed SHA, runs `/opsx:verify`, validates required terminal checks and rejects code edits in QA. Code fixes follow Luna implementer -> new Luna reviewer -> Sol QA. OpenSpec-only fixes remain with Sol. Approved design changes return to Design and Alan approval.

### Release

Spawn `crypto_luna_release_manager` with `fork_turns="none"` only after Alan's explicit release request. Require the observed release sandbox/permission profile and an exact homologated package. Only this authorized release lane may run OpenSpec sync/archive. The manager does not edit code. A code blocker stops release; cards already Done/Homologado keep their Status while technical revalidation repeats.

## Handoff

For bootstrap, record the static checks and independent read-only review without claiming runtime lane evidence. For a naturally used post-activation Luna lane, record stage, exact safe routing fields, diff/SHA or package, executed checks, result and next gate. Do not call a blocked lane complete.
