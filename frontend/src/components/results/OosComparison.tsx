import type { JSX } from 'react'

export interface OosVerdict {
    status?: string
    reasons?: string[]
    warnings?: string[]
    holdout_trades?: number
    execution_mode?: string
    split_train_ratio?: number
}

const VERDICT_STYLES: Record<string, { label: string; className: string }> = {
    GO: { label: 'GO', className: 'border-[#0ecb81]/50 bg-[#0ecb81]/10 text-[#0ecb81]' },
    'NO-GO': { label: 'NO-GO', className: 'border-[#f6465d]/50 bg-[#f6465d]/10 text-[#f6465d]' },
    ERROR: { label: 'Erro no holdout', className: 'border-[#f6465d]/50 bg-[#f6465d]/10 text-[#f6465d]' },
}

const METRIC_ROWS: Array<{ label: string; key: string; format: (v: any) => string }> = [
    { label: 'Retorno total', key: 'total_return', format: (v) => formatPercent(v) },
    { label: 'CAGR', key: 'cagr', format: (v) => formatPercent(v) },
    { label: 'Taxa de acerto', key: 'win_rate', format: (v) => formatPercent(v) },
    { label: 'Sharpe', key: 'sharpe_ratio', format: (v) => formatDecimal(v, 2) },
    { label: 'Drawdown máx.', key: 'max_drawdown', format: (v) => formatPercent(v) },
    { label: 'Profit factor', key: 'profit_factor', format: (v) => formatDecimal(v, 2) },
    { label: 'Calmar', key: 'calmar_ratio', format: (v) => formatDecimal(v, 2) },
    { label: 'Operações', key: 'total_trades', format: (v) => String(v ?? 0) },
]

function formatPercent(value: any): string {
    const n = Number(value)
    if (!Number.isFinite(n)) return '—'
    const pct = Math.abs(n) >= 1 ? n : n * 100
    return `${pct.toFixed(1)}%`
}

function formatDecimal(value: any, digits = 2): string {
    const n = Number(value)
    if (!Number.isFinite(n)) return '—'
    return n.toFixed(digits)
}

export function OosVerdictBadge({ verdict }: { verdict?: OosVerdict | null }): JSX.Element | null {
    if (!verdict?.status) return null
    const status = String(verdict.status).toUpperCase()
    const style = VERDICT_STYLES[status] ?? VERDICT_STYLES['NO-GO']
    return (
        <span
            className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-sm font-bold ${style.className}`}
            data-testid="oos-verdict-badge"
        >
            {style.label}
            {verdict.holdout_trades !== undefined ? (
                <span className="font-normal opacity-80">({verdict.holdout_trades} trades)</span>
            ) : null}
        </span>
    )
}

export function OosMetricsTable({
    trainMetrics,
    oosMetrics,
    verdict,
}: {
    trainMetrics: Record<string, any>
    oosMetrics?: Record<string, any> | null
    verdict?: OosVerdict | null
}): JSX.Element {
    if (!oosMetrics) {
        return (
            <div className="px-5 py-4 text-sm text-[#929aa5]" data-testid="oos-metrics-missing">
                Métricas de validação indisponíveis para esta execução.
            </div>
        )
    }
    const verdictText = (verdict?.reasons ?? []).join(' ') || (verdict?.status ? `Veredito ${verdict.status}` : '')
    const isNoGo = String(verdict?.status ?? '').toUpperCase() !== 'GO'
    return (
        <div className="overflow-x-auto">
            <table className="w-full min-w-[520px] text-left text-sm">
                <thead>
                    <tr className="border-b border-[#2b3139] text-xs uppercase tracking-wide text-[#929aa5]">
                        <th scope="col" className="px-5 py-3 font-semibold">Métrica</th>
                        <th scope="col" className="px-5 py-3 font-semibold">Treino (IS)</th>
                        <th scope="col" className="px-5 py-3 font-semibold">Holdout (OOS)</th>
                        <th scope="col" className="px-5 py-3 font-semibold">Avaliação</th>
                    </tr>
                </thead>
                <tbody>
                    {METRIC_ROWS.map((row) => {
                        const trainValue = row.format(trainMetrics?.[row.key])
                        const oosValue = row.format(oosMetrics[row.key])
                        const tone = row.key === 'total_trades' ? 'text-[#eaecef]' : 'text-[#929aa5]'
                        return (
                            <tr key={row.key} className="border-b border-[#2b3139]/60">
                                <td className="px-5 py-3 text-[#929aa5]">{row.label}</td>
                                <td className="px-5 py-3 font-mono tabular-nums text-[#eaecef]">{trainValue}</td>
                                <td className="px-5 py-3 font-mono tabular-nums text-[#eaecef]">{oosValue}</td>
                                <td className={`px-5 py-3 text-xs ${tone}`}>
                                    {row.key === 'total_trades'
                                        ? (oosMetrics.total_trades >= 0 ? `${oosMetrics.total_trades} trades no holdout` : '—')
                                        : oosMetrics[row.key] === undefined ? '—' : 'OOS'}
                                </td>
                            </tr>
                        )
                    })}
                </tbody>
            </table>
            {verdictText ? (
                <div
                    className={`border-t border-[#2b3139] px-5 py-4 text-sm ${isNoGo ? 'text-[#f6465d]' : 'text-[#0ecb81]'}`}
                    data-testid="oos-verdict-reasons"
                >
                    <strong>{isNoGo ? 'Bloqueado:' : 'Aprovado:'}</strong> {verdictText}
                </div>
            ) : null}
        </div>
    )
}
