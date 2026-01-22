import { useState, useEffect } from 'react'
import { X, Star, AlertCircle } from 'lucide-react'

interface SaveFavoriteModalProps {
    isOpen: boolean
    onClose: () => void
    backtestResult: {
        template_name: string
        symbol: string
        timeframe: string
        parameters: Record<string, any>
        metrics: {
            total_return: number
            win_rate: number
            total_trades: number
            max_drawdown?: number
            sharpe_ratio?: number
        }
    }
    onSave: (data: {
        name: string
        symbol: string
        timeframe: string
        strategy_name: string
        parameters: Record<string, any>
        metrics: Record<string, any>
        notes?: string
    }) => Promise<void>
}

export function SaveFavoriteModal({ isOpen, onClose, backtestResult, onSave }: SaveFavoriteModalProps) {
    const [name, setName] = useState('')
    const [notes, setNotes] = useState('')
    const [isSaving, setIsSaving] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Auto-generate name when modal opens
    useEffect(() => {
        if (isOpen && backtestResult && backtestResult.metrics) {
            const roi = backtestResult.metrics.total_return?.toFixed(0) || '0'
            const autoName = `${backtestResult.symbol} ${backtestResult.timeframe} - ${backtestResult.template_name} - ${roi}% ROI`
            setName(autoName)
            setNotes('')
            setError(null)
        }
    }, [isOpen, backtestResult])

    const handleSave = async () => {
        if (!name.trim()) {
            setError('Nome é obrigatório')
            return
        }

        setIsSaving(true)
        setError(null)

        try {
            await onSave({
                name: name.trim(),
                symbol: backtestResult.symbol,
                timeframe: backtestResult.timeframe,
                strategy_name: backtestResult.template_name,
                parameters: backtestResult.parameters,
                metrics: backtestResult.metrics, // Salva TODAS as métricas
                notes: notes.trim() || undefined
            })
            onClose()
        } catch (err: any) {
            setError(err.message || 'Erro ao salvar favorito')
        } finally {
            setIsSaving(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-gray-800 rounded-2xl border border-gray-700 w-full max-w-2xl p-6 shadow-2xl">
                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <Star className="w-5 h-5 text-yellow-500" />
                        Salvar nos Favoritos
                    </h3>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="space-y-4">
                    {/* Error Alert */}
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                            <p className="text-red-400 text-sm">{error}</p>
                        </div>
                    )}

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
                                    {backtestResult.metrics?.total_return?.toFixed(2) || '0.00'}%
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

                    {/* Save Button */}
                    <button
                        onClick={handleSave}
                        disabled={isSaving || !name.trim()}
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
