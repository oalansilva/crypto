## Why

Card #100 reports that the Monitor can initialize with `monitor-theme--black` when the product contract expects `dark-green` as the default. This breaks visual consistency and the existing Playwright coverage for Monitor theme preference.

## What Changes

- Ensure the Monitor uses `dark-green` whenever the global monitor preference has no valid theme.
- Preserve explicit user choice when `__global__.theme` is set to `black`.
- Keep the visual label and toggle behavior unchanged.
- Validate with the existing `monitor-theme.spec.ts` E2E tests.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `monitor-theme-preference`: clarify that missing or invalid global theme preference resolves to `dark-green`.
- `frontend-ux`: confirm the Monitor root renders with the dark-green theme by default.

## Impact

- Frontend Monitor preference normalization and initial render behavior.
- Existing Playwright Monitor theme tests.
