# Single-Operator Operating Playbook (Crypto)

This document replaced the multi-agent operating model for solo execution.

## Scope

Use this playbook when:
- you are implementing directly in this repository (no separate PO/DESIGN/QA agents);
- change tracking is done through OpenSpec and PR history;
- `main` is the production branch; optional feature branches (`feature/*`) merge into `main`.

## Core rules

1. Keep one source of status truth: the OpenSpec change + PR status.
2. Before starting a change, ensure there is no active pending change in OpenSpec.
3. If you stop a change or hit blocker, record:
   - current status
   - blocker
   - what is needed to continue
4. Never leave a step without commit/PR evidence.
5. For approval:
   - keep an PT-BR summary for Alan,
   - add OpenSpec links to the PR summary,
   - ask for explicit "ok" before moving to production lane.

## Handoff template (PR summary)

```text
<DATE> <UTC_TIME>
Status: pass | blocked | needs-review
What changed: ...
Evidence: tests / artifact paths / PR link / screenshots
Next step: ...
```

## DoD for completion

- CI verde no PR aberto.
- Crítica de aceitação validada.
- Homologação registrada.
- Arquivamento executado via OpenSpec.
