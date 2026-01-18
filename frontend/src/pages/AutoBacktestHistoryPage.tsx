// file: frontend/src/pages/AutoBacktestHistoryPage.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Clock, CheckCircle, XCircle, Ban } from 'lucide-react';

interface HistoryItem {
    run_id: string;
    symbol: string;
    strategy: string;
    status: string;
    created_at: string;
    completed_at?: string;
    favorite_id?: number;
}

export const AutoBacktestHistoryPage: React.FC = () => {
    const navigate = useNavigate();

    const { data: history, isLoading } = useQuery({
        queryKey: ['auto-backtest-history'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/api/backtest/auto/history');
            if (!response.ok) throw new Error('Failed to fetch history');
            return response.json() as Promise<HistoryItem[]>;
        }
    });

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'COMPLETED': return <CheckCircle className="w-5 h-5 text-green-500" />;
            case 'FAILED': return <XCircle className="w-5 h-5 text-red-500" />;
            case 'CANCELLED': return <Ban className="w-5 h-5 text-yellow-500" />;
            default: return <Clock className="w-5 h-5 text-gray-500" />;
        }
    };

    return (
        <div className="min-h-screen font-sans p-6" style={{ backgroundColor: '#0B0E14', color: '#E2E8F0' }}>
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold mb-2" style={{ color: '#14b8a6' }}>
                        Auto Backtest History
                    </h1>
                    <p className="text-gray-400">
                        View past auto backtest executions
                    </p>
                </div>

                {/* Table */}
                <div className="rounded-xl overflow-hidden" style={{ backgroundColor: '#151922', border: '1px solid #2A2F3A' }}>
                    <table className="w-full">
                        <thead className="bg-gray-900">
                            <tr>
                                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-400">Status</th>
                                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-400">Run ID</th>
                                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-400">Symbol</th>
                                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-400">Strategy</th>
                                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-400">Created</th>
                                <th className="text-right py-4 px-6 text-sm font-semibold text-gray-400">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {isLoading ? (
                                <tr>
                                    <td colSpan={6} className="text-center py-8 text-gray-500">
                                        Loading...
                                    </td>
                                </tr>
                            ) : history?.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="text-center py-8 text-gray-500">
                                        No executions found
                                    </td>
                                </tr>
                            ) : (
                                history?.map((item) => (
                                    <tr
                                        key={item.run_id}
                                        className="border-t border-gray-800 hover:bg-gray-900/50 cursor-pointer"
                                        onClick={() => navigate(`/backtest/auto/results/${item.run_id}`)}
                                    >
                                        <td className="py-4 px-6">
                                            <div className="flex items-center gap-2">
                                                {getStatusIcon(item.status)}
                                                <span className="text-sm font-medium">{item.status}</span>
                                            </div>
                                        </td>
                                        <td className="py-4 px-6 font-mono text-sm text-gray-400">
                                            {item.run_id.substring(0, 20)}...
                                        </td>
                                        <td className="py-4 px-6 font-medium">{item.symbol}</td>
                                        <td className="py-4 px-6">
                                            <span className="px-2 py-1 rounded bg-teal-900/30 text-teal-400 text-xs font-bold">
                                                {item.strategy.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="py-4 px-6 text-sm text-gray-400">
                                            {new Date(item.created_at).toLocaleString()}
                                        </td>
                                        <td className="py-4 px-6 text-right">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigate(`/backtest/auto/results/${item.run_id}`);
                                                }}
                                                className="px-4 py-2 text-sm rounded-md bg-teal-600 hover:bg-teal-500 text-white font-medium"
                                            >
                                                View Results
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Actions */}
                <div className="mt-6">
                    <button
                        onClick={() => navigate('/backtest/auto')}
                        className="px-6 py-3 rounded-md font-bold bg-teal-500 hover:bg-teal-400 text-black"
                    >
                        Run New Auto Backtest
                    </button>
                </div>
            </div>
        </div>
    );
};
