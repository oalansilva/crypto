## Why

After user recovery and password reset, the browser can keep stale access and refresh tokens while React state still considers the user authenticated. Opening Monitor then shows a generic preferences error even though the real problem is an invalid session.

## What Changes

- Clear stored auth tokens and user state when an authenticated request receives `401` and token refresh fails.
- Notify the React auth provider when `authFetch` clears tokens outside the normal logout flow.
- Let protected routes redirect to login instead of keeping Monitor mounted with stale credentials.
- Preserve existing successful refresh behavior and normal logout behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `login-password-mandatory`: invalid authenticated sessions must clear client-side auth state like logout does.

## Impact

- Frontend auth fetch wrapper: `frontend/src/lib/authFetch.ts`
- Frontend auth state provider: `frontend/src/stores/authStore.tsx`
- Focused frontend test/build coverage for stale-session handling
