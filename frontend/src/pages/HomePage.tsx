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
    <main className="container mx-auto px-6 py-10">
      <div className="space-y-6 animate-in fade-in duration-500">
        {/* Hero */}
        <section className="grid grid-cols-1 lg:grid-cols-[1.6fr_1fr] gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white">Seu snapshot diário de crypto</h1>
            <p className="text-gray-400 mt-3 max-w-[60ch]">
              Um Home mais claro para responder: <span className="text-white font-semibold">como estou indo</span>, o que
              precisa atenção e qual o próximo passo mais rápido.
            </p>

            <div className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => navigate('/combo/select')}
                className={cx(
                  'glass-strong rounded-2xl p-4 border border-white/10 text-left group',
                  'hover:border-emerald-500/30 hover:bg-white/[0.10] transition-all duration-300'
                )}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-bold text-white">Rodar um backtest</div>
                    <div className="text-xs text-gray-400 mt-1">Escolha estratégia · timeframe · parâmetros</div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
                </div>
              </button>

              <button
                type="button"
                onClick={() => navigate('/lab')}
                className={cx(
                  'glass-strong rounded-2xl p-4 border border-white/10 text-left group',
                  'hover:border-emerald-500/30 hover:bg-white/[0.10] transition-all duration-300'
                )}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-bold text-white">Atualizar / checar dados</div>
                    <div className="text-xs text-gray-400 mt-1">Explorar candles · run guiado no Lab</div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
                </div>
              </button>

              <button
                type="button"
                onClick={() => navigate('/monitor')}
                className={cx(
                  'glass-strong rounded-2xl p-4 border border-white/10 text-left group',
                  'hover:border-emerald-500/30 hover:bg-white/[0.10] transition-all duration-300'
                )}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-bold text-white">Abrir Monitor</div>
                    <div className="text-xs text-gray-400 mt-1">Sinais · posições · alerts</div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
                </div>
              </button>
            </div>
          </div>

          <aside className="glass-strong rounded-2xl p-5 border border-white/10">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-sm font-bold text-white/90 tracking-wide">Saúde do sistema</h2>
              <span
                className={cx(
                  'text-xs font-bold px-3 py-1 rounded-full border',
                  health.status === 'ok' && 'text-emerald-300 border-emerald-500/30 bg-emerald-500/10',
                  health.status === 'loading' && 'text-gray-300 border-white/10 bg-white/5',
                  health.status === 'error' && 'text-rose-300 border-rose-500/30 bg-rose-500/10'
                )}
              >
                {health.status === 'loading' ? 'CHECK' : health.status.toUpperCase()}
              </span>
            </div>

            <dl className="mt-4 space-y-3">
              <div className="flex items-center justify-between border-t border-white/10 pt-3">
                <dt className="text-xs text-gray-400">Último check</dt>
                <dd className="text-xs text-gray-200">{nowLabel}</dd>
              </div>
              <div className="flex items-center justify-between border-t border-white/10 pt-3">
                <dt className="text-xs text-gray-400">API</dt>
                <dd className="text-xs text-gray-200">{health.service || '—'}</dd>
              </div>
              <div className="flex items-center justify-between border-t border-white/10 pt-3">
                <dt className="text-xs text-gray-400">Fonte de carteira</dt>
                <dd className="text-xs text-gray-200">External balances</dd>
              </div>
            </dl>

            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => navigate('/openspec')}
                className="px-3 py-2 rounded-xl text-xs font-semibold text-gray-300 hover:text-white hover:bg-white/5 border border-white/10 transition-colors"
              >
                <FileText className="w-4 h-4 inline-block mr-2" />
                OpenSpec
              </button>
              <button
                type="button"
                onClick={() => navigate('/lab')}
                className="px-3 py-2 rounded-xl text-xs font-semibold text-gray-300 hover:text-white hover:bg-white/5 border border-white/10 transition-colors"
              >
                <Settings className="w-4 h-4 inline-block mr-2" />
                Lab
              </button>
            </div>
          </aside>
        </section>

        {/* KPI grid */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3" aria-label="KPIs">
          <div className="glass-strong rounded-2xl p-4 border border-white/10">
            <div className="text-xs text-gray-400">Portfolio PnL (hoje)</div>
            <div className="text-2xl font-extrabold mt-2 text-emerald-300">+2.34%</div>
            <div className="text-xs text-gray-400 mt-1">vs. BTC: +0.40%</div>
          </div>
          <div className="glass-strong rounded-2xl p-4 border border-white/10">
            <div className="text-xs text-gray-400">Drawdown (30d)</div>
            <div className="text-2xl font-extrabold mt-2 text-rose-300">-6.10%</div>
            <div className="text-xs text-gray-400 mt-1">Pico: 12 Fev</div>
          </div>
          <div className="glass-strong rounded-2xl p-4 border border-white/10">
            <div className="text-xs text-gray-400">Melhor estratégia (7d)</div>
            <div className="text-2xl font-extrabold mt-2 text-white">MA Crossover</div>
            <div className="text-xs text-gray-400 mt-1">ROI: +8.9%</div>
          </div>
          <div className="glass-strong rounded-2xl p-4 border border-white/10">
            <div className="text-xs text-gray-400">Data freshness</div>
            <div className="text-2xl font-extrabold mt-2 text-white">200 candles</div>
            <div className="text-xs text-gray-400 mt-1">BTC/USDT · 1h</div>
          </div>
        </section>

        {/* Main layout */}
        <section className="grid grid-cols-1 lg:grid-cols-[1.6fr_1fr] gap-3">
          <div className="flex flex-col gap-3">
            <div className="glass-strong rounded-2xl p-5 border border-white/10">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-sm font-bold text-white/90 tracking-wide">Foco de hoje</h2>
                <Link to="/kanban" className="text-xs text-emerald-300 hover:underline">
                  Ver tudo
                </Link>
              </div>

              <ul className="mt-4 space-y-2">
                <li className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 flex items-center gap-3">
                  <span className="text-[10px] font-bold px-3 py-1 rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-200">
                    Action
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-white truncate">Revisar dados (candles) para ETH/USDT</div>
                    <div className="text-xs text-gray-400 mt-0.5">Sugestão v0 (placeholder)</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => navigate('/lab')}
                    className="text-xs font-bold px-3 py-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/15 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4 inline-block mr-2" />
                    Abrir
                  </button>
                </li>

                <li className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 flex items-center gap-3">
                  <span className="text-[10px] font-bold px-3 py-1 rounded-full border border-white/10 bg-white/5 text-gray-300">
                    Info
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-white truncate">Resultados recentes</div>
                    <div className="text-xs text-gray-400 mt-0.5">Momentum v2 · ROI +12.1% · DD -4.0% (placeholder)</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => navigate('/combo/results')}
                    className="text-xs font-bold px-3 py-2 rounded-xl border border-white/10 text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
                  >
                    <Sparkles className="w-4 h-4 inline-block mr-2" />
                    Ver
                  </button>
                </li>

                <li className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 flex items-center gap-3">
                  <span className="text-[10px] font-bold px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-200">
                    OK
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-white truncate">External balances</div>
                    <div className="text-xs text-gray-400 mt-0.5">Binance · {nowLabel} (placeholder)</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => navigate('/external/balances')}
                    className="text-xs font-bold px-3 py-2 rounded-xl border border-white/10 text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
                  >
                    Abrir
                  </button>
                </li>
              </ul>
            </div>

            <div className="glass-strong rounded-2xl p-5 border border-white/10">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-sm font-bold text-white/90 tracking-wide">Runs recentes</h2>
                <Link to="/lab" className="text-xs text-emerald-300 hover:underline">
                  Lab
                </Link>
              </div>

              <div className="mt-4 border border-white/10 rounded-2xl overflow-hidden">
                <div className="grid grid-cols-[1.4fr_1fr_0.6fr_0.7fr_0.7fr_0.8fr] gap-3 px-4 py-2 text-[11px] text-gray-400 bg-white/[0.04]">
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
                    className="grid grid-cols-[1.4fr_1fr_0.6fr_0.7fr_0.7fr_0.8fr] gap-3 px-4 py-3 text-xs border-t border-white/10"
                  >
                    <div className="text-white font-semibold truncate">{r.s}</div>
                    <div className="text-gray-300 truncate">{r.p}</div>
                    <div className="text-gray-300">{r.tf}</div>
                    <div className={cx('font-semibold', r.roi.startsWith('-') ? 'text-rose-300' : 'text-emerald-300')}>{r.roi}</div>
                    <div className="text-gray-300">{r.dd}</div>
                    <div>
                      <span
                        className={cx(
                          'text-[11px] px-3 py-1 rounded-full border inline-flex items-center',
                          r.tone === 'ok' && 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200',
                          r.tone === 'warn' && 'border-amber-500/30 bg-amber-500/10 text-amber-200',
                          r.tone === 'idle' && 'border-white/10 bg-white/5 text-gray-300'
                        )}
                      >
                        {r.st}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <p className="text-xs text-gray-500 mt-3">
                Obs: tabela ainda usa dados de exemplo (placeholder) até termos endpoint de listagem.
              </p>
            </div>
          </div>

          <aside className="flex flex-col gap-3">
            <div className="glass-strong rounded-2xl p-5 border border-white/10">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-sm font-bold text-white/90 tracking-wide">Market watch</h2>
                <Link to="/monitor" className="text-xs text-emerald-300 hover:underline">
                  Monitor
                </Link>
              </div>

              <ul className="mt-4 space-y-3">
                {[
                  { pair: 'BTC/USDT', price: '$62,340', chg: '+1.2%' },
                  { pair: 'ETH/USDT', price: '$3,420', chg: '-0.4%' },
                  { pair: 'SOL/USDT', price: '$128', chg: '+3.1%' },
                ].map((row) => (
                  <li key={row.pair} className="grid grid-cols-[1fr_auto_auto] gap-3 items-baseline">
                    <div className="font-semibold text-white">{row.pair}</div>
                    <div className="text-gray-400 text-xs tabular-nums">{row.price}</div>
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
                  className="text-xs font-bold px-3 py-2 rounded-xl border border-white/10 text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
                >
                  <Activity className="w-4 h-4 inline-block mr-2" />
                  Abrir monitor
                </button>
              </div>
            </div>

            <div className="glass-strong rounded-2xl p-5 border border-white/10">
              <h2 className="text-sm font-bold text-white/90 tracking-wide">Atalhos</h2>
              <div className="mt-4 flex flex-wrap gap-2">
                {[
                  { to: '/combo/select', label: 'Combo', icon: Layers },
                  { to: '/kanban', label: 'Kanban', icon: Kanban },
                  { to: '/external/balances', label: 'Carteira', icon: Activity },
                ].map(({ to, label, icon: Icon }) => (
                  <Link
                    key={to}
                    to={to}
                    className="inline-flex items-center gap-2 px-3 py-2 rounded-full border border-white/10 bg-white/[0.03] text-xs text-gray-300 hover:text-white hover:bg-white/[0.06] transition-colors"
                  >
                    <Icon className="w-4 h-4" />
                    {label}
                  </Link>
                ))}
              </div>
            </div>

            <div className="glass-strong rounded-2xl p-5 border border-white/10">
              <h2 className="text-sm font-bold text-white/90 tracking-wide">Notas</h2>
              <p className="text-xs text-gray-400 mt-3">
                Implementação guiada pelo prototype (Option A). Algumas seções ainda usam placeholders até termos dados/endpoint
                dedicados.
              </p>
            </div>
          </aside>
        </section>
      </div>
    </main>
  )
}
