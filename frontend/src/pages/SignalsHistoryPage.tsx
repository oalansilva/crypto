import { useEffect, useState } from 'react'
import { RefreshCcw } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

import { SignalStats } from '@/components/signals/SignalStats'
import { SignalHistoryList, type FiltersState } from '@/components/signals/SignalHistoryList'
import { Button } from '@/components/ui/Button'
import { apiUrl } from '@/lib/apiBase'
import { useToast } from '@/components/ui/use-toast'
import type { SignalHistoryResponse, SignalStats as SignalStatsType } from '@/types/signals'

const PAGE_SIZE = 20

function useDebouncedValue<T>(value: T, delay = 300) {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delay)
    return () => window.clearTimeout(timer)
  }, [delay, value])

  return debounced
}

const DEFAULT_FILTERS: FiltersState = {
  asset: '',
  type: '',
  status: '',
  data_inicio: '',
  data_fim: '',
  confidence_min: 0,
}

export default function SignalsHistoryPage() {
  const { toast } = useToast()
  const [filters, setFilters] = useState<FiltersState>(DEFAULT_FILTERS)
  const [page, setPage] = useState(1)

  const debouncedFilters = useDebouncedValue(filters, 300)

  const query = useQuery({
    queryKey: ['signals-history', debouncedFilters, page],
    queryFn: async (): Promise<SignalHistoryResponse> => {
      const url = apiUrl('/signals/history')
      url.searchParams.set('limit', String(PAGE_SIZE))
      url.searchParams.set('offset', String((page - 1) * PAGE_SIZE))

      if (debouncedFilters.asset) url.searchParams.set('asset', debouncedFilters.asset)
      if (debouncedFilters.type) url.searchParams.set('type', debouncedFilters.type)
      if (debouncedFilters.status) url.searchParams.set('status', debouncedFilters.status)
      if (debouncedFilters.data_inicio) url.searchParams.set('data_inicio', debouncedFilters.data_inicio)
      if (debouncedFilters.data_fim) url.searchParams.set('data_fim', debouncedFilters.data_fim)
      if (debouncedFilters.confidence_min > 0) url.searchParams.set('confidence_min', String(debouncedFilters.confidence_min))

      const response = await fetch(url.toString())
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      return response.json()
    },
    placeholderData: (prev) => prev,
  })

  const statsQuery = useQuery({
    queryKey: ['signals-stats'],
    queryFn: async (): Promise<SignalStatsType> => {
      const url = apiUrl('/signals/stats')
      if (debouncedFilters.data_inicio) url.searchParams.set('data_inicio', debouncedFilters.data_inicio)
      if (debouncedFilters.data_fim) url.searchParams.set('data_fim', debouncedFilters.data_fim)

      const response = await fetch(url.toString())
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      return response.json()
    },
  })

  useEffect(() => {
    if (!query.error) return
    toast({
      variant: 'destructive',
      title: 'Erro ao carregar histórico',
      description: query.error instanceof Error ? query.error.message : 'Falha desconhecida',
    })
  }, [query.error, toast])

  function handleFiltersChange(newFilters: FiltersState) {
    setFilters(newFilters)
    setPage(1)
  }

  function handlePageChange(newPage: number) {
    setPage(newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="app-page space-y-6 pb-20">
      {/* Header */}
      <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">Card #57</p>
          <h1 className="mt-2 text-3xl font-bold text-[var(--text-primary)]">Histórico de Sinais</h1>
          <p className="mt-2 max-w-3xl text-sm text-[var(--text-secondary)]">
            Acompanha todos os sinais gerados, com filtros, paginação e PnL por posição.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="secondary"
            onClick={() => void query.refetch()}
            icon={<RefreshCcw className="h-4 w-4" />}
            disabled={query.isFetching}
          >
            Atualizar
          </Button>
        </div>
      </header>

      {/* Stats */}
      <SignalStats stats={statsQuery.data ?? null} isLoading={statsQuery.isLoading} />

      {/* Main Content */}
      <SignalHistoryList
        data={query.data ?? null}
        isLoading={query.isLoading}
        onFiltersChange={handleFiltersChange}
        filters={filters}
        onPageChange={handlePageChange}
      />

      {/* Disclaimer */}
      <div className="rounded-xl border border-amber-400/20 bg-amber-400/8 px-4 py-3">
        <p className="text-xs text-amber-200">
          ⚠️ <strong>Isenção de responsabilidade:</strong> Este não é advice financeiro. Sinais passados não garantem resultados futuros.
        </p>
      </div>
    </div>
  )
}
