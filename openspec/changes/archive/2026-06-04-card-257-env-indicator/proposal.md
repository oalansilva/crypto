## Why

Users can log into development and production with the same application shell, but the current UI does not provide a persistent environment signal after login. This creates operational risk: validation, data changes, and support checks can happen in the wrong environment without an immediate visual cue.

## What Changes

- Add a persistent authenticated-shell environment indicator that clearly labels `DEV` or `PROD`.
- Resolve the displayed environment from a centralized frontend runtime configuration source instead of hardcoding per page.
- Use distinct visual treatments for development and production while preserving the existing Binance-style dark shell from `DESIGN.md`.
- Keep the indicator visible across protected desktop and mobile navigation.

## Capabilities

### New Capabilities

- `environment-indicator`: Persistent authenticated UI signal that identifies the active runtime environment.

### Modified Capabilities

- None.

## Impact

- Frontend shell/navigation components:
  - `frontend/src/components/Layout.tsx`
  - `frontend/src/components/AppNav.tsx`
- New frontend environment helper/component may be added under `frontend/src/lib/` and `frontend/src/components/`.
- Runtime startup script `start.sh` passes the frontend environment label into static builds.
- Frontend build and UI validation are required.
