// src/components/StrategyBuilder.tsx
import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import {
    Search, Plus, X, ChevronRight, Binary, Activity,
    BarChart2, Zap, Layout, Code, Save, Trash2,
    HelpCircle, Filter
} from 'lucide-react'
import { API_BASE_URL } from '../lib/apiBase'

// --- Interfaces ---
interface IndicatorParam {
    name: string
    type: string
    default: any
}

interface IndicatorMetadata {
    name: string
    category: string
    params: IndicatorParam[]
}

interface IndicatorConfig {
    name: string
    params: Record<string, any>
}

interface CustomStrategyConfig {
    name: string
    indicators: IndicatorConfig[]
    entry: string
    exit: string
}

interface StrategyBuilderProps {
    onSave: (config: CustomStrategyConfig) => void
    onCancel: () => void
}

const CATEGORY_ICONS: Record<string, any> = {
    'momentum': Zap,
    'trend': Activity,
    'volatility': BarChart2,
    'overlap': Layout,
    'statistics': Binary,
    'performance': Activity,
    'volume': BarChart2,
    'cycle': Activity
}

export function StrategyBuilder({ onSave, onCancel }: StrategyBuilderProps) {
    const [searchTerm, setSearchTerm] = useState('')
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
    const [strategyName, setStrategyName] = useState('My Custom Strategy')

    // Strategy Definition State
    const [selectedIndicators, setSelectedIndicators] = useState<IndicatorConfig[]>([])
    const [entryCondition, setEntryCondition] = useState('RSI_14 < 30')
    const [exitCondition, setExitCondition] = useState('RSI_14 > 70')

    // View State
    const [activeTab, setActiveTab] = useState<'indicators' | 'logic'>('indicators')

    const { data: indicators = [], isLoading } = useQuery<IndicatorMetadata[]>({
        queryKey: ['indicators-metadata'],
        queryFn: async () => {
            const res = await axios.get(`${API_BASE_URL}/strategies/metadata`)
            // API returns: { "category1": [...], "category2": [...] }
            // Transform to flat array: [...]
            const grouped = res.data
            const flat: IndicatorMetadata[] = []
            for (const category in grouped) {
                grouped[category].forEach((ind: any) => {
                    flat.push({
                        name: ind.name,
                        category: ind.category,
                        params: ind.params
                    })
                })
            }
            return flat
        },
        staleTime: Infinity
    })

    // Grouping Logic
    const categories = useMemo(() => {
        const unique = new Set(indicators.map(i => i.category))
        return Array.from(unique).sort()
    }, [indicators])

    const filteredIndicators = useMemo(() => {
        let items = indicators
        if (selectedCategory) {
            items = items.filter(i => i.category === selectedCategory)
        }
        if (searchTerm) {
            const lower = searchTerm.toLowerCase()
            items = items.filter(i => i.name.toLowerCase().includes(lower))
        }
        return items
    }, [indicators, selectedCategory, searchTerm])

    const handleAddIndicator = (indicator: IndicatorMetadata) => {
        const defaultParams: Record<string, any> = {}
        indicator.params.forEach(p => {
            defaultParams[p.name] = p.default
        })

        const newConfig: IndicatorConfig = {
            name: indicator.name,
            params: defaultParams
        }
        setSelectedIndicators([...selectedIndicators, newConfig])
    }

    const removeIndicator = (index: number) => {
        const newList = [...selectedIndicators]
        newList.splice(index, 1)
        setSelectedIndicators(newList)
    }

    const updateIndicatorParam = (idx: number, paramName: string, value: any) => {
        const newList = [...selectedIndicators]
        newList[idx].params = { ...newList[idx].params, [paramName]: value }
        setSelectedIndicators(newList)
    }

    const handleSave = () => {
        onSave({
            name: strategyName,
            indicators: selectedIndicators,
            entry: entryCondition,
            exit: exitCondition
        })
    }

    return (
        <div className="flex h-full bg-[#0a0f1c] text-white">

            {/* LEFT SIDEBAR: Discovery */}
            <div className="w-80 border-r border-white/5 flex flex-col bg-slate-900/30">
                <div className="p-6 border-b border-white/5">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Library</h3>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search indicators..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full bg-black/40 border border-white/10 rounded-xl pl-9 pr-4 h-10 text-sm text-white focus:border-blue-500/50 transition-all outline-none"
                        />
                    </div>
                </div>

                {/* Categories */}
                <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1 custom-scrollbar">
                    <button
                        onClick={() => setSelectedCategory(null)}
                        className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all ${selectedCategory === null
                            ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                            : 'text-gray-400 hover:bg-white/5 hover:text-white'
                            }`}
                    >
                        <span className="flex items-center gap-3">
                            <Filter className="w-4 h-4" />
                            All Categories
                        </span>
                        {selectedCategory === null && <ChevronRight className="w-4 h-4" />}
                    </button>

                    {categories.map(cat => {
                        const Icon = CATEGORY_ICONS[cat] || HelpCircle
                        const isSelected = selectedCategory === cat
                        return (
                            <button
                                key={cat}
                                onClick={() => setSelectedCategory(cat)}
                                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all ${isSelected
                                    ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                                    }`}
                            >
                                <span className="flex items-center gap-3 capitalize">
                                    <Icon className="w-4 h-4 opacity-70" />
                                    {cat}
                                </span>
                                {isSelected && <ChevronRight className="w-4 h-4" />}
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* MAIN CONTENT: List & Config */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <div className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-white/[0.02]">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-500/20">
                            <Code className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <input
                                type="text"
                                value={strategyName}
                                onChange={(e) => setStrategyName(e.target.value)}
                                className="bg-transparent text-xl font-bold text-white outline-none placeholder-gray-600 w-full"
                                placeholder="Strategy Name"
                            />
                            <p className="text-xs text-gray-500 flex items-center gap-2">
                                <span className={selectedIndicators.length > 0 ? "text-green-400" : "text-gray-600"}>●</span>
                                {selectedIndicators.length} indicators selected
                            </p>
                        </div>
                    </div>

                    <div className="flex bg-slate-900 rounded-lg p-1 border border-white/10">
                        <button
                            onClick={() => setActiveTab('indicators')}
                            className={`px-4 py-2 rounded-md text-xs font-semibold transition-all flex items-center gap-2 ${activeTab === 'indicators' ? 'bg-white/10 text-white shadow' : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            <Layout className="w-3.5 h-3.5" />
                            Indicators
                        </button>
                        <button
                            onClick={() => setActiveTab('logic')}
                            className={`px-4 py-2 rounded-md text-xs font-semibold transition-all flex items-center gap-2 ${activeTab === 'logic' ? 'bg-white/10 text-white shadow' : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            <Binary className="w-3.5 h-3.5" />
                            Logic Rules
                        </button>
                    </div>
                </div>

                {/* Content Area */}
                <div className="flex-1 overflow-hidden relative">

                    {/* INDICATORS TAB */}
                    {activeTab === 'indicators' && (
                        <div className="absolute inset-0 flex">
                            {/* Browser Grid */}
                            <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                                <h2 className="text-lg font-semibold mb-6">Select Indicators</h2>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {isLoading ? (
                                        // Skeletons
                                        Array.from({ length: 6 }).map((_, i) => (
                                            <div key={i} className="h-24 bg-white/5 rounded-xl animate-pulse" />
                                        ))
                                    ) : (
                                        filteredIndicators.map((ind) => (
                                            <button
                                                key={ind.name}
                                                onClick={() => handleAddIndicator(ind)}
                                                className="group relative flex flex-col items-start p-5 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.06] hover:border-blue-500/30 transition-all text-left"
                                            >
                                                <span className="text-sm font-bold text-gray-200 group-hover:text-blue-400 transition-colors uppercase tracking-wide">
                                                    {ind.name}
                                                </span>
                                                <span className="text-xs text-gray-500 mt-2 uppercase font-medium bg-black/30 px-2 py-1 rounded">
                                                    {ind.category}
                                                </span>
                                                <Plus className="absolute top-5 right-5 w-4 h-4 text-gray-600 group-hover:text-blue-500 opacity-0 group-hover:opacity-100 transition-all transform group-hover:rotate-90" />
                                            </button>
                                        ))
                                    )}
                                </div>
                            </div>

                            {/* Selected Config Panel */}
                            <div className="w-96 border-l border-white/5 bg-slate-900/30 flex flex-col">
                                <div className="p-6 border-b border-white/5">
                                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Active Configuration</h3>
                                </div>
                                <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                                    {selectedIndicators.length === 0 ? (
                                        <div className="text-center py-20 text-gray-600">
                                            <Layout className="w-12 h-12 mx-auto mb-4 opacity-20" />
                                            <p className="text-sm">No indicators selected</p>
                                        </div>
                                    ) : (
                                        selectedIndicators.map((item, idx) => (
                                            <div key={idx} className="bg-black/40 rounded-xl border border-white/10 overflow-hidden">
                                                <div className="bg-white/[0.02] px-4 py-3 flex items-center justify-between border-b border-white/5">
                                                    <span className="font-bold text-sm text-blue-400">{item.name}</span>
                                                    <button onClick={() => removeIndicator(idx)} className="text-gray-500 hover:text-red-400 transition-colors">
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                                <div className="p-4 space-y-4">
                                                    {Object.entries(item.params).map(([key, val]) => (
                                                        <div key={key}>
                                                            <div className="flex justify-between mb-1.5">
                                                                <label className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">{key}</label>
                                                                <span className="text-[10px] text-gray-600">{typeof val}</span>
                                                            </div>
                                                            {typeof val === 'number' || !isNaN(Number(val)) ? (
                                                                <input
                                                                    type="number"
                                                                    value={val}
                                                                    onChange={(e) => updateIndicatorParam(idx, key, Number(e.target.value))}
                                                                    className="w-full bg-slate-900 border border-white/10 rounded-lg px-3 h-8 text-xs text-white focus:border-blue-500/50 outline-none transition-all"
                                                                />
                                                            ) : (
                                                                <input
                                                                    type="text"
                                                                    value={val}
                                                                    onChange={(e) => updateIndicatorParam(idx, key, e.target.value)}
                                                                    className="w-full bg-slate-900 border border-white/10 rounded-lg px-3 h-8 text-xs text-white focus:border-blue-500/50 outline-none transition-all"
                                                                />
                                                            )}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* LOGIC TAB */}
                    {activeTab === 'logic' && (
                        <div className="p-8 max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="mb-8 text-center">
                                <h2 className="text-2xl font-bold text-white mb-2">Signal Logic</h2>
                                <p className="text-gray-400 text-sm">Define the conditions for entering and exiting trades using Python logical expressions.</p>
                            </div>

                            <div className="space-y-8">
                                {/* Available Variables */}
                                <div className="bg-blue-500/5 border border-blue-500/20 rounded-xl p-6">
                                    <h3 className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                                        <Code className="w-4 h-4" /> Available Variables
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedIndicators.map((ind, i) => (
                                            <span key={i} className="px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-lg text-xs font-mono text-blue-300">
                                                {ind.name.toLowerCase()}_length
                                            </span>
                                        ))}
                                        {['close', 'open', 'high', 'low', 'volume'].map(v => (
                                            <span key={v} className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs font-mono text-gray-400">
                                                {v}
                                            </span>
                                        ))}
                                    </div>
                                    <p className="mt-4 text-[11px] text-gray-500 leading-relaxed">
                                        Tip: Use standard Python comparison operators: <code className="text-gray-300 bg-white/5 px-1 rounded">{'>'}</code> <code className="text-gray-300 bg-white/5 px-1 rounded">{'<'}</code> <code className="text-gray-300 bg-white/5 px-1 rounded">{'=='}</code> <code className="text-gray-300 bg-white/5 px-1 rounded">{'and'}</code> <code className="text-gray-300 bg-white/5 px-1 rounded">{'or'}</code>
                                    </p>
                                </div>

                                {/* Entry Condition */}
                                <div className="group">
                                    <label className="flex items-center gap-3 mb-3">
                                        <span className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center border border-green-500/30">
                                            <Activity className="w-4 h-4 text-green-400" />
                                        </span>
                                        <span className="font-bold text-gray-200">Entry Condition (Buy)</span>
                                    </label>
                                    <textarea
                                        value={entryCondition}
                                        onChange={(e) => setEntryCondition(e.target.value)}
                                        className="w-full h-32 bg-black/40 border border-white/10 rounded-xl p-5 font-mono text-sm text-green-300 focus:border-green-500/50 focus:bg-black/60 outline-none transition-all resize-none shadow-inner"
                                        placeholder="e.g. RSI_14 < 30"
                                    />
                                </div>

                                {/* Exit Condition */}
                                <div className="group">
                                    <label className="flex items-center gap-3 mb-3">
                                        <span className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center border border-red-500/30">
                                            <Activity className="w-4 h-4 text-red-400" />
                                        </span>
                                        <span className="font-bold text-gray-200">Exit Condition (Sell)</span>
                                    </label>
                                    <textarea
                                        value={exitCondition}
                                        onChange={(e) => setExitCondition(e.target.value)}
                                        className="w-full h-32 bg-black/40 border border-white/10 rounded-xl p-5 font-mono text-sm text-red-300 focus:border-red-500/50 focus:bg-black/60 outline-none transition-all resize-none shadow-inner"
                                        placeholder="e.g. RSI_14 > 70"
                                    />
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer Controls */}
                <div className="h-20 border-t border-white/5 bg-slate-900/50 flex items-center justify-between px-8 backdrop-blur-md z-10">
                    <button
                        onClick={onCancel}
                        className="px-6 py-2.5 rounded-lg text-sm font-semibold text-gray-400 hover:text-white hover:bg-white/5 transition-all"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={selectedIndicators.length === 0}
                        className="px-8 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-xl shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 group"
                    >
                        <Save className="w-4 h-4 group-hover:scale-110 transition-transform" />
                        Save Strategy
                    </button>
                </div>
            </div>
        </div>
    )
}
