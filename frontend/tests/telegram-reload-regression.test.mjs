import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const telegramFormPath = path.resolve(__dirname, '../src/components/telegram/TelegramAlertsForm.tsx')
const monitorTabPath = path.resolve(__dirname, '../src/components/monitor/MonitorStatusTab.tsx')
const profilePagePath = path.resolve(__dirname, '../src/pages/ProfilePage.tsx')
const authFetchPath = path.resolve(__dirname, '../src/lib/authFetch.ts')

test('TelegramAlertsForm preserves linked state on transient 401 (card 749 Q1=C)', async () => {
  const source = await readFile(telegramFormPath, 'utf8')
  assert.match(source, /hasLoadedRef/)
  assert.match(source, /onSettingsChangeRef/)
  assert.match(source, /AbortController/)
  assert.match(source, /controller\.signal/)
  assert.match(source, /signal\?.aborted/)
  assert.match(source, /hasLoadedRef\.current/)
  assert.match(source, /isRealLogout/)
  assert.match(source, /authFetch\([^)]*telegram-settings[^)]*signal/)
  assert.doesNotMatch(source, /\[onSettingsChange, toast\]/)
  assert.match(source, /useEffect\(\(\) => \{\s*const controller = new AbortController\(\)/)
})

test('TelegramAlertsForm does not clear settings when already loaded', async () => {
  const source = await readFile(telegramFormPath, 'utf8')
  assert.match(source, /hasLoadedRef\.current && !isRealLogout/)
  assert.match(source, /hasLoadedRef\.current = true/)
  assert.match(source, /hasLoadedRef\.current = false/)
})

test('MonitorStatusTab preserves telegramAlertsEnabled on transient 401 (card 749 Q2=A)', async () => {
  const source = await readFile(monitorTabPath, 'utf8')
  assert.match(source, /telegramHasLoadedRef/)
  assert.match(source, /AbortController/)
  assert.match(source, /fetchMonitorContext\(controller\.signal\)/)
  assert.match(source, /telegramHasLoadedRef\.current = true/)
  assert.match(source, /telegramHasLoadedRef\.current/)
  assert.match(source, /isRealLogout/)
})

test('ProfilePage guards TelegramAlertsForm with Auth isLoading (card 749 Q4)', async () => {
  const source = await readFile(profilePagePath, 'utf8')
  assert.match(source, /useAuth\(\)/)
  assert.match(source, /authLoading/)
  assert.match(source, /isLoading: authLoading/)
  assert.match(source, /authLoading \? \(/)
  assert.match(source, /<TelegramAlertsForm variant="profile" \/>/)
})

test('authFetch encapsulates retry so transient 401 returns 200 (card 749 Q1=C)', async () => {
  const source = await readFile(authFetchPath, 'utf8')
  assert.match(source, /refreshAuthToken\(\)/)
  assert.match(source, /if \(!refreshedToken\) \{\s*return response/)
  assert.match(source, /notifyAuthSessionCleared\('missing-refresh-token'\)/)
  assert.match(source, /notifyAuthSessionCleared\('refresh-failed'\)/)
})
