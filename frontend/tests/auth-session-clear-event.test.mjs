import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const authFetchPath = new URL('../src/lib/authFetch.ts', import.meta.url)
const authStorePath = new URL('../src/stores/authStore.tsx', import.meta.url)
const authEventsPath = new URL('../src/lib/authEvents.ts', import.meta.url)

test('authFetch notifies AuthProvider when refresh cannot recover a stale session', async () => {
  const [authFetchSource, authStoreSource, authEventsSource] = await Promise.all([
    readFile(authFetchPath, 'utf8'),
    readFile(authStorePath, 'utf8'),
    readFile(authEventsPath, 'utf8'),
  ])

  assert.match(authEventsSource, /AUTH_SESSION_CLEARED_EVENT = 'crypto:auth-session-cleared'/)
  assert.match(authEventsSource, /window\.dispatchEvent\(new CustomEvent\(AUTH_SESSION_CLEARED_EVENT/)

  assert.match(authFetchSource, /notifyAuthSessionCleared\('missing-refresh-token'\)/)
  assert.match(authFetchSource, /notifyAuthSessionCleared\('refresh-failed'\)/)
  assert.match(authFetchSource, /notifyAuthSessionCleared\('refresh-invalid'\)/)
  assert.match(authFetchSource, /notifyAuthSessionCleared\('refresh-error'\)/)

  assert.match(authStoreSource, /window\.addEventListener\(AUTH_SESSION_CLEARED_EVENT,\s*handleSessionCleared\)/)
  assert.match(authStoreSource, /persistAuthState\(null,\s*null,\s*null\)/)
  assert.match(authStoreSource, /queryClient\.clear\(\)/)
  assert.match(authStoreSource, /setState\(\{\s*user:\s*null,\s*accessToken:\s*null,\s*refreshToken:\s*null,\s*isLoading:\s*false\s*\}\)/)
})
