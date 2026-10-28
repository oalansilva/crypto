import { useEffect, useId, useRef, useState, type KeyboardEvent, type RefObject } from 'react'
import { fetchCatalogPage, type CatalogPage } from '@/lib/assetCatalogApi'
import { CLASS_FILTER_LABEL, isMarked, type CatalogAsset, type ClassFilter } from '@/lib/assetSelection'
import { classLabel, historyLine, type ChoiceHint } from '@/lib/benchmarkComparison'
import './BenchmarkComparison.css'

const FILTERS: ClassFilter[] = ['all', 'crypto', 'stock', 'etf']
const PAGE = 30

export const ICON_WARN = (
    <svg className="b23-ic" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" />
        <path d="M12 9v4" />
        <path d="M12 17h.01" />
    </svg>
)
export const ICON_INFO = (
    <svg className="b23-ic" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 16v-4" />
        <path d="M12 8h.01" />
    </svg>
)
export const ICON_SWITCH = (
    <svg className="b23-ic" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="m16 3 4 4-4 4" />
        <path d="M20 7H4" />
        <path d="m8 21-4-4 4-4" />
        <path d="M4 17h16" />
    </svg>
)
const ICON_SEARCH = (
    <svg className="b23-ic" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.3-4.3" />
    </svg>
)
const ICON_CLOSE = (
    <svg className="b23-ic" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 6 6 18" />
        <path d="m6 6 12 12" />
    </svg>
)

export interface OwnOption {
    symbol: string
    name: string
    hist: string
    asset_class?: string | null
    currency?: string | null
}

export interface ReferencePickerProps {
    title: string
    description: string
    own: OwnOption
    /** `own` ou o símbolo da referência gravada. */
    currentId: string
    /** Símbolos que não entram na lista do catálogo (o próprio ativo já é a primeira opção). */
    exclude?: string[]
    hintsFor: (asset: CatalogAsset) => ChoiceHint[]
    onUse: (symbol: string | null, asset: CatalogAsset | null) => void
    onClose: () => void
    returnFocus: RefObject<HTMLElement | null>
}

/**
 * Seletor "Escolher referência" (card #1123, decisão 3): diálogo modal de escolha única sobre o catálogo
 * (`GET /api/assets/catalog`, mesma busca e mesmos filtros do AssetPicker), com "Próprio ativo · Padrão"
 * no topo, aviso antes da escolha (sem coletar e sem bloquear) e ativo marcado desabilitado com o estado e o
 * motivo do catálogo ligados ao rádio por `aria-describedby`. Foco preso, Esc fecha e o foco volta ao gatilho.
 * Reaproveitado pelo resultado, pelo favorito e pela coluna extra do Decidir.
 */
export function ReferencePicker(props: ReferencePickerProps) {
    const { own, currentId, onClose, onUse, returnFocus, hintsFor } = props
    const uid = useId()
    const [q, setQ] = useState('')
    const [filter, setFilter] = useState<ClassFilter>('all')
    const [items, setItems] = useState<CatalogAsset[]>([])
    const [page, setPage] = useState(1)
    const [pages, setPages] = useState(1)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [picked, setPicked] = useState<string>(currentId || 'own')
    const dialogRef = useRef<HTMLDivElement | null>(null)
    const searchRef = useRef<HTMLInputElement | null>(null)
    const exclude = new Set((props.exclude || []).map((s) => s.toUpperCase()))
    const onCloseRef = useRef(onClose)
    useEffect(() => {
        onCloseRef.current = onClose
    }, [onClose])

    useEffect(() => {
        searchRef.current?.focus()
        const previous = document.body.style.overflow
        document.body.style.overflow = 'hidden'
        const target = returnFocus.current
        // Esc fecha com o foco em qualquer lugar; Tab vindo de fora volta para dentro do diálogo.
        const onDocumentKey = (event: globalThis.KeyboardEvent) => {
            const dialog = dialogRef.current
            if (!dialog || dialog.contains(document.activeElement)) return
            if (event.key === 'Escape') {
                event.preventDefault()
                onCloseRef.current()
            } else if (event.key === 'Tab') {
                event.preventDefault()
                searchRef.current?.focus()
            }
        }
        document.addEventListener('keydown', onDocumentKey)
        return () => {
            document.removeEventListener('keydown', onDocumentKey)
            document.body.style.overflow = previous
            target?.focus()
        }
    }, [returnFocus])

    useEffect(() => {
        const controller = new AbortController()
        setLoading(true)
        setError(null)
        const timer = window.setTimeout(() => {
            fetchCatalogPage({ q, filter, page, pageSize: PAGE }, controller.signal)
                .then((data: CatalogPage) => {
                    setItems((current) => (page === 1 ? data.items : [...current, ...data.items]))
                    setPages(data.pages || 1)
                })
                .catch((err: unknown) => {
                    if ((err as { name?: string })?.name === 'AbortError') return
                    setError(err instanceof Error ? err.message : 'Não foi possível carregar o catálogo de ativos.')
                })
                .finally(() => {
                    if (!controller.signal.aborted) setLoading(false)
                })
        }, page === 1 ? 180 : 0)
        return () => {
            controller.abort()
            window.clearTimeout(timer)
        }
    }, [q, filter, page])

    const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
        if (event.key === 'Escape') {
            event.preventDefault()
            onClose()
            return
        }
        if (event.key !== 'Tab') return
        const nodes = Array.from(
            dialogRef.current?.querySelectorAll<HTMLElement>('button:not([disabled]), input:not([disabled])') ?? [],
        ).filter((el) => {
            if (el instanceof HTMLInputElement && el.type === 'radio') return el.checked
            return el.offsetParent !== null || el === document.activeElement
        })
        if (nodes.length === 0) return
        const first = nodes[0]
        const last = nodes[nodes.length - 1]
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault()
            last.focus()
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault()
            first.focus()
        }
    }

    const visible = items.filter((a) => !exclude.has(a.symbol.toUpperCase()))
    const ownMatches = !q || `${own.symbol} próprio ativo ${own.name}`.toLowerCase().includes(q.toLowerCase())
    const showOwn = ownMatches && (filter === 'all' || !own.asset_class || own.asset_class === filter)
    const titleId = `${uid}-title`
    const descId = `${uid}-desc`
    const ownChip = classLabel(own.asset_class)

    return (
        <div
            className="b23-overlay"
            onMouseDown={(event) => {
                if (event.target === event.currentTarget) onClose()
            }}
        >
            <div
                ref={dialogRef}
                className="b23-dialog"
                role="dialog"
                aria-modal="true"
                aria-labelledby={titleId}
                aria-describedby={descId}
                data-testid="benchmark-dialog"
                onKeyDown={onKeyDown}
            >
                <div className="b23-dlg-head">
                    <h2 id={titleId}>{props.title}</h2>
                    <button type="button" className="b23-icon-btn" aria-label="Fechar" onClick={onClose}>
                        {ICON_CLOSE}
                    </button>
                </div>
                <p id={descId} className="b23-dlg-desc">{props.description}</p>
                <div className="b23-dlg-tools">
                    <label className="b23-search">
                        {ICON_SEARCH}
                        <span className="sr-only-b23">Buscar ativo</span>
                        <input
                            ref={searchRef}
                            type="search"
                            placeholder="Buscar por símbolo ou nome"
                            autoComplete="off"
                            value={q}
                            data-testid="benchmark-search"
                            onChange={(event) => {
                                setQ(event.target.value)
                                setPage(1)
                            }}
                        />
                    </label>
                    <div className="b23-filters" role="group" aria-label="Classe">
                        {FILTERS.map((f) => (
                            <button
                                key={f}
                                type="button"
                                aria-pressed={filter === f}
                                data-testid={`benchmark-filter-${f}`}
                                onClick={() => {
                                    setFilter(f)
                                    setPage(1)
                                }}
                            >
                                {CLASS_FILTER_LABEL[f]}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="b23-list-wrap" role="radiogroup" aria-label="Ativos do catálogo" aria-busy={loading}>
                    <ul className="b23-list">
                        {showOwn ? (
                            <li className="b23-opt" data-testid="benchmark-opt-own">
                                <input
                                    type="radio"
                                    name={`${uid}-ref`}
                                    id={`${uid}-own`}
                                    value="own"
                                    checked={picked === 'own'}
                                    onChange={() => setPicked('own')}
                                />
                                <label htmlFor={`${uid}-own`}>
                                    <span className="b23-opt-main">
                                        <strong>{own.symbol}</strong>
                                        <span className="b23-own-tag">Padrão</span>
                                        {ownChip ? <span className="b23-chip">{ownChip}</span> : null}
                                        {own.currency ? <span className="b23-cur">{own.currency}</span> : null}
                                    </span>
                                    <span className="b23-opt-name">{own.name}</span>
                                    <span className="b23-opt-hist">{own.hist}</span>
                                </label>
                            </li>
                        ) : null}
                        {visible.map((asset) => {
                            const id = `${uid}-r-${asset.asset_id.replace(/[^a-zA-Z0-9]/g, '_')}`
                            const marked = isMarked(asset)
                            const hints = marked ? [] : hintsFor(asset)
                            const reason = `${(asset.state_reason || `${asset.state_label}.`).trim()} Não pode ser escolhido como referência.`
                            return (
                                <li
                                    key={asset.asset_id}
                                    className={`b23-opt${marked ? ' b23-opt-off' : ''}`}
                                    data-testid={`benchmark-opt-${asset.symbol}`}
                                >
                                    <input
                                        type="radio"
                                        name={`${uid}-ref`}
                                        id={id}
                                        value={asset.symbol}
                                        disabled={marked}
                                        aria-describedby={marked ? `${id}-why` : undefined}
                                        checked={picked === asset.symbol}
                                        onChange={() => {
                                            if (!marked) setPicked(asset.symbol)
                                        }}
                                    />
                                    <label htmlFor={id}>
                                        <span className="b23-opt-main">
                                            <strong>{asset.symbol}</strong>
                                            <span className="b23-chip">{classLabel(asset.asset_class)}</span>
                                            <span className="b23-cur">{asset.asset_class === 'crypto' ? asset.symbol.split('/')[1] || 'USDT' : 'USD'}</span>
                                            {marked ? <span className="b23-state-tag">{asset.state_label}</span> : null}
                                        </span>
                                        <span className="b23-opt-name">{asset.name}</span>
                                        <span className="b23-opt-hist">{historyLine(asset)}</span>
                                        {hints.map((hint) => (
                                            <span
                                                key={hint.text}
                                                className={hint.tone === 'warn' ? 'b23-opt-warn' : 'b23-opt-note'}
                                                data-hint={hint.tone}
                                            >
                                                {hint.tone === 'warn' ? ICON_WARN : ICON_INFO}
                                                <span>{hint.text}</span>
                                            </span>
                                        ))}
                                        {marked ? (
                                            <span className="b23-opt-reason" id={`${id}-why`}>{reason}</span>
                                        ) : null}
                                    </label>
                                </li>
                            )
                        })}
                    </ul>
                    {!loading && !error && visible.length === 0 && !showOwn ? (
                        <p className="b23-empty">Nenhum ativo do catálogo com esse texto.</p>
                    ) : null}
                    {error ? <p className="b23-empty" role="alert">{error}</p> : null}
                    {loading ? <p className="b23-empty" role="status">Carregando o catálogo…</p> : null}
                    {!loading && page < pages ? (
                        <button type="button" className="b23-btn b23-more" onClick={() => setPage((p) => p + 1)}>
                            Mostrar mais ativos
                        </button>
                    ) : null}
                </div>
                <div className="b23-dlg-foot">
                    <button type="button" className="b23-btn" onClick={onClose}>Cancelar</button>
                    <button
                        type="button"
                        className="b23-btn b23-primary"
                        data-testid="benchmark-use"
                        onClick={() => onUse(picked === 'own' ? null : picked, items.find((a) => a.symbol === picked) ?? null)}
                    >
                        Usar referência
                    </button>
                </div>
            </div>
        </div>
    )
}
