import { useCallback, useEffect, useRef, useState } from 'react'
import { Bell, Link2, MessageCircle } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/components/ui/use-toast'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'

type TelegramSettings = {
  telegramUsername: string | null
  telegramAlertsEnabled: boolean
  linked: boolean
  linkedAt: string | null
  usernameMismatch: boolean
  botUsername: string | null
  hasPendingLinkToken: boolean
}

type TelegramAlertsFormProps = {
  variant?: 'profile' | 'compact'
  onSettingsChange?: (settings: TelegramSettings | null) => void
}

export function TelegramAlertsForm({
  variant = 'profile',
  onSettingsChange,
}: TelegramAlertsFormProps) {
  const { toast } = useToast()
  const [settings, setSettings] = useState<TelegramSettings | null>(null)
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [linkCommand, setLinkCommand] = useState<string | null>(null)
  const hasLoadedRef = useRef(false)
  const onSettingsChangeRef = useRef(onSettingsChange)

  useEffect(() => {
    onSettingsChangeRef.current = onSettingsChange
  }, [onSettingsChange])

  const loadSettings = useCallback(async (signal?: AbortSignal) => {
    if (signal?.aborted) return
    setLoading(true)
    try {
      const res = await authFetch(
        `${API_BASE_URL}/users/me/telegram-settings`,
        signal ? { signal } : {},
      )
      if (signal?.aborted) return
      const payload = await res.json() as TelegramSettings
      if (!res.ok) throw new Error(String((payload as { detail?: string })?.detail || res.status))
      if (signal?.aborted) return
      setSettings(payload)
      hasLoadedRef.current = true
      setUsername(payload.telegramUsername ?? '')
      onSettingsChangeRef.current?.(payload)
    } catch (error: unknown) {
      if (signal?.aborted) return
      if (error instanceof DOMException && error.name === 'AbortError') return
      const isRealLogout = (() => {
        try {
          return !localStorage.getItem('auth_access_token') && !localStorage.getItem('auth_refresh_token')
        } catch {
          return false
        }
      })()
      if (hasLoadedRef.current && !isRealLogout) {
        return
      }
      setSettings(null)
      hasLoadedRef.current = false
      onSettingsChangeRef.current?.(null)
      toast({
        variant: 'destructive',
        title: 'Erro ao carregar alertas Telegram',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [toast])

  useEffect(() => {
    const controller = new AbortController()
    void loadSettings(controller.signal)
    return () => controller.abort()
  }, [loadSettings])

  const saveSettings = async (patch: Partial<{ telegramUsername: string; telegramAlertsEnabled: boolean }>) => {
    setSaving(true)
    try {
      const body: { telegramUsername?: string; telegramAlertsEnabled?: boolean } = {}
      if (patch.telegramUsername !== undefined) {
        body.telegramUsername = patch.telegramUsername.replace(/^@/, '').trim()
      } else if (patch.telegramAlertsEnabled === undefined) {
        body.telegramUsername = username.replace(/^@/, '').trim()
      }
      if (patch.telegramAlertsEnabled !== undefined) {
        body.telegramAlertsEnabled = patch.telegramAlertsEnabled
      }

      const res = await authFetch(`${API_BASE_URL}/users/me/telegram-settings`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const payload = await res.json() as TelegramSettings & { detail?: string }
      if (!res.ok) throw new Error(String(payload.detail || `Falha (${res.status})`))
      setSettings(payload)
      setUsername(payload.telegramUsername ?? '')
      onSettingsChange?.(payload)
      toast({ title: 'Preferências Telegram salvas' })
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Erro ao salvar',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    } finally {
      setSaving(false)
    }
  }

  const generateLink = async () => {
    setSaving(true)
    try {
      await saveSettings({ telegramUsername: username.replace(/^@/, '').trim() })
      const res = await authFetch(`${API_BASE_URL}/users/me/telegram-settings/link-token`, {
        method: 'POST',
      })
      const payload = await res.json() as { command?: string; detail?: string }
      if (!res.ok) throw new Error(String(payload.detail || `Falha (${res.status})`))
      setLinkCommand(payload.command ?? null)
      toast({
        title: 'Código gerado',
        description: 'Envie o comando no bot Cripto Farol para vincular.',
      })
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Erro ao gerar vínculo',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    } finally {
      setSaving(false)
    }
  }

  const shellClass = variant === 'profile' ? 'space-y-5' : 'space-y-4'

  if (loading) {
    return <div className="py-4 text-sm text-[var(--text-secondary)]">Carregando alertas Telegram...</div>
  }

  return (
    <div className={shellClass} data-testid="telegram-alerts-form">
      <div>
        <div className="eyebrow">
          <span>Notificações</span>
        </div>
        <h2 className="mt-2 flex items-center gap-2 text-lg font-semibold text-[var(--text-primary)]">
          <MessageCircle className="h-5 w-5 text-sky-300" />
          Alertas Telegram
        </h2>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">
          Receba DMs individuais quando um sinal mudar de forma relevante para a sua carteira Spot.
        </p>
      </div>

      <label className="flex items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3">
        <span className="text-sm text-[var(--text-primary)]">Receber alertas Telegram</span>
        <input
          type="checkbox"
          checked={Boolean(settings?.telegramAlertsEnabled)}
          disabled={saving}
          onChange={(event) => void saveSettings({ telegramAlertsEnabled: event.target.checked })}
          data-testid="telegram-alerts-enabled"
        />
      </label>

      <Input
        label="@username Telegram"
        value={username}
        onChange={(event) => setUsername(event.target.value.replace(/^@/, ''))}
        placeholder="seu_usuario"
        maxLength={32}
        required
      />

      <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-[var(--text-secondary)]">
        <div className="font-medium text-[var(--text-primary)]">
          Status: {settings?.linked ? 'Vinculado' : 'Não vinculado'}
        </div>
        {settings?.linkedAt ? (
          <div className="mt-1 text-xs">Vinculado em {new Date(settings.linkedAt).toLocaleString('pt-BR')}</div>
        ) : null}
        {settings?.usernameMismatch ? (
          <div className="mt-2 text-amber-300">
            O @username vinculado difere do informado aqui. Revise se necessário.
          </div>
        ) : null}
        {settings?.botUsername ? (
          <div className="mt-2 text-xs">Bot: @{settings.botUsername}</div>
        ) : null}
      </div>

      <div className="flex flex-wrap gap-3">
        <Button
          type="button"
          loading={saving}
          icon={<Bell className="h-4 w-4" />}
          onClick={() => void saveSettings({})}
        >
          Salvar @username
        </Button>
        <Button
          type="button"
          variant="secondary"
          loading={saving}
          icon={<Link2 className="h-4 w-4" />}
          onClick={() => void generateLink()}
          data-testid="telegram-generate-link"
        >
          Gerar vínculo
        </Button>
      </div>

      {linkCommand ? (
        <div className="rounded-xl border border-sky-400/30 bg-sky-400/10 px-4 py-3 text-sm">
          <div className="font-medium text-[var(--text-primary)]">Envie no bot:</div>
          <code className="mt-2 block break-all text-sky-200">{linkCommand}</code>
        </div>
      ) : null}
    </div>
  )
}

export type { TelegramSettings }
