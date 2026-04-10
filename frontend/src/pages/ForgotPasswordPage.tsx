import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { CheckCircle, Mail, TrendingUp } from 'lucide-react'
import { apiUrl } from '@/lib/apiBase'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sent, setSent] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!email) return

    setIsLoading(true)

    try {
      await axios.post(apiUrl('/auth/forgot-password').toString(), { email })
      setSent(true)
    } catch {
      setSent(true)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md">
      <div className="rounded-3xl border border-[var(--border-default)] bg-[linear-gradient(135deg,rgba(10,21,33,0.95),rgba(11,23,36,0.95))] p-8 shadow-[0_24px_60px_rgba(0,0,0,0.5)] backdrop-blur-xl">
        <div className="mb-8 flex flex-col items-center gap-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-emerald-300/20 bg-[linear-gradient(135deg,rgba(38,194,129,0.95),rgba(56,189,248,0.95))] shadow-[0_12px_24px_rgba(18,154,125,0.24)]">
            <TrendingUp className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-xl font-bold text-[var(--text-primary)]">Recuperar Senha</h1>
          <p className="text-center text-sm text-[var(--text-muted)]">
            {sent
              ? 'Verifique sua caixa de entrada'
              : 'Digite seu email para receber o link de recuperacao'}
          </p>
        </div>

        {sent ? (
          <div className="flex flex-col items-center gap-4 py-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/10">
              <CheckCircle className="h-8 w-8 text-emerald-400" />
            </div>
            <p className="text-center text-sm text-[var(--text-secondary)]">
              Se o email <strong className="text-[var(--text-primary)]">{email}</strong> estiver
              cadastrado, voce recebera um link para redefinir sua senha.
            </p>
            <p className="text-center text-xs text-[var(--text-muted)]">
              Este e um ambiente de demonstracao. O link foi registrado no servidor.
            </p>
            <Link
              to="/login"
              className="mt-2 inline-flex items-center gap-2 rounded-xl bg-[var(--accent-primary)] px-6 py-3 text-sm font-bold text-white transition hover:brightness-110"
            >
              Voltar ao Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="seu@email.com"
                  required
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] py-3 pl-11 pr-4 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || !email}
              className="w-full rounded-xl bg-[linear-gradient(135deg,rgba(38,194,129,0.95),rgba(56,189,248,0.95))] py-3.5 text-sm font-bold text-white shadow-lg transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Enviando...
                </span>
              ) : (
                'Enviar Link de Recuperacao'
              )}
            </button>
          </form>
        )}
      </div>

      <div className="mt-6 text-center">
        <Link
          to="/login"
          className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] transition"
        >
          ← Voltar ao Login
        </Link>
      </div>
    </div>
  )
}
