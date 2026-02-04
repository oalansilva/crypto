import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Settings, Save, ArrowLeft, AlertTriangle, Check, Code, Type } from 'lucide-react'
import Editor from '@monaco-editor/react'
import { API_BASE_URL } from '../lib/apiBase'

interface ParamConfig {
    min: number
    max: number
    step: number
    default?: number
}

interface TemplateMetadata {
    name: string
    description: string
    indicators: any[]
    entry_logic: string
    exit_logic: string
    is_readonly: boolean
    optimization_schema: {
        parameters?: Record<string, ParamConfig>
        [key: string]: any
    }
    [key: string]: any
}

/** Backend can return flat schema (multi_ma_crossover, multi_ma_crossoverV2) or nested .parameters. Normalize to params map. */
function getOptimizationParameters(schema: TemplateMetadata['optimization_schema'] | null | undefined): Record<string, ParamConfig> {
    if (!schema || typeof schema !== 'object') return {}
    if (schema.parameters && typeof schema.parameters === 'object') return schema.parameters
    const flat = schema as Record<string, unknown>
    const result: Record<string, ParamConfig> = {}
    for (const [k, v] of Object.entries(flat)) {
        if (v && typeof v === 'object' && 'min' in v && 'max' in v)
            result[k] = v as ParamConfig
    }
    return result
}

export function ComboEditPage() {
    const navigate = useNavigate()
    const { templateName } = useParams()

    const [metadata, setMetadata] = useState<TemplateMetadata | null>(null)
    const [originalMetadata, setOriginalMetadata] = useState<TemplateMetadata | null>(null)
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [advancedMode, setAdvancedMode] = useState(false)

    const [jsonContent, setJsonContent] = useState('')
    const [jsonError, setJsonError] = useState<string | null>(null)
    const [formErrors, setFormErrors] = useState<Record<string, string>>({})

    useEffect(() => {
        if (templateName) {
            fetchMetadata()
        }
    }, [templateName])

    // Update JSON content when metadata changes (switching modes)
    useEffect(() => {
        if (metadata) {
            setJsonContent(JSON.stringify(metadata, null, 2))
        }
    }, [metadata])

    const fetchMetadata = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/combos/meta/${templateName}`)
            if (!response.ok) throw new Error('Failed to fetch template')

            const data = await response.json()
            setMetadata(data)
            setOriginalMetadata(data)
            setJsonContent(JSON.stringify(data, null, 2))
        } catch (error) {
            console.error('Error fetching metadata:', error)
            alert('Failed to load template')
            navigate('/combo/select')
        } finally {
            setLoading(false)
        }
    }

    const validateForm = (data: TemplateMetadata): boolean => {
        const errors: Record<string, string> = {}
        let isValid = true

        // Validate description
        if (data.description && data.description.length > 500) {
            errors['description'] = 'Description too long (max 500 chars)'
            isValid = false
        }

        // Validate parameters (supports both nested .parameters and flat schema)
        const params = getOptimizationParameters(data.optimization_schema)
        if (Object.keys(params).length > 0) {
            Object.entries(params).forEach(([paramName, config]) => {
                if (config.min >= config.max) {
                    errors[paramName] = `Min (${config.min}) must be less than Max (${config.max})`
                    isValid = false
                }
                if (config.step <= 0) {
                    errors[paramName] = `Step (${config.step}) must be greater than 0`
                    isValid = false
                }
                if (config.step > (config.max - config.min)) {
                    errors[paramName] = `Step cannot contain range (Max - Min)`
                    isValid = false
                }
            })
        }

        setFormErrors(errors)
        return isValid
    }

    const handleSave = async () => {
        setSaving(true)
        setFormErrors({})
        setJsonError(null)

        try {
            let payload: any = {}

            if (advancedMode) {
                // Parse JSON from editor
                try {
                    const parsed = JSON.parse(jsonContent)
                    // Basic structure validation could go here
                    payload = {
                        description: parsed.description,
                        optimization_schema: parsed.optimization_schema,
                        template_data: parsed // Send full object for structure updates
                    }
                } catch (e: any) {
                    setJsonError(`Invalid JSON: ${e.message}`)
                    setSaving(false)
                    return
                }
            } else {
                // Use form state
                if (!metadata || !validateForm(metadata)) {
                    setSaving(false)
                    return
                }
                payload = {
                    description: metadata.description,
                    optimization_schema: metadata.optimization_schema
                }
            }

            const response = await fetch(`${API_BASE_URL}/combos/meta/${templateName}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })

            if (!response.ok) {
                const error = await response.json()
                throw new Error(error.detail || 'Failed to update template')
            }

            // Success
            alert('Template updated successfully!')
            navigate('/combo/select')

        } catch (error: any) {
            console.error('Save error:', error)
            alert(`Error saving template: ${error.message}`)
        } finally {
            setSaving(false)
        }
    }

    const handleParamChange = (paramName: string, field: 'min' | 'max' | 'step', value: string) => {
        if (!metadata) return

        const numValue = parseFloat(value)
        const currentParams = getOptimizationParameters(metadata.optimization_schema)
        const newParams = { ...currentParams }

        newParams[paramName] = {
            ...newParams[paramName],
            [field]: isNaN(numValue) ? 0 : numValue
        }

        const newMetadata = {
            ...metadata,
            optimization_schema: {
                ...metadata.optimization_schema,
                parameters: newParams
            }
        }

        setMetadata(newMetadata)

        // Live validation
        if (formErrors[paramName]) {
            const tempErrors = { ...formErrors }
            delete tempErrors[paramName]
            setFormErrors(tempErrors)
        }
    }

    if (loading) return <div className="p-10 text-center text-white">Loading editor...</div>
    if (!metadata) return null

    if (metadata.is_readonly) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center glass-strong p-8 rounded-2xl max-w-md">
                    <AlertTriangle className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-white mb-2">Read-Only Template</h2>
                    <p className="text-gray-400 mb-6">
                        This is a system template and cannot be edited directly. Please clone it to make changes.
                    </p>
                    <button
                        onClick={() => navigate('/combo/select')}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
                    >
                        Go Back
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen relative pb-20">
            {/* Background */}
            <div className="fixed inset-0 -z-10 bg-gradient-to-br from-gray-900 to-black"></div>

            {/* Header */}
            <header className="glass-strong border-b border-white/10 sticky top-0 z-50">
                <div className="container mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => navigate('/combo/select')}
                                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                            >
                                <ArrowLeft className="w-5 h-5 text-gray-400" />
                            </button>
                            <div>
                                <h1 className="text-xl font-bold text-white">Edit Strategy</h1>
                                <p className="text-xs text-blue-400 font-mono mt-0.5">{metadata.name}</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            {/* Mode Toggle */}
                            <div className="bg-black/40 p-1 rounded-lg flex items-center border border-white/10">
                                <button
                                    onClick={() => setAdvancedMode(false)}
                                    className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center gap-2 transition-all ${!advancedMode ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
                                        }`}
                                >
                                    <Type className="w-3 h-3" />
                                    Visual
                                </button>
                                <button
                                    onClick={() => setAdvancedMode(true)}
                                    className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center gap-2 transition-all ${advancedMode ? 'bg-purple-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'
                                        }`}
                                >
                                    <Code className="w-3 h-3" />
                                    JSON
                                </button>
                            </div>

                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white px-6 py-2 rounded-lg font-bold flex items-center gap-2 transition-all"
                            >
                                {saving ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Save className="w-4 h-4" />}
                                Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-6 py-8">
                {advancedMode ? (
                    // JSON Editor Mode
                    <div className="h-[80vh] glass-strong rounded-xl border border-white/10 overflow-hidden">
                        <Editor
                            height="100%"
                            defaultLanguage="json"
                            theme="vs-dark"
                            value={jsonContent}
                            onChange={(value) => {
                                setJsonContent(value || '')
                                setJsonError(null)
                            }}
                            options={{
                                minimap: { enabled: false },
                                fontSize: 13,
                                formatOnPaste: true,
                                formatOnType: true
                            }}
                        />
                        {jsonError && (
                            <div className="absolute bottom-4 left-4 right-4 bg-red-500/90 text-white p-3 rounded-lg text-sm font-mono backdrop-blur-md border border-red-400 shadow-xl animate-shake">
                                {jsonError}
                            </div>
                        )}
                    </div>
                ) : (
                    // Visual Form Mode
                    <div className="max-w-3xl mx-auto space-y-6">
                        {/* Description */}
                        <div className="glass-strong p-6 rounded-xl border border-white/10">
                            <label className="block text-sm font-medium text-gray-400 mb-2">Description</label>
                            <textarea
                                value={metadata.description}
                                onChange={(e) => setMetadata({ ...metadata, description: e.target.value })}
                                className="w-full bg-black/30 border border-white/10 rounded-lg p-3 text-white focus:border-blue-500 focus:outline-none h-24 text-sm"
                                placeholder="Strategy description..."
                            />
                            {formErrors.description && (
                                <p className="text-red-400 text-xs mt-1">{formErrors.description}</p>
                            )}
                        </div>

                        {/* Optimization Parameters */}
                        <div className="space-y-4">
                            <h2 className="text-lg font-bold text-white flex items-center gap-2">
                                <Settings className="w-5 h-5 text-purple-400" />
                                Optimization Ranges
                            </h2>

                            {(() => {
                                const params = getOptimizationParameters(metadata?.optimization_schema)
                                const entries = Object.entries(params)
                                if (entries.length === 0) return <p className="text-gray-500 text-sm">No optimization ranges defined for this template.</p>
                                return entries.map(([paramName, config]) => (
                                <div key={paramName} className={`glass-strong p-4 rounded-xl border transition-all ${formErrors[paramName] ? 'border-red-500/50 bg-red-500/5' : 'border-white/5'}`}>
                                    <div className="flex justify-between items-center mb-3">
                                        <h3 className="font-mono text-blue-300 text-sm">{paramName}</h3>
                                        <div className="text-xs text-gray-500">
                                            Current Default: {config.default ?? '—'}
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-3 gap-4">
                                        <div>
                                            <label className="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1 block">Min</label>
                                            <input
                                                type="number"
                                                step={config.step}
                                                value={config.min}
                                                onChange={(e) => handleParamChange(paramName, 'min', e.target.value)}
                                                className="w-full bg-black/40 border border-white/10 rounded px-2 py-1.5 text-sm text-white focus:border-purple-500 outline-none"
                                            />
                                        </div>
                                        <div>
                                            <label className="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1 block">Max</label>
                                            <input
                                                type="number"
                                                step={config.step}
                                                value={config.max}
                                                onChange={(e) => handleParamChange(paramName, 'max', e.target.value)}
                                                className="w-full bg-black/40 border border-white/10 rounded px-2 py-1.5 text-sm text-white focus:border-purple-500 outline-none"
                                            />
                                        </div>
                                        <div>
                                            <label className="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1 block">Step</label>
                                            <input
                                                type="number"
                                                value={config.step}
                                                onChange={(e) => handleParamChange(paramName, 'step', e.target.value)}
                                                className="w-full bg-black/40 border border-white/10 rounded px-2 py-1.5 text-sm text-white focus:border-purple-500 outline-none"
                                            />
                                        </div>
                                    </div>

                                    {formErrors[paramName] && (
                                        <div className="mt-3 flex items-center gap-2 text-red-400 text-xs bg-red-500/10 p-2 rounded">
                                            <AlertTriangle className="w-3 h-3" />
                                            {formErrors[paramName]}
                                        </div>
                                    )}
                                </div>
                            ))
                            })()}
                        </div>
                    </div>
                )}
            </main>
        </div>
    )
}
