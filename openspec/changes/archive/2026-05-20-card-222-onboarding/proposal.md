## Why

New beta users can enter Cripto Farol without understanding the first-use path from setup to useful signal reading. Card #222 addresses Bruno's onboarding friction by making the recommended flow visible inside the product instead of relying on manual support.

## What Changes

- Add an in-product onboarding/help experience with a compact first-use guide and a persistent Help route.
- Explain the recommended order: connect/confirm portfolio context, curate Favorites, use Monitor, then inspect chart/trades.
- Add lightweight contextual guidance to Monitor and Favorites so each screen states its role without excessive reading.
- Preserve responsible positioning: Cripto Farol is decision support, not financial recommendation, guaranteed result, leverage encouragement, or guru-style call.
- Keep the experience responsive and aligned with `DESIGN.md` tokens: near-black canvas, elevated surfaces, yellow primary accents, compact radius, readable mobile layout.

## Capabilities

### New Capabilities
- `user-onboarding`: First-use and help-center guidance for the beta user journey.

### Modified Capabilities
- `frontend-ux`: Navigation and contextual screen guidance now include onboarding/help entrypoints.

## Impact

- Frontend route/navigation: add `/help` and a nav entry.
- Shared layout: render a dismissible first-use onboarding prompt for authenticated users.
- Monitor/Favorites UI: add compact help panels.
- E2E coverage: add focused Playwright tests for Help, first-use prompt, and core onboarding copy.
