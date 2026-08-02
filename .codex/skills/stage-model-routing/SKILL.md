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

1. Validate the primary Sol pin and all Luna profiles statically through TOML parsing, exact agent/model/effort/thread assertions, the declared sandbox intent, this skill's validator, contract tests and OpenSpec validation. Read the official Codex cache at `${CODEX_HOME:-$HOME/.codex}/models_cache.json` and prove that Sol supports `high` while Luna supports `max` in `supported_reasoning_levels`.
2. Use an independent read-only Codex review available to the bootstrap task for the exact diff. It must not edit the reviewed content.
3. Do not pre-spawn the implementer, reviewer or release manager for runtime proof. The release manager must never be spawned without an explicitly authorized release.
4. Do not change AppArmor, sysctl, bubblewrap, user namespaces, sandbox launchers or any other host/server security configuration to make a diagnostic run.
5. A failed pre-activation smoke diagnostic is not acceptance evidence and does not invalidate the reproducible static checks.

After the profiles are versioned and loaded by a new task, the exception ends. Enforce the exact Luna profile and runtime checks when each lane is naturally used; do not apply bootstrap evidence to a later lane. A runtime sandbox broader than the requested role is observable residual risk, not a failure by itself; it activates the behavioral-containment checks below and never authorizes host-security changes.

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

## Behavioral containment (option 2)

Every Luna lane uses behavioral containment regardless of the effective sandbox.
Sandbox policy type and permission profile type remain observable and must be
reported, but equality with `workspace-write` or `read-only` is not a gate. A
broader policy such as `danger-full-access` may proceed only when the exact
agent/model/effort/`fork_turns="none"` contract is satisfied and the bounded
before/after audit passes. A narrower runtime policy is accepted as additional
protection; it does not remove these checks. This contract does not provide
operating-system isolation, and every handoff must disclose that residual risk.

Before spawn, the orchestrator records the relevant state and sends a
self-contained packet with:

- exact ownership (paths, repositories, worktrees and package/base/head);
- allowed commands/actions and explicit external-system limits;
- prohibited mutations and the digest/inventory used for comparison.

`fork_turns="none"` is separate control-plane evidence. The orchestrator MUST
record the explicit spawn request and the native spawn result (or equivalent
public control metadata) proving that value before accepting a lane. Missing,
ambiguous, inherited, or different fork control evidence blocks the stage. The
local `scripts/inspect-agent-runtime.sh` intentionally allowlists only five
runtime fields—`agent_type`, `model`, `effort`, `sandbox_policy_type`, and
`permission_profile_type`—and does not inspect or prove `fork_turns`; it MUST
never be cited as evidence for that control. A new thread id is not proof of
`fork_turns="none"`.

After return, the orchestrator independently inspects the actual state, compares
the before/after inventory and digest, audits tracked and relevant untracked
files, and checks external actions. Any unclassified mutation or action outside
the packet blocks the stage. The Luna report is an assertion, never the proof.

| Lane | Acceptance evidence | Residual-risk disclosure |
| --- | --- | --- |
| Implementer | Only assigned paths changed; base/head, status, diff and relevant untracked digests are accounted for; no unapproved commit, push, PR, board or service action. | A broad sandbox can technically reach other paths or systems; the packet and independent audit are the containment boundary. |
| Reviewer | New thread, exact diff, explicit `fork_turns="none"` spawn control evidence, and identical before/after state for the mandatory inventory below; no mutation observed within the required inventory. Any difference rejects the review and the reviewer does not repair it. | Behavioral read-only cannot prove that no external read/network occurred; broadened sandbox is not OS isolation. |
| Release manager | Exact Homologado package, repositories/worktrees/stashes and authorized external checklist reconcile; no code or out-of-package mutation. | `danger-full-access` is expected for authorized release actions but still offers no OS-level isolation. |

### Reviewer mandatory inventory

For **every** repository and worktree named in a reviewer packet, the
orchestrator captures the same bounded inventory before and after review. Git
reads use `GIT_OPTIONAL_LOCKS=0` where applicable. The minimum inventory is:

- `git worktree list` plus each worktree's HEAD and branch;
- refs/branches/tags (`git for-each-ref`) and the exact reviewed base/head;
- `git stash list` and the repository's config and hooks (including configured
  hook paths and files under the explicitly inventoried roots);
- tracked/untracked and ignored files within every explicitly inventoried root
  (`git status --short --untracked-files=all --ignored` and equivalent bounded
  file listing);
- content and link digests relevant to the packet, including the exact diff
  and any declared untracked artifacts.

Acceptance means **no mutation observed within the required inventory**. It does
not mean zero global mutation: other host paths/repos, reads or network activity,
and external actions without an auditable API remain technically unobservable
and MUST be listed as residual risk. Ignored roots explicitly excluded for cost
must also be named in that residual-risk record. Any observed difference or
undeclared exclusion blocks the review; the reviewer does not restore state.

## Accept post-activation runtime routing

Treat every Luna report as a claim. Collect runtime evidence only when a post-activation Luna lane is naturally used; never create a lane only to collect metadata.

1. Inspect public spawn/details metadata first.
2. Require the exact agent type, `gpt-5.6-luna`, `max`, and the separately recorded spawn control `fork_turns="none"`, plus observable sandbox policy type and permission profile type. The policy values must be observable, but a broader value does not block solely by being broader than the role request.
3. When public details omit one of the five allowlisted runtime fields—agent type, model, effort, sandbox policy type or permission profile type—and a local rollout is available, resolve `scripts/inspect-agent-runtime.sh` relative to this skill and run it with the exact native thread id. If public details omit any required field—agent type, model, effort, sandbox policy type or permission profile type—the same inspector fallback applies; it cannot fill a missing `fork_turns` control record, so missing spawn evidence blocks.
4. Require public and local values to agree when both expose the same field.
5. Block on missing, stale, conflicting, unavailable, ambiguous or unobservable agent/model/effort/fork-control/security evidence, or on a failed behavioral audit. Do not fall back. A broader sandbox is recorded as residual risk and evaluated by the lane's before/after criteria.

Public handoffs may report the safe five runtime fields plus the separate control-plane result `fork_turns="none"`. Never publish thread ids, rollout paths, prompts, messages, environment values, tokens or arbitrary runtime payloads.

## Stage contracts

### Development

Spawn `crypto_luna_implementer` with `fork_turns="none"`. Give it the approved OpenSpec and owned files. The orchestrator inspects the actual diff and reruns focused verification before moving to Code Review.

### Code Review

After activation, spawn a new `crypto_luna_reviewer` with an explicit,
recorded `fork_turns="none"` request/result. Require an observed sandbox policy
and permission profile, but enforce read-only behavior through the packet and
the mandatory inventory's before/after evidence rather than a sandbox-equality
gate. Give it the exact diff and evidence. It returns severity-ordered findings
and never edits. A blocking finding or any observed difference in the required
inventory returns code to the implementer, followed by another new reviewer.
For the bootstrap change only, use the independent read-only Codex review
defined above; this exception does not carry into tasks started after
activation.

### QA

The Sol High primary session inspects the reviewed SHA, runs `/opsx:verify`, validates required terminal checks and rejects code edits in QA. Code fixes follow Luna implementer -> new Luna reviewer -> Sol QA. OpenSpec-only fixes remain with Sol. Approved design changes return to Design and Alan approval.

### Release

Spawn `crypto_luna_release_manager` with `fork_turns="none"` only after Alan's explicit release request. Require the observed release sandbox/permission profile and an exact homologated package; `danger-full-access` alone is not a blocker, while package/audit violations are. Only this authorized release lane may run OpenSpec sync/archive. The manager does not edit code. A code blocker stops release; cards already Done/Homologado keep their Status while technical revalidation repeats.

## Handoff

For bootstrap, record the static checks and independent read-only review without claiming runtime lane evidence. For a naturally used post-activation Luna lane, record stage, exact safe routing fields, the separately controlled `fork_turns="none"` spawn evidence, effective sandbox/permission metadata, the mandatory before/after inventory and digests, diff/SHA or package, residual risk, executed checks, result and next gate. Do not call a blocked lane complete.
