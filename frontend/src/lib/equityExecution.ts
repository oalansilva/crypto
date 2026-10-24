/**
 * Identidade, precisão efetiva e convenções de uma execução (card #1119, decisões 7, 12, 16 e 19).
 *
 * Lógica pura, sem DOM e sem rede, para ser testada com `tsx --test`. Os textos são os do protótipo
 * aprovado (`frontend/public/prototypes/card-1119-backtest-acoes-etfs/`): o componente só os desenha.
 */

import { formatDate } from './assetSelection'

export type ResultAssetClass = 'crypto' | 'stock' | 'etf'

export interface ResultAsset {
  symbol: string
  asset_id?: string | null
  asset_class?: ResultAssetClass | null
  name?: string | null
  currency?: string | null
}

export interface IntradayStretch {
  from: string
  to: string
}

export interface CollectionNote {
  status: 'partial'
  /** Onde a coleta parou: no começo da janela, no fim ou nos dois. */
  kind?: 'head' | 'tail' | 'both'
  series: string
  symbol: string
  reason: string
  stopped_after: string
  covered: { start?: string | null; end?: string | null; candles?: number }
  requested: { start?: string | null; end?: string | null }
  left_out: Array<{ from: string; to: string }>
}

export interface ExecutionInfo {
  precision_requested?: 'intrabar' | 'daily'
  precision_effective?: 'intrabar_15m' | 'candle'
  timeframe?: string
  intraday_missing?: IntradayStretch[]
  intraday_reason?: 'missing' | 'coverage' | 'read_error' | 'no_window' | null
  intraday_error?: string | null
  gap_stops?: number
  window?: {
    requested?: { start?: string | null; end?: string | null }
    covered?: { start?: string | null; end?: string | null; candles?: number }
  }
  collection?: CollectionNote | null
}

export interface ConventionsInfo {
  fee?: number
  fee_confirmed?: boolean
  slippage?: number
  calendar?: { kind?: string; timezone?: string; years?: string; sessions_per_year?: number | null }
  fraction?: { simulated?: boolean; confirms_account?: boolean } | null
  short?: { simulated?: boolean; confirms_account?: boolean } | null
  gap_exit?: { enabled?: boolean; stops_with_gap?: number }
  adjusted_prices?: boolean
}

export interface ProvenanceInfo {
  data_source?: string
  asset_class?: string
  session?: string
  adjustment?: string
  timeframe_origin?: string
  version_label?: string
  data_version?: number
  snapshot_id?: string | null
  kept_until?: string | null
}

export interface GapTradeLike {
  exit_time?: string
  exit_price?: number
  stop_price?: number
  exit_reason?: string
}

export const NY_ZONE = 'America/New_York'

export function isEquityClass(cls: string | null | undefined): boolean {
  return cls === 'stock' || cls === 'etf'
}

export const CLASS_CHIP_LABEL: Record<ResultAssetClass, string> = {
  crypto: 'Cripto',
  stock: 'Ação',
  etf: 'ETF',
}

/** Moeda da classe: USDT para cripto, USD para ação e ETF (decisão 13). */
export function currencyOf(asset: ResultAsset | null | undefined, symbol?: string): string {
  if (asset?.currency) return asset.currency
  if (isEquityClass(asset?.asset_class)) return 'USD'
  const sym = asset?.symbol ?? symbol ?? ''
  const quote = sym.includes('/') ? sym.split('/')[1] : ''
  return quote || 'USDT'
}

// --- Números e datas ------------------------------------------------------------------------

const PT = 'pt-BR'

export function pct(value: number, digits = 3): string {
  const text = (value * 100).toLocaleString(PT, { maximumFractionDigits: digits })
  return `${text}%`
}

export function money(value: number): string {
  return value.toLocaleString(PT, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const DATE_ONLY = /^\d{4}-\d{2}-\d{2}$/

/** Data só de dia ("2024-01-31") vale como está (UTC); instante vale no fuso informado. */
function day(iso: string | null | undefined, zone: string): string {
  if (!iso) return ''
  return formatDate(iso, DATE_ONLY.test(iso) ? 'UTC' : zone)
}

/** Candles de 1d de ação/ETF vêm na meia-noite de Nova York; o dia vale nesse fuso. */
function zoneOf(asset: ResultAsset | null | undefined): string {
  return isEquityClass(asset?.asset_class) ? NY_ZONE : 'UTC'
}

// --- Linha de proveniência ----------------------------------------------------------------------

const ADJUSTMENT_LABEL: Record<string, string> = {
  adjusted: 'ajustado por split',
  raw: 'sem ajuste',
}

export function provenanceLine(asset: ResultAsset | null | undefined, provenance?: ProvenanceInfo | null): string {
  if (isEquityClass(asset?.asset_class)) {
    const adjustment = ADJUSTMENT_LABEL[provenance?.adjustment ?? 'adjusted'] ?? 'ajustado por split'
    return `Binance Ações · pregão regular de Nova York · ${adjustment} · ${currencyOf(asset)}`
  }
  return `Binance Spot · 24/7 · ajuste não se aplica · ${currencyOf(asset)}`
}

// --- Precisão -----------------------------------------------------------------------------------

export type PrecisionTone = 'info' | 'warn'

export interface PrecisionView {
  tone: PrecisionTone
  title: string
  text: string
  /** Valor do fato "Precisão" e a linha de apoio. */
  fact: string
  factNote: string | null
}

/** Nome do tempo na precisão: "diária" só no 1d; nos demais, "do candle de 4h". */
export function candleName(timeframe: string | null | undefined): { title: string; fact: string; text: string } {
  const tf = String(timeframe || '1d').toLowerCase()
  if (tf === '1d') return { title: 'Precisão diária', fact: 'Diária', text: 'candle diário' }
  return { title: `Precisão do candle de ${tf}`, fact: `Candle de ${tf}`, text: `candle de ${tf}` }
}

function stretchText(stretches: IntradayStretch[], zone: string): string {
  return stretches
    .map((s) => {
      const from = day(s.from, zone) || s.from
      const to = day(s.to, zone) || s.to
      return from === to ? `em ${from}` : `de ${from} a ${to}`
    })
    .join(' e ')
}

export function precisionView(
  execution: ExecutionInfo | null | undefined,
  options: { asset?: ResultAsset | null; page?: 'result' | 'optimize' } = {},
): PrecisionView | null {
  if (!execution || !execution.precision_effective) return null
  const equity = isEquityClass(options.asset?.asset_class)
  const timeframe = execution.timeframe || '1d'
  const name = candleName(timeframe)
  const asker = options.page === 'optimize' ? 'A Otimização pede precisão intrabar' : 'Você pediu precisão intrabar'

  if (execution.precision_effective === 'intrabar_15m') {
    return {
      tone: 'info',
      title: 'Precisão intrabar 15m',
      text: equity
        ? 'O 15m, montado do 5m no pregão, cobre a janela inteira: stops e saídas foram simulados candle a candle de 15m.'
        : 'O 15m cobre a janela inteira: stops e saídas foram simulados candle a candle de 15m.',
      fact: 'Intrabar 15m',
      factNote: equity ? 'Montado do 5m' : null,
    }
  }
  if (execution.precision_requested === 'daily' || !execution.intraday_reason) {
    return {
      tone: 'info',
      title: `${name.title}, escolhida`,
      text: `O Deep Backtest estava desligado: stops e saídas foram simulados no ${name.text}.`,
      fact: name.fact,
      factNote: 'Deep Backtest desligado',
    }
  }
  if (execution.intraday_reason === 'read_error') {
    return {
      tone: 'warn',
      title: name.title,
      text: `Não foi possível ler o intradiário de 15m desta janela (falha ao ler o histórico guardado). O stop foi simulado no ${name.text} em toda a janela.`,
      fact: name.fact,
      factNote: 'Pedida: intrabar 15m',
    }
  }
  const zone = zoneOf(options.asset)
  const stretches = execution.intraday_missing ?? []
  return {
    tone: 'warn',
    title: name.title,
    text:
      `O intradiário de 15m faltou ${stretchText(stretches, zone)}. ${asker}; como ele não cobre a janela, ` +
      `o stop foi simulado no ${name.text} em toda a janela.`,
    fact: name.fact,
    factNote: 'Pedida: intrabar 15m',
  }
}

/** Nota âmbar "Janela coberta menor que a pedida" (coleta que parou com parte gravada). */
export function coverageNote(execution: ExecutionInfo | null | undefined): { title: string; text: string } | null {
  const note = execution?.collection
  if (!note || note.status !== 'partial') return null
  const zone = NY_ZONE
  const from = day(note.covered?.start, zone)
  const to = day(note.covered?.end, zone)
  const left = (note.left_out ?? []).map((l) => `de ${day(l.from, zone)} a ${day(l.to, zone)}`).join(' e ')
  const stopped =
    note.kind === 'head'
      ? `A coleta do ${note.series} de ${note.symbol} parou antes de chegar ao início da janela (${note.reason}): só há histórico guardado desde ${from}.`
      : `A coleta do ${note.series} de ${note.symbol} parou depois de guardar até ${day(note.stopped_after, zone)} (${note.reason}).`
  return {
    title: 'Janela coberta menor que a pedida',
    text: `${stopped} O backtest rodou no trecho guardado, de ${from} a ${to}; ${left} ficou fora. Rode de novo mais tarde para completar.`,
  }
}

// --- Tempo gráfico, custo e anualização ------------------------------------------------------------

const EQUITY_TF_FACT: Record<string, [string, string]> = {
  '1d': ['1d nativo', '1 candle por pregão'],
  '1h': ['1h montado do 5m', '09:30, 10:30 … 15:30–16:00; nenhum candle atravessa o fechamento'],
  '4h': [
    '4h montado do 5m',
    '09:30–13:30 e 13:30–16:00 (meio-pregão: 09:30–13:00); nenhum candle atravessa o fechamento',
  ],
  '15m': ['15m montado do 5m', '09:30, 09:45 … 15:45–16:00; nenhum candle atravessa o fechamento'],
}

export function timeframeFact(
  asset: ResultAsset | null | undefined,
  timeframe: string,
): { value: string; note: string | null } {
  const tf = timeframe.toLowerCase()
  if (isEquityClass(asset?.asset_class)) {
    const row = EQUITY_TF_FACT[tf]
    if (row) return { value: row[0], note: row[1] }
  }
  return { value: `${tf} nativo`, note: null }
}

export function annualizationText(): string {
  return 'Anos pelo calendário (dias corridos ÷ 365). Sharpe e Sortino por operação, sem anualização.'
}

// --- Fatos --------------------------------------------------------------------------------------------

export interface Fact {
  key: string
  label: string
  value: string
  note?: string | null
}

export interface ExecutionTexts {
  provenance: string
  precision: PrecisionView | null
  coverage: { title: string; text: string } | null
  facts: Fact[]
  conventions: Array<{ key: string; label: string; text: string }>
  alerts: string[]
}

interface BuildInput {
  asset: ResultAsset | null | undefined
  provenance?: ProvenanceInfo | null
  execution: ExecutionInfo
  conventions?: ConventionsInfo | null
  timeframe: string
  periodAll?: boolean
  gapTrades?: GapTradeLike[]
  page?: 'result' | 'optimize'
  /** Datas da janela pedida (formulário), quando a execução não as trouxe. */
  requestedFallback?: { start?: string | null; end?: string | null }
  /** Linha de apoio da janela pedida (Otimização: "Período fixo desta tela"). */
  requestedNote?: string
}

function windowRange(start: string | null | undefined, end: string | null | undefined, zone: string): string {
  const a = day(start, zone)
  const b = day(end, zone)
  if (a && b) return `${a} – ${b}`
  return a || b || '—'
}

function gapExample(trades: GapTradeLike[] | undefined, equity: boolean, timeframe: string): string | null {
  const first = (trades ?? []).find((t) => t.exit_reason === 'stop_loss_gap')
  if (!first || first.stop_price == null || first.exit_price == null || !first.exit_time) return null
  const zone = equity ? NY_ZONE : 'UTC'
  const when = day(first.exit_time, zone)
  let place = ''
  if (equity && timeframe !== '1d') {
    const hm = new Intl.DateTimeFormat('en-GB', { timeZone: NY_ZONE, hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(first.exit_time))
    place = hm === '09:30' ? ', abertura do pregão' : `, ${hm}`
  }
  return `${when}${place}: stop ${money(first.stop_price)}, abertura ${money(first.exit_price)}`
}

export function buildExecutionTexts(input: BuildInput): ExecutionTexts {
  const { asset, execution, conventions, provenance } = input
  const timeframe = (execution.timeframe || input.timeframe || '1d').toLowerCase()
  const equity = isEquityClass(asset?.asset_class)
  const zone = zoneOf(asset)
  const precision = precisionView(execution, { asset, page: input.page })
  const coverage = coverageNote(execution)
  const gaps = Number(execution.gap_stops ?? conventions?.gap_exit?.stops_with_gap ?? 0)
  const cls = asset?.asset_class ? CLASS_CHIP_LABEL[asset.asset_class] : ''
  const tf = timeframeFact(asset, timeframe)
  const adjustmentLabel = ADJUSTMENT_LABEL[provenance?.adjustment ?? 'adjusted'] ?? 'ajustado por split'
  // "a série ajustada por split" (feminino), como no protótipo
  const adjustmentSeries = adjustmentLabel.replace(/^ajustado/, 'ajustada')
  const requested = execution.window?.requested
  const covered = execution.window?.covered
  const requestedStart = requested?.start ?? input.requestedFallback?.start ?? null
  const requestedEnd = requested?.end ?? input.requestedFallback?.end ?? null

  const facts: Fact[] = [
    { key: 'asset', label: 'Ativo', value: `${asset?.symbol ?? ''}${cls ? ` · ${cls}` : ''}`, note: asset?.name || null },
    equity
      ? { key: 'source', label: 'Fonte e sessão', value: 'Binance Ações', note: 'Pregão regular de Nova York, 09:30–16:00 (horário de Nova York)' }
      : { key: 'source', label: 'Fonte e sessão', value: 'Binance Spot', note: '24/7' },
    equity
      ? {
          key: 'adjustment',
          label: 'Ajuste e moeda',
          value: adjustmentLabel[0].toUpperCase() + adjustmentLabel.slice(1),
          note: 'USD, sem conversão para USDT',
        }
      : { key: 'adjustment', label: 'Ajuste e moeda', value: 'Ajuste não se aplica', note: currencyOf(asset) },
    { key: 'timeframe', label: 'Tempo gráfico', value: tf.value, note: tf.note },
    {
      key: 'requested',
      label: 'Janela pedida',
      value: input.periodAll || (!requestedStart && !requestedEnd) ? 'Todo o histórico' : windowRange(requestedStart, requestedEnd, zone),
      note: input.requestedNote ?? null,
    },
    {
      key: 'covered',
      label: 'Janela coberta',
      value: windowRange(covered?.start, covered?.end, zone),
      note: coverage
        ? execution.collection?.kind === 'head'
          ? `Coleta parou antes do início; pedida desde ${day(requestedStart, zone)}`
          : `Coleta parou em ${day(execution.collection?.stopped_after, zone)}; pedida até ${day(requestedEnd, zone) || 'hoje'}`
        : covered?.candles != null
          ? `${covered.candles.toLocaleString(PT)} ${equity && timeframe === '1d' ? 'pregões' : 'candles'}`
          : null,
    },
    sampleFact(equity, provenance),
    {
      key: 'precision',
      label: 'Precisão',
      value: precision?.fact ?? '—',
      note: precision?.factNote ?? null,
    },
  ]

  const conv: ExecutionTexts['conventions'] = []
  const example = gapExample(input.gapTrades, equity, timeframe)
  const gapNow =
    gaps === 0
      ? 'Nesta execução: nenhuma saída com gap.'
      : `Nesta execução: ${gaps} ${gaps === 1 ? 'saída' : 'saídas'} com gap${example ? ` (${example})` : ''}.`
  conv.push({
    key: 'gap',
    label: 'Gap no stop',
    text:
      'Se o candle abre além do stop, a saída é na abertura, com taxa e slippage, e não no preço do stop. ' +
      gapNow +
      (equity ? '' : ' Resultados e favoritos de cripto calculados antes desta regra podem ter número melhor onde houve gap.'),
  })
  if (conventions?.short) {
    conv.push({
      key: 'short',
      label: 'Short simulado',
      text: 'A venda a descoberto é só da simulação: não indica que a sua conta na Binance pode vender a descoberto.',
    })
  }
  const feeText = conventions?.fee != null ? `${pct(conventions.fee)} por lado` : '0,075% por lado'
  const slipText = conventions?.slippage != null ? `${pct(conventions.slippage)} por lado no ${timeframe}` : null
  if (equity) {
    const confirmed = conventions?.fee_confirmed === true
    conv.push({
      key: 'costs',
      label: 'Custos',
      text: confirmed
        ? `Taxa de ${feeText}, confirmada na Binance Ações.${slipText ? ` Slippage de ${slipText}.` : ''}`
        : `Taxa de ${feeText}, assumida: a taxa da Binance Ações ainda não foi confirmada.${slipText ? ` Slippage de ${slipText}.` : ''}`,
    })
    conv.push({
      key: 'fraction',
      label: 'Posição com fração',
      text: `Cada operação usa o capital inteiro, com fração de ${asset?.asset_class === 'etf' ? 'cota' : 'ação'}. Isso não confirma que a sua conta na Binance compra fração.`,
    })
    conv.push({
      key: 'calendar',
      label: 'Calendário',
      text: 'Só pregões da bolsa de Nova York, com o horário de verão de lá. Noite, fim de semana e feriado não viram candle nem lacuna.',
    })
  } else {
    conv.push({
      key: 'costs',
      label: 'Custos',
      text: `Taxa de ${feeText}${slipText ? ` e slippage de ${slipText}` : ''}.`,
    })
    conv.push({ key: 'calendar', label: 'Calendário', text: '24/7, sem sessão.' })
  }
  conv.push({ key: 'annualization', label: 'Anualização', text: annualizationText() })
  if (equity) {
    conv.push({
      key: 'adjusted',
      label: 'Preços ajustados',
      text: `Entrada, saída e stop usam a série ${adjustmentSeries} e podem diferir do preço negociado na época.`,
    })
  }

  const alerts: string[] = []
  if (coverage) alerts.push('janela coberta menor que a pedida')
  if (gaps > 0) alerts.push(`${gaps} ${gaps === 1 ? 'saída' : 'saídas'} com gap`)
  if (conventions?.short) alerts.push('short simulado')
  if (equity && conventions?.fee_confirmed === false) alerts.push('taxa assumida')
  if (equity) alerts.push('posição com fração')

  return {
    provenance: provenanceLine(asset, provenance),
    precision,
    coverage,
    facts,
    conventions: conv,
    alerts,
  }
}

function sampleFact(equity: boolean, provenance: ProvenanceInfo | null | undefined): Fact {
  const label = 'Amostra'
  if (!provenance || !provenance.version_label) {
    return {
      key: 'sample',
      label,
      value: 'Não guardada nesta execução',
      note: equity ? 'Ação e ETF não viram favorito: vale o prazo de 30 dias.' : 'Ao favoritar, Favoritos guarda a amostra do último refresh.',
    }
  }
  const until = provenance.kept_until ? ` · guardada até ${formatDate(provenance.kept_until)}` : ''
  return {
    key: 'sample',
    label,
    value: `Versão ${provenance.version_label}${until}`,
    note: equity ? 'Ação e ETF não viram favorito: vale o prazo de 30 dias.' : 'Ao favoritar, Favoritos guarda a amostra do último refresh.',
  }
}

/** Texto do botão que abre os fatos no celular: "8 fatos · 6 convenções". */
export function toggleMeta(texts: ExecutionTexts): string {
  const n = texts.conventions.length
  return `${texts.facts.length} fatos · ${n} ${n === 1 ? 'convenção' : 'convenções'}`
}

// --- Favoritar recusado -----------------------------------------------------------------------------------

export const FAVORITE_REFUSED_REASON =
  'Ações e ETFs ainda não podem ser favoritados: atualização diária e alertas dessas classes ainda não existem.'

// --- Hora de Nova York na lista de operações ----------------------------------------------------------------

export interface NyStamp {
  date: string
  time: string
}

const MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

/** `Aug 27, 2026` + `09:30 EDT` (EST fora do horário de verão), sempre no fuso de Nova York. */
export function nyStamp(iso: string | undefined | null): NyStamp | null {
  if (!iso) return null
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return null
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: NY_ZONE,
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZoneName: 'short',
  }).formatToParts(date)
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? ''
  const hour = get('hour') === '24' ? '00' : get('hour')
  return {
    date: `${MONTHS_EN[Number(get('month')) - 1]} ${Number(get('day'))}, ${get('year')}`,
    time: `${hour}:${get('minute')} ${get('timeZoneName')}`,
  }
}
