import { Outlet } from 'react-router-dom'
import { AppNav } from './AppNav'

export function Layout() {
  return (
    <div className="relative min-h-screen w-full overflow-hidden text-white font-sans selection:bg-emerald-500/30">
      {/* Background - Dark theme */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950" />
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `
              radial-gradient(circle at 15% 30%, rgba(16, 185, 129, 0.15) 0%, transparent 45%),
              radial-gradient(circle at 85% 15%, rgba(139, 92, 246, 0.1) 0%, transparent 40%),
              radial-gradient(circle at 75% 70%, rgba(6, 182, 212, 0.08) 0%, transparent 35%)
            `,
          }}
        />
        {/* Subtle grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      <AppNav />

      {/* Main content area managed by AppNav sidebar */}
      <div className="lg:ml-64 lg:transition-all lg:duration-300">
        <div className="p-6 lg:p-8">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
