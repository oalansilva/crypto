import { useCallback, useEffect, useMemo, useState } from 'react'
import { API_BASE_URL, apiUrl } from '@/lib/apiBase'
import type { LabLogEntry, LabLogLevel, LogConnectionState } from '@/types/lab'

interface UseLogSSEOptions {
  runId: string
  enabled: boolean
  step?: string
}

interface UseLogSSEResult {
  logs: LabLogEntry[]
  connectionState: LogConnectionState
  isConnected: boolean
  error: Error | null
  reconnect: () => void
}

const MAX_LOG_ENTRIES = 4000

function normalizeLevel(level: unknown): LabLogLevel {
  const value = String(level || 'INFO').toUpperCase()
  if (value === 'WARNING') return 'WARN'
  if (value === 'WARN' || value === 'ERROR' || value === 'DEBUG' || value === 'INFO') return value
  return 'INFO'
}

function parseEntry(data: unknown): LabLogEntry | null {
  if (!data || typeof data !== 'object') return null
  const item = data as Record<string, unknown>
  const message = String(item.message || '').trim()
  if (!message) return null
  return {
    timestamp: String(item.timestamp || ''),
    level: normalizeLevel(item.level),
    message,
    step: String(item.step || ''),
    phase: item.phase ? String(item.phase) : undefined,
  }
}

function getStoredJwtToken(): string {
  if (typeof window === 'undefined') return ''
  const keys = ['lab_jwt_token', 'auth_token', 'token']
  for (const key of keys) {
    const value = String(window.localStorage.getItem(key) || '').trim()
    if (value) return value
  }
  return ''
}

function isSameEntry(a: LabLogEntry, b: LabLogEntry): boolean {
  return a.timestamp === b.timestamp && a.level === b.level && a.message === b.message && a.step === b.step
}

export function useLogSSE({ runId, enabled, step }: UseLogSSEOptions): UseLogSSEResult {
  const [logs, setLogs] = useState<LabLogEntry[]>([])
  const [connectionState, setConnectionState] = useState<LogConnectionState>('closed')
  const [error, setError] = useState<Error | null>(null)
  const [retryNonce, setRetryNonce] = useState(0)

  const streamUrl = useMemo(() => {
    const id = String(runId || '').trim()
    if (!id) return ''
    const url = apiUrl(`/lab/runs/${encodeURIComponent(id)}/logs/stream`)
    if (step) url.searchParams.set('step', step)
    const token = getStoredJwtToken()
    if (token) url.searchParams.set('token', token)
    return url.toString()
  }, [runId, step])

  const reconnect = useCallback(() => {
    setRetryNonce((prev) => prev + 1)
  }, [])

  useEffect(() => {
    if (!enabled || !streamUrl) {
      setConnectionState('closed')
      return
    }

    setLogs([])
    setError(null)
    setConnectionState('connecting')

    const source = new EventSource(streamUrl)

    source.onopen = () => {
      setConnectionState('connected')
      setError(null)
    }

    source.onmessage = (event: MessageEvent<string>) => {
      try {
        const payload = JSON.parse(event.data)
        const parsed = parseEntry(payload)
        if (!parsed) return
        setLogs((prev) => {
          if (prev.some((item) => isSameEntry(item, parsed))) return prev
          const next = [...prev, parsed]
          if (next.length > MAX_LOG_ENTRIES) {
            return next.slice(next.length - MAX_LOG_ENTRIES)
          }
          return next
        })
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Falha ao processar mensagem de log'))
      }
    }

    source.addEventListener('done', () => {
      setConnectionState('closed')
      source.close()
    })

    source.onerror = () => {
      if (source.readyState === EventSource.CLOSED) {
        setConnectionState('closed')
        return
      }
      setConnectionState('error')
      setError(new Error('Falha na conexão de logs em tempo real'))
      source.close()
    }

    return () => {
      source.close()
      setConnectionState('closed')
    }
  }, [enabled, streamUrl, retryNonce])

  return {
    logs,
    connectionState,
    isConnected: connectionState === 'connected',
    error,
    reconnect,
  }
}

