import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { Mail, CheckCircle, TrendingUp } from 'lucide-react'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!email) return

    setIsLoading(true)
    setError('')

    try {
      await axios.post('/api/auth/forgot-password', { email })
      setSent(true)
    } catch {
      // Always show success for security
      setSent(true)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md">
      <div className="rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] p-8 shadow-[var(--shadow-xl)] backdrop-blur-xl">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center gap-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl border border-[rgba(252,213,53,0.26)] bg-[var(--accent-primary)] shadow-[var(--shadow-md)]">
            <TrendingUp className="h-7 w-7 text-[var(--text-on-primary)]" />
          </div>
          <h1 className="text-xl font-bold text-[var(--text-primary)]">Recuperar Senha</h1>
          <p className="text-center text-sm text-[var(--text-muted)]">
            {sent
              ? 'Verifique sua caixa de entrada'
              : 'Digite seu email para receber o link de recuperação'}
          </p>
        </div>

        {sent ? (
          <div className="flex flex-col items-center gap-4 py-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/10">
              <CheckCircle className="h-8 w-8 text-emerald-400" />
            </div>
            <p className="text-center text-sm text-[var(--text-secondary)]">
              Se o email <strong className="text-[var(--text-primary)]">{email}</strong> estiver
              cadastrado, você receberá um link para redefinir sua senha.
            </p>
            <p className="text-center text-xs text-[var(--text-muted)]">
              (Este é um ambiente de demonstração. O link foi logged no servidor.)
            </p>
            <Link
              to="/login"
              className="mt-2 inline-flex items-center gap-2 rounded-md bg-[var(--accent-primary)] px-6 py-3 text-sm font-bold text-[var(--text-on-primary)] transition hover:bg-[var(--accent-primary-hover)]"
            >
              Voltar ao Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                {error}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@email.com"
                  required
                  className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] py-3 pl-11 pr-4 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || !email}
              className="w-full rounded-md bg-[var(--accent-primary)] py-3.5 text-sm font-bold text-[var(--text-on-primary)] shadow-lg transition hover:bg-[var(--accent-primary-hover)] disabled:cursor-not-allowed disabled:bg-[var(--accent-primary-disabled)] disabled:text-[var(--text-muted)]"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Enviando...
                </span>
              ) : (
                'Enviar Link de Recuperação'
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
