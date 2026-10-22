import { useEffect, useRef, useState } from 'react'
import { API_BASE_URL } from '../lib/apiBase'
import { authFetch } from '../lib/authFetch'

export interface BatchProgress {
  status: string
  processed: number
  total: number
  succeeded: number
  failed: number
  skipped?: number
  errors: Array<{ symbol: string; error: string }>
  started_at: string | null
  elapsed_sec: number
  estimated_remaining_sec: number | null
  current_symbol?: string | null
}

const FINAL_STATUSES = ['completed', 'failed', 'paused', 'cancelled']

/**
 * Lote do Combo (`POST /combos/backtest/batch`): progresso por polling, Pausar e
 * Encerrar. Compartilhado pelo Combo e pela Otimização, que rodam o mesmo lote.
 */
export function useBatchJob() {
  const [batchRunning, setBatchRunning] = useState(false)
  const [batchJobId, setBatchJobId] = useState<string | null>(null)
  const [batchPauseCancelRequested, setBatchPauseCancelRequested] = useState(false)
  const [batchProgress, setBatchProgress] = useState<BatchProgress | null>(null)
  const [batchTotal, setBatchTotal] = useState(0)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const batchStartTimeRef = useRef<number | null>(null)
  const [clientElapsedSec, setClientElapsedSec] = useState(0)

  const handlePauseBatch = async () => {
    if (!batchJobId || batchPauseCancelRequested) return
    setBatchPauseCancelRequested(true)
    try {
      const res = await authFetch(`${API_BASE_URL}/combos/backtest/batch/${batchJobId}/pause`, { method: 'POST' })
      if (!res.ok) setBatchPauseCancelRequested(false)
    } catch {
      setBatchPauseCancelRequested(false)
    }
  }

  const handleCancelBatch = async () => {
    if (!batchJobId || batchPauseCancelRequested) return
    setBatchPauseCancelRequested(true)
    try {
      const res = await authFetch(`${API_BASE_URL}/combos/backtest/batch/${batchJobId}/cancel`, { method: 'POST' })
      if (!res.ok) setBatchPauseCancelRequested(false)
    } catch {
      setBatchPauseCancelRequested(false)
    }
  }

  useEffect(() => {
    if (!batchJobId) return
    const poll = async () => {
      try {
        const res = await authFetch(`${API_BASE_URL}/combos/backtest/batch/${batchJobId}`)
        if (!res.ok) return
        const data = await res.json()
        setBatchProgress(data)
        if (FINAL_STATUSES.includes(data.status)) {
          if (pollRef.current) {
            clearInterval(pollRef.current)
            pollRef.current = null
          }
          setBatchRunning(false)
          setBatchJobId(null)
          setBatchPauseCancelRequested(false)
          batchStartTimeRef.current = null
        }
      } catch {
        /* ignore */
      }
    }
    poll()
    pollRef.current = setInterval(poll, 2000)
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [batchJobId])

  useEffect(() => {
    if (!batchRunning) return
    const t = setInterval(() => {
      const start = batchStartTimeRef.current
      if (start != null) setClientElapsedSec(Math.floor((Date.now() - start) / 1000))
    }, 1000)
    return () => clearInterval(t)
  }, [batchRunning])

  return {
    batchRunning,
    setBatchRunning,
    batchJobId,
    setBatchJobId,
    batchPauseCancelRequested,
    setBatchPauseCancelRequested,
    batchProgress,
    setBatchProgress,
    batchTotal,
    setBatchTotal,
    clientElapsedSec,
    setClientElapsedSec,
    batchStartTimeRef,
    handlePauseBatch,
    handleCancelBatch,
  }
}

export function isBatchFinal(progress: BatchProgress | null): boolean {
  return progress != null && FINAL_STATUSES.includes(progress.status)
}

export function formatElapsed(sec: number): string {
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}m ${s}s`
}
