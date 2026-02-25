import { useEffect, useMemo, useRef, useState } from 'react'
import { API_BASE_URL } from '@/lib/apiBase'
import { MiniCandlesChart, type MarketCandle } from './MiniCandlesChart'

type Timeframe = '15m' | '1h' | '4h' | '1d'

interface FavoriteItem {
  id: number
  symbol: string
}

interface SymbolCard {
  symbol: string
  assetType: 'crypto' | 'stock'
  favoritesCount: number
}

const TIMEFRAMES: Timeframe[] = ['15m', '1h', '4h', '1d']

function classifyAsset(symbol: string): 'crypto' | 'stock' {
  return symbol.includes('/') ? 'crypto' : 'stock'
}

export function MonitorDashboardTab() {
  const [favorites, setFavorites] = useState<FavoriteItem[]>([])
  const [favoritesLoading, setFavoritesLoading] = useState(false)
  const [favoritesError, setFavoritesError] = useState<string | null>(null)
  const [selectedSymbol, setSelectedSymbol] = useState<string>('')
  const [timeframe, setTimeframe] = useState<Timeframe>('1d')
  const [candles, setCandles] = useState<MarketCandle[]>([])
  const [candlesLoading, setCandlesLoading] = useState(false)
  const [candlesError, setCandlesError] = useState<string | null>(null)

  const candlesCacheRef = useRef<Map<string, MarketCandle[]>>(new Map())

  const symbols = useMemo<SymbolCard[]>(() => {
    const grouped = new Map<string, SymbolCard>()

    // Only include tiered favorites (tier 1/2/3). "No tier" is ignored in the Dashboard.
    const tieredFavorites = favorites.filter((f: any) => [1, 2, 3].includes(Number(f?.tier)))

    for (const fav of tieredFavorites) {
      const key = String((fav as any).symbol || '').trim()
      if (!key) continue
      const row = grouped.get(key)
      if (row) {
        row.favoritesCount += 1
        continue
      }
      grouped.set(key, {
        symbol: key,
        assetType: classifyAsset(key),
        favoritesCount: 1,
      })
    }
    return Array.from(grouped.values()).sort((a, b) => a.symbol.localeCompare(b.symbol))
  }, [favorites])

  useEffect(() => {
    if (!selectedSymbol && symbols.length > 0) {
      setSelectedSymbol(symbols[0].symbol)
    } else if (selectedSymbol && !symbols.some((s) => s.symbol === selectedSymbol)) {
      setSelectedSymbol(symbols[0]?.symbol || '')
    }
  }, [selectedSymbol, symbols])

  useEffect(() => {
    const controller = new AbortController()
    const run = async () => {
      setFavoritesLoading(true)
      setFavoritesError(null)
      try {
        const response = await fetch(`${API_BASE_URL}/favorites/`, { signal: controller.signal })
        if (!response.ok) {
          throw new Error(`Failed to load favorites (${response.status})`)
        }
        const data = await response.json()
        setFavorites(Array.isArray(data) ? data : [])
      } catch (error) {
        if (!controller.signal.aborted) {
          setFavoritesError(error instanceof Error ? error.message : 'Failed to load favorites')
        }
      } finally {
        if (!controller.signal.aborted) {
          setFavoritesLoading(false)
        }
      }
    }
    run()
    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (!selectedSymbol) {
      setCandles([])
      setCandlesError(null)
      return
    }

    const key = `${selectedSymbol}|${timeframe}`
    const cached = candlesCacheRef.current.get(key)
    if (cached) {
      setCandles(cached)
      setCandlesError(null)
      return
    }

    const controller = new AbortController()
    const run = async () => {
      setCandlesLoading(true)
      setCandlesError(null)
      try {
        const url = new URL(`${API_BASE_URL}/market/candles`, window.location.origin)
        url.searchParams.set('symbol', selectedSymbol)
        url.searchParams.set('timeframe', timeframe)
        url.searchParams.set('limit', '300')
        const response = await fetch(url.toString(), { signal: controller.signal })
        const payload = await response.json()
        if (!response.ok) {
          throw new Error(String(payload?.detail || `Failed to load candles (${response.status})`))
        }
        const rows = Array.isArray(payload?.candles) ? payload.candles : []
        candlesCacheRef.current.set(key, rows)
        setCandles(rows)
      } catch (error) {
        if (!controller.signal.aborted) {
          setCandles([])
          setCandlesError(error instanceof Error ? error.message : 'Failed to load candles')
        }
      } finally {
        if (!controller.signal.aborted) {
          setCandlesLoading(false)
        }
      }
    }
    run()
    return () => controller.abort()
  }, [selectedSymbol, timeframe])

  const selectedMeta = symbols.find((s) => s.symbol === selectedSymbol) || null
  const isStock = (selectedMeta?.assetType ?? classifyAsset(selectedSymbol)) === 'stock'
  const lastClose = candles.length > 0 ? candles[candles.length - 1].close : null
  const previousClose = candles.length > 1 ? candles[candles.length - 2].close : null
  const changePct = lastClose && previousClose ? ((lastClose - previousClose) / previousClose) * 100 : null

  return (
    <section className="space-y-4 max-w-full overflow-x-hidden" data-testid="monitor-dashboard-tab">
      <header className="space-y-1">
        <h2 className="text-2xl font-bold text-white">Dashboard</h2>
        <p className="text-sm text-gray-400">Favorites only. Select a symbol to inspect candles by timeframe.</p>
      </header>

      {favoritesLoading ? <p className="text-sm text-gray-400">Loading favorites...</p> : null}
      {favoritesError ? <p className="text-sm text-red-400">{favoritesError}</p> : null}

      {!favoritesLoading && !favoritesError && symbols.length === 0 ? (
        <p className="text-sm text-gray-400">No favorites found. Add favorites to use the dashboard.</p>
      ) : null}

      {symbols.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2" data-testid="dashboard-symbol-list">
          {symbols.map((item) => {
            const active = item.symbol === selectedSymbol
            return (
              <button
                key={item.symbol}
                type="button"
                onClick={() => setSelectedSymbol(item.symbol)}
                className={`w-full rounded-xl border text-left px-3 py-3 min-h-11 transition-colors ${
                  active
                    ? 'border-blue-400 bg-blue-500/15 text-white'
                    : 'border-white/15 bg-white/5 text-gray-200 hover:bg-white/10'
                }`}
                aria-pressed={active}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold">{item.symbol}</span>
                  <span className="text-xs uppercase tracking-wide text-gray-300">{item.assetType}</span>
                </div>
                <p className="text-xs text-gray-400 mt-1">{item.favoritesCount} favorite strategy{item.favoritesCount > 1 ? 'ies' : ''}</p>
              </button>
            )
          })}
        </div>
      ) : null}

      {selectedSymbol ? (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 className="text-lg font-semibold text-white">{selectedSymbol}</h3>
              <p className="text-xs text-gray-400">
                {selectedMeta?.assetType ?? classifyAsset(selectedSymbol)} • {timeframe} • {candles.length} candles
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-300">Last close</p>
              <p className="font-mono text-lg text-white">{lastClose !== null ? lastClose.toFixed(4) : '-'}</p>
              <p className={`text-xs ${changePct !== null && changePct < 0 ? 'text-red-400' : 'text-green-400'}`}>
                {changePct !== null ? `${changePct >= 0 ? '+' : ''}${changePct.toFixed(2)}%` : 'n/a'}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2" role="group" aria-label="Timeframe">
            {TIMEFRAMES.map((tf) => {
              const active = tf === timeframe
              return (
                <button
                  key={tf}
                  type="button"
                  onClick={() => setTimeframe(tf)}
                  disabled={isStock && tf !== '1d'}
                  className={`rounded-lg border px-3 min-h-11 min-w-11 text-sm font-medium transition-colors ${
                    active
                      ? 'border-blue-400 bg-blue-500/20 text-white'
                      : 'border-white/15 bg-white/5 text-gray-200 hover:bg-white/10'
                  } ${isStock && tf !== '1d' ? 'opacity-40 cursor-not-allowed' : ''}`}
                  aria-pressed={active}
                  data-testid={`timeframe-${tf}`}
                >
                  {tf}
                </button>
              )
            })}
          </div>

          {candlesLoading ? <p className="text-sm text-gray-400">Loading candles...</p> : null}
          {candlesError ? <p className="text-sm text-red-400">{candlesError}</p> : null}
          {isStock ? <p className="text-xs text-gray-400">Stocks: intraday (15m/1h/4h) disabled for now. Use 1d.</p> : null}
          {!candlesLoading && !candlesError && candles.length === 0 ? (
            <p className="text-sm text-gray-400">No candle data available for this symbol/timeframe.</p>
          ) : null}
          {!candlesLoading && !candlesError && candles.length > 0 ? <MiniCandlesChart candles={candles} /> : null}
        </div>
      ) : null}
    </section>
  )
}
