import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Check, ChevronLeft, ChevronRight, Search, X } from 'lucide-react'

/* ---- types ---- */

type AxisId = 'templates' | 'symbols'

export type CatalogItem = { id: string; label: string; category: string; meta: string }

export type WorkingAxis = {
  mode: 'manual' | 'all'
  selected: Set<string>
  excluded: Set<string>
  query: string
  category: string
  page: number
  catalogState: 'ready' | 'loading' | 'error' | 'stale' | 'frozen'
}

export type SelectionSnapshot = { templates: WorkingAxis; symbols: WorkingAxis }

type Props = {
  open: boolean
  initialAxis?: AxisId
  templates: CatalogItem[]
  symbols: CatalogItem[]
  committed: SelectionSnapshot
  multiplier: number
  onApply: (state: SelectionSnapshot) => void
  onClose: () => void
}

/* ---- helpers ---- */

function totalCount(items: CatalogItem[]): number {
  return items.length
}

function isSelected(axis: WorkingAxis, id: string): boolean {
  return axis.mode === 'all' ? !axis.excluded.has(id) : axis.selected.has(id)
}

function selectedCount(axis: WorkingAxis, items: CatalogItem[]): number {
  return axis.mode === 'all'
    ? items.length - axis.excluded.size
    : axis.selected.size
}

function copyAxis(a: WorkingAxis): WorkingAxis {
  return {
    mode: a.mode,
    selected: new Set(a.selected),
    excluded: new Set(a.excluded),
    query: a.query,
    category: a.category,
    page: Math.max(1, a.page),
    catalogState: a.catalogState,
  }
}

function copyState(s: SelectionSnapshot): SelectionSnapshot {
  return { templates: copyAxis(s.templates), symbols: copyAxis(s.symbols) }
}

function signature(s: SelectionSnapshot): string {
  return JSON.stringify({
    t: { m: s.templates.mode, s: [...s.templates.selected].sort(), e: [...s.templates.excluded].sort() },
    y: { m: s.symbols.mode, s: [...s.symbols.selected].sort(), e: [...s.symbols.excluded].sort() },
  })
}

function axisName(a: AxisId): string {
  return a === 'templates' ? 'templates' : 'símbolos'
}

/* ---- component ---- */

export function SelectionWorkbench({
  open,
  initialAxis,
  templates,
  symbols,
  committed,
  multiplier,
  onApply,
  onClose,
}: Props) {
  const [activeAxis, setActiveAxis] = useState<AxisId>('templates')
  const [working, setWorking] = useState<SelectionSnapshot>(() => copyState(committed))
  const [openingSignature, setOpeningSignature] = useState<string>('')
  const [discardConfirm, setDiscardConfirm] = useState(false)
  const [toast, setToast] = useState('')
  const searchRef = useRef<HTMLInputElement | null>(null)
  const toastTimer = useRef<number | null>(null)
  const keepEditingRef = useRef<HTMLButtonElement | null>(null)

  useEffect(() => {
    if (open) {
      const snap = copyState(committed)
      setWorking(snap)
      setOpeningSignature(signature(snap))
      setDiscardConfirm(false)
      setToast('')
      setActiveAxis(initialAxis ?? 'templates')
      setTimeout(() => searchRef.current?.focus(), 0)
    }
    return () => {
      if (toastTimer.current !== null) window.clearTimeout(toastTimer.current)
    }
  }, [open, committed, initialAxis])

  useEffect(() => {
    if (discardConfirm) {
      keepEditingRef.current?.focus()
    }
  }, [discardConfirm])

  const announce = useCallback((msg: string) => {
    setToast(msg)
    if (toastTimer.current !== null) window.clearTimeout(toastTimer.current)
    toastTimer.current = window.setTimeout(() => setToast(''), 4000)
  }, [])

  const isDirty = useMemo(() => signature(working) !== openingSignature, [working, openingSignature])

  const requestClose = useCallback(() => {
    if (isDirty) {
      setDiscardConfirm(true)
    } else {
      onClose()
    }
  }, [isDirty, onClose])

  const applySelection = useCallback(() => {
    const tc = selectedCount(working.templates, templates)
    const sc = selectedCount(working.symbols, symbols)
    if (tc === 0) {
      setActiveAxis('templates')
      announce('Selecione ao menos um template.')
      return
    }
    if (sc === 0) {
      setActiveAxis('symbols')
      announce('Selecione ao menos um símbolo.')
      return
    }
    onApply(copyState(working))
    onClose()
  }, [working, templates, symbols, announce, onApply, onClose])

  /* ---- axis helpers ---- */

  const axis = useMemo(() => working[activeAxis], [working, activeAxis])
  const items = activeAxis === 'templates' ? templates : symbols
  const PAGE_SIZE = 6

  const filtered = useMemo(() => {
    const term = axis.query.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    return items.filter((item) => {
      if (axis.category !== 'all' && item.category !== axis.category) return false
      if (!term) return true
      const haystack = `${item.label} ${item.meta} ${item.category}`.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      return haystack.includes(term)
    })
  }, [items, axis.query, axis.category])

  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const page = Math.min(axis.page, pages)
  const slice = useMemo(() => filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE), [filtered, page])

  const categories = useMemo(() => [...new Set(items.map((i) => i.category))].sort(), [items])
  const sc = selectedCount(axis, items)

  const reviewIds = useMemo(() => {
    if (axis.mode === 'all') return [...axis.excluded].slice(0, 8)
    return [...axis.selected].slice(0, 8)
  }, [axis])
  const reviewTotal = axis.mode === 'all' ? axis.excluded.size : axis.selected.size

  const itemLabel = useCallback((id: string) => items.find((i) => i.id === id)?.label ?? id, [items])

  const toggle = useCallback(
    (id: string) => {
      setWorking((prev) => {
        const a = copyAxis(prev[activeAxis])
        if (a.mode === 'all') {
          if (a.excluded.has(id)) a.excluded.delete(id); else a.excluded.add(id)
        } else {
          if (a.selected.has(id)) a.selected.delete(id); else a.selected.add(id)
        }
        a.catalogState = 'ready'
        announce(`${items.find((i) => i.id === id)?.label ?? id} ${isSelected(prev[activeAxis], id) ? 'excluído da' : 'adicionado à'} seleção. ${selectedCount(a, items)} ${axisName(activeAxis)} selecionados.`)
        return { ...prev, [activeAxis]: a }
      })
    },
    [activeAxis, items, announce],
  )

  const addMany = useCallback(
    (ids: string[]) => {
      setWorking((prev) => {
        const a = copyAxis(prev[activeAxis])
        if (a.mode === 'all') ids.forEach((id) => a.excluded.delete(id))
        else ids.forEach((id) => a.selected.add(id))
        a.catalogState = 'ready'
        announce(`${ids.length} resultados adicionados. ${selectedCount(a, items)} ${axisName(activeAxis)} selecionados.`)
        return { ...prev, [activeAxis]: a }
      })
    },
    [activeAxis, items, announce],
  )

  const selectAllAxis = useCallback(() => {
    setWorking((prev) => {
      const a = copyAxis(prev[activeAxis])
      a.mode = 'all'; a.selected.clear(); a.excluded.clear()
      a.catalogState = 'ready'
      announce(`Catálogo inteiro de ${axisName(activeAxis)} selecionado.`)
      return { ...prev, [activeAxis]: a }
    })
  }, [activeAxis, announce])

  const clearAxis = useCallback(() => {
    setWorking((prev) => {
      const a = copyAxis(prev[activeAxis])
      a.mode = 'manual'; a.selected.clear(); a.excluded.clear()
      a.catalogState = 'ready'
      announce(`Seleção de ${axisName(activeAxis)} limpa.`)
      return { ...prev, [activeAxis]: a }
    })
  }, [activeAxis, announce])

  /* ---- keyboard ---- */

  useEffect(() => {
    if (!open) return
    const handle = (e: KeyboardEvent) => {
      if (discardConfirm) {
        if (e.key === 'Escape') { e.preventDefault(); setDiscardConfirm(false); searchRef.current?.focus() }
        return
      }
      if (e.key === 'Escape') { e.preventDefault(); requestClose(); return }
      if (e.key === 'Enter' && document.activeElement === searchRef.current) {
        if (slice.length) {
          e.preventDefault()
          toggle(slice[0].id)
        }
      }
    }
    window.addEventListener('keydown', handle)
    return () => window.removeEventListener('keydown', handle)
  }, [open, discardConfirm, requestClose, slice, toggle])

  const handleTabKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key !== 'Tab') return
    const dialog = e.currentTarget.closest('[role="dialog"]')
    if (!dialog) return
    const focusables = dialog.querySelectorAll<HTMLElement>(
      'button:not(:disabled), input:not(:disabled), select:not(:disabled), [tabindex]:not([tabindex="-1"])',
    )
    if (focusables.length === 0) return
    const first = focusables[0]
    const last = focusables[focusables.length - 1]
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault()
      last.focus()
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault()
      first.focus()
    }
  }, [])

  const handleTabsKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return
    e.preventDefault()
    const order: AxisId[] = ['templates', 'symbols']
    const current = order.indexOf(activeAxis)
    const next = e.key === 'ArrowRight'
      ? order[(current + 1) % order.length]
      : order[(current - 1 + order.length) % order.length]
    setActiveAxis(next)
    setWorking((p) => ({ ...p, [next]: { ...p[next], page: 1 } }))
    setTimeout(() => document.getElementById(`tab-${next}`)?.focus(), 0)
  }, [activeAxis])

  if (!open) return null

  const projected = selectedCount(working.templates, templates) * selectedCount(working.symbols, symbols) * multiplier
  const limited = projected > 1000

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-6 max-md:p-2"
      onClick={(e) => { if (e.target === e.currentTarget) requestClose() }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="workbench-title"
        aria-describedby="workbench-desc"
        id="selection-workbench"
        onKeyDown={handleTabKeyDown}
        className="flex h-full max-h-[calc(100dvh-48px)] w-full max-w-[1060px] flex-col overflow-hidden rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] shadow-[0_24px_72px_rgba(0,0,0,0.5)]"
      >
        {/* Header */}
        <header className="flex items-start justify-between gap-4 border-b border-[var(--border-default)] px-5 py-3.5">
          <div>
            <h1 id="workbench-title" className="text-xl font-semibold text-[var(--text-primary)]">Montar escopo da varredura</h1>
            <p id="workbench-desc" className="mt-1 text-xs text-[var(--text-tertiary)]">Busque, revise e aplique a seleção sem rolar o catálogo inteiro.</p>
          </div>
          <button
            type="button"
            onClick={requestClose}
            className="grid h-11 w-11 place-items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-[var(--bg-input)]"
            aria-label="Fechar editor de seleção"
          >
            <X className="h-5 w-5" />
          </button>
        </header>

        {/* Tabs */}
        <div className="grid grid-cols-2 border-b border-[var(--border-default)]" role="tablist" aria-label="Catálogos" onKeyDown={handleTabsKeyDown}>
          {(['templates', 'symbols'] as const).map((ax) => (
            <button
              key={ax}
              role="tab"
              type="button"
              id={`tab-${ax}`}
              aria-selected={activeAxis === ax}
              aria-controls={`panel-${ax}`}
              tabIndex={activeAxis === ax ? 0 : -1}
              onClick={() => { setActiveAxis(ax); setWorking((p) => ({ ...p, [ax]: { ...p[ax], page: 1 } })); setTimeout(() => searchRef.current?.focus(), 0) }}
              className={`relative min-h-[48px] border-0 font-semibold text-[var(--text-tertiary)] ${activeAxis === ax ? 'bg-[var(--bg-elevated)] text-[var(--text-primary)]' : 'bg-[var(--bg-secondary)]'}`}
            >
              {ax === 'templates' ? 'Templates' : 'Símbolos'}{' '}
              <span className={`ml-2 text-[11px] font-normal ${activeAxis === ax ? 'text-[var(--accent-primary)]' : ''}`}>
                {selectedCount(working[ax], ax === 'templates' ? templates : symbols)}/{totalCount(ax === 'templates' ? templates : symbols)}
              </span>
              {activeAxis === ax && <span className="absolute inset-x-5 bottom-0 h-0.5 bg-[var(--accent-primary)]" />}
            </button>
          ))}
        </div>

        {/* Panel */}
        <div id={`panel-${activeAxis}`} role="tabpanel" aria-labelledby={`tab-${activeAxis}`} className="flex min-h-0 flex-1 overflow-hidden">
          <div className="grid min-w-0 flex-1 grid-cols-[minmax(0,1fr)_300px] max-md:grid-cols-1">
            {/* Catalog */}
            <section className="flex min-h-0 min-w-0 flex-col gap-2.5 border-r border-[var(--border-default)] p-3.5 max-md:order-2" aria-label={`Catálogo de ${axisName(activeAxis)}`} role="region">
              <div className="grid grid-cols-[minmax(0,1fr)_200px] gap-2 max-md:grid-cols-[minmax(0,1fr)_148px]">
                <div className="relative">
                  <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
                  <input
                    ref={searchRef}
                    type="search"
                    value={axis.query}
                    onChange={(e) => setWorking((p) => ({ ...p, [activeAxis]: { ...p[activeAxis], query: e.target.value, page: 1 } }))}
                    placeholder={activeAxis === 'templates' ? 'Buscar nome ou código' : 'Buscar ticker ou par'}
                    className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] py-2 pl-9 pr-3 text-sm text-[var(--text-primary)] outline-none"
                    disabled={axis.catalogState === 'loading' || axis.catalogState === 'frozen'}
                  />
                </div>
                <select
                  value={axis.category}
                  onChange={(e) => setWorking((p) => ({ ...p, [activeAxis]: { ...p[activeAxis], category: e.target.value, page: 1 } }))}
                  className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)] max-md:text-[11px] max-md:px-2"
                  disabled={axis.catalogState === 'loading' || axis.catalogState === 'frozen'}
                >
                  <option value="all">Todas as categorias</option>
                  {categories.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div className="flex items-center justify-between gap-2">
                <span className="text-xs text-[var(--text-tertiary)]">{filtered.length} resultados · {PAGE_SIZE} por página</span>
                <div className="flex gap-1.5 max-md:grid max-md:w-full max-md:grid-cols-4">
                  <button data-testid="select-page" type="button" onClick={() => addMany(slice.map((i) => i.id))} disabled={axis.catalogState === 'loading' || axis.catalogState === 'frozen' || slice.length === 0} className="min-h-[44px] rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-2.5 text-xs font-semibold text-[var(--text-secondary)] disabled:opacity-40">
                    <span className="max-md:hidden">Adicionar página</span><span className="md:hidden">Página</span>
                  </button>
                  <button data-testid="select-filtered" type="button" onClick={() => addMany(filtered.map((i) => i.id))} disabled={axis.catalogState === 'loading' || axis.catalogState === 'frozen' || filtered.length === 0} className="min-h-[44px] rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-2.5 text-xs font-semibold text-[var(--text-secondary)] disabled:opacity-40">
                    <span className="max-md:hidden">Adicionar filtrados</span><span className="md:hidden">Filtrados</span>
                  </button>
                  <button data-testid="select-all" type="button" onClick={selectAllAxis} disabled={axis.mode === 'all' || axis.catalogState === 'loading' || axis.catalogState === 'frozen'} className="min-h-[44px] rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-2.5 text-xs font-semibold text-[var(--text-secondary)] disabled:opacity-40">
                    <span className="max-md:hidden">Catálogo inteiro</span><span className="md:hidden">Catálogo</span>
                  </button>
                  <button data-testid="clear-axis" type="button" onClick={clearAxis} disabled={axis.catalogState === 'loading' || axis.catalogState === 'frozen' || sc === 0} className="min-h-[44px] rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-2.5 text-xs font-semibold text-[var(--text-secondary)] disabled:opacity-40">
                    <span className="max-md:hidden">Limpar seleção</span><span className="md:hidden">Limpar</span>
                  </button>
                </div>
              </div>

              {/* Notice */}
              {limited ? (
                <div className="flex items-center gap-2.5 rounded-md border border-[rgba(245,158,11,0.4)] bg-[rgba(245,158,11,0.07)] p-2.5 text-[11px] text-[#fbbf24]">
                  <div>
                    <strong className="block">Limite projetado excedido</strong>
                    <p className="mt-0.5">{projected.toLocaleString('pt-BR')} combinações brutas; limite do servidor: 1.000. Reduza o escopo.</p>
                  </div>
                </div>
              ) : null}

              {/* Results grid */}
              <div className="min-h-0 flex-1 overflow-y-auto">
                <div className="grid grid-cols-2 gap-2 max-md:grid-cols-1" role="list" aria-label={`Resultados de ${axisName(activeAxis)}`}>
                  {slice.length === 0 ? (
                    <div className="col-span-full grid place-items-center py-8 text-center text-xs text-[var(--text-tertiary)]">
                      <div>
                        <strong className="block text-[var(--text-secondary)]">Nenhum resultado</strong>
                        <span className="mt-1 block">Ajuste a busca ou a categoria.</span>
                      </div>
                    </div>
                  ) : null}
                  {slice.map((item) => {
                    const sel = isSelected(axis, item.id)
                    const busy = axis.catalogState === 'loading' || axis.catalogState === 'frozen'
                    return (
                      <div
                        key={item.id}
                        role="listitem"
                        className={`flex min-h-[52px] items-stretch overflow-hidden rounded-md border text-sm ${sel ? 'border-[rgba(252,213,53,0.45)] bg-[rgba(252,213,53,0.07)]' : 'border-[var(--border-default)] bg-[var(--bg-secondary)]'}`}
                      >
                        <button
                          type="button"
                          onClick={() => toggle(item.id)}
                          disabled={busy}
                          className="min-w-0 flex-1 px-3 py-2 text-left"
                        >
                          <b className="block truncate text-[13px] text-[var(--text-secondary)]">{item.label}</b>
                          <small className="block truncate text-[11px] text-[var(--text-tertiary)]">{item.meta} · {item.category}</small>
                        </button>
                        <button
                          type="button"
                          onClick={() => toggle(item.id)}
                          disabled={busy}
                          className={`min-w-[96px] border-l border-[var(--border-default)] px-3 text-[11px] font-bold ${sel ? 'text-[var(--accent-primary)]' : 'text-[var(--text-tertiary)]'} max-md:min-w-[92px]`}
                        >
                          {sel ? (axis.mode === 'all' ? 'Excluir da seleção' : 'Remover da seleção') : 'Adicionar à seleção'}
                        </button>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Pager */}
              <div className="grid grid-cols-[44px_1fr_44px] items-center gap-2">
                <button
                  type="button"
                  disabled={page <= 1}
                  onClick={() => setWorking((p) => ({ ...p, [activeAxis]: { ...p[activeAxis], page: Math.max(1, page - 1) } }))}
                  className="grid h-11 w-11 place-items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] text-[var(--text-secondary)] disabled:opacity-40"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <span className="text-center text-xs text-[var(--text-tertiary)]">Página {page} de {pages}</span>
                <button
                  type="button"
                  disabled={page >= pages}
                  onClick={() => setWorking((p) => ({ ...p, [activeAxis]: { ...p[activeAxis], page: Math.min(pages, page + 1) } }))}
                  className="grid h-11 w-11 place-items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] text-[var(--text-secondary)] disabled:opacity-40"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
            </section>

            {/* Review panel */}
            <aside className="flex min-h-0 flex-col bg-[var(--bg-secondary)] p-3.5 max-md:order-1 max-md:flex-none max-md:border-b max-md:border-[var(--border-default)]" aria-label="Revisão da seleção">
              <h3 className="text-sm font-semibold text-[var(--text-secondary)]">{sc} {axisName(activeAxis)} selecionados</h3>
              <p className="mt-1 text-xs text-[var(--text-tertiary)]">
                {axis.mode === 'all'
                  ? `Catálogo inteiro · ${axis.excluded.size} exceções`
                  : 'Seleção manual · revisão preservada no rascunho'}
              </p>
              <div className="mt-1.5 rounded-md border border-[rgba(59,130,246,0.34)] bg-[rgba(59,130,246,0.07)] p-2 text-[11px] text-[#bfdbfe] max-md:p-1.5">
                {axis.mode === 'all'
                  ? `Exceções explícitas: ${[...axis.excluded].slice(0, 8).map((id) => itemLabel(id)).join(', ')}${axis.excluded.size > 8 ? ` +${axis.excluded.size - 8} exceções` : ''}.`
                  : 'Busca, categoria e página ficam preservadas por aba.'}
              </div>
              <div className="mt-2 flex flex-1 flex-wrap items-start gap-2 overflow-y-auto max-md:mt-1.5 max-md:max-h-[104px]" role="list" aria-label={axis.mode === 'all' ? 'Exceções explícitas' : 'Itens selecionados'}>
                {reviewIds.map((id) => (
                  <span key={id} className="inline-flex min-h-[28px] max-w-full items-center gap-1 rounded-md border border-[var(--border-default)] bg-[var(--bg-primary)] py-0.5 pl-2 pr-1 text-[11px] text-[var(--text-secondary)]">
                    <span className="min-w-0 break-words leading-tight">{itemLabel(id)}</span>
                    <button type="button" onClick={() => toggle(id)} className="grid h-6 w-6 place-items-center rounded text-[var(--text-tertiary)] hover:bg-[rgba(252,213,53,0.1)] hover:text-[var(--accent-primary)]" aria-label={axis.mode === 'all' ? `Incluir ${itemLabel(id)}` : `Remover ${itemLabel(id)}`}>
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </span>
                ))}
                {reviewTotal > reviewIds.length ? <span className="inline-flex items-center min-h-[28px] rounded border border-dashed border-[var(--border-default)] px-2 py-0.5 text-[11px] text-[var(--text-tertiary)]">+{reviewTotal - reviewIds.length} {axis.mode === 'all' ? 'exceções' : 'itens'} na contagem</span> : null}
              </div>
            </aside>
          </div>
        </div>

        {/* Footer */}
        <footer className="flex items-center justify-between gap-3 border-t border-[var(--border-default)] px-4 py-2.5">
          <div className="min-w-0 text-[11px] text-[var(--text-tertiary)]" role="status">
            {limited
              ? <><strong className="text-[var(--text-secondary)]">Limite:</strong> {projected.toLocaleString('pt-BR')} combinações projetadas excedem 1.000.</>
              : <><strong className="text-[var(--text-secondary)]">Projeção local:</strong> {projected.toLocaleString('pt-BR')} combinações; o servidor revalida ao aplicar.</>}
          </div>
          <div className="flex gap-2">
            <button type="button" onClick={requestClose} className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3.5 text-sm font-semibold text-[var(--text-secondary)] hover:bg-[var(--bg-input)]">Cancelar</button>
            <button
              type="button"
              onClick={applySelection}
              className="inline-flex min-h-[44px] items-center rounded-md border border-[rgba(252,213,53,0.28)] bg-[var(--accent-primary)] px-3.5 text-sm font-semibold text-[#181a20] hover:bg-[var(--accent-hover)]"
            >
              Aplicar seleção
            </button>
          </div>
        </footer>

        {/* Discard confirmation */}
        {discardConfirm && (
          <div className="absolute bottom-14 inset-x-4 z-10 flex items-center justify-between gap-3 rounded-lg border border-[rgba(245,158,11,0.46)] bg-[var(--bg-elevated)] p-3 shadow-[0_16px_42px_rgba(0,0,0,0.46)]" role="alertdialog" aria-modal="true" aria-labelledby="discard-title">
            <p id="discard-title" className="text-xs text-[var(--text-secondary)]"><strong>Descartar alterações não aplicadas?</strong><br />O rascunho salvo será mantido.</p>
            <div className="flex gap-2">
              <button ref={keepEditingRef} type="button" onClick={() => { setDiscardConfirm(false); searchRef.current?.focus() }} className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 text-xs font-semibold text-[var(--text-secondary)]">Continuar editando</button>
              <button type="button" onClick={onClose} className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 text-xs font-semibold text-[var(--text-secondary)]">Descartar alterações</button>
            </div>
          </div>
        )}

        {/* Toast */}
        {toast ? (
          <div role="status" className="absolute bottom-20 right-4 z-20 flex max-w-[min(360px,calc(100vw-32px))] items-start gap-2.5 rounded-md border border-[rgba(252,213,53,0.35)] bg-[var(--bg-elevated)] px-3 py-2 text-sm text-[var(--text-secondary)] shadow-2xl">
            <Check className="mt-0.5 h-4 w-4 shrink-0 text-[var(--accent-primary)]" />
            <span>{toast}</span>
          </div>
        ) : null}
      </section>
    </div>
  )
}
