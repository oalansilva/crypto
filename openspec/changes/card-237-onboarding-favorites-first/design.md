## Context

The #222 onboarding release added a Help route, first-use prompt, and contextual screen guidance. After review, the published sequence still starts with wallet setup, but the product direction is Favorites first: users evaluate strategies, select what matters, then monitor those strategies. Binance wallet setup is optional and later.

## Goals / Non-Goals

**Goals:**
- Keep the #222 onboarding structure and styling.
- Correct visible copy and CTA order to Favorites -> selected strategies -> Monitor -> Binance optional.
- Update tests and OpenSpec contracts to match the corrected journey.

**Non-Goals:**
- No new route, modal, backend API, persistence, or onboarding state model.
- No changes to chart, strategy, wallet, or Monitor business logic.
- No edits to archived `card-222-onboarding` artifacts.

## Decisions

- Reuse `OnboardingGuide` rather than creating another onboarding component.
  - Rationale: the issue is copy/order, not a new interaction pattern.
  - Alternative rejected: a separate first-access flow would increase UI surface and test cost.
- Modify main specs through a new delta spec instead of reopening the archived #222 change.
  - Rationale: #222 is already in `Pronto`; this is a new follow-up correction.
- Keep the existing focused Playwright spec and adjust assertions to the corrected text.
  - Rationale: it already covers first-use prompt, Help route, navigation, Monitor, and Favorites guidance.

## Risks / Trade-offs

- Existing screenshots from #222 may show the older journey -> leave them archived as historical evidence and produce new validation output through tests/build.
- Copy-only changes can regress product intent without breaking TypeScript -> keep test assertions tied to the journey order.
