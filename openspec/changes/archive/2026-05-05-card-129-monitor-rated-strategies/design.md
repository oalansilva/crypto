## Context

Card #129 asks the Monitor to show only strategies marked with 1, 2, or 3 stars. The current frontend initializes the internal tier filter as `all`; for common users the backend rewrites `all` to `1,2,3`, but admins keep `all`, so Alan can see unstarred strategies.

## Decision

Use a new frontend tier mode named `rated` as the Monitor default. It maps to API query `tier=1,2,3` and is independent from signal section, so HOLD rows remain visible when starred.

## UI/UX

No layout or visual control changes. The existing Monitor surface remains dense and operational, following `DESIGN.md` tokens/components already used by `MonitorStatusTab`. The star dropdown still filters among the rated results.

## Testing

Add focused Playwright coverage in the existing Monitor E2E file:
- default request uses `tier=1,2,3`;
- unstarred opportunity returned by a mock backend is not visible;
- starred HOLD opportunity remains visible.
