import type { Page, Route } from '@playwright/test'

/**
 * Catálogo de ativos Binance simulado para os specs funcionais (card #1117).
 * Implementa as rotas `/api/assets/catalog` (pesquisa paginada), `/resolve`,
 * `/lookup` e `/refresh` sobre uma amostra com cripto, ações e ETFs, incluindo
 * ativos marcados (suspenso, fora de mercado, removido).
 */

export type MockState = 'tradable' | 'suspended' | 'off_market' | 'no_trading' | 'no_rules' | 'removed'
export type MockClass = 'crypto' | 'stock' | 'etf'

export interface MockAsset {
  asset_id: string
  asset_class: MockClass
  symbol: string
  name: string
  state: MockState
  state_label: string
  state_reason: string | null
  info_note: null
  removed_at: string | null
  selectable: boolean
  analysis_available: boolean
  history: { status: 'local' | 'on_demand' | 'not_collected' | 'none'; from: string | null; to: string | null }
}

const STATE_LABEL: Record<MockState, string> = {
  tradable: 'Negociável',
  suspended: 'Suspenso',
  off_market: 'Fora de mercado',
  no_trading: 'Sem negociação',
  no_rules: 'Sem regras de negociação',
  removed: 'Removido',
}

function make(
  asset_class: MockClass,
  symbol: string,
  name: string,
  state: MockState = 'tradable',
  reason: string | null = null,
  history?: MockAsset['history'],
): MockAsset {
  return {
    asset_id: asset_class === 'crypto' ? `binance:spot:${symbol}` : `binance:equity:EQ_${symbol}`,
    asset_class,
    symbol,
    name,
    state,
    state_label: STATE_LABEL[state],
    state_reason: reason,
    info_note: null,
    removed_at: state === 'removed' ? '2026-09-12T00:00:00Z' : null,
    selectable: state === 'tradable',
    analysis_available: asset_class === 'crypto',
    history:
      history ??
      (asset_class === 'crypto'
        ? { status: state === 'tradable' ? 'on_demand' : 'none', from: null, to: null }
        : { status: 'not_collected', from: null, to: null }),
  }
}

/** Catálogo só de cripto negociável, para specs que precisam de uma lista pequena e previsível. */
export function cryptoCatalog(symbols: string[]): MockAsset[] {
  return symbols.map((symbol) => make('crypto', symbol, symbol.split('/')[0]))
}

const BTC_HISTORY = { status: 'local' as const, from: '2017-08-17T00:00:00Z', to: '2026-10-19T00:00:00Z' }
const WAVES_HISTORY = { status: 'local' as const, from: '2018-01-01T00:00:00Z', to: '2024-05-31T00:00:00Z' }

export function defaultCatalog(): MockAsset[] {
  return [
    make('crypto', 'BTC/USDT', 'Bitcoin', 'tradable', null, BTC_HISTORY),
    make('crypto', 'ETH/USDT', 'Ethereum', 'tradable', null, BTC_HISTORY),
    make('crypto', 'SOL/USDT', 'Solana'),
    make('crypto', 'BNB/USDT', 'BNB'),
    make('crypto', 'XRP/USDT', 'XRP'),
    make('crypto', 'DOGE/USDT', 'Dogecoin'),
    make('crypto', 'ADA/USDT', 'Cardano'),
    make('crypto', 'LINK/USDT', 'Chainlink'),
    make('crypto', 'AVAX/USDT', 'Avalanche'),
    make('crypto', 'DOT/USDT', 'Polkadot'),
    make('crypto', 'ALPHA/USDT', 'Alpha'),
    make('crypto', 'ARPA/USDT', 'Arpa'),
    make('crypto', 'AGLD/USDT', 'Adventure Gold', 'removed', 'Saiu da lista spot da Binance em 12 set. 2026.', WAVES_HISTORY),
    make('crypto', 'WAVES/USDT', 'Waves', 'suspended', 'Negociação pausada pela Binance (status BREAK).', WAVES_HISTORY),
    make('stock', 'NVDA', 'NVIDIA Corporation Common Stock'),
    make('stock', 'AAPL', 'Apple Inc. Common Stock'),
    make('stock', 'MSFT', 'Microsoft Corporation Common Stock'),
    make('stock', 'AVB', 'AvalonBay Communities, Inc.', 'off_market', 'A Binance marcou a ação como fora de mercado.'),
    make('stock', 'TMHC', 'Taylor Morrison Home Corporation Common Stock', 'no_rules', 'Está no catálogo da Binance, mas sem regras de negociação.'),
    make('etf', 'SPY', 'State Street SPDR S&P 500 ETF Trust'),
    make('etf', 'QQQ', 'Invesco QQQ Trust, Series 1'),
    make('etf', 'NVDX', 'T-Rex 2X Long NVIDIA Daily Target ETF'),
    make('etf', 'IBIC', 'iShares iBonds Oct 2026 Term TIPS ETF', 'off_market', 'A Binance marcou o ETF como fora de mercado.'),
  ]
}

const OK = {
  status: 'ok' as const,
  updated_at: '2026-10-20T09:00:00Z',
  last_attempt_at: '2026-10-20T09:00:00Z',
  reason: null,
  code: null,
  refreshing: false,
}

export type MockFreshness = Record<MockClass, typeof OK | Record<string, unknown>>

export interface CatalogMock {
  assets: MockAsset[]
  /** Altera a falha simulada: `crypto-down`, `equity-stale` ou `ok`. */
  setScenario(name: 'ok' | 'crypto-down' | 'equity-stale'): void
  requests: { catalog: string[]; resolve: unknown[]; lookup: unknown[]; refresh: unknown[] }
}

function normalize(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
}

export async function mockAssetCatalog(
  page: Page,
  options: { assets?: MockAsset[]; scenario?: 'ok' | 'crypto-down' | 'equity-stale' } = {},
): Promise<CatalogMock> {
  const assets = options.assets ?? defaultCatalog()
  let scenario: 'ok' | 'crypto-down' | 'equity-stale' = options.scenario ?? 'ok'
  const requests: CatalogMock['requests'] = { catalog: [], resolve: [], lookup: [], refresh: [] }

  const freshness = () => {
    const down = { status: 'unavailable', updated_at: null, last_attempt_at: '2026-10-20T09:00:00Z', reason: 'A Binance não respondeu.', code: 'network', refreshing: false }
    const stale = { status: 'stale', updated_at: '2026-10-19T21:00:00Z', last_attempt_at: '2026-10-20T09:00:00Z', reason: 'A Binance não respondeu.', code: 'network', refreshing: false }
    return {
      crypto: scenario === 'crypto-down' ? down : OK,
      stock: scenario === 'equity-stale' ? stale : OK,
      etf: scenario === 'equity-stale' ? stale : OK,
    }
  }
  const visible = () => assets.filter((a) => !(scenario === 'crypto-down' && a.asset_class === 'crypto'))

  const filtered = (q: string, cls: string) => {
    const norm = normalize(q.trim())
    const rows = visible().filter((a) => {
      if (cls && cls !== 'all' && a.asset_class !== cls) return false
      if (!norm) return true
      return normalize(`${a.symbol}\n${a.name}`).includes(norm)
    })
    const rank = (a: MockAsset) => {
      const sym = normalize(a.symbol)
      if (!norm) return 0
      if (sym === norm || sym.split('/')[0] === norm) return 0
      if (sym.startsWith(norm)) return 1
      if (sym.includes(norm)) return 2
      return 3
    }
    const classRank = { crypto: 0, stock: 1, etf: 2 } as const
    return rows.sort((a, b) => rank(a) - rank(b) || classRank[a.asset_class] - classRank[b.asset_class] || a.symbol.localeCompare(b.symbol))
  }

  const counts = () => {
    const out: Record<string, { total: number | null; eligible: number | null }> = {
      all: { total: 0, eligible: 0 },
      crypto: { total: null, eligible: null },
      stock: { total: 0, eligible: 0 },
      etf: { total: 0, eligible: 0 },
    }
    for (const cls of ['crypto', 'stock', 'etf'] as const) {
      if (cls === 'crypto' && scenario === 'crypto-down') continue
      const rows = assets.filter((a) => a.asset_class === cls)
      out[cls] = { total: rows.length, eligible: rows.filter((a) => a.state === 'tradable').length }
      out.all.total! += rows.length
      out.all.eligible! += rows.filter((a) => a.state === 'tradable').length
    }
    return out
  }

  const json = (route: Route, body: unknown, status = 200) =>
    route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })

  await page.route('**/api/assets/catalog/resolve', async (route) => {
    const body = JSON.parse(route.request().postData() || '{}')
    requests.resolve.push(body)
    const rows = filtered(body.q ?? '', body.class ?? 'all')
    const eligible = rows.filter((a) => a.state === 'tradable')
    await json(route, {
      asset_ids: eligible.map((a) => a.asset_id),
      items: eligible.map((a) => ({ asset_id: a.asset_id, symbol: a.symbol, asset_class: a.asset_class, name: a.name })),
      eligible_total: eligible.length,
      marked_total: rows.length - eligible.length,
      total: rows.length,
    })
  })

  await page.route('**/api/assets/catalog/lookup', async (route) => {
    const body = JSON.parse(route.request().postData() || '{}')
    requests.lookup.push(body)
    const wanted = new Set<string>((body.symbols ?? []).map((s: string) => s.toUpperCase()))
    await json(route, { items: visible().filter((a) => wanted.has(a.symbol)), freshness: freshness() })
  })

  await page.route('**/api/assets/catalog/refresh', async (route) => {
    const body = JSON.parse(route.request().postData() || '{}')
    requests.refresh.push(body)
    scenario = 'ok'
    await json(route, { results: [], freshness: freshness() })
  })

  await page.route('**/api/assets/catalog?**', async (route) => {
    const url = new URL(route.request().url())
    requests.catalog.push(url.search)
    const q = url.searchParams.get('q') ?? ''
    const cls = url.searchParams.get('class') ?? 'all'
    const page_no = Number(url.searchParams.get('page') ?? '1')
    const size = Number(url.searchParams.get('page_size') ?? '6')
    const rows = filtered(q, cls)
    const eligible = rows.filter((a) => a.state === 'tradable').length
    await json(route, {
      items: rows.slice((page_no - 1) * size, page_no * size),
      q,
      class: cls,
      page: page_no,
      page_size: size,
      pages: Math.max(1, Math.ceil(rows.length / size)),
      total: rows.length,
      eligible_total: eligible,
      marked_total: rows.length - eligible,
      counts: counts(),
      freshness: freshness(),
    })
  })

  return {
    assets,
    setScenario(name) {
      scenario = name
    },
    requests,
  }
}
