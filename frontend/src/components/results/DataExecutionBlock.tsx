import { useId, useState } from 'react'
import {
    buildExecutionTexts,
    combinationErrorsText,
    toggleMeta,
    type CombinationErrorsInfo,
    type ConventionsInfo,
    type ExecutionInfo,
    type GapTradeLike,
    type ProvenanceInfo,
    type ResultAsset,
} from '@/lib/equityExecution'
import './DataExecution.css'

const ICON_WARN = (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" />
        <path d="M12 9v4" />
        <path d="M12 17h.01" />
    </svg>
)
const ICON_INFO = (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 16v-4" />
        <path d="M12 8h.01" />
    </svg>
)
const ICON_CHEVRON = (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="m6 9 6 6 6-6" />
    </svg>
)

export interface DataExecutionBlockProps {
    combinationErrors?: CombinationErrorsInfo | null
    asset?: ResultAsset | null
    provenance?: ProvenanceInfo | null
    execution?: ExecutionInfo | null
    conventions?: ConventionsInfo | null
    timeframe: string
    /** "Todo o histórico" quando o período escolhido foi `all`. */
    periodAll?: boolean
    trades?: GapTradeLike[]
    page?: 'result' | 'optimize'
    requestedFallback?: { start?: string | null; end?: string | null }
    requestedNote?: string
}

/**
 * Bloco "Dados e execução" (card #1119, decisões 16 e 19): proveniência, faixa de precisão, nota de
 * coleta parcial, 8 fatos e as convenções da execução. De 768 px para cima tudo fica aberto; abaixo, o
 * resumo (precisão e avisos) fica à vista e o resto abre com um toque (`aria-expanded`). Oculto em
 * resultado sem `execution` (favorito ainda não atualizado). Segue o clone `index.html` do protótipo.
 */
export function DataExecutionBlock(props: DataExecutionBlockProps) {
    const { asset, provenance, execution, conventions, timeframe } = props
    const [open, setOpen] = useState(false)
    const uid = useId()
    if (!execution || !execution.precision_effective) return null

    const texts = buildExecutionTexts({
        asset,
        provenance,
        execution,
        conventions,
        timeframe,
        periodAll: props.periodAll,
        gapTrades: props.trades,
        page: props.page,
        requestedFallback: props.requestedFallback,
        requestedNote: props.requestedNote,
    })
    const combinationText = combinationErrorsText(props.combinationErrors)
    const titleId = `${uid}-title`
    const moreId = `${uid}-more`
    const precision = texts.precision

    return (
        <section className="r19-data" aria-labelledby={titleId} data-testid="result-data-execution">
            <div className="r19-head">
                <h2 id={titleId}>Dados e execução</h2>
                <p data-testid="result-provenance">{texts.provenance}</p>
            </div>
            <div className="r19-body">
                {precision ? (
                    <div className="r19-precision" data-tone={precision.tone} role="note" data-testid="result-precision">
                        {precision.tone === 'warn' ? ICON_WARN : ICON_INFO}
                        <div>
                            <strong data-testid="result-precision-title">{precision.title}</strong>
                            <p data-testid="result-precision-text">{precision.text}</p>
                        </div>
                    </div>
                ) : null}
                {combinationText ? (
                    <div className="r19-precision r19-coverage" data-tone="warn" role="note" data-testid="result-combination-errors">
                        {ICON_WARN}
                        <div>
                            <strong>Combinações puladas</strong>
                            <p>{combinationText}. O resultado vem das combinações que funcionaram.</p>
                        </div>
                    </div>
                ) : null}
                {texts.coverage ? (
                    <div className="r19-precision r19-coverage" data-tone="warn" role="note" data-testid="result-coverage">
                        {ICON_WARN}
                        <div>
                            <strong>{texts.coverage.title}</strong>
                            <p>{texts.coverage.text}</p>
                        </div>
                    </div>
                ) : null}
                {texts.alerts.length > 0 ? (
                    <p className="r19-alerts" data-testid="result-alerts">
                        <b>Avisos:</b> <span>{texts.alerts.join(' · ')}</span>
                    </p>
                ) : null}
                <button
                    type="button"
                    className="r19-toggle"
                    aria-expanded={open}
                    aria-controls={moreId}
                    data-testid="result-data-toggle"
                    onClick={() => setOpen((value) => !value)}
                >
                    <span>Fatos e convenções desta execução</span>
                    <span className="r19-toggle-meta">{toggleMeta(texts)}</span>
                    {ICON_CHEVRON}
                </button>
                <div className="r19-more" id={moreId} data-open={open ? 'true' : 'false'} data-testid="result-data-more">
                    <dl className="r19-facts" data-testid="result-facts">
                        {texts.facts.map((fact) => (
                            <div key={fact.key} data-fact={fact.key}>
                                <dt>{fact.label}</dt>
                                <dd>
                                    {fact.value}
                                    {fact.note ? <span>{fact.note}</span> : null}
                                </dd>
                            </div>
                        ))}
                    </dl>
                    <div className="r19-conv" data-testid="result-conventions">
                        <h3>Convenções desta execução</h3>
                        <ul>
                            {texts.conventions.map((item) => (
                                <li key={item.key} data-convention={item.key}>
                                    <b>{item.label}.</b> {item.text}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        </section>
    )
}
