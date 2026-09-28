import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'

export type ScalpPanelState = 'off' | 'on' | 'kill' | 'nokey'

export type ScalpPosition = {
  entry_quote?: string
  age_s?: number
  target_bp?: string
  stop_bp?: string
}

export type ScalpDiagnosisHistory = {
  date?: string
  label?: string
  verb?: string
  text?: string
  decision?: string
}

export type ScalpDiagnosis = {
  closed_day?: string
  shown_on?: string
  lead?: string
  when?: string
  data_ok?: string
  until?: string
  period?: string | null
  confidence_now?: string
  regime_boundary_bp?: string | null
  regime_boundary_status?: 'configured' | 'absent'
  viability_status?: 'viable' | 'not_operable' | 'indeterminate' | 'insufficient_sample'
  barrier_measurement?: {
    candidate_count?: number
    measured_candidates?: number
    indeterminate_candidates?: number
    no_hit_candidates?: number
  } | null
  decision?: string
  verb?: string
  sample?: string
  target_stop?: string
  signal?: string
  side?: string
  reason?: string
  calibration_note?: string
  history?: ScalpDiagnosisHistory[]
  can_revert?: boolean
}

export type ScalpStatus = {
  symbol?: string
  state?: ScalpPanelState
  has_spot_key?: boolean
  jev_available?: boolean
  jev_unavailable?: boolean
  horizon_s?: number
  lookback_label?: string
  t_quote?: string
  clip_quote?: string
  inventory_btc?: string
  calibration?: { hits: number; signals: number; last_latency_s: number | null } | null
  pnl_quote?: string
  status_text?: string
  book_available?: boolean
  kill_banner?: boolean
  inventory_clipped?: boolean
  enabled?: boolean
  fee_bp?: string
  bnb_fee_active?: boolean
  hurdle_bp?: string
  exit_target_bp?: string
  exit_stop_bp?: string
  position?: ScalpPosition | null
  last_trade_bp?: string | null
  last_trade_quote?: string | null
  stuck?: boolean
  calibration_paused?: boolean
  calibration_enabled?: boolean
  confidence_version?: {
    version_n?: number
    previous?: { version_n?: number } | null
    current?: Record<string, { kind?: string; value?: string | null }>
    reason?: string
  } | null
  jev_diagnosis?: ScalpDiagnosis | null
}

const DEFAULT_STATUS: ScalpStatus = {
  state: 'off',
  has_spot_key: true,
  lookback_label: 'últimos 15 min',
  horizon_s: 900,
  t_quote: '100',
  clip_quote: '10',
  inventory_btc: '0',
  calibration: null,
  pnl_quote: '0',
  status_text:
    'Desligado: não envia ordem deste scalp. Lookback últimos 15 min. Inventário e P&L ficam visíveis.',
  kill_banner: false,
  inventory_clipped: false,
  fee_bp: '10',
  hurdle_bp: '20.1',
  exit_target_bp: '35',
  exit_stop_bp: '-28',
  stuck: false,
  calibration_paused: true,
  calibration_enabled: false,
  jev_diagnosis: null,
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

function formatBp(value: string | undefined): string {
  if (!value) return '—'
  const n = parseNumber(value)
  if (n > 0) return `+${n.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} bp`
  return `${n.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} bp`
}

function formatAge(seconds: number | undefined): string {
  if (seconds == null || seconds < 0) return '—'
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  if (m <= 0) return `${s} s`
  return `${m} min ${s} s`
}

function formatFeeBp(status: ScalpStatus): string {
  const n = parseNumber(status.fee_bp)
  const rate = `${n.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} bp`
  return status.bnb_fee_active ? `${rate} (BNB habilitado; desconto não aplicado)` : rate
}

function formatHurdle(value: string | undefined): string {
  const n = parseNumber(value)
  return `${n.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} bp`
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

  const visual: ScalpPanelState =
    status.state === 'nokey' || status.state === 'on' || status.state === 'kill' ? status.state : 'off'
  const checked = visual === 'on'
  const bookUnavailable = visual === 'on' && status.book_available === false
  const dataBook = visual === 'on' ? (bookUnavailable ? 'unavailable' : 'fresh') : 'fresh'
  const disabled = visual === 'nokey' || pending
  const pnl = parseNumber(status.pnl_quote)
  const pnlClass = pnl < 0 ? 'neg' : pnl > 0 ? 'pos' : ''
  const lookback = status.lookback_label || 'últimos 15 min'
  const hasPosition = Boolean(status.position && status.position.entry_quote)
  const lastBp = parseNumber(status.last_trade_bp ?? undefined)
  const lastUsd = parseNumber(status.last_trade_quote ?? undefined)
  const lastBpClass = lastBp < 0 ? 'neg' : lastBp > 0 ? 'pos' : ''
  const lastUsdClass = lastUsd < 0 ? 'neg' : lastUsd > 0 ? 'pos' : ''
  const diagnosis = status.jev_diagnosis || null
  const calibrationOn = status.calibration_paused === false || status.calibration_enabled === true
  const canRevert = Boolean(diagnosis?.can_revert || status.confidence_version?.previous)
  const history = diagnosis?.history || []

  const postJson = async (path: string, body?: unknown) => {
    const res = await authFetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
    const payload = (await res.json().catch(() => null)) as ScalpStatus | { detail?: string } | null
    if (res.ok && payload && typeof payload === 'object' && 'state' in payload) {
      setStatus({ ...DEFAULT_STATUS, ...(payload as ScalpStatus) })
    } else {
      await load()
    }
  }

  const setCalibration = async (paused: boolean) => {
    if (pending) return
    setPending(true)
    try {
      await postJson('/scalp/calibration', { paused })
    } finally {
      setPending(false)
    }
  }

  const revertVersion = async () => {
    if (pending) return
    setPending(true)
    try {
      await postJson('/scalp/revert')
    } finally {
      setPending(false)
    }
  }

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
      data-book={dataBook}
      data-horizon="15"
      data-horizon-s={String(status.horizon_s ?? 900)}
      aria-labelledby="scalp-title"
    >
      <div className="scalp-head">
        <div>
          <h2 id="scalp-title">Scalp BTCUSDT</h2>
          <p className="scalp-sub">
            À vista · limitadora post-only que não cruza · lookback {lookback} · a sua conta Binance. Um lado de cada
            vez. Resultado por trade, não meta.
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
          <dt>Lookback</dt>
          <dd id="scalp-horizon" data-testid="scalp-horizon">{lookback}</dd>
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
      <dl className="scalp-kpis scalp-trade-kpis">
        <div>
          <dt>Hurdle</dt>
          <dd id="scalp-hurdle" data-testid="scalp-hurdle">{formatHurdle(status.hurdle_bp)}</dd>
        </div>
        <div>
          <dt>Taxa em uso</dt>
          <dd id="scalp-fee" data-testid="scalp-fee">{formatFeeBp(status)}</dd>
        </div>
        <div>
          <dt>Alvo</dt>
          <dd id="scalp-exit-target" data-testid="scalp-exit-target">+35 bp</dd>
        </div>
        <div>
          <dt>Stop</dt>
          <dd id="scalp-exit-stop" data-testid="scalp-exit-stop">−28 bp</dd>
        </div>
        <div>
          <dt>Último trade</dt>
          <dd id="scalp-last-bp" className={lastBpClass} data-testid="scalp-last-bp">
            {status.last_trade_bp ? formatBp(status.last_trade_bp) : '—'}
          </dd>
        </div>
        <div>
          <dt>Último trade US$</dt>
          <dd id="scalp-last-usd" className={lastUsdClass} data-testid="scalp-last-usd">
            {status.last_trade_quote ? formatUsd(status.last_trade_quote) : '—'}
          </dd>
        </div>
      </dl>
      <dl className="scalp-position" id="scalp-position" data-testid="scalp-position" hidden={!hasPosition}>
        <div>
          <dt>Entrada</dt>
          <dd id="scalp-entry">{hasPosition ? formatUsd(status.position?.entry_quote) : '—'}</dd>
        </div>
        <div>
          <dt>Idade</dt>
          <dd id="scalp-age">{hasPosition ? formatAge(status.position?.age_s) : '—'}</dd>
        </div>
        <div>
          <dt>Alvo</dt>
          <dd id="scalp-target">+35 bp</dd>
        </div>
        <div>
          <dt>Stop</dt>
          <dd id="scalp-stop">−28 bp</dd>
        </div>
      </dl>
      <p className="scalp-status" id="scalp-status" data-testid="scalp-status" aria-live="polite">
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
      <p className="scalp-stuck" id="scalp-stuck" data-testid="scalp-stuck" hidden={!status.stuck}>
        posição presa: saída post-only não preencheu até 15:30. O utilizador decide. Operar continua disponível. Sem
        ordem a mercado.
      </p>
      {status.inventory_clipped ? (
        <p className="scalp-note" data-testid="scalp-clip-note">
          Inventário clipado ao BTC livre acima do piso (fill fora deste loop não entra no P&amp;L).
        </p>
      ) : (
        <p className="scalp-note">
          Mesma chave Spot de Meu Perfil que o Operar. O Operar (clique a mercado) continua ao lado. Nunca saque.
          P&amp;L e perda por trade tão visíveis quanto o ganho.
        </p>
      )}
      <section
        className="scalp-diagnosis"
        id="scalp-diagnosis"
        data-testid="scalp-diagnosis"
        data-outcome={diagnosis?.verb || 'bloquear'}
        aria-labelledby="scalp-diagnosis-title"
      >
        <div className="scalp-diagnosis-head">
          <h3 id="scalp-diagnosis-title">Como está o scalp</h3>
          <button
            className="scalp-switch"
            id="scalp-calibration"
            type="button"
            role="switch"
            aria-checked={calibrationOn}
            aria-label="Ajuste automático"
            data-testid="scalp-calibration"
            disabled={pending}
            onClick={() => {
              void setCalibration(calibrationOn)
            }}
          >
            {calibrationOn ? 'Ligada' : 'Pausada'}
          </button>
        </div>
        <p className="scalp-diagnosis-lead">
          {diagnosis?.lead || 'Um aviso por dia, só depois que o dia fecha. Ainda não há aviso deste dia fechado.'}
        </p>
        <dl className="scalp-diagnosis-facts">
          <div>
            <dt>Quando</dt>
            <dd>{diagnosis?.when || '—'}</dd>
          </div>
          <div>
            <dt>Dados</dt>
            <dd>{diagnosis?.data_ok || '—'}</dd>
          </div>
          <div>
            <dt>Período</dt>
            <dd>{diagnosis?.period || diagnosis?.until || 'só o que já tinha fechado à meia-noite UTC'}</dd>
          </div>
          <div>
            <dt>Confiança agora</dt>
            <dd>{diagnosis?.confidence_now || '—'}</dd>
          </div>
          <div>
            <dt>Última decisão</dt>
            <dd>
              <span className="scalp-verb" data-verb={diagnosis?.verb || 'bloquear'}>
                {diagnosis?.decision || 'não mudei a confiança'}
              </span>
            </dd>
          </div>
          <div>
            <dt>Amostra</dt>
            <dd>{diagnosis?.sample || '—'}</dd>
          </div>
          <div>
            <dt>Alvo e stop</dt>
            <dd>{diagnosis?.target_stop || 'alvo +35 e stop −28. O prazo do scalp não muda.'}</dd>
          </div>
          <div>
            <dt>O sinal</dt>
            <dd>{diagnosis?.signal || '—'}</dd>
          </div>
          <div>
            <dt>O lado</dt>
            <dd>{diagnosis?.side || '—'}</dd>
          </div>
        </dl>
        <p className="scalp-diagnosis-reason" id="scalp-diagnosis-reason" data-testid="scalp-diagnosis-reason">
          {diagnosis?.reason ||
            'Ainda não há aviso deste dia fechado. A confiança fica. Alvo, stop e o prazo do scalp não mudam.'}
        </p>
        <p className="scalp-note">
          {diagnosis?.calibration_note ||
            'Ligar o ajuste automático não liga o scalp nem envia ordem. O interruptor acima continua como o deixou. Se já houver uma posição aberta, ela sai como estava.'}
        </p>
        <div className="scalp-actions" aria-label="Comandos do diagnóstico">
          <button
            type="button"
            data-testid="scalp-calibration-pause"
            disabled={pending || !calibrationOn}
            onClick={() => {
              void setCalibration(true)
            }}
          >
            Pausar ajuste automático
          </button>
          <button
            type="button"
            data-testid="scalp-revert"
            disabled={pending || !canRevert}
            onClick={() => {
              void revertVersion()
            }}
          >
            Voltar à versão anterior
          </button>
        </div>
        <h4 id="scalp-history-title">Histórico</h4>
        <ol className="scalp-diagnosis-history" aria-labelledby="scalp-history-title">
          {history.length === 0 ? (
            <li>
              <span>Ainda não há histórico deste scalp.</span>
            </li>
          ) : (
            history.map((item, index) => (
              <li key={`${item.date || 'h'}-${index}`}>
                <time dateTime={item.date}>{item.label || item.date}</time>
                <span>
                  <span className="scalp-verb" data-verb={item.verb || 'bloquear'}>
                    {item.verb === 'aplicar'
                      ? 'Apliquei.'
                      : item.verb === 'reverter'
                        ? 'Voltei atrás.'
                        : item.verb === 'manter'
                          ? 'Mantive.'
                          : 'Não mudei.'}
                  </span>{' '}
                  {item.text}
                </span>
              </li>
            ))
          )}
        </ol>
      </section>
    </section>
  )
}
