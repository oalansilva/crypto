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
}

export default function SystemPreferencesPage() {
  const { toast } = useToast()
  const [data, setData] = useState<SystemPreferencesResponse | null>(null)
  const [minimaxApiKey, setMinimaxApiKey] = useState('')
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
    if (!minimaxApiKey.trim()) {
      toast({
        variant: 'destructive',
        title: 'Campo obrigatório',
        description: 'Informe a API key da MiniMax antes de salvar.',
      })
      return
    }

    setIsSaving(true)
    try {
      const response = await authFetch(`${API_BASE_URL}/system/preferences`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ minimax_api_key: minimaxApiKey.trim() }),
      })
      if (!response.ok) {
        throw new Error(`Falha ao salvar preferências do sistema (${response.status})`)
      }
      const payload = await response.json() as SystemPreferencesResponse
      setData(payload)
      setMinimaxApiKey('')
      toast({
        title: 'Preferências atualizadas',
        description: 'A API key da MiniMax foi salva para uso do sistema.',
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
      setData({ minimax_api_key_configured: false, minimax_api_key_masked: null })
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
    </div>
  )
}
