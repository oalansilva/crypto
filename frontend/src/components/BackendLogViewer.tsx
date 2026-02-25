import React, { useEffect, useMemo, useState } from 'react'
import { API_BASE_URL } from '../lib/apiBase'

type LogName = 'full_execution_log' | 'backtest_debug'

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

  const url = useMemo(() => {
    // API_BASE_URL may be relative (e.g. "/api"), which requires a base URL.
    const endpoint = `${API_BASE_URL}/logs/tail`
    const u = endpoint.startsWith('http')
      ? new URL(endpoint)
      : new URL(endpoint, window.location.origin)

    u.searchParams.set('name', name)
    u.searchParams.set('lines', String(lines))
    return u.toString()
  }, [name, lines])

  useEffect(() => {
    if (!open) return

    let alive = true
    const tick = async () => {
      try {
        setError(null)
        const res = await fetch(url)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        if (alive) setContent(data.content || '')
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : 'Erro ao buscar logs'
        if (alive) setError(msg)
      }
    }

    tick()
    const id = window.setInterval(tick, pollMs)
    return () => {
      alive = false
      window.clearInterval(id)
    }
  }, [open, url, pollMs])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative w-full max-w-5xl max-h-[85vh] rounded-2xl border border-white/10 bg-gray-900/95 overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
          <div>
            <div className="text-white font-bold">Logs do Backend</div>
            <div className="text-xs text-gray-400 font-mono">{name} • atualiza a cada {Math.round(pollMs / 1000)}s</div>
          </div>
          <button onClick={onClose} className="text-gray-300 hover:text-white px-3 py-1 rounded bg-white/5 hover:bg-white/10">
            Fechar
          </button>
        </div>

        {error ? (
          <div className="px-4 py-3 text-sm text-red-400 border-b border-red-500/30 bg-red-500/10">{error}</div>
        ) : null}

        <div className="p-4">
          <pre className="text-xs text-gray-200 whitespace-pre-wrap font-mono overflow-auto max-h-[70vh]">
            {content || '(sem logs ainda)'}
          </pre>
        </div>
      </div>
    </div>
  )
}
