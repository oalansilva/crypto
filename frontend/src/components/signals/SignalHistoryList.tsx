import { useState } from 'react'
import { SignalHistoryCard } from './SignalHistoryCard'
import type { SignalHistoryItem, SignalHistoryResponse } from '@/types/signals'

interface SignalHistoryListProps {
  data: SignalHistoryResponse | null
  isLoading: boolean
  onFiltersChange: (filters: FiltersState) => void
  filters: FiltersState
  onPageChange: (page: number) => void
}

export type FiltersState = {
  asset: string
  status: string
  risk_profile: string
  data_inicio: string
  data_fim: string
  confidence_min: number
  pnl_filter: string
  sort_by: string
  sort_order: string
}

const PAGE_SIZE = 20

function formatPrice(value: number): string {
  const absValue = Math.abs(value)
  let maximumFractionDigits = 2

  if (absValue < 1000) maximumFractionDigits = 4
  if (absValue < 1) maximumFractionDigits = 6
  if (absValue < 0.01) maximumFractionDigits = 8

  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits,
  }).format(value)
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

const STATUS_CLASSES: Record<string, string> = {
  open: 'bg-sky-500/12 text-sky-300 border-sky-400/25',
  closed: 'bg-emerald-500/12 text-emerald-300 border-emerald-400/25',
}

function getDisplayStatus(status: string): 'open' | 'closed' {
  return status === 'ativo' ? 'open' : 'closed'
}

export function SignalHistoryList({ data, isLoading, onFiltersChange, filters, onPageChange }: SignalHistoryListProps) {
  const [selectedSignal, setSelectedSignal] = useState<SignalHistoryItem | null>(null)
  const [currentPage, setCurrentPage] = useState(1)

  const total = data?.total ?? 0
  const signals = data?.signals ?? []
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  function handlePageChange(page: number) {
    setCurrentPage(page)
    onPageChange(page)
  }

  function handleFilterChange(key: keyof FiltersState, value: string | number) {
    const newFilters = { ...filters, [key]: value }
    onFiltersChange(newFilters)
    setCurrentPage(1)
  }

  function handleClearFilters() {
    onFiltersChange({
      asset: '',
      status: '',
      risk_profile: '',
      data_inicio: '',
      data_fim: '',
      confidence_min: 0,
      pnl_filter: '',
      sort_by: 'created_at',
      sort_order: 'desc',
    })
    setCurrentPage(1)
  }

  const hasActiveFilters =
    filters.asset ||
    filters.status ||
    filters.risk_profile ||
    filters.data_inicio ||
    filters.data_fim ||
    filters.confidence_min > 0 ||
    filters.pnl_filter ||
    filters.sort_by !== 'created_at' ||
    filters.sort_order !== 'desc'

  function applyPreset(preset: 'best' | 'winners' | 'open') {
    if (preset === 'best') {
      onFiltersChange({
        ...filters,
        status: 'closed',
        confidence_min: 70,
        pnl_filter: 'positive',
        sort_by: 'pnl',
        sort_order: 'desc',
      })
      setCurrentPage(1)
      return
    }

    if (preset === 'winners') {
      onFiltersChange({
        ...filters,
        status: 'closed',
        pnl_filter: 'positive',
        sort_by: 'pnl',
        sort_order: 'desc',
      })
      setCurrentPage(1)
      return
    }

    onFiltersChange({
      ...filters,
      status: 'open',
      pnl_filter: '',
      sort_by: 'created_at',
      sort_order: 'desc',
    })
    setCurrentPage(1)
  }

  return (
    <>
      {/* Filters Panel */}
      <aside className="rounded-2xl border border-white/8 bg-[#101c2a] p-5">
        <h2 className="mb-4 text-sm font-semibold text-[var(--text-primary)]">Filtros</h2>

        <div className="space-y-4">
          <div>
            <div className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
              Atalhos
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => applyPreset('best')}
                className="rounded-xl border border-emerald-400/30 bg-emerald-400/10 px-3 py-2 text-xs font-semibold text-emerald-300 transition-all hover:bg-emerald-400/20"
              >
                Melhores sinais
              </button>
              <button
                type="button"
                onClick={() => applyPreset('winners')}
                className="rounded-xl border border-sky-400/30 bg-sky-400/10 px-3 py-2 text-xs font-semibold text-sky-300 transition-all hover:bg-sky-400/20"
              >
                Só vencedores
              </button>
              <button
                type="button"
                onClick={() => applyPreset('open')}
                className="rounded-xl border border-white/12 bg-white/[0.03] px-3 py-2 text-xs font-semibold text-[var(--text-secondary)] transition-all hover:bg-white/[0.06]"
              >
                Só abertos
              </button>
            </div>
          </div>

          {/* Asset */}
          <div>
            <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
              Ativo
            </label>
            <select
              value={filters.asset}
              onChange={(e) => handleFilterChange('asset', e.target.value)}
              className="w-full rounded-xl border border-white/12 bg-white/[0.03] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-emerald-400/50"
            >
              <option value="">Todos</option>
              {data?.signals
                .reduce<string[]>((acc, s) => (acc.includes(s.asset) ? acc : [...acc, s.asset]), [])
                .sort()
                .map((a) => (
                  <option key={a} value={a}>{a}</option>
                ))}
            </select>
          </div>

          {/* Type */}
          {/* Status */}
          <div>
            <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full rounded-xl border border-white/12 bg-white/[0.03] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-emerald-400/50"
            >
              <option value="">Todos</option>
              <option value="open">Aberto</option>
              <option value="closed">Fechado</option>
            </select>
          </div>

          <div>
            <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
              Perfil de risco
            </label>
            <select
              value={filters.risk_profile}
              onChange={(e) => handleFilterChange('risk_profile', e.target.value)}
              className="w-full rounded-xl border border-white/12 bg-white/[0.03] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-emerald-400/50"
            >
              <option value="">Todos</option>
              <option value="conservative">Conservative</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>

          {/* Date Range */}
          <div>
            <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
              Período
            </label>
            <div className="space-y-2">
              <input
                type="date"
                value={filters.data_inicio}
                onChange={(e) => handleFilterChange('data_inicio', e.target.value)}
                className="w-full rounded-xl border border-white/12 bg-white/[0.03] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-emerald-400/50"
              />
              <input
                type="date"
                value={filters.data_fim}
                onChange={(e) => handleFilterChange('data_fim', e.target.value)}
                className="w-full rounded-xl border border-white/12 bg-white/[0.03] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-emerald-400/50"
              />
            </div>
          </div>

          {/* Confidence Min */}
          <div>
            <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
              Confiança Mínima
            </label>
            <input
              type="range"
              min={0}
              max={100}
              value={filters.confidence_min}
              onChange={(e) => handleFilterChange('confidence_min', parseInt(e.target.value))}
              className="w-full accent-emerald-400"
            />
            <div className="mt-1 flex justify-between text-xs text-[var(--text-muted)]">
              <span>0%</span>
              <span className="font-semibold text-emerald-400">{filters.confidence_min}%</span>
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
              Resultado
            </label>
            <select
              value={filters.pnl_filter}
              onChange={(e) => handleFilterChange('pnl_filter', e.target.value)}
              className="w-full rounded-xl border border-white/12 bg-white/[0.03] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-emerald-400/50"
            >
              <option value="">Todos</option>
              <option value="positive">PnL positivo</option>
              <option value="negative">PnL negativo</option>
              <option value="realized">Só encerrados</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
                Ordenar por
              </label>
              <select
                value={filters.sort_by}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                className="w-full rounded-xl border border-white/12 bg-white/[0.03] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-emerald-400/50"
              >
                <option value="created_at">Data</option>
                <option value="confidence">Confiança</option>
                <option value="pnl">PnL</option>
              </select>
            </div>
            <div>
              <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
                Ordem
              </label>
              <select
                value={filters.sort_order}
                onChange={(e) => handleFilterChange('sort_order', e.target.value)}
                className="w-full rounded-xl border border-white/12 bg-white/[0.03] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-emerald-400/50"
              >
                <option value="desc">Maior primeiro</option>
                <option value="asc">Menor primeiro</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={() =>
                onFiltersChange({ ...filters })
              }
              className="flex-1 rounded-xl border border-emerald-400/30 bg-emerald-400/10 px-3 py-2 text-xs font-semibold text-emerald-300 transition-all hover:bg-emerald-400/20"
            >
              Aplicar
            </button>
            <button
              type="button"
              onClick={handleClearFilters}
              disabled={!hasActiveFilters}
              className="flex-1 rounded-xl border border-white/12 bg-white/[0.03] px-3 py-2 text-xs font-semibold text-[var(--text-secondary)] transition-all hover:bg-white/[0.06] disabled:opacity-40"
            >
              Limpar
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div>
        {/* List Header */}
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm font-semibold text-[var(--text-primary)]">Sinais</span>
          <span className="text-xs text-[var(--text-tertiary)]">
            {total === 0 ? 'Nenhum sinal' : `Mostrando ${signals.length} de ${total.toLocaleString('pt-BR')}`}
          </span>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-14 animate-pulse rounded-xl bg-white/[0.03]" />
            ))}
          </div>
        ) : signals.length === 0 ? (
          <div className="rounded-2xl border border-white/8 bg-[#101c2a] p-10 text-center">
            <div className="text-4xl opacity-30">📊</div>
            <p className="mt-3 font-semibold text-[var(--text-secondary)]">Nenhum sinal encontrado</p>
            <p className="mt-1 text-sm text-[var(--text-muted)]">Ajuste os filtros ou aguarde novos sinais.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/8">
                  {['Ativo', 'Tipo', 'Confiança', 'Target', 'Stop Loss', 'Status', 'PnL', 'Data', ''].map((h) => (
                    <th
                      key={h}
                      className="whitespace-nowrap px-3 py-2.5 text-left text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {signals.map((signal) => {
                  const displayStatus = getDisplayStatus(signal.status)
                  const pnlPct =
                    signal.entry_price && signal.exit_price && signal.type === 'BUY'
                      ? (((signal.exit_price - signal.entry_price) / signal.entry_price) * 100).toFixed(2)
                      : signal.type === 'SELL' && signal.entry_price && signal.exit_price
                        ? (((signal.entry_price - signal.exit_price) / signal.entry_price) * 100).toFixed(2)
                        : null

                  const pnlPositive = pnlPct !== null && parseFloat(pnlPct) >= 0
                  const pnlNegative = pnlPct !== null && parseFloat(pnlPct) < 0

                  return (
                    <tr
                      key={signal.id}
                      onClick={() => setSelectedSignal(signal)}
                      className="cursor-pointer border-b border-white/5 transition-colors hover:bg-white/[0.03]"
                    >
                      <td className="px-3 py-3 text-sm font-semibold text-[var(--text-primary)]">{signal.asset}</td>

                      {/* Type badge */}
                      <td className="px-3 py-3">
                        <span
                          className={[
                            'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold',
                            signal.type === 'BUY'
                              ? 'bg-emerald-500/15 text-emerald-300'
                              : signal.type === 'SELL'
                                ? 'bg-red-500/15 text-red-300'
                                : 'bg-white/8 text-zinc-300',
                          ].join(' ')}
                        >
                          {signal.type === 'BUY' ? '↑' : signal.type === 'SELL' ? '↓' : '⏸'} {signal.type}
                        </span>
                      </td>

                      {/* Confidence bar */}
                      <td className="px-3 py-3">
                        <div className="flex items-center gap-2">
                          <div className="h-1 w-16 overflow-hidden rounded-full bg-white/8">
                            <div
                              className={[
                                'h-full rounded-full',
                                signal.confidence >= 80
                                  ? 'bg-emerald-400'
                                  : signal.confidence >= 60
                                    ? 'bg-amber-400'
                                    : 'bg-red-400',
                              ].join(' ')}
                              style={{ width: `${signal.confidence}%` }}
                            />
                          </div>
                          <span className="text-xs font-semibold text-[var(--text-secondary)]">{signal.confidence}%</span>
                        </div>
                      </td>

                      {/* Target */}
                      <td className="px-3 py-3 text-sm font-semibold text-emerald-300">{formatPrice(signal.target_price)}</td>

                      {/* Stop Loss */}
                      <td className="px-3 py-3 text-sm font-semibold text-red-300">{formatPrice(signal.stop_loss)}</td>

                      {/* Status */}
                      <td className="px-3 py-3">
                        <span
                          className={[
                            'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide border',
                            STATUS_CLASSES[displayStatus] || 'bg-white/8 text-zinc-300 border-white/15',
                          ].join(' ')}
                        >
                          <span className="h-1 w-1 rounded-full bg-current" />
                          {displayStatus === 'open' ? 'Aberto' : 'Fechado'}
                        </span>
                      </td>

                      {/* PnL */}
                      <td className="px-3 py-3">
                        {pnlPct !== null ? (
                          <span
                            className={[
                              'text-sm font-semibold',
                              pnlPositive ? 'text-emerald-300' : 'text-red-300',
                            ].join(' ')}
                          >
                            {pnlPositive ? '+' : ''}{pnlPct}%
                          </span>
                        ) : (
                          <span className="text-sm text-[var(--text-muted)]">—</span>
                        )}
                      </td>

                      {/* Date */}
                      <td className="px-3 py-3 text-xs text-[var(--text-tertiary)]">{formatDate(signal.created_at)}</td>

                      {/* Action */}
                      <td className="px-3 py-3">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedSignal(signal)
                          }}
                          className="rounded-lg border border-white/10 bg-white/[0.03] px-2.5 py-1 text-[11px] font-semibold text-[var(--text-secondary)] transition-all hover:border-white/20 hover:bg-white/[0.06] hover:text-white"
                        >
                          Ver
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-5 flex items-center justify-between border-t border-white/8 pt-4">
            <span className="text-xs text-[var(--text-tertiary)]">
              Página {currentPage} de {totalPages}
            </span>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage <= 1}
                className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-sm font-semibold text-[var(--text-secondary)] transition-all hover:border-white/20 hover:bg-white/[0.06] hover:text-white disabled:opacity-40"
              >
                ‹
              </button>

              {/* Page numbers */}
              {[...Array(Math.min(5, totalPages))].map((_, i) => {
                let page: number
                if (totalPages <= 5) {
                  page = i + 1
                } else if (currentPage <= 3) {
                  page = i + 1
                } else if (currentPage >= totalPages - 2) {
                  page = totalPages - 4 + i
                } else {
                  page = currentPage - 2 + i
                }

                return (
                  <button
                    key={page}
                    type="button"
                    onClick={() => handlePageChange(page)}
                    className={[
                      'flex h-9 w-9 items-center justify-center rounded-xl border text-sm font-semibold transition-all',
                      page === currentPage
                        ? 'border-emerald-400/50 bg-emerald-400/15 text-emerald-300'
                        : 'border-white/10 bg-white/[0.03] text-[var(--text-secondary)] hover:border-white/20 hover:bg-white/[0.06] hover:text-white',
                    ].join(' ')}
                  >
                    {page}
                  </button>
                )
              })}

              <button
                type="button"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= totalPages}
                className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-sm font-semibold text-[var(--text-secondary)] transition-all hover:border-white/20 hover:bg-white/[0.06] hover:text-white disabled:opacity-40"
              >
                ›
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Drawer */}
      <SignalHistoryCard signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
    </>
  )
}
