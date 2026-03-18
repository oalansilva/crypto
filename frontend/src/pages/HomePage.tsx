import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Activity, ArrowRight, FileText, Kanban, Layers, Settings } from 'lucide-react'
import { backtestApi } from '@/lib/api'

type HealthState = {
  status: 'loading' | 'ok' | 'error'
  service?: string
}

function cx(...xs: Array<string | false | null | undefined>) {
  return xs.filter(Boolean).join(' ')
}

function formatDt(dt: Date) {
  return dt.toLocaleString('pt-BR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function HomePage() {
  const navigate = useNavigate()
  const [health, setHealth] = useState<HealthState>({ status: 'loading' })

  useEffect(() => {
    let mounted = true

    backtestApi
      .health()
      .then((res) => {
        if (!mounted) return
        const data = (res?.data || {}) as { status?: string; service?: string }
        setHealth({ status: data.status === 'ok' ? 'ok' : 'error', service: data.service })
      })
      .catch(() => {
        if (!mounted) return
        setHealth({ status: 'error' })
      })

    return () => {
      mounted = false
    }
  }, [])

  const nowLabel = useMemo(() => formatDt(new Date()), [])

  return (
    <main className="page-stack">
      <div className="page-stack">
        {/* Hero */}
        <section className="grid grid-cols-1 gap-6 lg:grid-cols-[1.45fr_0.95fr]">
          <div className="page-card p-6 sm:p-8 lg:p-10">
            <span className="eyebrow mb-5">Cockpit diário</span>
            <h1 className="section-title">
              Seu snapshot diário de crypto
            </h1>
            <p className="section-copy mt-4 text-sm sm:text-base">
              Como estou indo, o que precisa atenção e qual o próximo passo mais rápido.
            </p>

            <div className="mt-8 grid grid-cols-1 gap-3 md:grid-cols-3">
              <button
                type="button"
                onClick={() => navigate('/combo/select')}
                className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left shadow-[inset_0_1px_0_rgba(255,255,255,0.03)] hover:-translate-y-0.5 hover:border-emerald-300/20 hover:bg-white/[0.06]"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-[var(--text-primary)]">Rodar um backtest</div>
                    <div className="mt-1 text-xs text-[var(--text-tertiary)]">Escolha estratégia · timeframe</div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-[var(--text-tertiary)]" />
                </div>
              </button>

              <button
                type="button"
                onClick={() => navigate('/lab')}
                className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left shadow-[inset_0_1px_0_rgba(255,255,255,0.03)] hover:-translate-y-0.5 hover:border-sky-300/20 hover:bg-white/[0.06]"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-[var(--text-primary)]">Atualizar dados</div>
                    <div className="mt-1 text-xs text-[var(--text-tertiary)]">Explorar candles · Lab</div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-[var(--text-tertiary)]" />
                </div>
              </button>

              <button
                type="button"
                onClick={() => navigate('/monitor')}
                className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left shadow-[inset_0_1px_0_rgba(255,255,255,0.03)] hover:-translate-y-0.5 hover:border-amber-300/20 hover:bg-white/[0.06]"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-[var(--text-primary)]">Abrir monitor</div>
                    <div className="mt-1 text-xs text-[var(--text-tertiary)]">Sinais · posições</div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-[var(--text-tertiary)]" />
                </div>
              </button>
            </div>
          </div>

          <aside className="page-card p-6 sm:p-7">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Saúde do sistema</h2>
              <span
                className={cx(
                  'rounded-full px-3 py-1 text-[10px] font-semibold tracking-[0.12em]',
                  health.status === 'ok' && 'bg-emerald-400/12 text-emerald-300',
                  health.status === 'loading' && 'bg-white/[0.06] text-[var(--text-secondary)]',
                  health.status === 'error' && 'bg-red-400/12 text-red-300'
                )}
              >
                {health.status === 'loading' ? 'CHECK' : health.status.toUpperCase()}
              </span>
            </div>

            <dl className="mt-5 space-y-3 text-sm">
              <div className="flex justify-between gap-4 rounded-2xl bg-white/[0.03] px-4 py-3">
                <dt className="text-[var(--text-tertiary)]">Último check</dt>
                <dd className="text-[var(--text-secondary)]">{nowLabel}</dd>
              </div>
              <div className="flex justify-between gap-4 rounded-2xl bg-white/[0.03] px-4 py-3">
                <dt className="text-[var(--text-tertiary)]">API</dt>
                <dd className="text-[var(--text-secondary)]">{health.service || '—'}</dd>
              </div>
              <div className="flex justify-between gap-4 rounded-2xl bg-white/[0.03] px-4 py-3">
                <dt className="text-[var(--text-tertiary)]">Carteira</dt>
                <dd className="text-[var(--text-secondary)]">External balances</dd>
              </div>
            </dl>

            <div className="mt-5 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => navigate('/openspec')}
                className="rounded-full border border-white/10 px-3.5 py-2 text-xs font-medium text-[var(--text-secondary)] hover:border-sky-300/18 hover:bg-white/[0.05] hover:text-white"
              >
                <FileText className="mr-1.5 inline-block h-3.5 w-3.5" />
                OpenSpec
              </button>
              <button
                type="button"
                onClick={() => navigate('/lab')}
                className="rounded-full border border-white/10 px-3.5 py-2 text-xs font-medium text-[var(--text-secondary)] hover:border-emerald-300/18 hover:bg-white/[0.05] hover:text-white"
              >
                <Settings className="mr-1.5 inline-block h-3.5 w-3.5" />
                Lab
              </button>
            </div>
          </aside>
        </section>

        {/* KPI grid */}
        <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <div className="page-card p-5">
            <div className="text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">Portfolio PnL (hoje)</div>
            <div className="mt-3 text-2xl font-semibold text-emerald-300">+2.34%</div>
            <div className="mt-1 text-[12px] text-[var(--text-tertiary)]">vs. BTC: +0.40%</div>
          </div>
          <div className="page-card p-5">
            <div className="text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">Drawdown (30d)</div>
            <div className="mt-3 text-2xl font-semibold text-rose-300">-6.10%</div>
            <div className="mt-1 text-[12px] text-[var(--text-tertiary)]">Pico: 12 Fev</div>
          </div>
          <div className="page-card p-5">
            <div className="text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">Melhor estratégia (7d)</div>
            <div className="mt-3 text-2xl font-semibold text-[var(--text-primary)]">MA Crossover</div>
            <div className="mt-1 text-[12px] text-[var(--text-tertiary)]">ROI: +8.9%</div>
          </div>
          <div className="page-card p-5">
            <div className="text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">Data freshness</div>
            <div className="mt-3 text-2xl font-semibold text-[var(--text-primary)]">200 candles</div>
            <div className="mt-1 text-[12px] text-[var(--text-tertiary)]">BTC/USDT · 1h</div>
          </div>
        </section>

        {/* Main layout */}
        <section className="grid grid-cols-1 gap-6 lg:grid-cols-[1.45fr_0.95fr]">
          <div className="flex flex-col gap-4">
            <div className="page-card p-6">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Foco de hoje</h2>
                <Link to="/kanban" className="text-[11px] font-semibold text-emerald-300 hover:text-emerald-200">
                  Ver tudo
                </Link>
              </div>

              <ul className="mt-5 space-y-3">
                <li className="flex items-center gap-3 rounded-2xl border border-white/8 bg-white/[0.03] p-4 hover:bg-white/[0.05]">
                  <span className="rounded-full bg-amber-400/12 px-3 py-1 text-[10px] font-semibold tracking-[0.12em] text-amber-300">
                    Action
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="truncate text-sm text-[var(--text-primary)]">Revisar dados (candles) para ETH/USDT</div>
                    <div className="mt-0.5 text-[11px] text-[var(--text-tertiary)]">Sugestão v0</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => navigate('/lab')}
                    className="rounded-full border border-white/10 px-3 py-1.5 text-[11px] font-semibold text-[var(--text-secondary)] hover:bg-white/[0.06] hover:text-white"
                  >
                    Abrir
                  </button>
                </li>

                <li className="flex items-center gap-3 rounded-2xl border border-white/8 bg-white/[0.03] p-4 hover:bg-white/[0.05]">
                  <span className="rounded-full bg-white/10 px-3 py-1 text-[10px] font-semibold tracking-[0.12em] text-[var(--text-secondary)]">
                    Info
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="truncate text-sm text-[var(--text-primary)]">Resultados recentes</div>
                    <div className="mt-0.5 text-[11px] text-[var(--text-tertiary)]">Momentum v2 · ROI +12.1%</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => navigate('/combo/results')}
                    className="rounded-full border border-white/10 px-3 py-1.5 text-[11px] font-semibold text-[var(--text-secondary)] hover:bg-white/[0.06] hover:text-white"
                  >
                    Ver
                  </button>
                </li>

                <li className="flex items-center gap-3 rounded-2xl border border-white/8 bg-white/[0.03] p-4 hover:bg-white/[0.05]">
                  <span className="rounded-full bg-emerald-400/12 px-3 py-1 text-[10px] font-semibold tracking-[0.12em] text-emerald-300">
                    OK
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="truncate text-sm text-[var(--text-primary)]">External balances</div>
                    <div className="mt-0.5 text-[11px] text-[var(--text-tertiary)]">Binance · {nowLabel}</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => navigate('/external/balances')}
                    className="rounded-full border border-white/10 px-3 py-1.5 text-[11px] font-semibold text-[var(--text-secondary)] hover:bg-white/[0.06] hover:text-white"
                  >
                    Abrir
                  </button>
                </li>
              </ul>
            </div>

            <div className="page-card p-6">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Runs recentes</h2>
                <Link to="/lab" className="text-[11px] font-semibold text-emerald-300 hover:text-emerald-200">
                  Lab
                </Link>
              </div>

              <div className="mt-5 overflow-hidden rounded-2xl border border-white/8 bg-white/[0.03]">
                <div className="grid grid-cols-[1.5fr_1fr_0.5fr_0.7fr_0.7fr_0.8fr] gap-2 bg-white/[0.04] px-4 py-3 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
                  <div>Strategy</div>
                  <div>Pair</div>
                  <div>TF</div>
                  <div>ROI</div>
                  <div>DD</div>
                  <div>Status</div>
                </div>

                {[
                  { s: 'Momentum v2', p: 'BTC/USDT', tf: '4h', roi: '+12.1%', dd: '-4.0%', st: 'Done', tone: 'ok' as const },
                  { s: 'Mean reversion', p: 'ETH/USDT', tf: '1h', roi: '-1.2%', dd: '-7.6%', st: 'Done', tone: 'idle' as const },
                  { s: 'MA Crossover', p: 'SOL/USDT', tf: '1h', roi: '+8.9%', dd: '-3.4%', st: 'Queued', tone: 'warn' as const },
                ].map((r, idx) => (
                  <div
                    key={idx}
                    className="grid grid-cols-[1.5fr_1fr_0.5fr_0.7fr_0.7fr_0.8fr] gap-2 border-t border-white/6 px-4 py-3 text-xs hover:bg-white/[0.04]"
                  >
                    <div className="truncate text-[var(--text-primary)]">{r.s}</div>
                    <div className="truncate text-[var(--text-tertiary)]">{r.p}</div>
                    <div className="text-[var(--text-tertiary)]">{r.tf}</div>
                    <div className={cx('font-semibold', r.roi.startsWith('-') ? 'text-rose-300' : 'text-emerald-300')}>{r.roi}</div>
                    <div className="text-[var(--text-tertiary)]">{r.dd}</div>
                    <div>
                      <span
                        className={cx(
                          'inline-flex items-center rounded-full px-3 py-1 text-[10px] font-semibold tracking-[0.12em]',
                          r.tone === 'ok' && 'bg-emerald-400/12 text-emerald-300',
                          r.tone === 'warn' && 'bg-amber-400/12 text-amber-300',
                          r.tone === 'idle' && 'bg-white/10 text-[var(--text-secondary)]'
                        )}
                      >
                        {r.st}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <p className="mt-3 text-[11px] text-[var(--text-tertiary)]">
                Obs: tabela com dados de exemplo até termos endpoint de listagem.
              </p>
            </div>
          </div>

          <aside className="flex flex-col gap-4">
            <div className="page-card p-6">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Market watch</h2>
                <Link to="/monitor" className="text-[11px] font-semibold text-emerald-300 hover:text-emerald-200">
                  Monitor
                </Link>
              </div>

              <ul className="mt-5 space-y-3">
                {[
                  { pair: 'BTC/USDT', price: '$62,340', chg: '+1.2%' },
                  { pair: 'ETH/USDT', price: '$3,420', chg: '-0.4%' },
                  { pair: 'SOL/USDT', price: '$128', chg: '+3.1%' },
                ].map((row) => (
                  <li key={row.pair} className="grid grid-cols-[1fr_auto_auto] items-center gap-3 rounded-2xl bg-white/[0.03] px-4 py-3">
                    <div className="text-sm font-semibold text-[var(--text-primary)]">{row.pair}</div>
                    <div className="text-xs tabular-nums text-[var(--text-secondary)]">{row.price}</div>
                    <div
                      className={cx(
                        'text-xs font-semibold tabular-nums',
                        row.chg.startsWith('-') ? 'text-rose-300' : 'text-emerald-300'
                      )}
                    >
                      {row.chg}
                    </div>
                  </li>
                ))}
              </ul>

              <div className="mt-4 flex justify-end">
                <button
                  type="button"
                  onClick={() => navigate('/monitor')}
                  className="rounded-full border border-white/10 px-3.5 py-2 text-[11px] font-semibold text-[var(--text-secondary)] hover:bg-white/[0.06] hover:text-white"
                >
                  <Activity className="mr-1.5 inline-block h-3.5 w-3.5" />
                  Abrir monitor
                </button>
              </div>
            </div>

            <div className="page-card p-6">
              <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Atalhos</h2>
              <div className="mt-4 flex flex-wrap gap-2">
                {[
                  { to: '/combo/select', label: 'Combo', icon: Layers },
                  { to: '/kanban', label: 'Kanban', icon: Kanban },
                  { to: '/external/balances', label: 'Carteira', icon: Activity },
                ].map(({ to, label, icon: Icon }) => (
                  <Link
                    key={to}
                    to={to}
                    className="inline-flex items-center gap-1.5 rounded-full border border-white/10 px-3 py-2 text-xs font-medium text-[var(--text-secondary)] hover:border-white/20 hover:bg-white/[0.05] hover:text-white"
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {label}
                  </Link>
                ))}
              </div>
            </div>

            <div className="page-card p-6">
              <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Notas</h2>
              <p className="mt-3 text-[12px] leading-6 text-[var(--text-tertiary)]">
                Implementação guiada pelo prototype. Algumas seções usam placeholders até termos endpoints dedicados.
              </p>
            </div>
          </aside>
        </section>
      </div>
    </main>
  )
}
