/* Prototype-only JS: fake dataset + filtering/sorting + states. */

const fmtUSD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 })
const fmtNum = (n, max = 8) => {
  if (n === null || n === undefined || Number.isNaN(n)) return '—'
  const s = Number(n).toFixed(max)
  return s.replace(/\.0+$/, '').replace(/(\.[0-9]*?)0+$/, '$1')
}

/** @type {Array<any>} */
const DATA = [
  { asset: 'BTC', name: 'Bitcoin', total: 0.125, free: 0.08, locked: 0.045, price: 62500.23, value_usd: 7812.53, pnl_usd: 420.12, pnl_pct: 5.68, has_pnl: true },
  { asset: 'ETH', name: 'Ethereum', total: 2.42, free: 2.42, locked: 0.0, price: 3420.12, value_usd: 8276.69, pnl_usd: -122.5, pnl_pct: -1.46, has_pnl: true },
  { asset: 'SOL', name: 'Solana', total: 65.0, free: 65.0, locked: 0.0, price: 128.22, value_usd: 8334.3, pnl_usd: null, pnl_pct: null, has_pnl: false },
  { asset: 'BNB', name: 'BNB', total: 5.35, free: 5.35, locked: 0.0, price: 580.10, value_usd: 3103.54, pnl_usd: 42.01, pnl_pct: 1.37, has_pnl: true },
  { asset: 'ADA', name: 'Cardano', total: 1200.0, free: 1180.0, locked: 20.0, price: 0.62, value_usd: 744.0, pnl_usd: null, pnl_pct: null, has_pnl: false },
  { asset: 'DOGE', name: 'Dogecoin', total: 10000.0, free: 10000.0, locked: 0.0, price: 0.17, value_usd: 1700.0, pnl_usd: -55.0, pnl_pct: -3.14, has_pnl: true },
  { asset: 'ARB', name: 'Arbitrum', total: 400.0, free: 400.0, locked: 0.0, price: 1.82, value_usd: 728.0, pnl_usd: 18.5, pnl_pct: 2.61, has_pnl: true },
  { asset: 'XRP', name: 'XRP', total: 950.0, free: 950.0, locked: 0.0, price: 0.56, value_usd: 532.0, pnl_usd: null, pnl_pct: null, has_pnl: false },
  { asset: 'DUST', name: 'Tiny coin', total: 12.0, free: 12.0, locked: 0.0, price: 0.001, value_usd: 0.012, pnl_usd: null, pnl_pct: null, has_pnl: false },
]

const el = (id) => document.getElementById(id)

const rowsEl = el('rows')
const cardsEl = el('cards')
const emptyEl = el('stateEmpty')

const qEl = el('q')
const minUsdEl = el('minUsd')
const lockedOnlyEl = el('lockedOnly')
const sortEl = el('sort')

const kpiTotalEl = el('kpiTotal')
const kpiMetaEl = el('kpiMeta')

const sumTotalEl = el('sumTotal')
const sumLockedEl = el('sumLocked')
const sumPnlEl = el('sumPnl')

const metaLineEl = el('metaLine')
const footerMetaEl = el('footerMeta')

const toastEl = el('toast')
const toastTitleEl = el('toastTitle')
const toastBodyEl = el('toastBody')

let sortOverride = null // { key: 'value'|'asset'|'pnl', dir: 'asc'|'desc' }

function computeView() {
  const q = String(qEl.value || '').trim().toLowerCase()
  const minUsd = Number(minUsdEl.value || 0)
  const lockedOnly = !!lockedOnlyEl.checked

  let items = DATA.slice()

  if (q) {
    items = items.filter((it) => it.asset.toLowerCase().includes(q) || it.name.toLowerCase().includes(q))
  }

  items = items.filter((it) => (Number.isFinite(minUsd) ? it.value_usd >= minUsd : true))

  if (lockedOnly) {
    items = items.filter((it) => it.locked > 0)
  }

  const s = sortOverride || parseSort(sortEl.value)
  items.sort((a, b) => cmp(a, b, s))

  return { items, q, minUsd, lockedOnly, sort: s }
}

function parseSort(v) {
  switch (v) {
    case 'value_asc': return { key: 'value', dir: 'asc' }
    case 'value_desc': return { key: 'value', dir: 'desc' }
    case 'asset_desc': return { key: 'asset', dir: 'desc' }
    case 'asset_asc': return { key: 'asset', dir: 'asc' }
    case 'pnl_asc': return { key: 'pnl', dir: 'asc' }
    case 'pnl_desc': return { key: 'pnl', dir: 'desc' }
    default: return { key: 'value', dir: 'desc' }
  }
}

function cmp(a, b, s) {
  const dir = s.dir === 'asc' ? 1 : -1
  if (s.key === 'asset') return dir * a.asset.localeCompare(b.asset)
  if (s.key === 'pnl') {
    const ap = a.pnl_usd
    const bp = b.pnl_usd
    if (ap == null && bp == null) return 0
    if (ap == null) return 1
    if (bp == null) return -1
    return dir * (ap - bp)
  }
  // value
  return dir * (a.value_usd - b.value_usd)
}

function render() {
  const { items, q, minUsd, lockedOnly, sort } = computeView()

  const total = items.reduce((acc, it) => acc + it.value_usd, 0)
  const lockedUsd = items.reduce((acc, it) => acc + (it.locked * it.price), 0)
  const pnlItems = items.filter((it) => it.pnl_usd != null)
  const pnlSum = pnlItems.reduce((acc, it) => acc + it.pnl_usd, 0)

  // Top KPIs
  kpiTotalEl.textContent = fmtUSD.format(total)
  kpiMetaEl.textContent = `${items.length} ativos · filtro min USD ${Number.isFinite(minUsd) ? minUsd.toFixed(2) : '—'}`

  sumTotalEl.textContent = fmtUSD.format(total)
  sumLockedEl.textContent = fmtUSD.format(lockedUsd)

  if (pnlItems.length) {
    const cls = pnlSum >= 0 ? 'pos' : 'neg'
    sumPnlEl.innerHTML = `<span class="${cls}">${fmtUSD.format(pnlSum)}</span> <span class="muted" style="font-size:12px;">(${pnlItems.length}/${items.length})</span>`
  } else {
    sumPnlEl.textContent = '—'
  }

  const bits = []
  if (q) bits.push(`busca: “${q.toUpperCase()}”`)
  if (lockedOnly) bits.push('locked only')
  bits.push(`min USD: ${Number.isFinite(minUsd) ? minUsd.toFixed(2) : '—'}`)
  bits.push(`sort: ${sort.key}/${sort.dir}`)
  metaLineEl.innerHTML = `<span class="muted">${bits.join(' · ')}</span>`

  footerMetaEl.textContent = `Prototype · ${items.length} rows visíveis · sort ${sort.key}/${sort.dir}`

  // Empty state
  emptyEl.hidden = items.length !== 0

  // Desktop table rows
  rowsEl.innerHTML = items.map((it) => rowHTML(it)).join('')

  // Mobile cards
  cardsEl.innerHTML = items.map((it) => cardHTML(it)).join('')
}

function rowHTML(it) {
  const pnl = it.pnl_usd
  const pnlCls = pnl == null ? '' : (pnl >= 0 ? 'pos' : 'neg')
  const pnlText = pnl == null ? '—' : `${fmtUSD.format(pnl)} (${fmtNum(it.pnl_pct, 2)}%)`
  const badge = it.locked > 0 ? '<span class="badge">LOCKED</span>' : '<span class="badge">SPOT</span>'

  return `
    <div class="table__row" role="row">
      <div class="td">
        <div class="asset">
          <div class="asset__icon" aria-hidden="true">${it.asset.slice(0, 1)}</div>
          <div class="asset__main">
            <div class="asset__sym">${it.asset} ${badge}</div>
            <div class="asset__meta">${it.name}</div>
          </div>
        </div>
      </div>
      <div class="td td--num">${fmtNum(it.total, 8)}</div>
      <div class="td td--num">${fmtNum(it.free, 8)}</div>
      <div class="td td--num">${fmtNum(it.locked, 8)}</div>
      <div class="td td--num">${fmtUSD.format(it.value_usd)}</div>
      <div class="td td--num">$${fmtNum(it.price, 6)}</div>
      <div class="td td--num ${pnlCls}">${pnlText}</div>
    </div>
  `.trim()
}

function cardHTML(it) {
  const pnl = it.pnl_usd
  const pnlCls = pnl == null ? '' : (pnl >= 0 ? 'pos' : 'neg')
  const pnlText = pnl == null ? '—' : `${fmtUSD.format(pnl)} (${fmtNum(it.pnl_pct, 2)}%)`

  return `
    <div class="cardRow">
      <div class="cardRow__top">
        <div class="asset">
          <div class="asset__icon" aria-hidden="true">${it.asset.slice(0, 1)}</div>
          <div class="asset__main">
            <div class="asset__sym">${it.asset}</div>
            <div class="asset__meta">${it.locked > 0 ? `Locked: ${fmtNum(it.locked, 8)}` : 'Spot'}</div>
          </div>
        </div>
        <div class="cardRow__vals">
          <div class="cardRow__usd">${fmtUSD.format(it.value_usd)}</div>
          <div class="cardRow__qty">Total: ${fmtNum(it.total, 8)}</div>
        </div>
      </div>

      <div class="cardRow__grid">
        <div class="miniKV">
          <div class="miniKV__k">Preço</div>
          <div class="miniKV__v">$${fmtNum(it.price, 6)}</div>
        </div>
        <div class="miniKV">
          <div class="miniKV__k">PnL</div>
          <div class="miniKV__v ${pnlCls}">${pnlText}</div>
        </div>
        <div class="miniKV">
          <div class="miniKV__k">Free</div>
          <div class="miniKV__v">${fmtNum(it.free, 8)}</div>
        </div>
        <div class="miniKV">
          <div class="miniKV__k">Locked</div>
          <div class="miniKV__v">${fmtNum(it.locked, 8)}</div>
        </div>
      </div>
    </div>
  `.trim()
}

function toast(title, body) {
  toastTitleEl.textContent = title
  toastBodyEl.textContent = body
  toastEl.hidden = false
}

function toastClose() {
  toastEl.hidden = true
}

function simulateLoading() {
  rowsEl.innerHTML = Array.from({ length: 6 }).map(() => skeletonRow()).join('')
  cardsEl.innerHTML = Array.from({ length: 5 }).map(() => skeletonCard()).join('')
  emptyEl.hidden = true
  footerMetaEl.textContent = 'Prototype · loading…'
  kpiTotalEl.textContent = '—'
  kpiMetaEl.textContent = 'Carregando…'
  sumTotalEl.textContent = '—'
  sumLockedEl.textContent = '—'
  sumPnlEl.textContent = '—'
  setTimeout(() => render(), 650)
}

function skeletonRow() {
  return `
    <div class="table__row" style="opacity:0.7">
      <div class="td"><span class="badge">loading</span></div>
      <div class="td td--num">—</div>
      <div class="td td--num">—</div>
      <div class="td td--num">—</div>
      <div class="td td--num">—</div>
      <div class="td td--num">—</div>
      <div class="td td--num">—</div>
    </div>
  `.trim()
}

function skeletonCard() {
  return `
    <div class="cardRow" style="opacity:0.7">
      <div class="cardRow__top">
        <div class="asset"><span class="badge">loading</span></div>
        <div class="cardRow__vals"><div class="cardRow__usd">—</div><div class="cardRow__qty">—</div></div>
      </div>
      <div class="cardRow__grid">
        <div class="miniKV"><div class="miniKV__k">Preço</div><div class="miniKV__v">—</div></div>
        <div class="miniKV"><div class="miniKV__k">PnL</div><div class="miniKV__v">—</div></div>
        <div class="miniKV"><div class="miniKV__k">Free</div><div class="miniKV__v">—</div></div>
        <div class="miniKV"><div class="miniKV__k">Locked</div><div class="miniKV__v">—</div></div>
      </div>
    </div>
  `.trim()
}

function bind() {
  const rerender = () => { sortOverride = null; render() }
  qEl.addEventListener('input', rerender)
  minUsdEl.addEventListener('input', rerender)
  lockedOnlyEl.addEventListener('change', rerender)
  sortEl.addEventListener('change', () => { sortOverride = null; render() })

  document.body.addEventListener('click', (e) => {
    const t = /** @type {HTMLElement} */ (e.target)
    const sortBtn = t.closest('[data-sort]')
    if (sortBtn) {
      const key = sortBtn.getAttribute('data-sort')
      // toggle dir
      const current = sortOverride || parseSort(sortEl.value)
      const dir = current.key === key && current.dir === 'desc' ? 'asc' : 'desc'
      sortOverride = { key, dir }
      render()
      return
    }

    const act = t.closest('[data-action]')
    if (!act) return
    const a = act.getAttribute('data-action')
    if (a === 'reset') {
      qEl.value = ''
      minUsdEl.value = '0.02'
      lockedOnlyEl.checked = false
      sortEl.value = 'value_desc'
      sortOverride = null
      render()
    }
    if (a === 'loading') simulateLoading()
    if (a === 'error') toast('Erro ao sincronizar balances', 'Tente novamente. (Prototype: não exibir detalhes sensíveis)')
    if (a === 'toast-close') toastClose()
    if (a === 'refresh') simulateLoading()
    if (a === 'export') toast('Export (placeholder)', 'No produto: CSV / copiar para clipboard.')
  })
}

bind()
render()
