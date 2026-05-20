## Why

The published onboarding from #222 still presents wallet setup as the first step, which conflicts with the approved beta journey. New users should start in Favorites, choose strategies, then use Monitor; Binance wallet setup must be optional and later.

## What Changes

- Update onboarding and Help copy to make Favorites the first step.
- Change the onboarding secondary action from Monitor to Favorites.
- Clarify Monitor and Favorites contextual guidance around selected strategies.
- Keep Binance/wallet setup as an optional follow-up, not a prerequisite.
- Update focused onboarding Playwright coverage.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-onboarding`: Correct the recommended beta journey and wallet positioning.
- `frontend-ux`: Align contextual guidance copy on Favorites and Monitor with the corrected journey.

## Impact

- Frontend copy/components only:
  - `frontend/src/components/onboarding/OnboardingGuide.tsx`
  - `frontend/src/pages/HelpPage.tsx`
  - `frontend/src/pages/FavoritesDashboard.tsx`
  - `frontend/src/pages/MonitorPage.tsx`
  - `frontend/tests/e2e/card-222-onboarding.spec.ts`
- No backend, database, or API changes.
