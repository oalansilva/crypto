import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Activity, ArrowRight, FileText, Kanban, Layers, RefreshCw, Settings, Sparkles } from 'lucide-react'
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
    <main className="container mx-auto px-4 lg:px-6 py-8 lg:py-12">
      <div className="space-y-8">
        {/* Hero */}
        <section className="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-8">
          <div>
            <h1 className="text-2xl md:text-3xl font-semibold text-white">
              Seu snapshot diário de crypto
            </h1>
            <p className="text-white/70 mt-3 max-w-[55ch] text-sm">
              Como estou indo, o que precisa atenção e qual o próximo passo mais rápido.
            </p>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => navigate('/combo/select')}
                className="rounded-lg p-4 text-left hover:bg-white/5 transition-colors cursor-pointer border border-white/10"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-white text-sm">Rodar um backtest</div>
                    <div className="text-white/70 text-xs mt-1">Escolha estratégia · timeframe</div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-white/60" />
                </div>
              </button>

              <button
                type="button"
                onClick={() => navigate('/lab')}
                className="rounded-lg p-4 text-left hover:bg-white/5 transition-colors cursor-pointer border border-white/10"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-white text-sm">Atualizar dados</div>
                    <div className="text-white/70 text-xs mt-1">Explorar candles · Lab</div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-white/60" />
                </div>
              </button>

              <button
                type="button"
                onClick={() => navigate('/monitor')}
                className="rounded-lg p-4 text-left hover:bg-white/5 transition-colors cursor-pointer border border-white/10"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-white text-sm">Abrir Monitor</div>
                    <div className="text-white/70 text-xs mt-1">Sinais · posições</div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-white/60" />
                </div>
              </button>
            </div>
          </div>

          <aside className="rounded-lg p-4 border border-white/10">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xs font-medium text-white/60">Saúde do sistema</h2>
              <span
                className={cx(
                  'text-[10px] font-medium px-2 py-1 rounded',
                  health.status === 'ok' && 'text-green-400 bg-green-400/10',
                  health.status === 'loading' && 'text-white/60 bg-white/5',
                  health.status === 'error' && 'text-red-400 bg-red-400/10'
                )}
              >
                {health.status === 'loading' ? 'CHECK' : health.status.toUpperCase()}
              </span>
            </div>

            <dl className="mt-4 space-y-2 text-xs">
              <div className="flex justify-between">
                <dt className="text-white/70">Último check</dt>
                <dd className="text-white/60">{nowLabel}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-white/70">API</dt>
                <dd className="text-white/60">{health.service || '—'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-white/70">Carteira</dt>
                <dd className="text-white/60">External balances</dd>
              </div>
            </dl>

            <div className="mt-4 flex gap-2">
              <button
                type="button"
                onClick={() => navigate('/openspec')}
                className="px-3 py-1.5 rounded text-xs text-white/70 hover:text-white hover:bg-white/5 transition-colors"
              >
                <FileText className="w-3.5 h-3.5 inline-block mr-1.5" />
                OpenSpec
              </button>
              <button
                type="button"
                onClick={() => navigate('/lab')}
                className="px-3 py-1.5 rounded text-xs text-white/70 hover:text-white hover:bg-white/5 transition-colors"
              >
                <Settings className="w-3.5 h-3.5 inline-block mr-1.5" />
                Lab
              </button>
            </div>
          </aside>
        </section>

        {/* KPI grid */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="rounded-lg p-4 border border-white/10">
            <div className="text-[11px] text-white/70">Portfolio PnL (hoje)</div>
            <div className="text-xl font-medium mt-2 text-green-400">+2.34%</div>
            <div className="text-[11px] text-white/70 mt-1">vs. BTC: +0.40%</div>
          </div>
          <div className="rounded-lg p-4 border border-white/10">
            <div className="text-[11px] text-white/70">Drawdown (30d)</div>
            <div className="text-xl font-medium mt-2 text-red-400">-6.10%</div>
            <div className="text-[11px] text-white/70 mt-1">Pico: 12 Fev</div>
          </div>
          <div className="rounded-lg p-4 border border-white/10">
            <div className="text-[11px] text-white/70">Melhor estratégia (7d)</div>
            <div className="text-xl font-medium mt-2 text-white">MA Crossover</div>
            <div className="text-[11px] text-white/70 mt-1">ROI: +8.9%</div>
          </div>
          <div className="rounded-lg p-4 border border-white/10">
            <div className="text-[11px] text-white/70">Data freshness</div>
            <div className="text-xl font-medium mt-2 text-white">200 candles</div>
            <div className="text-[11px] text-white/70 mt-1">BTC/USDT · 1h</div>
          </div>
        </section>

        {/* Main layout */}
        <section className="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-6">
          <div className="flex flex-col gap-4">
            <div className="rounded-lg p-5 border border-white/10">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xs font-medium text-white/60">Foco de hoje</h2>
                <Link to="/kanban" className="text-[11px] text-green-400 hover:underline">
                  Ver tudo
                </Link>
              </div>

              <ul className="mt-4 space-y-2">
                <li className="rounded-lg border border-white/10 p-3 flex items-center gap-3 hover:bg-white/5 transition-colors">
                  <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-amber-400/10 text-amber-400">
                    Action
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-white truncate">Revisar dados (candles) para ETH/USDT</div>
                    <div className="text-[11px] text-white/70 mt-0.5">Sugestão v0</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => navigate('/lab')}
                    className="text-[11px] font-medium px-2.5 py-1.5 rounded border border-white/10 text-white/60 hover:text-white hover:bg-white/5 transition-colors"
                  >
                    Abrir
                  </button>
                </li>

                <li className="rounded-lg border border-white/10 p-3 flex items-center gap-3 hover:bg-white/5 transition-colors">
                  <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-white/10 text-white/60">
                    Info
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-white truncate">Resultados recentes</div>
                    <div className="text-[11px] text-white/70 mt-0.5">Momentum v2 · ROI +12.1%</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => navigate('/combo/results')}
                    className="text-[11px] font-medium px-2.5 py-1.5 rounded border border-white/10 text-white/60 hover:text-white hover:bg-white/5 transition-colors"
                  >
                    Ver
                  </button>
                </li>

                <li className="rounded-lg border border-white/10 p-3 flex items-center gap-3 hover:bg-white/5 transition-colors">
                  <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-green-400/10 text-green-400">
                    OK
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-white truncate">External balances</div>
                    <div className="text-[11px] text-white/70 mt-0.5">Binance · {nowLabel}</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => navigate('/external/balances')}
                    className="text-[11px] font-medium px-2.5 py-1.5 rounded border border-white/10 text-white/60 hover:text-white hover:bg-white/5 transition-colors"
                  >
                    Abrir
                  </button>
                </li>
              </ul>
            </div>

            <div className="rounded-lg p-5 border border-white/10">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xs font-medium text-white/60">Runs recentes</h2>
                <Link to="/lab" className="text-[11px] text-green-400 hover:underline">
                  Lab
                </Link>
              </div>

              <div className="mt-4 rounded-lg overflow-hidden border border-white/10">
                <div className="grid grid-cols-[1.5fr_1fr_0.5fr_0.7fr_0.7fr_0.8fr] gap-2 px-3 py-2 text-[10px] text-white/70 bg-white/5 font-medium">
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
                    className="grid grid-cols-[1.5fr_1fr_0.5fr_0.7fr_0.7fr_0.8fr] gap-2 px-3 py-2.5 text-xs border-t border-white/5 hover:bg-white/5 transition-colors"
                  >
                    <div className="text-white truncate">{r.s}</div>
                    <div className="text-white/70 truncate">{r.p}</div>
                    <div className="text-white/70">{r.tf}</div>
                    <div className={cx('font-medium', r.roi.startsWith('-') ? 'text-red-400' : 'text-green-400')}>{r.roi}</div>
                    <div className="text-white/70">{r.dd}</div>
                    <div>
                      <span
                        className={cx(
                          'text-[10px] px-2 py-0.5 rounded inline-flex items-center',
                          r.tone === 'ok' && 'bg-green-400/10 text-green-400',
                          r.tone === 'warn' && 'bg-amber-400/10 text-amber-400',
                          r.tone === 'idle' && 'bg-white/10 text-white/70'
                        )}
                      >
                        {r.st}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <p className="text-[11px] text-white/60 mt-3">
                Obs: tabela com dados de exemplo até termos endpoint de listagem.
              </p>
            </div>
          </div>

          <aside className="flex flex-col gap-4">
            <div className="rounded-lg p-5 border border-white/10">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xs font-medium text-white/60">Market watch</h2>
                <Link to="/monitor" className="text-[11px] text-green-400 hover:underline">
                  Monitor
                </Link>
              </div>

              <ul className="mt-4 space-y-2">
                {[
                  { pair: 'BTC/USDT', price: '$62,340', chg: '+1.2%' },
                  { pair: 'ETH/USDT', price: '$3,420', chg: '-0.4%' },
                  { pair: 'SOL/USDT', price: '$128', chg: '+3.1%' },
                ].map((row) => (
                  <li key={row.pair} className="grid grid-cols-[1fr_auto_auto] gap-3 items-baseline">
                    <div className="font-medium text-sm text-white">{row.pair}</div>
                    <div className="text-white/70 text-xs tabular-nums">{row.price}</div>
                    <div
                      className={cx(
                        'text-xs font-medium tabular-nums',
                        row.chg.startsWith('-') ? 'text-red-400' : 'text-green-400'
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
                  className="text-[11px] font-medium px-3 py-1.5 rounded border border-white/10 text-white/70 hover:text-white hover:bg-white/5 transition-colors"
                >
                  <Activity className="w-3.5 h-3.5 inline-block mr-1.5" />
                  Abrir monitor
                </button>
              </div>
            </div>

            <div className="rounded-lg p-5 border border-white/10">
              <h2 className="text-xs font-medium text-white/60">Atalhos</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {[
                  { to: '/combo/select', label: 'Combo', icon: Layers },
                  { to: '/kanban', label: 'Kanban', icon: Kanban },
                  { to: '/external/balances', label: 'Carteira', icon: Activity },
                ].map(({ to, label, icon: Icon }) => (
                  <Link
                    key={to}
                    to={to}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs text-white/70 hover:text-white hover:bg-white/5 transition-colors"
                  >
                    <Icon className="w-3.5 h-3.5" />
                    {label}
                  </Link>
                ))}
              </div>
            </div>

            <div className="rounded-lg p-5 border border-white/10">
              <h2 className="text-xs font-medium text-white/60">Notas</h2>
              <p className="text-[11px] text-white/60 mt-2">
                Implementação guiada pelo prototype. Algumas seções usam placeholders até termos endpoints dedicados.
              </p>
            </div>
          </aside>
        </section>
      </div>
    </main>
  )
}
