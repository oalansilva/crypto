import { useEffect, useState, type FormEvent } from 'react'
import { CalendarClock, Mail, Save, UserRound } from 'lucide-react'

import { BinanceCredentialsForm } from '@/components/binance/BinanceCredentialsForm'
import { TelegramAlertsForm } from '@/components/telegram/TelegramAlertsForm'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/components/ui/use-toast'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'
import { useAuth } from '@/stores/authStore'

type ProfileResponse = {
  id: string
  email: string
  name: string
  createdAt: string | null
  lastLogin: string | null
}

function formatDateTime(value: string | null) {
  if (!value) return 'Nunca'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('pt-BR')
}

export default function ProfilePage() {
  const { toast } = useToast()
  const { updateUser, isLoading: authLoading } = useAuth()
  const [profile, setProfile] = useState<ProfileResponse | null>(null)
  const [name, setName] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    let cancelled = false

    const loadProfile = async () => {
      setIsLoading(true)
      const response = await authFetch(`${API_BASE_URL}/users/me`)
      if (!response.ok) {
        throw new Error(`Falha ao carregar perfil (${response.status})`)
      }
      const payload = await response.json() as ProfileResponse
      if (!cancelled) {
        setProfile(payload)
        setName(payload.name)
        setIsLoading(false)
      }
    }

    loadProfile().catch((error: unknown) => {
      if (cancelled) return
      setIsLoading(false)
      toast({
        variant: 'destructive',
        title: 'Erro ao carregar perfil',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    })

    return () => {
      cancelled = true
    }
  }, [toast])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setIsSaving(true)
    try {
      const response = await authFetch(`${API_BASE_URL}/users/me`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      })
      if (!response.ok) {
        const payload = await response.json().catch(() => null) as { detail?: string } | null
        throw new Error(payload?.detail || `Falha ao atualizar perfil (${response.status})`)
      }
      const payload = await response.json() as ProfileResponse
      setProfile(payload)
      setName(payload.name)
      updateUser({ name: payload.name })
      toast({
        title: 'Perfil atualizado',
        description: 'Seu nome foi salvo com sucesso.',
      })
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Erro ao salvar perfil',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="app-page space-y-6 pb-20">
      <section className="page-card p-6 sm:p-7 lg:p-8">
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-3xl border border-[rgba(252,213,53,0.22)] bg-[linear-gradient(135deg,rgba(252,213,53,0.16),rgba(56,189,248,0.1))]">
            <UserRound className="h-6 w-6 text-[var(--accent-primary)]" />
          </div>
          <div>
            <div className="eyebrow">
              <span>Conta</span>
            </div>
            <h1 className="section-title mt-2">Meu Perfil</h1>
            <p className="section-copy mt-2">
              Dados da conta e acesso à API da Binance em um só lugar: leitura para Home/Carteira; Spot Trade (sem saque) opcional para Operar no Monitor.
            </p>
          </div>
        </div>
      </section>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="divide-y divide-white/8 p-0">
          <section className="p-6 sm:p-7" aria-labelledby="profile-account-heading">
            {isLoading ? (
              <div className="py-8 text-sm text-[var(--text-secondary)]">Carregando perfil...</div>
            ) : profile ? (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="eyebrow">
                      <span>Identidade</span>
                    </div>
                    <h2 id="profile-account-heading" className="mt-2 text-lg font-semibold text-[var(--text-primary)]">
                      Dados da conta
                    </h2>
                    <p className="mt-2 text-sm text-[var(--text-secondary)]">
                      Atualize o nome exibido no app. O e-mail é somente leitura.
                    </p>
                  </div>
                </div>

                <div className="grid gap-4 lg:grid-cols-2">
                  <Input
                    label="Nome"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    placeholder="Seu nome"
                    maxLength={120}
                    required
                  />
                  <Input
                    label="E-mail"
                    value={profile.email}
                    readOnly
                    icon={<Mail className="h-4 w-4" />}
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="page-card-muted px-4 py-3">
                    <div className="flex items-start gap-2.5">
                      <CalendarClock className="mt-0.5 h-4 w-4 shrink-0 text-sky-300" />
                      <div className="min-w-0">
                        <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                          Último login
                        </div>
                        <div className="mt-1 truncate text-sm text-[var(--text-secondary)]">
                          {formatDateTime(profile.lastLogin)}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="page-card-muted px-4 py-3">
                    <div className="flex items-start gap-2.5">
                      <CalendarClock className="mt-0.5 h-4 w-4 shrink-0 text-emerald-300" />
                      <div className="min-w-0">
                        <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                          Membro desde
                        </div>
                        <div className="mt-1 truncate text-sm text-[var(--text-secondary)]">
                          {formatDateTime(profile.createdAt)}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="page-card-muted px-4 py-3">
                    <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                      User ID
                    </div>
                    <div className="mt-1 break-all font-mono text-xs text-[var(--text-secondary)]">{profile.id}</div>
                  </div>
                </div>

                <div className="flex justify-end border-t border-white/8 pt-5">
                  <Button type="submit" loading={isSaving} icon={<Save className="h-4 w-4" />}>
                    Salvar perfil
                  </Button>
                </div>
              </form>
            ) : (
              <div className="py-8 text-sm text-[var(--text-secondary)]">Perfil indisponível.</div>
            )}
          </section>

          <section className="p-6 sm:p-7">
            <BinanceCredentialsForm mode="full" variant="profile" />
          </section>

          <section className="p-6 sm:p-7">
            {authLoading ? (
              <div className="py-4 text-sm text-[var(--text-secondary)]">Carregando alertas Telegram...</div>
            ) : (
              <TelegramAlertsForm variant="profile" />
            )}
          </section>
        </CardContent>
      </Card>
    </div>
  )
}
