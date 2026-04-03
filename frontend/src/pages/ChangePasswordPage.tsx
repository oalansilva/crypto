import { useState, type FormEvent } from 'react'
import { KeyRound, LockKeyhole } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/components/ui/use-toast'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'

export default function ChangePasswordPage() {
  const { toast } = useToast()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [errors, setErrors] = useState<{ newPassword?: string; confirmPassword?: string }>({})

  const validate = () => {
    const nextErrors: { newPassword?: string; confirmPassword?: string } = {}
    if (newPassword.length < 8) {
      nextErrors.newPassword = 'A nova senha deve ter ao menos 8 caracteres.'
    }
    if (newPassword !== confirmPassword) {
      nextErrors.confirmPassword = 'As senhas não coincidem.'
    }
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!validate()) return

    setIsSaving(true)
    try {
      const response = await authFetch(`${API_BASE_URL}/users/password`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          currentPassword,
          newPassword,
        }),
      })
      if (!response.ok) {
        const payload = await response.json().catch(() => null) as { detail?: string } | null
        throw new Error(payload?.detail || `Falha ao alterar senha (${response.status})`)
      }

      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setErrors({})
      toast({
        title: 'Senha atualizada',
        description: 'Sua senha foi alterada com sucesso.',
      })
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Erro ao alterar senha',
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
          <div className="flex h-14 w-14 items-center justify-center rounded-3xl border border-amber-300/20 bg-[linear-gradient(135deg,rgba(245,158,11,0.18),rgba(56,189,248,0.12))]">
            <KeyRound className="h-6 w-6 text-amber-100" />
          </div>
          <div>
            <div className="eyebrow">
              <span>Segurança</span>
            </div>
            <h1 className="section-title mt-2">Alterar Senha</h1>
            <p className="section-copy mt-2">
              Confirme sua senha atual e defina uma nova senha com pelo menos 8 caracteres.
            </p>
          </div>
        </div>
      </section>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="mx-auto max-w-2xl space-y-4">
            <Input
              label="Senha atual"
              type="password"
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
              placeholder="Digite sua senha atual"
              icon={<LockKeyhole className="h-4 w-4" />}
              required
            />
            <Input
              label="Nova senha"
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              placeholder="Digite a nova senha"
              icon={<KeyRound className="h-4 w-4" />}
              error={errors.newPassword}
              required
            />
            <Input
              label="Confirmar nova senha"
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="Repita a nova senha"
              icon={<KeyRound className="h-4 w-4" />}
              error={errors.confirmPassword}
              required
            />

            <div className="page-card-muted px-4 py-3 text-sm text-[var(--text-secondary)]">
              Dica: use uma senha única com mistura de letras, números e símbolos.
            </div>

            <div className="flex justify-end">
              <Button type="submit" loading={isSaving} icon={<KeyRound className="h-4 w-4" />}>
                Atualizar senha
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
