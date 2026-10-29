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

/** Card #1122: fonte, sessão e ajuste do favorito (com os rótulos que a API devolve). */
export interface FavoriteConfiguration {
  data_source?: string | null
  session?: string | null
  adjustment?: string | null
  label_short?: string | null
  label_compact?: string | null
  label_long?: string | null
}

export interface FavoriteClassInput {
  symbol: string
  timeframe: string
  created_at?: string | null
  notes?: string | null
  asset?: ResultAsset | null
  metrics?: Record<string, any> | null
  configuration?: FavoriteConfiguration | null
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

/** Card #1122: o favorito é da fonte antiga (Stooq, só diário). */
export function isLegacyConfiguration(configuration: FavoriteConfiguration | null | undefined): boolean {
  return String(configuration?.data_source || '').toLowerCase() === 'stooq'
}

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

export function conventionsShort(
  cls: AssetClass,
  conventions: ConventionsInfo | null,
  configuration?: FavoriteConfiguration | null,
): string {
  if (!isEquityClass(cls)) return 'Binance Spot · 24/7 · 365 dias/ano'
  // Card #1122: a configuração do favorito manda (a fonte antiga não é "Binance Ações").
  if (isLegacyConfiguration(configuration)) return 'Stooq · fonte antiga · diário'
  const adjusted = conventions?.adjusted_prices === false ? 'sem ajuste' : 'split'
  return `Binance Ações · NY · ${adjusted} · ${sessionsPerYear(conventions)}/ano`
}

export function conventionsFull(
  cls: AssetClass,
  conventions: ConventionsInfo | null,
  configuration?: FavoriteConfiguration | null,
): string | null {
  if (!isEquityClass(cls)) return null
  if (isLegacyConfiguration(configuration)) return 'Configuração: Stooq · fonte antiga · diário (migração para a Binance no #1126)'
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
  const full = conventionsFull(cls, conventions, fav.configuration)
  const limitations = limitationsText(cls, conventions)
  let details: RowData['details'] = null
  if (full || limitations) details = { summary: 'Limitações e origem', conventionsFull: full, limitations, lote }
  else if (lote) details = { summary: 'Origem', conventionsFull: null, limitations: null, lote }
  return {
    cls,
    currency: favoriteCurrency(fav),
    precision: precisionText(execution, cls, fav.timeframe),
    conventions: conventionsShort(cls, conventions, fav.configuration),
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

// --- Status da atualização diária (card #1122) -----------------------------------------------------------------

export interface FavoriteRefreshInput {
  symbol: string
  timeframe: string
  asset?: ResultAsset | null
  metrics?: Record<string, any> | null
  auto_refresh_status?: string | null
  auto_refresh_error?: string | null
  auto_refresh_started_at?: string | null
  auto_refresh_completed_at?: string | null
}

export interface RefreshStatus {
  label: string
  className: string
  title?: string
}

function ddmm(value: string): string | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value)
  return match ? `${match[3]}/${match[2]}` : null
}

function formatRefreshMoment(value: string): string {
  return new Date(value).toLocaleString('pt-BR', {
    timeZone: 'America/Sao_Paulo',
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Status da atualização diária. Ação/ETF: "Backtest atualizado: 24/10, 08:12 · último pregão 23/10";
 * série curta: "Aguardando dados: 40 de 200 candles" (cinza, nunca "Falha").
 */
export function formatFavoriteRefreshStatus(fav: FavoriteRefreshInput): RefreshStatus {
  const status = String(fav.auto_refresh_status || '').toUpperCase()
  const completedAt = fav.auto_refresh_completed_at || fav.auto_refresh_started_at
  const formattedDate = completedAt ? formatRefreshMoment(completedAt) : null
  if (status === 'RUNNING') return { label: 'Atualizando backtest', className: 'running' }
  if (status === 'INSUFFICIENT') {
    const counts = String(fav.auto_refresh_error || '').trim()
    return {
      label: counts ? `Aguardando dados: ${counts}` : 'Aguardando dados',
      className: 'waiting',
    }
  }
  if (status === 'FAILED') {
    return {
      label: formattedDate ? `Falha na atualização: ${formattedDate}` : 'Falha na atualização',
      className: 'failed',
      title: fav.auto_refresh_error || undefined,
    }
  }
  if (status === 'SUCCESS') {
    const base = formattedDate ? `Backtest atualizado: ${formattedDate}` : 'Backtest atualizado'
    const lastSession = isEquityClass(favoriteClass(fav)) ? fav.metrics?.analysis_last_session : null
    const session = typeof lastSession === 'string' ? ddmm(lastSession) : null
    return { label: session ? `${base} · último pregão ${session}` : base, className: 'success' }
  }
  return { label: 'Backtest aguardando atualização', className: 'pending' }
}

/** Card #1122 (d2, decisão 19): a estrela é a porta do Monitor e do alerta; Favoritos não tem "Alertar". */
export const MONITOR_STAR_HELP =
  'Com pelo menos 1 estrela, a estratégia entra no Monitor e manda alerta no Telegram, ligado por padrão (desligue no Monitor). Sem estrela, fica só aqui; lote e Descoberta salvam sem estrela.'

export const FILTER_EMPTY_LOTE = 'Nenhuma estratégia com estes filtros. Troque a classe ou limpe os filtros.'
