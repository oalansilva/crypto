import React, { useEffect, useMemo, useRef, useState } from 'react'
import { API_BASE_URL } from '@/lib/apiBase'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/use-toast'

type BalanceRow = {
  asset: string
  free: number
  locked: number
  total: number
  price_usdt?: number | null
  value_usd?: number | null
  avg_cost_usdt?: number | null
  pnl_usd?: number | null
  pnl_pct?: number | null
}

type SortKey = 'value' | 'asset' | 'pnl'

type SortSpec = {
  key: SortKey
  dir: 'asc' | 'desc'
}

const fmtUSD = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
})

function fmtNum(n: unknown, max = 8) {
  if (n === null || n === undefined) return '—'
  const v = Number(n)
  if (!Number.isFinite(v)) return '—'
  const s = v.toFixed(max)
  return s.replace(/\.0+$/, '').replace(/(\.[0-9]*?)0+$/, '$1')
}

function formatAsOf(asOf: string | null) {
  if (!asOf) return null
  const d = new Date(asOf)
  if (Number.isNaN(d.getTime())) return asOf
  return d
    .toISOString()
    .replace('T', ' ')
    .replace(/\.\d{3}Z$/, ' UTC')
}

function parseSort(v: string): SortSpec {
  switch (v) {
    case 'value_asc':
      return { key: 'value', dir: 'asc' }
    case 'value_desc':
      return { key: 'value', dir: 'desc' }
    case 'asset_desc':
      return { key: 'asset', dir: 'desc' }
    case 'asset_asc':
      return { key: 'asset', dir: 'asc' }
    case 'pnl_asc':
      return { key: 'pnl', dir: 'asc' }
    case 'pnl_desc':
      return { key: 'pnl', dir: 'desc' }
    default:
      return { key: 'value', dir: 'desc' }
  }
}

function cmp(a: BalanceRow, b: BalanceRow, s: SortSpec) {
  const dir = s.dir === 'asc' ? 1 : -1

  if (s.key === 'asset') return dir * String(a.asset || '').localeCompare(String(b.asset || ''))

  if (s.key === 'pnl') {
    const ap = a.pnl_usd
    const bp = b.pnl_usd
    if (ap == null && bp == null) return 0
    if (ap == null) return 1
    if (bp == null) return -1
    return dir * (Number(ap) - Number(bp))
  }

  const av = Number(a.value_usd)
  const bv = Number(b.value_usd)
  const aHas = Number.isFinite(av)
  const bHas = Number.isFinite(bv)
  if (!aHas && !bHas) return 0
  if (!aHas) return 1
  if (!bHas) return -1
  return dir * (av - bv)
}

export default function ExternalBalancesPage() {
  const { toast } = useToast()

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [balances, setBalances] = useState<BalanceRow[]>([])
  const [serverTotalUsd, setServerTotalUsd] = useState<number | null>(null)
  const [asOf, setAsOf] = useState<string | null>(null)

  const [q, setQ] = useState('')
  const [lockedOnly, setLockedOnly] = useState(false)
  const [minUsd, setMinUsd] = useState<string>('0.02')
  const [sortValue, setSortValue] = useState<string>('value_desc')
  const [sortOverride, setSortOverride] = useState<SortSpec | null>(null)

  const lastFetchId = useRef(0)

  const load = async (opts?: { minUsdOverride?: string }) => {
    const fetchId = ++lastFetchId.current
    setLoading(true)
    setError(null)

    const effectiveMinUsd = String(opts?.minUsdOverride ?? minUsd)
    const min = Number(effectiveMinUsd)
    const qs = new URLSearchParams()
    if (Number.isFinite(min)) qs.set('min_usd', String(min))

    try {
      const res = await fetch(`${API_BASE_URL}/external/binance/spot/balances?${qs.toString()}`)
      const payload = await res.json()
      if (!res.ok) throw new Error(String(payload?.detail || 'Falha ao carregar saldos externos'))
      if (fetchId !== lastFetchId.current) return
      setBalances((payload?.balances || []) as BalanceRow[])
      setServerTotalUsd(typeof payload?.total_usd === 'number' ? payload.total_usd : null)
      setAsOf(typeof payload?.as_of === 'string' ? payload.as_of : null)
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Falha ao carregar saldos.'
      setError(msg)
      toast({ title: 'Erro', description: msg, variant: 'destructive' })
    } finally {
      if (fetchId === lastFetchId.current) setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const t = setTimeout(() => {
      void load()
    }, 320)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [minUsd])

  useEffect(() => {
    const onRefresh = () => {
      void load()
    }
    const onExport = () => {
      const headers = ['asset', 'total', 'free', 'locked', 'value_usd', 'price_usdt', 'pnl_usd', 'pnl_pct']
      const csv = [
        headers.join(','),
        ...view.items.map((row) =>
          [row.asset, row.total, row.free, row.locked, row.value_usd ?? '', row.price_usdt ?? '', row.pnl_usd ?? '', row.pnl_pct ?? '']
            .map((cell) => `"${String(cell ?? '').replaceAll('"', '""')}"`)
            .join(','),
        ),
      ].join('\n')
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'wallet-balances.csv'
      a.click()
      URL.revokeObjectURL(url)
    }

    window.addEventListener('wallet:refresh', onRefresh)
    window.addEventListener('wallet:export', onExport)
    return () => {
      window.removeEventListener('wallet:refresh', onRefresh)
      window.removeEventListener('wallet:export', onExport)
    }
  })

  const view = useMemo(() => {
    const query = q.trim().toLowerCase()
    const min = Number(minUsd)
    const minOk = Number.isFinite(min) ? min : 0

    let items = balances.slice()
    if (query) items = items.filter((it) => String(it.asset || '').toLowerCase().includes(query))
    if (Number.isFinite(min)) {
      items = items.filter((it) => {
        const v = Number(it.value_usd)
        return Number.isFinite(v) ? v >= minOk : false
      })
    }
    if (lockedOnly) items = items.filter((it) => Number(it.locked || 0) > 0)

    const s = sortOverride || parseSort(sortValue)
    items.sort((a, b) => cmp(a, b, s))

    return { items, sort: s, query }
  }, [balances, lockedOnly, minUsd, q, sortOverride, sortValue])

  const summary = useMemo(() => {
    const totalUsd = view.items.reduce((acc, it) => acc + (Number(it.value_usd) || 0), 0)
    const lockedUsd = view.items.reduce((acc, it) => {
      const locked = Number(it.locked) || 0
      const px = Number(it.price_usdt)
      if (!Number.isFinite(px)) return acc
      return acc + locked * px
    }, 0)

    const pnlItems = view.items.filter((it) => typeof it.pnl_usd === 'number')
    const pnlSum = pnlItems.reduce((acc, it) => acc + (Number(it.pnl_usd) || 0), 0)

    return {
      totalUsd,
      lockedUsd,
      pnlSum,
      pnlCount: pnlItems.length,
      count: view.items.length,
    }
  }, [view.items])

  const onHeaderSort = (key: SortKey) => {
    const current = sortOverride || parseSort(sortValue)
    const dir: SortSpec['dir'] = current.key === key && current.dir === 'desc' ? 'asc' : 'desc'
    setSortOverride({ key, dir })
  }

  const reset = () => {
    setQ('')
    setLockedOnly(false)
    setMinUsd('0.02')
    setSortValue('value_desc')
    setSortOverride(null)
    void load({ minUsdOverride: '0.02' })
  }

  const metaLine = useMemo(() => {
    const bits: string[] = []
    bits.push(`min USD: ${Number.isFinite(Number(minUsd)) ? Number(minUsd).toFixed(2) : '—'}`)
    bits.push(`sort: ${view.sort.key}/${view.sort.dir}`)
    if (view.query) bits.unshift(`busca: ${view.query.toUpperCase()}`)
    return bits.join(' · ')
  }, [minUsd, view.query, view.sort.dir, view.sort.key])

  const asOfLabel = formatAsOf(asOf)

  return (
    <main className="w-full">
      <div
        className="pb-10 pt-[18px] sm:pb-12"
        style={{ width: 'min(1120px, calc(100% - 28px))', marginInline: 'auto' }}
      >
        <section className="flex flex-col gap-[14px] border-b border-transparent px-0 pb-[10px] pt-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-[28px] font-bold tracking-[-0.4px] text-white lg:text-[32px]">Carteira</h1>
            <div className="mt-2 flex flex-wrap items-center gap-2.5 text-sm text-white/62">
              <span className="inline-flex items-center rounded-full border border-white/10 bg-white/6 px-3 py-1 text-xs text-white/92">
                Binance Spot
              </span>
              <span className="text-white/44">·</span>
              <span>read-only</span>
              {asOfLabel && (
                <>
                  <span className="text-white/44">·</span>
                  <span>as of {asOfLabel}</span>
                </>
              )}
            </div>
          </div>

          <div className="text-left sm:min-w-[180px] sm:text-right">
            <div className="text-xs text-white/62">Total</div>
            <div className="mt-1 text-[22px] font-extrabold tracking-[-0.2px] text-white lg:text-[24px]">
              {loading ? '—' : fmtUSD.format(summary.totalUsd)}
            </div>
            <div className="mt-0.5 text-xs text-white/62">
              {loading ? '—' : `${summary.count} ativos · filtro min USD ${Number(minUsd).toFixed(2)}`}
            </div>
          </div>
        </section>

        <section className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-3">
          <article className="glass rounded-[14px] p-[14px] shadow-[0_10px_30px_rgba(0,0,0,0.40)]">
            <div className="text-xs text-white/62">Total USD</div>
            <div className="mt-1.5 text-[22px] font-extrabold tracking-[-0.2px] text-white">{loading ? '—' : fmtUSD.format(summary.totalUsd)}</div>
            <div className="mt-1.5 text-xs text-white/62">Soma do valor (USD) das linhas visíveis</div>
          </article>
          <article className="glass rounded-[14px] p-[14px] shadow-[0_10px_30px_rgba(0,0,0,0.40)]">
            <div className="text-xs text-white/62">Locked USD</div>
            <div className="mt-1.5 text-[22px] font-extrabold tracking-[-0.2px] text-white">{loading ? '—' : fmtUSD.format(summary.lockedUsd)}</div>
            <div className="mt-1.5 text-xs text-white/62">Estimado por “locked” × preço</div>
          </article>
          <article className="glass rounded-[14px] p-[14px] shadow-[0_10px_30px_rgba(0,0,0,0.40)]">
            <div className="text-xs text-white/62">PnL (parcial)</div>
            <div className={`mt-1.5 text-[22px] font-extrabold tracking-[-0.2px] ${summary.pnlSum >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
              {loading ? '—' : summary.pnlCount ? fmtUSD.format(summary.pnlSum) : '—'}
              {!loading && summary.pnlCount ? <span className="ml-1 text-sm text-white/72">({summary.pnlCount}/{summary.count})</span> : null}
            </div>
            <div className="mt-1.5 text-xs text-white/62">Apenas para ativos com avg cost / pnl calculados</div>
          </article>
        </section>

        <section className="mt-4">
          <div className="grid grid-cols-1 items-end gap-3 lg:grid-cols-[1.25fr_0.75fr_0.65fr_0.9fr_0.9fr]">
            <label className="grid gap-1.5">
              <span className="text-xs text-white/62">Buscar</span>
              <input
                className="h-11 rounded-[10px] border border-white/10 bg-black/18 px-3 text-white outline-none transition focus:border-[rgba(138,166,255,0.65)] focus:ring-4 focus:ring-[rgba(138,166,255,0.14)]"
                placeholder="BTC, ETH, SOL..."
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
            </label>

            <label className="grid gap-1.5">
              <span className="text-xs text-white/62">Dust threshold</span>
              <div className="grid grid-cols-[1fr_auto] items-center gap-2">
                <input
                  inputMode="decimal"
                  className="h-11 rounded-[10px] border border-white/10 bg-black/18 px-3 font-mono text-white outline-none transition focus:border-[rgba(138,166,255,0.65)] focus:ring-4 focus:ring-[rgba(138,166,255,0.14)]"
                  value={minUsd}
                  onChange={(e) => setMinUsd(e.target.value)}
                />
                <span className="text-xs text-white/62">USD</span>
              </div>
            </label>

            <label className="flex h-11 items-center gap-3 rounded-[10px] border border-white/10 bg-white/5 px-3 text-sm text-white/92">
              <span className={`relative h-[22px] w-[38px] rounded-full border border-white/10 transition ${lockedOnly ? 'bg-[rgba(53,208,127,0.22)] border-[rgba(53,208,127,0.45)]' : 'bg-white/14'}`}>
                <span className={`absolute top-[1px] h-[18px] w-[18px] rounded-full bg-white/86 transition ${lockedOnly ? 'left-[17px]' : 'left-[1px]'}`} />
              </span>
              <input type="checkbox" className="sr-only" checked={lockedOnly} onChange={(e) => setLockedOnly(e.target.checked)} />
              Locked only
            </label>

            <label className="grid gap-1.5">
              <span className="text-xs text-white/62">Ordenar</span>
              <select
                className="h-11 rounded-[10px] border border-white/10 bg-black/18 px-3 text-white outline-none"
                value={sortValue}
                onChange={(e) => {
                  setSortValue(e.target.value)
                  setSortOverride(null)
                }}
              >
                <option value="value_desc">Maior valor</option>
                <option value="value_asc">Menor valor</option>
                <option value="asset_asc">Ativo (A–Z)</option>
                <option value="asset_desc">Ativo (Z–A)</option>
                <option value="pnl_desc">PnL (maior)</option>
                <option value="pnl_asc">PnL (menor)</option>
              </select>
            </label>

            <div className="flex min-h-11 items-center rounded-[10px] border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/75">
              {metaLine}
            </div>
          </div>

          <div className="mt-3 rounded-[14px] border border-amber-400/30 bg-[rgba(255,176,32,0.10)] p-3 text-white/80 shadow-[0_10px_30px_rgba(0,0,0,0.24)]">
            <div className="text-[11px] font-extrabold tracking-wide text-white/92">Nota sobre PnL</div>
            <div className="mt-1 text-sm leading-snug">
              O backend calcula <strong>avg cost / pnl</strong> somente para um número limitado de ativos (budget de tempo). A UI deve sinalizar <strong>parcial</strong> e não sugerir contabilidade completa.
            </div>
          </div>
        </section>

        <section className="mt-4 overflow-hidden rounded-[14px] border border-white/10 bg-[rgba(255,255,255,0.06)] shadow-[0_10px_30px_rgba(0,0,0,0.40)] lg:min-h-[642px]">
          <div className="flex items-start justify-between gap-[14px] border-b border-white/10 bg-[rgba(255,255,255,0.03)] px-[14px] py-[14px]">
            <div>
              <h2 className="text-base font-bold text-white">Balances</h2>
              <div className="mt-1 text-xs text-white/62">Layout responsivo: tabela (desktop) / cards (mobile)</div>
            </div>
            <Button variant="ghost" size="sm" className="rounded-[10px] border border-white/10 bg-white/5 px-[10px] text-xs font-semibold text-white/90 hover:bg-white/10" onClick={reset}>
              Reset filtros
            </Button>
          </div>

          {error && !loading ? (
            <div className="p-4">
              <div className="rounded-[14px] border border-rose-400/30 bg-rose-400/10 p-4">
                <div className="font-bold text-white">Erro ao carregar</div>
                <div className="mt-1 text-sm text-white/75">{error}</div>
                <div className="mt-3">
                  <Button variant="secondary" onClick={() => void load()}>
                    Tentar novamente
                  </Button>
                </div>
              </div>
            </div>
          ) : view.items.length === 0 && !loading ? (
            <div className="p-4">
              <div className="rounded-[14px] border border-white/10 bg-white/5 p-4">
                <div className="font-bold text-white">Nada para mostrar</div>
                <div className="mt-1 text-sm text-white/70">
                  Pode ser que todos os ativos tenham ficado abaixo do min USD, ou que a busca não encontrou nenhum símbolo.
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="hidden md:block lg:min-h-[392px]">
                <div className="grid grid-cols-[140px_1fr_1fr_1fr_1fr_1fr_1fr] gap-[10px] border-b border-white/10 bg-[rgba(10,15,30,0.85)] px-[14px] py-[10px] text-xs text-white/60 backdrop-blur-xl">
                  <button className="text-left hover:text-white/90" onClick={() => onHeaderSort('asset')}>Ativo</button>
                  <div className="text-right">Total</div>
                  <div className="text-right">Free</div>
                  <div className="text-right">Locked</div>
                  <button className="text-right hover:text-white/90" onClick={() => onHeaderSort('value')}>Valor (USD)</button>
                  <div className="text-right">Preço</div>
                  <button className="text-right hover:text-white/90" onClick={() => onHeaderSort('pnl')}>PnL</button>
                </div>

                {(loading ? Array.from({ length: 8 }).map((_, i) => ({ asset: `loading-${i}`, free: 0, locked: 0, total: 0 })) : view.items).map((row: any) => {
                  const locked = Number(row.locked || 0)
                  const value = row.value_usd
                  const price = row.price_usdt
                  const pnlUsd = row.pnl_usd
                  const pnlPct = row.pnl_pct
                  const pnlColor = typeof pnlUsd === 'number' ? (pnlUsd >= 0 ? 'text-emerald-300' : 'text-rose-300') : 'text-white/70'

                  return (
                    <div key={row.asset} className="grid grid-cols-[140px_1fr_1fr_1fr_1fr_1fr_1fr] gap-[10px] border-b border-white/5 px-[14px] py-[10px] text-[13px] leading-[1.2]" style={{ opacity: loading ? 0.7 : 1 }}>
                      <div className="flex items-center gap-[10px]">
                        <div className="grid h-[26px] w-[26px] place-items-center rounded-[9px] border border-white/10 bg-white/5 text-[13px] font-black tracking-[0.4px] text-white">{String(row.asset || '—').slice(0, 1)}</div>
                        <div className="min-w-0">
                          <div className="truncate font-extrabold tracking-[0.2px] text-white">{loading ? '—' : row.asset}</div>
                          <div className="mt-[2px] flex items-center gap-1.5 text-xs text-white/44">
                            {!loading && (
                              <span className="inline-flex rounded-full border border-white/10 bg-white/5 px-2 py-[3px] text-[11px] text-white/78">
                                {locked > 0 ? 'LOCKED' : 'SPOT'}
                              </span>
                            )}
                            <span>{locked > 0 ? `locked: ${fmtNum(locked, 8)}` : 'spot'}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right font-mono text-white/85">{loading ? '—' : fmtNum(row.total, 8)}</div>
                      <div className="text-right font-mono text-white/70">{loading ? '—' : fmtNum(row.free, 8)}</div>
                      <div className={`text-right font-mono ${locked > 0 ? 'font-bold text-amber-300' : 'text-white/70'}`}>{loading ? '—' : fmtNum(row.locked, 8)}</div>
                      <div className="text-right font-mono font-extrabold text-white">{loading ? '—' : typeof value === 'number' ? fmtUSD.format(value) : '—'}</div>
                      <div className="text-right font-mono text-white/70">{loading ? '—' : typeof price === 'number' ? `$${fmtNum(price, 6)}` : '—'}</div>
                      <div className={`text-right font-mono ${pnlColor}`}>
                        {loading ? '—' : typeof pnlUsd === 'number' ? `${fmtUSD.format(pnlUsd)} (${fmtNum(pnlPct, 2)}%)` : '—'}
                      </div>
                    </div>
                  )
                })}
              </div>

              <div className="md:hidden">
                {(loading ? Array.from({ length: 6 }).map((_, i) => ({ asset: `loading-${i}`, free: 0, locked: 0, total: 0 })) : view.items).map((row: any) => {
                  const locked = Number(row.locked || 0)
                  const value = row.value_usd
                  const price = row.price_usdt
                  const pnlUsd = row.pnl_usd
                  const pnlPct = row.pnl_pct
                  const pnlColor = typeof pnlUsd === 'number' ? (pnlUsd >= 0 ? 'text-emerald-300' : 'text-rose-300') : 'text-white/70'

                  return (
                    <div key={row.asset} className="border-b border-white/5 px-[14px] py-3" style={{ opacity: loading ? 0.7 : 1 }}>
                      <div className="flex items-center justify-between gap-[10px]">
                        <div className="flex items-center gap-[10px]">
                          <div className="grid h-[26px] w-[26px] place-items-center rounded-[9px] border border-white/10 bg-white/5 text-[13px] font-black tracking-[0.4px] text-white">{String(row.asset || '—').slice(0, 1)}</div>
                          <div>
                            <div className="font-extrabold tracking-[0.2px] text-white">{loading ? '—' : row.asset}</div>
                            <div className="mt-[2px] text-xs text-white/55">{locked > 0 ? `Locked: ${fmtNum(locked, 8)}` : 'Spot'}</div>
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="font-mono text-[15px] font-extrabold text-white">{loading ? '—' : typeof value === 'number' ? fmtUSD.format(value) : '—'}</div>
                          <div className="mt-[2px] text-xs text-white/62">Total: {loading ? '—' : fmtNum(row.total, 8)}</div>
                        </div>
                      </div>

                      <div className="mt-[10px] grid grid-cols-2 gap-[10px]">
                        <div className="rounded-xl border border-white/10 bg-white/5 p-[10px]">
                          <div className="text-[11px] text-white/60">Preço</div>
                          <div className="mt-1 font-mono text-xs text-white">{loading ? '—' : typeof price === 'number' ? `$${fmtNum(price, 6)}` : '—'}</div>
                        </div>
                        <div className="rounded-xl border border-white/10 bg-white/5 p-[10px]">
                          <div className="text-[11px] text-white/60">PnL</div>
                          <div className={`mt-1 font-mono text-xs ${pnlColor}`}>{loading ? '—' : typeof pnlUsd === 'number' ? `${fmtUSD.format(pnlUsd)} (${fmtNum(pnlPct, 2)}%)` : '—'}</div>
                        </div>
                        <div className="rounded-xl border border-white/10 bg-white/5 p-[10px]">
                          <div className="text-[11px] text-white/60">Free</div>
                          <div className="mt-1 font-mono text-xs text-white">{loading ? '—' : fmtNum(row.free, 8)}</div>
                        </div>
                        <div className="rounded-xl border border-white/10 bg-white/5 p-[10px]">
                          <div className="text-[11px] text-white/60">Locked</div>
                          <div className={`mt-1 font-mono text-xs ${locked > 0 ? 'font-bold text-amber-300' : 'text-white/80'}`}>{loading ? '—' : fmtNum(row.locked, 8)}</div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>

              <div className="flex items-center justify-between gap-3 bg-white/5 p-4 text-xs text-white/60">
                <div>{serverTotalUsd != null ? `total_usd (server): ${fmtUSD.format(serverTotalUsd)}` : `Carteira · ${summary.count} rows visíveis`}</div>
                <div>{asOfLabel ? `as_of ${asOfLabel}` : ''}</div>
              </div>
            </>
          )}
        </section>
      </div>
    </main>
  )
}
