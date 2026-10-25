import type { Page, Route } from '@playwright/test'

/**
 * API do lote simulada para os specs do card #1120: preview, criação, andamento por ativo, pausa,
 * retomada, encerramento e lote ativo. Os dados são os do protótipo aprovado (lote 7f3c2a91 com
 * BTC/USDT, NVDA e SPY); o teste controla o tempo com `advance()` e `settle()`.
 */

export const LOTE_ID = '7f3c2a91-0000-4000-8000-000000000001'

export interface SimItem {
  position: number
  symbol: string
  asset_class: 'crypto' | 'stock' | 'etf'
  currency: string
  state: string
  reason: string | null
  progress: string | null
  favorite_id: number | null
  execution: Record<string, unknown> | null
  snapshot_id: string | null
  started_at: string | null
  finished_at: string | null
  collect_kind: 'none' | 'missing' | 'tail'
  needs_collection: Array<{ series: string; role: string; kind: string }>
}

export const INTRABAR = {
  precision_requested: 'intrabar',
  precision_effective: 'intrabar_15m',
  window: { covered: { start: '2017-08-17T00:00:00Z', end: '2026-10-24T00:00:00Z', candles: 3400 } },
}
export const DAILY_NVDA = {
  precision_requested: 'intrabar',
  precision_effective: 'candle',
  intraday_reason: 'coverage',
  intraday_missing: [{ from: '2014-11-11', to: '2026-05-18' }],
  window: { covered: { start: '2014-11-11T05:00:00Z', end: '2026-10-23T04:00:00Z', candles: 3000 } },
}
export const DAILY_SPY = {
  ...DAILY_NVDA,
  intraday_missing: [{ from: '2015-01-02', to: '2026-05-18' }],
  window: { covered: { start: '2015-01-02T05:00:00Z', end: '2026-10-23T04:00:00Z', candles: 2900 } },
}

const CLASS_OF: Record<string, 'crypto' | 'stock' | 'etf'> = { 'BTC/USDT': 'crypto', 'ETH/USDT': 'crypto', 'SOL/USDT': 'crypto', NVDA: 'stock', AAPL: 'stock', SPY: 'etf', QQQ: 'etf' }

export function simItem(position: number, symbol: string, state: string, extra: Partial<SimItem> = {}): SimItem {
  const cls = CLASS_OF[symbol] ?? 'stock'
  return {
    position,
    symbol,
    asset_class: cls,
    currency: cls === 'crypto' ? 'USDT' : 'USD',
    state,
    reason: null,
    progress: null,
    favorite_id: null,
    execution: null,
    snapshot_id: null,
    started_at: null,
    finished_at: null,
    collect_kind: 'none',
    needs_collection: [],
    ...extra,
  }
}

export interface SimJob {
  job_id: string
  status: string
  processed: number
  total: number
  succeeded: number
  failed: number
  skipped: number
  errors: unknown[]
  started_at: string | null
  elapsed_sec: number
  estimated_remaining_sec: number | null
  current_symbol: string | null
  current_stage: string | null
  pause_requested: boolean
  cancel_requested: boolean
  config: Record<string, unknown>
  items: SimItem[]
  totals: Record<string, number>
}

const FINAL = ['success', 'success_daily', 'insufficient', 'rejected', 'failed', 'skipped', 'not_run']

export function buildJob(items: SimItem[], status = 'running', extra: Partial<SimJob> = {}): SimJob {
  const total = items.filter((i) => i.state !== 'out').length
  const processed = items.filter((i) => FINAL.includes(i.state)).length
  const totals: Record<string, number> = {}
  for (const item of items) totals[item.state] = (totals[item.state] ?? 0) + 1
  return {
    job_id: LOTE_ID,
    status,
    processed,
    total,
    succeeded: items.filter((i) => i.state === 'success' || i.state === 'success_daily').length,
    failed: items.filter((i) => i.state === 'failed').length,
    skipped: 0,
    errors: [],
    started_at: '2026-10-24T21:40:00Z',
    elapsed_sec: 48,
    estimated_remaining_sec: 90,
    current_symbol: items.find((i) => i.state === 'collecting' || i.state === 'optimizing')?.symbol ?? null,
    current_stage: null,
    pause_requested: false,
    cancel_requested: false,
    config: { template_name: 'ema_rsi', timeframe: '1d', page: 'combo' },
    items,
    totals,
    ...extra,
  }
}

export function previewItem(symbol: string, plan: 'run' | 'out', extra: Record<string, unknown> = {}) {
  const cls = CLASS_OF[symbol] ?? 'stock'
  return {
    symbol,
    asset_class: cls,
    currency: cls === 'crypto' ? 'USDT' : 'USD',
    plan,
    reason: null,
    out_kind: null,
    needs_collection: [],
    collect_kind: 'none',
    ...extra,
  }
}

export function previewOf(items: Array<ReturnType<typeof previewItem>>, config: Record<string, unknown> = {}) {
  const run = items.filter((i) => i.plan === 'run')
  const needing = run.filter((i) => i.collect_kind !== 'none')
  return {
    items,
    totals: {
      total: items.length,
      run: run.length,
      out: items.length - run.length,
      by_class: {},
      collect: {
        count: needing.length,
        of: run.length,
        missing: needing.filter((i) => i.collect_kind === 'missing').length,
        tail: needing.filter((i) => i.collect_kind === 'tail').length,
      },
    },
    config: { template_name: 'ema_rsi', timeframe: '1d', page: 'combo', ...config },
  }
}

export interface LoteSim {
  /** Estado do servidor simulado; o teste pode ler e trocar. */
  job: SimJob | null
  previewResponse: ReturnType<typeof previewOf>
  /** Itens iniciais do lote quando "Confirmar e rodar" cria o lote. */
  startItems: () => SimItem[]
  calls: Array<{ method: string; path: string; body?: any }>
  /** Troca o job (e o que `GET /active` e `GET /{id}` devolvem). */
  setJob(job: SimJob | null): void
  /** Aplica o pedido de pausa/encerramento: o worker chegou ao fim da etapa. */
  settle(): void
}

export async function installLoteApi(page: Page, init: Partial<Pick<LoteSim, 'previewResponse' | 'startItems' | 'job'>> = {}): Promise<LoteSim> {
  const sim: LoteSim = {
    job: init.job ?? null,
    previewResponse:
      init.previewResponse ??
      previewOf([
        previewItem('BTC/USDT', 'run'),
        previewItem('NVDA', 'run'),
        previewItem('SPY', 'run', {
          collect_kind: 'missing',
          needs_collection: [
            { series: '1d', role: 'candles', kind: 'missing' },
            { series: '5m', role: 'intraday', kind: 'missing' },
          ],
        }),
      ]),
    startItems:
      init.startItems ??
      (() => [
        simItem(0, 'BTC/USDT', 'success', { execution: INTRABAR, favorite_id: 101 }),
        simItem(1, 'NVDA', 'optimizing'),
        simItem(2, 'SPY', 'queued', {
          collect_kind: 'missing',
          needs_collection: [
            { series: '1d', role: 'candles', kind: 'missing' },
            { series: '5m', role: 'intraday', kind: 'missing' },
          ],
        }),
      ]),
    calls: [],
    setJob(job) {
      sim.job = job
    },
    settle() {
      const job = sim.job
      if (!job) return
      if (job.cancel_requested) {
        job.items = job.items.map((i) =>
          ['queued', 'collecting', 'optimizing'].includes(i.state)
            ? { ...i, state: 'not_run', reason: 'lote encerrado antes', progress: null }
            : i,
        )
        Object.assign(job, buildJob(job.items, 'cancelled'), { elapsed_sec: job.elapsed_sec })
      } else if (job.pause_requested) {
        job.items = job.items.map((i) =>
          i.state === 'optimizing' || i.state === 'collecting'
            ? { ...i, state: 'queued', progress: 'histórico coletado; otimiza ao retomar, na mesma amostra.' }
            : i,
        )
        Object.assign(job, buildJob(job.items, 'paused'), { elapsed_sec: job.elapsed_sec })
      }
    },
  }

  const json = (route: Route, body: unknown, status = 200) =>
    route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
  const record = (method: string, path: string, body?: unknown) => sim.calls.push({ method, path, body })

  await page.route('**/api/combos/backtest/batch/preview', async (route) => {
    const body = JSON.parse(route.request().postData() || '{}')
    record('POST', 'preview', body)
    if (sim.job?.status === 'paused') {
      return json(route, { detail: { code: 'batch_paused', job_id: sim.job.job_id, message: 'Retome ou encerre o lote antes de começar outro.' } }, 409)
    }
    await json(route, sim.previewResponse)
  })
  await page.route('**/api/combos/backtest/batch/active', async (route) => {
    record('GET', 'active')
    await json(route, sim.job && !['completed', 'cancelled', 'failed'].includes(sim.job.status) ? sim.job : null)
  })
  await page.route(`**/api/combos/backtest/batch/${LOTE_ID}`, async (route) => {
    record('GET', LOTE_ID)
    await json(route, sim.job ?? {})
  })
  for (const action of ['pause', 'resume', 'cancel'] as const) {
    await page.route(`**/api/combos/backtest/batch/${LOTE_ID}/${action}`, async (route) => {
      record('POST', action)
      const job = sim.job
      if (!job) return json(route, { detail: 'Batch job not found' }, 404)
      if (action === 'pause') job.pause_requested = true
      if (action === 'cancel') {
        if (job.status === 'paused') {
          job.cancel_requested = true
          sim.settle()
        } else {
          job.cancel_requested = true
        }
      }
      if (action === 'resume') {
        job.status = 'running'
        job.pause_requested = false
      }
      await json(route, { status: action })
    })
  }
  await page.route('**/api/combos/backtest/batch', async (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    const body = JSON.parse(route.request().postData() || '{}')
    record('POST', 'batch', body)
    sim.job = buildJob(sim.startItems(), 'running', { config: { template_name: body.template_name, timeframe: body.timeframe, page: body.page } })
    await json(route, { job_id: LOTE_ID })
  })
  return sim
}
