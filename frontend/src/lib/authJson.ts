import { apiUrl } from './apiBase'
import {
  authFetch,
  hasRecoverableAuthSession,
  isAuthRefreshInFlight,
  isFetchAbortedError,
} from './authFetch'

export {
  isFetchAbortedError,
  isNetworkFetchError,
  hasRecoverableAuthSession,
  isAuthRefreshInFlight,
} from './authFetch'

const MAX_AUTH_RECOVERY_ATTEMPTS = 12
const AUTH_RECOVERY_DELAY_MS = 50

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

export class AuthFetchAbortedError extends Error {
  constructor() {
    super('Auth fetch aborted')
    this.name = 'AuthFetchAbortedError'
  }
}

export class AuthSessionExpiredError extends Error {
  constructor() {
    super('Auth session expired')
    this.name = 'AuthSessionExpiredError'
  }
}

export async function fetchAuthJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = apiUrl(path).toString()

  for (let attempt = 0; attempt < MAX_AUTH_RECOVERY_ATTEMPTS; attempt += 1) {
    const res = await authFetch(url, options)
    const payload = await res.json().catch(() => null)
    if (res.ok) {
      return payload as T
    }

    if (res.status === 401) {
      if (!hasRecoverableAuthSession()) {
        throw new AuthSessionExpiredError()
      }
      if (isAuthRefreshInFlight() || attempt < MAX_AUTH_RECOVERY_ATTEMPTS - 1) {
        await delay(AUTH_RECOVERY_DELAY_MS)
        continue
      }
      throw new AuthSessionExpiredError()
    }

    const detail =
      payload && typeof payload === 'object' ? (payload as { detail?: string }).detail : undefined
    throw new Error(detail || `Falha ao carregar ${path}`)
  }

  throw new Error(`Falha ao carregar ${path}`)
}
