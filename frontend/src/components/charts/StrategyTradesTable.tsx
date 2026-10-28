import { Activity, DollarSign, Download, Target, TrendingDown, TrendingUp } from 'lucide-react'
import type { TradeExplanation } from '@/types/tradeExplanation'
import { formatBoundedRatioPercent, formatCompoundReturn } from '@/lib/compoundReturn'
import { nyStamp } from '@/lib/equityExecution'
import '../results/DataExecution.css'

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
    /** Saída com gap (card #1119): preço do stop que a abertura passou. */
    stop_price?: number
    gap_pct?: number
    entry_signal_type?: string
    entry_explanation?: TradeExplanation | null
    exit_explanation?: TradeExplanation | null
    current_state_explanation?: TradeExplanation | null
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
    total_return_pct?: number
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
    /** Card #1123: status do download da planilha (região `polite`). */
    exportStatus?: string
    testId?: string
    showMetrics?: boolean
    /** Moeda da classe em todas as colunas de dinheiro: USDT (cripto, padrão) ou USD (ação e ETF). */
    currency?: string
    /** Intradiário de ação/ETF (15m, 1h, 4h): data e hora de Nova York com o fuso (decisão 18). */
    newYorkClock?: boolean
}

const INITIAL_CAPITAL = 100

function formatDate(dateStr?: string) {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return `${months[date.getUTCMonth()]} ${date.getUTCDate()}, ${date.getUTCFullYear()}`
}

function num(value: number) {
    return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatPrice(price: number | null | undefined, currency: string) {
    if (price === null || price === undefined || Number.isNaN(price)) return '-'
    return `${num(price)} ${currency}`
}

function formatMoney(value: number | null | undefined, currency: string) {
    if (value === null || value === undefined || Number.isNaN(value)) return '-'
    return `${num(value)} ${currency}`
}

function formatPnl(amount: number, pct: number, isPositive: boolean, currency: string) {
    const color = isPositive ? 'text-[#0ecb81]' : 'text-[#f6465d]'
    return (
        <div>
            <span className={color}>{isPositive ? '+' : ''}{num(amount)} {currency}</span>
            <span className={`ml-2 ${color}`}>, {isPositive ? '+' : ''}{pct.toFixed(2)}%</span>
        </div>
    )
}

function isGapExit(trade: StrategyTrade) {
    return trade.exit_reason === 'stop_loss_gap' || trade.signal_type === 'Stop com gap'
}

/** Data (e hora de Nova York no intradiário de ação/ETF) de uma entrada ou saída. */
function DateCell({ iso, newYork }: { iso?: string; newYork: boolean }) {
    if (newYork) {
        const stamp = nyStamp(iso)
        if (stamp) {
            return (
                <>
                    {stamp.date}
                    <span className="r19-time">{stamp.time}</span>
                </>
            )
        }
    }
    return <>{formatDate(iso)}</>
}

/** Intervalo do cartão móvel: "Oct 7, 2026, 11:30 -> Oct 9, 2026, 15:30" com o fuso numa linha. */
function mobileRange(entry: string | undefined, exit: string | undefined, newYork: boolean) {
    if (!newYork) return <>{formatDate(entry)} → {formatDate(exit)}</>
    const a = nyStamp(entry)
    const b = nyStamp(exit)
    if (!a || !b) return <>{formatDate(entry)} → {formatDate(exit)}</>
    const zoneA = a.time.split(' ')[1]
    const zoneB = b.time.split(' ')[1]
    const zone = zoneA === zoneB ? zoneA : `${zoneA} → ${zoneB}`
    return (
        <>
            {a.date}, {a.time.split(' ')[0]} → {b.date}, {b.time.split(' ')[0]}
            <span className="r19-time">Horário de Nova York ({zone})</span>
        </>
    )
}

function resolveSignalType(trade: StrategyTrade, isShort: boolean) {
    if (trade.signal_type) return trade.signal_type
    const exitReason = trade.exit_reason || ''
    if (exitReason.toLowerCase().includes('stop')) return 'Stop de perda'
    if (exitReason) return isShort ? 'Cobrir' : 'Encerrar posição'
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

function deriveMetrics(rows: ReturnType<typeof buildClosedTradeRows>, metrics?: StrategyTradeMetrics | null): StrategyTradeMetrics {
    const wins = rows.filter((trade) => trade.netPnlUSD > 0).length
    const fallbackRatio = rows[0]?.cumulativePnlPct ? rows[0].cumulativePnlPct / 100 : 0
    const totalReturnPct = metrics?.total_return_pct
    return {
        total_trades: Number(metrics?.total_trades ?? rows.length),
        win_rate: Number(metrics?.win_rate ?? (rows.length > 0 ? wins / rows.length : 0)),
        total_return: Number(metrics?.total_return ?? fallbackRatio),
        total_return_pct: totalReturnPct === undefined || totalReturnPct === null || Number.isNaN(Number(totalReturnPct))
            ? undefined
            : Number(totalReturnPct),
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
    exportStatus,
    testId = 'strategy-trades-table',
    showMetrics = true,
    currency = 'USDT',
    newYorkClock = false,
}: StrategyTradesTableProps) {
    const isShort = direction.toLowerCase() === 'short'
    const rows = buildClosedTradeRows(trades, candles, isShort)
    const openTrades = [...trades]
        .filter((trade) => trade.entry_time && (!trade.exit_time || trade.exit_price == null))
        .sort((left, right) => new Date(right.entry_time).getTime() - new Date(left.entry_time).getTime())
    const displayMetrics = deriveMetrics(rows, metrics)
    const returnDisplay = formatCompoundReturn(displayMetrics)

    return (
        <section className="space-y-4" data-testid={testId}>
            {showMetrics ? <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="rounded-lg border border-[#2b3139] bg-[#1e2329] p-5">
                    <div className="mb-3 flex items-center justify-between">
                        <Activity className="h-5 w-5 text-[#fcd535]" />
                        <span className="text-2xl font-bold text-[#eaecef]" data-metric="trades">{displayMetrics.total_trades}</span>
                    </div>
                    <p className="text-sm text-[#929aa5]">Total de operações</p>
                </div>
                <div className="rounded-lg border border-[#2b3139] bg-[#1e2329] p-5">
                    <div className="mb-3 flex items-center justify-between">
                        <Target className="h-5 w-5 text-[#0ecb81]" />
                        <span className="text-2xl font-bold text-[#eaecef]" data-metric="win">{formatBoundedRatioPercent(displayMetrics.win_rate, 2, '0.00%')}</span>
                    </div>
                    <p className="text-sm text-[#929aa5]">Taxa de acerto</p>
                </div>
                <div className="rounded-lg border border-[#2b3139] bg-[#1e2329] p-5">
                    <div className="mb-3 flex items-center justify-between">
                        {returnDisplay.positive ? <TrendingUp className="h-5 w-5 text-[#0ecb81]" /> : <TrendingDown className="h-5 w-5 text-[#f6465d]" />}
                        <span className={`text-2xl font-bold ${returnDisplay.positive ? 'text-[#0ecb81]' : 'text-[#f6465d]'}`} data-metric="return">
                            {returnDisplay.text}
                        </span>
                    </div>
                    <p className="text-sm text-[#929aa5]">Retorno total</p>
                </div>
                <div className="rounded-lg border border-[#2b3139] bg-[#1e2329] p-5">
                    <div className="mb-3 flex items-center justify-between">
                        <DollarSign className="h-5 w-5 text-[#fcd535]" />
                        <span className="text-2xl font-bold text-[#eaecef]" data-metric="avg">{(displayMetrics.avg_profit * 100).toFixed(2)}%</span>
                    </div>
                    <p className="text-sm text-[#929aa5]">Lucro médio</p>
                </div>
            </div> : null}

            <div className="overflow-hidden rounded-lg border border-[#2b3139] bg-[#1e2329]">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#2b3139] bg-[#181a20] p-4">
                    <div className="flex items-center gap-3">
                        <span className="rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-1.5 text-sm font-medium text-[#929aa5]">
                            Métricas
                        </span>
                        <span className="rounded-md border border-[#fcd535] bg-[#fcd535] px-3 py-1.5 text-sm font-semibold text-[#181a20]">
                            Lista de operações
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        {loading ? <span className="text-sm text-[#929aa5]">Carregando trades...</span> : null}
                        {error ? <span className="text-sm text-[#f6465d]">{error}</span> : null}
                        {onExport ? (
                            <button
                                type="button"
                                onClick={onExport}
                                className="inline-flex min-h-11 items-center gap-2 rounded-md bg-[#fcd535] px-4 py-2 text-sm font-semibold text-[#181a20] transition-colors hover:bg-[#f0b90b] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6]"
                            >
                                <Download className="h-4 w-4" />
                                Exportar para Excel
                            </button>
                        ) : null}
                        {onExport ? (
                            <span className="b23-export-status" role="status" aria-live="polite" data-testid="trades-export-status">
                                {exportStatus ?? ''}
                            </span>
                        ) : null}
                    </div>
                </div>
                <div className="space-y-3 bg-[#1e2329] p-3 md:hidden">
                    {openTrades.map((trade, index) => (
                        <article key={`mobile-open-${trade.entry_time}-${index}`} className="rounded-lg border border-[#2b3139] bg-[#181a20] p-3">
                            <div className="flex items-start justify-between gap-3">
                                <div>
                                    <p className="text-xs font-semibold uppercase text-[#0ecb81]">Posição aberta</p>
                                    <p className="mt-1 text-sm font-semibold text-[#eaecef]">{isShort ? 'Venda/Short' : 'Compra'} · <DateCell iso={trade.entry_time} newYork={newYorkClock} /></p>
                                </div>
                                <span className="font-mono text-sm text-[#eaecef]">{formatPrice(trade.entry_price, currency)}</span>
                            </div>
                        </article>
                    ))}
                    {rows.map((trade) => (
                        <article key={`mobile-closed-${trade.tradeNum}`} className="rounded-lg border border-[#2b3139] bg-[#181a20] p-3">
                            <div className="flex items-start justify-between gap-3">
                                <div>
                                    <p className="text-xs font-semibold uppercase text-[#929aa5]">Trade {trade.tradeNum} · encerrado</p>
                                    <p className="mt-1 text-sm text-[#eaecef]">{mobileRange(trade.entry_time, trade.exit_time, newYorkClock)}</p>
                                </div>
                                <span className={trade.netPnlUSD >= 0 ? 'text-[#0ecb81]' : 'text-[#f6465d]'}>{trade.netPnlPct >= 0 ? '+' : ''}{trade.netPnlPct.toFixed(2)}%</span>
                            </div>
                            <dl className="mt-3 grid grid-cols-2 gap-2 text-xs">
                                <div><dt className="text-[#929aa5]">Entrada</dt><dd className="mt-1 text-[#eaecef]">{formatPrice(trade.entry_price, currency)}</dd></div>
                                <div><dt className="text-[#929aa5]">Saída</dt><dd className="mt-1 text-[#eaecef]">{formatPrice(trade.exit_price, currency)}</dd></div>
                            </dl>
                            {isGapExit(trade) && trade.stop_price != null ? (
                                <p className="r19-gap-card" data-testid="trade-gap-card">
                                    <b>Stop com gap</b> · stop {num(trade.stop_price)}, abriu {num(Number(trade.exit_price))}
                                </p>
                            ) : null}
                        </article>
                    ))}
                    {rows.length === 0 && openTrades.length === 0 ? <p className="p-3 text-center text-sm text-[#929aa5]">Nenhuma operação disponível.</p> : null}
                </div>
                <div className="hidden overflow-x-auto bg-[#1e2329] md:block">
                    <table className="w-full text-sm">
                        <thead className="border-b border-[#2b3139] bg-[#181a20]">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Operação <span className="text-[#707a8a]">↓</span></th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Tipo</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">{newYorkClock ? 'Data e hora (Nova York)' : 'Data e hora'}</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Sinal</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Preço</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Valor da posição</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Lucro/Prejuízo</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Máximo favorável</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Máximo adverso</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Resultado acumulado</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[#2b3139] bg-[#1e2329]">
                            {openTrades.map((trade, index) => (
                                <tr key={`open-${trade.entry_time}-${index}`} className="border-b border-[#2b3139] bg-[#1e2329] transition-colors hover:bg-[#2b3139]">
                                    <td className="border-r border-[#2b3139] px-4 py-3 text-center">
                                        <div className="font-medium text-[#eaecef]">{rows.length + openTrades.length - index}</div>
                                        <div className={`text-xs ${isShort ? 'text-[#f0b90b]' : 'text-[#929aa5]'}`}>{isShort ? 'Venda' : 'Compra'}</div>
                                    </td>
                                    <td className="px-4 py-2 text-[#eaecef]">Entrada</td>
                                    <td className="px-4 py-2 text-[#eaecef]"><DateCell iso={trade.entry_time} newYork={newYorkClock} /></td>
                                    <td className="px-4 py-2 text-[#eaecef]">{isShort ? 'Vender' : 'Comprar'}</td>
                                    <td className="px-4 py-2 font-medium text-[#eaecef]">{formatPrice(trade.entry_price, currency)}</td>
                                    <td className="px-4 py-2 text-[#eaecef]">-</td>
                                    <td colSpan={4} className="px-4 py-2 align-top">
                                        <div className="mb-2 font-medium text-[#0ecb81]">Posição aberta</div>
                                    </td>
                                </tr>
                            ))}
                            {rows.length > 0 ? rows.flatMap((trade) => [
                                <tr key={`${trade.tradeNum}-entry`} className="bg-[#1e2329] transition-colors hover:bg-[#2b3139]">
                                    <td rowSpan={2} className="border-r border-[#2b3139] px-4 py-3 text-center">
                                        <div className="font-medium text-[#eaecef]">{trade.tradeNum}</div>
                                        <div className={`text-xs ${isShort ? 'text-[#f0b90b]' : 'text-[#929aa5]'}`}>{isShort ? 'Venda' : 'Compra'}</div>
                                    </td>
                                    <td className="px-4 py-2 text-[#eaecef]">Entrada</td>
                                    <td className="px-4 py-2 text-[#eaecef]"><DateCell iso={trade.entry_time} newYork={newYorkClock} /></td>
                                    <td className="px-4 py-2 text-[#eaecef]">{isShort ? 'Vender' : 'Comprar'}</td>
                                    <td className="px-4 py-2 font-medium text-[#eaecef]">{formatPrice(trade.entry_price, currency)}</td>
                                    <td className="px-4 py-2 text-[#eaecef]">
                                        <div>{formatMoney(trade.positionValueUSD, currency)}</div>
                                    </td>
                                    <td colSpan={4} className="px-4 py-2 align-top" />
                                </tr>,
                                <tr key={`${trade.tradeNum}-exit`} className="border-b border-[#2b3139] bg-[#1e2329] transition-colors hover:bg-[#2b3139]">
                                    <td className="px-4 py-2 text-[#eaecef]">Saida</td>
                                    <td className="px-4 py-2 text-[#eaecef]"><DateCell iso={trade.exit_time} newYork={newYorkClock} /></td>
                                    <td className="px-4 py-2 text-[#eaecef]">
                                        {isGapExit(trade) && trade.stop_price != null ? (
                                            <>
                                                <span className="r19-gap">Stop com gap</span>
                                                <span className="r19-gap-note">stop {num(trade.stop_price)} · abriu {num(Number(trade.exit_price))}</span>
                                            </>
                                        ) : trade.signalType}
                                    </td>
                                    <td className="px-4 py-2 font-medium text-[#eaecef]">{formatPrice(trade.exit_price, currency)}</td>
                                    <td className="px-4 py-2" />
                                    <td className="px-4 py-2">{formatPnl(trade.netPnlUSD, trade.netPnlPct, trade.netPnlUSD >= 0, currency)}</td>
                                    <td className="px-4 py-2 text-[#eaecef]">
                                        <div>{num(trade.favorableExcursionUSD)} {currency}</div>
                                        <div className="text-xs text-[#929aa5]">, {trade.favorableExcursionPct.toFixed(2)}%</div>
                                    </td>
                                    <td className="px-4 py-2 text-[#f6465d]">
                                        <div>-{num(trade.adverseExcursionUSD)} {currency}</div>
                                        <div className="text-xs">, -{trade.adverseExcursionPct.toFixed(2)}%</div>
                                    </td>
                                    <td className="px-4 py-2 text-[#eaecef]">
                                        <div>{num(trade.cumulativePnlUSD)} {currency}</div>
                                        <div className="text-xs text-[#929aa5]">, {trade.cumulativePnlPct.toFixed(2)}%</div>
                                    </td>
                                </tr>,
                            ]) : openTrades.length === 0 ? (
                                <tr>
                                    <td colSpan={10} className="px-4 py-8 text-center text-[#929aa5]">
                                        Sem lista de trades fechados para esta estrategia.
                                    </td>
                                </tr>
                            ) : null}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    )
}
