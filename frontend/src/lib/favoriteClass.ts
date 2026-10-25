/**
 * Favoritos como lista única de cripto, ação e ETF (card #1120, decisão 14).
 *
 * Lógica pura, sem DOM e sem rede, para ser testada com `tsx --test`. Os textos são os do protótipo
 * aprovado (`frontend/public/prototypes/card-1120-lote-multiclasse/index.html`): classe e moeda por
 * linha, precisão, convenções e período efetivo à vista, e "Limitações e origem" atrás de um `<details>`.
 */

import {
  CLASS_LABEL,
  fmtInt,
  formatDatePlain as formatDate,
  formatDateTime,
  symbolIsCrypto,
  type AssetClass,
} from './assetSelection'
import { candleName, type ExecutionInfo, type ConventionsInfo, type ResultAsset } from './equityExecution'

export interface FavoriteClassInput {
  symbol: string
  timeframe: string
  created_at?: string | null
  notes?: string | null
  asset?: ResultAsset | null
  metrics?: Record<string, any> | null
}

const NY = 'America/New_York'

export function isEquityClass(cls: AssetClass | null | undefined): boolean {
  return cls === 'stock' || cls === 'etf'
}

/** Classe do favorito: `asset` da API, `metrics.analysis_asset` (legado: `metrics.asset`) ou, sem catálogo, o formato do símbolo. */
export function favoriteClass(fav: FavoriteClassInput): AssetClass {
  const stored = fav.asset?.asset_class ?? fav.metrics?.analysis_asset?.asset_class ?? fav.metrics?.asset?.asset_class
  if (stored === 'crypto' || stored === 'stock' || stored === 'etf') return stored
  return symbolIsCrypto(fav.symbol) ? 'crypto' : 'stock'
}

export function favoriteCurrency(fav: FavoriteClassInput): string {
  const stored = fav.asset?.currency ?? fav.metrics?.analysis_asset?.currency ?? fav.metrics?.asset?.currency
  if (stored) return String(stored)
  const cls = favoriteClass(fav)
  if (cls === 'crypto') return fav.symbol.split('/')[1] || 'USDT'
  return 'USD'
}

// Fonte única: `analysis_*` (o lote grava e o refresh diário atualiza); a chave sem prefixo só vale para
// favoritos antigos, para que a atualização mais nova sempre ganhe.
export function favoriteExecution(fav: FavoriteClassInput): ExecutionInfo | null {
  const execution = fav.metrics?.analysis_execution ?? fav.metrics?.execution
  return execution && typeof execution === 'object' ? (execution as ExecutionInfo) : null
}

export function favoriteConventions(fav: FavoriteClassInput): ConventionsInfo | null {
  const conventions = fav.metrics?.analysis_conventions ?? fav.metrics?.conventions
  return conventions && typeof conventions === 'object' ? (conventions as ConventionsInfo) : null
}

/** Id do lote (8 primeiros caracteres): `metrics.batch_id` ou a nota "gerado em lote (<id8>)". */
export function favoriteLoteId(fav: FavoriteClassInput): string | null {
  const batchId = fav.metrics?.batch_id
  if (typeof batchId === 'string' && batchId) return batchId.slice(0, 8)
  const match = /gerado em lote \(([0-9a-f]{8})\)/i.exec(fav.notes ?? '')
  return match ? match[1] : null
}

export type ClassFilterValue = 'all' | AssetClass

export function classCounts(favs: FavoriteClassInput[]): Record<ClassFilterValue, number> {
  const counts: Record<ClassFilterValue, number> = { all: favs.length, crypto: 0, stock: 0, etf: 0 }
  for (const fav of favs) counts[favoriteClass(fav)] += 1
  return counts
}

export function classFilterOptions(counts: Record<ClassFilterValue, number>): Array<{ value: ClassFilterValue; label: string }> {
  return [
    { value: 'all', label: `Todas (${fmtInt(counts.all)})` },
    { value: 'crypto', label: `Cripto (${fmtInt(counts.crypto)})` },
    { value: 'stock', label: `Ações (${fmtInt(counts.stock)})` },
    { value: 'etf', label: `ETFs (${fmtInt(counts.etf)})` },
  ]
}

export function chipLabel(cls: AssetClass): string {
  return CLASS_LABEL[cls]
}

// --- Texto da linha e do cartão ---------------------------------------------------------------------------------

export const PENDING_EQUITY_TEXT = 'Atualização diária, Monitor, Telegram e Revalidar: ainda não para ações e ETFs'
export const OFF_EQUITY_TITLE = 'Revalidar: ainda não para ações e ETFs'

export type PrecisionTone = 'info' | 'warn' | 'muted'

export interface RowData {
  cls: AssetClass
  currency: string
  precision: { tone: PrecisionTone; text: string }
  conventions: string
  /** "Período efetivo 11 nov. 2014 – 23 out. 2026" ou o aviso do favorito antigo. */
  effective: string
  /** "11 nov. 2014 – 23 out. 2026" (coluna Período); `null` sem execução. */
  effectiveRange: string | null
  details: { summary: string; conventionsFull: string | null; limitations: string | null; lote: string | null } | null
  lote: string | null
}

function zoneOf(cls: AssetClass): string {
  return isEquityClass(cls) ? NY : 'UTC'
}

function dayText(value: string | null | undefined, cls: AssetClass): string {
  if (!value) return ''
  // data só de dia ("2026-01-02") vale como está (UTC); instante vale no fuso do mercado
  return formatDate(value, /^\d{4}-\d{2}-\d{2}$/.test(value) ? 'UTC' : zoneOf(cls))
}

export function precisionText(
  execution: ExecutionInfo | null,
  cls: AssetClass,
  timeframe: string,
): { tone: PrecisionTone; text: string } {
  if (!execution || !execution.precision_effective) {
    return { tone: 'muted', text: 'Precisão e período efetivo: aparecem na próxima atualização diária' }
  }
  if (execution.precision_effective === 'intrabar_15m') return { tone: 'info', text: 'Precisão intrabar (15m)' }
  const name = candleName(execution.timeframe || timeframe).title
  if (execution.precision_requested === 'daily' || !execution.intraday_reason) {
    return { tone: 'muted', text: `${name} · Deep Backtest desligado` }
  }
  if (execution.intraday_reason === 'read_error') {
    return { tone: 'warn', text: `${name} · intradiário de 15m não lido` }
  }
  const stretch = (execution.intraday_missing ?? [])
    .map((m) => `${dayText(m.from, cls)} a ${dayText(m.to, cls)}`)
    .join(' e ')
  return { tone: 'warn', text: stretch ? `${name} · sem 15m de ${stretch}` : name }
}

function sessionsPerYear(conventions: ConventionsInfo | null): number {
  return conventions?.calendar?.sessions_per_year ?? 252
}

export function conventionsShort(cls: AssetClass, conventions: ConventionsInfo | null): string {
  if (!isEquityClass(cls)) return 'Binance Spot · 24/7 · 365 dias/ano'
  const adjusted = conventions?.adjusted_prices === false ? 'sem ajuste' : 'split'
  return `Binance Ações · NY · ${adjusted} · ${sessionsPerYear(conventions)}/ano`
}

export function conventionsFull(cls: AssetClass, conventions: ConventionsInfo | null): string | null {
  if (!isEquityClass(cls)) return null
  const adjusted = conventions?.adjusted_prices === false ? 'sem ajuste' : 'ajustado por split'
  return `Convenções: Binance Ações · pregão regular de Nova York · ${adjusted} · ${sessionsPerYear(conventions)} pregões/ano`
}

export function limitationsText(cls: AssetClass, conventions: ConventionsInfo | null): string | null {
  if (!isEquityClass(cls)) return null
  const parts: string[] = []
  if (conventions?.fraction?.simulated !== false) parts.push('simulação com fração')
  if (conventions?.fee_confirmed === false) parts.push('taxa assumida')
  if (conventions?.adjusted_prices !== false) parts.push('preços ajustados podem diferir do negociado')
  return parts.length ? `Limitações: ${parts.join(' · ')}` : null
}

export function loteTag(fav: FavoriteClassInput): string | null {
  const id = favoriteLoteId(fav)
  if (!id) return null
  const when = fav.created_at ? formatDate(fav.created_at, 'America/Sao_Paulo') : ''
  return `Gerado em lote ${id}${when ? ` · ${when}` : ''}`
}

export function favoriteRowData(fav: FavoriteClassInput): RowData {
  const cls = favoriteClass(fav)
  const execution = favoriteExecution(fav)
  const conventions = favoriteConventions(fav)
  const covered = execution?.window?.covered
  const range =
    covered?.start && covered?.end ? `${dayText(covered.start, cls)} – ${dayText(covered.end, cls)}` : null
  const lote = loteTag(fav)
  const full = conventionsFull(cls, conventions)
  const limitations = limitationsText(cls, conventions)
  let details: RowData['details'] = null
  if (full || limitations) details = { summary: 'Limitações e origem', conventionsFull: full, limitations, lote }
  else if (lote) details = { summary: 'Origem', conventionsFull: null, limitations: null, lote }
  return {
    cls,
    currency: favoriteCurrency(fav),
    precision: precisionText(execution, cls, fav.timeframe),
    conventions: conventionsShort(cls, conventions),
    effective: range ? `Período efetivo ${range}` : 'Período efetivo: na próxima atualização',
    effectiveRange: range,
    details,
    lote: favoriteLoteId(fav),
  }
}

/** ATR com a moeda do ativo ("4.87 USD"); sem valor, o traço de sempre. */
export function atrWithCurrency(value: unknown, currency: string): string {
  const n = Number(value)
  if (value === null || value === undefined || value === '' || !Number.isFinite(n)) return '-'
  return `${n.toFixed(2)} ${currency}`
}

// --- Faixa do lote, nota das estrelas e rodapé ------------------------------------------------------------------

export function loteBannerText(loteId: string, favs: FavoriteClassInput[]): string {
  const created = favs
    .filter((f) => favoriteLoteId(f) === loteId && f.created_at)
    .map((f) => String(f.created_at))
    .sort()[0]
  const when = created ? ` (${formatDateTime(created, 'America/Sao_Paulo')})` : ''
  return `Mostrando só o lote ${loteId}${when}: os favoritos gravados por ele, de todas as classes.`
}

export function tierNoteText(equityCount: number): string | null {
  if (!equityCount) return null
  const who =
    equityCount === 1
      ? 'O favorito de ação ou ETF fica'
      : `Os ${fmtInt(equityCount)} favoritos de ação e ETF ficam`
  return `Monitor, Telegram e Revalidar: ainda não para ações e ETFs. ${who} fora destes níveis.`
}

export const FILTER_EMPTY_LOTE = 'Nenhuma estratégia com estes filtros. Troque a classe ou limpe os filtros.'
