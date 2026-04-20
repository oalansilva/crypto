import { Badge } from '@/components/ui/Badge'
import { SignalsList } from './SignalsList'

export type AIDashboardInsight = {
  id: string
  title: string
  description: string
  tone: string
  asset: string | null
  badge: string | null
}

export type AIDashboardFearGreed = {
  value: number
  label: string
  tone: string
}

export type AIDashboardIndicatorReading = {
  asset: string
  value: string
  status: string
  tone: string
}

export type AIDashboardIndicator = {
  id: string
  title: string
  subtitle: string
  readings: AIDashboardIndicatorReading[]
}

export type AIDashboardSignal = {
  id: string
  asset: string
  action: string
  confidence: number
  reason: string
  direction: string
  strength: number
  total_sources: number
  price: number | null
  sources: Array<{
    source: string
    action: string
    confidence: number
    direction?: string
    status?: string
    reason?: string
    price?: number | null
    criteria?: Array<{
      label: string
      score?: number | null
      value?: string | null
    }>
  }>
}

export type AIDashboardStats = {
  hit_rate: number
  total_signals: number
  avg_confidence: number
}

export type AIDashboardNewsItem = {
  id: string
  title: string
  summary: string
  source: string
  url: string
  published_at: string
  relative_time: string
  sentiment: string
  related_asset: string | null
}

export type AIDashboardResponse = {
  generated_at: string
  insights: AIDashboardInsight[]
  fear_greed: AIDashboardFearGreed
  indicators: AIDashboardIndicator[]
  recent_signals: AIDashboardSignal[]
  stats: AIDashboardStats
  news: AIDashboardNewsItem[]
  section_errors: Record<string, string>
}

function formatGeneratedAt(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'Atualização indisponível'
  }

  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(date)
}

export function AIDashboard({ data }: { data: AIDashboardResponse }) {
  const errorEntries = Object.entries(data.section_errors || {})

  return (
    <div className="app-page space-y-6 pb-20">
      <section className="page-card relative overflow-hidden p-6 sm:p-7 lg:p-8">
        <div className="absolute inset-x-0 top-0 h-px bg-[linear-gradient(90deg,transparent,rgba(56,189,248,0.55),transparent)]" />
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-3">
            <div className="eyebrow">
              <span>AI Dashboard</span>
            </div>
            <div className="space-y-2">
              <h1 className="section-title">Sinais unificados por ativo</h1>
              <p className="section-copy">
                Esta tela exibe somente sinais consolidados entre AI e Signals. Quando o cruzamento entre fontes não é suficiente, itens de fonte única são ocultados para manter apenas decisões confiáveis por ativo.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Badge className="border border-emerald-400/25 bg-emerald-500/12 px-3 py-1 text-emerald-200" variant="default">
              Atualizado {formatGeneratedAt(data.generated_at)}
            </Badge>
            {errorEntries.length > 0 ? (
              <Badge className="px-3 py-1" variant="warning">
                {errorEntries.length} seção(ões) com fallback
              </Badge>
            ) : (
              <Badge className="px-3 py-1" variant="success">
                Todas as seções online
              </Badge>
            )}
          </div>
        </div>
      </section>

      <SignalsList signals={data.recent_signals} sectionErrors={data.section_errors} />
    </div>
  )
}

export default AIDashboard
