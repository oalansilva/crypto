import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'

export type ScalpPanelState = 'off' | 'on' | 'kill' | 'nokey'

export type ScalpStatus = {
  symbol?: string
  state?: ScalpPanelState
  has_spot_key?: boolean
  jev_available?: boolean
  jev_unavailable?: boolean
  t_quote?: string
  clip_quote?: string
  inventory_btc?: string
  calibration?: { hits: number; signals: number; last_latency_s: number | null } | null
  pnl_quote?: string
  status_text?: string
  kill_banner?: boolean
  inventory_clipped?: boolean
  enabled?: boolean
}

const DEFAULT_STATUS: ScalpStatus = {
  state: 'off',
  has_spot_key: true,
  t_quote: '100',
  clip_quote: '10',
  inventory_btc: '0',
  calibration: null,
  pnl_quote: '0',
  status_text: 'Desligado — não envia ordem deste scalp. Inventário e P&L ficam visíveis.',
  kill_banner: false,
  inventory_clipped: false,
}

function parseNumber(value: string | undefined): number {
  const n = Number(String(value ?? '0').replace(',', '.'))
  return Number.isFinite(n) ? n : 0
}

function formatUsd(value: string | undefined): string {
  const n = parseNumber(value)
  const formatted = Math.abs(n).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  if (n < 0) return `−US$ ${formatted}`
  return `US$ ${formatted}`
}

function formatT(value: string | undefined): string {
  const n = parseNumber(value)
  const rounded = Math.abs(n) >= 100 ? Math.floor(n) : n
  if (Number.isInteger(rounded) || Math.abs(rounded - Math.round(rounded)) < 0.001) {
    return `US$ ${Math.round(n)}`
  }
  return formatUsd(value)
}

function formatBtc(value: string | undefined): string {
  const n = parseNumber(value)
  if (n === 0) return '0 BTC'
  return `${n.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 8 })} BTC`
}

function formatCalibration(cal: ScalpStatus['calibration']): string {
  if (!cal || !cal.signals) return '—'
  const latency = cal.last_latency_s != null ? ` · ${cal.last_latency_s}s` : ''
  return `${cal.hits}/${cal.signals}${latency}`
}

export function ScalpModule() {
  const [status, setStatus] = useState<ScalpStatus>(DEFAULT_STATUS)
  const [pending, setPending] = useState(false)

  const load = useCallback(async () => {
    try {
      const res = await authFetch(`${API_BASE_URL}/scalp/status`)
      if (!res.ok) return
      const payload = (await res.json()) as ScalpStatus
      if (payload && typeof payload === 'object') {
        setStatus({ ...DEFAULT_STATUS, ...payload })
      }
    } catch {
      /* panel stays on last known / default off */
    }
  }, [])

  useEffect(() => {
    void load()
    const id = window.setInterval(() => {
      void load()
    }, 2000)
    return () => window.clearInterval(id)
  }, [load])

  const visual: ScalpPanelState = status.state === 'nokey' || status.state === 'on' || status.state === 'kill'
    ? status.state
    : 'off'
  const checked = visual === 'on'
  const disabled = visual === 'nokey' || pending
  const pnl = parseNumber(status.pnl_quote)
  const pnlClass = pnl < 0 ? 'neg' : pnl > 0 ? 'pos' : ''

  const toggle = async () => {
    if (disabled) return
    setPending(true)
    try {
      const res = await authFetch(`${API_BASE_URL}/scalp/switch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !checked }),
      })
      const payload = (await res.json().catch(() => null)) as ScalpStatus | { detail?: string } | null
      if (!res.ok) {
        await load()
        return
      }
      if (payload && typeof payload === 'object' && 'state' in payload) {
        setStatus({ ...DEFAULT_STATUS, ...(payload as ScalpStatus) })
      } else {
        await load()
      }
    } finally {
      setPending(false)
    }
  }

  return (
    <section
      className="scalp-module"
      id="scalp-module"
      data-testid="scalp-module"
      data-state={visual}
      aria-labelledby="scalp-title"
    >
      <div className="scalp-head">
        <div>
          <h2 id="scalp-title">Scalp BTCUSDT</h2>
          <p className="scalp-sub">
            À vista · limitadora post-only que não cruza · a sua conta Binance. Um lado de cada vez. Calibração, não
            meta.
          </p>
        </div>
        <button
          className="scalp-switch"
          id="scalp-switch"
          type="button"
          role="switch"
          aria-checked={checked}
          aria-labelledby="scalp-title"
          data-testid="scalp-switch"
          disabled={disabled}
          onClick={() => {
            void toggle()
          }}
        >
          {checked ? 'Ligado' : 'Desligado'}
        </button>
      </div>
      <dl className="scalp-kpis">
        <div>
          <dt>Teto T</dt>
          <dd id="scalp-t">{formatT(status.t_quote)}</dd>
        </div>
        <div>
          <dt>Clip</dt>
          <dd>≤ US$ 10</dd>
        </div>
        <div>
          <dt>Inventário</dt>
          <dd id="scalp-inv">{formatBtc(status.inventory_btc)}</dd>
        </div>
        <div>
          <dt>Calibração</dt>
          <dd id="scalp-cal">{formatCalibration(status.calibration)}</dd>
        </div>
        <div>
          <dt>P&amp;L</dt>
          <dd id="scalp-pnl" className={pnlClass} data-testid="scalp-pnl">
            {formatUsd(status.pnl_quote)}
          </dd>
        </div>
      </dl>
      <p className="scalp-status" id="scalp-status" data-testid="scalp-status">
        {status.status_text || DEFAULT_STATUS.status_text}
        {visual === 'nokey' ? (
          <>
            {' '}
            <Link to="/profile">Meu Perfil</Link>
          </>
        ) : null}
      </p>
      <p className="scalp-banner" id="scalp-kill" data-testid="scalp-kill" hidden={visual !== 'kill'}>
        Parado por kill (−2% de T). Não religa sozinho. Ordens deste bot canceladas.
      </p>
      {status.inventory_clipped ? (
        <p className="scalp-note" data-testid="scalp-clip-note">
          Inventário clipado ao BTC livre acima do piso (fill fora deste loop não entra no P&amp;L).
        </p>
      ) : (
        <p className="scalp-note">
          Mesma chave Spot de Meu Perfil que o Operar. O Operar (clique a mercado) continua ao lado. Nunca saque. P&amp;L
          negativo tão visível quanto o positivo.
        </p>
      )}
    </section>
  )
}
