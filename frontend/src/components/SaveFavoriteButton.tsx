import React, { useState } from 'react';
import { Bookmark, Save, X } from 'lucide-react';

interface SaveFavoriteButtonProps {
    config: {
        symbol: string;
        timeframe: string;
        strategy_name: string;
        parameters: Record<string, any>;
    };
    metrics: Record<string, any>;
    variant?: 'icon' | 'button'; // 'icon' for table row, 'button' for hero card
    className?: string; // Additional classes
}

const SaveFavoriteButton: React.FC<SaveFavoriteButtonProps> = ({ config, metrics, variant = 'button', className = '' }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [name, setName] = useState('');
    const [notes, setNotes] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [saved, setSaved] = useState(false);

    // Default Name Auto-generation
    const generateDefaultName = () => {
        const timestamp = new Date().toLocaleTimeString();
        return `${config.strategy_name} - ${config.symbol} ${config.timeframe} (${timestamp})`;
    };

    const handleOpen = () => {
        if (!name) setName(generateDefaultName());
        setIsModalOpen(true);
        setSaved(false);
    };

    const handleSave = async () => {
        setIsSaving(true);
        try {
            const payload = {
                name,
                symbol: config.symbol,
                timeframe: config.timeframe,
                strategy_name: config.strategy_name,
                parameters: config.parameters,
                metrics: metrics,
                notes: notes
            };

            console.log('💾 Saving favorite with payload:', payload);
            console.log('   max_loss in metrics:', metrics.max_loss);

            const response = await fetch('http://localhost:8000/api/favorites/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Failed to save');

            setSaved(true);
            setTimeout(() => {
                setIsModalOpen(false);
                setSaved(false);
            }, 1000); // Close after 1s success feedback
        } catch (err) {
            console.error(err);
            alert('Error saving favorite');
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <>
            {/* Trigger Button */}
            {variant === 'button' ? (
                <button
                    onClick={handleOpen}
                    className={`flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors ${className}`}
                >
                    <Bookmark className="w-4 h-4" />
                    Save Strategy
                </button>
            ) : (
                <button
                    onClick={handleOpen}
                    className={`p-2 hover:bg-purple-500/20 text-purple-400 rounded-lg transition-colors ${className}`}
                    title="Save to Favorites"
                >
                    <Bookmark className="w-4 h-4" />
                </button>
            )}

            {/* Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <div className="bg-gray-800 rounded-2xl border border-gray-700 w-full max-w-md p-6 shadow-2xl">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Bookmark className="w-5 h-5 text-purple-400" />
                                Save Strategy
                            </h3>
                            <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Name</label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none"
                                    placeholder="My Winning Strat"
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Notes (Optional)</label>
                                <textarea
                                    value={notes}
                                    onChange={(e) => setNotes(e.target.value)}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none h-24 resize-none"
                                    placeholder="Detailed description..."
                                />
                            </div>

                            {/* Summary Preview */}
                            <div className="bg-gray-900/50 rounded-lg p-3 text-xs text-gray-400">
                                <p><strong>Params:</strong> {Object.keys(config.parameters).length} items</p>
                                <p><strong>Metrics:</strong> Sharpe: {metrics.sharpe_ratio?.toFixed(2) || 'N/A'}, Return: {metrics.total_return_pct?.toFixed(2) || 'N/A'}%</p>
                            </div>

                            <button
                                onClick={handleSave}
                                disabled={isSaving || saved}
                                className={`w-full py-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all ${saved
                                    ? 'bg-green-500 text-white'
                                    : 'bg-purple-600 hover:bg-purple-700 text-white'
                                    }`}
                            >
                                {saved ? (
                                    <>Saved! ✓</>
                                ) : (
                                    <>
                                        {isSaving ? 'Saving...' : 'Save Configuration'}
                                        {!isSaving && <Save className="w-4 h-4" />}
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default SaveFavoriteButton;
