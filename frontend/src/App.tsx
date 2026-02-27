import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import HomePage from './pages/HomePage'
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
import ExternalBalancesPage from './pages/ExternalBalancesPage'
import KanbanPage from './pages/KanbanPage'
import { Toaster } from "@/components/ui/toaster"


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
          <Route path="/external/balances" element={<ExternalBalancesPage />} />
          <Route path="/kanban" element={<KanbanPage />} />
        </Route>
      </Routes>
      <Toaster />
    </BrowserRouter>
  )
}

export default App
