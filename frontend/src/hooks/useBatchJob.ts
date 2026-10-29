import { useCallback, useEffect, useRef, useState } from 'react'
import { API_BASE_URL } from '../lib/apiBase'
import { authFetch } from '../lib/authFetch'
import { refusalMessage } from '../lib/assetSelection'
import { isJobFinal, type BatchJob, type BatchPreview } from '../lib/batchLote'

export type { BatchJob, BatchPreview } from '../lib/batchLote'

const BASE = `${API_BASE_URL}/combos/backtest/batch`
// Polling do lote; os testes E2E encurtam o intervalo com VITE_BATCH_POLL_MS.
const POLL_MS = Number(import.meta.env.VITE_BATCH_POLL_MS) || 2000
const POLL_FAST_MS = Math.min(POLL_MS, 1000)

export type ConfirmState =
  | { phase: 'closed' }
  | { phase: 'loading' }
  | { phase: 'ready'; preview: BatchPreview; body: Record<string, unknown> }
  | { phase: 'paused'; jobId: string }
  | { phase: 'error'; message: string }

export type PendingAction = 'pause' | 'cancel' | null

async function readJson<T>(res: Response): Promise<T | null> {
  try {
    return (await res.json()) as T
  } catch {
    return null
  }
}

/**
 * Lote multiclasse (`/api/combos/backtest/batch`): plano antes de começar, progresso por ativo,
 * Pausar, Retomar e Encerrar. Compartilhado pelo Combo e pela Otimização. O estado vive no servidor
 * (PostgreSQL): ao reabrir a página o painel do lote não final volta (`GET /batch/active`).
 */
export function useBatchJob() {
  const [job, setJob] = useState<BatchJob | null>(null)
  const [confirm, setConfirm] = useState<ConfirmState>({ phase: 'closed' })
  const [starting, setStarting] = useState(false)
  const [pending, setPending] = useState<PendingAction>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const jobId = job?.job_id ?? null
  const status = job?.status ?? null
  const pauseRequested = !!job?.pause_requested || !!job?.cancel_requested
  const mounted = useRef(true)

  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])

  const load = useCallback(async (id: string): Promise<BatchJob | null> => {
    try {
      const res = await authFetch(`${BASE}/${id}`)
      if (!res.ok) return null
      const data = await readJson<BatchJob>(res)
      if (data && mounted.current) setJob(data)
      return data
    } catch {
      return null
    }
  }, [])

  // Ao abrir a página: o lote não final mais recente do usuário (rodando, na fila ou pausado).
  useEffect(() => {
    let cancelled = false
    void (async () => {
      try {
        const res = await authFetch(`${BASE}/active`)
        if (!res.ok) return
        const data = await readJson<BatchJob | null>(res)
        if (!cancelled && data && data.job_id) setJob(data)
      } catch {
        /* sem lote ativo visível: a tela segue como estava */
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  // Polling: rodando ou na fila (2 s; 1 s enquanto um pedido de pausa/encerramento espera a etapa).
  useEffect(() => {
    if (!jobId || !status || isJobFinal(job) || status === 'paused') return
    const timer = setInterval(() => {
      void load(jobId)
    }, pauseRequested || pending ? POLL_FAST_MS : POLL_MS)
    return () => clearInterval(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId, status, pauseRequested, pending, load])

  // O pedido de pausa/encerramento terminou quando o servidor mostra o novo estado.
  useEffect(() => {
    if (pending && (status === 'paused' || isJobFinal(job))) setPending(null)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, pending])

  const closeConfirm = useCallback(() => setConfirm({ phase: 'closed' }), [])

  /** Um lote já terminado sai da tela quando o usuário parte para outra execução. */
  const dismissFinished = useCallback(() => {
    setJob((current) => (current && isJobFinal(current) ? null : current))
  }, [])

  /** Abre o Confirmar com o plano do servidor, ou o aviso do lote pausado (decisão 16). */
  const requestPreview = useCallback(
    async (body: Record<string, unknown>) => {
      setActionError(null)
      if (job?.status === 'paused') {
        setConfirm({ phase: 'paused', jobId: job.job_id })
        return
      }
      setConfirm({ phase: 'loading' })
      try {
        const res = await authFetch(`${BASE}/preview`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        })
        const data = await readJson<Record<string, unknown>>(res)
        if (res.status === 409 && (data?.detail as { code?: string } | undefined)?.code === 'batch_paused') {
          const pausedId = String((data?.detail as { job_id?: string }).job_id)
          await load(pausedId)
          setConfirm({ phase: 'paused', jobId: pausedId })
          return
        }
        if (!res.ok) {
          setConfirm({ phase: 'error', message: refusalMessage(data?.detail, 'Falha ao montar o plano do lote') })
          return
        }
        if (!Array.isArray(data?.items)) {
          setConfirm({ phase: 'error', message: 'O servidor devolveu um plano de lote que a tela não entende.' })
          return
        }
        setConfirm({ phase: 'ready', preview: data as unknown as BatchPreview, body })
      } catch (e) {
        setConfirm({ phase: 'error', message: e instanceof Error ? e.message : 'Falha ao montar o plano do lote' })
      }
    },
    [job, load],
  )

  /** "Confirmar e rodar": o servidor cria o lote e o painel aparece no lugar do Confirmar. */
  const confirmAndRun = useCallback(
    async (body: Record<string, unknown>): Promise<boolean> => {
      setStarting(true)
      setActionError(null)
      try {
        const res = await authFetch(BASE, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        })
        const data = await readJson<Record<string, unknown>>(res)
        if (res.status === 409 && (data?.detail as { code?: string } | undefined)?.code === 'batch_paused') {
          const pausedId = String((data?.detail as { job_id?: string }).job_id)
          await load(pausedId)
          setConfirm({ phase: 'paused', jobId: pausedId })
          return false
        }
        if (!res.ok || !data?.job_id) {
          setConfirm({ phase: 'error', message: refusalMessage(data?.detail, 'Falha ao iniciar o lote') })
          return false
        }
        setConfirm({ phase: 'closed' })
        setPending(null)
        await load(String(data.job_id))
        return true
      } catch (e) {
        setConfirm({ phase: 'error', message: e instanceof Error ? e.message : 'Falha ao iniciar o lote' })
        return false
      } finally {
        if (mounted.current) setStarting(false)
      }
    },
    [load],
  )

  const act = useCallback(
    async (kind: 'pause' | 'cancel' | 'resume', id: string | null) => {
      if (!id) return
      setActionError(null)
      if (kind !== 'resume') setPending(kind)
      try {
        const res = await authFetch(`${BASE}/${id}/${kind}`, { method: 'POST' })
        if (!res.ok) {
          const data = await readJson<Record<string, unknown>>(res)
          setPending(null)
          setActionError(refusalMessage(data?.detail, 'Não foi possível concluir o pedido'))
        }
      } catch (e) {
        setPending(null)
        setActionError(e instanceof Error ? e.message : 'Não foi possível concluir o pedido')
      }
      await load(id)
    },
    [load],
  )

  const pause = useCallback(() => act('pause', jobId), [act, jobId])
  const cancel = useCallback(() => act('cancel', jobId), [act, jobId])
  const resume = useCallback(() => act('resume', jobId), [act, jobId])
  const cancelById = useCallback((id: string) => act('cancel', id), [act])
  const resumeById = useCallback((id: string) => act('resume', id), [act])

  const active = !!job && !isJobFinal(job)

  return {
    job,
    active,
    confirm,
    starting,
    pending,
    actionError,
    closeConfirm,
    dismissFinished,
    requestPreview,
    confirmAndRun,
    pause,
    cancel,
    resume,
    cancelById,
    resumeById,
  }
}

export { formatDuration as formatElapsed } from '../lib/batchLote'
export { isJobFinal as isBatchFinal } from '../lib/batchLote'
