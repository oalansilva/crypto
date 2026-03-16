import { useEffect, useMemo, useRef, useState, type DragEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Kanban, Search, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { API_BASE_URL } from '@/lib/apiBase'

type CoordinationChangeItem = {
  id: string
  title?: string | null
  description?: string | null
  card_number?: number | null
  path: string
  status: Record<string, string>
  archived: boolean
  column: string
  position?: number
  has_bugs?: boolean
}

type CoordinationChangeListResponse = {
  items: CoordinationChangeItem[]
}

type TaskChecklistItem = {
  text: string
  checked?: boolean | null
  code?: string | null
  title?: string | null
  children?: TaskChecklistItem[]
}

type TaskChecklistSection = {
  title: string
  items: TaskChecklistItem[]
}

type ChangeTasksChecklistResponse = {
  change_id: string
  path: string
  sections: TaskChecklistSection[]
}

type CoordinationCommentItem = {
  id: string
  change: string
  author: string
  created_at: string
  body: string
}

type CoordinationCommentsListResponse = {
  change_id: string
  items: CoordinationCommentItem[]
}

type ChangeUpdateResponse = {
  id: string
  project_id: string
  change_id: string
  title: string
  description: string
  status: string
  card_number?: number | null
  created_at: string
  updated_at: string
}

const DESKTOP_DRAG_MIME = 'application/x-kanban-change-id'

const MOBILE_SWIPE_THRESHOLD = 48
const MOBILE_LONG_PRESS_MS = 420
const MOBILE_LONG_PRESS_MOVE_TOLERANCE = 12

const COLUMNS_ORDER = [
  'Pending',
  'PO',
  'DESIGN',
  'Alan approval',
  'DEV',
  'QA',
  'Alan homologation',
  'Archived',
] as const

function StatusLine({ label, value }: { label: string; value?: string }) {
  if (!value) return null
  return (
    <div className="flex items-center justify-between gap-2 text-[11px] text-gray-300">
      <span className="text-gray-400">{label}</span>
      <span className="font-mono capitalize">{value}</span>
    </div>
  )
}

function formatTs(iso: string) {
  // backend uses UTC ISO-8601; keep it readable in the user's locale.
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString()
}

// Returns additional CSS classes for bug items (card #14: tipos-itens)
function getBugCardClass(selected: boolean, hasBugs?: boolean): string {
  if (!hasBugs) return ''
  // Coral/red styling for bug items: border + subtle background tint
  return selected
    ? 'border-red-400/60 bg-red-950/30 ring-2 ring-red-400/30'
    : 'border-red-400/40 bg-red-950/20 hover:bg-red-950/30'
}

function TaskTree({
  item,
  depth,
  inheritedChecked = false,
}: {
  item: TaskChecklistItem
  depth: number
  inheritedChecked?: boolean
}) {
  const children = item.children || []

  // If a child item doesn't have an explicit checkbox state in the markdown,
  // inherit the parent completion state to avoid confusion in the UI.
  const hasExplicitChecked = typeof item.checked === 'boolean'
  const checked = hasExplicitChecked ? Boolean(item.checked) : inheritedChecked

  return (
    <div className="space-y-1">
      <div className="flex items-start gap-2" style={{ paddingLeft: `${depth * 14}px` }}>
        <span
          className={
            "mt-0.5 inline-flex h-4 w-4 items-center justify-center rounded border text-[10px] " +
            (checked
              ? 'bg-emerald-500/20 border-emerald-400/40 text-emerald-200'
              : 'bg-white/5 border-white/10 text-gray-400')
          }
          aria-label={checked ? 'checked' : 'unchecked'}
        >
          {checked ? '✓' : ''}
        </span>
        <div className="min-w-0">
          <div className="text-sm text-gray-200 break-words leading-snug">
            {item.title ? <span className="font-semibold">{item.title}: </span> : null}
            <span className={checked ? 'line-through opacity-80' : ''}>{item.text}</span>
          </div>
          {item.code ? <div className="text-[11px] text-gray-500 font-mono">{item.code}</div> : null}
        </div>
      </div>

      {children.length ? (
        <div className="space-y-1">
          {children.map((ch, idx) => (
            <TaskTree
              key={`${ch.text}-${idx}`}
              item={ch}
              depth={depth + 1}
              inheritedChecked={checked}
            />
          ))}
        </div>
      ) : null}
    </div>
  )
}

export default function KanbanPage() {
  const qc = useQueryClient()
  const [selected, setSelected] = useState<CoordinationChangeItem | null>(null)
  const [activeMobileColumn, setActiveMobileColumn] = useState<(typeof COLUMNS_ORDER)[number]>('Pending')
  const [moveTarget, setMoveTarget] = useState<CoordinationChangeItem | null>(null)
  const [dragTargetColumn, setDragTargetColumn] = useState<string | null>(null)
  const touchStartX = useRef<number | null>(null)
  const touchDeltaX = useRef(0)
  const longPressTimerRef = useRef<number | null>(null)
  const cardTouchStartRef = useRef<{ x: number; y: number } | null>(null)
  const suppressNextCardClickRef = useRef<string | null>(null)
  const mobileColumnInitializedRef = useRef(false)

  useEffect(() => {
    const prev = document.body.style.overflow
    if (selected || moveTarget) document.body.style.overflow = "hidden"
    return () => {
      document.body.style.overflow = prev
    }
  }, [selected, moveTarget])

  useEffect(() => {
    setEditTitle(selected?.title || '')
    setEditDescription(selected?.description || '')
  }, [selected])

  useEffect(() => {
    return () => {
      if (longPressTimerRef.current != null) {
        window.clearTimeout(longPressTimerRef.current)
      }
    }
  }, [])

  const { data, isLoading, error } = useQuery({
    queryKey: ['kanban', 'changes'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/workflow/kanban/changes?project_slug=crypto`)
      if (!res.ok) throw new Error(`Failed to load changes (${res.status})`)
      return (await res.json()) as CoordinationChangeListResponse
    },
    refetchOnWindowFocus: false,
  })

  type FilterMode = 'all' | 'active' | 'archived'
  type SortMode = 'column' | 'title' | 'id'

  const items = data?.items || []

  // Local search ("Localizar"): filters cards by id/title.
  const [query, setQuery] = useState('')
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false)

  // Mobile toolbar controls (match prototype intent).
  const [filterMode, setFilterMode] = useState<FilterMode>('all')
  const [sortMode, setSortMode] = useState<SortMode>('column')

  const filteredItems = useMemo(() => {
    const q = query.trim().toLowerCase()

    let out = items

    if (filterMode !== 'all') {
      out = out.filter((it) => (filterMode === 'archived' ? it.archived : !it.archived))
    }

    if (q) {
      out = out.filter((it) => {
        const hay = `${it.id} ${it.title || ''}`.toLowerCase()
        return hay.includes(q)
      })
    }

    const sourceIndex = new Map(items.map((item, index) => [item.id, index]))
    const colIdx = (col: string) => {
      const i = COLUMNS_ORDER.indexOf(col as (typeof COLUMNS_ORDER)[number])
      return i === -1 ? 999 : i
    }

    out = [...out].sort((a, b) => {
      if (sortMode === 'title') {
        const at = (a.title || a.id).toLowerCase()
        const bt = (b.title || b.id).toLowerCase()
        return at.localeCompare(bt)
      }
      if (sortMode === 'id') return a.id.localeCompare(b.id)

      const dc = colIdx(a.column) - colIdx(b.column)
      if (dc !== 0) return dc
      const dp = (a.position ?? 0) - (b.position ?? 0)
      if (dp !== 0) return dp
      return (sourceIndex.get(a.id) ?? 0) - (sourceIndex.get(b.id) ?? 0)
    })

    return out
  }, [items, query, filterMode, sortMode])

  const byColumn = useMemo(() => {
    const map = new Map<string, CoordinationChangeItem[]>()
    for (const c of COLUMNS_ORDER) map.set(c, [])

    for (const it of filteredItems) {
      const col = map.has(it.column) ? it.column : 'DEV'
      map.get(col)!.push(it)
    }

    return map
  }, [filteredItems])

  const canReorder = (item: CoordinationChangeItem, direction: 'up' | 'down') => {
    const columnItems = byColumn.get(item.column) || []
    const index = columnItems.findIndex((candidate) => candidate.id === item.id)
    if (index === -1) return false
    return direction === 'up' ? index > 0 : index < columnItems.length - 1
  }

  useEffect(() => {
    if (mobileColumnInitializedRef.current) return
    const firstNonEmpty = COLUMNS_ORDER.find((col) => (byColumn.get(col)?.length || 0) > 0)
    if (firstNonEmpty) {
      setActiveMobileColumn(firstNonEmpty)
    }
    mobileColumnInitializedRef.current = true
  }, [byColumn])

  const activeMobileIndex = COLUMNS_ORDER.indexOf(activeMobileColumn)

  const moveMobileStage = (direction: -1 | 1) => {
    const next = Math.max(0, Math.min(COLUMNS_ORDER.length - 1, activeMobileIndex + direction))
    setActiveMobileColumn(COLUMNS_ORDER[next])
  }

  const handleDesktopDragStart = (event: DragEvent, item: CoordinationChangeItem) => {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData(DESKTOP_DRAG_MIME, item.id)
    event.dataTransfer.setData('text/plain', item.id)
  }

  const handleDesktopDragOver = (event: DragEvent, column: string) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
    setDragTargetColumn(column)
  }

  const handleDesktopDrop = (event: DragEvent, column: string) => {
    event.preventDefault()
    event.stopPropagation()
    setDragTargetColumn(null)
    const changeId = event.dataTransfer.getData(DESKTOP_DRAG_MIME) || event.dataTransfer.getData('text/plain')
    if (!changeId) return
    const item = items.find((candidate) => candidate.id === changeId)
    if (!item || item.column === column) return
    moveChange.mutate({ changeId, status: column })
  }

  const handleDesktopDragEnd = () => {
    setDragTargetColumn(null)
  }

  const handleBoardTouchStart = (clientX: number) => {
    touchStartX.current = clientX
    touchDeltaX.current = 0
  }

  const handleBoardTouchMove = (clientX: number) => {
    if (touchStartX.current == null) return
    touchDeltaX.current = clientX - touchStartX.current
  }

  const clearLongPressTimer = () => {
    if (longPressTimerRef.current != null) {
      window.clearTimeout(longPressTimerRef.current)
      longPressTimerRef.current = null
    }
  }

  const handleBoardTouchEnd = () => {
    if (touchStartX.current == null) return
    if (Math.abs(touchDeltaX.current) >= MOBILE_SWIPE_THRESHOLD) {
      moveMobileStage(touchDeltaX.current > 0 ? -1 : 1)
    }
    touchStartX.current = null
    touchDeltaX.current = 0
  }

  const startCardLongPress = (it: CoordinationChangeItem, clientX: number, clientY: number) => {
    clearLongPressTimer()
    cardTouchStartRef.current = { x: clientX, y: clientY }
    longPressTimerRef.current = window.setTimeout(() => {
      suppressNextCardClickRef.current = it.id
      setMoveTarget(it)
      longPressTimerRef.current = null
      cardTouchStartRef.current = null
    }, MOBILE_LONG_PRESS_MS)
  }

  const handleCardTouchMove = (clientX: number, clientY: number) => {
    const start = cardTouchStartRef.current
    if (!start) return
    const deltaX = clientX - start.x
    const deltaY = clientY - start.y
    if (Math.hypot(deltaX, deltaY) > MOBILE_LONG_PRESS_MOVE_TOLERANCE) {
      clearLongPressTimer()
      cardTouchStartRef.current = null
    }
  }

  const cancelCardLongPress = () => {
    clearLongPressTimer()
    cardTouchStartRef.current = null
  }

  const handleCardClick = (it: CoordinationChangeItem) => {
    if (suppressNextCardClickRef.current === it.id) {
      suppressNextCardClickRef.current = null
      return
    }
    setSelected(it)
  }

  const tasksQuery = useQuery({
    queryKey: ['workflow', 'kanban', 'change', selected?.id, 'tasks'],
    enabled: Boolean(selected?.id),
    queryFn: async () => {
      const changeId = encodeURIComponent(selected!.id)
      const res = await fetch(
        `${API_BASE_URL}/workflow/kanban/changes/${changeId}/tasks?project_slug=crypto`
      )
      if (!res.ok) throw new Error(`Failed to load tasks (${res.status})`)
      return (await res.json()) as ChangeTasksChecklistResponse
    },
    refetchOnWindowFocus: false,
  })

  const commentsQuery = useQuery({
    queryKey: ['workflow', 'kanban', 'change', selected?.id, 'comments'],
    enabled: Boolean(selected?.id),
    queryFn: async () => {
      const changeId = encodeURIComponent(selected!.id)
      const url = `${API_BASE_URL}/workflow/kanban/changes/${changeId}/comments?project_slug=crypto`
      const res = await fetch(url)
      if (!res.ok) throw new Error(`Failed to load comments (${res.status})`)
      return (await res.json()) as CoordinationCommentsListResponse
    },
    refetchOnWindowFocus: false,
  })

  const moveChange = useMutation({
    mutationFn: async ({ changeId, status }: { changeId: string; status: string }) => {
      const res = await fetch(`${API_BASE_URL}/workflow/projects/crypto/changes/${encodeURIComponent(changeId)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      })
      if (!res.ok) {
        let message = ''
        try {
          const payload = await res.json()
          const detail = payload?.detail
          if (typeof detail === 'string') {
            message = detail
          } else if (detail && typeof detail === 'object') {
            const base = typeof detail.message === 'string' ? detail.message : ''
            const allowed = Array.isArray(detail.allowed_targets) && detail.allowed_targets.length
              ? ` Allowed: ${detail.allowed_targets.join(', ')}.`
              : ''
            message = `${base}${allowed}`.trim()
          }
        } catch {
          message = await res.text().catch(() => '')
        }
        throw new Error(`Failed to move card (${res.status})${message ? `: ${message}` : ''}`)
      }
      return (await res.json()) as ChangeUpdateResponse
    },
    onSuccess: async (_data, vars) => {
      setMoveTarget((curr) => (curr?.id === vars.changeId ? null : curr))
      setActiveMobileColumn(vars.status as (typeof COLUMNS_ORDER)[number])
      await qc.invalidateQueries({ queryKey: ['kanban', 'changes'] })
      await qc.invalidateQueries({ queryKey: ['workflow', 'kanban', 'change', vars.changeId, 'tasks'] })
      await qc.invalidateQueries({ queryKey: ['workflow', 'kanban', 'change', vars.changeId, 'comments'] })
    },
  })

  const reorderChange = useMutation({
    mutationFn: async ({ changeId, direction }: { changeId: string; direction: 'up' | 'down' }) => {
      const res = await fetch(`${API_BASE_URL}/workflow/projects/crypto/changes/${encodeURIComponent(changeId)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reorder: direction }),
      })
      if (!res.ok) {
        const txt = await res.text().catch(() => '')
        throw new Error(`Failed to reorder card (${res.status})${txt ? `: ${txt}` : ''}`)
      }
      return (await res.json()) as ChangeUpdateResponse
    },
    onSuccess: async (_data, vars) => {
      await qc.invalidateQueries({ queryKey: ['kanban', 'changes'] })
      await qc.invalidateQueries({ queryKey: ['workflow', 'kanban', 'change', vars.changeId, 'tasks'] })
      await qc.invalidateQueries({ queryKey: ['workflow', 'kanban', 'change', vars.changeId, 'comments'] })
    },
  })

  const [author, setAuthor] = useState(() => localStorage.getItem('kanban.commentAuthor') || 'User')
  const [body, setBody] = useState('')
  const [newTitle, setNewTitle] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [editTitle, setEditTitle] = useState('')
  const [editDescription, setEditDescription] = useState('')

  const createChange = useMutation({
    mutationFn: async () => {
      const title = newTitle.trim()
      const description = newDescription.trim()
      if (!title) throw new Error('Title is required')

      const res = await fetch(`${API_BASE_URL}/workflow/kanban/changes?project_slug=crypto`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description }),
      })

      if (!res.ok) {
        const txt = await res.text().catch(() => '')
        throw new Error(`Failed to create card (${res.status})${txt ? `: ${txt}` : ''}`)
      }

      return (await res.json()) as { item: CoordinationChangeItem }
    },
    onSuccess: async (data) => {
      setNewTitle('')
      setNewDescription('')
      setSelected(data.item)
      setEditTitle(data.item.title || '')
      setEditDescription(data.item.description || '')
      setActiveMobileColumn('Pending')
      await qc.invalidateQueries({ queryKey: ['kanban', 'changes'] })
      await qc.invalidateQueries({ queryKey: ['workflow', 'kanban', 'change', data.item.id, 'tasks'] })
      await qc.invalidateQueries({ queryKey: ['workflow', 'kanban', 'change', data.item.id, 'comments'] })
    },
  })

  const updateSelectedChange = useMutation({
    mutationFn: async ({
      changeId,
      payload,
    }: {
      changeId: string
      payload: { title?: string; description?: string; status?: string; cancel_archive?: boolean }
    }) => {
      const res = await fetch(`${API_BASE_URL}/workflow/projects/crypto/changes/${encodeURIComponent(changeId)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        let message = ''
        try {
          const body = await res.json()
          message = typeof body?.detail === 'string' ? body.detail : JSON.stringify(body?.detail || body)
        } catch {
          message = await res.text().catch(() => '')
        }
        throw new Error(`Failed to update card (${res.status})${message ? `: ${message}` : ''}`)
      }
      return (await res.json()) as ChangeUpdateResponse
    },
    onSuccess: async (data, vars) => {
      const updated: CoordinationChangeItem = {
        id: data.change_id,
        title: data.title,
        description: data.description,
        card_number: data.card_number ?? selected?.card_number ?? null,
        path: selected?.path || `openspec/changes/${data.change_id}/proposal`,
        status: selected?.status || {},
        archived: data.status === 'Archived',
        column: data.status as CoordinationChangeItem['column'],
      }
      setSelected(updated)
      setEditTitle(data.title || '')
      setEditDescription(data.description || '')
      if (data.status === 'Archived') setActiveMobileColumn('Archived')
      await qc.invalidateQueries({ queryKey: ['kanban', 'changes'] })
      await qc.invalidateQueries({ queryKey: ['workflow', 'kanban', 'change', vars.changeId, 'tasks'] })
      await qc.invalidateQueries({ queryKey: ['workflow', 'kanban', 'change', vars.changeId, 'comments'] })
    },
  })

  const createComment = useMutation({
    mutationFn: async () => {
      if (!selected?.id) throw new Error('No change selected')
      const a = author.trim()
      const b = body.trimEnd()
      if (!a) throw new Error('Author is required')
      if (!b) throw new Error('Body is required')
      if (b.length > 2000) throw new Error('Body too long (max 2000 chars)')

      const changeId = encodeURIComponent(selected.id)
      const url = `${API_BASE_URL}/workflow/kanban/changes/${changeId}/comments?project_slug=crypto`

      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author: a, body: b }),
      })

      if (!res.ok) {
        const txt = await res.text().catch(() => '')
        throw new Error(`Failed to post comment (${res.status})${txt ? `: ${txt}` : ''}`)
      }

      return (await res.json()) as { item: CoordinationCommentItem }
    },
    onSuccess: async () => {
      localStorage.setItem('kanban.commentAuthor', author.trim())
      setBody('')
      await qc.invalidateQueries({ queryKey: ['workflow', 'kanban', 'change', selected?.id, 'comments'] })
    },
  })

  return (
    <main className="mx-auto px-0 py-0 sm:container sm:px-6 sm:py-10">
      {/* Mobile-only topbar (match approved prototype layout; keep desktop unchanged) */}
      <header className="sm:hidden sticky top-0 z-40 border-b border-white/10 bg-zinc-950/70 backdrop-blur">
        <div className="h-14 px-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs text-gray-300">
            <a href="/" className="opacity-80 hover:opacity-100">
              Home
            </a>
            <span className="opacity-40">/</span>
            <span className="font-semibold text-gray-100">Kanban</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              className="h-10 w-10 rounded-xl border border-white/10 bg-white/5 grid place-items-center"
              aria-label="Search"
              onClick={() => setMobileSearchOpen((v) => !v)}
            >
              <Search className="w-4 h-4 text-gray-200" />
            </button>
            <Button
              type="button"
              onClick={() => createChange.mutate()}
              disabled={createChange.isPending || !newTitle.trim()}
              className="h-10 px-3 rounded-xl"
              aria-label="Create new card"
            >
              {createChange.isPending ? 'Creating…' : 'New'}
            </Button>
          </div>
        </div>
      </header>

      {/* Mobile-only search row (toggle from topbar). */}
      <div className="sm:hidden border-b border-white/10 bg-zinc-950/70 backdrop-blur">
        <div className="px-4 py-3 space-y-2">
          <Input value={newTitle} onChange={(e) => setNewTitle(e.target.value)} placeholder="Novo card / backlog item" />
          <textarea
            className="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-white/20"
            rows={3}
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            maxLength={2000}
            placeholder="Descrição opcional"
          />
          {createChange.error ? (
            <div className="text-xs text-red-400">
              {createChange.error instanceof Error ? createChange.error.message : 'Falha ao criar card'}
            </div>
          ) : null}
        </div>
      </div>
      {mobileSearchOpen ? (
        <div className="sm:hidden border-b border-white/10 bg-zinc-950/70 backdrop-blur">
          <div className="px-4 py-3 flex items-center gap-2">
            <div className="flex-1">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Localizar…"
                autoFocus
              />
            </div>
            <Button
              variant="ghost"
              onClick={() => {
                setQuery('')
                setMobileSearchOpen(false)
              }}
              aria-label="Close search"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>
      ) : null}

      <div className="px-4 py-3 sm:px-0 sm:py-0 sm:mb-6">
        <div className="rounded-2xl border border-white/10 bg-zinc-950/60 p-4 sm:p-5">
          <div className="sm:flex sm:items-start sm:justify-between sm:gap-6">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Kanban className="w-5 h-5" /> Kanban
              </h1>
              <p className="text-sm text-gray-400">
                Pending entra antes de PO. Desktop arrasta entre colunas; mobile mantém swipe + long press.
              </p>
            </div>
            <div className="mt-4 sm:mt-0 sm:w-[360px] space-y-2">
              <Input value={newTitle} onChange={(e) => setNewTitle(e.target.value)} placeholder="Novo card / backlog item" />
              <textarea
                className="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-white/20"
                rows={3}
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                maxLength={2000}
                placeholder="Descrição opcional"
              />
              <div className="flex items-center justify-between gap-3">
                <div className="text-xs text-gray-500">Cria direto em Pending.</div>
                <Button onClick={() => createChange.mutate()} disabled={createChange.isPending || !newTitle.trim()}>
                  {createChange.isPending ? 'Criando…' : 'Criar card'}
                </Button>
              </div>
              {createChange.error ? (
                <div className="text-xs text-red-400">
                  {createChange.error instanceof Error ? createChange.error.message : 'Falha ao criar card'}
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </div>

      <div className="px-4 py-4 sm:px-0 sm:py-0">
        <div className="sm:hidden sticky top-14 z-30 -mx-4 mb-3 border-b border-white/10 bg-zinc-950/85 backdrop-blur">
          <div className="px-4 py-3">
            <div className="text-lg font-semibold text-white">Opportunity Board</div>
            <div className="text-xs text-gray-400">Uma etapa por vez · swipe + tabs</div>
          </div>

          <div className="px-4 pb-3 flex gap-2 overflow-x-auto">
            <select
              className="h-10 min-w-[110px] rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-gray-100"
              value={filterMode}
              onChange={(e) => setFilterMode(e.target.value as FilterMode)}
              aria-label="Filter"
            >
              <option value="all">All</option>
              <option value="active">Active</option>
              <option value="archived">Archived</option>
            </select>

            <select
              className="h-10 min-w-[110px] rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-gray-100"
              value={sortMode}
              onChange={(e) => setSortMode(e.target.value as SortMode)}
              aria-label="Sort"
            >
              <option value="column">Priority</option>
              <option value="title">Title</option>
              <option value="id">ID</option>
            </select>

            <div className="h-10 shrink-0 rounded-xl border border-white/10 bg-white/5 px-3 grid place-items-center text-xs text-gray-300">
              {filteredItems.length} items
            </div>
          </div>

          <div className="px-4 pb-2 overflow-x-auto">
            <div className="flex gap-2 min-w-max" role="tablist" aria-label="Workflow stages">
              {COLUMNS_ORDER.map((col) => {
                const count = byColumn.get(col)?.length || 0
                const active = activeMobileColumn === col
                return (
                  <button
                    key={col}
                    type="button"
                    role="tab"
                    aria-selected={active}
                    onClick={() => setActiveMobileColumn(col)}
                    className={
                      'h-11 rounded-2xl px-4 text-sm font-semibold border transition-colors ' +
                      (active
                        ? 'border-cyan-400/40 bg-cyan-400/15 text-white'
                        : 'border-white/10 bg-white/5 text-gray-300')
                    }
                  >
                    {col} <span className="ml-1 text-xs text-gray-400">{count}</span>
                  </button>
                )
              })}
            </div>
            <div className="mt-2 text-[11px] text-gray-400">Swipe para trocar de etapa</div>
          </div>
        </div>

        <Card className="hidden sm:block border border-white/10 glass">
          <CardHeader>
            <div className="text-sm text-gray-300">Board</div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-gray-400 text-sm">Carregando…</div>
            ) : error ? (
              <div className="text-red-400 text-sm">Erro: {error instanceof Error ? error.message : 'falha ao carregar'}</div>
            ) : (
              <div className="overflow-x-auto">
                <div className="flex items-start gap-4 min-w-max pb-2">
                  {COLUMNS_ORDER.map((col) => {
                    const colItems = byColumn.get(col) || []
                    return (
                      <section
                        key={col}
                        className={
                          'w-[320px] shrink-0 rounded-xl border bg-zinc-900/40 transition-colors ' +
                          (dragTargetColumn === col ? 'border-cyan-400/50' : 'border-white/10')
                        }
                        onDragOver={(event) => handleDesktopDragOver(event, col)}
                        onDrop={(event) => handleDesktopDrop(event, col)}
                        onDragLeave={() => setDragTargetColumn((curr) => (curr === col ? null : curr))}
                      >
                        <div className="px-4 py-3 border-b border-white/10">
                          <div className="flex items-center justify-between gap-3">
                            <div className="font-semibold text-sm text-white">{col}</div>
                            <div className="text-xs text-gray-400">{colItems.length}</div>
                          </div>
                        </div>

                        <div className="p-3 space-y-3 min-h-[220px]">
                          {colItems.length === 0 ? (
                            <div className="rounded-lg border border-dashed border-white/10 p-4 text-xs text-gray-500">vazio</div>
                          ) : (
                            colItems.map((it) => (
                              <div
                                key={it.id}
                                draggable={!it.archived && !moveChange.isPending}
                                onDragStart={(event) => handleDesktopDragStart(event, it)}
                                onDragEnd={handleDesktopDragEnd}
                                onDragOver={(event) => handleDesktopDragOver(event, col)}
                                onDrop={(event) => handleDesktopDrop(event, col)}
                                onClick={() => setSelected(it)}
                                onKeyDown={(event) => {
                                  if (event.key === 'Enter' || event.key === ' ') {
                                    event.preventDefault()
                                    setSelected(it)
                                  }
                                }}
                                className={
                                  'w-full text-left rounded-xl border border-white/10 bg-zinc-950/40 hover:bg-zinc-950/30 shadow-sm transition-colors p-3 focus:outline-none focus:ring-2 focus:ring-white/20 cursor-pointer ' +
                                  (selected?.id === it.id ? 'ring-2 ring-white/20' : '') +
                                  ' ' + getBugCardClass(selected?.id === it.id, it.has_bugs)
                                }
                                aria-label={`Open details for ${it.id}`}
                                role="button"
                                tabIndex={0}
                              >
                                <div className="flex items-start justify-between gap-3">
                                  <div className="min-w-0">
                                    {it.card_number ? <div className="text-[11px] font-semibold text-cyan-300">#{it.card_number}</div> : null}
                                    <div className="text-sm font-semibold text-white truncate">{it.title || it.id}</div>
                                    <div className="text-[11px] text-gray-400 font-mono truncate">{it.id}</div>
                                  </div>
                                  {it.archived ? (
                                    <div className="text-[10px] px-2 py-0.5 rounded-full border border-white/10 text-gray-300">archived</div>
                                  ) : null}
                                </div>

                                {it.description ? (
                                  <div className="mt-2 text-xs text-gray-300 break-words">{it.description}</div>
                                ) : null}

                                <div className="mt-2 pt-2 border-t border-white/10 space-y-1">
                                  <StatusLine label="PO" value={it.status?.['PO']} />
                                  <StatusLine label="DESIGN" value={it.status?.['DESIGN'] || 'skipped'} />
                                  <StatusLine label="Alan approval" value={it.status?.['Alan approval'] || it.status?.['Alan (Stakeholder)']} />
                                  <StatusLine label="DEV" value={it.status?.['DEV']} />
                                  <StatusLine label="QA" value={it.status?.['QA']} />
                                  <StatusLine label="Publish" value={it.status?.['Publish']} />
                                  <StatusLine label="Ready for homologation" value={it.status?.['Homologation readiness']} />
                                  <StatusLine label="Alan homologation" value={it.status?.['Alan homologation'] || it.status?.['Alan (Stakeholder)']} />
                                </div>

                                {!it.archived ? (
                                  <div className="mt-3 flex items-center gap-2">
                                    <button
                                      type="button"
                                      onClick={(event) => {
                                        event.stopPropagation()
                                        reorderChange.mutate({ changeId: it.id, direction: 'up' })
                                      }}
                                      disabled={!canReorder(it, 'up') || reorderChange.isPending || moveChange.isPending}
                                      className="rounded-lg border border-white/10 px-2 py-1 text-[11px] text-gray-200 disabled:opacity-40"
                                    >
                                      Move up
                                    </button>
                                    <button
                                      type="button"
                                      onClick={(event) => {
                                        event.stopPropagation()
                                        reorderChange.mutate({ changeId: it.id, direction: 'down' })
                                      }}
                                      disabled={!canReorder(it, 'down') || reorderChange.isPending || moveChange.isPending}
                                      className="rounded-lg border border-white/10 px-2 py-1 text-[11px] text-gray-200 disabled:opacity-40"
                                    >
                                      Move down
                                    </button>
                                  </div>
                                ) : null}
                              </div>
                            ))
                          )}
                        </div>
                      </section>
                    )
                  })}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="sm:hidden">
          {isLoading ? (
            <div className="text-gray-400 text-sm">Carregando…</div>
          ) : error ? (
            <div className="text-red-400 text-sm">Erro: {error instanceof Error ? error.message : 'falha ao carregar'}</div>
          ) : (
            <section
              className="rounded-2xl border border-white/10 bg-zinc-900/40 overflow-hidden"
              onTouchStart={(e) => handleBoardTouchStart(e.touches[0]?.clientX ?? 0)}
              onTouchMove={(e) => handleBoardTouchMove(e.touches[0]?.clientX ?? 0)}
              onTouchEnd={handleBoardTouchEnd}
            >
              <div className="px-4 py-3 border-b border-white/10 bg-zinc-950/70">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-xs text-gray-400">Current stage</div>
                    <div className="font-semibold text-white">{activeMobileColumn}</div>
                  </div>
                  <div className="text-sm text-gray-300">{(byColumn.get(activeMobileColumn)?.length || 0)} cards</div>
                </div>
              </div>

              <div className="p-3 space-y-3 min-h-[50vh]">
                {(byColumn.get(activeMobileColumn)?.length || 0) === 0 ? (
                  <div className="rounded-xl border border-dashed border-white/10 p-5 text-sm text-gray-500">Nenhum card nesta etapa.</div>
                ) : (
                  (byColumn.get(activeMobileColumn) || []).map((it) => (
                    <button
                      type="button"
                      key={it.id}
                      onClick={() => handleCardClick(it)}
                      onTouchStart={(e) => {
                        const touch = e.touches[0]
                        startCardLongPress(it, touch?.clientX ?? 0, touch?.clientY ?? 0)
                      }}
                      onTouchEnd={cancelCardLongPress}
                      onTouchCancel={cancelCardLongPress}
                      onTouchMove={(e) => {
                        const touch = e.touches[0]
                        handleCardTouchMove(touch?.clientX ?? 0, touch?.clientY ?? 0)
                      }}
                      className={"w-full text-left rounded-2xl border border-white/10 bg-zinc-950/60 p-4 shadow-sm " + getBugCardClass(false, it.has_bugs)}
                      aria-label={`Open details for ${it.id}`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5 h-14 w-1.5 shrink-0 rounded-full bg-gradient-to-b from-cyan-400 to-emerald-400" />
                        <div className="min-w-0 flex-1">
                          <div className="flex items-start justify-between gap-3">
                            <div>
                              <div className="flex flex-wrap items-center gap-2 text-[11px]">
                                {it.card_number ? <span className="font-semibold text-cyan-300">#{it.card_number}</span> : null}
                                <span className="font-mono text-gray-400">{it.id}</span>
                              </div>
                              <div className="mt-1 text-base font-semibold leading-tight text-white">{it.title || it.id}</div>
                            </div>
                            {it.archived ? <div className="rounded-full border border-white/10 px-2 py-1 text-[10px] text-gray-300">archived</div> : null}
                          </div>

                          <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
                            <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2 py-1 text-cyan-100">{activeMobileColumn}</span>
                            <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-gray-300">PO {it.status?.['PO'] || '—'}</span>
                            <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-gray-300">DEV {it.status?.['DEV'] || '—'}</span>
                            <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-gray-300">QA {it.status?.['QA'] || '—'}</span>
                            <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-gray-300">Publish {it.status?.['Publish'] || '—'}</span>
                          </div>

                          <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-gray-400">
                            <div className="rounded-xl border border-white/10 bg-black/20 px-3 py-2">Alan approval · {(it.status?.['Alan approval'] || it.status?.['Alan (Stakeholder)'] || '—')}</div>
                            <div className="rounded-xl border border-white/10 bg-black/20 px-3 py-2">Ready for homologation · {(it.status?.['Homologation readiness'] || '—')}</div>
                          </div>

                          <div className="mt-3 flex items-center gap-2">
                            <button
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation()
                                reorderChange.mutate({ changeId: it.id, direction: 'up' })
                              }}
                              disabled={!canReorder(it, 'up') || reorderChange.isPending || moveChange.isPending}
                              className="rounded-lg border border-white/10 px-2 py-1 text-[11px] text-gray-200 disabled:opacity-40"
                            >
                              Move up
                            </button>
                            <button
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation()
                                reorderChange.mutate({ changeId: it.id, direction: 'down' })
                              }}
                              disabled={!canReorder(it, 'down') || reorderChange.isPending || moveChange.isPending}
                              className="rounded-lg border border-white/10 px-2 py-1 text-[11px] text-gray-200 disabled:opacity-40"
                            >
                              Move down
                            </button>
                          </div>

                          <div className="mt-3 text-[11px] text-amber-200/80">Pressione e segure para mover de etapa</div>
                        </div>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </section>
          )}
        </div>
      </div>

      {moveTarget ? (
        <div className="fixed inset-0 z-50 sm:hidden">
          <div className="absolute inset-0 bg-black/70" onClick={() => setMoveTarget(null)} aria-hidden="true" />
          <aside className="absolute inset-x-0 bottom-0 rounded-t-3xl border-t border-white/10 bg-zinc-950 shadow-2xl">
            <div className="px-4 py-4 border-b border-white/10">
              <div className="text-xs text-gray-400">Mover card</div>
              <div className="mt-1 flex flex-wrap items-center gap-2 text-base font-semibold text-white">
                {moveTarget.card_number ? <span className="text-cyan-300">#{moveTarget.card_number}</span> : null}
                <span>{moveTarget.title || moveTarget.id}</span>
              </div>
              <div className="text-[11px] font-mono text-gray-500">{moveTarget.id}</div>
            </div>

            <div className="p-4 space-y-3 max-h-[70vh] overflow-y-auto">
              <div className="text-xs text-gray-400">Escolha a nova etapa no fluxo</div>
              <div className="grid grid-cols-1 gap-2">
                {COLUMNS_ORDER.map((col) => {
                  const active = moveTarget.column === col
                  return (
                    <button
                      key={col}
                      type="button"
                      disabled={active || moveChange.isPending}
                      onClick={() => moveChange.mutate({ changeId: moveTarget.id, status: col })}
                      className={
                        'rounded-2xl border px-4 py-3 text-left text-sm font-semibold transition-colors ' +
                        (active
                          ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-100'
                          : 'border-white/10 bg-white/5 text-gray-100 disabled:opacity-60')
                      }
                    >
                      <div className="flex items-center justify-between gap-3">
                        <span>{col}</span>
                        <span className="text-[11px] text-gray-400">{active ? 'Atual' : 'Mover'}</span>
                      </div>
                    </button>
                  )
                })}
              </div>

              {moveChange.error ? (
                <div className="text-xs text-red-400">
                  {moveChange.error instanceof Error ? moveChange.error.message : 'Falha ao mover card'}
                </div>
              ) : null}

              <div className="flex justify-end">
                <Button variant="ghost" onClick={() => setMoveTarget(null)} disabled={moveChange.isPending}>
                  Fechar
                </Button>
              </div>
            </div>
          </aside>
        </div>
      ) : null}

      {selected ? (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/70" onClick={() => setSelected(null)} aria-hidden="true" />
          <aside className="absolute inset-0 h-full w-full bg-zinc-950 border-t border-white/10 shadow-2xl sm:rounded-none sm:inset-y-0 sm:left-auto sm:right-0 sm:w-[520px] sm:border-t-0 sm:border-l sm:border-white/10">
            <div className="h-full flex flex-col">
              <div className="px-4 py-3 border-b border-white/10 flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="text-sm text-gray-400">Detalhes</div>
                  <div className="flex flex-wrap items-center gap-2 text-lg font-semibold text-white truncate">
                    {selected.card_number ? <span className="text-cyan-300">#{selected.card_number}</span> : null}
                    <span className="truncate">{selected.title || selected.id}</span>
                  </div>
                  <div className="text-[11px] text-gray-500 font-mono truncate">{selected.id}</div>
                </div>
                <Button variant="ghost" onClick={() => setSelected(null)} aria-label="Close panel">
                  <X className="w-4 h-4" />
                </Button>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-6">
                <section className="space-y-3">
                  <div className="text-sm font-semibold text-white">Card</div>

                  {!selected.archived ? (
                    <div className="flex flex-wrap items-center gap-2">
                      <Button
                        variant="secondary"
                        onClick={() => reorderChange.mutate({ changeId: selected.id, direction: 'up' })}
                        disabled={!canReorder(selected, 'up') || reorderChange.isPending || moveChange.isPending}
                      >
                        Move up
                      </Button>
                      <Button
                        variant="secondary"
                        onClick={() => reorderChange.mutate({ changeId: selected.id, direction: 'down' })}
                        disabled={!canReorder(selected, 'down') || reorderChange.isPending || moveChange.isPending}
                      >
                        Move down
                      </Button>
                    </div>
                  ) : null}

                  <div className="rounded-xl border border-white/10 bg-white/5 p-3 space-y-3">
                    <div>
                      <div className="text-[11px] text-gray-400 mb-1">Título</div>
                      <Input
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        maxLength={256}
                        placeholder="Título do card"
                      />
                    </div>

                    <div>
                      <div className="text-[11px] text-gray-400 mb-1">Descrição</div>
                      <textarea
                        className="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-white/20"
                        rows={4}
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        maxLength={2000}
                        placeholder="Descrição do card"
                      />
                    </div>

                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="text-xs text-gray-500">Editar metadados preserva id, comments e gates.</div>
                      <div className="flex flex-wrap items-center gap-2">
                        <Button
                          variant="secondary"
                          onClick={() => {
                            setEditTitle(selected.title || '')
                            setEditDescription(selected.description || '')
                          }}
                          disabled={updateSelectedChange.isPending}
                        >
                          Reverter
                        </Button>
                        <Button
                          onClick={() => updateSelectedChange.mutate({
                            changeId: selected.id,
                            payload: { title: editTitle.trim(), description: editDescription.trim() },
                          })}
                          disabled={updateSelectedChange.isPending || !editTitle.trim()}
                        >
                          {updateSelectedChange.isPending ? 'Salvando…' : 'Salvar'}
                        </Button>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-3">
                      <div>
                        <div className="text-sm font-medium text-red-300">Cancelar card</div>
                        <div className="text-xs text-gray-500">Retira do fluxo ativo sem apagar histórico.</div>
                      </div>
                      <Button
                        variant="secondary"
                        className="border border-red-500/40 bg-red-500/10 text-red-100 hover:bg-red-500/20"
                        onClick={() => {
                          if (!window.confirm(`Cancelar o card ${selected.id}? O histórico será preservado.`)) return
                          updateSelectedChange.mutate({
                            changeId: selected.id,
                            payload: { status: 'Archived', cancel_archive: true },
                          })
                        }}
                        disabled={updateSelectedChange.isPending || selected.column === 'Archived'}
                      >
                        {selected.column === 'Archived' ? 'Já cancelado' : 'Cancelar card'}
                      </Button>
                    </div>

                    {updateSelectedChange.error ? (
                      <div className="text-xs text-red-400">
                        {updateSelectedChange.error instanceof Error ? updateSelectedChange.error.message : 'Falha ao atualizar card'}
                      </div>
                    ) : null}
                  </div>
                </section>

                <section className="space-y-2">
                  <div className="text-sm font-semibold text-white">Tasks</div>
                  {tasksQuery.isLoading ? (
                    <div className="text-sm text-gray-400">Carregando tasks…</div>
                  ) : tasksQuery.error ? (
                    <div className="text-sm text-red-400">
                      Erro: {tasksQuery.error instanceof Error ? tasksQuery.error.message : 'falha ao carregar'}
                    </div>
                  ) : tasksQuery.data ? (
                    <div className="space-y-4">
                      {tasksQuery.data.sections.length === 0 ? (
                        <div className="text-xs text-gray-500">(sem checklist)</div>
                      ) : (
                        tasksQuery.data.sections.map((sec) => (
                          <div key={sec.title} className="rounded-xl border border-white/10 bg-white/5 p-3">
                            <div className="text-sm font-semibold text-gray-100 mb-2">{sec.title}</div>
                            <div className="space-y-2">
                              {sec.items.map((it, idx) => (
                                <TaskTree key={`${it.text}-${idx}`} item={it} depth={0} />
                              ))}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  ) : null}
                </section>

                <section className="space-y-2">
                  <div className="text-sm font-semibold text-white">Comments</div>

                  <div className="rounded-xl border border-white/10 bg-white/5 p-3 space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <div>
                        <div className="text-[11px] text-gray-400 mb-1">Author</div>
                        <Input value={author} onChange={(e) => setAuthor(e.target.value)} placeholder="Alan" />
                      </div>
                      <div>
                        <div className="text-[11px] text-gray-400 mb-1">Body (max 2000)</div>
                        <div className="text-[11px] text-gray-500 text-right">{body.length}/2000</div>
                      </div>
                    </div>

                    <textarea
                      className="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-white/20"
                      rows={4}
                      value={body}
                      onChange={(e) => setBody(e.target.value)}
                      maxLength={2000}
                      placeholder="Escreva um comentário…"
                    />

                    <div className="flex items-center justify-between gap-3">
                      <div className="text-xs text-gray-500">Append-only (sem editar/apagar) — v1</div>
                      <Button
                        onClick={() => createComment.mutate()}
                        disabled={createComment.isPending || !author.trim() || !body.trim()}
                      >
                        {createComment.isPending ? 'Enviando…' : 'Comentar'}
                      </Button>
                    </div>

                    {createComment.error ? (
                      <div className="text-xs text-red-400">
                        {createComment.error instanceof Error ? createComment.error.message : 'Falha ao enviar'}
                      </div>
                    ) : null}
                  </div>

                  {commentsQuery.isLoading ? (
                    <div className="text-sm text-gray-400">Carregando comentários…</div>
                  ) : commentsQuery.error ? (
                    <div className="text-sm text-red-400">
                      Erro: {commentsQuery.error instanceof Error ? commentsQuery.error.message : 'falha ao carregar'}
                    </div>
                  ) : commentsQuery.data ? (
                    <div className="space-y-3">
                      {commentsQuery.data.items.length === 0 ? (
                        <div className="text-xs text-gray-500">(sem comentários ainda)</div>
                      ) : (
                        commentsQuery.data.items.map((c) => (
                          <div key={c.id} className="rounded-xl border border-white/10 bg-black/20 p-3">
                            <div className="flex items-baseline justify-between gap-3">
                              <div className="text-sm font-semibold text-white truncate">{c.author}</div>
                              <div className="text-[11px] text-gray-500 font-mono shrink-0">{formatTs(c.created_at)}</div>
                            </div>
                            <div className="mt-2 text-sm text-gray-200 whitespace-pre-wrap break-words">{c.body}</div>
                          </div>
                        ))
                      )}
                    </div>
                  ) : null}
                </section>
              </div>
            </div>
          </aside>
        </div>
      ) : null}
    </main>
  )
}
