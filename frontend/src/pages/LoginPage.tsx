import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Eye, EyeOff, TrendingUp } from 'lucide-react'
import { useAuth } from '@/stores/authStore'

type Mode = 'login' | 'register'

interface FormErrors {
  email?: string
  password?: string
  name?: string
  general?: string
}

const PASSWORDLESS_EMAIL = 'o.alan.silva@gmail.com'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, register, user, isLoading: authLoading } = useAuth()

  const [mode, setMode] = useState<Mode>('login')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const normalizedEmail = email.trim().toLowerCase()
  const isPasswordlessLogin = mode === 'login' && normalizedEmail === PASSWORDLESS_EMAIL

  useEffect(() => {
    if (!authLoading && user) {
      navigate('/', { replace: true })
    }
  }, [authLoading, navigate, user])

  useEffect(() => {
    if (isPasswordlessLogin && password) {
      setPassword('')
    }
  }, [isPasswordlessLogin, password])

  const toggleMode = (nextMode: Mode) => {
    setMode(nextMode)
    setErrors({})
    setEmail('')
    setPassword('')
    setName('')
    setConfirmPassword('')
  }

  const validate = (): boolean => {
    const nextErrors: FormErrors = {}
    if (!email) nextErrors.email = 'Email e obrigatorio'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) nextErrors.email = 'Email invalido'

    if (!isPasswordlessLogin) {
      if (!password) nextErrors.password = 'Senha e obrigatoria'
      else if (password.length < 8) nextErrors.password = 'Senha deve ter pelo menos 8 caracteres'
    }

    if (mode === 'register') {
      if (!name.trim()) nextErrors.name = 'Nome e obrigatorio'
      if (password !== confirmPassword) nextErrors.password = 'As senhas nao coincidem'
    }

    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!validate()) return

    setIsLoading(true)
    setErrors({})

    try {
      if (mode === 'login') {
        await login(email, isPasswordlessLogin ? '' : password)
      } else {
        await register(name, email, password)
      }
      navigate('/', { replace: true })
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail || 'Erro de conexao'
        setErrors({ general: Array.isArray(detail) ? detail.join(', ') : String(detail) })
      } else {
        setErrors({ general: 'Erro inesperado' })
      }
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
          <h1 className="text-xl font-bold text-[var(--text-primary)]">
            {mode === 'login' ? 'Bem-vindo de volta' : 'Criar conta'}
          </h1>
          <p className="text-center text-sm text-[var(--text-muted)]">
            {mode === 'login'
              ? 'Entre com suas credenciais para continuar'
              : 'Preencha os dados para criar sua conta'}
          </p>
        </div>

        <div className="mb-6 flex rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-secondary)] p-1">
          <button
            type="button"
            onClick={() => toggleMode('login')}
            className={`flex-1 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all ${
              mode === 'login'
                ? 'bg-[var(--accent-primary)] text-white shadow-lg'
                : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
            }`}
          >
            Entrar
          </button>
          <button
            type="button"
            onClick={() => toggleMode('register')}
            className={`flex-1 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all ${
              mode === 'register'
                ? 'bg-[var(--accent-primary)] text-white shadow-lg'
                : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
            }`}
          >
            Criar Conta
          </button>
        </div>

        {errors.general && (
          <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {mode === 'register' && (
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                Nome
              </label>
              <input
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Seu nome completo"
                className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
              />
              {errors.name && <p className="text-xs text-red-400">{errors.name}</p>}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="seu@email.com"
              autoComplete="email"
              className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
            />
            {errors.email && <p className="text-xs text-red-400">{errors.email}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
              Senha
            </label>
            {isPasswordlessLogin && (
              <p className="text-xs text-[var(--text-muted)]">
                Este email entra sem senha e o campo nao persiste credencial.
              </p>
            )}
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="••••••••"
                autoComplete={isPasswordlessLogin ? 'off' : mode === 'login' ? 'current-password' : 'new-password'}
                data-form-type={isPasswordlessLogin ? 'other' : 'password'}
                disabled={isPasswordlessLogin}
                readOnly={isPasswordlessLogin}
                className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 pr-11 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
              />
              {!isPasswordlessLogin && (
                <button
                  type="button"
                  onClick={() => setShowPassword((value) => !value)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                  aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              )}
            </div>
            {errors.password && <p className="text-xs text-red-400">{errors.password}</p>}
          </div>

          {mode === 'register' && (
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                Confirmar Senha
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="••••••••"
                  autoComplete="new-password"
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 pr-11 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword((value) => !value)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                  aria-label={showConfirmPassword ? 'Ocultar confirmacao de senha' : 'Mostrar confirmacao de senha'}
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
          )}

          {mode === 'login' && (
            <div className="text-right">
              <Link
                to="/forgot-password"
                className="text-xs font-medium text-[var(--accent-primary)] hover:underline"
              >
                Esqueci minha senha
              </Link>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-xl bg-[linear-gradient(135deg,rgba(38,194,129,0.95),rgba(56,189,248,0.95))] py-3.5 text-sm font-bold text-white shadow-lg transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                {mode === 'login' ? 'Entrando...' : 'Criando conta...'}
              </span>
            ) : mode === 'login' ? (
              'Entrar'
            ) : (
              'Criar Conta'
            )}
          </button>
        </form>
      </div>

      <div className="mt-6 text-center">
        <Link
          to="/"
          className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] transition"
        >
          ← Voltar para o Playground
        </Link>
      </div>
    </div>
  )
}
