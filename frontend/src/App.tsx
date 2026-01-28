import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import FavoritesDashboard from './pages/FavoritesDashboard'
import { MonitorPage } from './pages/MonitorPage'
import { ComboSelectPage } from './pages/ComboSelectPage'
import { ComboConfigurePage } from './pages/ComboConfigurePage'
import { ComboResultsPage } from './pages/ComboResultsPage'
import { ComboOptimizePage } from './pages/ComboOptimizePage'
import { ComboEditPage } from './pages/ComboEditPage'
import { Activity, TrendingUp, Sparkles, Bookmark } from 'lucide-react'
import { Toaster } from "@/components/ui/toaster"

function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="fixed inset-0 -z-10">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '4s' }}></div>
      </div>

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
                onClick={() => navigate('/')}
                className="px-6 py-2.5 rounded-lg font-semibold transition-all duration-300 bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-glow-blue"
              >
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Playground
                </div>
              </button>
              <button
                onClick={() => navigate('/favorites')}
                className="px-6 py-2.5 rounded-lg font-semibold transition-all duration-300 text-gray-400 hover:text-white hover:bg-white/5"
              >
                <div className="flex items-center gap-2">
                  <Bookmark className="w-4 h-4" />
                  Favorites
                </div>
              </button>
              <button
                onClick={() => navigate('/monitor')}
                className="px-6 py-2.5 rounded-lg font-semibold transition-all duration-300 text-gray-400 hover:text-white hover:bg-white/5"
              >
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  Monitor
                </div>
              </button>
            </div>
          </div>
        </div>
      </header>

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
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/favorites" element={<FavoritesDashboard />} />
        <Route path="/monitor" element={<MonitorPage />} />
        <Route path="/combo/select" element={<ComboSelectPage />} />
        <Route path="/combo/edit/:templateName" element={<ComboEditPage />} />
        <Route path="/combo/configure" element={<ComboConfigurePage />} />
        <Route path="/combo/optimize" element={<ComboOptimizePage />} />
        <Route path="/combo/results" element={<ComboResultsPage />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  )
}

export default App
