/** Período de varredura Descoberta / Combo (card #1078). */

export type PeriodKey = '15d' | '1m' | '3m' | '6m' | '1y' | '2y' | 'custom' | 'all'

export const PERIOD_OPTIONS: ReadonlyArray<{ value: PeriodKey; label: string }> = [
  { value: '15d', label: '15 dias' },
  { value: '1m', label: '1 mês' },
  { value: '3m', label: '3 meses' },
  { value: '6m', label: '6 meses' },
  { value: '1y', label: '1 ano' },
  { value: '2y', label: '2 anos' },
  { value: 'custom', label: 'Personalizado' },
  { value: 'all', label: 'Todo o histórico' },
]

export const DISCOVERY_DEFAULT_PERIOD: PeriodKey = '15d'

const PERIOD_LABEL: Record<PeriodKey, string> = Object.fromEntries(
  PERIOD_OPTIONS.map((o) => [o.value, o.label]),
) as Record<PeriodKey, string>

export function isPeriodKey(value: string | null | undefined): value is PeriodKey {
  return PERIOD_OPTIONS.some((o) => o.value === value)
}

export function periodDisplayLabel(key: PeriodKey): string {
  return PERIOD_LABEL[key]
}

export function utcTodayIso(): string {
  const now = new Date()
  return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()))
    .toISOString()
    .slice(0, 10)
}

function subtractFixedWindow(endIso: string, key: Exclude<PeriodKey, 'custom' | 'all'>): string {
  const [y, m, d] = endIso.split('-').map(Number)
  const end = new Date(Date.UTC(y, m - 1, d))
  switch (key) {
    case '15d':
      end.setUTCDate(end.getUTCDate() - 15)
      break
    case '1m':
      end.setUTCMonth(end.getUTCMonth() - 1)
      break
    case '3m':
      end.setUTCMonth(end.getUTCMonth() - 3)
      break
    case '6m':
      end.setUTCMonth(end.getUTCMonth() - 6)
      break
    case '1y':
      end.setUTCFullYear(end.getUTCFullYear() - 1)
      break
    case '2y':
      end.setUTCFullYear(end.getUTCFullYear() - 2)
      break
    default:
      break
  }
  return end.toISOString().slice(0, 10)
}

/** Resolve janela «últimos X» ou Personalizado (espírito do backend). */
export function resolvePeriodDates(
  period: PeriodKey,
  customStart: string,
  customEnd: string,
  todayUtc = utcTodayIso(),
): { start_date: string | null; end_date: string | null } {
  if (period === 'all') return { start_date: null, end_date: null }
  if (period === 'custom') {
    return {
      start_date: customStart || null,
      end_date: customEnd || null,
    }
  }
  return {
    start_date: subtractFixedWindow(todayUtc, period),
    end_date: todayUtc,
  }
}

export type PeriodPayload = {
  period_type: PeriodKey
  start_date?: string | null
  end_date?: string | null
}

export function periodPayloadForApi(
  period: PeriodKey,
  customStart: string,
  customEnd: string,
): PeriodPayload {
  const { start_date, end_date } = resolvePeriodDates(period, customStart, customEnd)
  if (period === 'custom') {
    return { period_type: period, start_date: start_date ?? undefined, end_date: end_date ?? undefined }
  }
  if (period === 'all') {
    return { period_type: period }
  }
  return { period_type: period, start_date, end_date }
}

/** Copy Preflight decisão 6 (design.md). */
export function customPeriodImpediments(
  period: PeriodKey,
  customStart: string,
  customEnd: string,
  todayUtc = utcTodayIso(),
): string[] {
  if (period !== 'custom') return []
  if (!customStart && !customEnd) return ['Seleccione Data Inicial e Data Final.']
  if (!customStart) return ['Seleccione Data Inicial.']
  if (!customEnd) return ['Seleccione Data Final.']
  if (customStart > customEnd) return ['Data Inicial não pode ser depois da Data Final.']
  if (customEnd > todayUtc) return ['Data Final não pode ser depois de hoje.']
  return []
}

export function comboPeriodHint(
  period: PeriodKey,
  customStart: string,
  customEnd: string,
): string {
  if (period === 'all') {
    return 'Será usado todo o histórico disponível para os símbolos escolhidos.'
  }
  if (period === 'custom') {
    const imp = customPeriodImpediments(period, customStart, customEnd)
    if (imp.length) {
      return imp[0]
    }
    const { start_date, end_date } = resolvePeriodDates(period, customStart, customEnd)
    return `Será usado o intervalo ${start_date} → ${end_date}.`
  }
  const label = periodDisplayLabel(period)
  const { start_date, end_date } = resolvePeriodDates(period, '', '')
  if (start_date && end_date) {
    return `Será usada a janela ${label} (${start_date} → ${end_date}).`
  }
  return `Será usada a janela ${label}.`
}
