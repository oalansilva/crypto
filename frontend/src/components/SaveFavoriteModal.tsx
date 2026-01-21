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
        if (isOpen && backtestResult) {
            const roi = backtestResult.metrics.total_return.toFixed(0)
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
                metrics: backtestResult.metrics,
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-800">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-800">
                    <div className="flex items-center gap-3">
                        <Star className="w-6 h-6 text-yellow-500" />
                        <h2 className="text-xl font-semibold text-white">Salvar nos Favoritos</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Error Alert */}
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                            <p className="text-red-400 text-sm">{error}</p>
                        </div>
                    )}

                    {/* Name Input */}
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Nome da Estratégia *
                        </label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Ex: BTC 1d - Multi MA - 24000% ROI"
                        />
                    </div>

                    {/* Notes Input */}
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Notas (Opcional)
                        </label>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            rows={3}
                            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                            placeholder="Ex: Melhor resultado em mercado de alta"
                        />
                    </div>

                    {/* Metrics Display */}
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-3">
                            Métricas de Performance
                        </label>
                        <div className="bg-gray-800/50 rounded-lg p-4 grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Retorno Total</p>
                                <p className="text-lg font-semibold text-green-400">
                                    {backtestResult.metrics.total_return.toFixed(2)}%
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Win Rate</p>
                                <p className="text-lg font-semibold text-blue-400">
                                    {(backtestResult.metrics.win_rate * 100).toFixed(1)}%
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Total de Trades</p>
                                <p className="text-lg font-semibold text-white">
                                    {backtestResult.metrics.total_trades}
                                </p>
                            </div>
                            {backtestResult.metrics.sharpe_ratio !== undefined && (
                                <div>
                                    <p className="text-xs text-gray-400 mb-1">Sharpe Ratio</p>
                                    <p className="text-lg font-semibold text-purple-400">
                                        {backtestResult.metrics.sharpe_ratio.toFixed(2)}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Parameters (collapsed/hidden) */}
                    <details className="bg-gray-800/30 rounded-lg">
                        <summary className="px-4 py-3 cursor-pointer text-sm text-gray-400 hover:text-white transition-colors">
                            Ver Parâmetros
                        </summary>
                        <div className="px-4 pb-4">
                            <pre className="text-xs text-gray-300 overflow-x-auto">
                                {JSON.stringify(backtestResult.parameters, null, 2)}
                            </pre>
                        </div>
                    </details>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-800">
                    <button
                        onClick={onClose}
                        disabled={isSaving}
                        className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isSaving || !name.trim()}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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
