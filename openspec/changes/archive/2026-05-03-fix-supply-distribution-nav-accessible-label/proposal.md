## Why

Card #101 reports the Supply Distribution E2E flow cannot find the navigation link when the test uses the ASCII accessible name `Distribuicao`. The visible label can remain accented, but the role-based selector needs a stable ASCII accessible label.

## What Changes

- Keep the visible menu label as `Distribuição`.
- Add an ASCII accessible label `Distribuicao` for the `/supply-distribution` navigation link.
- Align affected Playwright locators with `Navegacao principal` and `Distribuicao`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `frontend-ux`: navigation accessibility names remain stable for role-based E2E selectors.

## Impact

- `frontend/src/components/AppNav.tsx`
- Navigation-related Playwright tests.
