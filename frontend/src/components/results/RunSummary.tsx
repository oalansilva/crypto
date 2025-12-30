import { Calendar, DollarSign, Activity } from 'lucide-react'

interface RunSummaryProps {
    dataset: {
        exchange: string
        symbol: string
        timeframe: string
        since: string
        until: string
        candle_count?: number
    }
    capital: number
    fee: number
    strategiesCount: number
}

export function RunSummary({ dataset, capital, fee, strategiesCount }: RunSummaryProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="glass p-4 rounded-xl flex items-center gap-4">
                <div className="p-3 bg-blue-500/10 rounded-lg">
                    <Activity className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                    <h3 className="text-sm font-medium text-gray-400">Market Config</h3>
                    <p className="text-white font-semibold">
                        {dataset.symbol} • {dataset.timeframe}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                        {dataset.exchange.toUpperCase()} • {strategiesCount} Strategies
                    </p>
                </div>
            </div>

            <div className="glass p-4 rounded-xl flex items-center gap-4">
                <div className="p-3 bg-purple-500/10 rounded-lg">
                    <Calendar className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                    <h3 className="text-sm font-medium text-gray-400">Period</h3>
                    <p className="text-white font-semibold">
                        {dataset.since ? new Date(dataset.since).toLocaleDateString() : 'N/A'} - {dataset.until ? new Date(dataset.until).toLocaleDateString() : 'N/A'}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                        {dataset.candle_count ? dataset.candle_count.toLocaleString() : 0} candles processed
                    </p>
                </div>
            </div>

            <div className="glass p-4 rounded-xl flex items-center gap-4">
                <div className="p-3 bg-emerald-500/10 rounded-lg">
                    <DollarSign className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                    <h3 className="text-sm font-medium text-gray-400">Risk Settings</h3>
                    <p className="text-white font-semibold">
                        ${capital.toLocaleString()} Initial
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                        Fee: {(fee * 100).toFixed(2)}%
                    </p>
                </div>
            </div>
        </div>
    )
}
