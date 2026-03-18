import { Outlet, useLocation } from 'react-router-dom'
import { AppNav } from './AppNav'

export function Layout() {
  const location = useLocation()
  const isKanbanRoute = location.pathname.startsWith('/kanban')

  return (
    <div className="relative min-h-screen w-full overflow-hidden font-sans text-[var(--text-primary)] selection:bg-sky-400/30">
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

      <AppNav />

      <div className="app-main-offset" style={{ marginLeft: 'var(--app-sidebar-width)' }}>
        <div className={isKanbanRoute ? 'page-shell page-shell-wide' : 'page-shell'}>
          <Outlet />
        </div>
      </div>
    </div>
  )
}
