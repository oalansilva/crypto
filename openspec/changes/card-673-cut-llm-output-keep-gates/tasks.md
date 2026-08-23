## 1. Lei de Design (emissão vs avaliação)

- [x] 1.1 Add `.agents/skills/impeccable/references/cripto-farol-token-sheet.md` (shell 224px, `--bg-*`/`--accent-primary`, Inter, nav real, density; pointer to `DESIGN.md`; do not rewrite `DESIGN.md`)
- [x] 1.2 Update `.agents/skills/design-critic/SKILL.md`: avaliação intacta; emissão = bullets P0–P3 + disposition + verdict; snapshot em `.impeccable/critique/`; critics inherit model not transcript; critics MAY write only `.impeccable/critique/**`; empty snapshot ⇒ BLOCKED; clone+delta without HTML dump; polish = patch; UI none keeps N/A
- [x] 1.3 Update `rules.md` Design/Impeccable bullets to the same evaluation/emission split (no Nielsen/persona dump in `design.md`/chat; snapshot linked; apply does not read snapshot)
- [x] 1.4 Update only the Impeccable bullets in `docs/crypto-overlay.md` (pipeline intact; published emission short; snapshot path; both clients). Do not load/rewrite the rest of the overlay

## 2. Apply, colunas e reviewers

- [x] 2.1 Update `.cursor/skills/openspec-apply-change/SKILL.md`: per task load task + matching capability spec + `## Apply contract`; do not read every `contextFiles`; do not read `.impeccable/critique/`; still read prototype files from disk when UI affected
- [x] 2.2 Update `.cursor/skills/alan-workflow/SKILL.md`: one chat per column titled `#id coluna`; refuse mixing Design/Apply/Review/Release; no FSM change; T7 opens the snapshot linked on the card (Gist is not the critique); handoff proxies (design.md words, HTML generated vs copied bytes, spawn count)
- [x] 2.3 Update `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md`: self-contained prompt; no Design/Apply transcript; do not read `.impeccable/critique/`; output findings or `No findings.`; keep two roles; Bugbot optional

## 3. Grok stubs e publish

- [x] 3.1 Extend `scripts/process-fsm/grok_stubs.py` to generate/check `.grok/skills/design-critic` and `.grok/skills/impeccable` pointing at `.agents/skills/<name>/SKILL.md` (body ≤8 lines, MUST Read, map Task inherit → spawn_subagent inherit)
- [x] 3.2 Generate the two extra stubs and keep existing `.cursor/skills` stubs as-is
- [x] 3.3 Update `publish-openspec-card-artifacts.sh` with `--snapshot-path` (separate comment block, never upload `.impeccable/critique/` to the Gist) and a Proxies block

## 4. Specs e testes

- [x] 4.1 Apply spec deltas: `llm-flow-emission` (new), `impeccable-design-gate`, `cursor-harness`, `process-harness`, `cursor-code-review`, `prototype-as-ui-spec`
- [x] 4.2 Add/adjust pytest in `scripts/process-fsm` for extra Grok stubs (missing/stale fails; pointer is `.agents/skills/`; body ≤8; no runbook copy)
- [x] 4.3 Assert apply skill no longer says to read every `contextFiles`; assert design-critic forbids Nielsen table / full Brief in `design.md`; `pytest scripts/process-fsm -q`
- [x] 4.4 `openspec validate --change card-673-cut-llm-output-keep-gates`

## 5. Verify

- [x] 5.1 UI impact: none — no `frontend/src/` or product `backend/` edits
- [x] 5.2 Comment on #673 after apply: change + snapshot N/A for this card + proxies of the apply itself + reminder that T7 stays Alan
- [x] 5.3 Homologation note (not apply): next UI-affected Design must show short `design.md`, non-empty `.impeccable/critique/` linked on the card, and apply/review not reading the snapshot — on Cursor and Grok
