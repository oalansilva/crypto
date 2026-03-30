import { Outlet } from 'react-router-dom'
import { TrendingUp } from 'lucide-react'

export function AuthLayout() {
  return (
    <div className="relative min-h-screen w-full overflow-hidden font-sans text-[var(--text-primary)] selection:bg-sky-400/30">
      {/* Background */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.12),transparent_25%),radial-gradient(circle_at_85%_0%,rgba(38,194,129,0.1),transparent_22%),linear-gradient(180deg,#07111a_0%,#0b1520_42%,#0d1823_100%)]" />
        <div
          className="absolute inset-0 opacity-70"
          style={{
            backgroundImage: `
              radial-gradient(circle at 18% 24%, rgba(56, 189, 248, 0.1) 0%, transparent 36%),
              radial-gradient(circle at 82% 16%, rgba(38, 194, 129, 0.12) 0%, transparent 32%),
              radial-gradient(circle at 76% 76%, rgba(245, 158, 11, 0.08) 0%, transparent 24%)
            `,
          }}
        />
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      {/* Header */}
      <header className="fixed top-0 inset-x-0 z-50 border-b border-[var(--border-subtle)] bg-[rgba(7,17,26,0.84)] backdrop-blur-xl">
        <div className="mx-auto flex h-18 w-full max-w-[1480px] items-center gap-3 px-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-[18px] border border-emerald-300/20 bg-[linear-gradient(135deg,rgba(38,194,129,0.95),rgba(56,189,248,0.95))] shadow-[0_12px_24px_rgba(18,154,125,0.24)]">
            <TrendingUp className="h-4.5 w-4.5 text-white" />
          </div>
          <div>
            <span className="block text-[13px] font-semibold text-[var(--text-primary)]">Crypto Lab</span>
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
