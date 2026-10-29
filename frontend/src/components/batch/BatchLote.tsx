import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react'
import {
    Ban,
    ChevronsRight,
    CircleCheck,
    CircleMinus,
    CircleX,
    Clock,
    LoaderCircle,
    Pause,
    Play,
    Square,
    TriangleAlert,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { CLASS_LABEL, fmtInt, type AssetClass } from '../../lib/assetSelection'
import {
    PAGE_STEP,
    PILL,
    STATE_META,
    chipCounts,
    confirmView,
    dailyNote,
    favoritesHref,
    favoritesLinkText,
    filterItems,
    isLegacyJob,
    itemDetail,
    jobView,
    liveLine,
    metaLine,
    outNamesText,
    pausedBlockView,
    savedCount,
    shortId,
    visibleChips,
    type BatchItem,
    type BatchJob,
    type BatchPreview,
    type ChipKey,
    type StateIcon,
} from '../../lib/batchLote'
import type { PendingAction } from '../../hooks/useBatchJob'
import '../../styles/lote.css'

const ICONS: Record<StateIcon, typeof CircleCheck> = {
    ok: CircleCheck,
    warn: TriangleAlert,
    fail: CircleX,
    ban: Ban,
    skip: ChevronsRight,
    out: CircleMinus,
    load: LoaderCircle,
    wait: Clock,
    stop: Square,
}

export function ClassChip({ assetClass }: { assetClass: AssetClass | null }) {
    const key = assetClass ?? 'stock'
    return (
        <span className="lote-cls" data-class={key}>
            {assetClass ? CLASS_LABEL[assetClass] : 'Ação ou ETF'}
        </span>
    )
}

/** O estado do item no vocabulário do protótipo (`daily`, `notrun`) para o CSS. */
const dataState = (item: BatchItem): string =>
    item.state === 'success_daily' ? 'daily' : item.state === 'not_run' ? 'notrun' : item.state

// --------------------------------------------------------------------------------------------------------
// Confirmar lote (painel no fluxo, sem modal)

export interface ConfirmConfig {
    /** "Médias: tendência · 1d · todo o histórico · Long · Deep Backtest (15m)". */
    text: string
}

interface ConfirmProps {
    preview: BatchPreview
    config: ConfirmConfig
    busy: boolean
    onConfirm: () => void
    onBack: () => void
}

export function BatchConfirm({ preview, config, busy, onConfirm, onBack }: ConfirmProps) {
    const view = confirmView(preview)
    const title = useRef<HTMLHeadingElement>(null)
    useEffect(() => {
        title.current?.focus()
    }, [])
    const needs = (
        <>
            <span className="lote-big" data-testid="batch-need-count">{view.collect.headline}</span> {view.collect.detail}
        </>
    )
    return (
        <section
            className="lote-confirm"
            aria-labelledby="lote-confirm-title"
            data-testid="batch-confirm-panel"
        >
            <h3 id="lote-confirm-title" tabIndex={-1} ref={title}>{view.title}</h3>
            <dl>
                <div>
                    <dt>Vão rodar</dt>
                    <dd>
                        <span className="lote-big">{fmtInt(view.run.count)}</span> — {view.run.classes}: {view.run.names}
                    </dd>
                </div>
                <div className="lote-collect">
                    <dt>Precisam de coleta de histórico</dt>
                    <dd>{needs}</dd>
                </div>
                <div>
                    <dt>Ficam fora</dt>
                    <dd data-testid="batch-out">
                        {view.out ? (
                            <span className="lote-out">
                                {outNamesText(view.out)} — {view.outReason}.
                            </span>
                        ) : (
                            'nenhum'
                        )}
                    </dd>
                </div>
                <div>
                    <dt>Configuração</dt>
                    <dd data-testid="batch-config">{config.text}</dd>
                </div>
                <div>
                    <dt>Favoritos</dt>
                    <dd>
                        o melhor de cada ativo, com a nota "gerado em lote"; ativo que já tem favorito no mesmo período e direção é pulado.
                    </dd>
                </div>
            </dl>
            <div className="lote-actions">
                <button
                    type="button"
                    className="lote-btn primary"
                    data-testid="batch-confirm"
                    onClick={onConfirm}
                    disabled={busy}
                >
                    <Play aria-hidden="true" />
                    Confirmar e rodar
                </button>
                <button type="button" className="lote-btn" data-testid="batch-back" onClick={onBack}>
                    Voltar
                </button>
            </div>
        </section>
    )
}

export function BatchConfirmLoading() {
    const title = useRef<HTMLHeadingElement>(null)
    useEffect(() => {
        title.current?.focus()
    }, [])
    return (
        <section className="lote-confirm" aria-labelledby="lote-confirm-title" data-testid="batch-confirm-panel">
            <h3 id="lote-confirm-title" tabIndex={-1} ref={title}>Montando o plano do lote…</h3>
            <p className="lote-block" role="status">
                Conferindo o catálogo e o histórico guardado. Nada é coletado nesta etapa.
            </p>
        </section>
    )
}

export function BatchConfirmError({ message, onBack }: { message: string; onBack: () => void }) {
    const title = useRef<HTMLHeadingElement>(null)
    useEffect(() => {
        title.current?.focus()
    }, [])
    return (
        <section className="lote-confirm" aria-labelledby="lote-confirm-title" data-testid="batch-confirm-panel">
            <h3 id="lote-confirm-title" tabIndex={-1} ref={title}>Não foi possível montar o lote</h3>
            <p className="lote-block" role="alert" data-testid="batch-confirm-error">{message}</p>
            <div className="lote-actions">
                <button type="button" className="lote-btn" data-testid="batch-back" onClick={onBack}>
                    Voltar
                </button>
            </div>
        </section>
    )
}

// --------------------------------------------------------------------------------------------------------
// Lote pausado bloqueia um lote novo (decisão 16)

interface PausedBlockProps {
    job: BatchJob | null
    jobId: string
    onResume: () => void
    onCancel: () => void
    onBack: () => void
}

export function BatchPausedBlock({ job, jobId, onResume, onCancel, onBack }: PausedBlockProps) {
    const view = pausedBlockView({ job_id: jobId }, job ? savedCount(job) : 0)
    const title = useRef<HTMLHeadingElement>(null)
    useEffect(() => {
        title.current?.focus()
    }, [])
    return (
        <section className="lote-confirm" aria-labelledby="lote-confirm-title" data-testid="batch-confirm-panel">
            <h3 id="lote-confirm-title" tabIndex={-1} ref={title}>{view.title}</h3>
            <p className="lote-block" data-testid="batch-paused-block">{view.body}</p>
            <div className="lote-actions">
                <button type="button" className="lote-btn primary" data-testid="batch-block-resume" onClick={onResume}>
                    <Play aria-hidden="true" />
                    {view.resume}
                </button>
                <button type="button" className="lote-btn danger" data-testid="batch-block-cancel" onClick={onCancel}>
                    <Square aria-hidden="true" />
                    {view.cancel}
                </button>
                <button type="button" className="lote-btn" data-testid="batch-back" onClick={onBack}>
                    Voltar
                </button>
            </div>
        </section>
    )
}

// --------------------------------------------------------------------------------------------------------
// Painel do lote, ativo por ativo

export interface BatchPanelHandle {
    focusTitle: () => void
}

interface PanelProps {
    job: BatchJob
    pending: PendingAction
    actionError: string | null
    onPause: () => void
    onResume: () => void
    onCancel: () => void
    showDiscoveryLink?: boolean
}

function ItemRow({ item, job }: { item: BatchItem; job: BatchJob }) {
    const meta = STATE_META[item.state]
    const Icon = ICONS[meta.icon]
    const detail = itemDetail(item, job)
    return (
        <li className="lote-row" data-state={dataState(item)} data-asset={item.symbol}>
            <div className="lote-asset">
                <b>{item.symbol}</b>
                <span>
                    <ClassChip assetClass={item.asset_class} /> · <span className="lote-cur">{item.currency ?? ''}</span>
                </span>
            </div>
            <div className="lote-state">
                <Icon aria-hidden="true" className={meta.icon === 'load' ? 'lote-spin' : undefined} />
                <span>{meta.label}</span>
            </div>
            <div className="lote-detail">
                {detail.kind === 'saved' ? (
                    <>
                        <b>Favorito gravado</b> · {detail.summary} · <Link to={detail.href}>abrir em Favoritos</Link>
                    </>
                ) : detail.kind === 'progress' ? (
                    <>
                        {detail.text}
                        {detail.progress ? (
                            <progress
                                max={detail.progress.max}
                                value={detail.progress.value}
                                aria-label={`Coleta de ${item.symbol}: página ${detail.progress.value} de ${detail.progress.max}`}
                            />
                        ) : null}
                    </>
                ) : (
                    detail.text
                )}
            </div>
        </li>
    )
}

export const BatchPanel = forwardRef<BatchPanelHandle, PanelProps>(function BatchPanel(
    { job, pending, actionError, onPause, onResume, onCancel, showDiscoveryLink = false },
    ref,
) {
    const title = useRef<HTMLHeadingElement>(null)
    const pauseBtn = useRef<HTMLButtonElement>(null)
    const resumeBtn = useRef<HTMLButtonElement>(null)
    const [chip, setChip] = useState<ChipKey>('all')
    const [shown, setShown] = useState(PAGE_STEP)
    const acted = useRef<'pause' | 'cancel' | 'resume' | null>(null)
    const view = jobView(job)

    useImperativeHandle(ref, () => ({ focusTitle: () => title.current?.focus() }))

    // O foco acompanha a ação: pausou -> Retomar; retomou -> Pausar; encerrou -> título do lote.
    useEffect(() => {
        const how = acted.current
        if (view === 'paused' && how === 'pause') {
            resumeBtn.current?.focus()
            acted.current = null
        } else if (view === 'running' && how === 'resume') {
            pauseBtn.current?.focus()
            acted.current = null
        } else if ((view === 'cancelled' || view === 'completed') && how === 'cancel') {
            title.current?.focus()
            acted.current = null
        }
    }, [view])

    useEffect(() => {
        setChip('all')
        setShown(PAGE_STEP)
    }, [job.job_id])

    if (isLegacyJob(job)) return <LegacyBatchSummary job={job} showDiscoveryLink={showDiscoveryLink} />

    const items = job.items ?? []
    const counts = chipCounts(items)
    const chips = visibleChips(counts)
    const filtered = filterItems(items, chip)
    const slice = filtered.slice(0, shown)
    const pill = PILL[view]
    const pausing = view === 'pausing' || pending === 'pause'
    const cancelling = view === 'cancelling' || pending === 'cancel'
    const running = view === 'running' || view === 'pausing' || view === 'cancelling'
    const saved = savedCount(job)
    const daily = items.filter((i) => i.state === 'success_daily').length
    const note = dailyNote(daily)
    const total = job.total
    const pct = total ? Math.round((job.processed / total) * 100) : 0
    const off = (flag: boolean) => (flag ? ({ 'aria-disabled': true } as const) : {})

    return (
        <section className="lote-batch" aria-labelledby="lote-batch-title" data-testid="batch-panel">
            <div className="lote-bhead">
                <h3 id="lote-batch-title" tabIndex={-1} ref={title}>
                    Lote {shortId(job.job_id)}{' '}
                    <span className="lote-pill" data-tone={pill.tone} data-testid="batch-status">{pill.label}</span>
                </h3>
                <p className="lote-bmeta">{metaLine(job)}</p>
            </div>
            <div className="lote-bbody">
                <p className="lote-live" role="status" aria-live="polite" data-testid="batch-live">{liveLine(job)}</p>
                <div
                    className="lote-bar"
                    role="progressbar"
                    aria-label="Ativos concluídos"
                    aria-valuemin={0}
                    aria-valuemax={total}
                    aria-valuenow={job.processed}
                >
                    <span style={{ width: `${pct}%` }} />
                </div>
                {note ? (
                    <p className="lote-note" data-testid="batch-daily-note">
                        <b>{note.title}</b>{note.body}
                    </p>
                ) : null}
                <div className="lote-chips" role="group" aria-label="Filtrar por estado">
                    {chips.map(([key, label]) => (
                        <button
                            key={key}
                            type="button"
                            className="lote-chip"
                            data-chip={key}
                            aria-pressed={chip === key}
                            onClick={() => {
                                setChip(key)
                                setShown(PAGE_STEP)
                            }}
                        >
                            {label} <b>{fmtInt(counts[key])}</b>
                        </button>
                    ))}
                </div>
                <div className="lote-listhead" aria-hidden="true">
                    <span>Ativo</span>
                    <span>Estado</span>
                    <span>Detalhe</span>
                </div>
                <ol className="lote-list" aria-labelledby="lote-batch-title" data-testid="batch-items">
                    {slice.map((item) => (
                        <ItemRow key={item.position} item={item} job={job} />
                    ))}
                </ol>
                {filtered.length > shown ? (
                    <button
                        type="button"
                        className="lote-more"
                        onClick={() => setShown((n) => n + PAGE_STEP)}
                    >
                        Mostrar mais {PAGE_STEP} · {fmtInt(Math.min(shown, filtered.length))} de {fmtInt(filtered.length)}
                    </button>
                ) : null}
                {actionError ? <p className="lote-block" role="alert">{actionError}</p> : null}
                {running ? (
                    <div className="lote-actions">
                        <button
                            type="button"
                            ref={pauseBtn}
                            className="lote-btn warn"
                            data-testid="batch-pause"
                            {...off(pausing || cancelling)}
                            onClick={() => {
                                if (pausing || cancelling) return
                                acted.current = 'pause'
                                onPause()
                            }}
                        >
                            <Pause aria-hidden="true" />
                            {pausing ? 'Pausando…' : 'Pausar'}
                        </button>
                        <button
                            type="button"
                            className="lote-btn danger"
                            data-testid="batch-cancel"
                            {...off(pausing || cancelling)}
                            onClick={() => {
                                if (pausing || cancelling) return
                                acted.current = 'cancel'
                                onCancel()
                            }}
                        >
                            <Square aria-hidden="true" />
                            {cancelling ? 'Encerrando…' : 'Encerrar'}
                        </button>
                    </div>
                ) : null}
                {view === 'paused' ? (
                    <div className="lote-actions">
                        <button
                            type="button"
                            ref={resumeBtn}
                            className="lote-btn primary"
                            data-testid="batch-resume"
                            onClick={() => {
                                acted.current = 'resume'
                                onResume()
                            }}
                        >
                            <Play aria-hidden="true" />
                            Retomar
                        </button>
                        <button
                            type="button"
                            className="lote-btn danger"
                            data-testid="batch-cancel"
                            onClick={() => {
                                acted.current = 'cancel'
                                onCancel()
                            }}
                        >
                            <Square aria-hidden="true" />
                            Encerrar
                        </button>
                    </div>
                ) : null}
                {view === 'completed' || view === 'cancelled' || view === 'paused' || view === 'failed' ? (
                    <div className="lote-links" data-testid="batch-links">
                        {saved ? (
                            <Link to={favoritesHref(job)} data-testid="batch-open-favorites">
                                {favoritesLinkText(saved)}
                            </Link>
                        ) : null}
                        {showDiscoveryLink ? (
                            <Link to="/combo/discovery" data-testid="batch-discovery">
                                Descoberta sistemática (varredura)
                            </Link>
                        ) : null}
                    </div>
                ) : null}
            </div>
        </section>
    )
})

/** Lote anterior ao #1120 (sem itens): o resumo antigo, até o fim deles. */
function LegacyBatchSummary({ job, showDiscoveryLink }: { job: BatchJob; showDiscoveryLink: boolean }) {
    return (
        <section className="lote-batch" aria-label="Lote anterior" data-testid="batch-summary">
            <div className="lote-bbody">
                <p className="lote-live" role="status">
                    Lote {shortId(job.job_id)}: {job.processed} de {job.total} ativos, {job.succeeded} sucesso,{' '}
                    {job.failed} falha{(job.skipped ?? 0) > 0 ? `, ${job.skipped} ignorado(s)` : ''}.
                </p>
                <div className="lote-links">
                    <Link to="/favorites">Abrir Strategy Favorites</Link>
                    {showDiscoveryLink ? <Link to="/combo/discovery">Descoberta sistemática (varredura)</Link> : null}
                </div>
            </div>
        </section>
    )
}

