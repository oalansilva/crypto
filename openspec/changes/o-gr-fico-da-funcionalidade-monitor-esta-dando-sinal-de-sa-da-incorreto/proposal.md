# Proposal

## Change
Fix incorrect EXIT signal shown in the Monitor chart when the BTC monitor view is not backed by a confirmed exit condition.

## Work item type
bug

## Problem statement
The Monitor currently shows an incorrect exit signal in the chart. Based on refinement, this bug must be treated as a mismatch between the Monitor exit rule and the way that rule is represented in the chart UI, not only as a rendering issue.

The visible risk is high because the user can interpret a chart marker as a confirmed sell/exit decision when the underlying rule is stale, belongs to a different candle/timeframe, or is otherwise inconclusive.

## User story
As a Monitor user,
I want the chart and headline signal to show EXIT only when the exit rule is truly confirmed for the current context,
So that I do not act on a false exit signal.

## Value proposition
- Restores trust in the Monitor signal output.
- Prevents false-positive exit interpretation in a trading-sensitive screen.
- Aligns chart marker, summary badge, and strategy context under one resolved state.

## Scope in
- Review and correct the Monitor exit signal semantics for chart presentation.
- Enforce a single resolved signal state for chart marker, badge, and supporting metadata.
- Prevent confirmed EXIT display when data is stale, mismatched by timeframe/candle, loading, or conflicting.
- Expose minimum context for the displayed signal, including timeframe, candle reference, and freshness.
- Define QA-ready acceptance criteria for false-positive and mismatch scenarios.

## Scope out
- New trading strategies or new signal-generation logic unrelated to this mismatch.
- Broad redesign of the Monitor screen outside signal clarity.
- Portfolio, Favorites, Playground, or other modules.
- Design prototype delivery in PO stage.

## Risks and dependencies
- Dependency: DEV must identify the current source of truth for Monitor signal resolution.
- Dependency: DESIGN is required if the UI needs visual treatment for neutral/inconclusive states.
- Risk: if chart marker and badge continue to read different sources, the bug can reappear after partial fixes.
- Risk: lack of explicit candle/timeframe metadata makes QA unable to validate the resolved state objectively.
- Risk: the canonical workflow API currently returns this change in `Canceled`, which conflicts with the claimed PO work item context and must be reconciled operationally.

## Functional framing
The Monitor may display `EXIT confirmed` only when all of the following are true:
1. The exit rule resolves to EXIT from the current source of truth.
2. The resolved state belongs to the currently visible timeframe.
3. The resolved state belongs to the current reference candle/window.
4. The data freshness is valid for display.
5. Badge, marker, and metadata all reflect the same resolved state.

If any of those checks fail, the UI must not present a confirmed EXIT state.

## Options considered
### Option A, strict neutral fallback for any inconsistency
- Show a neutral/inconclusive state whenever signal inputs disagree or are stale.
- Best for trust and QA clarity.
- Recommended.

### Option B, keep EXIT marker but append warning text
- Lower implementation change, but unsafe because the visual still implies action.
- Not recommended.

## Recommendation
Adopt Option A. Inconclusive or mismatched data must degrade to a neutral state instead of displaying EXIT.

## Acceptance criteria
1. Given a Monitor view where the underlying exit rule is not confirmed for the current candle/timeframe, when the chart is rendered, then no confirmed EXIT marker or badge is shown.
2. Given the resolved signal state is EXIT, when the Monitor renders badge, chart marker, and metadata, then all three show the same state and same context.
3. Given the resolved signal belongs to another timeframe or older candle, when the current timeframe/candle is displayed, then EXIT is blocked and a neutral/inconclusive state is shown.
4. Given signal inputs are stale, loading, or conflicting, when the Monitor renders, then the UI does not show confirmed EXIT.
5. Given a visible signal is shown, when the user inspects it, then timeframe, candle reference, and freshness context are visible or otherwise testable in the UI.
6. Given the same response payload is rendered more than once, when the Monitor resolves the signal, then the resulting visual state is deterministic.
7. Given QA reproduces the false-positive BTC scenario from the attached evidence, when validating the Monitor, then the incorrect exit signal is no longer shown.

## 5W2H
- What: Correct false exit indication in Monitor chart.
- Why: Prevent wrong trading interpretation and restore signal trust.
- Who: Monitor users and QA/DEV/DESIGN workflow owners.
- Where: Monitor chart, signal badge, and related metadata.
- When: Immediately in this bug-fix change.
- How: Centralize resolved state, validate current context, and fall back to neutral on inconsistency.
- How much: Small-to-medium scoped bug fix with high product sensitivity.

## Prioritization
- Impact: 9
- Confidence: 7
- Ease: 5
- ICE: 315
