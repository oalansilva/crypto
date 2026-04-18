Use project skills from `.codex/skills` when applicable, especially for architecture review, API contract checks, frontend design and test planning.

## 1. Product and ranking rules

- [ ] 1.1 Define asset eligibility and tiering rules for `primary`, `secondary` and `excluded`
- [ ] 1.2 Define deterministic ranking inputs for the curated dashboard list
- [ ] 1.3 Define taxonomy for freshness states, agreement states and conviction bands

## 2. Backend contract

- [ ] 2.1 Extend `/api/ai/dashboard` unified signal schema with tier or exclusion metadata
- [ ] 2.2 Add `actionability` fields to unified signals with safe null and fallback behavior
- [ ] 2.3 Add per-source trust metadata and final conviction summary to unified signals
- [ ] 2.4 Isolate curation, actionability and trust logic into helper functions with integration coverage

## 3. Frontend experience

- [ ] 3.1 Update the dashboard list to separate primary opportunities from additional coverage
- [ ] 3.2 Render actionability context in signal cards with explicit unavailable states
- [ ] 3.3 Render freshness, agreement and conviction states in source detail and consolidated summary

## 4. Validation and rollout

- [ ] 4.1 Add backend integration tests for curated tiers, hidden assets and trust metadata
- [ ] 4.2 Add frontend or E2E coverage for primary versus additional coverage and actionability fallbacks
- [ ] 4.3 Validate copy and interaction states against trader-facing UX before promotion to QA
