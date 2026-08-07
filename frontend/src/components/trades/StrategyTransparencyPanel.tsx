import React from 'react'
import {
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
    showIdentity?: boolean
    showRules?: boolean
    defaultDetailsOpen?: boolean
    detailsLabel?: string
    fallbackParameters?: Record<string, unknown>
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

function EffectiveParameters({ parameters }: { parameters: Record<string, unknown> }) {
    const entries = Object.entries(parameters).filter(([key]) => !key.startsWith('_'))
    if (entries.length === 0) return null

    return (
        <div>
            <h5 className="text-xs font-semibold uppercase tracking-wide text-[#929aa5]">Parâmetros efetivos</h5>
            <dl className="mt-2 grid gap-2 text-xs sm:grid-cols-2">
                {entries.map(([key, value]) => (
                    <div key={key} className="flex min-w-0 justify-between gap-3 rounded-md bg-[#0b0e11] px-3 py-2">
                        <dt className="break-words text-[#929aa5]">{formatStrategyParameterLabel(key)}</dt>
                        <dd className="break-words text-right font-mono text-[#eaecef]">{formatStrategyParameterValue(key, value)}</dd>
                    </div>
                ))}
            </dl>
        </div>
    )
}

export function StrategyTransparencyPanel({
    strategyTransparency,
    direction,
    timeframe,
    id = 'strategy-transparency-panel',
    compact = false,
    fallbackName = 'Estratégia',
    showIdentity = true,
    showRules = true,
    defaultDetailsOpen,
    detailsLabel,
    fallbackParameters = {},
}: StrategyTransparencyPanelProps) {
    const transparency = React.useMemo(
        () => normalizeStrategyTransparency(strategyTransparency),
        [strategyTransparency],
    )
    const [detailsOpen, setDetailsOpen] = React.useState(defaultDetailsOpen ?? !compact)

    if (!transparency) {
        return (
            <section
                className="min-w-0 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3"
                aria-labelledby={`${id}-title`}
                data-testid={id}
            >
                {showIdentity ? (
                    <h4 id={`${id}-title`} className="text-sm font-semibold text-[#eaecef]">{fallbackName}</h4>
                ) : (
                    <h4 id={`${id}-title`} className="sr-only">Detalhes técnicos da estratégia</h4>
                )}
                <details
                    className={`${showIdentity ? 'mt-3 ' : ''}rounded-md border border-[#2b3139] bg-[#1e2329]`}
                    open={detailsOpen}
                    onToggle={(event) => setDetailsOpen(event.currentTarget.open)}
                >
                    <summary className="min-h-11 cursor-pointer rounded-md px-3 py-3 text-sm font-semibold text-[#eaecef] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6]">
                        {detailsLabel || (compact ? 'Ver indicadores e parâmetros' : 'Detalhes técnicos comprovados')}
                    </summary>
                    <div className="space-y-3 border-t border-[#2b3139] p-3">
                        <p className="text-sm leading-6 text-[#929aa5]" role="status">
                            Manifesto técnico completo indisponível; exibindo os parâmetros salvos desta execução.
                        </p>
                        <EffectiveParameters parameters={fallbackParameters} />
                    </div>
                </details>
            </section>
        )
    }

    const resolvedDirection = String(direction || transparency.direction || '').toLowerCase()
    const resolvedTimeframe = String(timeframe || transparency.timeframe || '').toLowerCase()
    const timeframeMismatch = Boolean(
        transparency.timeframe && resolvedTimeframe && transparency.timeframe !== resolvedTimeframe,
    )
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
            {showIdentity ? <div className="min-w-0">
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
            </div> : (
                <h4 id={`${id}-title`} className="sr-only">Detalhes técnicos da estratégia</h4>
            )}

            {statusMessage ? (
                <p className="mt-3 rounded-md border border-[#fcd535]/40 bg-[#fcd535]/10 px-3 py-2 text-sm leading-6 text-[#eaecef]" role="status">
                    {statusMessage}
                </p>
            ) : null}

            {showRules ? <div className="mt-3">
                <StrategyRuleOverview
                    id={`${id}-rules`}
                    strategyTransparency={transparency}
                    direction={resolvedDirection}
                />
            </div> : null}

            <details
                className="mt-3 rounded-md border border-[#2b3139] bg-[#1e2329]"
                open={detailsOpen}
                onToggle={(event) => setDetailsOpen(event.currentTarget.open)}
            >
                <summary className={`${compact ? '' : 'min-h-11 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6] '}cursor-pointer px-3 py-3 text-sm font-semibold text-[#eaecef]`}>
                    {detailsLabel || (compact ? 'Ver indicadores e parâmetros' : 'Detalhes técnicos comprovados')}
                </summary>
                <div className="space-y-3 border-t border-[#2b3139] p-3">
                    <div>
                        <h5 className="text-xs font-semibold uppercase tracking-wide text-[#929aa5]">Indicadores</h5>
                        {transparency.indicators.length > 0 ? (
                            <>
                            {!statusMessage && transparency.indicators.some((indicator) => (
                                timeframeMismatch
                                || indicator.availability !== 'available'
                                || indicator.series.length === 0
                            )) ? (
                                <p className="mt-2 rounded-md border border-[#fcd535]/40 bg-[#fcd535]/10 px-3 py-2 text-sm leading-6 text-[#eaecef]" role="status">
                                    Uma ou mais séries timestampadas ainda não estão disponíveis. A configuração comprovada permanece listada abaixo.
                                </p>
                            ) : null}
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
                                            {available ? (
                                                <p className="mt-2 text-xs text-emerald-300" role="status">Série disponível para o timeframe atual.</p>
                                            ) : null}
                                        </li>
                                    )
                                })}
                            </ul>
                            </>
                        ) : (
                            <p className="mt-2 text-sm text-[#929aa5]" role="status">Nenhum indicador comprovado.</p>
                        )}
                    </div>

                    <EffectiveParameters parameters={transparency.effective_parameters} />
                </div>
            </details>
        </section>
    )
}
