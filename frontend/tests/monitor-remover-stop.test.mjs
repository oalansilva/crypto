import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')

const protect = () => read('src/components/monitor/SpotProtectStopPanel.tsx')
const trade = () => read('src/components/monitor/SpotMarketTradePanel.tsx')
const proto = () => read('public/prototypes/card-861-remover-stop/index.html')

// --- 1.3 chart remove ---

test('1.3 gráfico: Remover stop abre confirmação em vez de chamar DELETE direto', () => {
  const source = protect()
  assert.match(source, /data-testid="spot-protect-remove"/)
  assert.match(source, /onClick=\{openRemoveConfirm\}/)
  assert.doesNotMatch(source, /spot-protect-remove"[\s\S]{0,400}void remove\(\)/)
  assert.match(source, /const openRemoveConfirm/)
  assert.match(source, /setConfirmRemove\(true\)/)
})

test('1.3 gráfico: DELETE só acontece a partir da confirmação', () => {
  const source = protect()
  const deleteIdx = source.indexOf("method: 'DELETE'")
  assert.notEqual(deleteIdx, -1, 'expected DELETE /monitor/spot-stop-order')
  assert.match(source, /onClick=\{\(\) => void remove\(\)\}/)
  assert.match(source, /data-testid="spot-protect-remove-confirm-yes"/)
  // remove() é referenciado só pelo botão de confirmação
  const refs = [...source.matchAll(/void remove\(\)/g)].length
  assert.equal(refs, 1, `remove() must be wired once (confirm), found ${refs}`)
})

test('1.3 gráfico: Cancelar fecha sem chamar API', () => {
  const source = protect()
  assert.match(source, /data-testid="spot-protect-remove-confirm-no"/)
  assert.match(source, /const closeRemoveConfirm = \(\) => \{\s+setConfirmRemove\(false\)\s+\}/)
})

test('1.3 gráfico: remover nunca dispara venda', () => {
  const source = protect()
  assert.doesNotMatch(source, /spot-market-orders/)
  assert.doesNotMatch(source, /requestPreview|submitOrder/)
})

test('1.3 gráfico: sem HOLD/stop não é oferecido', () => {
  const source = protect()
  assert.match(source, /\{!disabledReason && protectedOrder \? \(/)
  assert.match(source, /\{confirmRemove && !disabledReason && protectedOrder \? \(/)
})

test('1.3 gráfico: confirmação identifica stop + origem explícita + foco vai-e-volta', () => {
  const source = protect()
  assert.match(source, /data-testid="spot-protect-remove-confirm"/)
  assert.match(source, /role="group"/)
  assert.match(source, /aria-label="Confirmar remoção da stop"/)
  assert.match(source, /tabIndex=\{-1\}/)
  assert.match(source, /aria-expanded=\{confirmRemove\}/)
  assert.match(source, /aria-controls="spot-protect-remove-confirm"/)
  assert.match(source, /criada no app \(Farol\)/)
  assert.match(source, /removeConfirmRef\.current\?\.focus\(\)/)
  assert.match(source, /removeTriggerRef\.current\?\.focus\(\)/)
  assert.match(source, /data-testid="spot-protect-app-note"/)
  assert.match(source, /data-testid="spot-protect-external-note"/)
})

// --- 2.4 sell-flow remove ---

test('2.4 venda: falha com sinal de saldo travado busca a stop e entra em blocked', () => {
  const source = trade()
  assert.match(source, /looksStopBlocked/)
  assert.match(source, /STOP_BLOCKED_MESSAGE_RE/)
  assert.match(source, /enterBlockedIfStopOpen/)
  assert.match(source, /setStep\('blocked'\)/)
  assert.match(source, /data-testid="spot-sell-stop-blocked"/)
})

test('2.4 venda: bloqueada→remove→volta a entry exigindo nova prévia; remover sozinho não vende', () => {
  const source = trade()
  assert.match(source, /data-testid="spot-sell-stop-remove"/)
  assert.match(source, /data-testid="spot-sell-stop-confirm-yes"/)
  assert.match(source, /data-testid="spot-sell-stop-confirm-no"/)
  assert.match(source, /data-testid="spot-sell-stop-removed"/)
  assert.match(source, /data-testid="spot-repreview-order"/)
  assert.match(source, /removeBlockingStop/)
  assert.match(source, /method: 'DELETE'/)
  // pós-remoção: step removed + limpeza de preview/result exigindo nova prévia
  assert.match(source, /setStep\('removed'\)/)
  const body = source.slice(source.indexOf('const removeBlockingStop'))
  assert.match(body, /setPreview\(null\)/)
  assert.match(body, /setResult\(null\)/)
  // removeBlockingStop não chama preview/submit
  assert.doesNotMatch(body.slice(0, body.indexOf('backToEntryForNewPreview')), /requestPreview|submitOrder/)
  // repreview volta a entry (nova prévia obrigatória)
  assert.match(source, /backToEntryForNewPreview/)
})

test('2.4 venda: falha não-stop mantém o caminho atual sem oferecer remover', () => {
  const source = trade()
  // sem stop aberta, enterBlockedIfStopOpen retorna false e o erro segue o fluxo
  assert.match(source, /if \(!stop\) return false/)
  assert.match(source, /if \(entered\) return;/)
  // guarda SELL: compra nunca entra em blocked
  assert.match(source, /side === 'SELL' && looksStopBlocked/)
})

test('2.4 venda: confirmação própria com origem explícita + foco vai-e-volta', () => {
  const source = trade()
  assert.match(source, /id="spot-trade-remove-confirm"/)
  assert.match(source, /aria-label="Confirmar remoção da stop"/)
  assert.match(source, /aria-controls="spot-trade-remove-confirm"/)
  assert.match(source, /criada no app \(Farol\)/)
  assert.match(source, /criada só na exchange/)
  assert.match(source, /tradeRemoveConfirmRef\.current\?\.focus\(\)/)
  assert.match(source, /tradeRemoveTriggerRef\.current\?\.focus\(\)/)
})

// --- prototype conformance (layout spec) ---

test('protótipo 861 é a spec de layout: testids do delta existem no produto', () => {
  const protoSource = proto()
  const product = protect() + trade()
  for (const testid of [
    'spot-protect-remove',
    'spot-sell-stop-blocked',
    'spot-sell-stop-remove',
    'spot-sell-stop-confirm-yes',
    'spot-sell-stop-removed',
    'spot-repreview-order',
  ]) {
    assert.ok(protoSource.includes(testid), `prototype missing ${testid}`)
    assert.ok(product.includes(testid), `product missing ${testid}`)
  }
  // Desvio justificado (P3 Apply): confirmação do gráfico usa
  // spot-protect-remove-confirm* em vez de spot-protect-confirm* do protótipo,
  // porque spot-protect-confirm* já pertence ao fluxo Proteger no produto.
  assert.ok(product.includes('spot-protect-remove-confirm'))
})
