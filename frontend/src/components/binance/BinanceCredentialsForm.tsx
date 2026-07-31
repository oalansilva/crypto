import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Eye, EyeOff, KeyRound, ShieldCheck, Trash2 } from 'lucide-react'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/components/ui/use-toast'

const BINANCE_API_KEY_HELP =
  'Use a API Key read-only criada na Binance. Não use e-mail ou senha da sua conta Binance.'
const BINANCE_API_SECRET_HELP =
  'Use o API Secret da mesma chave read-only. O Cripto Farol não pede sua senha da Binance.'

type BinanceCredentialsFormProps = {
  mode?: 'full' | 'compact'
  /** full+profile: visual alinhado ao Meu Perfil (sem painel da carteira). */
  variant?: 'wallet' | 'profile'
  onCredentialsChange?: (configured: boolean) => void
  className?: string
}

export function BinanceCredentialsForm({
  mode = 'full',
  variant = 'wallet',
  onCredentialsChange,
  className = '',
}: BinanceCredentialsFormProps) {
  const { toast } = useToast()
  const [credentialsConfigured, setCredentialsConfigured] = useState<boolean | null>(null)
  const [maskedApiKey, setMaskedApiKey] = useState<string | null>(null)
  const [apiKeyInput, setApiKeyInput] = useState('')
  const [apiSecretInput, setApiSecretInput] = useState('')
  const [showApiSecret, setShowApiSecret] = useState(false)
  const [savingCredentials, setSavingCredentials] = useState(false)
  const [loadingStatus, setLoadingStatus] = useState(true)

  const notifyChange = useCallback(
    (configured: boolean) => {
      onCredentialsChange?.(configured)
    },
    [onCredentialsChange],
  )

  const loadCredentialStatus = useCallback(async () => {
    setLoadingStatus(true)
    try {
      const res = await authFetch(`${API_BASE_URL}/user/binance-credentials`)
      const payload = await res.json()
      if (!res.ok) throw new Error(String(payload?.detail || 'Falha ao carregar status das credenciais'))
      const configured = Boolean(payload?.configured)
      setCredentialsConfigured(configured)
      setMaskedApiKey(typeof payload?.api_key_masked === 'string' ? payload.api_key_masked : null)
    } catch {
      setCredentialsConfigured(null)
      setMaskedApiKey(null)
    } finally {
      setLoadingStatus(false)
    }
  }, [])

  useEffect(() => {
    void loadCredentialStatus()
  }, [loadCredentialStatus])

  const saveCredentials = async () => {
    const apiKey = apiKeyInput.trim()
    const apiSecret = apiSecretInput.trim()
    if (apiKey.includes('@')) {
      toast({
        title: 'Use uma API Key da Binance',
        description: 'Este campo não aceita e-mail. Crie uma chave API read-only na Binance e cole a API Key aqui.',
        variant: 'destructive',
      })
      return
    }
    if (!apiKey || !apiSecret) return

    setSavingCredentials(true)
    try {
      const res = await authFetch(`${API_BASE_URL}/user/binance-credentials`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, api_secret: apiSecret }),
      })
      const payload = await res.json()
      if (!res.ok) throw new Error(String(payload?.detail || 'Falha ao salvar credenciais'))
      setCredentialsConfigured(true)
      setMaskedApiKey(typeof payload?.api_key_masked === 'string' ? payload.api_key_masked : null)
      setApiKeyInput('')
      setApiSecretInput('')
      notifyChange(true)
      toast({ title: 'Credenciais salvas', description: 'A Home e a carteira agora usam a API key da conta logada.' })
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Falha ao salvar credenciais.'
      toast({ title: 'Erro', description: msg, variant: 'destructive' })
    } finally {
      setSavingCredentials(false)
    }
  }

  const deleteCredentials = async () => {
    setSavingCredentials(true)
    try {
      const res = await authFetch(`${API_BASE_URL}/user/binance-credentials`, { method: 'DELETE' })
      if (!res.ok && res.status !== 404) {
        const payload = await res.json().catch(() => null)
        throw new Error(String(payload?.detail || 'Falha ao remover credenciais'))
      }
      setCredentialsConfigured(false)
      setMaskedApiKey(null)
      setApiKeyInput('')
      setApiSecretInput('')
      notifyChange(false)
      toast({ title: 'Credenciais removidas', description: 'A carteira deste usuário foi desconectada da Binance.' })
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Falha ao remover credenciais.'
      toast({ title: 'Erro', description: msg, variant: 'destructive' })
    } finally {
      setSavingCredentials(false)
    }
  }

  const statusLabel =
    credentialsConfigured === null && loadingStatus
      ? 'Carregando…'
      : credentialsConfigured
        ? 'Configurada'
        : 'Não configurada'

  const statusTone = credentialsConfigured ? 'bg-emerald-300' : 'bg-amber-300'

  if (mode === 'compact') {
    return (
      <section className={`rounded-lg border border-white/10 bg-[#101c2a] p-4 ${className}`.trim()}>
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-50">
              <KeyRound className="h-4 w-4 text-slate-400" />
              Credenciais Binance
            </div>
            <div className="mt-2 max-w-3xl text-sm text-slate-400">
              Gerencie a chave API read-only em Meu Perfil (menu da conta na barra). A Home e a carteira usam a chave
              vinculada ao usuário logado.
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex w-fit items-center gap-2 rounded-md border border-white/10 bg-slate-950/40 px-3 py-1.5 font-mono text-xs text-slate-300">
              <span className={`h-1.5 w-1.5 rounded-full ${statusTone}`} />
              {statusLabel}
              {maskedApiKey ? <span className="text-slate-500">· {maskedApiKey}</span> : null}
            </div>
            <Link
              to="/profile"
              className="inline-flex h-10 items-center justify-center rounded-md border border-white/10 bg-slate-950/40 px-4 text-xs font-semibold text-slate-100 hover:bg-white/10"
            >
              Configurar no Perfil
            </Link>
          </div>
        </div>
      </section>
    )
  }

  if (variant === 'profile') {
    return (
      <section className={className} aria-labelledby="binance-credentials-heading">
        <div className="min-w-0">
          <div className="eyebrow">
            <span>Integração</span>
          </div>
          <h2 id="binance-credentials-heading" className="mt-2 text-lg font-semibold text-[var(--text-primary)]">
            Credenciais Binance
          </h2>
          <p className="mt-2 max-w-2xl text-sm text-[var(--text-secondary)]">
            Chave API somente leitura vinculada à sua conta. Home e Carteira usam essa chave. Mantenha IP whitelist
            habilitado na Binance.
          </p>
        </div>

        <div
          className={[
            'mt-5 max-w-3xl rounded-lg border px-4 py-3',
            credentialsConfigured
              ? 'border-emerald-300/20 bg-emerald-400/8'
              : 'border-[var(--border-default)] bg-[var(--bg-secondary)]',
          ].join(' ')}
        >
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                Status da chave
              </div>
              <div className="mt-1.5 flex flex-wrap items-center gap-2">
                <span className={`inline-flex h-1.5 w-1.5 rounded-full ${statusTone}`} />
                <span className="text-sm font-medium text-[var(--text-primary)]">{statusLabel}</span>
              </div>
              {maskedApiKey ? (
                <div className="mt-2">
                  <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                    API Key atual
                  </div>
                  <div className="mt-1 break-all font-mono text-sm text-[var(--text-secondary)]">{maskedApiKey}</div>
                </div>
              ) : (
                <p className="mt-2 text-sm text-[var(--text-secondary)]">
                  Nenhuma chave salva. Cole API Key e Secret abaixo para conectar.
                </p>
              )}
            </div>
            {credentialsConfigured ? (
              <Button
                type="button"
                variant="secondary"
                size="sm"
                className="shrink-0 border border-rose-300/25 bg-rose-400/10 text-rose-100 hover:bg-rose-400/20"
                onClick={deleteCredentials}
                disabled={savingCredentials}
                icon={<Trash2 className="h-4 w-4" />}
              >
                Remover chave
              </Button>
            ) : null}
          </div>
        </div>

        <div className="mt-6 grid max-w-3xl gap-4" data-lpignore="true">
          <div className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--text-muted)]">
            {credentialsConfigured ? 'Substituir chave' : 'Adicionar chave'}
          </div>
          <Input
            label="API Key read-only"
            aria-label="Binance API Key read-only"
            title={BINANCE_API_KEY_HELP}
            name="binance_api_key_readonly"
            autoComplete="off"
            data-lpignore="true"
            data-1p-ignore="true"
            spellCheck={false}
            className="font-mono text-sm"
            placeholder="Cole a API Key da Binance"
            value={apiKeyInput}
            onChange={(e) => setApiKeyInput(e.target.value)}
            icon={<ShieldCheck className="h-4 w-4" />}
          />

          <div className="w-full">
            <label
              htmlFor="binance-api-secret-profile"
              className="mb-2 block text-xs font-semibold uppercase tracking-[0.08em] text-[var(--text-muted)]"
            >
              API Secret read-only
            </label>
            <div className="relative">
              <div
                aria-hidden="true"
                className="input-icon pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
              >
                <KeyRound className="h-4 w-4" />
              </div>
              <input
                id="binance-api-secret-profile"
                type={showApiSecret ? 'text' : 'password'}
                aria-label="Binance API Secret read-only"
                title={BINANCE_API_SECRET_HELP}
                name="binance_api_secret_readonly"
                autoComplete="new-password"
                data-lpignore="true"
                data-1p-ignore="true"
                spellCheck={false}
                className="input input-with-icon font-mono text-sm pr-12"
                placeholder="Cole o API Secret da mesma chave"
                value={apiSecretInput}
                onChange={(e) => setApiSecretInput(e.target.value)}
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 rounded p-1 text-[var(--text-muted)] hover:bg-[var(--bg-elevated)] hover:text-[var(--text-primary)]"
                onClick={() => setShowApiSecret((v) => !v)}
                aria-label="Mostrar ou ocultar secret"
              >
                {showApiSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </div>

        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-[var(--text-muted)]">O Cripto Farol não pede e-mail nem senha da Binance.</p>
          <Button
            type="button"
            loading={savingCredentials}
            disabled={savingCredentials || !apiKeyInput.trim() || !apiSecretInput.trim()}
            onClick={saveCredentials}
            icon={<ShieldCheck className="h-4 w-4" />}
          >
            {credentialsConfigured ? 'Atualizar credenciais' : 'Salvar credenciais'}
          </Button>
        </div>
      </section>
    )
  }

  return (
    <section className={`rounded-lg border border-white/10 bg-[#101c2a] p-4 ${className}`.trim()}>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-50">
            <KeyRound className="h-4 w-4 text-slate-400" />
            Credenciais Binance
          </div>
          <div className="mt-2 max-w-3xl text-sm text-slate-400">
            A Home e a carteira usam uma chave API vinculada ao usuário logado. Use permissão somente leitura e mantenha IP
            whitelist habilitado na Binance.
          </div>
        </div>
        <div className="inline-flex w-fit items-center gap-2 rounded-md border border-white/10 bg-slate-950/40 px-3 py-1.5 font-mono text-xs text-slate-300">
          <span className={`h-1.5 w-1.5 rounded-full ${statusTone}`} />
          {statusLabel}
          {maskedApiKey ? <span className="text-slate-500">· {maskedApiKey}</span> : null}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-3 xl:grid-cols-[1fr_1fr_auto_auto]" data-lpignore="true">
        <label className="flex h-10 items-center gap-2 rounded-md border border-white/10 bg-slate-950/35 px-3 text-sm text-slate-200 focus-within:border-sky-300/50">
          <ShieldCheck className="h-4 w-4 text-slate-500" />
          <input
            aria-label="Binance API Key read-only"
            title={BINANCE_API_KEY_HELP}
            name="binance_api_key_readonly"
            autoComplete="off"
            data-lpignore="true"
            data-1p-ignore="true"
            spellCheck={false}
            className="min-w-0 flex-1 appearance-none border-0 bg-transparent p-0 font-mono text-xs text-slate-100 outline-none placeholder:text-slate-600"
            placeholder="API Key read-only da Binance"
            value={apiKeyInput}
            onChange={(e) => setApiKeyInput(e.target.value)}
          />
        </label>
        <label className="flex h-10 items-center gap-2 rounded-md border border-white/10 bg-slate-950/35 px-3 text-sm text-slate-200 focus-within:border-sky-300/50">
          <KeyRound className="h-4 w-4 text-slate-500" />
          <input
            type={showApiSecret ? 'text' : 'password'}
            aria-label="Binance API Secret read-only"
            title={BINANCE_API_SECRET_HELP}
            name="binance_api_secret_readonly"
            autoComplete="new-password"
            data-lpignore="true"
            data-1p-ignore="true"
            spellCheck={false}
            className="min-w-0 flex-1 appearance-none border-0 bg-transparent p-0 font-mono text-xs text-slate-100 outline-none placeholder:text-slate-600"
            placeholder="API Secret da chave read-only"
            value={apiSecretInput}
            onChange={(e) => setApiSecretInput(e.target.value)}
          />
          <button
            type="button"
            className="rounded p-1 text-slate-500 hover:bg-white/10 hover:text-slate-200"
            onClick={() => setShowApiSecret((v) => !v)}
            aria-label="Mostrar ou ocultar secret"
          >
            {showApiSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </label>
        {credentialsConfigured ? (
          <Button
            variant="secondary"
            className="h-10 gap-2 rounded-md border border-rose-300/25 bg-rose-400/10 px-4 text-xs font-semibold text-rose-100 hover:bg-rose-400/20"
            onClick={deleteCredentials}
            disabled={savingCredentials}
          >
            <Trash2 className="h-4 w-4" />
            Remover credenciais
          </Button>
        ) : null}
        <Button
          className="h-10 gap-2 rounded-md border border-sky-300/20 bg-sky-300 px-4 text-xs font-semibold text-slate-950 hover:bg-sky-200"
          onClick={saveCredentials}
          disabled={savingCredentials || !apiKeyInput.trim() || !apiSecretInput.trim()}
        >
          <ShieldCheck className="h-4 w-4" />
          Salvar credenciais
        </Button>
      </div>
    </section>
  )
}
