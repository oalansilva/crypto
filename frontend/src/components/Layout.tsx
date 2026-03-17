import { Outlet, useLocation } from 'react-router-dom'
import { AppNav } from './AppNav'

export function Layout() {
  // AppNav is always visible - unified navigation on all pages
  return (
    <div className="relative min-h-screen w-full overflow-hidden text-white font-sans selection:bg-[rgba(138,166,255,0.30)] pb-20">
      {/* Global app background matches the approved Wallet prototype palette */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div
          className="absolute inset-0"
          style={{
            background:
              'radial-gradient(1000px 500px at 10% 0%, rgba(138,166,255,0.25), transparent 55%), radial-gradient(900px 500px at 100% 0%, rgba(53,208,127,0.14), transparent 60%), #0b1020',
          }}
        />
      </div>

      <AppNav />
      <Outlet />
    </div>
  )
}
