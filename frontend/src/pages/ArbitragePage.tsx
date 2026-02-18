import { useEffect, useMemo, useState } from 'react'

const DEFAULT_EXCHANGES = ['binance', 'okx', 'bybit']
const DEFAULT_SYMBOLS = 'USDT/USDC,USDT/DAI,USDC/DAI'

interface Opportunity {
  buy_exchange: string
  sell_exchange: string
  buy_price: number
  sell_price: number
  spread_pct: number
  timestamp: number
}

interface ApiResponse {
  symbols: string[]
  threshold: number
  exchanges: string[]
  results: Record<string, { spreads: Opportunity[]; opportunities: Opportunity[] }>
}

export default function ArbitragePage() {
  const [symbols, setSymbols] = useState(DEFAULT_SYMBOLS)
  const [threshold, setThreshold] = useState('0.1')
  const [exchanges, setExchanges] = useState(DEFAULT_EXCHANGES.join(','))
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<ApiResponse | null>(null)

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
        <header>
          <h1 className="text-3xl font-bold text-white">Arbitragem CEX ↔ CEX</h1>
          <p className="text-gray-400 mt-1">
            Monitoramento em tempo real de spreads stablecoin via WebSocket (sem execução de trades).
          </p>
        </header>

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
              const spreads = data?.results?.[sym]?.spreads ?? []
              return (
                <div key={sym} className="rounded-xl border border-white/10 overflow-hidden">
                  <div className="px-4 py-3 bg-white/5 flex items-center justify-between">
                    <span className="font-semibold text-white">{sym}</span>
                    <span className="text-xs text-gray-400">{spreads.length} pares</span>
                  </div>
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
