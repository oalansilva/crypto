import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import FavoritesDashboard from './pages/FavoritesDashboard'
import { MonitorPage } from './pages/MonitorPage'
import { ComboSelectPage } from './pages/ComboSelectPage'
import { ComboConfigurePage } from './pages/ComboConfigurePage'
import { ComboResultsPage } from './pages/ComboResultsPage'
import { ComboOptimizePage } from './pages/ComboOptimizePage'
import { ComboEditPage } from './pages/ComboEditPage'
import OpenSpecListPage from './pages/OpenSpecListPage'
import OpenSpecDetailPage from './pages/OpenSpecDetailPage'
import LabPage from './pages/LabPage'
import LabRunPage from './pages/LabRunPage'
import ArbitragePage from './pages/ArbitragePage'
import { Sparkles } from 'lucide-react'
import { Toaster } from "@/components/ui/toaster"

function HomePage() {
  const navigate = useNavigate()

  return (
    <main className="container mx-auto px-6 py-12">
        <div className="space-y-8 animate-in fade-in duration-500">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-4xl font-bold text-white mb-3">
              <span className="gradient-text">New Backtest</span>
            </h2>
            <p className="text-gray-400 text-lg">
              Configure your parameters and start testing your strategy
            </p>
          </div>

          <div className="mb-8">
            <div className="glass-strong rounded-2xl p-6 border border-white/10 hover:border-emerald-500/30 transition-all duration-300 group">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="relative">
                      <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg blur opacity-75 group-hover:opacity-100 transition-opacity"></div>
                      <div className="relative bg-gradient-to-br from-emerald-500 to-teal-600 p-2 rounded-lg">
                        <Sparkles className="w-5 h-5 text-white" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        Combo Strategies
                        <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] uppercase tracking-wider rounded border border-emerald-500/30 font-bold">
                          Novo
                        </span>
                      </h3>
                      <p className="text-sm text-gray-400 mt-0.5">
                        Combine múltiplos indicadores em uma estratégia
                      </p>
                    </div>
                  </div>
                  <p className="text-gray-300 text-sm mb-4">
                    Crie estratégias poderosas combinando vários indicadores (EMA, RSI, MACD, Bollinger, etc.) com lógica customizada. Escolha entre templates prontos ou crie o seu próprio.
                  </p>
                  <button
                    onClick={() => navigate('/combo/select')}
                    className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 inline-flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/30 group-hover:shadow-emerald-500/50 group-hover:scale-[1.02]"
                  >
                    <Sparkles className="w-5 h-5" />
                    Explorar Combo Strategies
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
    </main>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/favorites" element={<FavoritesDashboard />} />
          <Route path="/monitor" element={<MonitorPage />} />
          <Route path="/combo/select" element={<ComboSelectPage />} />
          {/* Backward-compat route (old link/bookmark) */}
          <Route path="/combo/selectCrypto" element={<ComboSelectPage />} />
          <Route path="/combo/edit/:templateName" element={<ComboEditPage />} />
          <Route path="/combo/configure" element={<ComboConfigurePage />} />
          <Route path="/combo/optimize" element={<ComboOptimizePage />} />
          <Route path="/combo/results" element={<ComboResultsPage />} />
          <Route path="/openspec" element={<OpenSpecListPage />} />
          {/* Catch-all to support nested specs like /openspec/backend/spec */}
          <Route path="/openspec/*" element={<OpenSpecDetailPage />} />
          <Route path="/lab" element={<LabPage />} />
          <Route path="/lab/runs/:runId" element={<LabRunPage />} />
          <Route path="/arbitrage" element={<ArbitragePage />} />
        </Route>
      </Routes>
      <Toaster />
    </BrowserRouter>
  )
}

export default App
