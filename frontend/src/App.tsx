import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { Layout } from './components/Layout'
import { ProtectedLayout } from './components/ProtectedLayout'
import { AuthLayout } from './components/AuthLayout'
import { AuthProvider } from './stores/authStore'
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
import ExternalBalancesPage from './pages/ExternalBalancesPage'
import KanbanPage from './pages/KanbanPage'
import SignalsPage from './pages/SignalsPage'
import SignalsHistoryPage from './pages/SignalsHistoryPage'
import LoginPage from './pages/LoginPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import { Toaster } from "@/components/ui/toaster"

function PrototypeRedirect({ to }: { to: string }) {
  useEffect(() => {
    // Force a full reload into the static prototype (served from Vite public/).
    window.location.replace(to)
  }, [to])

  return (
    <div style={{ padding: 16, fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' }}>
      Redirecting to prototype…
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/*
            Some static prototype links are shared without a trailing slash.
            In production, the server's SPA fallback can intercept that and serve the React app,
            resulting in a blank/empty route. Redirect to the real static directory URL.
          */}
          <Route
            path="/prototypes/improve-wallet-screen"
            element={<PrototypeRedirect to="/prototypes/improve-wallet-screen/" />}
          />

          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          </Route>

          <Route element={<ProtectedLayout />}>
            <Route element={<Layout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/favorites" element={<FavoritesDashboard />} />
              <Route path="/monitor" element={<MonitorPage />} />
              <Route path="/signals" element={<SignalsPage />} />
              <Route path="/signals/history" element={<SignalsHistoryPage />} />
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
              <Route path="/external/balances" element={<ExternalBalancesPage />} />
              <Route path="/kanban" element={<KanbanPage />} />
            </Route>
          </Route>
        </Routes>
        <Toaster />
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
