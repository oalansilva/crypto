import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const environmentPath = path.resolve(__dirname, '../src/lib/environment.ts')

test('environment indicator detects DEV host before Vite production-build fallback', async () => {
  const source = await readFile(environmentPath, 'utf8')

  assert.match(source, /resolveHostnameEnvironment/)
  assert.match(source, /hostname\.startsWith\('dev\.'\)/)
  assert.match(source, /if \(hostnameEnvironment\) return hostnameEnvironment/)
  assert.match(source, /return import\.meta\.env\.PROD \? 'production' : 'development'/)
})
