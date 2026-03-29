import { ExternalLink, Newspaper } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card, CardContent } from '@/components/ui/Card'
import type { AIDashboardNewsItem } from './AIDashboard'

function sentimentVariant(sentiment: string) {
  switch (sentiment) {
    case 'bullish':
      return 'success' as const
    case 'bearish':
      return 'danger' as const
    case 'neutral':
      return 'secondary' as const
    default:
      return 'outline' as const
  }
}

export function DailyNews({ news }: { news: AIDashboardNewsItem[] }) {
  return (
    <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
      <CardContent className="p-6">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Notícias</div>
            <h2 className="mt-2 text-xl font-semibold text-[var(--text-primary)]">Resumo diário do mercado</h2>
          </div>
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
            <Newspaper className="h-5 w-5 text-sky-200" />
          </div>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          {news.slice(0, 5).map((item) => (
            <a
              key={item.id}
              href={item.url}
              target="_blank"
              rel="noreferrer"
              className="page-card-muted group flex h-full flex-col justify-between gap-4 px-4 py-4 transition-transform duration-200 hover:-translate-y-0.5 hover:border-white/15"
            >
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="outline">{item.source}</Badge>
                  <Badge variant={sentimentVariant(item.sentiment)}>{item.sentiment}</Badge>
                  {item.related_asset ? <Badge variant="secondary">{item.related_asset}</Badge> : null}
                </div>
                <h3 className="mt-3 text-sm font-semibold leading-6 text-[var(--text-primary)] group-hover:text-white">{item.title}</h3>
              </div>

              <div className="flex items-center justify-between gap-3 text-xs text-[var(--text-muted)]">
                <span>{item.relative_time}</span>
                <ExternalLink className="h-3.5 w-3.5 transition-transform duration-200 group-hover:translate-x-0.5" />
              </div>
            </a>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
