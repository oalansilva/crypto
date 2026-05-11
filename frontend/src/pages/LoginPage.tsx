import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '@/stores/authStore'
import axios from 'axios'
import { Eye, EyeOff } from 'lucide-react'
import { MonitorDisclaimer } from '@/components/monitor/MonitorDisclaimer'

interface FormErrors {
  email?: string
  password?: string
  general?: string
}

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()

  const fallbackRoute = '/monitor'
  const destination = ((location.state as { returnTo?: string } | null)?.returnTo || fallbackRoute).trim() || fallbackRoute

  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})

  // Form fields
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const validate = (): boolean => {
    const errs: FormErrors = {}
    const normalizedEmail = email.trim().toLowerCase()
    if (!email) errs.email = 'Email é obrigatório'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errs.email = 'Email inválido'
    if (!password) errs.password = 'Senha é obrigatória'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setIsLoading(true)
    setErrors({})

    try {
      const user = await login(email, password)
      navigate(user.mustChangePassword ? '/change-password' : destination, { replace: true })
    } catch (err: unknown) {
      setIsLoading(false)
      if (axios.isAxiosError(err)) {
        const responseData = err.response?.data
        const detail =
          typeof responseData === 'string'
            ? responseData
            : Array.isArray(responseData?.detail)
              ? responseData.detail.join(', ')
              : responseData?.detail

        const msg =
          detail ||
          (err.response?.status ? `Falha no login (${err.response.status})` : null) ||
          err.message ||
          'Erro de conexao'

        setErrors({ general: String(msg) })
      } else {
        setErrors({ general: 'Erro inesperado' })
      }
    }
  }

  return (
    <div className="w-full max-w-md">
      <MonitorDisclaimer className="mb-4" />

      {/* Card */}
      <div className="rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] p-8 shadow-[var(--shadow-xl)] backdrop-blur-xl">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center gap-3">
          <img
            src="/brand/cripto-farol-logo-v6-transparent.svg"
            alt="Cripto Farol"
            className="h-16 w-[220px] object-contain"
          />
          <h1 className="text-xl font-bold text-[var(--text-primary)]">
            Bem-vindo de volta
          </h1>
          <p className="text-center text-sm text-[var(--text-muted)]">
            Entre com suas credenciais para continuar
          </p>
        </div>

        {/* General Error */}
        {errors.general && (
          <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {errors.general}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.com"
              autoComplete="email"
              className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
            />
            {errors.email && <p className="text-xs text-red-400">{errors.email}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
              Senha
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 pr-11 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.password && <p className="text-xs text-red-400">{errors.password}</p>}
          </div>

          <div className="text-right">
            <Link
              to="/forgot-password"
              className="text-xs font-medium text-[var(--accent-primary)] hover:underline"
            >
              Esqueci minha senha
            </Link>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-md bg-[var(--accent-primary)] py-3.5 text-sm font-bold text-[var(--text-on-primary)] shadow-lg transition hover:bg-[var(--accent-primary-hover)] disabled:cursor-not-allowed disabled:bg-[var(--accent-primary-disabled)] disabled:text-[var(--text-muted)]"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Entrando...
              </span>
            ) : (
              'Entrar'
            )}
          </button>
        </form>
      </div>

    </div>
  )
}
