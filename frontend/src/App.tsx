import { useState } from 'react'
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { backtestApi } from './lib/api'
import { ResultsPage } from './pages/ResultsPage'
import { SimpleBacktestWizard } from './components/SimpleBacktestWizard'
import {
  Activity,
  TrendingUp,
  Clock,
  CheckCircle2,
  Sparkles,
  Pause,
  Play
} from 'lucide-react'

function HomePage() {
  const [activeTab, setActiveTab] = useState<'playground' | 'history'>('playground')
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: runs, isLoading: runsLoading } = useQuery({
    queryKey: ['runs'],
    queryFn: async () => {
      const response = await backtestApi.listRuns(10)
      return response.data
    },
    refetchInterval: 5000,
  })

  // Check for paused jobs on mount
  useState(() => {
    const checkPaused = async () => {
      try {
        const jobs = await backtestApi.listJobs()
        const paused = jobs.data.find((j: any) => j.status === 'PAUSED')
        if (paused) {
          const shouldResume = window.confirm(`Found paused simulation "${paused.job_id}". Resume now?`)
          if (shouldResume) {
            await backtestApi.resume(paused.job_id)
            setActiveTab('history')
            queryClient.invalidateQueries({ queryKey: ['runs'] })
          }
        }
      } catch (e) {
        console.error("Error checking paused jobs", e)
      }
    }
    checkPaused()
  }) // Run once

  const handleCustomBacktestSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['runs'] })
    setActiveTab('history')
  }

  const handlePause = async (runId: string) => {
    try {
      await backtestApi.pause(runId)
      queryClient.invalidateQueries({ queryKey: ['runs'] })
    } catch (e) {
      console.error("Failed to pause", e)
      alert("Falha ao pausar simulação")
    }
  }

  const handleResume = async (runId: string) => {
    try {
      await backtestApi.resume(runId)
      queryClient.invalidateQueries({ queryKey: ['runs'] })
    } catch (e) {
      console.error("Failed to resume", e)
      alert("Falha ao retomar simulação")
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'DONE': return 'text-emerald-400'
      case 'RUNNING': return 'text-blue-400'
      case 'PAUSADO':
      case 'PAUSED': return 'text-amber-400'
      case 'FAILED': return 'text-rose-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5"
    switch (status) {
      case 'DONE':
        return (
          <span className={`${baseClasses} bg-emerald-500/20 text-emerald-400 border border-emerald-500/30`}>
            <CheckCircle2 className="w-3 h-3" />
            Completed
          </span>
        )
      case 'RUNNING':
        return (
          <span className={`${baseClasses} bg-blue-500/20 text-blue-400 border border-blue-500/30`}>
            <Activity className="w-3 h-3 animate-spin" />
            Running
          </span>
        )
      case 'PAUSED':
      case 'PAUSADO':
        return (
          <span className={`${baseClasses} bg-amber-500/20 text-amber-400 border border-amber-500/30`}>
            <div className="flex gap-1">
              <span className="w-1.5 h-3 bg-amber-400 rounded-sm inline-block" />
              <span className="w-1.5 h-3 bg-amber-400 rounded-sm inline-block" />
            </div>
            Paused
          </span>
        )
      case 'FAILED':
        return (
          <span className={`${baseClasses} bg-rose-500/20 text-rose-400 border border-rose-500/30`}>
            <Clock className="w-3 h-3" />
            Failed
          </span>
        )
      default:
        return (
          <span className={`${baseClasses} bg-gray-500/20 text-gray-400 border border-gray-500/30`}>
            <Clock className="w-3 h-3" />
            Pending
          </span>
        )
    }
  }



  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '4s' }}></div>
      </div>

      {/* Header */}
      <header className="glass-strong border-b border-white/10 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl blur opacity-75 animate-pulse"></div>
                <div className="relative bg-gradient-to-br from-blue-500 to-purple-600 p-2.5 rounded-xl shadow-glow-blue">
                  <TrendingUp className="w-7 h-7 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-bold gradient-text">Crypto Backtester</h1>
                <p className="text-sm text-gray-400 mt-0.5">Professional Trading Analysis</p>
              </div>
            </div>

            <div className="flex gap-2 glass p-1.5 rounded-xl">
              <button
                onClick={() => setActiveTab('playground')}
                className={`px-6 py-2.5 rounded-lg font-semibold transition-all duration-300 ${activeTab === 'playground'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-glow-blue'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
              >
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Playground
                </div>
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-6 py-2.5 rounded-lg font-semibold transition-all duration-300 ${activeTab === 'history'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-glow-blue'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
              >
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  History
                </div>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        {activeTab === 'playground' && (
          <div className="space-y-8 animate-in fade-in duration-500">
            <div className="text-center max-w-2xl mx-auto mb-12">
              <h2 className="text-4xl font-bold text-white mb-3">
                <span className="gradient-text">New Backtest</span>
              </h2>
              <p className="text-gray-400 text-lg">
                Configure your parameters and start testing your strategy
              </p>
            </div>

            {/* Wizard Component */}
            <SimpleBacktestWizard onSuccess={handleCustomBacktestSuccess} />
          </div>
        )}

        {activeTab === 'history' && (
          <div className="space-y-8 animate-in fade-in duration-500">
            <div className="text-center max-w-2xl mx-auto">
              <h2 className="text-4xl font-bold text-white mb-3">
                Backtest <span className="gradient-text">History</span>
              </h2>
              <p className="text-gray-400 text-lg">
                Track and analyze your previous backtests
              </p>
            </div>

            {runsLoading ? (
              <div className="flex flex-col items-center justify-center py-20">
                <Activity className="w-12 h-12 animate-spin text-blue-400 mb-4" />
                <p className="text-gray-400">Loading history...</p>
              </div>
            ) : runs && runs.length > 0 ? (
              <div className="glass-strong rounded-2xl overflow-hidden border border-white/10">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                          Symbol
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                          Timeframe
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                          Strategies
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                          Created
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {runs.map((run) => (
                        <tr key={run.id} className="hover:bg-white/5 transition-colors">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex flex-col gap-2">
                              <div>{getStatusBadge(run.status)}</div>
                              {run.status === 'RUNNING' && (
                                <div className="space-y-1.5 min-w-[140px]">
                                  <div className="flex items-center justify-between text-xs">
                                    <div className="flex items-center gap-1.5 text-blue-300 font-medium">
                                      <Activity className="w-3 h-3 animate-spin" />
                                      Running
                                    </div>
                                    <span className="text-blue-400 font-bold">{Math.round(run.progress || 0)}%</span>
                                  </div>

                                  {/* Progress Bar */}
                                  <div className="w-full h-1.5 bg-blue-900/30 rounded-full overflow-hidden border border-blue-500/10">
                                    <div
                                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500 ease-out rounded-full"
                                      style={{ width: `${run.progress || 0}%` }}
                                    />
                                  </div>

                                  {run.message && (
                                    <div className="text-[10px] text-gray-400 truncate max-w-[140px]" title={run.message}>
                                      {run.message}
                                    </div>
                                  )}
                                </div>
                              )}
                              {(run.status === 'PAUSED' || run.status === 'PAUSADO') && (
                                <div className="space-y-1.5 min-w-[140px]">
                                  <div className="flex items-center justify-between text-xs">
                                    <div className="flex items-center gap-1.5 text-amber-300 font-medium">
                                      Paused
                                    </div>
                                    <span className="text-amber-400 font-bold">{Math.round(run.progress || 0)}%</span>
                                  </div>
                                  <div className="w-full h-1.5 bg-amber-900/30 rounded-full overflow-hidden border border-amber-500/10">
                                    <div
                                      className="h-full bg-amber-500 transition-all duration-500 ease-out rounded-full"
                                      style={{ width: `${run.progress || 0}%` }}
                                    />
                                  </div>
                                </div>
                              )}
                              {run.status === 'FAILED' && run.message && (
                                <div className="text-xs text-rose-300 max-w-[200px] truncate" title={run.message}>
                                  {run.message}
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-white font-semibold">{run.symbol}</span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-gray-300">{run.timeframe}</span>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex flex-wrap gap-1">
                              {run.strategies.map((strategy, i) => (
                                <span
                                  key={i}
                                  className="px-2 py-1 bg-blue-500/10 text-blue-400 text-xs rounded-md border border-blue-500/20"
                                >
                                  {typeof strategy === 'string' ? strategy : strategy.name || 'Custom'}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                            {new Date(run.created_at).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {run.status === 'DONE' && (
                              <button
                                onClick={() => navigate(`/results/${run.id}`)}
                                className="text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1 group"
                              >
                                Ver Resultados
                              </button>
                            )}
                            {(run.status === 'RUNNING' || run.status === 'PENDING') && (
                              <button
                                onClick={() => handlePause(run.id)}
                                className="px-3 py-1.5 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-lg hover:bg-amber-500/20 transition-all text-xs font-semibold flex items-center gap-1.5"
                              >
                                <Pause className="w-3.5 h-3.5" />
                                Pausar
                              </button>
                            )}

                            {(run.status === 'PAUSED' || run.status === 'PAUSADO') && (
                              <button
                                onClick={() => handleResume(run.id)}
                                className="px-3 py-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-lg hover:bg-emerald-500/20 transition-all text-xs font-semibold flex items-center gap-1.5"
                              >
                                <Play className="w-3.5 h-3.5" />
                                Continuar
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="glass-strong rounded-2xl p-16 text-center border border-white/10">
                <Clock className="w-16 h-16 mx-auto text-gray-600 mb-4 opacity-50" />
                <h3 className="text-xl font-semibold text-white mb-2">No backtests yet</h3>
                <p className="text-gray-400 mb-6">Start by running a preset from the Playground</p>
                <button
                  onClick={() => setActiveTab('playground')}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-3 px-8 rounded-xl transition-all duration-300 inline-flex items-center gap-2"
                >
                  <Sparkles className="w-5 h-5" />
                  Go to Playground
                </button>
              </div>
            )}
          </div>
        )}
      </main>


    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/results/:runId" element={<ResultsPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
