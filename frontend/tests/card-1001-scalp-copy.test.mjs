import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..')

function read(rel) {
  return fs.readFileSync(path.join(root, rel), 'utf8')
}

test('landing v4 no longer claims 24/7 bot as an absolute', () => {
  const html = read('public/prototypes/cripto-farol-landing-v4/index.html')
  assert.doesNotMatch(html, /Não, não é bot 24\/7/)
  assert.match(html, /Não por omissão/)
  assert.match(html, /scalp direcional BTCUSDT/)
  assert.match(html, /nunca sacamos/i)
})

test('help page admits optional scalp and drops nao e bot', () => {
  const help = read('src/pages/HelpPage.tsx')
  assert.doesNotMatch(help, /nao e bot/)
  assert.match(help, /scalp direcional BTCUSDT/)
  assert.match(help, /Operar/)
})

test('profile clause uses the same Spot key for scalp', () => {
  const profile = read('src/pages/ProfilePage.tsx')
  assert.match(profile, /mesma chave Spot também alimenta o scalp BTCUSDT/)
})

test('monitor panel copy bans profitable-strategy claims', () => {
  const module = read('src/components/monitor/ScalpModule.tsx')
  assert.doesNotMatch(module, /estratégia lucrativa/)
  assert.doesNotMatch(module, /formador de mercado/)
  assert.match(module, /Scalp BTCUSDT/)
})
