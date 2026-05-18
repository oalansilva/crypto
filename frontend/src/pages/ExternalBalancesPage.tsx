import React, { useEffect, useMemo, useRef, useState } from 'react'
import { Download, Eye, EyeOff, KeyRound, RefreshCw, Search, ShieldCheck, Trash2, WalletCards } from 'lucide-react'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/use-toast'

const BINANCE_API_KEY_HELP = 'Use a API Key read-only criada na Binance. Não use e-mail ou senha da sua conta Binance.'
const BINANCE_API_SECRET_HELP = 'Use o API Secret da mesma chave read-only. O Cripto Farol não pede sua senha da Binance.'

type BalanceRow = {
  asset: string
  free: number
  locked: number
  total: number
  price_usdt?: number | null
  value_usd?: number | null
  avg_cost_usdt?: number | null
  pnl_usd?: number | null
  pnl_pct?: number | null
}

type SortKey = 'value' | 'asset' | 'pnl'

type SortSpec = {
  key: SortKey
  dir: 'asc' | 'desc'
}

const fmtUSD = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
})

function fmtNum(n: unknown, max = 8) {
  if (n === null || n === undefined) return '—'
  const v = Number(n)
  if (!Number.isFinite(v)) return '—'
  const s = v.toFixed(max)
  return s.replace(/\.0+$/, '').replace(/(\.[0-9]*?)0+$/, '$1')
}

function fmtSignedUSD(n: unknown) {
  if (n === null || n === undefined) return '—'
  const v = Number(n)
  if (!Number.isFinite(v)) return '—'
  const formatted = fmtUSD.format(Math.abs(v))
  if (v > 0) return `+${formatted}`
  if (v < 0) return `-${formatted}`
  return formatted
}

function fmtPct(n: unknown) {
  if (n === null || n === undefined) return '—'
  const v = Number(n)
  if (!Number.isFinite(v)) return '—'
  return `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`
}

function formatAsOf(asOf: string | null) {
  if (!asOf) return null
  const d = new Date(asOf)
  if (Number.isNaN(d.getTime())) return asOf
  return d
    .toISOString()
    .replace('T', ' ')
    .replace(/\.\d{3}Z$/, ' UTC')
}

function assetName(asset: string) {
  const names: Record<string, string> = {
    BTC: 'Bitcoin',
    ETH: 'Ethereum',
    USDT: 'Tether USD',
    SOL: 'Solana',
    BNB: 'BNB',
    ADA: 'Cardano',
  }
  return names[asset.toUpperCase()] || 'Spot balance'
}

function assetTileStyle(asset: string): React.CSSProperties {
  const symbol = asset.toUpperCase()
  const gradients: Record<string, string> = {
    BTC: 'linear-gradient(135deg, #f7931a 0%, #8b5108 100%)',
    ETH: 'linear-gradient(135deg, #627eea 0%, #2a3d8b 100%)',
    USDT: 'linear-gradient(135deg, #26a17b 0%, #0f4a37 100%)',
    SOL: 'linear-gradient(135deg, #9945ff 0%, #14f195 100%)',
    BNB: 'linear-gradient(135deg, #f3ba2f 0%, #7b5d14 100%)',
    ADA: 'linear-gradient(135deg, #2f66ff 0%, #092776 100%)',
  }
  return { background: gradients[symbol] || 'linear-gradient(135deg, #38bdf8 0%, #145374 100%)' }
}

function parseSort(v: string): SortSpec {
  switch (v) {
    case 'value_asc':
      return { key: 'value', dir: 'asc' }
    case 'value_desc':
      return { key: 'value', dir: 'desc' }
    case 'asset_desc':
      return { key: 'asset', dir: 'desc' }
    case 'asset_asc':
      return { key: 'asset', dir: 'asc' }
    case 'pnl_asc':
      return { key: 'pnl', dir: 'asc' }
    case 'pnl_desc':
      return { key: 'pnl', dir: 'desc' }
    default:
      return { key: 'value', dir: 'desc' }
  }
}

function cmp(a: BalanceRow, b: BalanceRow, s: SortSpec) {
  const dir = s.dir === 'asc' ? 1 : -1

  if (s.key === 'asset') return dir * String(a.asset || '').localeCompare(String(b.asset || ''))

  if (s.key === 'pnl') {
    const ap = a.pnl_usd
    const bp = b.pnl_usd
    if (ap == null && bp == null) return 0
    if (ap == null) return 1
    if (bp == null) return -1
    return dir * (Number(ap) - Number(bp))
  }

  const av = Number(a.value_usd)
  const bv = Number(b.value_usd)
  const aHas = Number.isFinite(av)
  const bHas = Number.isFinite(bv)
  if (!aHas && !bHas) return 0
  if (!aHas) return 1
  if (!bHas) return -1
  return dir * (av - bv)
}

export default function ExternalBalancesPage() {
  const { toast } = useToast()

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [balances, setBalances] = useState<BalanceRow[]>([])
  const [serverTotalUsd, setServerTotalUsd] = useState<number | null>(null)
  const [asOf, setAsOf] = useState<string | null>(null)
  const [credentialsConfigured, setCredentialsConfigured] = useState<boolean | null>(null)
  const [maskedApiKey, setMaskedApiKey] = useState<string | null>(null)
  const [apiKeyInput, setApiKeyInput] = useState('')
  const [apiSecretInput, setApiSecretInput] = useState('')
  const [showApiSecret, setShowApiSecret] = useState(false)
  const [savingCredentials, setSavingCredentials] = useState(false)

  const [q, setQ] = useState('')
  const [minUsd, setMinUsd] = useState<string>('0.02')
  const [sortValue, setSortValue] = useState<string>('value_desc')
  const [sortOverride, setSortOverride] = useState<SortSpec | null>(null)

  const lastFetchId = useRef(0)

  const load = async (/* opts?: { minUsdOverride?: string } */) => {
    const fetchId = ++lastFetchId.current
    setLoading(true)
    setError(null)

    try {
      const res = await authFetch(`${API_BASE_URL}/external/binance/spot/balances`)
      const payload = await res.json()
      if (!res.ok) throw new Error(String(payload?.detail || 'Falha ao carregar saldos externos'))
      if (fetchId !== lastFetchId.current) return
      setBalances((payload?.balances || []) as BalanceRow[])
      setServerTotalUsd(typeof payload?.total_usd === 'number' ? payload.total_usd : null)
      setAsOf(typeof payload?.as_of === 'string' ? payload.as_of : null)
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Falha ao carregar saldos.'
      setError(msg)
      toast({ title: 'Erro', description: msg, variant: 'destructive' })
    } finally {
      if (fetchId === lastFetchId.current) setLoading(false)
    }
  }

  const loadCredentialStatus = async () => {
    try {
      const res = await authFetch(`${API_BASE_URL}/user/binance-credentials`)
      const payload = await res.json()
      if (!res.ok) throw new Error(String(payload?.detail || 'Falha ao carregar status das credenciais'))
      setCredentialsConfigured(Boolean(payload?.configured))
      setMaskedApiKey(typeof payload?.api_key_masked === 'string' ? payload.api_key_masked : null)
    } catch {
      setCredentialsConfigured(null)
    }
  }

  useEffect(() => {
    void loadCredentialStatus()
    void load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const t = setTimeout(() => {
      void load()
    }, 320)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [minUsd])

  useEffect(() => {
    const onRefresh = () => void load()
    const onExport = () => exportCsv()
    window.addEventListener('wallet:refresh', onRefresh)
    window.addEventListener('wallet:export', onExport)
    return () => {
      window.removeEventListener('wallet:refresh', onRefresh)
      window.removeEventListener('wallet:export', onExport)
    }
  })

  const view = useMemo(() => {
    const query = q.trim().toLowerCase()
    const min = Number(minUsd)
    const minOk = Number.isFinite(min) ? min : 0

    let items = balances.slice()
    if (query) items = items.filter((it) => String(it.asset || '').toLowerCase().includes(query))
    if (Number.isFinite(min)) {
      items = items.filter((it) => {
        const v = Number(it.value_usd)
        return Number.isFinite(v) ? v >= minOk : false
      })
    }
    const s = sortOverride || parseSort(sortValue)
    items.sort((a, b) => cmp(a, b, s))

    return { items, sort: s, query }
  }, [balances, minUsd, q, sortOverride, sortValue])

  const summary = useMemo(() => {
    const totalUsd = view.items.reduce((acc, it) => acc + (Number(it.value_usd) || 0), 0)
    const pnlItems = view.items.filter((it) => typeof it.pnl_usd === 'number')
    const pnlSum = pnlItems.reduce((acc, it) => acc + (Number(it.pnl_usd) || 0), 0)
    const weightedPct =
      totalUsd > 0
        ? view.items.reduce((acc, it) => {
            const value = Number(it.value_usd) || 0
            const pct = typeof it.pnl_pct === 'number' ? Number(it.pnl_pct) : 0
            return acc + pct * (value / totalUsd)
          }, 0)
        : null

    return {
      totalUsd,
      pnlSum,
      pnlCount: pnlItems.length,
      count: view.items.length,
      weightedPct,
    }
  }, [view.items])

  const onHeaderSort = (key: SortKey) => {
    const current = sortOverride || parseSort(sortValue)
    const dir: SortSpec['dir'] = current.key === key && current.dir === 'desc' ? 'asc' : 'desc'
    setSortOverride({ key, dir })
  }

  const reset = () => {
    setQ('')
    setMinUsd('0.02')
    setSortValue('value_desc')
    setSortOverride(null)
    void load()
  }

  const exportCsv = () => {
    const headers = ['asset', 'total', 'free', 'locked', 'value_usd', 'price_usdt', 'avg_cost_usdt', 'pnl_usd', 'pnl_pct']
    const csv = [
      headers.join(','),
      ...view.items.map((row) =>
        [
          row.asset,
          row.total,
          row.free,
          row.locked,
          row.value_usd ?? '',
          row.price_usdt ?? '',
          row.avg_cost_usdt ?? '',
          row.pnl_usd ?? '',
          row.pnl_pct ?? '',
        ]
          .map((cell) => `"${String(cell ?? '').replaceAll('"', '""')}"`)
          .join(','),
      ),
    ].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'wallet-balances.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

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
      setApiSecretInput('')
      toast({ title: 'Credenciais salvas', description: 'A carteira agora usa a API key da conta logada.' })
      await load()
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Falha ao salvar credenciais.'
      setError(msg)
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
      setBalances([])
      setServerTotalUsd(null)
      setAsOf(null)
      toast({ title: 'Credenciais removidas', description: 'A carteira deste usuário foi desconectada da Binance.' })
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Falha ao remover credenciais.'
      setError(msg)
      toast({ title: 'Erro', description: msg, variant: 'destructive' })
    } finally {
      setSavingCredentials(false)
    }
  }

  const metaLine = useMemo(() => {
    const bits: string[] = []
    bits.push(`min USD: ${Number.isFinite(Number(minUsd)) ? Number(minUsd).toFixed(2) : '—'}`)
    bits.push(`sort: ${view.sort.key}/${view.sort.dir}`)
    if (view.query) bits.unshift(`busca: ${view.query.toUpperCase()}`)
    return bits.join(' · ')
  }, [minUsd, view.query, view.sort.dir, view.sort.key])

  const asOfLabel = formatAsOf(asOf)

  const rows: BalanceRow[] = loading
    ? Array.from({ length: 6 }).map((_, i) => ({ asset: `loading-${i}`, free: 0, locked: 0, total: 0 }))
    : view.items

  return (
    <main className="app-page balances-page w-full bg-[#07111a] text-slate-100">
      <div className="mx-auto w-[min(1180px,calc(100%-28px))] pb-10 pt-5 sm:pb-12">
        <section className="mb-4 flex flex-col gap-3 border-b border-white/5 pb-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-slate-400">
              <span>Workspace</span>
              <span className="text-slate-600">/</span>
              <span>Conta</span>
              <span className="text-slate-600">/</span>
              <span className="font-semibold text-slate-200">Carteira</span>
            </div>
            <h1 className="text-[30px] font-bold tracking-normal text-slate-50 lg:text-[34px]">Carteira</h1>
            <div className="mt-2 max-w-3xl text-sm text-slate-400">
              Saldos lidos da Binance Spot por chave API read-only. O Cripto Farol não solicita e-mail nem senha da Binance.
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-400">
              <span className="inline-flex items-center gap-2 rounded-md border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1 font-mono text-emerald-200">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-300 shadow-[0_0_10px_rgba(52,211,153,0.75)]" />
                Binance · read-only
              </span>
              <span>Última sincronização</span>
              <span className="font-mono text-slate-200">{asOfLabel || '—'}</span>
            </div>
          </div>

          <Button
            className="h-10 gap-2 rounded-md border border-sky-300/20 bg-sky-300 px-4 text-sm font-semibold text-slate-950 hover:bg-sky-200"
            onClick={() => void load()}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Sincronizar
          </Button>
        </section>

        <section className="mb-4 grid overflow-hidden rounded-lg border border-white/10 bg-white/10 md:grid-cols-4">
          <article className="border-b border-white/10 p-5 md:col-span-1 md:border-b-0 md:border-r">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
              Total da carteira <span className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[10px] text-slate-300">USD</span>
            </div>
            <div className="mt-2 text-[30px] font-bold tracking-normal text-slate-50">{loading ? '—' : fmtUSD.format(summary.totalUsd)}</div>
            <div className="mt-1 text-xs text-slate-500">{loading ? '—' : `${summary.count} ativos · filtro min USD ${Number(minUsd).toFixed(2)}`}</div>
          </article>
          <article className="border-b border-white/10 p-5 md:border-b-0 md:border-r">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Total USD</div>
            <div className="mt-2 text-[24px] font-bold tracking-normal text-slate-50">{loading ? '—' : summary.count}</div>
            <div className="mt-1 text-xs text-slate-500">ativos visíveis</div>
          </article>
          <article className="border-b border-white/10 p-5 md:border-b-0 md:border-r">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">PnL parcial</div>
            <div className={`mt-2 text-[24px] font-bold tracking-normal ${summary.pnlSum >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
              {loading ? '—' : summary.pnlCount ? fmtSignedUSD(summary.pnlSum) : '—'}
            </div>
            <div className="mt-1 text-xs text-slate-500">{summary.pnlCount} símbolos · com avg cost</div>
          </article>
          <article className="p-5">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Performance</div>
            <div className={`mt-2 text-[24px] font-bold tracking-normal ${(summary.weightedPct ?? 0) >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
              {loading ? '—' : summary.weightedPct == null ? '—' : fmtPct(summary.weightedPct)}
            </div>
            <div className="mt-1 text-xs text-slate-500">média ponderada</div>
          </article>
        </section>

        <section className="mb-4 rounded-lg border border-white/10 bg-[#101c2a] p-4">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-50">
                <KeyRound className="h-4 w-4 text-slate-400" />
                Credenciais Binance
              </div>
              <div className="mt-2 max-w-3xl text-sm text-slate-400">
                A Home e a carteira usam uma chave API vinculada ao usuário logado. Use permissão somente leitura e mantenha IP whitelist habilitado na Binance.
              </div>
            </div>
            <div className="inline-flex w-fit items-center gap-2 rounded-md border border-white/10 bg-slate-950/40 px-3 py-1.5 font-mono text-xs text-slate-300">
              <span className={`h-1.5 w-1.5 rounded-full ${credentialsConfigured ? 'bg-emerald-300' : 'bg-amber-300'}`} />
              {credentialsConfigured ? 'Configurada' : 'Não configurada'}
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
              <button type="button" className="rounded p-1 text-slate-500 hover:bg-white/10 hover:text-slate-200" onClick={() => setShowApiSecret((v) => !v)} aria-label="Mostrar ou ocultar secret">
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

        <section className="mb-4 grid grid-cols-1 items-end gap-3 rounded-lg border border-white/10 bg-[#101c2a] p-4 lg:grid-cols-[1.4fr_0.7fr_0.85fr_auto]">
          <label className="grid gap-1.5">
            <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Buscar</span>
            <span className="flex h-9 items-center gap-2 rounded-md border border-white/10 bg-slate-950/35 px-3 text-sm text-slate-200 focus-within:border-sky-300/50">
              <Search className="h-4 w-4 text-slate-500" />
              <input
                className="min-w-0 flex-1 appearance-none border-0 bg-transparent p-0 text-sm text-slate-100 outline-none placeholder:text-slate-600"
                placeholder="BTC, ETH, SOL..."
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
            </span>
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Dust threshold</span>
            <span className="flex h-9 items-center gap-2 rounded-md border border-white/10 bg-slate-950/35 px-3 focus-within:border-sky-300/50">
              <input
                inputMode="decimal"
                className="min-w-0 flex-1 appearance-none border-0 bg-transparent p-0 font-mono text-sm text-slate-100 outline-none"
                value={minUsd}
                onChange={(e) => setMinUsd(e.target.value)}
              />
              <span className="font-mono text-[11px] text-slate-500">USD</span>
            </span>
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Ordenar</span>
            <select
              className="h-9 appearance-none rounded-md border border-white/10 bg-slate-950/35 px-3 text-sm text-slate-100 outline-none"
              value={sortValue}
              onChange={(e) => {
                setSortValue(e.target.value)
                setSortOverride(null)
              }}
            >
              <option value="value_desc">Maior valor</option>
              <option value="value_asc">Menor valor</option>
              <option value="asset_asc">Ativo (A-Z)</option>
              <option value="asset_desc">Ativo (Z-A)</option>
              <option value="pnl_desc">PnL (maior)</option>
              <option value="pnl_asc">PnL (menor)</option>
            </select>
          </label>

          <div className="flex flex-wrap justify-start gap-2 lg:justify-end">
            <Button variant="secondary" className="h-9 rounded-md border border-white/10 bg-slate-950/35 px-3 text-xs text-slate-200 hover:bg-white/10" onClick={reset}>
              Reset filtros
            </Button>
            <Button variant="secondary" className="h-9 gap-2 rounded-md border border-white/10 bg-slate-950/35 px-3 text-xs text-slate-200 hover:bg-white/10" onClick={exportCsv}>
              <Download className="h-4 w-4" />
              Exportar CSV
            </Button>
            <div className="basis-full font-mono text-[10px] text-slate-500 lg:text-right">{metaLine}</div>
          </div>
        </section>

        <section className="overflow-hidden rounded-lg border border-white/10 bg-[#101c2a]">
          <div className="flex flex-col gap-3 border-b border-white/10 px-4 py-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-300">
                Balances <span className="font-normal normal-case tracking-normal text-slate-500">({summary.count} ativos)</span>
              </h2>
              <div className="mt-1 text-xs text-slate-500">Layout responsivo: tabela no desktop e cards no mobile.</div>
            </div>
            <div className="text-xs text-slate-500">{serverTotalUsd != null ? 'total_usd do servidor disponível' : 'total calculado das linhas visíveis'}</div>
          </div>

          {error && !loading ? (
            <div className="p-4">
              <div className="rounded-lg border border-rose-300/25 bg-rose-400/10 p-4">
                <div className="font-semibold text-rose-100">Erro ao carregar</div>
                <div className="mt-1 text-sm text-rose-100/75">{error}</div>
                <Button className="mt-3 h-9 rounded-md" variant="secondary" onClick={() => void load()}>
                  Tentar novamente
                </Button>
              </div>
            </div>
          ) : view.items.length === 0 && !loading ? (
            <div className="p-4">
              <div className="rounded-lg border border-white/10 bg-slate-950/30 p-4">
                <div className="font-semibold text-slate-100">Nada para mostrar</div>
                <div className="mt-1 text-sm text-slate-400">
                  Pode ser que todos os ativos estejam abaixo do min USD, ou que a busca não encontrou nenhum símbolo.
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="hidden overflow-x-auto md:block">
                <table className="w-full border-collapse text-sm">
                  <thead className="sticky top-0 bg-[#101c2a]">
                    <tr className="border-b border-white/10 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                      <th className="px-4 py-3 text-left">
                        <button className="hover:text-slate-200" onClick={() => onHeaderSort('asset')}>Ativo</button>
                      </th>
                      <th className="px-4 py-3 text-right">Total</th>
                      <th className="px-4 py-3 text-right">Free</th>
                      <th className="px-4 py-3 text-right">
                        <button className="hover:text-slate-200" onClick={() => onHeaderSort('value')}>Valor USD</button>
                      </th>
                      <th className="px-4 py-3 text-right">Preço</th>
                      <th className="px-4 py-3 text-right">Avg cost</th>
                      <th className="px-4 py-3 text-right">
                        <button className="hover:text-slate-200" onClick={() => onHeaderSort('pnl')}>PnL</button>
                      </th>
                      <th className="px-4 py-3 text-right">Participação</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => {
                      const value = Number(row.value_usd) || 0
                      const share = summary.totalUsd > 0 ? (value / summary.totalUsd) * 100 : 0
                      const pnlUsd = row.pnl_usd
                      const pnlColor = typeof pnlUsd === 'number' ? (pnlUsd >= 0 ? 'text-emerald-300' : 'text-rose-300') : 'text-slate-400'
                      const dust = !loading && value < 1

                      return (
                        <tr key={row.asset} className="border-b border-white/10 last:border-b-0 hover:bg-white/[0.03]" style={{ opacity: loading ? 0.65 : 1 }}>
                          <td className="px-4 py-3 text-left">
                            <div className="flex min-w-[160px] items-center gap-3">
                              <div className="grid h-8 w-8 shrink-0 place-items-center rounded-md font-mono text-xs font-semibold text-white" style={assetTileStyle(row.asset)}>
                                {String(row.asset || '—').slice(0, 3)}
                              </div>
                              <div className="min-w-0">
                                <div className="truncate font-semibold text-slate-100">
                                  {loading ? '—' : row.asset}
                                  {dust ? <><span> </span><span className="ml-2 rounded bg-white/10 px-1.5 py-0.5 font-mono text-[10px] text-slate-400">DUST</span></> : null}
                                </div>
                                <div className="truncate text-xs text-slate-500">{loading ? 'Carregando' : assetName(row.asset)}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-right font-mono text-slate-300">{loading ? '—' : fmtNum(row.total, 8)}</td>
                          <td className="px-4 py-3 text-right font-mono text-slate-400">{loading ? '—' : fmtNum(row.free, 8)}</td>
                          <td className="px-4 py-3 text-right font-mono font-semibold text-slate-100">{loading ? '—' : typeof row.value_usd === 'number' ? fmtUSD.format(row.value_usd) : '—'}</td>
                          <td className="px-4 py-3 text-right font-mono text-slate-400">{loading ? '—' : typeof row.price_usdt === 'number' ? `$${fmtNum(row.price_usdt, 6)}` : '—'}</td>
                          <td className="px-4 py-3 text-right font-mono text-slate-400">{loading ? '—' : typeof row.avg_cost_usdt === 'number' ? `$${fmtNum(row.avg_cost_usdt, 6)}` : '—'}</td>
                          <td className={`px-4 py-3 text-right font-mono ${pnlColor}`}>
                            {loading ? '—' : typeof row.pnl_usd === 'number' && typeof row.pnl_pct === 'number' ? (
                              <span className="inline-flex flex-col items-end">
                                <span>{fmtSignedUSD(row.pnl_usd)}</span>
                                <span className="text-[11px]">{fmtPct(row.pnl_pct)}</span>
                              </span>
                            ) : '—'}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <div className="font-mono text-xs text-slate-400">{loading ? '—' : `${share.toFixed(2)}%`}</div>
                            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-slate-800">
                              <div className="h-full rounded-full bg-gradient-to-r from-sky-300 to-emerald-300" style={{ width: `${Math.min(share, 100)}%` }} />
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              <div className="md:hidden">
                {rows.map((row) => {
                  const value = Number(row.value_usd) || 0
                  const share = summary.totalUsd > 0 ? (value / summary.totalUsd) * 100 : 0
                  const pnlColor = typeof row.pnl_usd === 'number' ? (row.pnl_usd >= 0 ? 'text-emerald-300' : 'text-rose-300') : 'text-slate-400'

                  return (
                    <article key={row.asset} className="border-b border-white/10 p-4 last:border-b-0" style={{ opacity: loading ? 0.65 : 1 }}>
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex min-w-0 items-center gap-3">
                          <div className="grid h-9 w-9 shrink-0 place-items-center rounded-md font-mono text-xs font-semibold text-white" style={assetTileStyle(row.asset)}>
                            {String(row.asset || '—').slice(0, 3)}
                          </div>
                          <div className="min-w-0">
                            <div className="truncate font-semibold text-slate-100">{loading ? '—' : row.asset}</div>
                            <div className="truncate text-xs text-slate-500">{loading ? 'Carregando' : assetName(row.asset)}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-mono text-base font-semibold text-slate-100">{loading ? '—' : typeof row.value_usd === 'number' ? fmtUSD.format(row.value_usd) : '—'}</div>
                          <div className="mt-0.5 font-mono text-xs text-slate-500">{loading ? '—' : `${share.toFixed(2)}%`}</div>
                        </div>
                      </div>

                      <div className="mt-3 grid grid-cols-2 gap-2">
                        <div className="rounded-md border border-white/10 bg-slate-950/30 p-3">
                          <div className="text-[11px] text-slate-500">Total</div>
                          <div className="mt-1 font-mono text-xs text-slate-200">{loading ? '—' : fmtNum(row.total, 8)}</div>
                        </div>
                        <div className="rounded-md border border-white/10 bg-slate-950/30 p-3">
                          <div className="text-[11px] text-slate-500">Free</div>
                          <div className="mt-1 font-mono text-xs text-slate-200">{loading ? '—' : fmtNum(row.free, 8)}</div>
                        </div>
                        <div className="rounded-md border border-white/10 bg-slate-950/30 p-3">
                          <div className="text-[11px] text-slate-500">Preço</div>
                          <div className="mt-1 font-mono text-xs text-slate-200">{loading ? '—' : typeof row.price_usdt === 'number' ? `$${fmtNum(row.price_usdt, 6)}` : '—'}</div>
                        </div>
                        <div className="rounded-md border border-white/10 bg-slate-950/30 p-3">
                          <div className="text-[11px] text-slate-500">PnL</div>
                          <div className={`mt-1 font-mono text-xs ${pnlColor}`}>
                            {loading ? '—' : typeof row.pnl_usd === 'number' && typeof row.pnl_pct === 'number' ? `${fmtSignedUSD(row.pnl_usd)} (${fmtPct(row.pnl_pct)})` : '—'}
                          </div>
                        </div>
                      </div>
                    </article>
                  )
                })}
              </div>

              <div className="flex flex-col gap-1 border-t border-white/10 bg-slate-950/25 px-4 py-3 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
                <div className="inline-flex items-center gap-2">
                  <WalletCards className="h-4 w-4" />
                  Carteira · {summary.count} linhas visíveis
                </div>
                <div>{asOfLabel ? `as_of ${asOfLabel}` : ''}</div>
              </div>
            </>
          )}
        </section>
      </div>
    </main>
  )
}
