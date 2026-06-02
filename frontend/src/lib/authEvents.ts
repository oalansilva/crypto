export const AUTH_SESSION_CLEARED_EVENT = 'crypto:auth-session-cleared'

type AuthSessionClearedReason =
  | 'missing-refresh-token'
  | 'refresh-failed'
  | 'refresh-invalid'
  | 'refresh-error'

export function notifyAuthSessionCleared(reason: AuthSessionClearedReason) {
  if (typeof window === 'undefined') {
    return
  }

  window.dispatchEvent(new CustomEvent(AUTH_SESSION_CLEARED_EVENT, { detail: { reason } }))
}
