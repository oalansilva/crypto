/**
 * Descoberta com cripto, ação e ETF na mesma varredura (card #1121).
 *
 * Lógica pura, sem DOM e sem rede, testada com `tsx --test`. Os textos seguem o protótipo aprovado
 * (`frontend/public/prototypes/card-1121-descoberta-acoes-etfs/index.html`): Preflight por classe e moeda,
 * coleta e precisão previstas, teto, viés de sobrevivência, quadro "Por ativo", bloco compacto do
 * candidato, filtro Classe, nota "Sem resultado" e identidade da execução no modal de promoção.
 */

import { fmtInt, formatDatePlain, symbolIsCrypto, type AssetClass } from './assetSelection'
import { candleName, type ConventionsInfo, type ExecutionInfo, type ResultAsset } from './equityExecution'
import { conventionsShort, isEquityClass, precisionText } from './favoriteClass'

// --- Montar ---------------------------------------------------------------------------------------------------

/** Texto sob demanda das linhas do seletor na Descoberta (decisão 2): a coleta acontece ao rodar. */
export const ON_DEMAND_TEXT_DISCOVERY: Partial<Record<AssetClass, string>> = {
  crypto: 'Histórico sob demanda · coletado ao rodar a varredura',
  stock: 'Histórico sob demanda · coletado ao rodar a varredura',
  etf: 'Histórico sob demanda · coletado ao rodar a varredura',
}

export const DISCOVERY_CLASS_NOTE =
  'Cripto, ação e ETF entram na mesma varredura: cada ativo usa a sua fonte, sessão, ajuste e moeda (USDT ou USD). ' +
  'Sem 15m que cubra a janela, ação e ETF rodam em precisão diária, com a marca no resultado.'

export const DISCOVERY_FEE_BY_CLASS = 'taxa por lado: cripto 0,075% · ação e ETF 0,10% · slippage do timeframe'
export const DISCOVERY_COST_NOTE = `${DISCOVERY_FEE_BY_CLASS} (0,02% em 4h e 1d · 0,03% em 1h · 0,05% em 15m) · sem campo para alterar`

export interface ClassBucket {
  assets: number
  combinations: number
  currency?: string | null
}

export type ByClass = Partial<Record<AssetClass, ClassBucket>>

const CLASS_ORDER: AssetClass[] = ['crypto', 'stock', 'etf']

function classWord(cls: AssetClass, n: number): string {
  if (cls === 'crypto') return 'cripto'
  if (cls === 'stock') return n === 1 ? 'ação' : 'ações'
  return n === 1 ? 'ETF' : 'ETFs'
}

export function runAssets(byClass: ByClass | null | undefined): number {
  return CLASS_ORDER.reduce((sum, cls) => sum + (byClass?.[cls]?.assets ?? 0), 0)
}

/** `1 cripto · 2.431 ações · 1 ETF`. */
export function classesText(byClass: ByClass | null | undefined): string {
  return CLASS_ORDER.filter((cls) => (byClass?.[cls]?.assets ?? 0) > 0)
    .map((cls) => `${fmtInt(byClass![cls]!.assets)} ${classWord(cls, byClass![cls]!.assets)}`)
    .join(' · ')
}

/** `1 cripto (USDT) · 1 ação · 1 ETF (USD)`: a moeda fecha o grupo dela, USD e USDT nunca juntos. */
export function classesWithCurrency(byClass: ByClass | null | undefined): string {
  const present = CLASS_ORDER.filter((cls) => (byClass?.[cls]?.assets ?? 0) > 0)
  const lastEquity = [...present].reverse().find((cls) => cls !== 'crypto')
  return present
    .map((cls) => {
      const bucket = byClass![cls]!
      const base = `${fmtInt(bucket.assets)} ${classWord(cls, bucket.assets)}`
      if (cls === 'crypto') return `${base} (${bucket.currency || 'USDT'})`
      return cls === lastEquity ? `${base} (USD)` : base
    })
    .join(' · ')
}

function timeframesText(timeframes: string[]): string {
  return namesList(timeframes, timeframes.length)
}

/** "Vão rodar 3 ativos:" + o resto da linha (decisão 2). Acima do teto: "2.433 ativos selecionados:". */
export function runLine(
  byClass: ByClass | null | undefined,
  timeframes: string[],
  overLimit: boolean,
): { lead: string; rest: string } | null {
  const total = runAssets(byClass)
  if (!total) return null
  if (overLimit) {
    return { lead: `${fmtInt(total)} ativos selecionados:`, rest: `${classesWithCurrency(byClass)}.` }
  }
  const where = timeframes.length > 1 ? ` em ${timeframesText(timeframes)}` : ''
  return {
    lead: `Vão rodar ${fmtInt(total)} ${total === 1 ? 'ativo' : 'ativos'}${where}:`,
    rest: `${classesWithCurrency(byClass)}. Cada um com a sua fonte, sessão, ajuste e moeda.`,
  }
}

export const LIMIT_TITLE = (max: number) => `Acima do teto de ${fmtInt(max)} combinações`
export const LIMIT_ADVICE =
  'Estreite a seleção: menos ativos (filtre antes de usar “Todos do filtro”), menos templates ou menos timeframes. ' +
  'Nenhuma varredura foi criada.'

/** `2.433 combinações válidas passam do limite de 1.000: 2.433 ativos (…) × 1 template × 1 timeframe × Long.` */
export function limitText(
  total: number,
  max: number,
  byClass: ByClass | null | undefined,
  templates: number,
  timeframes: number,
  directions: string[],
): string {
  const assets = runAssets(byClass)
  const dirs = directions.map((d) => (d === 'short' ? 'Short' : 'Long')).join(' e ') || 'Long'
  return (
    `${fmtInt(total)} combinações válidas passam do limite de ${fmtInt(max)}: ` +
    `${fmtInt(assets)} ${assets === 1 ? 'ativo' : 'ativos'} (${classesText(byClass)}) × ` +
    `${fmtInt(templates)} ${templates === 1 ? 'template' : 'templates'} × ` +
    `${fmtInt(timeframes)} ${timeframes === 1 ? 'timeframe' : 'timeframes'} × ${dirs}.`
  )
}

/** `NVDA`, `NVDA e SPY`, `A, B e C`, `A, B, C e mais 4`. */
export function namesList(items: string[], max = 3): string {
  const unique = [...new Set(items)]
  if (unique.length <= max) {
    return unique.length < 2 ? unique.join('') : `${unique.slice(0, -1).join(', ')} e ${unique[unique.length - 1]}`
  }
  return `${unique.slice(0, max).join(', ')} e mais ${fmtInt(unique.length - max)}`
}

export interface CollectionForecast {
  count: number
  of: number
  assets: Array<{ symbol: string; asset_class?: string | null; series: string[] }>
  stored: string[]
}

/** "Precisam de coleta de histórico: 1 de 3 — SPY (1d e 5m do intrabar). BTC/USDT e NVDA já estão guardados. …" */
export function collectionLine(collection: CollectionForecast | null | undefined): { lead: string; rest: string } | null {
  if (!collection || !collection.of) return null
  if (!collection.count) {
    return {
      lead: 'Coleta de histórico: nenhuma',
      rest: `— ${collection.of === 1 ? 'o ativo já está guardado' : `os ${fmtInt(collection.of)} ativos já estão guardados`}.`,
    }
  }
  const shown = collection.assets.slice(0, 3).map((a) => `${a.symbol} (${namesList(a.series, a.series.length)})`)
  const extra = collection.assets.length - shown.length
  const who = shown.length < 2 ? shown.join('') : `${shown.slice(0, -1).join(', ')} e ${shown[shown.length - 1]}`
  const stored = collection.stored.length
    ? ` ${namesList(collection.stored)} ${collection.stored.length === 1 ? 'já está guardado' : 'já estão guardados'}.`
    : ''
  return {
    lead: `Precisam de coleta de histórico: ${fmtInt(collection.count)} de ${fmtInt(collection.of)}`,
    rest:
      `— ${who}${extra > 0 ? ` e mais ${fmtInt(extra)}` : ''}.${stored} ` +
      'A coleta acontece no começo do ativo e entra no tempo da varredura.',
  }
}

export interface DailyForecast {
  symbol: string
  timeframe: string
  from_label?: string | null
  to_label?: string | null
  five_from_label?: string | null
}

export interface PrecisionForecast {
  daily: DailyForecast[]
  no_candles: Array<{ symbol: string; timeframe: string; five_from_label?: string | null }>
  unknown: string[]
}

/** Previsão do Preflight (decisão 6): precisão diária por tempo, "sem candles prováveis" e ativo sem histórico. */
export function precisionLine(forecast: PrecisionForecast | null | undefined): { lead: string; rest: string } | null {
  if (!forecast) return null
  const { daily, no_candles: noCandles, unknown } = forecast
  if (!daily.length && !noCandles.length && !unknown.length) return null
  const leads: string[] = []
  const parts: string[] = []
  const byTf = (list: Array<{ timeframe: string }>) => [...new Set(list.map((d) => d.timeframe))]
  for (const tf of byTf(noCandles)) {
    const items = noCandles.filter((d) => d.timeframe === tf)
    const names = namesList(items.map((d) => d.symbol))
    leads.push(`Sem candles prováveis em ${tf}: ${names}`)
    const five = items.find((d) => d.five_from_label)?.five_from_label
    parts.push(
      `${five ? `o 5m da Binance começa em ${five}, então ` : ''}` +
        `${items.length === 1 ? 'essa combinação deve terminar' : `essas ${fmtInt(items.length)} combinações devem terminar`} ` +
        'como amostra insuficiente, sem resultado.',
    )
  }
  for (const tf of byTf(daily)) {
    const items = daily.filter((d) => d.timeframe === tf)
    const sentences = items.slice(0, 3).map((d) => {
      const why = d.five_from_label ? `o 15m dele começa em ${d.five_from_label}, então ` : ''
      return `${d.symbol} — ${why}${d.from_label} a ${d.to_label} roda no candle ${tf === '1d' ? 'diário' : `de ${tf}`}.`
    })
    const extra = items.length > 3 ? ` E mais ${fmtInt(items.length - 3)} ${items.length - 3 === 1 ? 'ativo' : 'ativos'}.` : ''
    if (!leads.length) leads.push(`Precisão diária prevista em ${tf}:`)
    else parts.push(`Precisão diária prevista em ${tf}:`)
    parts.push(sentences.join(' ') + extra)
  }
  if (unknown.length) {
    parts.push(`${namesList(unknown)}: sem histórico guardado; a precisão aparece depois da coleta.`)
  }
  parts.push('O resultado sempre marca o trecho.')
  const lead = leads.join(' · ') || 'Precisão prevista:'
  const restText = parts.join(' ')
  return { lead, rest: noCandles.length ? `— ${restText}` : restText }
}

export interface SurvivorshipWindow {
  start?: string | null
  start_label?: string | null
  end?: string | null
  end_label?: string | null
}

export interface Survivorship {
  catalog_as_of?: string | null
  window?: SurvivorshipWindow | null
}

/** `, e a janela começa em 2 jan. 2003` ou `, e a janela é 1 jan. 2019 – 31 dez. 2020`. */
export function survivorshipWindowSuffix(window: SurvivorshipWindow | null | undefined): string {
  if (!window?.start_label) return ''
  if (window.end_label) return `, e a janela é ${window.start_label} – ${window.end_label}`
  return `, e a janela começa em ${window.start_label}`
}

export const SURVIVORSHIP_PREFLIGHT =
  'a varredura usa só os ativos do catálogo de hoje. Ativos que saíram da Binance antes de hoje não entram'

/** Decidir (decisão 12): `… (janela desde 2 jan. 2003). Ativos que saíram da Binance antes de hoje não estão no ranking.` */
export function survivorshipDecidir(window: SurvivorshipWindow | null | undefined): string {
  const when = window?.start_label
    ? window.end_label
      ? ` (janela ${window.start_label} – ${window.end_label})`
      : ` (janela desde ${window.start_label})`
    : ''
  return `esta varredura usou só os ativos do catálogo de hoje${when}. Ativos que saíram da Binance antes de hoje não estão no ranking.`
}

// --- Linha do candidato -----------------------------------------------------------------------------------------

export interface ResultPrecision {
  kind: 'intrabar_15m' | 'daily' | 'candle'
  missing: Array<{ from?: string | null; to?: string | null }>
}

export interface MulticlassRow {
  symbol: string
  timeframe: string
  direction: string
  asset?: ResultAsset | null
  execution?: ExecutionInfo | null
  conventions?: ConventionsInfo | null
  provenance?: { asset_class?: string | null; period_covered?: { start?: string | null; end?: string | null } | null } | null
  start_at?: string | null
  end_at?: string | null
  snapshot_id?: string | null
}

export type Tone = 'info' | 'warn' | 'muted'

export interface RowBlock {
  cls: AssetClass
  currency: string
  lead: string
  precision: { tone: Tone; short: string; full: string }
  conventions: string
  period: string | null
}

export function rowClass(row: Pick<MulticlassRow, 'symbol' | 'asset' | 'provenance'>): AssetClass {
  const stored = row.asset?.asset_class ?? row.provenance?.asset_class
  if (stored === 'crypto' || stored === 'stock' || stored === 'etf') return stored
  return symbolIsCrypto(row.symbol) ? 'crypto' : 'stock'
}

export function rowCurrency(row: Pick<MulticlassRow, 'symbol' | 'asset' | 'provenance'>): string {
  if (row.asset?.currency) return String(row.asset.currency)
  return rowClass(row) === 'crypto' ? row.symbol.split('/')[1] || 'USDT' : 'USD'
}

function zoneOf(cls: AssetClass): string {
  return isEquityClass(cls) ? 'America/New_York' : 'UTC'
}

function dayOf(value: string | null | undefined, cls: AssetClass): string {
  if (!value) return ''
  return formatDatePlain(value, /^\d{4}-\d{2}-\d{2}$/.test(value) ? 'UTC' : zoneOf(cls))
}

function yearOf(value: string | null | undefined): string {
  return value ? String(value).slice(0, 4) : ''
}

export const PRECISION_NOT_RECORDED = 'Precisão: não registrada nesta varredura'

/**
 * Marca de precisão (decisão 6): o texto curto vai na linha ("Precisão diária (2003–2025)"); o trecho exato
 * ("Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025") vai no `title`, para leitor de tela e no modal.
 */
export function rowPrecision(row: MulticlassRow): RowBlock['precision'] {
  const cls = rowClass(row)
  const execution = row.execution ?? null
  if (!execution || !execution.precision_effective) {
    return { tone: 'muted', short: PRECISION_NOT_RECORDED, full: PRECISION_NOT_RECORDED }
  }
  const full = precisionText(execution, cls, row.timeframe)
  if (execution.precision_effective === 'intrabar_15m') return { tone: 'info', short: full.text, full: full.text }
  const missing = execution.intraday_missing ?? []
  if (full.tone !== 'warn' || !missing.length) return { tone: full.tone, short: full.text, full: full.text }
  const first = yearOf(missing[0]?.from)
  const last = yearOf(missing[missing.length - 1]?.to)
  const years = first && last ? (first === last ? first : `${first}–${last}`) : ''
  const name = candleName(execution.timeframe || row.timeframe).title
  return { tone: 'warn', short: years ? `${name} (${years})` : name, full: full.text }
}

/** `2 jan. 2003 – 23 out. 2026` (janela efetiva da execução; sem ela, a proveniência ou o início/fim do resultado). */
export function rowPeriod(row: MulticlassRow): string | null {
  const cls = rowClass(row)
  const covered = row.execution?.window?.covered
  const start = covered?.start ?? row.provenance?.period_covered?.start ?? row.start_at
  const end = covered?.end ?? row.provenance?.period_covered?.end ?? row.end_at
  if (!start || !end) return null
  return `${dayOf(start, cls)} – ${dayOf(end, cls)}`
}

export function rowBlock(row: MulticlassRow): RowBlock {
  const cls = rowClass(row)
  return {
    cls,
    currency: rowCurrency(row),
    lead: `${row.symbol} · ${row.timeframe} · ${row.direction === 'short' ? 'Short' : 'Long'}`,
    precision: rowPrecision(row),
    conventions: conventionsShort(cls, row.conventions ?? null),
    period: rowPeriod(row),
  }
}

/** Amostra no modal (decisão 10): `Amostra 8b41d7e2 · guardada enquanto o favorito existir · Direção Long`. */
export function modalSampleText(row: MulticlassRow): string {
  const direction = row.direction === 'short' ? 'Short' : 'Long'
  if (!row.snapshot_id) return `Amostra não guardada nesta varredura · Direção ${direction}`
  return `Amostra ${row.snapshot_id.replace(/^snap[-_]?/i, '').slice(0, 8)} · guardada enquanto o favorito existir · Direção ${direction}`
}

/** Card #1122 (d2, decisão 12): a Descoberta promove a favorito sem estrela, em qualquer classe. */
export function promotionTitle(_cls: AssetClass): string {
  return 'Promover a favorito'
}

export const PROMOTION_DESTINATION = 'Favoritos · sem estrela'

/** Estado da linha promovida (Decidir e parciais do Acompanhar). */
export const PROMOTED_LABEL = 'Em Favoritos'

/** Nota do destino: fora do Monitor até ganhar estrela (ação/ETF com a configuração). */
export function promotionDestinationNote(cls: AssetClass): string {
  const where = isEquityClass(cls)
    ? 'Onde ver depois: Favoritos, sem estrela e fora do Monitor, com a configuração Binance Ações. '
    : 'Onde ver depois: Favoritos, sem estrela e fora do Monitor. '
  return (
    where +
    'Para acompanhar no Monitor e receber no Telegram, dê pelo menos 1 estrela lá. ' +
    'Reversível: retire o favorito; o histórico da varredura fica.'
  )
}

/** Aviso de sucesso da promoção. */
export function promotionSuccessText(symbol: string, cls: AssetClass, favoriteId: string | null, sweepId: string): string {
  if (isEquityClass(cls)) {
    return `${symbol} entrou em Favoritos sem estrela, com classe, moeda, configuração, precisão, convenções, janela e amostra desta execução.`
  }
  return `${symbol} entrou em Favoritos sem estrela${favoriteId ? ` (favorito ${favoriteId})` : ''}, com origem #${sweepId}.`
}

// --- Filtro Classe e cabeçalho do Decidir --------------------------------------------------------------------------

export type ClassFilter = 'all' | AssetClass
export type ClassCounts = Record<ClassFilter, number>

export function classOptions(
  counts: Partial<ClassCounts> | null | undefined,
  current: ClassFilter,
): Array<{ value: ClassFilter; label: string; disabled: boolean }> {
  const c = { all: 0, crypto: 0, stock: 0, etf: 0, ...(counts ?? {}) }
  const option = (value: ClassFilter, name: string) => ({
    value,
    label: `${name} (${fmtInt(c[value])})`,
    // Opção com 0 fica desabilitada, salvo se já estiver escolhida (dá para voltar com "Limpar filtros").
    disabled: value !== 'all' && c[value] === 0 && current !== value,
  })
  return [option('all', 'Todas'), option('crypto', 'Cripto'), option('stock', 'Ações'), option('etf', 'ETFs')]
}

export function classEmptyText(cls: AssetClass): string {
  const word = cls === 'crypto' ? 'cripto' : cls === 'stock' ? 'ação' : 'ETF'
  return `Nenhum candidato de ${word} nesta varredura.`
}

export function classesPresent(counts: Partial<ClassCounts> | null | undefined): number {
  return CLASS_ORDER.filter((cls) => (counts?.[cls] ?? 0) > 0).length
}

/** `3 classes · janela, candles e amostra em cada linha · taxa por lado: …` (decisão 11). */
export function multiclassMeta(classes: number): string {
  return `${classes} classes · janela, candles e amostra em cada linha · ${DISCOVERY_FEE_BY_CLASS}`
}

export const CALENDAR_COVERAGE_NOTE =
  'Cobertura conta as velas esperadas no calendário da classe: 24/7 na cripto, pregões de Nova York na ação e no ETF ' +
  '(fim de semana e feriado não contam). USD e USDT não se somam nem se convertem: Return, Calmar e CAGR são percentuais ' +
  'da própria moeda do ativo.'

// --- Por ativo -------------------------------------------------------------------------------------------------------

export type AssetState =
  | 'queued'
  | 'collecting'
  | 'running'
  | 'done'
  | 'done_daily'
  | 'insufficient'
  | 'failed'
  | 'not_run'
  | 'mixed'

export interface AssetDetail {
  timeframe: string
  outcome: 'succeeded' | 'insufficient' | 'failed' | 'skipped'
  reason?: string | null
  precision?: ResultPrecision | null
  period?: { start_label?: string | null; end_label?: string | null } | null
}

export interface SweepAsset {
  symbol: string
  asset_class?: AssetClass | null
  currency?: string | null
  done: number
  total: number
  state: AssetState
  stage?: string | null
  series?: string | null
  role?: string | null
  page?: number | null
  pages?: number | null
  attempt?: number | null
  max_attempts?: number | null
  reason?: string | null
  outcomes?: { succeeded: number; daily: number; insufficient: number; failed: number; skipped: number }
  details?: AssetDetail[]
}

export type SweepStateName =
  | 'pending'
  | 'running'
  | 'paused'
  | 'cancelling'
  | 'cancelled'
  | 'failed'
  | 'partial_failure'
  | 'completed'

const IN_FLIGHT: AssetState[] = ['queued', 'collecting', 'running']

function inProgress(asset: SweepAsset): boolean {
  return asset.state === 'collecting' || asset.state === 'running'
}

function hasFailure(asset: SweepAsset): boolean {
  return asset.state === 'failed' || (asset.outcomes?.failed ?? 0) > 0
}

function hasInsufficient(asset: SweepAsset): boolean {
  return asset.state === 'insufficient' || (asset.outcomes?.insufficient ?? 0) > 0
}

/** Ordem do quadro (decisão 7): ativo em curso, falhas, amostras insuficientes e o resto na ordem da varredura. */
export function orderAssets(assets: SweepAsset[], cancelled = false): SweepAsset[] {
  const rank = (a: SweepAsset) =>
    !cancelled && inProgress(a) ? 0 : hasFailure(a) ? 1 : hasInsufficient(a) ? 2 : 3
  return assets
    .map((asset, index) => ({ asset, index }))
    .sort((x, y) => rank(x.asset) - rank(y.asset) || x.index - y.index)
    .map((item) => item.asset)
}

export const ASSET_PAGE = 50

export function countText(asset: SweepAsset): string {
  return `${fmtInt(asset.done)} de ${fmtInt(asset.total)} ${asset.total === 1 ? 'combinação' : 'combinações'}`
}

function plural(n: number, one: string, many: string): string {
  return `${fmtInt(n)} ${n === 1 ? one : many}`
}

function seriesLabel(asset: SweepAsset): string {
  const series = asset.series || asset.stage || ''
  return asset.role === 'intraday' ? `${series} do intrabar` : series
}

function pageText(asset: SweepAsset): string {
  if (!asset.page) return ''
  return ` · página ${fmtInt(asset.page)}${asset.pages ? ` de ${fmtInt(asset.pages)}` : ''}`
}

function precisionDetail(detail: AssetDetail, cls: AssetClass, timeframe: string): string {
  const p = detail.precision
  if (!p) return PRECISION_NOT_RECORDED
  if (p.kind === 'intrabar_15m') return 'Precisão intrabar (15m)'
  const name = candleName(timeframe).title
  const stretch = (p.missing ?? [])
    .filter((m) => m.from && m.to)
    .map((m) => `${dayOf(m.from, cls)} a ${dayOf(m.to, cls)}`)
    .join(' e ')
  return stretch ? `${name} · sem 15m de ${stretch}` : name
}

function periodDetail(detail: AssetDetail): string {
  const p = detail.period
  return p?.start_label && p?.end_label ? ` · período efetivo ${p.start_label} – ${p.end_label}` : ''
}

function detailText(asset: SweepAsset, cls: AssetClass, withTimeframe: boolean): string {
  return (asset.details ?? [])
    .map((d) => {
      const prefix = withTimeframe ? `${d.timeframe}: ` : ''
      if (d.outcome === 'succeeded') return `${prefix}${precisionDetail(d, cls, d.timeframe)}${periodDetail(d)}`
      if (d.outcome === 'insufficient') return `${prefix}Amostra insuficiente — ${d.reason ?? 'amostra abaixo do mínimo'}`
      if (d.outcome === 'failed') return `${prefix}Falha — ${d.reason ?? 'falha operacional'}`
      return `${prefix}Não rodou · varredura cancelada`
    })
    .join(' · ')
}

export type StateIcon = 'ok' | 'warn' | 'info' | 'fail' | 'clock' | 'load'

export interface AssetStateView {
  key: string
  icon: StateIcon
  label: string
  detail: string
}

/** Estado e detalhe de uma linha do "Por ativo" (decisão 7), sempre com ícone + texto. */
export function assetStateView(asset: SweepAsset, sweepState: SweepStateName): AssetStateView {
  const cls: AssetClass = asset.asset_class ?? (symbolIsCrypto(asset.symbol) ? 'crypto' : 'stock')
  const paused = sweepState === 'paused'
  const cancelled = sweepState === 'cancelled' || sweepState === 'cancelling'
  const multi = (asset.details?.length ?? 0) > 1 || asset.total > 1
  const tries = asset.attempt && asset.attempt > 1 ? ` · tentativa ${asset.attempt} de ${asset.max_attempts ?? 3}` : ''
  if (cancelled && IN_FLIGHT.includes(asset.state) && sweepState === 'cancelled') {
    return {
      key: 'queued',
      icon: 'clock',
      label: 'Não rodou · varredura cancelada',
      detail: 'Combinações pendentes viraram ignoradas; os resultados concluídos ficam.',
    }
  }
  switch (asset.state) {
    case 'collecting':
      if (paused) {
        return {
          key: 'paused',
          icon: 'warn',
          label: `Pausado na coleta · ${seriesLabel(asset)}${pageText(asset)} · retoma daqui`,
          detail: '',
        }
      }
      return {
        key: 'collecting',
        icon: 'load',
        label: `Coletando histórico · ${seriesLabel(asset)}${pageText(asset)}${tries}${asset.reason && tries ? ` · ${asset.reason}` : ''}`,
        detail: '',
      }
    case 'running':
      if (paused) {
        return { key: 'paused', icon: 'warn', label: `Pausado · ${asset.stage ?? ''} · retoma daqui`, detail: '' }
      }
      return { key: 'running', icon: 'load', label: `Rodando · ${asset.stage ?? ''}${tries}`, detail: '' }
    case 'queued':
      if (asset.attempt && asset.reason) {
        return {
          key: 'collecting',
          icon: 'load',
          label: `Na fila · ${asset.stage ?? ''} · nova tentativa (${asset.attempt + 1} de ${asset.max_attempts ?? 3}) · ${asset.reason}`,
          detail: '',
        }
      }
      return { key: 'queued', icon: 'clock', label: 'Na fila', detail: asset.done ? detailText(asset, cls, true) : '' }
    case 'done':
      return { key: 'done', icon: 'ok', label: 'Concluído', detail: detailText(asset, cls, multi) }
    case 'done_daily': {
      const detail = detailText(asset, cls, multi).replace(/^(Precisão diária|Precisão do candle de \w+) · s/, 'S')
      return { key: 'done_daily', icon: 'warn', label: 'Concluído · precisão diária', detail }
    }
    case 'insufficient':
      return {
        key: 'insufficient',
        icon: 'warn',
        label: `Amostra insuficiente: ${asset.reason ?? 'amostra abaixo do mínimo'}`,
        detail: multi ? detailText(asset, cls, true) : 'Nenhum resultado; a combinação não entra no ranking.',
      }
    case 'failed':
      return {
        key: 'failed',
        icon: 'fail',
        label: `Falha: ${asset.reason ?? 'falha operacional'}`,
        detail: 'Nenhum resultado; a combinação não entra no ranking nem vira amostra suficiente.',
      }
    case 'not_run':
      return {
        key: 'queued',
        icon: 'clock',
        label: 'Não rodou · varredura cancelada',
        detail: 'Combinações pendentes viraram ignoradas; os resultados concluídos ficam.',
      }
    case 'mixed': {
      const o = asset.outcomes ?? { succeeded: 0, daily: 0, insufficient: 0, failed: 0, skipped: 0 }
      const parts: string[] = []
      if (o.succeeded) parts.push(plural(o.succeeded, 'concluída', 'concluídas'))
      if (o.insufficient) parts.push(plural(o.insufficient, 'amostra insuficiente', 'amostras insuficientes'))
      if (o.failed) parts.push(plural(o.failed, 'falha', 'falhas'))
      if (o.skipped) parts.push(plural(o.skipped, 'não rodou', 'não rodaram'))
      return {
        key: o.failed ? 'mixed_failed' : 'insufficient',
        icon: o.failed ? 'fail' : 'warn',
        label: parts.join(' · '),
        detail: detailText(asset, cls, true),
      }
    }
    default:
      return { key: 'queued', icon: 'clock', label: 'Na fila', detail: '' }
  }
}

/** Linha viva (decisão 7): só o ativo e a etapa em curso. */
export function liveAnnouncement(assets: SweepAsset[], sweepState: SweepStateName): string {
  if (sweepState === 'paused') return 'Varredura pausada.'
  if (sweepState === 'cancelled') return 'Varredura cancelada.'
  if (sweepState === 'completed') return 'Varredura concluída.'
  if (sweepState === 'partial_failure') return 'Varredura concluída com falhas.'
  if (sweepState === 'failed') return 'Varredura falhou.'
  const current = assets.find(inProgress)
  if (!current) return ''
  if (current.state === 'collecting') {
    return `${current.symbol}: coletando histórico · ${seriesLabel(current)}${pageText(current)}`
  }
  return `${current.symbol}: rodando · ${current.stage ?? ''}`
}

// --- "Sem resultado" no Decidir ----------------------------------------------------------------------------------

export interface NoResultNote {
  kind: 'failed' | 'cancelled' | 'insufficient'
  parts: Array<{ lead: string; text: string }>
}

const TERMINAL: SweepStateName[] = ['cancelled', 'failed', 'partial_failure', 'completed']

/** Quem ficou sem resultado (decisão 7): falha, "não rodou" e amostra insuficiente nunca somem do Decidir. */
export function noResultNote(assets: SweepAsset[] | null | undefined, sweepState: SweepStateName): NoResultNote | null {
  if (!assets?.length || !TERMINAL.includes(sweepState)) return null
  const failed = assets.filter(hasFailure)
  const notRun = assets.filter(
    (a) => a.state === 'not_run' || (a.state === 'mixed' && (a.outcomes?.skipped ?? 0) > 0) || IN_FLIGHT.includes(a.state),
  )
  const insufficient = assets.flatMap((a) =>
    (a.details ?? []).filter((d) => d.outcome === 'insufficient').map((d) => ({ asset: a, detail: d })),
  )
  const parts: NoResultNote['parts'] = []
  let kind: NoResultNote['kind'] | null = null
  if (failed.length) {
    const reasons = failed
      .flatMap((a) => (a.details ?? []).filter((d) => d.outcome === 'failed').map((d) => d.reason))
      .filter(Boolean) as string[]
    const generic = reasons.length && reasons.every((r) => r.startsWith('a Binance não respondeu'))
      ? 'a Binance não respondeu ao histórico nas 3 tentativas'
      : reasons[0] ?? 'falha operacional'
    parts.push({ lead: 'Sem resultado:', text: `${namesList(failed.map((a) => a.symbol))} — Falha: ${generic}.` })
    kind = 'failed'
  }
  if (notRun.length && (sweepState === 'cancelled' || notRun.some((a) => a.state === 'not_run' || (a.outcomes?.skipped ?? 0) > 0))) {
    parts.push({ lead: 'Sem resultado:', text: `${namesList(notRun.map((a) => a.symbol))} — Não rodou · varredura cancelada.` })
    kind = kind ?? 'cancelled'
  }
  if (insufficient.length) {
    const noCandles = insufficient.every((i) => (i.detail.reason ?? '').startsWith('sem candles'))
    const names = namesList(insufficient.map((i) => `${i.asset.symbol} ${i.detail.timeframe}`))
    parts.push({
      lead: 'Amostra insuficiente:',
      text: `${names} — ${noCandles ? 'sem candles nessa janela' : 'amostra abaixo do mínimo'}; as linhas ficam sem rank e sem Promover.`,
    })
    kind = kind ?? 'insufficient'
  }
  return kind ? { kind, parts } : null
}
