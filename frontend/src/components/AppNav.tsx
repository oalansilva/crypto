import { NavLink, useLocation } from 'react-router-dom'
import { Activity, TrendingUp, Sparkles, Bookmark, Layers } from 'lucide-react'

const navItems = [
  { to: '/', label: 'Playground', icon: Sparkles },
  { to: '/favorites', label: 'Favorites', icon: Bookmark },
  { to: '/monitor', label: 'Monitor', icon: Activity },
  { to: '/combo/select', label: 'Combo', icon: Layers },
] as const

export function AppNav() {
  const location = useLocation()

  const isActive = (to: string) => {
    if (to === '/') return location.pathname === '/'
    if (to.startsWith('/combo')) return location.pathname.startsWith('/combo')
    return location.pathname === to
  }

  return (
    <header className="glass-strong border-b border-white/10 sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl blur opacity-75" />
              <div className="relative bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-xl shadow-glow-blue">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
            </div>
            <div>
              <span className="text-xl font-bold gradient-text">Crypto Backtester</span>
              <p className="text-xs text-gray-400">Professional Trading Analysis</p>
            </div>
          </NavLink>

          <nav className="flex gap-1 glass p-1.5 rounded-xl" aria-label="Navegação principal">
            {navItems.map(({ to, label, icon: Icon }) => {
              const active = isActive(to)
              return (
                <NavLink
                  key={to}
                  to={to}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-semibold transition-all duration-200 ${
                    active
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-glow-blue'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </NavLink>
              )
            })}
          </nav>
        </div>
      </div>
    </header>
  )
}
