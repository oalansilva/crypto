import { Outlet, useLocation } from 'react-router-dom'
import { AppNav } from './AppNav'
import { FirstUseOnboarding } from './onboarding/FirstUseOnboarding'

export function Layout() {
  const location = useLocation()
  const isKanbanRoute = location.pathname.startsWith('/kanban')
  const shouldShowFirstUseOnboarding = !location.pathname.startsWith('/help')

  return (
    <div className="relative min-h-screen w-full overflow-hidden font-sans text-[var(--text-primary)] selection:bg-[rgba(252,213,53,0.28)] selection:text-[var(--text-on-primary)]">
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[var(--bg-primary)]" />
        <div
          className="absolute inset-x-0 top-0 h-52 opacity-80"
          style={{
            backgroundImage: `
              linear-gradient(180deg, rgba(252, 213, 53, 0.16) 0%, rgba(11, 14, 17, 0) 100%)
            `,
          }}
        />
      </div>

      <AppNav />

      <div className="app-main-offset" style={{ marginLeft: 'var(--app-sidebar-width)' }}>
        <div className={isKanbanRoute ? 'page-shell page-shell-wide' : 'page-shell'}>
          {shouldShowFirstUseOnboarding ? <FirstUseOnboarding /> : null}
          <Outlet />
        </div>
      </div>
    </div>
  )
}
