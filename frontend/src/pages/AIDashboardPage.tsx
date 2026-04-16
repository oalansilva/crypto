import { useEffect } from 'react'
import { Brain, RefreshCcw } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import AIDashboard, { type AIDashboardResponse } from '@/components/ai-dashboard/AIDashboard'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { useToast } from '@/components/ui/use-toast'
import { apiUrl } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'
import { useAuth } from '@/stores/authStore'

function normalizeAIDashboardPayload(payload: AIDashboardResponse): AIDashboardResponse {
  const rawSignals = Array.isArray(payload.recent_signals) ? payload.recent_signals : []
  const unifiedSignals = rawSignals.filter((signal) => {
    if (Array.isArray(signal.sources) && signal.sources.length > 0) {
      const sourceNames = signal.sources
        .map((item) => (typeof item.source === 'string' ? item.source.trim().toLowerCase() : ''))
        .filter(Boolean)
      const uniqueSources = new Set(sourceNames)
      return uniqueSources.size >= 2
    }

    return Number.isFinite(signal.total_sources) && signal.total_sources >= 2
  })
  const droppedLegacySignals = rawSignals.length > 0 && unifiedSignals.length === 0

  return {
    ...payload,
    recent_signals: unifiedSignals,
    section_errors: {
      ...(payload.section_errors || {}),
      ...(droppedLegacySignals
        ? { signals: 'Não houve alinhamento suficiente entre as fontes nesta carga. Itens legados de fonte única foram ocultados para manter a visão consolidada.' }
        : {}),
    },
  }
}

function useAIDashboard(userId?: string) {
  return useQuery({
    queryKey: ['ai-dashboard', userId],
    queryFn: async () => {
      const response = await authFetch(apiUrl('/ai/dashboard').toString())
      if (!response.ok) {
        throw new Error(`Falha ao carregar AI Dashboard (${response.status})`)
      }
      return normalizeAIDashboardPayload((await response.json()) as AIDashboardResponse)
    },
    enabled: Boolean(userId),
    staleTime: 60_000,
    refetchInterval: 120_000,
  })
}

export default function AIDashboardPage() {
  const { toast } = useToast()
  const { user } = useAuth()
  const query = useAIDashboard(user?.id)

  useEffect(() => {
    if (!query.error) return
    const message = query.error instanceof Error ? query.error.message : 'Falha ao carregar AI Dashboard'
    toast({
      variant: 'destructive',
      title: 'Erro no AI Dashboard',
      description: message,
    })
  }, [query.error, toast])

  if (query.isLoading) {
    return (
      <div className="app-page space-y-6 pb-20">
        <div className="page-card p-6 sm:p-7 lg:p-8">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 animate-pulse items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
              <Brain className="h-5 w-5 text-sky-200" />
            </div>
            <div className="space-y-2">
              <div className="h-4 w-28 animate-pulse rounded-full bg-white/8" />
              <div className="h-8 w-72 max-w-[70vw] animate-pulse rounded-full bg-white/8" />
            </div>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="page-card h-36 animate-pulse" />
          ))}
        </div>

        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(320px,0.7fr)]">
          <div className="grid gap-6 lg:grid-cols-2">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="page-card h-52 animate-pulse" />
            ))}
          </div>
          <div className="page-card h-[420px] animate-pulse" />
        </div>
      </div>
    )
  }

  if (query.isError || !query.data) {
    return (
      <div className="app-page pb-20">
        <Card className="page-card border-red-500/20 bg-[linear-gradient(180deg,rgba(49,18,24,0.94),rgba(26,10,16,0.92))]">
          <CardContent className="flex flex-col gap-4 p-6 sm:p-8 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.16em] text-red-200/80">AI Dashboard</div>
              <h1 className="mt-2 text-2xl font-semibold text-white">Não foi possível carregar os insights</h1>
              <p className="mt-2 max-w-2xl text-sm text-red-100/80">
                {query.error instanceof Error ? query.error.message : 'Erro inesperado ao consultar /api/ai/dashboard.'}
              </p>
            </div>
            <Button onClick={() => query.refetch()} className="gap-2">
              <RefreshCcw className="h-4 w-4" />
              Tentar novamente
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return <AIDashboard data={query.data} />
}
