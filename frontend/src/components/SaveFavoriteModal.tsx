import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { X, Star, AlertCircle, ShieldAlert } from 'lucide-react'
import { useAuth } from '@/stores/authStore'
import '@/styles/favoriteAlerts.css'

/** Card #1122 (d2): o favorito entra sem estrela; a estrela põe no Monitor com o alerta ligado. */
export const SAVE_FAVORITE_ALERT_NOTE =
    'O favorito entra sem estrela, só em Favoritos. Dê pelo menos 1 estrela lá para acompanhar no Monitor e receber os sinais no Telegram; o alerta já vem ligado e você desliga no Monitor.'
export const SAVE_FAVORITE_DUPLICATE =
    'Já está nos favoritos com esta configuração (fonte, sessão e ajuste). Nada foi salvo.'

/** Erro do salvar com o status HTTP (409 = mesma configuração já salva). */
export class SaveFavoriteError extends Error {
    status: number

    constructor(message: string, status: number) {
        super(message)
        this.status = status
    }
}

export interface SaveFavoriteIdentity {
    /** "NVDA · Ação · USD" */
    title: string
    /** "Binance Ações · pregão regular de NY · ajustado por split · 1d · Long" */
    detail: string
    /** "Binance Ações" (texto do sucesso) */
    configurationShort: string
}

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), summary, [tabindex]:not([tabindex="-1"])'

interface SaveFavoriteModalProps {
    isOpen: boolean
    onClose: () => void
    backtestResult: {
        template_name: string
        symbol: string
        timeframe: string
        start_date?: string | null
        end_date?: string | null
        period_type?: string | null
        parameters: Record<string, any>
        metrics: {
            total_return: number
            total_return_pct?: number
            win_rate: number
            total_trades: number
            max_drawdown?: number
            sharpe_ratio?: number
        }
        promotion_metrics?: Record<string, any> | null
        trades?: Array<any>
        oos_verdict?: {
            status?: string
            reasons?: string[]
            holdout_trades?: number
            split_train_ratio?: number
        } | null
        oos_metrics?: Record<string, any> | null
        oos_proof?: string | null
    }
    onSave: (data: {
        name: string
        symbol: string
        timeframe: string
        start_date?: string | null
        end_date?: string | null
        period_type?: string | null
        strategy_name: string
        parameters: Record<string, any>
        metrics: Record<string, any>
        notes?: string
        oos_verdict?: Record<string, any> | null
        oos_metrics?: Record<string, any> | null
        oos_proof?: string | null
        override_oos?: boolean
    }) => Promise<void>
    /** Card #1122: ativo, classe, moeda e configuração do resultado. */
    identity?: SaveFavoriteIdentity | null
}

export function SaveFavoriteModal({ isOpen, onClose, backtestResult, onSave, identity = null }: SaveFavoriteModalProps) {
    const [name, setName] = useState('')
    const [notes, setNotes] = useState('')
    const [isSaving, setIsSaving] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [overrideOos, setOverrideOos] = useState(false)
    const [duplicate, setDuplicate] = useState(false)
    const [saved, setSaved] = useState(false)
    const dialogRef = useRef<HTMLDivElement | null>(null)
    const successLinkRef = useRef<HTMLAnchorElement | null>(null)
    const triggerRef = useRef<HTMLElement | null>(null)
    const { user } = useAuth()
    const isAdmin = Boolean(user?.isAdmin)

    const verdictStatus = String(backtestResult?.oos_verdict?.status ?? '').toUpperCase()
    const isBlocked = Boolean(backtestResult?.oos_verdict) && verdictStatus !== 'GO'

    // total_return é decimal (0.2939 = 29.39%); total_return_pct já é % (2939.86)
    const totalReturnPct = backtestResult?.metrics?.total_return_pct ?? ((backtestResult?.metrics?.total_return ?? 0) * 100)

    // Auto-generate name when modal opens
    useEffect(() => {
        if (isOpen && backtestResult && backtestResult.metrics) {
            const roi = totalReturnPct.toFixed(1)
            const autoName = `${backtestResult.symbol} ${backtestResult.timeframe} - ${backtestResult.template_name} - ${roi}% ROI`
            setName(autoName)
            setNotes('')
            setError(null)
            setOverrideOos(false)
            setDuplicate(false)
            setSaved(false)
        }
    }, [isOpen, backtestResult, totalReturnPct])

    const handleClose = () => {
        onClose()
        // O foco volta ao gatilho ("Salvar nos Favoritos").
        const trigger = triggerRef.current
        window.setTimeout(() => trigger?.focus(), 0)
    }

    // Diálogo: guarda o gatilho, prende o foco (Tab e Shift+Tab) e fecha com Esc em qualquer foco.
    useEffect(() => {
        if (!isOpen) return
        triggerRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null
        const firstField = dialogRef.current?.querySelector<HTMLElement>('input, textarea, button')
        firstField?.focus()
        const onKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                event.preventDefault()
                handleClose()
                return
            }
            if (event.key !== 'Tab' || !dialogRef.current) return
            const items = Array.from(dialogRef.current.querySelectorAll<HTMLElement>(FOCUSABLE))
                .filter((element) => element.offsetParent !== null || element === document.activeElement)
            if (items.length === 0) return
            const first = items[0]
            const last = items[items.length - 1]
            const active = document.activeElement as HTMLElement | null
            const inside = active ? dialogRef.current.contains(active) : false
            if (event.shiftKey && (active === first || !inside)) {
                event.preventDefault()
                last.focus()
            } else if (!event.shiftKey && (active === last || !inside)) {
                event.preventDefault()
                first.focus()
            }
        }
        document.addEventListener('keydown', onKeyDown)
        return () => document.removeEventListener('keydown', onKeyDown)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isOpen])

    useEffect(() => {
        if (saved) successLinkRef.current?.focus()
    }, [saved])

    const handleSave = async () => {
        if (!name.trim()) {
            setError('Nome é obrigatório')
            return
        }

        if (isBlocked && !isAdmin) {
            setError('Candidato reprovado na validação walk-forward (holdout). Apenas admin pode usar override.')
            return
        }

        if (isBlocked && !overrideOos) {
            setError('Candidato reprovado na validação walk-forward (holdout). Use override apenas com decisão explícita.')
            return
        }

        setIsSaving(true)
        setError(null)
        setDuplicate(false)

        try {
            await onSave({
                name: name.trim(),
                symbol: backtestResult.symbol,
                timeframe: backtestResult.timeframe,
                start_date: backtestResult.start_date ?? null,
                end_date: backtestResult.end_date ?? null,
                period_type: backtestResult.period_type ?? null,
                strategy_name: backtestResult.template_name,
                parameters: backtestResult.parameters,
                metrics: {
                    ...(backtestResult.oos_verdict
                        ? {
                            ...backtestResult.metrics,
                            metrics_snapshot: backtestResult.promotion_metrics ?? backtestResult.metrics,
                        }
                        : (backtestResult.promotion_metrics ?? backtestResult.metrics)),
                    trades: backtestResult.oos_verdict
                        ? (backtestResult.trades ?? backtestResult.promotion_metrics?.trades)
                        : (backtestResult.promotion_metrics?.trades ?? backtestResult.trades),
                },
                notes: notes.trim() || undefined,
                oos_verdict: backtestResult.oos_verdict ?? null,
                oos_metrics: backtestResult.oos_metrics ?? null,
                oos_proof: backtestResult.oos_proof ?? null,
                override_oos: isBlocked && overrideOos
            })
            // Card #1122: o sucesso fica no modal, com "Ver em Favoritos" (recebe o foco).
            setSaved(true)
        } catch (err: any) {
            if (err instanceof SaveFavoriteError && err.status === 409) {
                setDuplicate(true)
            } else {
                setError(err.message || 'Erro ao salvar favorito')
            }
        } finally {
            setIsSaving(false)
        }
    }

    if (!isOpen) return null

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
            role="dialog"
            aria-modal="true"
            aria-labelledby="save-favorite-title"
            data-testid="save-favorite-dialog"
        >
            <div ref={dialogRef} className="bg-gray-800 rounded-2xl border border-gray-700 w-full max-w-2xl p-6 shadow-2xl max-h-[calc(100vh-2rem)] overflow-y-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <h3 id="save-favorite-title" className="text-xl font-bold text-white flex items-center gap-2">
                        <Star className="w-5 h-5 text-yellow-500" aria-hidden="true" />
                        Salvar nos Favoritos
                    </h3>
                    <button type="button" onClick={handleClose} className="text-gray-400 hover:text-white" aria-label="Fechar">
                        <X className="w-5 h-5" aria-hidden="true" />
                    </button>
                </div>

                <div className="space-y-4">
                    {identity ? (
                        <div className="save-favorite-identity" data-testid="favorite-identity">
                            <strong>{identity.title}</strong>
                            <span>{identity.detail}</span>
                        </div>
                    ) : null}

                    {/* Error Alert */}
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                            <p className="text-red-400 text-sm">{error}</p>
                        </div>
                    )}

                    {/* Walk-forward gate (card #470) */}
                    {backtestResult.oos_verdict ? (
                        <div className={`rounded-lg border p-4 ${isBlocked ? 'border-red-500/50 bg-red-500/10' : 'border-green-500/40 bg-green-500/10'}`} data-testid="oos-gate-block">
                            <div className="flex items-start gap-3">
                                <ShieldAlert className={`w-5 h-5 flex-shrink-0 mt-0.5 ${isBlocked ? 'text-red-500' : 'text-green-500'}`} />
                                <div>
                                    <p className={`text-sm font-semibold ${isBlocked ? 'text-red-400' : 'text-green-400'}`}>
                                        Validação walk-forward: {isBlocked ? `veredito ${verdictStatus}` : 'GO no holdout'}
                                    </p>
                                    {isBlocked && backtestResult.oos_verdict.reasons?.length ? (
                                        <ul className="mt-2 space-y-1 text-xs text-red-300/90">
                                            {backtestResult.oos_verdict.reasons.slice(0, 5).map((reason, idx) => (
                                                <li key={idx}>• {reason}</li>
                                            ))}
                                        </ul>
                                    ) : null}
                                    {isBlocked && isAdmin && (
                                        <label className="mt-3 flex cursor-pointer items-center gap-2 text-xs text-gray-300">
                                            <input
                                                type="checkbox"
                                                checked={overrideOos}
                                                onChange={(e) => setOverrideOos(e.target.checked)}
                                                className="h-4 w-4 rounded border-gray-600"
                                            />
                                            Salvar mesmo assim (override de admin — só com decisão explícita)
                                        </label>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : null}

                    {/* Name Input */}
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Nome da Estratégia *</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="Ex: BTC 1d - Multi MA - 24000% ROI"
                        />
                    </div>

                    {/* Notes Input */}
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Notas (Opcional)</label>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 outline-none h-24 resize-none"
                            placeholder="Ex: Melhor resultado em mercado de alta"
                        />
                    </div>

                    {/* Metrics Display */}
                    <div>
                        <label className="block text-sm text-gray-400 mb-2">Métricas de Performance</label>
                        <div className="bg-gray-900/50 rounded-lg p-4 grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Retorno Total</p>
                                <p className="text-lg font-semibold text-green-400">
                                    {totalReturnPct.toFixed(2)}%
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Win Rate</p>
                                <p className="text-lg font-semibold text-blue-400">
                                    {((backtestResult.metrics?.win_rate || 0) * 100).toFixed(1)}%
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Total de Trades</p>
                                <p className="text-lg font-semibold text-white">
                                    {backtestResult.metrics?.total_trades || 0}
                                </p>
                            </div>
                            {backtestResult.metrics?.sharpe_ratio !== undefined && (
                                <div>
                                    <p className="text-xs text-gray-400 mb-1">Sharpe Ratio</p>
                                    <p className="text-lg font-semibold text-purple-400">
                                        {backtestResult.metrics.sharpe_ratio.toFixed(2)}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Parameters Preview */}
                    <details className="bg-gray-900/50 rounded-lg">
                        <summary className="px-4 py-3 cursor-pointer text-sm text-gray-400 hover:text-white transition-colors">
                            Ver Parâmetros
                        </summary>
                        <div className="px-4 pb-4">
                            <pre className="text-xs text-gray-300 overflow-x-auto">
                                {JSON.stringify(backtestResult.parameters, null, 2)}
                            </pre>
                        </div>
                    </details>

                    <p className="save-favorite-note" data-testid="favorite-alert-note">{SAVE_FAVORITE_ALERT_NOTE}</p>
                    {duplicate ? (
                        <p className="save-favorite-duplicate" role="alert" data-testid="favorite-duplicate">{SAVE_FAVORITE_DUPLICATE}</p>
                    ) : null}
                    {saved ? (
                        <div className="save-favorite-success" data-testid="favorite-saved">
                            <p role="status">
                                Salvo em Favoritos{identity ? ` com a configuração ${identity.configurationShort}` : ''}.
                            </p>
                            <Link ref={successLinkRef} className="save-favorite-success-link" to="/favorites" data-testid="favorite-saved-link">
                                Ver em Favoritos
                            </Link>
                        </div>
                    ) : null}

                    {/* Save Button */}
                    <button
                        type="button"
                        onClick={handleSave}
                        disabled={saved || isSaving || !name.trim() || (isBlocked && (!isAdmin || !overrideOos))}
                        className="w-full py-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSaving ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Salvando...
                            </>
                        ) : (
                            <>
                                <Star className="w-4 h-4" />
                                Salvar
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    )
}
