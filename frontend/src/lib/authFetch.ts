/**
 * Fetch wrapper that automatically includes JWT authentication.
 */

import { notifyAuthSessionCleared } from './authEvents'

type RefreshResponse = {
  accessToken: string
  refreshToken: string
  id: string
  userId: string
  email: string
  name: string
  isAdmin: boolean
  mustChangePassword: boolean
  expiresIn: number
}

const ACCESS_TOKEN_KEY = 'auth_access_token'
const REFRESH_TOKEN_KEY = 'auth_refresh_token'
const API_BASE_URL = import.meta.env?.VITE_API_URL || '/api'

const normalizedBase = String(API_BASE_URL || '').trim().replace(/\/$/, '')
const REFRESH_ENDPOINT = `${normalizedBase}/auth/refresh`

let refreshPromise: Promise<string | null> | null = null

export function isFetchAbortedError(error: unknown): boolean {
  if (error instanceof DOMException && error.name === 'AbortError') {
    return true
  }
  return error instanceof Error && error.name === 'AbortError'
}

export function isNetworkFetchError(error: unknown): boolean {
  if (isFetchAbortedError(error)) {
    return true
  }
  if (error instanceof TypeError) {
    return true
  }
  if (error instanceof Error) {
    return /failed to fetch|networkerror|load failed/i.test(error.message)
  }
  return false
}

export function isAuthRefreshInFlight(): boolean {
  return refreshPromise !== null
}

export function hasRecoverableAuthSession(): boolean {
  const { refreshToken } = loadAuthTokens()
  return Boolean(refreshToken)
}

function loadAuthTokens() {
  try {
    return {
      accessToken: localStorage.getItem(ACCESS_TOKEN_KEY),
      refreshToken: localStorage.getItem(REFRESH_TOKEN_KEY),
    }
  } catch {
    return {
      accessToken: null,
      refreshToken: null,
    }
  }
}

function persistAuthTokens(accessToken: string | null, refreshToken: string | null) {
  if (accessToken && refreshToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    return
  }

  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

function isAuthRefreshRequestUrl(url: string): boolean {
  try {
    const parsed = new URL(url, window.location.origin)
    return parsed.pathname === '/api/auth/refresh' || parsed.pathname.endsWith('/api/auth/refresh')
  } catch {
    return url.includes('/api/auth/refresh')
  }
}

function requestHeadersWithToken(headers: HeadersInit | undefined, token: string | null): Headers {
  const merged = new Headers(headers)
  if (token) {
    merged.set('Authorization', `Bearer ${token}`)
  }
  return merged
}

function parseRefreshPayload(data: unknown): RefreshResponse | null {
  if (!data || typeof data !== 'object') {
    return null
  }
  const maybe = data as Partial<Record<keyof RefreshResponse, unknown>>
  return (
    typeof maybe.accessToken === 'string' &&
    typeof maybe.refreshToken === 'string'
  )
    ? {
        accessToken: maybe.accessToken,
        refreshToken: maybe.refreshToken,
        id: String(maybe.id || ''),
        userId: String(maybe.userId || ''),
        email: String(maybe.email || ''),
        name: String(maybe.name || ''),
        isAdmin: Boolean(maybe.isAdmin),
        mustChangePassword: Boolean(maybe.mustChangePassword),
        expiresIn: typeof maybe.expiresIn === 'number' ? maybe.expiresIn : 0,
      }
    : null
}

async function refreshAuthToken(): Promise<string | null> {
  if (refreshPromise) {
    return refreshPromise
  }

  const { refreshToken } = loadAuthTokens()
  if (!refreshToken) {
    persistAuthTokens(null, null)
    notifyAuthSessionCleared('missing-refresh-token')
    return null
  }

  refreshPromise = (async () => {
    try {
      const response = await fetch(REFRESH_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken }),
      })

      if (!response.ok) {
        persistAuthTokens(null, null)
        notifyAuthSessionCleared('refresh-failed')
        return null
      }

      const payload = await response.json().catch(() => null)
      const parsed = parseRefreshPayload(payload)

      if (!parsed?.accessToken || !parsed.refreshToken) {
        persistAuthTokens(null, null)
        notifyAuthSessionCleared('refresh-invalid')
        return null
      }

      persistAuthTokens(parsed.accessToken, parsed.refreshToken)
      return parsed.accessToken
    } catch (error) {
      if (isNetworkFetchError(error)) {
        return null
      }
      persistAuthTokens(null, null)
      notifyAuthSessionCleared('refresh-error')
      return null
    } finally {
      refreshPromise = null
    }
  })()

  return refreshPromise
}

async function fetchWithAccessToken(
  url: string,
  options: RequestInit,
  accessToken: string | null,
): Promise<Response> {
  return fetch(url, {
    ...options,
    headers: requestHeadersWithToken(options.headers, accessToken),
  })
}

async function recoverUnauthorizedResponse(
  url: string,
  options: RequestInit,
  staleResponse: Response,
): Promise<Response> {
  if (!hasRecoverableAuthSession()) {
    return staleResponse
  }

  if (refreshPromise) {
    const inFlightToken = await refreshPromise
    if (inFlightToken) {
      const retried = await fetchWithAccessToken(url, options, inFlightToken)
      if (retried.status !== 401 || !hasRecoverableAuthSession()) {
        return retried
      }
    }
  }

  const refreshedToken = await refreshAuthToken()
  if (!refreshedToken) {
    return staleResponse
  }

  const retried = await fetchWithAccessToken(url, options, refreshedToken)
  if (retried.status === 401 && hasRecoverableAuthSession()) {
    return recoverUnauthorizedResponse(url, options, retried)
  }
  return retried
}

export async function authFetch(url: string, options: RequestInit = {}, isRetry = false): Promise<Response> {
  let { accessToken } = loadAuthTokens()

  if (!accessToken && refreshPromise) {
    accessToken = await refreshPromise
  }

  let response: Response
  try {
    response = await fetchWithAccessToken(url, options, accessToken)
  } catch (error) {
    if (isFetchAbortedError(error)) {
      if (refreshPromise) {
        const refreshedToken = await refreshPromise
        if (refreshedToken) {
          return authFetch(url, options, true)
        }
      }
      if (!isRetry && hasRecoverableAuthSession()) {
        const refreshedToken = await refreshAuthToken()
        if (refreshedToken) {
          return authFetch(url, options, true)
        }
      }
    }
    throw error
  }

  if (response.status !== 401 || isAuthRefreshRequestUrl(url)) {
    return response
  }

  return recoverUnauthorizedResponse(url, options, response)
}
