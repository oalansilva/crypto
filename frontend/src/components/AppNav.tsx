import { useState, useEffect } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { 
  Activity, TrendingUp, Sparkles, Bookmark, Layers, 
  Shuffle, Wallet, Kanban, Menu, X, ChevronLeft,
  Home, Settings, Beaker, Zap, TrendingDown
} from 'lucide-react'

interface AppNavProps {
  hideOnMobile?: boolean
}

const mainNavItems = [
  { to: '/', label: 'Playground', icon: Home },
  { to: '/favorites', label: 'Favorites', icon: Bookmark },
  { to: '/monitor', label: 'Monitor', icon: Activity },
  { to: '/kanban', label: 'Kanban', icon: Kanban },
]

const strategyNavItems = [
  { to: '/lab', label: 'Lab', icon: Beaker },
  { to: '/arbitrage', label: 'Arbitragem', icon: Zap },
  { to: '/combo/select', label: 'Combo', icon: Layers },
]

const accountNavItems = [
  { to: '/external/balances', label: 'Carteira', icon: Wallet },
]

function emitWalletAction(action: 'refresh' | 'export') {
  window.dispatchEvent(new CustomEvent(`wallet:${action}`))
}

export function openMobileMenu() {
  window.dispatchEvent(new CustomEvent('nav:open-menu'))
}

export function AppNav({ hideOnMobile = false }: AppNavProps) {
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  useEffect(() => {
    const handleOpenMenu = () => setMobileMenuOpen(true)
    window.addEventListener('nav:open-menu', handleOpenMenu)
    return () => window.removeEventListener('nav:open-menu', handleOpenMenu)
  }, [])

  const isActive = (to: string) => {
    if (to === '/') return location.pathname === '/'
    if (to.startsWith('/combo')) return location.pathname.startsWith('/combo')
    if (to.startsWith('/lab')) return location.pathname.startsWith('/lab')
    if (to.startsWith('/kanban')) return location.pathname.startsWith('/kanban')
    return location.pathname === to
  }

  const NavItem = ({ to, label, icon: Icon }: { to: string; label: string; icon: any }) => (
    <NavLink
      to={to}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium transition-all duration-200 group ${
        isActive(to)
          ? 'bg-emerald-500/15 text-emerald-400 border-l-2 border-emerald-500'
          : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200'
      }`}
    >
      <Icon className={`w-5 h-5 flex-shrink-0 transition-transform duration-200 group-hover:scale-110 ${isActive(to) ? 'text-emerald-400' : 'text-zinc-500 group-hover:text-zinc-300'}`} />
      {!collapsed && <span className="truncate">{label}</span>}
    </NavLink>
  )

  const NavGroup = ({ title, items, isLast }: { title: string; items: { to: string; label: string; icon: any }[]; isLast?: boolean }) => (
    <div className={!isLast ? 'mb-4 pb-4 border-b border-zinc-800' : ''}>
      {!collapsed && (
        <div className="px-3 mb-2">
          <span className="text-xs font-semibold text-zinc-600 uppercase tracking-wider">{title}</span>
        </div>
      )}
      <nav className="space-y-1">
        {items.map(item => (
          <NavItem key={item.to} {...item} />
        ))}
      </nav>
    </div>
  )

  // Mobile Menu
  if (isMobile) {
    return (
      <>
        {/* Mobile Header */}
        <header className="fixed top-0 left-0 right-0 z-50 bg-zinc-900/95 backdrop-blur-md border-b border-zinc-800 shadow-sm">
          <div className="flex items-center justify-between px-4 h-14">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(true)}
              className="p-2 rounded-xl hover:bg-zinc-800 transition-colors"
              aria-label="Abrir menu"
            >
              <Menu className="w-6 h-6 text-zinc-300" />
            </button>
            <NavLink to="/" className="flex items-center gap-2">
              <div
                className="w-8 h-8 rounded-xl flex items-center justify-center shadow-lg"
                style={{
                  background: 'linear-gradient(135deg, #10b981, #06b6d4)',
                }}
              >
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-white">Crypto Lab</span>
            </NavLink>
            <div className="w-10" />
          </div>
        </header>

        {/* Mobile Menu Overlay */}
        {mobileMenuOpen && (
          <>
            <div
              className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm lg:hidden"
              onClick={() => setMobileMenuOpen(false)}
            />
            <div className="fixed bottom-0 left-0 right-0 z-[110] h-[75vh] bg-zinc-900 rounded-t-3xl shadow-2xl lg:hidden overflow-y-auto">
              {/* Drag handle */}
              <div className="flex justify-center pt-3 pb-1">
                <div className="w-12 h-1.5 bg-zinc-700 rounded-full" />
              </div>

              {/* Header */}
              <div className="flex items-center justify-between px-4 pb-4 border-b border-zinc-800">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg"
                    style={{
                      background: 'linear-gradient(135deg, #10b981, #06b6d4)',
                    }}
                  >
                    <TrendingUp className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="font-bold text-white">Crypto Lab</div>
                    <div className="text-xs text-zinc-500">Navegação</div>
                  </div>
                </div>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-2 rounded-xl hover:bg-zinc-800 transition-colors"
                >
                  <X className="w-5 h-5 text-zinc-400" />
                </button>
              </div>

              {/* Navigation */}
              <nav className="p-4 space-y-1">
                <div className="text-xs font-semibold text-zinc-600 uppercase tracking-wider mb-3">Principal</div>
                {mainNavItems.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 ${
                      isActive(to)
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        : 'text-zinc-300 hover:bg-zinc-800'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {label}
                  </NavLink>
                ))}

                <div className="text-xs font-semibold text-zinc-600 uppercase tracking-wider mb-3 mt-6">Estratégias</div>
                {strategyNavItems.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 ${
                      isActive(to)
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        : 'text-zinc-300 hover:bg-zinc-800'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {label}
                  </NavLink>
                ))}

                <div className="text-xs font-semibold text-zinc-600 uppercase tracking-wider mb-3 mt-6">Conta</div>
                {accountNavItems.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 ${
                      isActive(to)
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        : 'text-zinc-300 hover:bg-zinc-800'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {label}
                  </NavLink>
                ))}
              </nav>
            </div>
          </>
        )}
      </>
    )
  }

  // Desktop Sidebar
  return (
    <>
      <aside
        className={`fixed left-0 top-0 h-screen bg-zinc-900/95 backdrop-blur-md border-r border-zinc-800 z-40 transition-all duration-300 flex flex-col shadow-[4px_0_24px_rgba(0,0,0,0.3)] ${
          collapsed ? 'w-20' : 'w-64'
        }`}
        style={{ display: isMobile ? 'none' : 'flex' }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 h-16 border-b border-zinc-800">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg"
            style={{
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.95), rgba(6, 182, 212, 0.95))',
              boxShadow: '0 4px 16px rgba(16, 185, 129, 0.3)',
            }}
          >
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          {!collapsed && (
            <div>
              <span className="font-bold text-white block">Crypto Lab</span>
              <span className="text-xs text-zinc-500">Backtester Pro</span>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 custom-scrollbar">
          <NavGroup title="Principal" items={mainNavItems} />
          <NavGroup title="Estratégias" items={strategyNavItems} />
          <NavGroup title="Conta" items={accountNavItems} isLast />
        </nav>

        {/* Collapse Button */}
        <div className="p-4 border-t border-zinc-800">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl font-medium transition-all duration-200 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 ${
              collapsed ? 'justify-center' : ''
            }`}
          >
            <ChevronLeft className={`w-5 h-5 transition-transform duration-300 ${collapsed ? 'rotate-180' : ''}`} />
            {!collapsed && <span>Recolher</span>}
          </button>
        </div>
      </aside>

      {/* Main Content Wrapper */}
      <div className={`transition-all duration-300 ${collapsed ? 'ml-20' : 'ml-64'}`}>
        <header className="sticky top-0 z-30 bg-zinc-900/90 backdrop-blur-md border-b border-zinc-800 shadow-sm">
          <div className="flex items-center justify-between px-6 h-14">
            <div className="text-sm font-medium text-zinc-400">
              {location.pathname === '/' && 'Dashboard Principal'}
              {location.pathname === '/favorites' && 'Favoritos'}
              {location.pathname === '/monitor' && 'Monitor de Sinais'}
              {location.pathname === '/kanban' && 'Kanban de Tarefas'}
              {location.pathname.startsWith('/lab') && 'Laboratório'}
              {location.pathname.startsWith('/arbitrage') && 'Arbitragem'}
              {location.pathname.startsWith('/combo') && 'Combo Estratégias'}
              {location.pathname.startsWith('/external') && 'Carteira'}
            </div>
            <div className="flex items-center gap-2">
              <button className="p-2 rounded-xl hover:bg-zinc-800 transition-colors">
                <Settings className="w-5 h-5 text-zinc-500" />
              </button>
            </div>
          </div>
        </header>
        <main className="min-h-[calc(100vh-3.5rem)]">
          {/* This is a placeholder - actual content will be rendered by Outlet */}
        </main>
      </div>
    </>
  )
}
