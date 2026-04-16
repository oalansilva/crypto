# Tasks

## PO
- [x] Frame the bug as a functional mismatch between Monitor exit logic and chart representation.
- [x] Define scope, risks, recommendation, and testable acceptance criteria.
- [x] Publish PO review package with direct OpenSpec paths.

## DESIGN
- [ ] Create the mandatory Monitor prototype showing confirmed EXIT, neutral/inconclusive, and mismatched-context states.
  - Acceptance: `prototype/prototype.html` or `prototype.html` clearly distinguishes `EXIT confirmed` from neutral/inconclusive states.
- [ ] Define visual language for inconclusive data without implying sell/exit action.
  - Acceptance: stale/loading/conflict states cannot be visually confused with confirmed EXIT.

## DEV
- [x] Centralize Monitor signal resolution into a single source of truth for badge, chart marker, and metadata.
  - Acceptance: badge, marker, and metadata use the exact same resolved state.
- [x] Validate current timeframe and reference candle before displaying confirmed EXIT.
  - Acceptance: EXIT is blocked if the state belongs to another timeframe or an older candle.
- [x] Implement a neutral/inconclusive state for stale, loading, or conflicting inputs.
  - Acceptance: no inconclusive scenario renders a confirmed EXIT state.
- [x] Expose minimum signal context in the UI.
  - Acceptance: timeframe, candle reference, and freshness are visible or otherwise testable.
- [x] Guarantee deterministic rendering for identical payloads.
  - Acceptance: the same input produces the same visual signal state every time.

## QA
- [ ] Reproduce the BTC false-positive exit scenario from the attached evidence.
  - Acceptance: the chart no longer shows confirmed EXIT for the false-positive case.
- [ ] Validate synchronization between badge, chart marker, and metadata.
  - Acceptance: all visible signal elements present the same resolved state and context.
- [ ] Validate timeframe switching behavior.
  - Acceptance: an EXIT from a previous timeframe/candle does not persist incorrectly.
- [ ] Validate stale/loading/conflict behavior.
  - Acceptance: inconclusive cases render as neutral, not EXIT.
- [ ] Attach reproducible evidence, preferably Playwright-based.
  - Acceptance: QA provides reproducible proof for badge, chart, and context alignment.

## Notes
- Expected next owner: DESIGN if visual treatment is needed, otherwise DEV after workflow reconciliation.
- Prototype remains mandatory before approval if the fix changes UI behavior.
- Main rule: uncertainty must never be rendered as confirmed EXIT.
- ICE: 315
