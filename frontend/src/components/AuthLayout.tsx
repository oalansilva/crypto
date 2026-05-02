import { Outlet } from 'react-router-dom'
import { TrendingUp } from 'lucide-react'

export function AuthLayout() {
  return (
    <div className="relative min-h-screen w-full overflow-hidden font-sans text-[var(--text-primary)] selection:bg-[rgba(252,213,53,0.28)] selection:text-[var(--text-on-primary)]">
      {/* Background */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[var(--bg-primary)]" />
        <div
          className="absolute inset-x-0 top-0 h-56 opacity-80"
          style={{
            backgroundImage: `
              linear-gradient(180deg, rgba(252, 213, 53, 0.16) 0%, rgba(11, 14, 17, 0) 100%)
            `,
          }}
        />
      </div>

      {/* Header */}
      <header className="fixed top-0 inset-x-0 z-50 border-b border-[var(--border-subtle)] bg-[rgba(11,14,17,0.92)] backdrop-blur-xl">
        <div className="mx-auto flex h-18 w-full max-w-[1480px] items-center gap-3 px-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-[rgba(252,213,53,0.26)] bg-[var(--accent-primary)] shadow-[var(--shadow-md)]">
            <TrendingUp className="h-4.5 w-4.5 text-[var(--text-on-primary)]" />
          </div>
          <div>
            <span className="block text-[13px] font-semibold text-[var(--text-primary)]">Crypto</span>
            <span className="block text-xs text-[var(--text-tertiary)]">Autenticação</span>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex min-h-screen items-center justify-center px-4 pt-20">
        <Outlet />
      </div>
    </div>
  )
}
