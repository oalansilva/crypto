## 1. Universal configuration model

- [x] 1.1 Add frontend helpers that derive trader-readable indicator and risk summaries from the canonical manifest.
- [x] 1.2 Preserve universal rendering for all current and future manifest indicator types without strategy-specific branches.

## 2. Chart UX

- [x] 2.1 Show indicator configuration prominently in the chart header with semantic colors and responsive wrapping.
- [x] 2.2 Keep detailed indicator cards visible with configuration and selected-candle values, including explicit unavailable state.
- [x] 2.3 Apply DESIGN.md tokens and validate desktop/mobile behavior.

## 3. Validation and delivery

- [x] 3.1 Add focused frontend/Playwright coverage for moving averages and generic indicator configurations.
- [x] 3.2 Run build, focused tests and OpenSpec validation.
- [x] 3.3 Run Codex review and `/opsx:verify` equivalent.
- [x] 3.4 Integrate into `develop`, restart DEV, validate served UI and move card to Done.

Use project skills in `.codex/skills` when applicable for frontend, testing, debugging and OpenSpec verification.
