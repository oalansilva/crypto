## Context

The authenticated React app is wrapped by `ProtectedLayout`, which renders `Layout` and the shared `AppNav` shell for the protected routes. That makes the shell the correct place for a persistent environment signal: it covers Monitor, Favoritos, Combo, Admin, Profile, and other logged-in screens without duplicating UI per page.

The frontend already reads runtime/build configuration through `import.meta.env` for API and E2E auth behavior. The environment indicator should follow that pattern and preserve the existing Binance-style dark interface from `DESIGN.md`: near-black surfaces, yellow accent for primary emphasis, restrained 8px-or-less radii for compact controls, and trading red/green accents only when they communicate state.

## Goals / Non-Goals

**Goals:**

- Show a persistent `DEV` or `PROD` signal in every authenticated screen.
- Centralize environment resolution in one frontend helper.
- Keep the indicator visible in desktop sidebar/header and mobile header/menu.
- Use `DESIGN.md` tokens and avoid a decorative or oversized treatment.
- Allow explicit configuration through `VITE_APP_ENV` while falling back to Vite mode.

**Non-Goals:**

- Do not add backend endpoints or database configuration.
- Do not change authentication behavior.
- Do not expose secrets, hostnames, tokens, or deployment identifiers in the UI.
- Do not publish this card to `main`; this implementation ends as Done técnico on `develop`.

## Decisions

1. **Use a frontend-only environment helper.**
   - Decision: create a small helper under `frontend/src/lib/` that normalizes `VITE_APP_ENV` / `VITE_ENVIRONMENT` / `import.meta.env.MODE` into `development` or `production`.
   - Rationale: the UI needs only a safe label and visual variant. Backend dependency would slow first paint and add failure modes for a shell-level cue.
   - Alternative considered: fetch environment from `/api/config`. Rejected because the indicator should render with the shell even if API requests are unavailable.

2. **Render the indicator in the authenticated navigation shell.**
   - Decision: add a reusable component and mount it from `AppNav` in desktop and mobile navigation.
   - Rationale: `AppNav` is present on every protected page and already owns responsive shell layout.
   - Alternative considered: mount in individual pages. Rejected because it would be inconsistent and easy to miss.

3. **Differentiate DEV and PROD with compact state styling.**
   - Decision: DEV uses warning/yellow emphasis plus a stronger border; PROD uses a calmer success/green treatment.
   - Rationale: DEV should be unmistakable during validation, while PROD should remain clear without dominating normal operation.
   - Alternative considered: a full-width banner. Rejected for now because it would consume vertical space on dense operational screens.

4. **Expose stable selectors for validation.**
   - Decision: add `data-testid` and `data-environment` attributes to the indicator.
   - Rationale: the card requires visual/runtime proof across screens; stable selectors make Playwright/DOM checks direct and less brittle.

## Risks / Trade-offs

- [Risk] A production build accidentally using an unset environment variable could show the wrong label. -> Mitigation: production mode defaults to `PROD`; only explicit development-like values or Vite dev mode show `DEV`.
- [Risk] The compact indicator may be missed in mobile if only shown inside the menu. -> Mitigation: render it in the fixed mobile header and repeat it in the mobile drawer context.
- [Risk] Header width could become crowded on desktop. -> Mitigation: use compact text and hide nonessential descriptive copy on narrow desktop widths.

## Migration Plan

1. Implement the helper/component and mount it in `AppNav`.
2. Build the frontend with default mode to prove TypeScript/Vite compatibility.
3. Validate the indicator in development mode and production build mode.
4. Integrate into `develop`, restart services, and verify the served app returns the new bundle.

Rollback is a normal frontend revert of the helper/component and `AppNav` imports/usages.

## Open Questions

- None for this card.
