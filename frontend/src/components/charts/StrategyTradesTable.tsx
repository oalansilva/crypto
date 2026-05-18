import { Activity, DollarSign, Download, Target, TrendingDown, TrendingUp } from 'lucide-react'

export interface StrategyTrade {
    entry_time: string
    entry_price: number
    exit_time?: string
    exit_price?: number
    profit?: number
    pnl?: number
    initial_capital?: number
    final_capital?: number
    type?: string
    signal_type?: string
    exit_reason?: string
    entry_signal_type?: string
}

export interface StrategyTradeCandle {
    timestamp_utc: string
    high: number
    low: number
}

export interface StrategyTradeMetrics {
    total_trades?: number
    win_rate?: number
    total_return?: number
    avg_profit?: number
}

interface StrategyTradesTableProps {
    trades: StrategyTrade[]
    candles?: StrategyTradeCandle[]
    direction?: string
    metrics?: StrategyTradeMetrics | null
    loading?: boolean
    error?: string | null
    onExport?: () => void
    testId?: string
}

const INITIAL_CAPITAL = 100

function formatDate(dateStr?: string) {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return `${months[date.getUTCMonth()]} ${date.getUTCDate()}, ${date.getUTCFullYear()}`
}

function formatPrice(price?: number | null) {
    if (price === null || price === undefined || Number.isNaN(price)) return '-'
    return `${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USDT`
}

function formatPnl(usd: number, pct: number, isPositive: boolean) {
    const color = isPositive ? 'text-[#0ecb81]' : 'text-[#f6465d]'
    return (
        <div>
            <span className={color}>{isPositive ? '+' : ''}{usd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</span>
            <span className={`ml-2 ${color}`}>, {isPositive ? '+' : ''}{pct.toFixed(2)}%</span>
        </div>
    )
}

function resolveSignalType(trade: StrategyTrade, isShort: boolean) {
    if (trade.signal_type) return trade.signal_type
    const exitReason = trade.exit_reason || ''
    if (exitReason.toLowerCase().includes('stop')) return 'Stop'
    if (exitReason) return isShort ? 'Cobrir' : 'Close entry(s) order...'
    return trade.entry_signal_type || (isShort ? 'Vender' : 'Comprar')
}

function buildClosedTradeRows(trades: StrategyTrade[], candles: StrategyTradeCandle[] | undefined, isShort: boolean) {
    const sortedTrades = [...trades]
        .filter((trade) => trade.exit_time && trade.exit_price)
        .sort((left, right) => new Date(left.entry_time).getTime() - new Date(right.entry_time).getTime())

    let runningEquity = INITIAL_CAPITAL
    return sortedTrades.map((trade, index) => {
        const entryPrice = Number(trade.entry_price || 0)
        const positionValueUSD = runningEquity
        const positionSize = entryPrice > 0 ? positionValueUSD / entryPrice : 0
        const profitPct = Number(trade.profit ?? (
            trade.pnl !== undefined && trade.initial_capital ? trade.pnl / trade.initial_capital : 0
        ))
        const netPnlUSD = runningEquity * profitPct
        const netPnlPct = profitPct * 100
        let favorableExcursionUSD = 0
        let favorableExcursionPct = 0
        let adverseExcursionUSD = 0
        let adverseExcursionPct = 0

        if (candles && trade.entry_time && trade.exit_time && entryPrice > 0) {
            const entryDate = new Date(trade.entry_time)
            const exitDate = new Date(trade.exit_time)
            const relevantCandles = candles.filter((candle) => {
                const candleDate = new Date(candle.timestamp_utc)
                return candleDate >= entryDate && candleDate <= exitDate
            })

            if (relevantCandles.length > 0) {
                const maxHigh = Math.max(...relevantCandles.map((candle) => candle.high))
                const minLow = Math.min(...relevantCandles.map((candle) => candle.low))
                const favorableMove = isShort ? entryPrice - minLow : maxHigh - entryPrice
                const adverseMove = isShort ? maxHigh - entryPrice : entryPrice - minLow
                favorableExcursionUSD = favorableMove * positionSize
                favorableExcursionPct = (favorableMove / entryPrice) * 100
                adverseExcursionUSD = adverseMove * positionSize
                adverseExcursionPct = (adverseMove / entryPrice) * 100
            }
        }

        runningEquity *= (1 + profitPct)

        return {
            ...trade,
            tradeNum: sortedTrades.length - index,
            signalType: resolveSignalType(trade, isShort),
            positionSize,
            positionValueUSD,
            netPnlUSD,
            netPnlPct,
            favorableExcursionUSD,
            favorableExcursionPct,
            adverseExcursionUSD,
            adverseExcursionPct,
            cumulativePnlUSD: runningEquity - INITIAL_CAPITAL,
            cumulativePnlPct: ((runningEquity / INITIAL_CAPITAL) - 1) * 100,
        }
    }).reverse()
}

function deriveMetrics(rows: ReturnType<typeof buildClosedTradeRows>, metrics?: StrategyTradeMetrics | null): Required<StrategyTradeMetrics> {
    const wins = rows.filter((trade) => trade.netPnlUSD > 0).length
    return {
        total_trades: Number(metrics?.total_trades ?? rows.length),
        win_rate: Number(metrics?.win_rate ?? (rows.length > 0 ? wins / rows.length : 0)),
        total_return: Number(metrics?.total_return ?? (rows[0]?.cumulativePnlPct ? rows[0].cumulativePnlPct / 100 : 0)),
        avg_profit: Number(metrics?.avg_profit ?? (rows.length > 0 && rows[0]?.cumulativePnlPct ? (rows[0].cumulativePnlPct / 100) / rows.length : 0)),
    }
}

export function StrategyTradesTable({
    trades,
    candles,
    direction = 'long',
    metrics,
    loading,
    error,
    onExport,
    testId = 'strategy-trades-table',
}: StrategyTradesTableProps) {
    const isShort = direction.toLowerCase() === 'short'
    const rows = buildClosedTradeRows(trades, candles, isShort)
    const displayMetrics = deriveMetrics(rows, metrics)

    return (
        <section className="space-y-4" data-testid={testId}>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="rounded-lg border border-[#2b3139] bg-[#1e2329] p-5">
                    <div className="mb-3 flex items-center justify-between">
                        <Activity className="h-5 w-5 text-[#fcd535]" />
                        <span className="text-2xl font-bold text-[#eaecef]">{displayMetrics.total_trades}</span>
                    </div>
                    <p className="text-sm text-[#929aa5]">Total Trades</p>
                </div>
                <div className="rounded-lg border border-[#2b3139] bg-[#1e2329] p-5">
                    <div className="mb-3 flex items-center justify-between">
                        <Target className="h-5 w-5 text-[#0ecb81]" />
                        <span className="text-2xl font-bold text-[#eaecef]">{(displayMetrics.win_rate * 100).toFixed(1)}%</span>
                    </div>
                    <p className="text-sm text-[#929aa5]">Win Rate</p>
                </div>
                <div className="rounded-lg border border-[#2b3139] bg-[#1e2329] p-5">
                    <div className="mb-3 flex items-center justify-between">
                        {displayMetrics.total_return >= 0 ? <TrendingUp className="h-5 w-5 text-[#0ecb81]" /> : <TrendingDown className="h-5 w-5 text-[#f6465d]" />}
                        <span className={`text-2xl font-bold ${displayMetrics.total_return >= 0 ? 'text-[#0ecb81]' : 'text-[#f6465d]'}`}>
                            {(displayMetrics.total_return * 100).toFixed(2)}%
                        </span>
                    </div>
                    <p className="text-sm text-[#929aa5]">Total Return</p>
                </div>
                <div className="rounded-lg border border-[#2b3139] bg-[#1e2329] p-5">
                    <div className="mb-3 flex items-center justify-between">
                        <DollarSign className="h-5 w-5 text-[#fcd535]" />
                        <span className="text-2xl font-bold text-[#eaecef]">{(displayMetrics.avg_profit * 100).toFixed(2)}%</span>
                    </div>
                    <p className="text-sm text-[#929aa5]">Avg Profit</p>
                </div>
            </div>

            <div className="overflow-hidden rounded-lg border border-[#2b3139] bg-[#1e2329]">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#2b3139] bg-[#181a20] p-4">
                    <div className="flex items-center gap-3">
                        <span className="rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-1.5 text-sm font-medium text-[#929aa5]">
                            Metrics
                        </span>
                        <span className="rounded-md border border-[#fcd535] bg-[#fcd535] px-3 py-1.5 text-sm font-semibold text-[#181a20]">
                            List of trades
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        {loading ? <span className="text-sm text-[#929aa5]">Carregando trades...</span> : null}
                        {error ? <span className="text-sm text-[#f6465d]">{error}</span> : null}
                        {onExport ? (
                            <button
                                type="button"
                                onClick={onExport}
                                className="inline-flex items-center gap-2 rounded-md bg-[#fcd535] px-4 py-2 text-sm font-semibold text-[#181a20] transition-colors hover:bg-[#f0b90b]"
                            >
                                <Download className="h-4 w-4" />
                                Exportar para Excel
                            </button>
                        ) : null}
                    </div>
                </div>
                <div className="overflow-x-auto bg-[#1e2329]">
                    <table className="w-full text-sm">
                        <thead className="border-b border-[#2b3139] bg-[#181a20]">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Trade # <span className="text-[#707a8a]">↓</span></th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Type</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Date and time</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Signal</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Price</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Position size</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Net P&L</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Favorable excursion</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Adverse excursion</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Cumulative P&L</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[#2b3139] bg-[#1e2329]">
                            {rows.length > 0 ? rows.flatMap((trade) => [
                                <tr key={`${trade.tradeNum}-entry`} className="bg-[#1e2329] transition-colors hover:bg-[#2b3139]">
                                    <td rowSpan={2} className="border-r border-[#2b3139] px-4 py-3 text-center">
                                        <div className="font-medium text-[#eaecef]">{trade.tradeNum}</div>
                                        <div className={`text-xs ${isShort ? 'text-[#f0b90b]' : 'text-[#929aa5]'}`}>{isShort ? 'Short' : 'Long'}</div>
                                    </td>
                                    <td className="px-4 py-2 text-[#eaecef]">Entry</td>
                                    <td className="px-4 py-2 text-[#eaecef]">{formatDate(trade.entry_time)}</td>
                                    <td className="px-4 py-2 text-[#eaecef]">{isShort ? 'Vender' : 'Comprar'}</td>
                                    <td className="px-4 py-2 font-medium text-[#eaecef]">{formatPrice(trade.entry_price)}</td>
                                    <td className="px-4 py-2 text-[#eaecef]">
                                        <div>{trade.positionSize.toFixed(2)}</div>
                                        <div className="text-xs text-[#929aa5]">{(trade.positionValueUSD / 1000).toFixed(2)} K USD</div>
                                    </td>
                                    <td colSpan={4} className="px-4 py-2" />
                                </tr>,
                                <tr key={`${trade.tradeNum}-exit`} className="border-b border-[#2b3139] bg-[#1e2329] transition-colors hover:bg-[#2b3139]">
                                    <td className="px-4 py-2 text-[#eaecef]">Exit</td>
                                    <td className="px-4 py-2 text-[#eaecef]">{formatDate(trade.exit_time)}</td>
                                    <td className="px-4 py-2 text-[#eaecef]">{trade.signalType}</td>
                                    <td className="px-4 py-2 font-medium text-[#eaecef]">{formatPrice(trade.exit_price)}</td>
                                    <td className="px-4 py-2" />
                                    <td className="px-4 py-2">{formatPnl(trade.netPnlUSD, trade.netPnlPct, trade.netPnlUSD >= 0)}</td>
                                    <td className="px-4 py-2 text-[#eaecef]">
                                        <div>{trade.favorableExcursionUSD.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</div>
                                        <div className="text-xs text-[#929aa5]">, {trade.favorableExcursionPct.toFixed(2)}%</div>
                                    </td>
                                    <td className="px-4 py-2 text-[#f6465d]">
                                        <div>-{trade.adverseExcursionUSD.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</div>
                                        <div className="text-xs">, -{trade.adverseExcursionPct.toFixed(2)}%</div>
                                    </td>
                                    <td className="px-4 py-2 text-[#eaecef]">
                                        <div>{trade.cumulativePnlUSD.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</div>
                                        <div className="text-xs text-[#929aa5]">, {trade.cumulativePnlPct.toFixed(2)}%</div>
                                    </td>
                                </tr>,
                            ]) : (
                                <tr>
                                    <td colSpan={10} className="px-4 py-8 text-center text-[#929aa5]">
                                        Sem lista de trades fechados para esta estrategia.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    )
}
