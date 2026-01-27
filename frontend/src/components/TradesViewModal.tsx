import React from 'react';
import { X, ArrowUp, ArrowDown, Download } from 'lucide-react';

interface Trade {
    entry_time: string;
    exit_time: string;
    entry_price: number;
    exit_price: number;
    pnl: number;
    pnl_pct: number;
    direction: string;
    size: number;
    type: string;
    initial_capital?: number;
    final_capital?: number;
    entry_reason?: string;
    exit_reason?: string;
}

interface TradesViewModalProps {
    isOpen: boolean;
    onClose: () => void;
    trades: Trade[];
    title?: string;
    subtitle?: string;
    symbol?: string;
    templateName?: string;
    timeframe?: string;
}

const TradesViewModal: React.FC<TradesViewModalProps> = ({ 
    isOpen, 
    onClose, 
    trades, 
    title = 'Trade History', 
    subtitle,
    symbol = '',
    templateName = '',
    timeframe = ''
}) => {
    if (!isOpen) return null;

    // Sort trades by entry time (newest first)
    const sortedTrades = [...(trades || [])].sort((a, b) => new Date(b.entry_time).getTime() - new Date(a.entry_time).getTime());

    const handleExportTrades = async () => {
        try {
            // Prepare trades data for export
            const tradesData = sortedTrades.map(trade => ({
                entry_time: trade.entry_time,
                entry_price: trade.entry_price,
                exit_time: trade.exit_time || '',
                exit_price: trade.exit_price || 0,
                type: trade.type || trade.direction?.toLowerCase() || 'long',
                profit: trade.pnl_pct || (trade.pnl && trade.initial_capital ? trade.pnl / trade.initial_capital : 0),
                pnl: trade.pnl || 0,
                initial_capital: trade.initial_capital || 100,
                final_capital: trade.final_capital || (trade.initial_capital ? trade.initial_capital + (trade.pnl || 0) : 100)
            }));

            const response = await fetch('http://localhost:8000/api/combos/export-trades', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    trades: tradesData,
                    symbol: symbol || 'UNKNOWN',
                    template_name: templateName || 'strategy',
                    timeframe: timeframe || '1d'
                })
            });

            if (!response.ok) {
                throw new Error('Erro ao exportar trades');
            }

            // Get the blob and create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // Extract filename from Content-Disposition header or use default
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `${templateName || 'strategy'}_${(symbol || 'UNKNOWN').replace('/', '_')}_${timeframe || '1d'}_trades.xlsx`;
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            console.error('❌ Erro ao exportar trades:', err);
            alert('Erro ao exportar trades para Excel. Tente novamente.');
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-[#0f1410] border border-white/10 rounded-2xl w-full max-w-5xl max-h-[80vh] flex flex-col shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
                <div className="flex items-center justify-between p-6 border-b border-white/5 bg-white/5 rounded-t-2xl">
                    <div>
                        <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
                            <div className="p-1.5 bg-blue-500/20 rounded-lg">
                                <ArrowUp className="w-4 h-4 text-blue-400" />
                            </div>
                            {title}
                        </h2>
                        {subtitle && (
                            <div className="text-sm text-gray-400 pl-10">
                                {subtitle}
                            </div>
                        )}
                    </div>
                    <div className="flex items-center gap-3">
                        {trades && trades.length > 0 && (
                            <button
                                onClick={handleExportTrades}
                                className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium transition-colors shadow-lg hover:shadow-emerald-500/50"
                            >
                                <Download className="w-4 h-4" />
                                Exportar para Excel
                            </button>
                        )}
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/10 rounded-full text-gray-400 hover:text-white transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                <div className="flex-1 overflow-auto bg-[#0a0f0a]">
                    <table className="w-full text-sm text-left">
                        <thead className="text-gray-400 font-semibold bg-white/5 border-b border-white/5 sticky top-0">
                            <tr>
                                <th className="px-6 py-4 border-r border-white/5">Entry Time</th>
                                <th className="px-6 py-4 text-right border-r border-white/5">Init. Bal.</th>
                                <th className="px-6 py-4 text-right border-r border-white/5">Final Bal.</th>
                                <th className="px-6 py-4 border-r border-white/5">Type</th>
                                <th className="px-6 py-4 text-right border-r border-white/5">Entry Price</th>
                                <th className="px-6 py-4 text-right border-r border-white/5">Exit Price</th>
                                <th className="px-6 py-4 text-right border-r border-white/5">PnL</th>
                                <th className="px-6 py-4 text-right">Return %</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sortedTrades.map((trade, idx) => {
                                const isWin = trade.pnl > 0;
                                return (
                                    <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                        <td className="px-6 py-3 text-gray-300 border-r border-white/5">
                                            {new Date(trade.entry_time).toLocaleString()}
                                            <div className="text-xs text-gray-500 mt-1">
                                                Exited: {trade.exit_time ? new Date(trade.exit_time).toLocaleString() : 'Open'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-3 text-right text-gray-300 border-r border-white/5 font-mono">
                                            ${trade.initial_capital?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '-'}
                                        </td>
                                        <td className="px-6 py-3 text-right text-gray-300 border-r border-white/5 font-mono">
                                            ${trade.final_capital?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '-'}
                                        </td>
                                        <td className="px-6 py-3 border-r border-white/5">
                                            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium ${trade.direction === 'Long' ? 'bg-green-500/10 text-green-400 ring-1 ring-green-500/20' : 'bg-red-500/10 text-red-400 ring-1 ring-red-500/20'}`}>
                                                {trade.direction === 'Long' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                                                {trade.direction}
                                            </span>
                                        </td>
                                        <td className="px-6 py-3 text-right text-gray-300 border-r border-white/5 font-mono">
                                            ${trade.entry_price?.toFixed(2)}
                                        </td>
                                        <td className="px-6 py-3 text-right text-gray-300 border-r border-white/5 font-mono">
                                            ${trade.exit_price?.toFixed(2)}
                                        </td>
                                        <td className={`px-6 py-3 text-right font-semibold border-r border-white/5 font-mono ${isWin ? 'text-green-400' : 'text-red-400'}`}>
                                            {trade.pnl > 0 ? '+' : ''}{trade.pnl?.toFixed(2)}
                                        </td>
                                        <td className={`px-6 py-3 text-right font-semibold font-mono ${isWin ? 'text-green-400' : 'text-red-400'}`}>
                                            {trade.pnl_pct ? (trade.pnl_pct * 100).toFixed(2) + '%' : '-'}
                                        </td>
                                    </tr>
                                );
                            })}
                            {(!trades || trades.length === 0) && (
                                <tr>
                                    <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                                        No trades recorded for this configuration.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default TradesViewModal;
