import React from 'react'
import {
    buildStrategyRuleOverview,
    normalizeStrategyTransparency,
    type StrategyTransparency,
} from '@/lib/strategyTransparency'
import { formatStrategyParameterLabel, formatStrategyParameterValue } from '@/lib/strategyParameters'
import { StrategyRuleOverview } from './StrategyRuleOverview'

interface StrategyTransparencyPanelProps {
    strategyTransparency?: StrategyTransparency | Record<string, unknown> | null
    direction?: string | null
    timeframe?: string | null
    id?: string
    compact?: boolean
    fallbackName?: string
}

const formatParticipation = (value: string): string => ({
    entry: 'entrada',
    exit: 'saída',
    risk: 'risco',
}[value] || value)

const formatIndicatorParameters = (parameters: Record<string, unknown>): string => (
    Object.entries(parameters)
        .map(([key, value]) => `${formatStrategyParameterLabel(key)}: ${formatStrategyParameterValue(key, value)}`)
        .join(' · ')
)

export function StrategyTransparencyPanel({
    strategyTransparency,
    direction,
    timeframe,
    id = 'strategy-transparency-panel',
    compact = false,
    fallbackName = 'Estratégia',
}: StrategyTransparencyPanelProps) {
    const transparency = React.useMemo(
        () => normalizeStrategyTransparency(strategyTransparency),
        [strategyTransparency],
    )
    const [detailsOpen, setDetailsOpen] = React.useState(!compact)

    if (!transparency) {
        return (
            <section
                className="min-w-0 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3"
                aria-labelledby={`${id}-title`}
                data-testid={id}
            >
                <h4 id={`${id}-title`} className="text-sm font-semibold text-[#eaecef]">{fallbackName}</h4>
                <p className="mt-2 text-sm leading-6 text-[#929aa5]" role="status">
                    Detalhes funcionais indisponíveis: a configuração executada não pôde ser comprovada.
                </p>
            </section>
        )
    }

    const resolvedDirection = String(direction || transparency.direction || '').toLowerCase()
    const resolvedTimeframe = String(timeframe || transparency.timeframe || '').toLowerCase()
    const timeframeMismatch = Boolean(
        transparency.timeframe && resolvedTimeframe && transparency.timeframe !== resolvedTimeframe,
    )
    const rules = buildStrategyRuleOverview(transparency, resolvedDirection)
    const risk = transparency.logic_blocks.find((block) => block.participation === 'risk')
    const statusMessage = timeframeMismatch
        ? `Detalhes indisponíveis: o manifesto usa ${transparency.timeframe.toUpperCase()} e a tela exibe ${resolvedTimeframe.toUpperCase()}.`
        : transparency.status !== 'available'
            ? `Detalhes indisponíveis${transparency.unavailable_reason ? `: ${transparency.unavailable_reason}` : '.'}`
            : null

    return (
        <section
            className="min-w-0 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3"
            aria-labelledby={`${id}-title`}
            data-testid={id}
        >
            <div className="min-w-0">
                <h4 id={`${id}-title`} className="break-words text-sm font-semibold text-[#eaecef]">
                    {transparency.display_name || fallbackName}
                </h4>
                {transparency.description ? (
                    <p className="mt-1 break-words text-xs leading-5 text-[#929aa5]">{transparency.description}</p>
                ) : null}
                <dl className="mt-3 grid grid-cols-2 gap-2 text-xs sm:grid-cols-3">
                    <div className="rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-2">
                        <dt className="text-[#929aa5]">Direção</dt>
                        <dd className="mt-1 font-semibold text-[#eaecef]">
                            {resolvedDirection === 'short' ? 'Short / venda' : 'Long / compra'}
                        </dd>
                    </div>
                    <div className="rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-2">
                        <dt className="text-[#929aa5]">Timeframe</dt>
                        <dd className="mt-1 font-semibold text-[#eaecef]">{resolvedTimeframe.toUpperCase() || '-'}</dd>
                    </div>
                    <div className="rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-2">
                        <dt className="text-[#929aa5]">Indicadores</dt>
                        <dd className="mt-1 font-semibold text-[#eaecef]">{transparency.indicators.length}</dd>
                    </div>
                </dl>
            </div>

            {statusMessage ? (
                <p className="mt-3 rounded-md border border-[#fcd535]/40 bg-[#fcd535]/10 px-3 py-2 text-sm leading-6 text-[#eaecef]" role="status">
                    {statusMessage}
                </p>
            ) : null}

            <div className="mt-3">
                <StrategyRuleOverview
                    id={`${id}-rules`}
                    strategyTransparency={transparency}
                    direction={resolvedDirection}
                />
            </div>

            <details
                className="mt-3 rounded-md border border-[#2b3139] bg-[#1e2329]"
                open={detailsOpen}
                onToggle={(event) => setDetailsOpen(event.currentTarget.open)}
            >
                <summary className="cursor-pointer px-3 py-3 text-sm font-semibold text-[#eaecef]">
                    {compact ? 'Ver indicadores e parâmetros' : 'Detalhes técnicos comprovados'}
                </summary>
                <div className="space-y-3 border-t border-[#2b3139] p-3">
                    <div>
                        <h5 className="text-xs font-semibold uppercase tracking-wide text-[#929aa5]">Indicadores</h5>
                        {transparency.indicators.length > 0 ? (
                            <ul className="mt-2 grid gap-2 md:grid-cols-2" aria-label="Indicadores da estratégia">
                                {transparency.indicators.map((indicator) => {
                                    const available = !timeframeMismatch
                                        && indicator.availability === 'available'
                                        && indicator.series.length > 0
                                    return (
                                        <li key={indicator.key} className="min-w-0 rounded-md border border-[#2b3139] bg-[#0b0e11] p-3">
                                            <div className="flex items-start gap-2">
                                                <span className="mt-1 h-3 w-3 shrink-0 rounded-full border border-white/20" style={{ backgroundColor: indicator.color }} aria-hidden="true" />
                                                <div className="min-w-0">
                                                    <p className="break-words text-sm font-semibold text-[#eaecef]">{indicator.label}</p>
                                                    {Object.keys(indicator.parameters).length > 0 ? (
                                                        <p className="mt-1 break-words text-xs text-[#929aa5]">
                                                            {formatIndicatorParameters(indicator.parameters)}
                                                        </p>
                                                    ) : null}
                                                    <p className="mt-1 text-xs text-[#929aa5]">
                                                        Painel {indicator.panel} · participação {indicator.participation.map(formatParticipation).join(', ') || 'não declarada'}
                                                    </p>
                                                </div>
                                            </div>
                                            {indicator.function ? <p className="mt-2 text-xs leading-5 text-[#929aa5]">Função: {indicator.function}</p> : null}
                                            <p className={`mt-2 text-xs ${available ? 'text-emerald-300' : 'text-[#fcd535]'}`} role="status">
                                                {available ? 'Série disponível para o timeframe atual.' : `Série indisponível${indicator.unavailable_reason ? `: ${indicator.unavailable_reason}` : '.'}`}
                                            </p>
                                        </li>
                                    )
                                })}
                            </ul>
                        ) : (
                            <p className="mt-2 text-sm text-[#929aa5]" role="status">Nenhum indicador comprovado.</p>
                        )}
                    </div>

                    {Object.keys(transparency.effective_parameters).length > 0 ? (
                        <div>
                            <h5 className="text-xs font-semibold uppercase tracking-wide text-[#929aa5]">Parâmetros efetivos</h5>
                            <dl className="mt-2 grid gap-2 text-xs sm:grid-cols-2">
                                {Object.entries(transparency.effective_parameters).map(([key, value]) => (
                                    <div key={key} className="flex min-w-0 justify-between gap-3 rounded-md bg-[#0b0e11] px-3 py-2">
                                        <dt className="break-words text-[#929aa5]">{formatStrategyParameterLabel(key)}</dt>
                                        <dd className="break-words text-right font-mono text-[#eaecef]">{formatStrategyParameterValue(key, value)}</dd>
                                    </div>
                                ))}
                            </dl>
                        </div>
                    ) : null}

                    {risk ? (
                        <div className="rounded-md border border-[#2b3139] bg-[#0b0e11] px-3 py-2">
                            <h5 className="text-xs font-semibold uppercase tracking-wide text-[#929aa5]">Risco</h5>
                            <p className="mt-1 text-sm leading-6 text-[#eaecef]">{risk.description}</p>
                        </div>
                    ) : null}
                </div>
            </details>
        </section>
    )
}
