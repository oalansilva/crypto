import React from 'react'
import { ChevronDown } from 'lucide-react'
import type { TradeEvidenceItem, TradeExplanation } from '@/types/tradeExplanation'
import type { StrategyTransparency } from '@/lib/strategyTransparency'
import { StrategyRuleOverview } from './StrategyRuleOverview'

interface TradeExplanationDisclosureProps {
    id: string
    entry?: TradeExplanation | null
    exit?: TradeExplanation | null
    currentState?: TradeExplanation | null
    strategyTransparency?: StrategyTransparency | null
    direction?: string | null
}

const PRICE_FORMATTER = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 8,
})

const DATE_FORMATTER = new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
    timeZone: 'UTC',
})

function formatDate(value?: string | null) {
    if (!value) return null
    const parsed = new Date(value)
    if (Number.isNaN(parsed.getTime())) return null
    return `${DATE_FORMATTER.format(parsed)} UTC`
}

function formatEvidenceValue(value: string | number | null | undefined) {
    if (value === null || value === undefined || value === '') return null
    if (typeof value === 'number') {
        return new Intl.NumberFormat('en-US', { maximumFractionDigits: 8 }).format(value)
    }
    return value
}

function evidenceState(item: TradeEvidenceItem) {
    const normalized = String(item.state || '').trim().toLowerCase()
    if (normalized === 'confirmed') return 'Confirmada'
    if (normalized === 'pending') return 'Pendente'
    if (normalized === 'reference') return 'Referência'
    return item.state || null
}

function formatTrigger(value?: string | null) {
    const labels: Record<string, string> = {
        entry_rule: 'Regra de entrada',
        exit_rule: 'Regra de saída',
        stop_loss: 'Stop de perda',
        take_profit: 'Objetivo',
        open_position: 'Posição aberta',
    }
    return value ? labels[value] || value.replace(/_/g, ' ') : null
}

function ExplanationBlock({ title, explanation }: { title: string; explanation: TradeExplanation }) {
    const unavailable = explanation.status === 'unavailable' || explanation.status === 'inconsistent'
    const decisionTime = formatDate(explanation.decision_candle_time)
    const executionTime = formatDate(explanation.execution_time)
    const trigger = formatTrigger(explanation.trigger)

    return (
        <section className="rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3" aria-label={title}>
            <div className="flex flex-wrap items-center justify-between gap-2">
                <h4 className="text-sm font-semibold text-[#eaecef]">{title}</h4>
                {explanation.action ? (
                    <span className="rounded-md border border-[#2b3139] bg-[#1e2329] px-2 py-1 text-xs font-semibold text-[#eaecef]">
                        {explanation.action}
                    </span>
                ) : null}
            </div>

            {unavailable ? (
                <p className="mt-2 text-sm text-[#929aa5]">
                    {explanation.unavailable_reason || 'Detalhes da decisão não estão disponíveis para este trade histórico.'}
                </p>
            ) : (
                <>
                    <p className="mt-2 text-sm leading-6 text-[#eaecef]">
                        {explanation.summary || 'A explicação deste evento está parcialmente disponível.'}
                    </p>
                    {explanation.rule_summary || explanation.risk_summary ? (
                        <dl className="mt-3 grid gap-2 sm:grid-cols-2">
                            {explanation.rule_summary ? (
                                <div className="rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-2">
                                    <dt className="text-xs text-[#929aa5]">Saída técnica</dt>
                                    <dd className="mt-1 text-sm leading-6 text-[#eaecef]">{explanation.rule_summary}</dd>
                                </div>
                            ) : null}
                            {explanation.risk_summary ? (
                                <div className="rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-2">
                                    <dt className="text-xs text-[#929aa5]">Stop de proteção</dt>
                                    <dd className="mt-1 text-sm leading-6 text-[#eaecef]">{explanation.risk_summary}</dd>
                                </div>
                            ) : null}
                        </dl>
                    ) : null}
                    <dl className="mt-3 grid gap-2 text-xs sm:grid-cols-2">
                        {trigger ? (
                            <div className="rounded-md bg-[#1e2329] px-3 py-2">
                                <dt className="text-[#929aa5]">Gatilho</dt>
                                <dd className="mt-1 text-[#eaecef]">{trigger}</dd>
                            </div>
                        ) : null}
                        {explanation.timeframe ? (
                            <div className="rounded-md bg-[#1e2329] px-3 py-2">
                                <dt className="text-[#929aa5]">Timeframe</dt>
                                <dd className="mt-1 font-mono text-[#eaecef]">{explanation.timeframe}</dd>
                            </div>
                        ) : null}
                        {decisionTime ? (
                            <div className="rounded-md bg-[#1e2329] px-3 py-2">
                                <dt className="text-[#929aa5]">Candle que confirmou</dt>
                                <dd className="mt-1 font-mono text-[#eaecef]">{decisionTime}</dd>
                            </div>
                        ) : null}
                        {executionTime ? (
                            <div className="rounded-md bg-[#1e2329] px-3 py-2">
                                <dt className="text-[#929aa5]">Execução</dt>
                                <dd className="mt-1 font-mono text-[#eaecef]">{executionTime}</dd>
                            </div>
                        ) : null}
                        {Number.isFinite(explanation.execution_price) ? (
                            <div className="rounded-md bg-[#1e2329] px-3 py-2">
                                <dt className="text-[#929aa5]">Preço executado</dt>
                                <dd className="mt-1 font-mono text-[#eaecef]">{PRICE_FORMATTER.format(Number(explanation.execution_price))}</dd>
                            </div>
                        ) : null}
                    </dl>
                    {explanation.evidence && explanation.evidence.length > 0 ? (
                        <ul className="mt-3 space-y-2" aria-label={`Evidências: ${title}`}>
                            {explanation.evidence.map((item, index) => {
                                const value = formatEvidenceValue(item.value)
                                const timestamp = formatDate(item.timestamp_utc)
                                const state = evidenceState(item)
                                return (
                                    <li key={`${item.key}-${index}`} className="grid min-w-0 gap-1 rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-2 text-xs sm:grid-cols-2">
                                        <span className="min-w-0 break-words text-[#eaecef]">{item.label}</span>
                                        <span className="min-w-0 break-words font-mono text-[#929aa5] sm:text-right">
                                            {[value, state, timestamp].filter(Boolean).join(' · ') || 'Sem valor público'}
                                        </span>
                                    </li>
                                )
                            })}
                        </ul>
                    ) : null}
                </>
            )}
        </section>
    )
}

export function TradeExplanationDisclosure({
    id,
    entry,
    exit,
    currentState,
    strategyTransparency,
    direction,
}: TradeExplanationDisclosureProps) {
    const [expanded, setExpanded] = React.useState(false)
    const panelId = `${id}-trade-explanation`
    const explanations = [
        entry ? { title: 'Por que entrou', explanation: entry } : null,
        exit ? { title: 'Por que saiu', explanation: exit } : null,
        currentState ? { title: 'Por que continua aberto', explanation: currentState } : null,
    ].filter((item): item is { title: string; explanation: TradeExplanation } => item !== null)

    return (
        <div className="min-w-0 max-w-2xl text-left" data-testid={`${id}-trade-explanation-disclosure`}>
            <button
                type="button"
                className="inline-flex min-h-11 w-full items-center justify-between gap-2 rounded-md border border-[#2b3139] bg-[#0b0e11] px-3 py-2 text-sm font-semibold text-[#eaecef] transition hover:border-[#fcd535] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6] sm:w-auto"
                aria-expanded={expanded}
                aria-controls={panelId}
                onClick={() => setExpanded((current) => !current)}
            >
                Entenda este trade
                <ChevronDown className={`h-4 w-4 transition-transform ${expanded ? 'rotate-180' : ''}`} aria-hidden="true" />
            </button>
            {expanded ? (
                <div
                    id={panelId}
                    className="mt-2 space-y-2 rounded-lg border border-[#2b3139] bg-[#1e2329] p-2 sm:p-3"
                    aria-label="Explicação do trade"
                    data-testid={`${id}-trade-explanation-panel`}
                >
                    <StrategyRuleOverview
                        id={`${id}-permanent-rules`}
                        strategyTransparency={strategyTransparency}
                        direction={direction}
                    />
                    {explanations.length > 0 ? explanations.map((item) => (
                        <ExplanationBlock key={item.title} title={item.title} explanation={item.explanation} />
                    )) : (
                        <p className="p-2 text-sm leading-6 text-[#929aa5]">
                            Detalhes da decisão não estão disponíveis para este trade histórico.
                        </p>
                    )}
                </div>
            ) : null}
        </div>
    )
}
