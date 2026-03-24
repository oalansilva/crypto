## Why

The current `home` specification only defines the initial page as a lightweight navigation hub, but the product's current direction calls for a stronger first screen that helps the user understand system state and choose the next action quickly.
We need to formalize the initial interface as a daily cockpit so DESIGN, DEV, and QA can align on the same expected experience instead of letting the Home screen evolve outside the spec.

## What Changes

- Expand the initial interface at `/` from a simple shortcut hub into a more complete operational entry screen.
- Preserve fast access to the main workflows, but prioritize a clearer first-step experience with primary actions for the most common daily tasks.
- Add lightweight status and summary blocks on the initial interface so the user can immediately see system health, current context, and what deserves attention.
- Add sections that orient the user around the day-to-day workflow, such as immediate actions, current focus, and recent activity.
- Keep the layout compact and responsive so the same initial interface works on desktop and mobile without losing hierarchy.

## Capabilities

### New Capabilities
- (none)

### Modified Capabilities
- `home`: Expand the Home requirements so the initial interface provides a daily cockpit with prioritized actions, system status, summary cards, and contextual sections in addition to navigation shortcuts.

## Impact

- Frontend: `frontend/src/pages/HomePage.tsx` and related navigation/layout copy will need to match the new initial-interface requirements.
- Design: the initial interface needs an explicit information hierarchy covering hero, primary actions, status/summary blocks, and contextual sections.
- Specs: the existing `home` capability will need a delta spec describing the richer first-screen behavior.
- Backend/API: no new backend surface is required for the proposal phase; the change should prefer existing data already available to the frontend.
