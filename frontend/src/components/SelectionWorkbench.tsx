import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Check, X } from 'lucide-react'

/* ---- types (inalterados para compat com DiscoveryPage) ---- */

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
  multiplier?: number
  onApply: (state: SelectionSnapshot) => void
  onClose: () => void
}

/* ---- helpers ---- */

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

function normalize(v: string): string {
  return v.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
}

/* ---- component ----
 * Card 852 (T18, fiel ao protótipo #m-adv): modal simples de eixo único —
 * campo de filtro + lista rolável única com checkboxes (sem paginação) +
 * contador ao vivo "X de N" + exatamente 2 ações de eixo inteiro
 * (Selecionar todos / Limpar seleção) + Aplicar seleção.
 * Sem tabs, sem cards, sem pager 6/página, sem "Projeção local", sem botões
 * por item. O filtrado fino continua no inline da DiscoveryPage.
 */

export function SelectionWorkbench({
  open,
  initialAxis,
  templates,
  symbols,
  committed,
  onApply,
  onClose,
}: Props) {
  // Eixo único por abertura (sem tabs): definido pelo trigger.
  const activeAxis: AxisId = initialAxis ?? 'templates'
  const [working, setWorking] = useState<SelectionSnapshot>(() => copyState(committed))
  const [query, setQuery] = useState('')
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
      setQuery('')
      setDiscardConfirm(false)
      setToast('')
      setTimeout(() => searchRef.current?.focus(), 0)
    }
    return () => {
      if (toastTimer.current !== null) window.clearTimeout(toastTimer.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

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

  const items = activeAxis === 'templates' ? templates : symbols
  const workingAxis = working[activeAxis]
  const count = selectedCount(workingAxis, items)

  const filtered = useMemo(() => {
    const term = normalize(query.trim())
    if (!term) return items
    return items.filter((item) =>
      normalize(`${item.label} ${item.id} ${item.meta} ${item.category}`).includes(term),
    )
  }, [items, query])

  const applySelection = useCallback(() => {
    const tc = selectedCount(working.templates, templates)
    const sc = selectedCount(working.symbols, symbols)
    if (tc === 0) {
      announce('Selecione ao menos um template.')
      return
    }
    if (sc === 0) {
      announce('Selecione ao menos um símbolo.')
      return
    }
    onApply(copyState(working))
    onClose()
  }, [working, templates, symbols, announce, onApply, onClose])

  const toggle = useCallback(
    (id: string) => {
      setWorking((prev) => {
        const a = copyAxis(prev[activeAxis])
        const was = isSelected(prev[activeAxis], id)
        if (a.mode === 'all') {
          if (a.excluded.has(id)) a.excluded.delete(id)
          else a.excluded.add(id)
        } else {
          if (a.selected.has(id)) a.selected.delete(id)
          else a.selected.add(id)
        }
        a.catalogState = 'ready'
        const next = { ...prev, [activeAxis]: a }
        announce(
          `${items.find((i) => i.id === id)?.label ?? id} ${was ? 'excluído da' : 'adicionado à'} seleção. ${selectedCount(a, items)} de ${items.length} selecionados.`,
        )
        return next
      })
    },
    [activeAxis, items, announce],
  )

  const selectAllAxis = useCallback(() => {
    setWorking((prev) => {
      const a = copyAxis(prev[activeAxis])
      a.mode = 'all'
      a.selected.clear()
      a.excluded.clear()
      a.catalogState = 'ready'
      announce(`Todos os ${axisName(activeAxis)} selecionados. ${items.length} de ${items.length} selecionados.`)
      return { ...prev, [activeAxis]: a }
    })
  }, [activeAxis, announce, items.length])

  const clearAxis = useCallback(() => {
    setWorking((prev) => {
      const a = copyAxis(prev[activeAxis])
      a.mode = 'manual'
      a.selected.clear()
      a.excluded.clear()
      a.catalogState = 'ready'
      announce(`Seleção de ${axisName(activeAxis)} limpa. 0 de ${items.length} selecionados.`)
      return { ...prev, [activeAxis]: a }
    })
  }, [activeAxis, announce, items.length])

  /* ---- keyboard: Escape fecha (ou abre confirmação se sujo) ---- */

  useEffect(() => {
    if (!open) return
    const handle = (e: KeyboardEvent) => {
      if (discardConfirm) {
        if (e.key === 'Escape') {
          e.preventDefault()
          setDiscardConfirm(false)
          searchRef.current?.focus()
        }
        return
      }
      if (e.key === 'Escape') {
        e.preventDefault()
        requestClose()
      }
    }
    window.addEventListener('keydown', handle)
    return () => window.removeEventListener('keydown', handle)
  }, [open, discardConfirm, requestClose])

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

  if (!open) return null

  const busy = workingAxis.catalogState === 'loading' || workingAxis.catalogState === 'frozen'

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
        className="flex max-h-[90vh] w-full max-w-[520px] flex-col overflow-auto rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] shadow-[0_24px_72px_rgba(0,0,0,0.5)]"
      >
        <header className="flex items-start justify-between gap-4 border-b border-[var(--border-default)] px-5 py-4">
          <div>
            <h1 id="workbench-title" className="text-xl font-semibold text-[var(--text-primary)]">Edição avançada</h1>
            <p id="workbench-desc" className="mt-1 text-xs text-[var(--text-tertiary)]">
              {activeAxis === 'templates'
                ? 'Templates — selecionar todos ou limpar seleção.'
                : 'Símbolos — selecionar todos ou limpar seleção.'}
            </p>
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

        <div className="flex flex-col gap-2.5 p-5">
          <input
            ref={searchRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filtrar…"
            aria-label="Filtrar itens"
            data-testid={activeAxis === 'templates' ? 'adv-templates-search' : 'adv-symbols-search'}
            className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none"
            disabled={busy}
          />
          {/* lista rolável única — sem paginação, sem cards, sem botões por item */}

          <div
            role="group"
            aria-label={activeAxis === 'templates' ? 'Templates' : 'Símbolos'}
            className="flex max-h-[240px] min-h-[120px] flex-col gap-1.5 overflow-auto"
          >
            {filtered.length === 0 ? (
              <p className="py-6 text-center text-xs text-[var(--text-tertiary)]">
                Nenhum item neste filtro — ajuste a busca.
              </p>
            ) : null}
            {filtered.map((item) => {
              const sel = isSelected(workingAxis, item.id)
              return (
                <label
                  key={item.id}
                  className="flex min-h-[44px] cursor-pointer items-center gap-2.5 rounded-md border border-[var(--border-default)] bg-[var(--bg-primary)] px-3 py-2 text-[13px] text-[var(--text-secondary)]"
                >
                  <input
                    type="checkbox"
                    checked={sel}
                    disabled={busy}
                    onChange={() => toggle(item.id)}
                    aria-label={item.label}
                    className="h-[18px] w-[18px] shrink-0 accent-[#fcd535]"
                  />
                  <span className="min-w-0 truncate">{item.label}</span>
                </label>
              )
            })}
          </div>

          <p className="text-xs text-[var(--text-tertiary)]" aria-live="polite" data-testid="adv-count">
            {count} de {items.length} selecionados
          </p>

          <div className="mt-1 flex flex-wrap gap-2">
            <button
              data-testid="select-all"
              type="button"
              onClick={selectAllAxis}
              disabled={busy || workingAxis.mode === 'all'}
              className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3.5 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--bg-input)] disabled:opacity-40"
            >
              Selecionar todos
            </button>
            <button
              data-testid="clear-axis"
              type="button"
              onClick={clearAxis}
              disabled={busy || count === 0}
              className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3.5 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--bg-input)] disabled:opacity-40"
            >
              Limpar seleção
            </button>
            <button
              type="button"
              onClick={applySelection}
              className="ml-auto inline-flex min-h-[44px] items-center rounded-md border border-[rgba(252,213,53,0.28)] bg-[var(--accent-primary)] px-3.5 text-sm font-semibold text-[#181a20] hover:bg-[var(--accent-hover)]"
            >
              Aplicar seleção
            </button>
          </div>
        </div>

        {/* Discard confirmation */}
        {discardConfirm && (
          <div className="mx-4 mb-4 flex items-center justify-between gap-3 rounded-lg border border-[rgba(245,158,11,0.46)] bg-[var(--bg-elevated)] p-3 shadow-[0_16px_42px_rgba(0,0,0,0.46)]" role="alertdialog" aria-modal="true" aria-labelledby="discard-title">
            <p id="discard-title" className="text-xs text-[var(--text-secondary)]"><strong>Descartar alterações não aplicadas?</strong><br />O rascunho salvo será mantido.</p>
            <div className="flex gap-2">
              <button ref={keepEditingRef} type="button" onClick={() => { setDiscardConfirm(false); searchRef.current?.focus() }} className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 text-xs font-semibold text-[var(--text-secondary)]">Continuar editando</button>
              <button type="button" onClick={onClose} className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 text-xs font-semibold text-[var(--text-secondary)]">Descartar alterações</button>
            </div>
          </div>
        )}

        {/* Toast */}
        {toast ? (
          <div role="status" className="mx-4 mb-4 flex max-w-[min(360px,calc(100vw-32px))] items-start gap-2.5 rounded-md border border-[rgba(252,213,53,0.35)] bg-[var(--bg-elevated)] px-3 py-2 text-sm text-[var(--text-secondary)] shadow-2xl">
            <Check className="mt-0.5 h-4 w-4 shrink-0 text-[var(--accent-primary)]" />
            <span>{toast}</span>
          </div>
        ) : null}
      </section>
    </div>
  )
}
