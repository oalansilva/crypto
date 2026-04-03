import { useEffect, useState, type FormEvent } from 'react'
import { CalendarClock, Mail, Save, UserRound } from 'lucide-react'

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
  const { updateUser } = useAuth()
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
          <div className="flex h-14 w-14 items-center justify-center rounded-3xl border border-emerald-300/20 bg-[linear-gradient(135deg,rgba(38,194,129,0.18),rgba(56,189,248,0.12))]">
            <UserRound className="h-6 w-6 text-emerald-100" />
          </div>
          <div>
            <div className="eyebrow">
              <span>Conta</span>
            </div>
            <h1 className="section-title mt-2">Meu Perfil</h1>
            <p className="section-copy mt-2">
              Atualize seu nome e revise as informações básicas da sua conta.
            </p>
          </div>
        </div>
      </section>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-6">
          {isLoading ? (
            <div className="py-10 text-sm text-[var(--text-secondary)]">Carregando perfil...</div>
          ) : profile ? (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(280px,0.9fr)]">
                <div className="space-y-4">
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

                <div className="space-y-3">
                  <div className="page-card-muted px-4 py-4">
                    <div className="flex items-start gap-3">
                      <CalendarClock className="mt-0.5 h-4 w-4 shrink-0 text-sky-300" />
                      <div>
                        <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Último login</div>
                        <div className="mt-1 text-sm text-[var(--text-secondary)]">{formatDateTime(profile.lastLogin)}</div>
                      </div>
                    </div>
                  </div>
                  <div className="page-card-muted px-4 py-4">
                    <div className="flex items-start gap-3">
                      <CalendarClock className="mt-0.5 h-4 w-4 shrink-0 text-emerald-300" />
                      <div>
                        <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Membro desde</div>
                        <div className="mt-1 text-sm text-[var(--text-secondary)]">{formatDateTime(profile.createdAt)}</div>
                      </div>
                    </div>
                  </div>
                  <div className="page-card-muted px-4 py-4">
                    <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">User ID</div>
                    <div className="mt-1 break-all text-sm text-[var(--text-secondary)]">{profile.id}</div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <Button type="submit" loading={isSaving} icon={<Save className="h-4 w-4" />}>
                  Salvar perfil
                </Button>
              </div>
            </form>
          ) : (
            <div className="py-10 text-sm text-[var(--text-secondary)]">Perfil indisponível.</div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
