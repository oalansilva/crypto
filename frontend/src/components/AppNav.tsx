import { useEffect, useRef, useState, type ComponentType } from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import {
  Activity,
  Bookmark,
  ChartPie,
  ChevronLeft,
  Play,
  KeyRound,
  Layers,
  LogOut,
  Menu,
  Settings,
  User,
  TrendingUp,
  UsersRound,
  Wallet,
  X,
  Mail,
  Fingerprint,
} from 'lucide-react'
import { useAuth } from '@/stores/authStore'

interface AppNavProps {
  hideOnMobile?: boolean
}

type NavItemConfig = {
  to: string
  label: string
  accessibilityLabel?: string
  icon: ComponentType<{ className?: string }>
  adminOnly?: boolean
}

const mainNavItems: NavItemConfig[] = [
  { to: '/favorites', label: 'Favoritos', icon: Bookmark },
  { to: '/monitor', label: 'Monitor', icon: Activity },
  { to: '/signals/history', label: 'Histórico', icon: TrendingUp, adminOnly: true },
  {
    to: '/supply-distribution',
    label: 'Distribuição',
    accessibilityLabel: 'Distribuicao',
    icon: ChartPie,
    adminOnly: true,
  },
]

const strategyNavItems: NavItemConfig[] = [
  { to: '/combo/select', label: 'Combo', icon: Layers, adminOnly: true },
  { to: '/signals', label: 'Backtests', icon: TrendingUp, adminOnly: true },
]

const accountNavItems: NavItemConfig[] = [
  { to: '/external/balances', label: 'Carteira', icon: Wallet },
  { to: '/profile', label: 'Meu Perfil', icon: User },
  { to: '/change-password', label: 'Alterar Senha', icon: KeyRound },
]

const adminNavItems: NavItemConfig[] = [
  { to: '/system/preferences', label: 'Preferências', icon: Settings },
  { to: '/admin/users', label: 'Usuários', icon: UsersRound },
  { to: '/admin/backfill', label: 'Backfill', icon: Play },
]

export function openMobileMenu() {
  window.dispatchEvent(new CustomEvent('nav:open-menu'))
}

function resolvePageTitle(pathname: string) {
  if (pathname === '/' || pathname === '/monitor') return 'Monitor de sinais'
  if (pathname === '/favorites') return 'Favoritos'
  if (pathname === '/signals') return 'Backtests'
  if (pathname === '/signals/history') return 'Histórico de Sinais'
  if (pathname === '/supply-distribution') return 'Distribuição de supply'
  if (pathname.startsWith('/combo')) return 'Combo estratégias'
  if (pathname.startsWith('/external')) return 'Carteira'
  if (pathname.startsWith('/profile')) return 'Meu Perfil'
  if (pathname.startsWith('/change-password')) return 'Alterar senha'
  if (pathname.startsWith('/system/preferences')) return 'Preferências do sistema'
  if (pathname.startsWith('/admin/users')) return 'Usuários'
  if (pathname.startsWith('/admin/backfill')) return 'Backfill de histórico'
  if (pathname.startsWith('/openspec')) return 'OpenSpec'
  return 'Crypto'
}

function getUserInitials(name?: string) {
  if (!name) return 'U'
  const initials = name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
  return initials || 'U'
}

function BrandBlock({ compact = false }: { compact?: boolean }) {
  const logoClasses = compact ? 'h-12 w-12 object-contain' : 'h-12 w-[172px] object-contain object-left'

  return (
    <div className={['flex min-w-0 items-center', compact ? 'justify-center' : 'justify-start'].join(' ')}>
      <img
        src="/brand/cripto-farol-logo-v6-transparent.svg"
        alt="Cripto Farol"
        className={logoClasses}
      />
    </div>
  )
}

function NavSection({
  title,
  items,
  collapsed,
  pathname,
  onNavigate,
}: {
  title: string
  items: NavItemConfig[]
  collapsed: boolean
  pathname: string
  onNavigate?: () => void
}) {
  return (
    <section className="space-y-2">
      {!collapsed && (
        <div className="px-2">
          <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{title}</span>
        </div>
      )}
      <div className="space-y-1">
        {items.map(({ to, label, accessibilityLabel, icon: Icon }) => {
          const isActive =
            to === '/monitor'
              ? pathname === '/monitor' || pathname === '/'
              : to.startsWith('/combo')
                ? pathname.startsWith('/combo')
                : pathname === to || pathname.startsWith(`${to}/`)

          return (
            <NavLink
              key={to}
              to={to}
              onClick={onNavigate}
              aria-label={accessibilityLabel ?? label}
              className={[
                'group relative flex items-center gap-2.5 overflow-hidden rounded-lg border px-3 py-2.5 text-[13px] font-medium transition-all duration-200',
                collapsed ? 'justify-center px-0' : '',
                isActive
                  ? 'border-[rgba(252,213,53,0.36)] bg-[rgba(252,213,53,0.1)] text-[var(--text-primary)] shadow-[var(--shadow-sm)]'
                  : 'border-transparent text-[var(--text-secondary)] hover:border-[var(--border-default)] hover:bg-[var(--bg-elevated)] hover:text-[var(--text-primary)]',
              ].join(' ')}
            >
              {isActive && !collapsed && <span className="absolute inset-y-2 left-0 w-1 rounded-full bg-[var(--accent-primary)]" />}
              <Icon
                className={[
                  'h-5 w-5 shrink-0 transition-transform duration-200 group-hover:scale-105',
                  isActive ? 'text-[var(--accent-primary)]' : 'text-[var(--text-tertiary)] group-hover:text-[var(--text-primary)]',
                ].join(' ')}
              />
              {!collapsed && <span className="truncate">{label}</span>}
            </NavLink>
          )
        })}
      </div>
    </section>
  )
}

export function AppNav({ hideOnMobile = false }: AppNavProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [accountMenuOpen, setAccountMenuOpen] = useState(false)
  const accountMenuRef = useRef<HTMLDivElement | null>(null)
  const { user, logout, isLoading } = useAuth()

  useEffect(() => {
    const syncViewport = () => setIsMobile(window.innerWidth < 1024)
    syncViewport()
    window.addEventListener('resize', syncViewport)
    return () => window.removeEventListener('resize', syncViewport)
  }, [])

  useEffect(() => {
    const handleOpenMenu = () => setMobileMenuOpen(true)
    window.addEventListener('nav:open-menu', handleOpenMenu)
    return () => window.removeEventListener('nav:open-menu', handleOpenMenu)
  }, [])

  useEffect(() => {
    const sidebarWidth = isMobile ? '0px' : collapsed ? '88px' : '224px'
    document.documentElement.style.setProperty('--app-sidebar-width', sidebarWidth)

    return () => {
      document.documentElement.style.setProperty('--app-sidebar-width', '224px')
    }
  }, [collapsed, isMobile])

  useEffect(() => {
    setAccountMenuOpen(false)
  }, [location.pathname, isMobile])

  useEffect(() => {
    if (!accountMenuOpen) return

    const handlePointerDown = (event: MouseEvent) => {
      if (!accountMenuRef.current?.contains(event.target as Node)) {
        setAccountMenuOpen(false)
      }
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setAccountMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handlePointerDown)
    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('mousedown', handlePointerDown)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [accountMenuOpen])

  const pathname = location.pathname
  const pageTitle = resolvePageTitle(pathname)
  const userInitials = getUserInitials(user?.name)
  const isAdmin = user?.isAdmin === true
  const shouldShowNavItem = (item: NavItemConfig) => {
    if (!item.adminOnly || isAdmin) return true
    return pathname === item.to || pathname.startsWith(`${item.to}/`)
  }
  const visibleMainNavItems = mainNavItems.filter(shouldShowNavItem)
  const visibleStrategyNavItems = strategyNavItems.filter(shouldShowNavItem)
  const visibleAdminNavItems = isAdmin
    ? adminNavItems
    : adminNavItems.filter((item) => pathname === item.to || pathname.startsWith(`${item.to}/`))
  const handleLogout = () => {
    setAccountMenuOpen(false)
    logout()
    window.location.href = '/login'
  }

  if (isMobile) {
    return (
      <>
        {!hideOnMobile && (
          <header className="fixed inset-x-0 top-0 z-50 border-b border-[var(--border-subtle)] bg-[rgba(11,14,17,0.92)] backdrop-blur-xl">
            <div className="mx-auto flex h-18 w-full max-w-[1480px] items-center justify-between gap-4 px-4">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(true)}
                className="inline-flex h-11 w-11 items-center justify-center rounded-lg border border-[var(--border-default)] bg-[var(--bg-elevated)] text-[var(--text-primary)] hover:bg-[var(--bg-input)]"
                aria-label="Abrir menu"
              >
                <Menu className="h-5 w-5" />
              </button>

              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-semibold text-[var(--text-primary)]">{pageTitle}</div>
                <div className="truncate text-xs text-[var(--text-tertiary)]">Navegação principal</div>
              </div>

              {user ? (
                <div className="relative" ref={accountMenuRef}>
                  <button
                    type="button"
                    onClick={() => setAccountMenuOpen((value) => !value)}
                    className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-[rgba(252,213,53,0.28)] bg-[rgba(252,213,53,0.1)] text-sm font-semibold text-[var(--accent-primary)] shadow-[var(--shadow-md)]"
                    aria-label="Abrir conta"
                    aria-expanded={accountMenuOpen}
                  >
                    {userInitials}
                  </button>

                  {accountMenuOpen && (
                    <div className="absolute right-0 top-[calc(100%+0.75rem)] z-[90] w-[min(88vw,320px)] overflow-hidden rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] p-4 shadow-[var(--shadow-xl)] backdrop-blur-xl">
                      <div className="mb-3 flex items-center gap-3">
                        <div className="flex h-12 w-12 items-center justify-center rounded-full border border-[rgba(252,213,53,0.24)] bg-[rgba(252,213,53,0.1)] text-base font-semibold text-[var(--accent-primary)]">
                          {userInitials}
                        </div>
                        <div className="min-w-0">
                          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Account</div>
                          <div className="truncate text-sm font-semibold text-[var(--text-primary)]">{user.name}</div>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="page-card-muted flex items-start gap-2.5 px-3 py-2.5">
                          <Mail className="mt-0.5 h-4 w-4 shrink-0 text-[var(--accent-primary)]" />
                          <div className="min-w-0">
                            <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Email</div>
                            <div className="truncate text-sm text-[var(--text-secondary)]">{user.email}</div>
                          </div>
                        </div>
                        <div className="page-card-muted flex items-start gap-2.5 px-3 py-2.5">
                          <Fingerprint className="mt-0.5 h-4 w-4 shrink-0 text-[var(--accent-primary)]" />
                          <div className="min-w-0">
                            <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">User ID</div>
                            <div className="truncate text-sm text-[var(--text-secondary)]">{user.id}</div>
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 flex items-center justify-between gap-3">
                        <button
                          type="button"
                          onClick={() => {
                            setAccountMenuOpen(false)
                            navigate('/profile')
                          }}
                          className="inline-flex items-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 py-2 text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-input)] hover:text-[var(--text-primary)]"
                        >
                          <User className="h-4 w-4" />
                          <span>Meu Perfil</span>
                        </button>
                        <button
                          type="button"
                          onClick={handleLogout}
                          className="inline-flex items-center gap-2 rounded-2xl border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm font-medium text-red-300 hover:bg-red-500/16 hover:text-red-200"
                        >
                          <LogOut className="h-4 w-4" />
                          <span>Sair</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="rounded-md border border-[rgba(252,213,53,0.24)] bg-[rgba(252,213,53,0.08)] px-3 py-1 text-[11px] font-semibold text-[var(--accent-primary)]">
                  Live
                </div>
              )}
            </div>
          </header>
        )}

        {mobileMenuOpen && (
          <>
            <button
              type="button"
              className="fixed inset-0 z-[70] bg-black/70 backdrop-blur-sm"
              onClick={() => setMobileMenuOpen(false)}
              aria-label="Fechar menu"
            />
            <aside className="fixed inset-y-0 left-0 z-[80] flex w-[min(88vw,360px)] flex-col border-r border-[var(--border-default)] bg-[var(--bg-secondary)] px-4 py-5 shadow-[24px_0_60px_rgba(0,0,0,0.4)]">
              <div className="flex items-center justify-between gap-3 pb-5">
                <BrandBlock />
                <button
                  type="button"
                  onClick={() => setMobileMenuOpen(false)}
                  className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-[var(--border-default)] bg-[var(--bg-elevated)] text-[var(--text-secondary)] hover:bg-[var(--bg-input)] hover:text-[var(--text-primary)]"
                  aria-label="Fechar menu"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="page-card-muted mb-5 px-4 py-3">
                <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Você está em</div>
                <div className="mt-2 text-sm font-semibold text-[var(--text-primary)]">{pageTitle}</div>
              </div>

              <div className="flex-1 space-y-5 overflow-y-auto pr-1 custom-scrollbar">
                <NavSection title="Principal" items={visibleMainNavItems} collapsed={false} pathname={pathname} onNavigate={() => setMobileMenuOpen(false)} />
                {visibleStrategyNavItems.length > 0 ? (
                  <NavSection title="Estratégias" items={visibleStrategyNavItems} collapsed={false} pathname={pathname} onNavigate={() => setMobileMenuOpen(false)} />
                ) : null}
                <NavSection title="Conta" items={accountNavItems} collapsed={false} pathname={pathname} onNavigate={() => setMobileMenuOpen(false)} />
                {visibleAdminNavItems.length > 0 ? <NavSection title="Admin" items={visibleAdminNavItems} collapsed={false} pathname={pathname} onNavigate={() => setMobileMenuOpen(false)} /> : null}

                {user && (
                  <div className="page-card-muted px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-11 w-11 items-center justify-center rounded-full border border-[rgba(252,213,53,0.24)] bg-[rgba(252,213,53,0.1)] text-sm font-semibold text-[var(--accent-primary)]">
                        {userInitials}
                      </div>
                      <div className="min-w-0">
                        <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Account</div>
                        <div className="truncate text-sm font-semibold text-[var(--text-primary)]">{user.name}</div>
                        <div className="truncate text-xs text-[var(--text-tertiary)]">{user.email}</div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="border-t border-[var(--border-subtle)] pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setMobileMenuOpen(false)
                      handleLogout()
                    }}
                    className="flex w-full items-center gap-2.5 rounded-lg border border-transparent px-3 py-2.5 text-[13px] font-medium text-[var(--text-secondary)] hover:border-red-500/20 hover:bg-red-500/10 hover:text-red-300"
                  >
                    <LogOut className="h-5 w-5" />
                    <span>Sair</span>
                  </button>
                </div>
              </div>
            </aside>
          </>
        )}
      </>
    )
  }

  return (
    <>
      <aside
        className={[
          'fixed inset-y-0 left-0 z-40 flex flex-col border-r border-[var(--border-subtle)] bg-[rgba(24,26,32,0.96)] px-2.5 py-3 backdrop-blur-xl transition-all duration-300',
          collapsed ? 'w-[88px]' : 'w-[224px]',
        ].join(' ')}
      >
        <div className="flex items-center justify-between gap-2 px-2 pb-4">
          <BrandBlock compact={collapsed} />
        </div>

        <div className="page-card-muted mx-1 mb-4 px-3 py-2.5">
          {!collapsed ? (
            <>
              <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Painel</div>
              <div className="mt-1 text-[13px] font-semibold text-[var(--text-primary)]">{pageTitle}</div>
            </>
          ) : (
            <div className="text-center text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Menu</div>
          )}
        </div>

        <nav
          className="custom-scrollbar flex-1 space-y-4 overflow-y-auto px-1 pb-3"
          aria-label="Navegacao principal"
        >
          <NavSection title="Principal" items={visibleMainNavItems} collapsed={collapsed} pathname={pathname} />
          {visibleStrategyNavItems.length > 0 ? (
            <NavSection title="Estratégias" items={visibleStrategyNavItems} collapsed={collapsed} pathname={pathname} />
          ) : null}
          <NavSection title="Conta" items={accountNavItems} collapsed={collapsed} pathname={pathname} />
          {visibleAdminNavItems.length > 0 ? <NavSection title="Admin" items={visibleAdminNavItems} collapsed={collapsed} pathname={pathname} /> : null}
        </nav>

        <div className="mt-3 border-t border-[var(--border-subtle)] pt-3">
          <button
            type="button"
            onClick={() => setCollapsed((value) => !value)}
            className={[
              'flex w-full items-center gap-2.5 rounded-lg border border-transparent px-3 py-2.5 text-[13px] font-medium text-[var(--text-secondary)] hover:border-[var(--border-default)] hover:bg-[var(--bg-elevated)] hover:text-[var(--text-primary)]',
              collapsed ? 'justify-center px-0' : '',
            ].join(' ')}
          >
            <ChevronLeft className={['h-5 w-5 transition-transform duration-300', collapsed ? 'rotate-180' : ''].join(' ')} />
            {!collapsed && <span>Recolher menu</span>}
          </button>
        </div>
      </aside>

      <header
        className="fixed right-0 top-0 z-30 border-b border-[var(--border-subtle)] bg-[rgba(11,14,17,0.88)] backdrop-blur-xl transition-all duration-300"
        style={{ left: 'var(--app-sidebar-width)' }}
      >
        <div className="mx-auto flex h-20 w-full max-w-[calc(1480px+4rem)] items-center justify-between gap-6 px-6">
          <div className="min-w-0">
            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Workspace</div>
            <div className="truncate text-lg font-semibold text-[var(--text-primary)]">{pageTitle}</div>
          </div>

          <div className="flex items-center gap-3">
            {!isLoading && (
              user ? (
                <div className="relative" ref={accountMenuRef}>
                  <button
                    type="button"
                    onClick={() => setAccountMenuOpen((value) => !value)}
                    className="flex items-center gap-3 rounded-lg border border-[var(--border-default)] bg-[var(--bg-elevated)] px-2.5 py-2 text-left shadow-[var(--shadow-sm)] hover:border-[rgba(252,213,53,0.32)] hover:bg-[var(--bg-input)]"
                    aria-label="Abrir conta"
                    aria-expanded={accountMenuOpen}
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-full border border-[rgba(252,213,53,0.24)] bg-[rgba(252,213,53,0.1)] text-sm font-semibold text-[var(--accent-primary)]">
                      {userInitials}
                    </div>
                    <div className="min-w-0">
                      <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Account</div>
                      <div className="max-w-[10rem] truncate text-sm font-semibold text-[var(--text-primary)]">{user.name}</div>
                    </div>
                  </button>

                  {accountMenuOpen && (
                    <div className="absolute right-0 top-[calc(100%+0.8rem)] z-50 w-[320px] overflow-hidden rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] p-4 shadow-[var(--shadow-xl)] backdrop-blur-xl">
                      <div className="flex items-center gap-3">
                        <div className="flex h-14 w-14 items-center justify-center rounded-full border border-[rgba(252,213,53,0.24)] bg-[rgba(252,213,53,0.1)] text-base font-semibold text-[var(--accent-primary)]">
                          {userInitials}
                        </div>
                        <div className="min-w-0">
                          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Account</div>
                          <div className="truncate text-base font-semibold text-[var(--text-primary)]">{user.name}</div>
                          <div className="truncate text-sm text-[var(--text-tertiary)]">Usuário autenticado no sistema</div>
                        </div>
                      </div>

                      <div className="mt-4 space-y-2">
                        <div className="page-card-muted flex items-start gap-3 px-3 py-3">
                          <Mail className="mt-0.5 h-4 w-4 shrink-0 text-[var(--accent-primary)]" />
                          <div className="min-w-0">
                            <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Email</div>
                            <div className="truncate text-sm text-[var(--text-secondary)]">{user.email}</div>
                          </div>
                        </div>
                        <div className="page-card-muted flex items-start gap-3 px-3 py-3">
                          <Fingerprint className="mt-0.5 h-4 w-4 shrink-0 text-[var(--accent-primary)]" />
                          <div className="min-w-0">
                            <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">User ID</div>
                            <div className="truncate text-sm text-[var(--text-secondary)]">{user.id}</div>
                          </div>
                        </div>
                        {user.isAdmin && (
                          <div className="page-card-muted flex items-start gap-3 px-3 py-3">
                            <Settings className="mt-0.5 h-4 w-4 shrink-0 text-[var(--accent-primary)]" />
                            <div className="min-w-0">
                              <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Perfil</div>
                              <div className="truncate text-sm text-[var(--text-secondary)]">Administrador do sistema</div>
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="mt-4 grid grid-cols-2 gap-3 border-t border-[var(--border-subtle)] pt-4">
                        <button
                          type="button"
                          onClick={() => {
                            setAccountMenuOpen(false)
                            navigate('/profile')
                          }}
                          className="inline-flex items-center justify-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 py-2 text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-input)] hover:text-[var(--text-primary)]"
                        >
                          <User className="h-4 w-4" />
                          <span>Perfil</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setAccountMenuOpen(false)
                            navigate('/change-password')
                          }}
                          className="inline-flex items-center justify-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 py-2 text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-input)] hover:text-[var(--text-primary)]"
                        >
                          <KeyRound className="h-4 w-4" />
                          <span>Senha</span>
                        </button>
                        <button
                          type="button"
                          onClick={handleLogout}
                          className="col-span-2 inline-flex items-center justify-center gap-2 rounded-2xl border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm font-medium text-red-300 hover:bg-red-500/16 hover:text-red-200"
                        >
                          <LogOut className="h-4 w-4" />
                          <span>Sair</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <NavLink
                  to="/login"
                  className="inline-flex h-10 items-center gap-2 rounded-md border border-[rgba(252,213,53,0.24)] bg-[rgba(252,213,53,0.08)] px-4 text-sm font-semibold text-[var(--accent-primary)] transition hover:bg-[rgba(252,213,53,0.14)]"
                >
                  Entrar
                </NavLink>
              )
            )}
            <button
              type="button"
              className="inline-flex h-11 w-11 items-center justify-center rounded-lg border border-[var(--border-default)] bg-[var(--bg-elevated)] text-[var(--text-secondary)] hover:bg-[var(--bg-input)] hover:text-[var(--text-primary)]"
              aria-label="Configurações"
            >
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>
    </>
  )
}
