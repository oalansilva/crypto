import React, { useEffect, useMemo, useRef, useState } from 'react'
import type { LabLogEntry } from '@/types/lab'

interface LogPanelProps {
  logs: LabLogEntry[]
  isLoading: boolean
  isConnected: boolean
  error: string | null
  fullLogUrl?: string | null
  onRetry?: () => void
  onClose?: () => void
}

const LEVEL_CLASS: Record<string, string> = {
  INFO: 'text-gray-300',
  WARN: 'text-yellow-400',
  ERROR: 'text-red-400',
  DEBUG: 'text-blue-400',
}

function formatTimestamp(value: string): string {
  if (!value) return '-'
  const parsed = Date.parse(value)
  if (Number.isNaN(parsed)) return value
  return new Date(parsed).toISOString()
}

export default function LogPanel({
  logs,
  isLoading,
  isConnected,
  error,
  fullLogUrl,
  onRetry,
  onClose,
}: LogPanelProps) {
  const scrollRef = useRef<HTMLDivElement | null>(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!autoScroll || !scrollRef.current) return
    const node = scrollRef.current
    node.scrollTop = node.scrollHeight
  }, [logs, autoScroll])

  const copyable = useMemo(() => {
    if (!logs.length) return ''
    return logs
      .map((item) => `[${item.timestamp}] [${item.level}] ${item.message}`)
      .join('\n')
  }, [logs])

  const copyLogs = async () => {
    if (!copyable) return
    try {
      await navigator.clipboard.writeText(copyable)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1200)
    } catch {
      setCopied(false)
    }
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-white">Logs do Step (tempo real)</div>
          <div className="text-xs text-gray-400">
            {isConnected ? 'Conectado' : isLoading ? 'Conectando...' : 'Desconectado'}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {fullLogUrl ? (
            <a
              href={fullLogUrl}
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1.5 text-xs rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-gray-200"
            >
              Log completo
            </a>
          ) : null}
          <button
            type="button"
            onClick={() => setAutoScroll((prev) => !prev)}
            className="px-3 py-1.5 text-xs rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-gray-200"
          >
            {autoScroll ? 'Pausar scroll' : 'Continuar scroll'}
          </button>
          <button
            type="button"
            onClick={copyLogs}
            disabled={!logs.length}
            className="px-3 py-1.5 text-xs rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 disabled:opacity-50 text-gray-200"
          >
            {copied ? 'Copiado' : 'Copiar logs'}
          </button>
          {onClose ? (
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 text-xs rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-gray-200"
            >
              Fechar
            </button>
          ) : null}
        </div>
      </div>

      {error ? (
        <div className="mt-3 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-200">
          {error}
          {onRetry ? (
            <button
              type="button"
              onClick={onRetry}
              className="ml-3 underline underline-offset-2 text-red-100 hover:text-white"
            >
              Tentar novamente
            </button>
          ) : null}
        </div>
      ) : null}

      <div
        ref={scrollRef}
        className="mt-3 h-[300px] w-full overflow-y-auto rounded-xl border border-white/10 bg-gray-900 p-3 font-mono text-sm"
      >
        {!logs.length && isLoading ? (
          <div className="text-gray-400">Conectando...</div>
        ) : null}
        {!logs.length && !isLoading ? (
          <div className="text-gray-500">(sem logs ainda)</div>
        ) : null}
        {logs.map((item, idx) => (
          <div key={`${item.timestamp}-${idx}`} className="flex flex-wrap items-start gap-x-3 gap-y-1 leading-relaxed">
            <span className="text-gray-500">{formatTimestamp(item.timestamp)}</span>
            <span className={LEVEL_CLASS[item.level] || LEVEL_CLASS.INFO}>[{item.level}]</span>
            <span className={LEVEL_CLASS[item.level] || LEVEL_CLASS.INFO}>{item.message}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
