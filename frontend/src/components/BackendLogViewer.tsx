import React, { useCallback, useEffect, useRef, useState } from 'react'
import { API_BASE_URL } from '../lib/apiBase'

type LogName = 'full_execution_log' | 'backtest_debug'

type TailSnapshot = {
  nextOffset: number
  fileId: string
}

type TailResponse = TailSnapshot & {
  content: string
  cursorReset: boolean
}

const SCROLL_THRESHOLD_PX = 24

export function BackendLogViewer({
  open,
  onClose,
  name = 'full_execution_log',
  pollMs = 2000,
  lines = 250,
}: {
  open: boolean
  onClose: () => void
  name?: LogName
  pollMs?: number
  lines?: number
}) {
  const [content, setContent] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [waiting, setWaiting] = useState(true)
  const [atBottom, setAtBottom] = useState(true)

  const containerRef = useRef<HTMLDivElement | null>(null)
  const panelRef = useRef<HTMLDivElement | null>(null)
  const openRef = useRef(open)
  const contentRef = useRef(content)
  const atBottomRef = useRef(atBottom)
  const cursorRef = useRef<TailSnapshot | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const pollTimerRef = useRef<number | null>(null)
  const pollInFlightRef = useRef(false)
  const sessionRef = useRef(0)

  openRef.current = open
  contentRef.current = content
  atBottomRef.current = atBottom

  const url = useCallback(
    (afterOffset?: number, fileId?: string) => {
      const endpoint = `${API_BASE_URL}/logs/tail`
      const u = endpoint.startsWith('http')
        ? new URL(endpoint)
        : new URL(endpoint, window.location.origin)

      u.searchParams.set('name', name)
      u.searchParams.set('lines', String(lines))
      if (afterOffset !== undefined) {
        u.searchParams.set('after_offset', String(afterOffset))
        u.searchParams.set('file_id', fileId ?? '')
      }
      return u.toString()
    },
    [name, lines],
  )

  const handleScroll = useCallback(() => {
    const el = containerRef.current
    if (!el) return
    const bottom = el.scrollHeight - el.scrollTop - el.clientHeight
    setAtBottom(bottom <= SCROLL_THRESHOLD_PX)
  }, [])

  const scrollToBottom = useCallback(() => {
    const el = containerRef.current
    if (el) el.scrollTop = el.scrollHeight
    setAtBottom(true)
  }, [])

  const schedulePoll = useCallback(
    (session: number) => {
      if (pollTimerRef.current !== null) {
        window.clearTimeout(pollTimerRef.current)
        pollTimerRef.current = null
      }
      pollTimerRef.current = window.setTimeout(() => {
        void tick(session)
      }, pollMs)
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [pollMs, url],
  )

  const tick = useCallback(
    async (session: number) => {
      if (!openRef.current || session !== sessionRef.current) return
      if (pollInFlightRef.current) return

      pollInFlightRef.current = true
      const controller = new AbortController()
      abortRef.current = controller
      setError(null)
      try {
        const cursor = cursorRef.current
        const target = cursor
          ? url(cursor.nextOffset, cursor.fileId)
          : url(undefined, undefined)
        const res = await fetch(target, { signal: controller.signal })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = (await res.json()) as TailResponse

        if (!openRef.current || session !== sessionRef.current) return

        if (cursor && data.cursorReset) {
          // Arquivo truncado/rotacionado: reinicia a sessão no arquivo atual.
          cursorRef.current = null
          setContent('')
          setWaiting(true)
          setError(null)
          await startSession(session)
          return
        }

        cursorRef.current = { nextOffset: data.nextOffset, fileId: data.fileId }
        if (data.content) {
          setContent((prev) => prev + data.content)
          setWaiting(false)
          // Rola somente quando a aderência ao final já estava ativa.
          if (atBottomRef.current) {
            requestAnimationFrame(() => {
              const el = containerRef.current
              if (el) el.scrollTop = el.scrollHeight
            })
          }
        } else {
          setError(null)
        }
      } catch (e: unknown) {
        if (!openRef.current || session !== sessionRef.current) return
        if (e instanceof DOMException && e.name === 'AbortError') return
        const msg = e instanceof Error ? e.message : 'Erro ao buscar logs'
        setError((prev) => (prev ? prev : msg))
      } finally {        pollInFlightRef.current = false
        abortRef.current = null
        if (openRef.current && session === sessionRef.current) {
          schedulePoll(session)
        }
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [url, schedulePoll],
  )

  const startSession = useCallback(
    async (session: number) => {
      if (!openRef.current || session !== sessionRef.current) return
      const controller = new AbortController()
      abortRef.current = controller
      try {
        const res = await fetch(url(undefined, undefined), { signal: controller.signal })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = (await res.json()) as TailResponse
        if (!openRef.current || session !== sessionRef.current) return
        // Conteúdo-base descartado: a sessão começa vazia a partir do cursor.
        cursorRef.current = { nextOffset: data.nextOffset, fileId: data.fileId }
        setError(null)
        setWaiting(true)
      } catch (e: unknown) {
        if (!openRef.current || session !== sessionRef.current) return
        if (e instanceof DOMException && e.name === 'AbortError') return
        const msg = e instanceof Error ? e.message : 'Erro ao buscar logs'
        setError(msg)
      } finally {
        abortRef.current = null
        if (openRef.current && session === sessionRef.current) {
          schedulePoll(session)
        }
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [url, schedulePoll],
  )

  useEffect(() => {
    if (!open) return

    sessionRef.current += 1
    const session = sessionRef.current
    cursorRef.current = null
    setContent('')
    setError(null)
    setWaiting(true)
    setAtBottom(true)

    void startSession(session)

    return () => {
      openRef.current = false
      abortRef.current?.abort()
      abortRef.current = null
      if (pollTimerRef.current !== null) {
        window.clearTimeout(pollTimerRef.current)
        pollTimerRef.current = null
      }
      pollInFlightRef.current = false
    }
  }, [open, startSession])

  useEffect(() => {
    if (!open) return
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open, onClose])

  useEffect(() => {
    if (!open) return
    const panel = panelRef.current
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    const focusables = () =>
      panel
        ? Array.from(
            panel.querySelectorAll<HTMLElement>(
              'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
            ),
          )
        : []
    const trap = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return
      const items = focusables()
      if (!items.length) return
      const first = items[0]
      const last = items[items.length - 1]
      const active = document.activeElement as HTMLElement | null
      if (!active || !panel?.contains(active)) {
        // Foco fora do painel (ex.: inicial no próprio painel): entra no primeiro.
        e.preventDefault()
        first.focus()
        return
      }
      if (e.shiftKey && active === first) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && active === last) {
        e.preventDefault()
        first.focus()
      }
    }
    window.addEventListener('keydown', trap)
    // Foco inicial no painel e devolução ao fechar.
    const restore = document.activeElement as HTMLElement | null
    panel?.focus()

    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', trap)
      restore?.focus()
    }
  }, [open, onClose])

  useEffect(() => {
    if (!open) return
    const el = containerRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [open])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Logs do Backend"
    >
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div
        ref={panelRef}
        tabIndex={-1}
        className="relative flex flex-col w-full max-w-5xl h-[85vh] rounded-2xl border border-white/10 bg-gray-900/95 overflow-hidden shadow-2xl outline-none"
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
          <div>
            <div className="text-white font-bold">Logs do Backend</div>
            <div className="text-xs text-gray-400 font-mono">
              {name} • atualiza a cada {Math.round(pollMs / 1000)}s
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span role="status" className="text-xs text-gray-400">
              {atBottom ? 'Rolagem automática' : 'Rolagem pausada'}
            </span>
            {!atBottom ? (
              <button
                onClick={scrollToBottom}
                className="text-xs text-cyan-400 hover:text-cyan-300 px-2 py-1 rounded bg-white/5 hover:bg-white/10"
              >
                Ir para o fim
              </button>
            ) : null}
            <button
              onClick={onClose}
              className="text-gray-300 hover:text-white px-3 py-1 rounded bg-white/5 hover:bg-white/10"
            >
              Fechar
            </button>
          </div>
        </div>

        {error ? (
          <div className="px-4 py-2 text-sm text-amber-400 border-b border-amber-500/30 bg-amber-500/10">
            {error}
          </div>
        ) : null}

        <div className="p-4 min-h-0 flex-1">
          <div
            ref={containerRef}
            onScroll={handleScroll}
            className="h-full overflow-auto text-xs text-gray-200 whitespace-pre-wrap font-mono rounded-lg border border-white/10 bg-black/30 p-3"
          >
            {content || (waiting ? 'Aguardando eventos…' : '(sem logs ainda)')}
          </div>
        </div>
      </div>
    </div>
  )
}
