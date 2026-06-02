## Context

`authFetch` removes access and refresh tokens when a refresh attempt fails, but this happens outside `AuthProvider`. React state can still expose a stored user, so protected pages keep rendering and local loaders show endpoint-specific errors such as Monitor preferences failures.

The backend already returns the correct `401` for stale credentials and `200` for fresh credentials. The missing behavior is client-side state synchronization after token cleanup.

## Goals / Non-Goals

**Goals:**

- Make stale authenticated sessions behave like logout from the user's perspective.
- Keep token refresh successful paths unchanged.
- Apply the fix globally to every `authFetch` consumer, including Monitor, Favorites and Admin pages.
- Avoid exposing endpoint-specific error toasts when the root cause is invalid authentication.

**Non-Goals:**

- Do not change backend authentication, JWT contents, or refresh token persistence.
- Do not change Monitor preferences API behavior.
- Do not force reload the page unless the route system cannot react to state cleanup.

## Decisions

- Emit a browser event from `authFetch` when it clears tokens after failed refresh. This keeps `authFetch` framework-agnostic and avoids importing React auth state into a low-level fetch helper.
- Make `AuthProvider` listen for that event and clear local auth state plus React Query cache. This reuses existing `ProtectedRoute` behavior to redirect to `/login`.
- Keep normal `logout()` using the same cleanup semantics so manual logout and forced invalid-session cleanup stay aligned.

## Risks / Trade-offs

- Multiple concurrent 401s can dispatch the event more than once -> cleanup is idempotent and setting null state/cache clear is safe.
- A 401 from an endpoint during refresh retry still returns its response to the caller -> the route will unmount after auth state clears, so endpoint-specific toast lifetime is short and the session contract remains correct.
- E2E auth bypass should not be disrupted -> bypass mode keeps its initialization path and the event listener ignores forced cleanup there.

## Migration Plan

- Build and deploy the frontend bundle.
- Restart the app services using the repo `./restart` flow.
- Validate a fresh login can read `/api/monitor/preferences` and an invalid stored token redirects to `/login`.

## Open Questions

None.
