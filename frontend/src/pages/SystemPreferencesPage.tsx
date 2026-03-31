import { useEffect, useState, type FormEvent } from 'react'
import { Shield, KeyRound, Trash2 } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/use-toast'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'

type SystemPreferencesResponse = {
  minimax_api_key_configured: boolean
  minimax_api_key_masked: string | null
  signal_history_min_confidence: number
  signal_history_min_reward_risk: number
  signal_history_max_reward_risk: number
  signal_history_min_rsi: number
  signal_history_max_rsi: number
  signal_history_allow_neutral_macd: boolean
  signal_history_allow_buy: boolean
  signal_history_allow_sell: boolean
  signal_history_allow_conservative: boolean
  signal_history_allow_moderate: boolean
  signal_history_allow_aggressive: boolean
}

export default function SystemPreferencesPage() {
  const { toast } = useToast()
  const [data, setData] = useState<SystemPreferencesResponse | null>(null)
  const [minimaxApiKey, setMinimaxApiKey] = useState('')
  const [signalHistoryMinConfidence, setSignalHistoryMinConfidence] = useState(55)
  const [signalHistoryMinRewardRisk, setSignalHistoryMinRewardRisk] = useState(1.2)
  const [signalHistoryMaxRewardRisk, setSignalHistoryMaxRewardRisk] = useState(5)
  const [signalHistoryMinRsi, setSignalHistoryMinRsi] = useState(30)
  const [signalHistoryMaxRsi, setSignalHistoryMaxRsi] = useState(34)
  const [signalHistoryAllowNeutralMacd, setSignalHistoryAllowNeutralMacd] = useState(true)
  const [signalHistoryAllowBuy, setSignalHistoryAllowBuy] = useState(true)
  const [signalHistoryAllowSell, setSignalHistoryAllowSell] = useState(false)
  const [signalHistoryAllowConservative, setSignalHistoryAllowConservative] = useState(false)
  const [signalHistoryAllowModerate, setSignalHistoryAllowModerate] = useState(true)
  const [signalHistoryAllowAggressive, setSignalHistoryAllowAggressive] = useState(true)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setIsLoading(true)
      const response = await authFetch(`${API_BASE_URL}/system/preferences`)
      if (!response.ok) {
        throw new Error(`Falha ao carregar preferências do sistema (${response.status})`)
      }
      const payload = await response.json() as SystemPreferencesResponse
      if (!cancelled) {
        setData(payload)
        setSignalHistoryMinConfidence(payload.signal_history_min_confidence)
        setSignalHistoryMinRewardRisk(payload.signal_history_min_reward_risk)
        setSignalHistoryMaxRewardRisk(payload.signal_history_max_reward_risk)
        setSignalHistoryMinRsi(payload.signal_history_min_rsi)
        setSignalHistoryMaxRsi(payload.signal_history_max_rsi)
        setSignalHistoryAllowNeutralMacd(payload.signal_history_allow_neutral_macd)
        setSignalHistoryAllowBuy(payload.signal_history_allow_buy)
        setSignalHistoryAllowSell(payload.signal_history_allow_sell)
        setSignalHistoryAllowConservative(payload.signal_history_allow_conservative)
        setSignalHistoryAllowModerate(payload.signal_history_allow_moderate)
        setSignalHistoryAllowAggressive(payload.signal_history_allow_aggressive)
        setIsLoading(false)
      }
    }

    load().catch((error: unknown) => {
      if (!cancelled) {
        setIsLoading(false)
        toast({
          variant: 'destructive',
          title: 'Erro ao carregar preferências',
          description: error instanceof Error ? error.message : 'Erro inesperado',
        })
      }
    })

    return () => {
      cancelled = true
    }
  }, [toast])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setIsSaving(true)
    try {
      const response = await authFetch(`${API_BASE_URL}/system/preferences`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          minimax_api_key: minimaxApiKey.trim() || undefined,
          signal_history_min_confidence: signalHistoryMinConfidence,
          signal_history_min_reward_risk: signalHistoryMinRewardRisk,
          signal_history_max_reward_risk: signalHistoryMaxRewardRisk,
          signal_history_min_rsi: signalHistoryMinRsi,
          signal_history_max_rsi: signalHistoryMaxRsi,
          signal_history_allow_neutral_macd: signalHistoryAllowNeutralMacd,
          signal_history_allow_buy: signalHistoryAllowBuy,
          signal_history_allow_sell: signalHistoryAllowSell,
          signal_history_allow_conservative: signalHistoryAllowConservative,
          signal_history_allow_moderate: signalHistoryAllowModerate,
          signal_history_allow_aggressive: signalHistoryAllowAggressive,
        }),
      })
      if (!response.ok) {
        throw new Error(`Falha ao salvar preferências do sistema (${response.status})`)
      }
      const payload = await response.json() as SystemPreferencesResponse
      setData(payload)
      setMinimaxApiKey('')
      setSignalHistoryMinConfidence(payload.signal_history_min_confidence)
      setSignalHistoryMinRewardRisk(payload.signal_history_min_reward_risk)
      setSignalHistoryMaxRewardRisk(payload.signal_history_max_reward_risk)
      setSignalHistoryMinRsi(payload.signal_history_min_rsi)
      setSignalHistoryMaxRsi(payload.signal_history_max_rsi)
      setSignalHistoryAllowNeutralMacd(payload.signal_history_allow_neutral_macd)
      setSignalHistoryAllowBuy(payload.signal_history_allow_buy)
      setSignalHistoryAllowSell(payload.signal_history_allow_sell)
      setSignalHistoryAllowConservative(payload.signal_history_allow_conservative)
      setSignalHistoryAllowModerate(payload.signal_history_allow_moderate)
      setSignalHistoryAllowAggressive(payload.signal_history_allow_aggressive)
      toast({
        title: 'Preferências atualizadas',
        description: 'As preferências do sistema foram salvas.',
      })
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Erro ao salvar',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async () => {
    setIsDeleting(true)
    try {
      const response = await authFetch(`${API_BASE_URL}/system/preferences`, { method: 'DELETE' })
      if (!response.ok) {
        throw new Error(`Falha ao remover preferências do sistema (${response.status})`)
      }
      setData((current) => current ? { ...current, minimax_api_key_configured: false, minimax_api_key_masked: null } : null)
      setMinimaxApiKey('')
      toast({
        title: 'API key removida',
        description: 'A MiniMax API key foi apagada das preferências do sistema.',
      })
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Erro ao remover',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <div className="app-page space-y-6 pb-20">
      <section className="page-card p-6 sm:p-7 lg:p-8">
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-3xl border border-amber-300/20 bg-[linear-gradient(135deg,rgba(245,158,11,0.18),rgba(56,189,248,0.12))]">
            <Shield className="h-6 w-6 text-amber-200" />
          </div>
          <div>
            <div className="eyebrow">
              <span>Sistema</span>
            </div>
            <h1 className="section-title mt-2">Preferências do sistema</h1>
            <p className="section-copy mt-2">
              Área administrativa para configurar segredos e preferências globais usadas pelos serviços internos.
            </p>
          </div>
        </div>
      </section>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">MiniMax</div>
              <h2 className="mt-2 text-xl font-semibold text-[var(--text-primary)]">API do MiniMax</h2>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">
                Essa chave será usada pelo backend para traduzir e resumir notícias no AI Dashboard.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-3">
              <KeyRound className="h-5 w-5 text-sky-200" />
            </div>
          </div>

          <div className="mt-5 page-card-muted px-4 py-3 text-sm text-[var(--text-secondary)]">
            {isLoading ? 'Carregando status atual…' : data?.minimax_api_key_configured
              ? `Chave configurada: ${data.minimax_api_key_masked ?? 'mascarada'}`
              : 'Nenhuma chave configurada no sistema.'}
          </div>

          <form onSubmit={handleSubmit} className="mt-5 space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                API Key
              </label>
              <input
                type="password"
                value={minimaxApiKey}
                onChange={(event) => setMinimaxApiKey(event.target.value)}
                placeholder="Cole a chave da MiniMax"
                className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
              />
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit" loading={isSaving}>
                Salvar API do MiniMax
              </Button>
              <Button type="button" variant="ghost" loading={isDeleting} onClick={handleDelete} icon={<Trash2 className="h-4 w-4" />}>
                Remover chave
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Sinais</div>
              <h2 className="mt-2 text-xl font-semibold text-[var(--text-primary)]">Gate do histórico</h2>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">
                Ajusta o filtro de qualidade antes de gravar sinais no histórico.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-3">
              <Shield className="h-5 w-5 text-emerald-200" />
            </div>
          </div>

          <form onSubmit={handleSubmit} className="mt-5 space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  Confiança mínima
                </label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={signalHistoryMinConfidence}
                  onChange={(event) => setSignalHistoryMinConfidence(Number(event.target.value))}
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  Reward/Risk mínimo
                </label>
                <input
                  type="number"
                  min={0.1}
                  max={20}
                  step={0.1}
                  value={signalHistoryMinRewardRisk}
                  onChange={(event) => setSignalHistoryMinRewardRisk(Number(event.target.value))}
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  Reward/Risk máximo
                </label>
                <input
                  type="number"
                  min={0.1}
                  max={20}
                  step={0.1}
                  value={signalHistoryMaxRewardRisk}
                  onChange={(event) => setSignalHistoryMaxRewardRisk(Number(event.target.value))}
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  RSI mínimo
                </label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  step={0.1}
                  value={signalHistoryMinRsi}
                  onChange={(event) => setSignalHistoryMinRsi(Number(event.target.value))}
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  RSI máximo
                </label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  step={0.1}
                  value={signalHistoryMaxRsi}
                  onChange={(event) => setSignalHistoryMaxRsi(Number(event.target.value))}
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>
            </div>

            <label className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-[var(--text-primary)]">
              <input
                type="checkbox"
                checked={signalHistoryAllowNeutralMacd}
                onChange={(event) => setSignalHistoryAllowNeutralMacd(event.target.checked)}
                className="h-4 w-4 rounded border-white/20 bg-transparent accent-emerald-400"
              />
              Permitir sinais com MACD neutro
            </label>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-3 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-4">
                <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Tipos permitidos</div>
                <label className="flex items-center gap-3 text-sm text-[var(--text-primary)]">
                  <input type="checkbox" checked={signalHistoryAllowBuy} onChange={(event) => setSignalHistoryAllowBuy(event.target.checked)} className="h-4 w-4 rounded border-white/20 bg-transparent accent-emerald-400" />
                  BUY
                </label>
                <label className="flex items-center gap-3 text-sm text-[var(--text-primary)]">
                  <input type="checkbox" checked={signalHistoryAllowSell} onChange={(event) => setSignalHistoryAllowSell(event.target.checked)} className="h-4 w-4 rounded border-white/20 bg-transparent accent-emerald-400" />
                  SELL
                </label>
              </div>

              <div className="space-y-3 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-4">
                <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Perfis permitidos</div>
                <label className="flex items-center gap-3 text-sm text-[var(--text-primary)]">
                  <input type="checkbox" checked={signalHistoryAllowConservative} onChange={(event) => setSignalHistoryAllowConservative(event.target.checked)} className="h-4 w-4 rounded border-white/20 bg-transparent accent-emerald-400" />
                  Conservative
                </label>
                <label className="flex items-center gap-3 text-sm text-[var(--text-primary)]">
                  <input type="checkbox" checked={signalHistoryAllowModerate} onChange={(event) => setSignalHistoryAllowModerate(event.target.checked)} className="h-4 w-4 rounded border-white/20 bg-transparent accent-emerald-400" />
                  Moderate
                </label>
                <label className="flex items-center gap-3 text-sm text-[var(--text-primary)]">
                  <input type="checkbox" checked={signalHistoryAllowAggressive} onChange={(event) => setSignalHistoryAllowAggressive(event.target.checked)} className="h-4 w-4 rounded border-white/20 bg-transparent accent-emerald-400" />
                  Aggressive
                </label>
              </div>
            </div>

            <div className="page-card-muted px-4 py-3 text-sm text-[var(--text-secondary)]">
              O histórico só grava sinais que passam o perfil calibrado atual: BUY, perfis moderate/aggressive, RSI entre 30 e 34, confiança mínima 55 e RR entre 1.2 e 5.0.
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit" loading={isSaving}>
                Salvar gate dos sinais
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
