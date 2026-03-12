import { NavLink, useLocation } from 'react-router-dom'
import { Activity, TrendingUp, Sparkles, Bookmark, Layers, Shuffle, Wallet, Kanban } from 'lucide-react'
import { Button } from '@/components/ui/Button'

const navItems = [
  { to: '/', label: 'Playground', icon: Sparkles },
  { to: '/favorites', label: 'Favorites', icon: Bookmark },
  { to: '/monitor', label: 'Monitor', icon: Activity },
  { to: '/kanban', label: 'Kanban', icon: Kanban },
  { to: '/lab', label: 'Lab', icon: Sparkles },
  { to: '/arbitrage', label: 'Arbitragem', icon: Shuffle },
  { to: '/combo/select', label: 'Combo', icon: Layers },
  { to: '/external/balances', label: 'Carteira', icon: Wallet },
] as const

function emitWalletAction(action: 'refresh' | 'export') {
  window.dispatchEvent(new CustomEvent(`wallet:${action}`))
}

export function AppNav() {
  const location = useLocation()

  const isActive = (to: string) => {
    if (to === '/') return location.pathname === '/'
    if (to.startsWith('/combo')) return location.pathname.startsWith('/combo')
    if (to.startsWith('/lab')) return location.pathname.startsWith('/lab')
    if (to.startsWith('/kanban')) return location.pathname.startsWith('/kanban')
    return location.pathname === to
  }

  const isWalletPage = location.pathname === '/external/balances'
  const hideOnMobileKanban = location.pathname.startsWith('/kanban')

  if (isWalletPage) {
    return (
      <header className="sticky top-0 z-50 border-b border-white/10 bg-[rgba(10,15,30,0.72)] backdrop-blur-xl">
        <div
          className="flex min-h-16 items-center justify-between gap-4"
          style={{ width: 'min(1120px, calc(100% - 28px))', marginInline: 'auto' }}
        >
          <NavLink to="/external/balances" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
            <div
              aria-hidden="true"
              className="h-3.5 w-3.5 rounded-[4px]"
              style={{
                background: 'linear-gradient(135deg, rgba(138,166,255,1), rgba(53,208,127,1))',
                boxShadow: '0 0 0 2px rgba(255,255,255,0.04)',
              }}
            />
            <div>
              <div className="text-[15px] font-bold tracking-[0.2px] text-white">Crypto Lab</div>
              <div className="mt-0.5 text-xs text-white/60">Carteira · /external/balances</div>
            </div>
          </NavLink>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="border border-white/10 bg-white/5 px-4 text-white/90 hover:bg-white/10" onClick={() => emitWalletAction('export')}>
              Exportar
            </Button>
            <Button variant="primary" size="sm" className="px-4" onClick={() => emitWalletAction('refresh')}>
              Atualizar
            </Button>
          </div>
        </div>
      </header>
    )
  }

  return (
    <header
      className={
        'glass-strong border-b border-white/10 sticky top-0 z-50 ' +
        (hideOnMobileKanban ? 'hidden sm:block' : '')
      }
    >
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
            <div className="relative">
              <div
                className="absolute inset-0 rounded-xl blur opacity-75"
                style={{
                  background:
                    'linear-gradient(135deg, rgba(138,166,255,1), rgba(53,208,127,1))',
                }}
              />
              <div
                className="relative p-2 rounded-xl"
                style={{
                  background:
                    'linear-gradient(135deg, rgba(138,166,255,0.95), rgba(53,208,127,0.95))',
                  boxShadow: '0 0 0 2px rgba(255,255,255,0.04)',
                }}
              >
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
            </div>
            <div>
              <span className="text-xl font-bold gradient-text">Crypto Backtester</span>
              <p className="text-xs text-white/60">Professional Trading Analysis</p>
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
                      ? 'text-white border border-[rgba(138,166,255,0.55)] bg-[rgba(138,166,255,0.18)] shadow-[0_10px_30px_rgba(0,0,0,0.35)]'
                      : 'text-white/60 hover:text-white/90 hover:bg-white/5'
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
