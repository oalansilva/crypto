## Why

The Monitor can show unstarred strategies for admin/operator users because the screen loads opportunities with `tier=all`. Alan expects the Monitor to show only strategies marked with 1, 2, or 3 stars, including strategies currently in HOLD.

## What Changes

- Make the Monitor default opportunity request target only rated strategies (`tier=1,2,3`).
- Keep HOLD, WAIT, and EXIT sections based on the same rated-strategy rule.
- Add a UI-side guard so unstarred opportunities are not shown if the backend returns them.
- Add focused E2E coverage for the Monitor request and visible filtering.

## Capabilities

### New Capabilities

### Modified Capabilities
- `monitor`: Monitor visible opportunities are limited to rated strategies by default.

## Impact

- Frontend Monitor query construction and visible opportunity filtering.
- Existing Monitor Playwright coverage.
