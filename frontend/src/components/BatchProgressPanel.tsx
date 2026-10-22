import { ExternalLink, Pause, Settings, Square } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { formatElapsed, isBatchFinal, type BatchProgress } from '../hooks/useBatchJob'

interface BatchProgressPanelProps {
    batchRunning: boolean
    batchProgress: BatchProgress | null
    batchTotal: number
    clientElapsedSec: number
    pauseCancelRequested: boolean
    onPause: () => void
    onCancel: () => void
    showDiscoveryLink?: boolean
}

/** Progresso e resumo do lote do Combo (mesmo painel no Combo e na Otimização). */
export function BatchProgressPanel({
    batchRunning,
    batchProgress,
    batchTotal,
    clientElapsedSec,
    pauseCancelRequested,
    onPause,
    onCancel,
    showDiscoveryLink = false,
}: BatchProgressPanelProps) {
    const navigate = useNavigate()
    return (
        <>
            {batchRunning && (
                <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/30 rounded-[16px]" data-testid="batch-progress">
                    <div className="flex items-center gap-2 text-blue-300 font-medium mb-2">
                        <Settings className="w-4 h-4 animate-spin" />
                        {(batchProgress?.processed ?? 0)} de {batchProgress?.total ?? batchTotal} ativos
                    </div>
                    {batchProgress?.current_symbol && (
                        <p className="text-sm text-cyan-700/90 mb-2">
                            Ativo atual: <span className="font-medium">{batchProgress.current_symbol}</span>
                        </p>
                    )}
                    <div className="text-sm text-zinc-500 space-y-1">
                        <p>Tempo decorrido: {formatElapsed(clientElapsedSec)}</p>
                        {(() => {
                            const p = batchProgress?.processed ?? 0
                            const t = batchProgress?.total ?? batchTotal
                            const eta = batchProgress?.estimated_remaining_sec
                            if (p > 0 && p < t && eta != null) return <p>Tempo restante: ~{formatElapsed(Math.ceil(eta))}</p>
                            if (p > 0 && p < t) return <p>Tempo restante: calculando…</p>
                            return null
                        })()}
                    </div>
                    <div className="flex gap-2 mt-3">
                        <button
                            type="button"
                            onClick={onPause}
                            disabled={pauseCancelRequested}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[16px] bg-amber-500/20 text-amber-700 border border-amber-500/40 hover:bg-amber-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
                        >
                            <Pause className="w-4 h-4" />
                            Pausar
                        </button>
                        <button
                            type="button"
                            onClick={onCancel}
                            disabled={pauseCancelRequested}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[16px] bg-red-500/20 text-red-300 border border-red-500/40 hover:bg-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
                        >
                            <Square className="w-4 h-4" />
                            Encerrar
                        </button>
                    </div>
                </div>
            )}

            {!batchRunning && batchProgress && isBatchFinal(batchProgress) && (
                <div className="mt-4 p-4 bg-zinc-50 border border-zinc-200 rounded-[16px] space-y-2" data-testid="batch-summary">
                    <p className="text-sm font-medium text-zinc-900">
                        {batchProgress.status === 'cancelled' && 'Encerrado pelo usuário. '}
                        {batchProgress.status === 'paused' && 'Pausado pelo usuário. '}
                        {batchProgress.succeeded} sucesso, {batchProgress.failed} falha
                        {(batchProgress.skipped ?? 0) > 0 && `, ${batchProgress.skipped} ignorado(s) (já em favoritos ou não suportados)`}.
                    </p>
                    {batchProgress.errors.length > 0 && (
                        <details className="text-xs text-zinc-400">
                            <summary>Erros por ativo</summary>
                            <ul className="mt-1 list-disc list-inside">
                                {batchProgress.errors.map((e, i) => (
                                    <li key={i}>{e.symbol}: {e.error}</li>
                                ))}
                            </ul>
                        </details>
                    )}
                    <button
                        onClick={() => navigate('/favorites')}
                        className="inline-flex items-center gap-1 text-sm text-cyan-400 hover:text-cyan-700"
                    >
                        <ExternalLink className="w-4 h-4" />
                        Abrir Strategy Favorites
                    </button>
                    {showDiscoveryLink && (
                        <button
                            onClick={() => navigate('/combo/discovery')}
                            className="inline-flex items-center gap-1 text-sm text-cyan-400 hover:text-cyan-700"
                        >
                            <ExternalLink className="w-4 h-4" />
                            Descoberta sistemática (varredura)
                        </button>
                    )}
                </div>
            )}
        </>
    )
}
