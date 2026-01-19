import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Layers, Sparkles, ArrowRight, Database } from 'lucide-react'

interface Template {
    name: string
    description: string
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
                                <p className="text-sm text-gray-400 mt-0.5">All strategies are database-driven</p>
                            </div>
                        </div>
                        <button
                            onClick={() => navigate('/')}
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            ← Back to Home
                        </button>
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
                                    <button
                                        key={template.name}
                                        onClick={() => handleSelectTemplate(template.name)}
                                        className={`glass-strong rounded-xl p-6 border transition-all duration-300 text-left group hover:scale-[1.02] ${selectedTemplate === template.name
                                            ? 'border-blue-500 bg-blue-500/10'
                                            : 'border-white/10 hover:border-blue-500/50'
                                            }`}
                                    >
                                        <div className="flex items-start justify-between mb-3">
                                            <div className="bg-blue-500/20 p-2 rounded-lg">
                                                <Layers className="w-5 h-5 text-blue-400" />
                                            </div>
                                            {selectedTemplate === template.name && (
                                                <div className="bg-blue-500 rounded-full p-1">
                                                    <ArrowRight className="w-4 h-4 text-white" />
                                                </div>
                                            )}
                                        </div>
                                        <h3 className="text-lg font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">
                                            {template.name.replace(/^Example: /, '').split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                                        </h3>
                                        <p className="text-sm text-gray-400 line-clamp-2">{template.description}</p>
                                    </button>
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
                                Continue with {selectedTemplate.replace(/^Example: /, '').split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                                <ArrowRight className="w-5 h-5" />
                            </button>
                        </div>
                    )}
                </div>
            </main>
        </div>
    )
}
