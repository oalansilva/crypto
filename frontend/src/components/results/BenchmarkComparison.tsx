import { useId, useRef, useState } from 'react'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'
import type { CatalogAsset } from '@/lib/assetSelection'
import {
    CURRENCY_NOTE_TITLE,
    PRICE_RETURN_TEXT,
    SECTION_SUBTITLE,
    classLabel,
    commonText,
    fxPair,
    hasTradesOut,
    holdLabel,
    insufficientHelp,
    isPriceNoDividends,
    leftOutText,
    recordedTail,
    recordedWhen,
    referenceName,
    resultChoiceHint,
    sampleText,
    sectionNumbers,
    storedSpan,
    type BenchmarkComparison as Comparison,
} from '@/lib/benchmarkComparison'
import { ICON_INFO, ICON_SWITCH, ICON_WARN, ReferencePicker } from './ReferencePicker'
import './BenchmarkComparison.css'

const ICON_OFF = (
    <svg className="b23-ic" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="m4.9 4.9 14.2 14.2" />
    </svg>
)

export interface BenchmarkStrategyInfo {
    symbol: string
    assetClass?: string | null
    currency: string
    name?: string | null
    direction: string
    window: { start?: string | null; end?: string | null }
}

export interface BenchmarkComparisonProps {
    strategy: BenchmarkStrategyInfo
    comparison: Comparison | null
    /** Erro da gravação padrão ao rodar (a rodada segue sem comparação). */
    initialError?: { message?: string } | null
    owner: 'result' | 'favorite'
    favoriteId?: number | null
    favoriteName?: string | null
    /** Contexto da rodada nova enviado ao servidor na troca (dono `result`). */
    buildContext?: () => Record<string, unknown>
    onRecorded: (payload: Comparison) => void
    /** Favorito da vitrine (de outro dono): mostra a comparação gravada, sem trocar. */
    readOnly?: boolean
}

interface Pending {
    symbol: string
    label: string
    collecting: boolean
}

interface Failure {
    symbol: string | null
    asset: CatalogAsset | null
    message: string
}

/**
 * Seção "Comparação com referência" (card #1123, decisão 2), entre a análise e "Dados e execução", na
 * moldura `r19-data`. Os números vêm só da comparação gravada; durante a gravação ou a coleta nenhum número
 * da referência nova existe no DOM. Layout de `index.html` e `favorite.html` do protótipo aprovado.
 */
export function BenchmarkComparison(props: BenchmarkComparisonProps) {
    const { strategy, comparison, owner } = props
    const uid = useId()
    const triggerRef = useRef<HTMLButtonElement | null>(null)
    const [open, setOpen] = useState(false)
    const [pending, setPending] = useState<Pending | null>(null)
    const [failure, setFailure] = useState<Failure | null>(null)
    const [announce, setAnnounce] = useState('')

    const titleId = `${uid}-title`
    const ctx = { owner, favoriteName: props.favoriteName }
    const record = async (symbol: string | null, asset: CatalogAsset | null) => {
        const target = symbol || strategy.symbol
        const collecting = Boolean(symbol && asset && !storedSpan(asset).from)
        setOpen(false)
        setFailure(null)
        setAnnounce('')
        setPending({ symbol: target, label: symbol ? target : `${strategy.symbol} (próprio ativo)`, collecting })
        try {
            const body =
                owner === 'favorite'
                    ? { owner: 'favorite', favorite_id: props.favoriteId, reference_symbol: symbol }
                    : { owner: 'result', reference_symbol: symbol, context: props.buildContext?.() ?? {} }
            const res = await authFetch(`${API_BASE_URL}/benchmark-comparisons`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            })
            const data = await res.json().catch(() => ({}))
            if (!res.ok) {
                const detail = data?.detail
                const message =
                    (detail && typeof detail === 'object' && detail.message) ||
                    (typeof detail === 'string' ? detail : `Não foi possível gravar a comparação com ${target}.`)
                setFailure({ symbol, asset, message })
                return
            }
            const payload = data as Comparison
            props.onRecorded(payload)
            setAnnounce(
                payload.status === 'valid'
                    ? `Referência trocada para ${symbol ? target : 'o próprio ativo'} e gravada.`
                    : `Referência ${target} gravada sem comparação: ${payload.reason?.code === 'short_overlap' ? 'período comum curto.' : 'histórico insuficiente.'}`,
            )
        } catch {
            setFailure({ symbol, asset, message: `Não foi possível gravar a comparação com ${target}: falha de conexão.` })
        } finally {
            setPending(null)
        }
    }

    const state: 'collecting' | 'unrecorded' | 'valid' | 'insufficient' = pending
        ? 'collecting'
        : !comparison
            ? 'unrecorded'
            : comparison.status === 'valid'
                ? 'valid'
                : 'insufficient'
    const ref = comparison?.reference ?? null
    const numbers = state === 'valid' && comparison ? sectionNumbers(comparison) : null
    const refLabel = pending
        ? pending.label
        : state === 'unrecorded'
            ? `Próprio ativo (${strategy.symbol})`
            : referenceName(ref, strategy.symbol)
    const refClass = pending ? null : state === 'unrecorded' ? strategy.assetClass : ref?.asset_class
    const refCurrency = pending ? null : state === 'unrecorded' ? strategy.currency : ref?.currency
    const previousLabel = comparison
        ? ref?.kind === 'own'
            ? 'o próprio ativo'
            : ref?.symbol
        : 'sem comparação registrada'
    const currentId = ref && ref.kind !== 'own' ? ref.symbol : 'own'
    const showFx = state === 'valid' && comparison?.currency_note

    return (
        <section
            className="r19-data b23"
            aria-labelledby={titleId}
            data-testid="benchmark-comparison"
            data-b23-owner={owner}
            data-b23-state={state}
            data-b23-reason={state === 'insufficient' ? comparison?.reason?.code ?? '' : ''}
        >
            <div className="r19-head">
                <h2 id={titleId}>Comparação com referência</h2>
                <p>{SECTION_SUBTITLE}</p>
            </div>
            <div className="r19-body">
                <div className="b23-top">
                    <div className="b23-ref">
                        <span className="b23-k">Referência</span>
                        <strong data-testid="benchmark-ref-name">{refLabel}</strong>
                        {!pending ? (
                            <span className="b23-ref-meta">
                                {classLabel(refClass) ? <span className="b23-chip">{classLabel(refClass)}</span> : null}
                                {refCurrency ? <span>{refCurrency}</span> : null}
                                <span aria-hidden="true">·</span>
                                <span>{holdLabel(strategy.direction)}</span>
                            </span>
                        ) : null}
                    </div>
                    {props.readOnly ? null : (
                    <button
                        ref={triggerRef}
                        type="button"
                        className="b23-switch"
                        aria-haspopup="dialog"
                        data-testid="benchmark-switch"
                        disabled={Boolean(pending)}
                        onClick={() => setOpen(true)}
                    >
                        {ICON_SWITCH}
                        <span>Trocar referência</span>
                    </button>
                    )}
                </div>
                <div className="b23-live" role="status" aria-live="polite" data-testid="benchmark-live">
                    {pending ? (
                        <>
                            <span className="b23-spin" aria-hidden="true" />
                            <span>
                                {pending.collecting
                                    ? `Coletando histórico de ${pending.symbol} na Binance…`
                                    : `Gravando a comparação com ${pending.symbol}…`}
                            </span>
                        </>
                    ) : announce ? (
                        <span>{announce}</span>
                    ) : null}
                </div>
                {failure ? (
                    <div className="b23-fail" role="alert" data-testid="benchmark-failure">
                        <p>
                            {failure.message} Nada foi gravado: a referência continua {previousLabel}.
                        </p>
                        <button type="button" className="b23-btn" onClick={() => void record(failure.symbol, failure.asset)}>
                            Tentar de novo
                        </button>
                    </div>
                ) : null}
                {state === 'unrecorded' ? (
                    <div className="b23-unrec" data-testid="benchmark-unrecorded">
                        <p>
                            <strong>Comparação não registrada{owner === 'favorite' ? ' para este favorito' : ''}.</strong>{' '}
                            {owner === 'favorite'
                                ? 'Ele foi salvo antes da comparação existir. Nada é calculado ao abrir: escolha a referência ou compare com o próprio ativo.'
                                : `${props.initialError?.message ?? 'A comparação com o próprio ativo não foi gravada nesta rodada.'} Nada é calculado ao abrir: escolha a referência ou compare com o próprio ativo.`}
                        </p>
                        {props.readOnly ? null : (
                            <button type="button" className="b23-btn" onClick={() => void record(null, null)}>
                                Comparar com o próprio ativo
                            </button>
                        )}
                    </div>
                ) : null}
                {state === 'valid' && numbers && comparison ? (
                    <dl className="b23-grid" data-testid="benchmark-grid">
                        <div className="b23-cell">
                            <dt>Estratégia no período comum</dt>
                            <dd>
                                <b data-tone={numbers.sTone} data-testid="benchmark-s-ret">{numbers.sRet}</b>
                                <span>CAGR <span data-testid="benchmark-s-cagr">{numbers.sCagr}</span></span>
                            </dd>
                        </div>
                        <div className="b23-cell">
                            <dt>Referência · <span>{comparison.reference.symbol}</span></dt>
                            <dd>
                                <b data-tone={numbers.rTone} data-testid="benchmark-r-ret">{numbers.rRet}</b>
                                <span>CAGR <span data-testid="benchmark-r-cagr">{numbers.rCagr}</span></span>
                            </dd>
                        </div>
                        <div className="b23-cell">
                            <dt>Diferença de CAGR</dt>
                            <dd>
                                <b data-tone={numbers.deltaTone} data-testid="benchmark-delta">{numbers.delta}</b>
                                <span>{numbers.deltaNote}</span>
                            </dd>
                        </div>
                    </dl>
                ) : null}
                {state === 'insufficient' && comparison ? (
                    <div className="b23-insuf" role="note" data-testid="benchmark-insufficient">
                        {ICON_OFF}
                        <div>
                            <strong>Sem comparação</strong>
                            <p data-testid="benchmark-insufficient-reason">{comparison.reason?.text}</p>
                            <p className="b23-dim">{insufficientHelp(comparison.reason?.code)}</p>
                        </div>
                    </div>
                ) : null}
                {(state === 'valid' || state === 'insufficient') && comparison ? (
                    <ul className="b23-facts">
                        {state === 'valid' ? (
                            <>
                                <li>
                                    <span className="b23-k">Período comum</span>
                                    <span data-testid="benchmark-common">{commonText(comparison.common_window)}</span>
                                </li>
                                <li>
                                    <span className="b23-k">Fora do período comum</span>
                                    <span data-testid="benchmark-left" data-partial={hasTradesOut(comparison) ? 'true' : 'false'}>
                                        {leftOutText(comparison)}
                                    </span>
                                </li>
                            </>
                        ) : null}
                        {isPriceNoDividends(comparison.reference) ? (
                            <li data-testid="benchmark-price">
                                <span className="b23-k">Tipo de retorno</span>
                                <span>{PRICE_RETURN_TEXT}</span>
                            </li>
                        ) : null}
                    </ul>
                ) : null}
                {showFx && comparison ? (
                    <div className="r19-precision b23-fx" data-tone="warn" role="note" data-testid="benchmark-fx">
                        {ICON_WARN}
                        <div>
                            <strong>{CURRENCY_NOTE_TITLE}</strong>
                            <p>
                                A comparação é só em percentual: {fxPair(strategy.symbol, strategy.currency, comparison.reference)}.
                            </p>
                        </div>
                    </div>
                ) : null}
                {(state === 'valid' || state === 'insufficient') && comparison ? (
                    <p className="b23-rec" data-testid="benchmark-recorded">
                        {ICON_INFO}
                        <span>
                            {recordedWhen(comparison, ctx)} Amostra da referência: {sampleText(comparison, owner)}. Abrir ou exportar de novo
                            não recalcula. {recordedTail(ctx)}
                        </span>
                    </p>
                ) : null}
            </div>
            {open ? (
                <ReferencePicker
                    title="Escolher referência"
                    description={
                        owner === 'favorite'
                            ? 'Buy-and-hold de um ativo do catálogo. A comparação é calculada uma vez e gravada neste favorito. Ativo sem histórico guardado é coletado na Binance ao escolher.'
                            : 'Buy-and-hold de um ativo do catálogo. A comparação é calculada uma vez e gravada neste resultado. Ativo sem histórico guardado é coletado na Binance ao escolher.'
                    }
                    own={{
                        symbol: strategy.symbol,
                        name: `Próprio ativo${strategy.name ? ` · ${strategy.name}` : ''}`,
                        hist: 'Buy-and-hold do próprio ativo no período da estratégia',
                        asset_class: strategy.assetClass,
                        currency: strategy.currency,
                    }}
                    currentId={currentId}
                    exclude={[strategy.symbol]}
                    hintsFor={(asset) => {
                        const hint = resultChoiceHint(asset, strategy.window)
                        return hint ? [hint] : []
                    }}
                    onUse={(symbol, asset) => void record(symbol, asset)}
                    onClose={() => setOpen(false)}
                    returnFocus={triggerRef}
                />
            ) : null}
        </section>
    )
}
