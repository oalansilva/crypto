import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Layers, Sparkles, ArrowRight, Database, Edit, Copy, Settings, Lock, Unlock, X, Trash2, Play } from 'lucide-react'

interface Template {
    name: string
    description: string
    is_readonly: boolean
}

interface TemplateList {
    prebuilt: Template[]
    examples: Template[]
    custom: Template[]
}

export function ComboSelectPage() {
    const navigate = useNavigate()
    const [templates, setTemplates] = useState<TemplateList | null>(null)
    const [loading, setLoading] = useState(true)
    const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)

    // Clone modal state
    const [cloneModalOpen, setCloneModalOpen] = useState(false)
    const [templateToClone, setTemplateToClone] = useState<string | null>(null)
    const [newTemplateName, setNewTemplateName] = useState('')
    const [cloning, setCloning] = useState(false)

    // Combine all templates into a single array
    const allTemplates = templates
        ? [...templates.prebuilt, ...templates.examples, ...templates.custom]
        : []

    useEffect(() => {
        fetchTemplates()
    }, [])

    const fetchTemplates = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/combos/templates')
            const data = await response.json()
            setTemplates(data)
        } catch (error) {
            console.error('Failed to fetch templates:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSelectTemplate = (templateName: string) => {
        setSelectedTemplate(templateName)
    }

    const handleContinue = () => {
        if (selectedTemplate) {
            navigate(`/combo/configure?template=${encodeURIComponent(selectedTemplate)}`)
        }
    }

    const handleEdit = (e: React.MouseEvent, template: Template) => {
        e.stopPropagation()
        if (template.is_readonly) {
            // If read-only, open clone modal
            setTemplateToClone(template.name)
            setNewTemplateName(`${template.name}_copy`)
            setCloneModalOpen(true)
        } else {
            // If editable, go to edit page
            navigate(`/combo/edit/${encodeURIComponent(template.name)}`)
        }
    }

    const handleClone = (e: React.MouseEvent, templateName: string) => {
        e.stopPropagation()
        setTemplateToClone(templateName)
        setNewTemplateName(`${templateName}_copy`)
        setCloneModalOpen(true)
    }

    const handleDelete = async (e: React.MouseEvent, templateName: string) => {
        e.stopPropagation()
        if (window.confirm(`Are you sure you want to delete "${templateName}"? This cannot be undone.`)) {
            try {
                const response = await fetch(`http://localhost:8000/api/combos/meta/${templateName}`, {
                    method: 'DELETE'
                })
                if (response.ok) {
                    await fetchTemplates()
                    if (selectedTemplate === templateName) setSelectedTemplate(null)
                } else {
                    alert("Failed to delete template")
                }
            } catch (error) {
                console.error("Delete error", error)
                alert("Error deleting template")
            }
        }
    }

    // Submit Clone Logic
    const submitClone = async () => {
        if (!templateToClone || !newTemplateName) return

        setCloning(true)
        try {
            const response = await fetch(`http://localhost:8000/api/combos/meta/${templateToClone}/clone`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_name: newTemplateName })
            })

            if (!response.ok) {
                const error = await response.json()
                throw new Error(error.detail || 'Failed to clone template')
            }

            // Success - navigate to edit page of new template
            setCloneModalOpen(false)
            navigate(`/combo/edit/${encodeURIComponent(newTemplateName)}`)
        } catch (error: any) {
            console.error('Clone error:', error)
            alert(`Error cloning template: ${error.message}`)
        } finally {
            setCloning(false)
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <Sparkles className="w-12 h-12 animate-spin text-blue-400 mx-auto mb-4" />
                    <p className="text-gray-400">Loading templates...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen relative overflow-hidden">
            {/* Animated background */}
            <div className="fixed inset-0 -z-10">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-float"></div>
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
            </div>

            {/* Header */}
            <header className="glass-strong border-b border-white/10 sticky top-0 z-50">
                <div className="container mx-auto px-6 py-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="relative">
                                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl blur opacity-75 animate-pulse"></div>
                                <div className="relative bg-gradient-to-br from-blue-500 to-purple-600 p-2.5 rounded-xl shadow-glow-blue">
                                    <Layers className="w-7 h-7 text-white" />
                                </div>
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold gradient-text">Combo Strategies</h1>
                                <p className="text-sm text-gray-400 mt-0.5">Select a template to backtest or edit</p>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-6 py-12">
                <div className="max-w-6xl mx-auto space-y-8">
                    {/* Unified Templates Section */}
                    <section>
                        <div className="flex items-center gap-3 mb-6">
                            <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-2 rounded-lg">
                                <Database className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">Available Templates</h2>
                                <p className="text-sm text-gray-400">{allTemplates.length} strategies stored in database</p>
                            </div>
                        </div>

                        {allTemplates.length === 0 ? (
                            <div className="glass-strong rounded-xl p-12 text-center">
                                <Database className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                                <p className="text-gray-400">No templates available</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {allTemplates.map((template) => (
                                    <div
                                        key={template.name}
                                        onClick={() => handleSelectTemplate(template.name)}
                                        className={`relative glass-strong rounded-xl p-6 border transition-all duration-300 text-left group hover:scale-[1.02] cursor-pointer ${selectedTemplate === template.name
                                            ? 'border-blue-500 bg-blue-500/10'
                                            : 'border-white/10 hover:border-blue-500/50'
                                            }`}
                                    >
                                        <div className="flex items-start justify-between mb-3">
                                            <div className="flex items-center gap-2">
                                                <div className="bg-blue-500/20 p-2 rounded-lg">
                                                    <Layers className="w-5 h-5 text-blue-400" />
                                                </div>
                                                {template.is_readonly ? (
                                                    <div className="p-1.5 rounded-md bg-gray-500/20" title='Read-Only (Clone to edit)'>
                                                        <Lock className="w-3 h-3 text-gray-400" />
                                                    </div>
                                                ) : (
                                                    <div className="p-1.5 rounded-md bg-green-500/20" title='Editable'>
                                                        <Unlock className="w-3 h-3 text-green-400" />
                                                    </div>
                                                )}
                                            </div>

                                            <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        navigate(`/combo/configure?template=${encodeURIComponent(template.name)}`);
                                                    }}
                                                    className="p-1.5 hover:bg-white/10 rounded-md transition-colors"
                                                    title="Run Strategy"
                                                >
                                                    <Play className="w-4 h-4 text-green-400" />
                                                </button>

                                                <button
                                                    onClick={(e) => handleEdit(e, template)}
                                                    className="p-1.5 hover:bg-white/10 rounded-md transition-colors"
                                                    title={template.is_readonly ? "Clone & Edit" : "Edit Template"}
                                                >
                                                    {template.is_readonly ? <Copy className="w-4 h-4 text-purple-400" /> : <Edit className="w-4 h-4 text-blue-400" />}
                                                </button>

                                                {!template.is_readonly && (
                                                    <button
                                                        onClick={(e) => handleDelete(e, template.name)}
                                                        className="p-1.5 hover:bg-white/10 rounded-md transition-colors"
                                                        title="Delete Template"
                                                    >
                                                        <Trash2 className="w-4 h-4 text-red-400" />
                                                    </button>
                                                )}

                                                <button
                                                    onClick={(e) => handleClone(e, template.name)}
                                                    className="p-1.5 hover:bg-white/10 rounded-md transition-colors"
                                                    title="Clone Template"
                                                >
                                                    <Copy className="w-4 h-4 text-gray-400 hover:text-white" />
                                                </button>
                                            </div>
                                        </div>

                                        <h3 className="text-lg font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">
                                            {template.name.replace(/^Example: /, '').split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                                        </h3>
                                        <p className="text-sm text-gray-400 line-clamp-2">{template.description}</p>

                                        {selectedTemplate === template.name && (
                                            <div className="absolute top-4 right-4 bg-blue-500 rounded-full p-1 animate-in fade-in zoom-in">
                                                <ArrowRight className="w-4 h-4 text-white" />
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>

                    {/* Continue Button */}
                    {selectedTemplate && (
                        <div className="flex justify-center pt-8 animate-in fade-in duration-500">
                            <button
                                onClick={handleContinue}
                                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 flex items-center gap-3 shadow-lg shadow-blue-500/50 hover:scale-105"
                            >
                                Continue with Backtest
                                <ArrowRight className="w-5 h-5" />
                            </button>
                        </div>
                    )}
                </div>
            </main>

            {/* Clone Modal */}
            {cloneModalOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setCloneModalOpen(false)}></div>
                    <div className="relative glass-strong rounded-2xl p-6 w-full max-w-md border border-white/20 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
                        <button
                            onClick={() => setCloneModalOpen(false)}
                            className="absolute top-4 right-4 text-gray-400 hover:text-white"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                            <Copy className="w-5 h-5 text-purple-400" />
                            Clone Template
                        </h2>
                        <p className="text-gray-400 text-sm mb-6">
                            Create a copy of <span className="font-mono text-blue-300">{templateToClone}</span> to customize it.
                        </p>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                                    New Template Name
                                </label>
                                <input
                                    type="text"
                                    value={newTemplateName}
                                    onChange={(e) => setNewTemplateName(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-white focus:border-purple-500 outline-none font-mono text-sm"
                                    placeholder="my_strategy_copy"
                                    autoFocus
                                />
                            </div>

                            <div className="flex gap-3 pt-2">
                                <button
                                    onClick={() => setCloneModalOpen(false)}
                                    className="flex-1 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={submitClone}
                                    disabled={!newTemplateName || cloning}
                                    className="flex-1 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-semibold transition-colors flex items-center justify-center gap-2"
                                >
                                    {cloning ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : null}
                                    Clone & Edit
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
