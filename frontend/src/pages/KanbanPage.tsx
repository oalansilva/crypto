import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Kanban, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { API_BASE_URL } from '@/lib/apiBase'

type CoordinationChangeItem = {
  id: string
  title?: string | null
  path: string
  status: Record<string, string>
  archived: boolean
  column: string
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

const COLUMNS_ORDER = [
  'PO',
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

  const { data, isLoading, error } = useQuery({
    queryKey: ['coordination', 'changes'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/coordination/changes`)
      if (!res.ok) throw new Error(`Failed to load changes (${res.status})`)
      return (await res.json()) as CoordinationChangeListResponse
    },
    refetchOnWindowFocus: false,
  })

  const items = data?.items || []

  const byColumn = useMemo(() => {
    const map = new Map<string, CoordinationChangeItem[]>()
    for (const c of COLUMNS_ORDER) map.set(c, [])

    for (const it of items) {
      const col = map.has(it.column) ? it.column : 'DEV'
      map.get(col)!.push(it)
    }

    return map
  }, [items])

  const tasksQuery = useQuery({
    queryKey: ['coordination', 'change', selected?.id, 'tasks'],
    enabled: Boolean(selected?.id),
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/coordination/changes/${encodeURIComponent(selected!.id)}/tasks`)
      if (!res.ok) throw new Error(`Failed to load tasks (${res.status})`)
      return (await res.json()) as ChangeTasksChecklistResponse
    },
    refetchOnWindowFocus: false,
  })

  const commentsQuery = useQuery({
    queryKey: ['coordination', 'change', selected?.id, 'comments'],
    enabled: Boolean(selected?.id),
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/coordination/changes/${encodeURIComponent(selected!.id)}/comments`)
      if (!res.ok) throw new Error(`Failed to load comments (${res.status})`)
      return (await res.json()) as CoordinationCommentsListResponse
    },
    refetchOnWindowFocus: false,
  })

  const [author, setAuthor] = useState(() => localStorage.getItem('kanban.commentAuthor') || '')
  const [body, setBody] = useState('')

  const createComment = useMutation({
    mutationFn: async () => {
      if (!selected?.id) throw new Error('No change selected')
      const a = author.trim()
      const b = body.trimEnd()
      if (!a) throw new Error('Author is required')
      if (!b) throw new Error('Body is required')
      if (b.length > 2000) throw new Error('Body too long (max 2000 chars)')

      const res = await fetch(
        `${API_BASE_URL}/coordination/changes/${encodeURIComponent(selected.id)}/comments`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ author: a, body: b }),
        },
      )

      if (!res.ok) {
        const txt = await res.text().catch(() => '')
        throw new Error(`Failed to post comment (${res.status})${txt ? `: ${txt}` : ''}`)
      }

      return (await res.json()) as { item: CoordinationCommentItem }
    },
    onSuccess: async () => {
      localStorage.setItem('kanban.commentAuthor', author.trim())
      setBody('')
      await qc.invalidateQueries({ queryKey: ['coordination', 'change', selected?.id, 'comments'] })
    },
  })

  return (
    <main className="container mx-auto px-6 py-10">
      <div className="flex items-start justify-between gap-6 mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Kanban className="w-5 h-5" /> Kanban
          </h1>
          <p className="text-sm text-gray-400">
            Visualização de coordenação (desktop-first). Colunas fixas; inclui ativos + arquivados.
          </p>
        </div>
      </div>

      <Card className="border border-white/10 glass">
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
                      className="w-[320px] shrink-0 rounded-xl border border-white/10 bg-white/5"
                    >
                      <div className="px-4 py-3 border-b border-white/10">
                        <div className="flex items-center justify-between gap-3">
                          <div className="font-semibold text-sm text-white">{col}</div>
                          <div className="text-xs text-gray-400">{colItems.length}</div>
                        </div>
                      </div>

                      <div className="p-3 space-y-3">
                        {colItems.length === 0 ? (
                          <div className="rounded-lg border border-dashed border-white/10 p-4 text-xs text-gray-500">
                            vazio
                          </div>
                        ) : (
                          colItems.map((it) => (
                            <button
                              type="button"
                              key={it.id}
                              onClick={() => setSelected(it)}
                              className={
                                'w-full text-left rounded-xl border border-white/10 bg-black/30 hover:bg-black/20 transition-colors p-3 focus:outline-none focus:ring-2 focus:ring-white/20 ' +
                                (selected?.id === it.id ? 'ring-2 ring-white/20' : '')
                              }
                              aria-label={`Open details for ${it.id}`}
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div className="min-w-0">
                                  <div className="text-sm font-semibold text-white truncate">{it.title || it.id}</div>
                                  <div className="text-[11px] text-gray-400 font-mono truncate">{it.id}</div>
                                </div>
                                {it.archived ? (
                                  <div className="text-[10px] px-2 py-0.5 rounded-full border border-white/10 text-gray-300">
                                    archived
                                  </div>
                                ) : null}
                              </div>

                              <div className="mt-2 pt-2 border-t border-white/10 space-y-1">
                                <StatusLine label="PO" value={it.status?.['PO']} />
                                <StatusLine
                                  label="Alan approval"
                                  value={it.status?.['Alan approval'] || it.status?.['Alan (Stakeholder)']}
                                />
                                <StatusLine label="DEV" value={it.status?.['DEV']} />
                                <StatusLine label="QA" value={it.status?.['QA']} />
                                <StatusLine
                                  label="Alan homologation"
                                  value={it.status?.['Alan homologation'] || it.status?.['Alan (Stakeholder)']}
                                />
                              </div>
                            </button>
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

      {selected ? (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/70" onClick={() => setSelected(null)} aria-hidden="true" />
          <aside className="absolute right-0 top-0 h-full w-full sm:w-[520px] bg-zinc-950 border-l border-white/10 shadow-2xl">
            <div className="h-full flex flex-col">
              <div className="px-4 py-3 border-b border-white/10 flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="text-sm text-gray-400">Detalhes</div>
                  <div className="text-lg font-semibold text-white truncate">{selected.title || selected.id}</div>
                  <div className="text-[11px] text-gray-500 font-mono truncate">{selected.id}</div>
                </div>
                <Button variant="ghost" onClick={() => setSelected(null)} aria-label="Close panel">
                  <X className="w-4 h-4" />
                </Button>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-6">
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
