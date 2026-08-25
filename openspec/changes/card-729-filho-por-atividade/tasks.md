## 1. Runbook e skills

- [ ] 1.1 Update `.cursor/skills/alan-workflow/SKILL.md`: replace “Um chat por coluna” / “abra `#id coluna`” / “pedir chat novo com o título da coluna” with one chat `#<id>` (Em Refinamento → Done técnico), parent orchestrator, activity children + waves (incl. QA checks; T14 on parent), same-chat refusal, no FSM change; keep T7 snapshot + proxies; keep global Task inherit; **require isolated spawn (no transcript) for the closed list**
- [ ] 1.2 Update `.agents/skills/design-critic/SKILL.md`: Design author = isolated child; parent does not write `design.md`/prototype except **only** `## Design Critique` after A/B; parent spawns A/B after artifacts; T5 parent-only; P0/P1 → re-spawn author (parent does not polish); drop “Um chat por coluna” / “outro chat `#id Apply`”
- [ ] 1.3 Update `.cursor/skills/grill-card/SKILL.md`: bind = Status of issue N is Em Refinamento + N in prompt matching parent `#<id>`; refuse if missing/mismatch; do **not** require `card-<id>-*` or treat unbound git as a blocker; parent relays; child writes body of N + T1-wait comment; child does not T1
- [ ] 1.4 Update `.cursor/skills/openspec-apply-change/SKILL.md`: one Em desenvolvimento child with per-task sliced reads inside that child; parent does not implement; child MUST NOT `process_event`, commit/push, or spawn reviewers; returns status to parent for git + `pedir_review`

## 2. Docs

- [ ] 2.1 Update `docs/backlog-operating-model.md` gate-de-design: chat `#id` + filhos de atividade, not “um chat por coluna”; T5 remains parent `process_event submeter_design` (not the Design-author child)
- [ ] 2.2 Add `docs/decision-log.md` entry 2026-08-25 card #729 (filho por atividade; D8 do #673 sucessor). Keep the #673 entry historical

## 3. Specs e testes

- [ ] 3.1 Apply spec deltas: `llm-flow-emission` (including Purpose line: chat por card + filhos, not “um chat por coluna”), `cursor-harness`, `grill-card`
- [ ] 3.2 In `scripts/process-fsm` tests only (not `process-fsm.yaml`): assert `alan-workflow` / `design-critic` do not instruct “abra `#id Apply`”, “pedir chat novo com o título da coluna”, or “Um chat por coluna”; `grill-card` does not require `card-<id>-*` as bind; update `test_grill_card.py` if it still treats `bound_card` as a branch requirement; `pytest scripts/process-fsm -q`
- [ ] 3.3 `openspec validate --change card-729-filho-por-atividade`

## 4. Verify

- [ ] 4.1 UI impact: none — no `frontend/src/` or product `backend/` edits
- [ ] 4.2 Comment on #729 after apply: change + snapshot N/A + proxies + T7 continua Alan
- [ ] 4.3 Homologation note (not apply): next card in `#<id>` must spawn activity children and MUST NOT ask for a new column chat — Cursor and Grok
