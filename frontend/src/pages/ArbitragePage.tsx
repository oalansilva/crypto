import { useEffect, useMemo, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { Shuffle, Menu, X, Sparkles, Bookmark, Layers, Wallet, Activity, Kanban } from 'lucide-react'

const DEFAULT_EXCHANGES = ['binance', 'okx', 'bybit']
const DEFAULT_SYMBOLS = 'USDT/USDC,USDT/DAI,USDC/DAI'

interface Opportunity {
  buy_exchange: string
  sell_exchange: string
  buy_price: number
  sell_price: number
  spread_pct: number
  timestamp: number
  meets_threshold?: boolean
}

interface ApiResponse {
  symbols: string[]
  threshold: number
  exchanges: string[]
  results: Record<string, { spreads: Opportunity[]; opportunities: Opportunity[]; error?: string }>
}

export default function ArbitragePage() {
  const [symbols, setSymbols] = useState(DEFAULT_SYMBOLS)
  const [threshold, setThreshold] = useState('0.1')
  const [exchanges, setExchanges] = useState(DEFAULT_EXCHANGES.join(','))
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<ApiResponse | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const query = useMemo(() => {
    const params = new URLSearchParams({
      symbols: symbols.trim() || DEFAULT_SYMBOLS,
      threshold: threshold.trim() || '0',
      exchanges: exchanges.trim() || DEFAULT_EXCHANGES.join(','),
    })
    return `/api/arbitrage/spreads?${params.toString()}`
  }, [symbols, threshold, exchanges])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(query)
      if (!response.ok) {
        const text = await response.text()
        throw new Error(text || 'Erro ao buscar spreads')
      }
      const payload = (await response.json()) as ApiResponse
      setData(payload)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro inesperado')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [query])

  useEffect(() => {
    if (!autoRefresh) return
    const id = setInterval(fetchData, 5000)
    return () => clearInterval(id)
  }, [autoRefresh, query])

  return (
    <main className="container mx-auto px-6 py-10">
      <div className="space-y-6">
        {/* Header with sticky on mobile */}
        <header className="sticky top-0 z-40 -mx-6 px-6 -mt-10 pt-10 pb-4 bg-[rgba(10,15,30,0.95)] backdrop-blur-sm border-b border-white/5 sm:static sm:bg-transparent sm:border-none sm:pt-0 sm:mt-0">
          <div className="flex items-center gap-3">
            {/* Mobile Hamburger */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(true)}
              className="sm:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
              aria-label="Abrir menu"
            >
              <Menu className="w-6 h-6 text-white" />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-white">Arbitragem CEX ↔ CEX</h1>
              <p className="text-gray-400 mt-1">
                Monitoramento em tempo real de spreads stablecoin via WebSocket (sem execução de trades).
              </p>
            </div>
          </div>
        </header>

        {/* Mobile Menu Bottom Sheet */}
        {mobileMenuOpen && (
            <>
                <div 
                    className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm sm:hidden"
                    onClick={() => setMobileMenuOpen(false)}
                />
                <div className="fixed inset-x-0 bottom-0 z-50 bg-[rgba(10,15,30,0.98)] rounded-t-3xl shadow-2xl sm:hidden max-h-[85vh] flex flex-col">
                    <div className="flex justify-center pt-3 pb-1">
                        <div className="w-12 h-1.5 bg-white/20 rounded-full" />
                    </div>
                    <div className="flex items-center justify-between px-4 pb-4 border-b border-white/10">
                        <div className="flex items-center gap-3">
                            <div
                                className="h-3.5 w-3.5 rounded-[4px]"
                                style={{
                                    background: 'linear-gradient(135deg, rgba(138,166,255,1), rgba(53,208,127,1))',
                                    boxShadow: '0 0 0 2px rgba(255,255,255,0.04)',
                                }}
                            />
                            <span className="font-bold text-white">Crypto Backtester</span>
                        </div>
                        <button
                            onClick={() => setMobileMenuOpen(false)}
                            className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                        >
                            <X className="w-5 h-5 text-white/70" />
                        </button>
                    </div>
                    <nav className="p-4 space-y-1 overflow-y-auto">
                        {[
                            { to: '/', label: 'Playground', icon: Sparkles },
                            { to: '/favorites', label: 'Favorites', icon: Bookmark },
                            { to: '/monitor', label: 'Monitor', icon: Activity },
                            { to: '/kanban', label: 'Kanban', icon: Kanban },
                            { to: '/lab', label: 'Lab', icon: Sparkles },
                            { to: '/arbitrage', label: 'Arbitragem', icon: Shuffle, active: true },
                            { to: '/combo/select', label: 'Combo', icon: Layers },
                            { to: '/external/balances', label: 'Carteira', icon: Wallet },
                        ].map(({ to, label, icon: Icon, active }) => (
                            <NavLink
                                key={to}
                                to={to}
                                onClick={() => setMobileMenuOpen(false)}
                                className={`flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all duration-200 ${
                                    active
                                        ? 'text-white bg-[rgba(138,166,255,0.35)] border border-[rgba(138,166,255,0.7)]'
                                        : 'text-white bg-[rgba(255,255,255,0.12)] hover:text-white hover:bg-[rgba(255,255,255,0.2)]'
                                }`}
                            >
                                <Icon className="w-5 h-5" />
                                {label}
                            </NavLink>
                        ))}
                    </nav>
                </div>
            </>
        )}

        <section className="glass-strong rounded-2xl p-6 border border-white/10 space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <label className="flex flex-col gap-2 text-sm text-gray-300">
              Símbolos (csv)
              <input
                value={symbols}
                onChange={(event) => setSymbols(event.target.value)}
                className="rounded-lg bg-white/5 border border-white/10 px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                placeholder="USDT/USDC,USDT/DAI,USDC/DAI"
              />
            </label>
            <label className="flex flex-col gap-2 text-sm text-gray-300">
              Threshold (%)
              <input
                value={threshold}
                onChange={(event) => setThreshold(event.target.value)}
                className="rounded-lg bg-white/5 border border-white/10 px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                placeholder="0.1"
              />
            </label>
            <label className="flex flex-col gap-2 text-sm text-gray-300">
              Exchanges (csv)
              <input
                value={exchanges}
                onChange={(event) => setExchanges(event.target.value)}
                className="rounded-lg bg-white/5 border border-white/10 px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                placeholder="binance,okx,bybit"
              />
            </label>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <button
              onClick={fetchData}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-6 py-2 rounded-lg transition"
            >
              Atualizar
            </button>
            <label className="flex items-center gap-2 text-sm text-gray-300">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(event) => setAutoRefresh(event.target.checked)}
                className="h-4 w-4 rounded border-white/20 bg-white/10 text-emerald-500"
              />
              Auto refresh (5s)
            </label>
            {loading && <span className="text-xs text-gray-400">Carregando...</span>}
            {error && <span className="text-xs text-red-400">{error}</span>}
          </div>
        </section>

        <section className="glass rounded-2xl border border-white/10 overflow-hidden">
          <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">Spreads atuais</h2>
              <p className="text-xs text-gray-400">Exibe todos os pares (mesmo abaixo do threshold).</p>
            </div>
            <span className="text-xs text-gray-400">
              {data?.symbols?.length ?? 0} símbolos
            </span>
          </div>
          <div className="space-y-6 p-6">
            {data?.symbols?.map((sym) => {
              const symbolResult = data?.results?.[sym]
              const spreads = symbolResult?.spreads ?? []
              const symbolError = symbolResult?.error
              return (
                <div key={sym} className="rounded-xl border border-white/10 overflow-hidden">
                  <div className="px-4 py-3 bg-white/5 flex items-center justify-between">
                    <span className="font-semibold text-white">{sym}</span>
                    <span className="text-xs text-gray-400">{spreads.length} pares</span>
                  </div>
                  {symbolError ? (
                    <div className="px-4 py-4 text-sm text-red-400">{symbolError}</div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm text-left text-gray-300">
                        <thead className="text-xs uppercase text-gray-400 border-b border-white/10">
                          <tr>
                            <th className="px-4 py-3">Buy</th>
                            <th className="px-4 py-3">Sell</th>
                            <th className="px-4 py-3">Buy Price</th>
                            <th className="px-4 py-3">Sell Price</th>
                            <th className="px-4 py-3">Spread %</th>
                            <th className="px-4 py-3">Status</th>
                            <th className="px-4 py-3">Timestamp</th>
                          </tr>
                        </thead>
                        <tbody>
                          {spreads.map((item, index) => (
                            <tr key={`${sym}-${item.buy_exchange}-${item.sell_exchange}-${index}`} className="border-b border-white/5">
                              <td className="px-4 py-3 font-semibold text-white">{item.buy_exchange}</td>
                              <td className="px-4 py-3 font-semibold text-white">{item.sell_exchange}</td>
                              <td className="px-4 py-3">{item.buy_price.toFixed(6)}</td>
                              <td className="px-4 py-3">{item.sell_price.toFixed(6)}</td>
                              <td className="px-4 py-3 text-emerald-400 font-semibold">{item.spread_pct.toFixed(4)}</td>
                              <td className="px-4 py-3">
                                {item.meets_threshold ? (
                                  <span className="text-emerald-400 font-semibold">OPORTUNIDADE</span>
                                ) : (
                                  <span className="text-gray-500">abaixo do threshold</span>
                                )}
                              </td>
                              <td className="px-4 py-3 text-gray-400">
                                {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : '-'}
                              </td>
                            </tr>
                          ))}
                          {!spreads.length && !loading && (
                            <tr>
                              <td colSpan={7} className="px-4 py-6 text-center text-gray-500">
                                Nenhum spread encontrado no momento.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )
            })}
            {!data?.symbols?.length && !loading && (
              <div className="text-center text-gray-500">Nenhum spread encontrado no momento.</div>
            )}
          </div>
        </section>
      </div>
    </main>
  )
}
