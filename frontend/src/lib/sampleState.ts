/**
 * Proveniência da série e estado da amostra no Decidir da Descoberta (card #1118).
 *
 * Textos do protótipo aprovado: a linha de evidência diz a série ("Binance Spot · 1d nativo · v7") e até
 * quando a amostra da varredura fica guardada; cada resultado diz o estado da própria amostra; resultado
 * favoritado lembra que Favoritos guarda a amostra do último refresh. Sem DOM e sem rede.
 */

import { formatDate } from './assetSelection'

export type SampleState = 'kept' | 'pinned' | 'expired' | 'none'

export interface SampleInfo {
  state: SampleState
  retain_until: string | null
}

export interface ResultProvenance {
  data_source?: string | null
  asset_class?: string | null
  session?: string | null
  adjustment?: string | null
  timeframe_origin?: string | null
  data_version?: number | null
}

export interface SampledRow {
  timeframe: string
  candle_source?: string | null
  candle_version?: string | null
  provenance?: ResultProvenance | null
  sample?: SampleInfo | null
  dedup_state?: string | null
}

export const NOT_REPRODUCIBLE = 'não reproduzível exatamente'
export const FAVORITES_KEEP_LAST_REFRESH = 'favoritos guardam a amostra do último refresh'
export const FAVORITE_ROW_TEXT = 'favorito: Favoritos guarda a amostra do último refresh'

export type SampleTone = 'plain' | 'expired' | 'favorite'

/** `Binance Spot · 1d nativo · v7` (ou `15m montado do 5m`); resultados antigos mantêm `ccxt v…`. */
export function seriesLine(row: SampledRow): string {
  const prov = row.provenance
  if (prov?.data_source) {
    const origin = prov.timeframe_origin === 'derived' ? 'montado do 5m' : 'nativo'
    const version = row.candle_version ?? (prov.data_version != null ? String(prov.data_version) : null)
    return `${prov.data_source} · ${row.timeframe} ${origin}${version ? ` · v${version}` : ''}`
  }
  return `${row.candle_source ?? '—'}${row.candle_version ? ` v${row.candle_version}` : ''}`
}

export function hasSeriesProvenance(row: SampledRow): boolean {
  return !!row.provenance?.data_source
}

const day = (iso: string | null | undefined) => formatDate(iso, 'UTC')

/**
 * Estado da amostra da varredura na linha de evidência. A varredura vale pelo prazo mais curto entre os
 * seus resultados; passado o prazo, diz "não reproduzível exatamente" e lembra que o favorito é outra conta.
 */
export function evidenceSample(rows: SampledRow[]): { text: string; tone: SampleTone; suffix?: string } | null {
  const sampled = rows.filter((r) => r.sample)
  if (!sampled.length) return null
  const kept = sampled.filter((r) => r.sample!.state === 'kept' || r.sample!.state === 'pinned')
  const expired = sampled.filter((r) => r.sample!.state === 'expired')
  const anyFavorite = rows.some((r) => r.dedup_state === 'already_promoted')
  if (!kept.length && !expired.length) {
    return { text: 'sem amostra guardada (varredura anterior à amostra por execução)', tone: 'plain' }
  }
  if (expired.length) {
    const dates = expired.map((r) => r.sample!.retain_until).filter(Boolean) as string[]
    const when = dates.length ? ` em ${day([...dates].sort().at(-1))}` : ''
    // "não reproduzível exatamente" pesa no estado; o lembrete do favorito vai fora do destaque.
    return {
      text: `amostra expirada${when}: ${NOT_REPRODUCIBLE}`,
      tone: 'expired',
      suffix: anyFavorite ? ` · ${FAVORITES_KEEP_LAST_REFRESH}` : undefined,
    }
  }
  const dates = kept.map((r) => r.sample!.retain_until).filter(Boolean) as string[]
  if (!dates.length) return { text: `amostra guardada; ${FAVORITES_KEEP_LAST_REFRESH}`, tone: 'plain' }
  const earliest = [...dates].sort()[0]
  return { text: `amostra guardada até ${day(earliest)}; ${FAVORITES_KEEP_LAST_REFRESH}`, tone: 'plain' }
}

/** Estado da amostra da própria varredura em cada resultado (e o aviso de favorito, quando promovido). */
export function rowSample(row: SampledRow): { sample: string | null; sampleTone: SampleTone; favorite: string | null } {
  const info = row.sample
  const favorite = row.dedup_state === 'already_promoted' ? FAVORITE_ROW_TEXT : null
  if (!info || info.state === 'none') return { sample: 'sem amostra guardada', sampleTone: 'plain', favorite }
  if (info.state === 'expired') return { sample: NOT_REPRODUCIBLE, sampleTone: 'expired', favorite }
  if (info.state === 'pinned') return { sample: 'amostra guardada enquanto for favorito', sampleTone: 'plain', favorite }
  return { sample: `amostra até ${day(info.retain_until)}`, sampleTone: 'plain', favorite }
}
