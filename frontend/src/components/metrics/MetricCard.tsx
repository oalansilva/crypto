import React from 'react';
import { Info } from 'lucide-react';

interface MetricCardProps {
    label: string;
    value: string | number;
    subtitle?: string;
    status?: 'good' | 'warning' | 'bad' | 'neutral';
    tooltip?: string;
    format?: 'percentage' | 'number' | 'currency' | 'ratio';
}

export const MetricCard: React.FC<MetricCardProps> = ({
    label,
    value,
    subtitle,
    status = 'neutral',
    tooltip,
    format = 'number'
}) => {
    const formatValue = (val: string | number): string => {
        if (typeof val === 'string') return val;

        switch (format) {
            case 'percentage':
                return `${(val * 100).toFixed(2)}%`;
            case 'currency':
                return `$${val.toFixed(2)}`;
            case 'ratio':
                return val.toFixed(2);
            default:
                return val.toString();
        }
    };

    const getStatusColor = () => {
        switch (status) {
            case 'good':
                return 'text-emerald-400 border-emerald-500/30 bg-emerald-900/20';
            case 'warning':
                return 'text-yellow-400 border-yellow-500/30 bg-yellow-900/20';
            case 'bad':
                return 'text-red-400 border-red-500/30 bg-red-900/20';
            default:
                return 'text-blue-400 border-blue-500/30 bg-blue-900/20';
        }
    };

    const getStatusIcon = () => {
        switch (status) {
            case 'good':
                return '✓';
            case 'warning':
                return '⚠';
            case 'bad':
                return '✗';
            default:
                return '';
        }
    };

    return (
        <div className={`rounded-lg border p-4 ${getStatusColor()}`}>
            <div className="flex items-start justify-between mb-2">
                <span className="text-xs text-gray-400 uppercase tracking-wide">{label}</span>
                {tooltip && (
                    <div className="group relative">
                        <Info className="w-4 h-4 text-gray-500 cursor-help" />
                        <div className="absolute right-0 top-6 w-64 p-2 bg-gray-800 border border-gray-700 rounded text-xs text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity z-10 pointer-events-none">
                            {tooltip}
                        </div>
                    </div>
                )}
            </div>

            <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold">{formatValue(value)}</span>
                {status !== 'neutral' && (
                    <span className="text-lg">{getStatusIcon()}</span>
                )}
            </div>

            {subtitle && (
                <p className="text-xs text-gray-400 mt-1">{subtitle}</p>
            )}
        </div>
    );
};
