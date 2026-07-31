import React from 'react'

import { API_BASE_URL } from '../../lib/apiBase'
import { authFetch } from '@/lib/authFetch'
import type { Opportunity } from './types'

type ProtectiveOrder = {
  order_id?: number | null
  side?: string | null
  type?: string | null
  status?: string | null
  stop_price?: number | null
  limit_price?: number | null
  quantity?: number | null
}

type StatusResponse = {
  protected: boolean
  symbol: string
  client_order_id?: string
  order?: ProtectiveOrder | null
}

type SpotProtectStopPanelProps = {
  opportunity: Opportunity
  showEntryStopRows: boolean
  direction: 'long' | 'short'
}

const PRICE = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 8,
})

function formatPrice(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(value)) return '-'
  return PRICE.format(value)
}

function errorMessage(payload: unknown, fallback: string) {
  if (typeof payload === 'object' && payload && 'detail' in payload) {
    const detail = (payload as { detail?: unknown }).detail
    if (typeof detail === 'string') return detail
  }
  return fallback
}

export function SpotProtectStopPanel({
  opportunity,
  showEntryStopRows,
  direction,
}: SpotProtectStopPanelProps) {
  const [status, setStatus] = React.useState<StatusResponse | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [acting, setActing] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [confirmPlace, setConfirmPlace] = React.useState(false)

  const opportunityId = String(opportunity.id)
  const symbol = String(opportunity.symbol || '').toUpperCase()
  const stopPrice = opportunity.stop_price ?? null
  const estimatedLimit = stopPrice != null ? stopPrice * (1 - 0.001) : null

  const disabledReason = React.useMemo(() => {
    if (direction === 'short') return 'Disponível apenas para long Spot'
    if (!showEntryStopRows) return 'Disponível apenas com posição HOLD e STOP visível'
    if (stopPrice == null || stopPrice <= 0) return 'Sem stop_price nesta opportunity'
    return null
  }, [direction, showEntryStopRows, stopPrice])

  const refresh = React.useCallback(async () => {
    if (disabledReason) {
      setStatus(null)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const qs = new URLSearchParams({ symbol, opportunity_id: opportunityId })
      const res = await authFetch(`${API_BASE_URL}/monitor/spot-stop-order?${qs}`)
      const payload = await res.json().catch(() => ({}))
      if (!res.ok) {
        setStatus(null)
        setError(errorMessage(payload, 'Não foi possível consultar a ordem protetiva'))
        return
      }
      setStatus(payload as StatusResponse)
    } catch {
      setStatus(null)
      setError('Falha de rede ao consultar proteção Spot')
    } finally {
      setLoading(false)
    }
  }, [disabledReason, opportunityId, symbol])

  React.useEffect(() => {
    void refresh()
  }, [refresh])

  const place = async () => {
    if (stopPrice == null) return
    setActing(true)
    setError(null)
    try {
      const res = await authFetch(`${API_BASE_URL}/monitor/spot-stop-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          opportunity_id: opportunityId,
          stop_price: stopPrice,
          direction,
        }),
      })
      const payload = await res.json().catch(() => ({}))
      if (!res.ok) {
        setError(errorMessage(payload, 'Falha ao criar stop-limit'))
        return
      }
      setConfirmPlace(false)
      await refresh()
    } catch {
      setError('Falha de rede ao criar stop-limit')
    } finally {
      setActing(false)
    }
  }

  const remove = async () => {
    setActing(true)
    setError(null)
    try {
      const qs = new URLSearchParams({ symbol, opportunity_id: opportunityId })
      const res = await authFetch(`${API_BASE_URL}/monitor/spot-stop-order?${qs}`, {
        method: 'DELETE',
      })
      const payload = await res.json().catch(() => ({}))
      if (!res.ok) {
        setError(errorMessage(payload, 'Falha ao remover stop-limit'))
        return
      }
      await refresh()
    } catch {
      setError('Falha de rede ao remover stop-limit')
    } finally {
      setActing(false)
    }
  }

  const protectedOrder = status?.protected ? status.order : null

  return (
    <section
      className="w-full rounded-lg border border-[#2b3139] bg-[#1e2329] px-3 py-2.5"
      data-testid="spot-protect-stop-panel"
      aria-label="Proteção Spot stop-limit"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 space-y-1">
          <p className="text-[10px] font-semibold uppercase tracking-normal text-[#929aa5]">
            Proteção Spot
          </p>
          {disabledReason ? (
            <p className="text-xs text-[#929aa5]" data-testid="spot-protect-disabled-reason">
              {disabledReason}
            </p>
          ) : loading ? (
            <p className="text-xs text-[#929aa5]">Consultando ordem protetiva…</p>
          ) : protectedOrder ? (
            <p className="text-xs text-[#eaecef]" data-testid="spot-protect-summary">
              Ativa: qty {protectedOrder.quantity ?? '-'} · stop {formatPrice(protectedOrder.stop_price)} ·
              limit {formatPrice(protectedOrder.limit_price)}
            </p>
          ) : (
            <p className="text-xs text-[#929aa5]">
              Sem ordem protetiva. Stop do gráfico: {formatPrice(stopPrice)}
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {!disabledReason && !protectedOrder ? (
            <button
              type="button"
              className="min-h-10 rounded-md border border-[#f6465d]/50 bg-[#f6465d]/15 px-3 py-2 text-sm font-medium text-[#eaecef] transition hover:border-[#f6465d] disabled:opacity-50"
              disabled={acting || loading || confirmPlace}
              onClick={() => setConfirmPlace(true)}
              data-testid="spot-protect-place"
            >
              Proteger stop
            </button>
          ) : null}
          {!disabledReason && protectedOrder ? (
            <button
              type="button"
              className="min-h-10 rounded-md border border-[#2b3139] bg-[#0b0e11] px-3 py-2 text-sm font-medium text-[#eaecef] transition hover:border-[#fcd535] disabled:opacity-50"
              disabled={acting || loading}
              onClick={() => void remove()}
              data-testid="spot-protect-remove"
            >
              {acting ? 'Removendo…' : 'Remover stop'}
            </button>
          ) : null}
        </div>
      </div>

      {confirmPlace && !disabledReason ? (
        <div
          className="mt-3 rounded-md border border-[#f6465d]/40 bg-[#0b0e11] p-3"
          data-testid="spot-protect-confirm"
        >
          <p className="text-sm text-[#eaecef]">
            Vender <span className="font-semibold">100%</span> do saldo free de{' '}
            <span className="font-mono">{symbol.replace(/USDT|USDC|BUSD$/i, '')}</span> se o preço ≤{' '}
            <span className="font-mono text-[#f6465d]">{formatPrice(stopPrice)}</span> (limit{' '}
            <span className="font-mono">{formatPrice(estimatedLimit)}</span>).
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              className="min-h-10 rounded-md border border-[#f6465d] bg-[#f6465d]/20 px-3 py-2 text-sm font-medium text-[#eaecef] disabled:opacity-50"
              disabled={acting}
              onClick={() => void place()}
              data-testid="spot-protect-confirm-yes"
            >
              {acting ? 'Enviando…' : 'Confirmar proteção'}
            </button>
            <button
              type="button"
              className="min-h-10 rounded-md border border-[#2b3139] px-3 py-2 text-sm text-[#929aa5]"
              disabled={acting}
              onClick={() => setConfirmPlace(false)}
              data-testid="spot-protect-confirm-no"
            >
              Cancelar
            </button>
          </div>
        </div>
      ) : null}

      {error ? (
        <p className="mt-2 text-xs text-[#f6465d]" data-testid="spot-protect-error" role="alert">
          {error}
        </p>
      ) : null}
    </section>
  )
}
