## Why

Alan reported that the `/monitor` screen does not work on mobile and needs a responsive layout. The current implementation keeps the desktop table structure on small screens and forces a minimum width, which breaks the experience on phones.

## What Changes

- Add a mobile-specific card layout for Monitor opportunities.
- Keep the desktop table layout unchanged for larger viewports.
- Adjust mobile spacing and controls inside opportunity details so actions, notes, and timeframe toggles fit on small screens.
- Add focused frontend validation for the mobile Monitor layout.

## Capabilities

### New Capabilities
- `monitor`: Monitor must render opportunities as usable cards on mobile viewports.

### Modified Capabilities
- `monitor`: Opportunity detail controls and footer actions must wrap correctly on small screens.

## Impact

- Frontend Monitor layout and CSS.
- Focused Playwright coverage for the mobile Monitor flow.
- OpenSpec delta for Monitor responsive behavior.
