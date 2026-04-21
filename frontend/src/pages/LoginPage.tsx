import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/stores/authStore'
import axios from 'axios'
import { Eye, EyeOff, TrendingUp } from 'lucide-react'

type Mode = 'login' | 'register'

interface FormErrors {
  email?: string
  password?: string
  name?: string
  general?: string
}

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, register } = useAuth()

  const [mode, setMode] = useState<Mode>('login')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})

  // Form fields
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const toggleMode = (m: Mode) => {
    setMode(m)
    setErrors({})
    setEmail('')
    setPassword('')
    setName('')
    setConfirmPassword('')
  }

  const validate = (): boolean => {
    const errs: FormErrors = {}
    if (!email) errs.email = 'Email é obrigatório'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errs.email = 'Email inválido'
    // DEV BYPASS: alan.silva@gmail.com não precisa de senha
    const bypassPassword = email.toLowerCase() === 'o.alan.silva@gmail.com'
    if (!bypassPassword) {
      if (!password) errs.password = 'Senha é obrigatória'
      else if (password.length < 8) errs.password = 'Senha deve ter pelo menos 8 caracteres'
    }
    if (mode === 'register') {
      if (!name.trim()) errs.name = 'Nome é obrigatório'
      if (password !== confirmPassword) errs.password = 'As senhas não coincidem'
    }
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setIsLoading(true)
    setErrors({})

    try {
      if (mode === 'login') {
        await login(email, password)
        navigate('/')
      } else {
        await register(name, email, password)
        navigate('/')
      }
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
      {/* Card */}
      <div className="rounded-3xl border border-[var(--border-default)] bg-[linear-gradient(135deg,rgba(10,21,33,0.95),rgba(11,23,36,0.95))] p-8 shadow-[0_24px_60px_rgba(0,0,0,0.5)] backdrop-blur-xl">
        {/* Logo */}
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

        {/* Tabs */}
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

        {/* General Error */}
        {errors.general && (
          <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {errors.general}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {mode === 'register' && (
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                Nome
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
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
              onChange={(e) => setEmail(e.target.value)}
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
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 pr-11 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
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

          {mode === 'register' && (
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                Confirmar Senha
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  autoComplete="new-password"
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 pr-11 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
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

      {/* Back link */}
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
