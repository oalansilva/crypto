import React from 'react';
import { X, ArrowUp, ArrowDown } from 'lucide-react';

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
}

const TradesViewModal: React.FC<TradesViewModalProps> = ({ isOpen, onClose, trades, title = 'Trade History', subtitle }) => {
    if (!isOpen) return null;

    // Sort trades by entry time (newest first)
    const sortedTrades = [...(trades || [])].sort((a, b) => new Date(b.entry_time).getTime() - new Date(a.entry_time).getTime());

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <div className="bg-[#151922] border border-[#2A2F3A] rounded-xl w-full max-w-5xl max-h-[80vh] flex flex-col shadow-2xl">
                <div className="flex items-center justify-between p-6 border-b border-[#2A2F3A]">
                    <div>
                        <h2 className="text-xl font-bold text-white mb-1">{title}</h2>
                        {subtitle && (
                            <div className="text-sm text-gray-400 font-mono">
                                {subtitle}
                            </div>
                        )}
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-[#2A2F3A] rounded-full transition-colors">
                        <X className="w-6 h-6 text-gray-400" />
                    </button>
                </div>

                <div className="flex-1 overflow-auto p-6">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-gray-400 uppercase bg-[#0B0E14] sticky top-0">
                            <tr>
                                <th className="px-4 py-3 rounded-tl-lg">Entry Time</th>
                                <th className="px-4 py-3 text-right">Init. Bal.</th>
                                <th className="px-4 py-3 text-right">Final Bal.</th>
                                <th className="px-4 py-3">Type</th>
                                <th className="px-4 py-3 text-right">Entry Price</th>
                                <th className="px-4 py-3 text-right">Exit Price</th>
                                <th className="px-4 py-3 text-right">PnL</th>
                                <th className="px-4 py-3 text-right rounded-tr-lg">Return %</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sortedTrades.map((trade, idx) => {
                                const isWin = trade.pnl > 0;
                                return (
                                    <tr key={idx} className="border-b border-[#2A2F3A] hover:bg-[#1A202C]">
                                        <td className="px-4 py-3 text-gray-300 font-mono">
                                            {new Date(trade.entry_time).toLocaleString()}
                                            <div className="text-xs text-gray-500 mt-1">
                                                Exited: {trade.exit_time ? new Date(trade.exit_time).toLocaleString() : 'Open'}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-right text-gray-300 font-mono">
                                            ${trade.initial_capital?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '-'}
                                        </td>
                                        <td className="px-4 py-3 text-right text-gray-300 font-mono">
                                            ${trade.final_capital?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '-'}
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${trade.direction === 'Long' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
                                                {trade.direction === 'Long' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                                                {trade.direction}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono text-gray-300">
                                            ${trade.entry_price?.toFixed(2)}
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono text-gray-300">
                                            ${trade.exit_price?.toFixed(2)}
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono font-bold" style={{ color: isWin ? '#10B981' : '#EF4444' }}>
                                            {trade.pnl > 0 ? '+' : ''}{trade.pnl?.toFixed(2)}
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono" style={{ color: isWin ? '#10B981' : '#EF4444' }}>
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
