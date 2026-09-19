import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const authFetchPath = new URL('../src/lib/authFetch.ts', import.meta.url)
const authJsonPath = new URL('../src/lib/authJson.ts', import.meta.url)
const favoritesPath = new URL('../src/pages/FavoritesDashboard.tsx', import.meta.url)
const homePath = new URL('../src/pages/HomePage.tsx', import.meta.url)
const walletPath = new URL('../src/pages/ExternalBalancesPage.tsx', import.meta.url)

test('auth renewal helpers and session-aware loaders are wired for #983', async () => {
  const [authFetchSource, authJsonSource, favoritesSource, homeSource, walletSource] = await Promise.all([
    readFile(authFetchPath, 'utf8'),
    readFile(authJsonPath, 'utf8'),
    readFile(favoritesPath, 'utf8'),
    readFile(homePath, 'utf8'),
    readFile(walletPath, 'utf8'),
  ])

  assert.match(authFetchSource, /export function isFetchAbortedError/)
  assert.match(authFetchSource, /export function isAuthRefreshInFlight/)
  assert.match(authFetchSource, /if \(!accessToken && refreshPromise\)/)
  assert.match(authFetchSource, /recoverUnauthorizedResponse/)
  assert.doesNotMatch(authFetchSource, /isRetry \|\| isAuthRefreshRequestUrl/)
  assert.match(authJsonSource, /MAX_AUTH_RECOVERY_ATTEMPTS/)
  assert.match(authJsonSource, /export async function fetchAuthJson/)
  assert.match(homeSource, /favoritesKpiPending/)
  assert.match(walletSource, /hasRecoverableAuthSession/)
  assert.match(homeSource, /fetchAuthJson/)
  assert.match(favoritesSource, /placeholderData: keepPreviousData/)
  assert.match(favoritesSource, /cancelRefetch: false/)
  assert.match(favoritesSource, /favorites-renewal-ok/)
  assert.match(walletSource, /fetchId !== lastFetchId\.current/)
  assert.match(walletSource, /wallet-renewal-ok/)
  assert.match(walletSource, /wallet-load-error/)
})

test('authFetch recovers when retry after refresh still returns 401 with refresh token', async () => {
  const storage = new Map()
  globalThis.localStorage = {
    getItem: (key) => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: (key) => storage.delete(key),
  }
  globalThis.window = { location: { origin: 'http://localhost:5173' } }

  storage.set('auth_access_token', 'stale-access')
  storage.set('auth_refresh_token', 'refresh-token')

  let resourceHits = 0
  let refreshHits = 0

  globalThis.fetch = async (url) => {
    const target = String(url)
    if (target.includes('/auth/refresh')) {
      refreshHits += 1
      return {
        ok: true,
        status: 200,
        json: async () => ({
          accessToken: `fresh-${refreshHits}`,
          refreshToken: 'refresh-token',
          id: 'user-1',
          userId: 'user-1',
          email: 'user@example.com',
          name: 'User',
          isAdmin: false,
          mustChangePassword: false,
          expiresIn: 3600,
        }),
      }
    }

    resourceHits += 1
    if (resourceHits <= 2) {
      return { ok: false, status: 401, json: async () => ({ detail: 'stale' }) }
    }
    return { ok: true, status: 200, json: async () => ({ items: [] }) }
  }

  const { authFetch } = await import('../src/lib/authFetch.ts')
  const response = await authFetch('http://localhost:5173/api/favorites/')
  assert.equal(response.status, 200)
  assert.equal(resourceHits, 3)
  assert.ok(refreshHits >= 2)
})

test('authFetch refreshes and retries after abort when refresh token remains', async () => {
  const storage = new Map()
  globalThis.localStorage = {
    getItem: (key) => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: (key) => storage.delete(key),
  }
  globalThis.window = { location: { origin: 'http://localhost:5173' } }

  storage.set('auth_access_token', 'stale-access')
  storage.set('auth_refresh_token', 'refresh-token')

  let resourceHits = 0
  let refreshHits = 0

  globalThis.fetch = async (url) => {
    const target = String(url)
    if (target.includes('/auth/refresh')) {
      refreshHits += 1
      return {
        ok: true,
        status: 200,
        json: async () => ({
          accessToken: 'fresh-after-abort',
          refreshToken: 'refresh-token',
          id: 'user-1',
          userId: 'user-1',
          email: 'user@example.com',
          name: 'User',
          isAdmin: false,
          mustChangePassword: false,
          expiresIn: 3600,
        }),
      }
    }

    resourceHits += 1
    if (resourceHits === 1) {
      throw new DOMException('The operation was aborted', 'AbortError')
    }
    return { ok: true, status: 200, json: async () => ({ ok: true }) }
  }

  const { authFetch } = await import('../src/lib/authFetch.ts')
  const response = await authFetch('http://localhost:5173/api/favorites/')
  assert.equal(response.status, 200)
  assert.equal(resourceHits, 2)
  assert.equal(refreshHits, 1)
})
