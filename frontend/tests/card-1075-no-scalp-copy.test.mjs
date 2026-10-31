import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..')

const FORBIDDEN = /\bscalp(er)?\b/i

/**
 * Surfaces that must not mention the removed scalper (OnboardingGuide is intentionally out of scope).
 * The public landing left this repo in card #1160: its copy check lives in oalansilva/cripto-farol-landing (tests/static).
 */
const COPY_SURFACES = [
  { label: 'Help (/help, outside OnboardingGuide)', rel: 'src/pages/HelpPage.tsx' },
  { label: 'Meu Perfil', rel: 'src/pages/ProfilePage.tsx' },
  { label: 'Credenciais Binance', rel: 'src/components/binance/BinanceCredentialsForm.tsx' },
]

function read(rel) {
  return fs.readFileSync(path.join(root, rel), 'utf8')
}

function assertNoScalpCopy(label, source) {
  const match = source.match(FORBIDDEN)
  assert.equal(
    match,
    null,
    `${label} must not expose scalp/scalper copy; found "${match?.[0]}"`,
  )
}

for (const { label, rel } of COPY_SURFACES) {
  test(`${label} has no scalp/scalper copy`, () => {
    assertNoScalpCopy(label, read(rel))
  })
}
