/**
 * Lógica pura do seletor de ativos (card #1117): tipos do catálogo, contagem da
 * seleção, o que roda e o que fica fora, e os textos que o protótipo aprovado
 * mostra antes e depois do clique. Sem DOM e sem rede, para ser testada com
 * `tsx --test`.
 */

export type AssetClass = 'crypto' | 'stock' | 'etf'
export type AssetState =
  | 'tradable'
  | 'suspended'
  | 'off_market'
  | 'no_trading'
  | 'no_rules'
  | 'removed'
export type ClassFilter = 'all' | AssetClass

/** Lacuna de uma série: primeiro e último candle esperado que não veio (UTC). */
export interface HistoryGap {
  start: string
  end: string
  count: number
  /** 15m montado do 5m: a falta é a mesma do 5m e não soma no resumo da linha. */
  inherited_from?: '5m' | null
  /** Fim do bloco de 15m (só nas lacunas herdadas). */
  block_end?: string
}

export interface HistoryTimeframe {
  timeframe: string
  from: string | null
  to: string | null
  candles?: number
  /** `null`: lacunas ainda desconhecidas (série fora da autoridade nova). */
  gap_count: number | null
  gaps: HistoryGap[]
  updated_at: string | null
  origin: 'native' | 'derived'
  derived_from?: string | null
  state?: 'idle' | 'collecting' | 'failed'
  insufficient?: boolean
  incomplete?: boolean
  pages_done?: number
  requested_since?: string | null
  starts_at?: string | null
  error?: string | null
  error_at?: string | null
}

export type HistoryStatus = 'on_demand' | 'collecting' | 'covered' | 'partial' | 'failed' | 'frozen' | 'none'

/** Cobertura do histórico de um ativo (card #1118): vem de `market_series_coverage`. */
export interface AssetHistory {
  status: HistoryStatus
  from: string | null
  to: string | null
  updated_at?: string | null
  gap_count?: number | null
  timeframes?: HistoryTimeframe[]
  note?: string | null
  calendar_timezone?: string | null
  collecting?: { timeframe: string; page: number; requested_at: string | null } | null
  error?: { timeframe: string; code: string | null; message: string | null; at: string | null } | null
  partial?: {
    timeframe: string
    requested_since: string | null
    starts_at: string | null
    insufficient: boolean
  } | null
}

export interface CatalogAsset {
  asset_id: string
  asset_class: AssetClass
  symbol: string
  name: string
  state: AssetState
  state_label: string
  state_reason: string | null
  info_note?: string | null
  removed_at?: string | null
  selectable: boolean
  analysis_available: boolean
  history: AssetHistory
}

export interface ClassFreshness {
  status: 'ok' | 'stale' | 'unavailable'
  updated_at: string | null
  last_attempt_at: string | null
  reason: string | null
  code: string | null
  refreshing: boolean
}

export type FreshnessMap = Record<AssetClass, ClassFreshness>

export interface ClassCount {
  total: number | null
  eligible: number | null
}

export type CountsMap = Record<'all' | AssetClass, ClassCount>

export const CLASS_LABEL: Record<AssetClass, string> = {
  crypto: 'Cripto',
  stock: 'Ação',
  etf: 'ETF',
}

export const CLASS_FILTER_LABEL: Record<ClassFilter, string> = {
  all: 'Todas',
  crypto: 'Cripto',
  stock: 'Ações',
  etf: 'ETFs',
}

export const PAGE_SIZE = 6
export const EQUITY_REASON = 'análise ainda não disponível para ações e ETFs'
export const MISSING_REASON = 'ativo fora do catálogo da Binance'
export const TOP10_SYMBOLS = [
  'BTC/USDT',
  'ETH/USDT',
  'BNB/USDT',
  'SOL/USDT',
  'XRP/USDT',
  'ADA/USDT',
  'DOGE/USDT',
  'AVAX/USDT',
  'MATIC/USDT',
  'LINK/USDT',
]

export function fmtInt(value: number): string {
  return value.toLocaleString('pt-BR')
}

export function isMarked(asset: Pick<CatalogAsset, 'state'>): boolean {
  return asset.state !== 'tradable'
}

export function symbolIsCrypto(symbol: string): boolean {
  return symbol.includes('/')
}

export function normalizeSymbol(symbol: string): string {
  return String(symbol || '').trim().toUpperCase()
}

/** Sem repetição e na ordem em que chegaram. */
export function mergeSymbols(current: string[], added: string[]): string[] {
  const seen = new Set(current.map(normalizeSymbol))
  const next = [...current]
  for (const raw of added) {
    const symbol = normalizeSymbol(raw)
    if (!symbol || seen.has(symbol)) continue
    seen.add(symbol)
    next.push(symbol)
  }
  return next
}

// --- Datas ------------------------------------------------------------------------

const MONTHS = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.']

function dateParts(iso: string, timeZone: string) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return null
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone,
    day: '2-digit',
    month: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(date)
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? ''
  return {
    day: get('day'),
    month: Number(get('month')),
    year: get('year'),
    hour: get('hour') === '24' ? '00' : get('hour'),
    minute: get('minute'),
  }
}

/** `20 out. 2026` (dia do catálogo, no fuso informado). */
export function formatDate(iso: string | null | undefined, timeZone = 'America/Sao_Paulo'): string {
  if (!iso) return ''
  const p = dateParts(iso, timeZone)
  return p ? `${p.day} ${MONTHS[p.month - 1]} ${p.year}` : ''
}

/** `20 out. 2026, 06:00`. */
export function formatDateTime(iso: string | null | undefined, timeZone = 'America/Sao_Paulo'): string {
  if (!iso) return ''
  const p = dateParts(iso, timeZone)
  return p ? `${p.day} ${MONTHS[p.month - 1]} ${p.year}, ${p.hour}:${p.minute}` : ''
}

// --- Fatos de cada linha ------------------------------------------------------------

/** Estado vazio de uma classe: o texto diz quando a coleta começa (sem botão nem outro gatilho). */
export const ON_DEMAND_TEXT: Record<AssetClass, string> = {
  crypto: 'Histórico sob demanda · coletado quando uma análise pedir',
  stock: 'Histórico sob demanda · a coleta começa quando as análises aceitarem ações',
  etf: 'Histórico sob demanda · a coleta começa quando as análises aceitarem ETFs',
}

export function onDemandHistory(): AssetHistory {
  return { status: 'on_demand', from: null, to: null, timeframes: [], gap_count: 0 }
}

const TIMEFRAME_MINUTES: Record<string, number> = { '1m': 1, '5m': 5, '15m': 15, '1h': 60, '4h': 240, '1d': 1440 }
const timeframeOrder = (tf: string) => TIMEFRAME_MINUTES[tf] ?? 9999

/** `22 out., 18:07` no fuso do navegador (ano só quando não é o corrente). */
export function formatShortDateTime(
  iso: string | null | undefined,
  timeZone = browserTimeZone(),
  now: Date = new Date(),
): string {
  if (!iso) return ''
  const p = dateParts(iso, timeZone)
  if (!p) return ''
  const sameYear = String(now.getFullYear()) === p.year
  return `${p.day} ${MONTHS[p.month - 1]}${sameYear ? '' : ` ${p.year}`}, ${p.hour}:${p.minute}`
}

export function browserTimeZone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
  } catch {
    return 'UTC'
  }
}

/** Nome do fuso no rótulo da coluna de atualização ("Brasília" para o horário de São Paulo). */
export function zoneLabel(timeZone = browserTimeZone()): string {
  if (timeZone === 'America/Sao_Paulo') return 'Brasília'
  if (timeZone === 'UTC' || timeZone === 'Etc/UTC') return 'UTC'
  return timeZone.split('/').pop()?.replace(/_/g, ' ') ?? timeZone
}

const listAnd = (names: string[]) =>
  names.length > 1 ? `${names.slice(0, -1).join(', ')} e ${names[names.length - 1]}` : (names[0] ?? '')

function withData(history: AssetHistory): HistoryTimeframe[] {
  return (history.timeframes ?? []).filter((t) => t.from)
}

/** Fuso em que o dia de início de cada série vale: Nova York para ação/ETF, UTC para cripto. */
function sessionZone(history: AssetHistory): string {
  return history.calendar_timezone || 'UTC'
}

/**
 * "desde" diz de qual timeframe é: início comum ("Histórico desde 17 ago. 2017 · 4 timeframes") ou um
 * início por grupo ("1d desde 11 nov. 2014 · 5m e 15m desde 19 mai. 2026"). Nunca um "desde" único
 * quando o intraday começa depois do diário.
 */
export function sinceText(history: AssetHistory): string {
  const frames = withData(history)
  const zone = sessionZone(history)
  const groups: { start: string; names: string[] }[] = []
  for (const frame of frames) {
    const start = formatDate(frame.from, zone)
    const group = groups.find((g) => g.start === start)
    if (group) group.names.push(frame.timeframe)
    else groups.push({ start, names: [frame.timeframe] })
  }
  groups.sort((x, y) => {
    const fx = frames.find((f) => formatDate(f.from, zone) === x.start)?.from ?? ''
    const fy = frames.find((f) => formatDate(f.from, zone) === y.start)?.from ?? ''
    return fx.localeCompare(fy)
  })
  if (groups.length === 1) {
    const n = frames.length
    return `Histórico desde ${groups[0].start} · ${n} ${n === 1 ? 'timeframe' : 'timeframes'}`
  }
  return groups
    .map((g) => `${listAnd([...g.names].sort((a, b) => timeframeOrder(a) - timeframeOrder(b)))} desde ${g.start}`)
    .join(' · ')
}

export function gapsCountText(count: number): string {
  return count === 0 ? 'sem lacunas' : count === 1 ? '1 lacuna' : `${count} lacunas`
}

export type HistoryTone = 'plain' | 'gap' | 'busy' | 'fail'

export interface HistorySummary {
  text: string
  tone: HistoryTone
}

/** Fato de histórico da linha do seletor (tarefa 6.2). "Histórico não coletado" não existe mais. */
export function historySummary(asset: CatalogAsset, now: Date = new Date()): HistorySummary {
  const history = asset.history
  const frames = withData(history)
  const zone = sessionZone(history)
  switch (history.status) {
    case 'collecting': {
      const info = history.collecting
      const at = info?.requested_at ? formatShortDateTime(info.requested_at, undefined, now).split(', ')[1] : ''
      return {
        text: `Coletando histórico · ${info?.timeframe ?? '—'}, página ${info?.page ?? 1}${at ? ` · pedido às ${at}` : ''}`,
        tone: 'busy',
      }
    }
    case 'failed': {
      const err = history.error
      const when = err?.at ? formatShortDateTime(err.at, undefined, now) : ''
      const collected = frames.length
        ? ` · já coletado: ${frames
            .filter((t) => t.origin === 'native')
            .map((t) => `${t.timeframe} desde ${formatDate(t.from, zone)}`)
            .join(', ')}`
        : ' · nada coletado ainda'
      return {
        text: `Coleta falhou${when ? ` ${when}` : ''} · ${err?.message ?? 'falha na coleta'}${collected}`,
        tone: 'fail',
      }
    }
    case 'partial': {
      const info = history.partial
      const updated = history.updated_at ? ` · atualizado ${formatShortDateTime(history.updated_at, undefined, now)}` : ''
      if (info?.insufficient) {
        return {
          text: `Parcial: pedido desde ${formatDate(info.requested_since, zone)}; a Binance tem desde ${formatDate(info.starts_at, zone)}${updated}`,
          tone: 'gap',
        }
      }
      return {
        text: `Parcial: coletado desde ${formatDate(info?.starts_at ?? history.from, zone)}; a coleta continua no próximo pedido${updated}`,
        tone: 'gap',
      }
    }
    case 'frozen': {
      const why = asset.state_label ? ` · sem atualização: ativo ${asset.state_label.toLowerCase()}` : ''
      return {
        text: `Histórico ${formatDate(history.from, zone)} – ${formatDate(history.to, zone)}${why}`,
        tone: 'plain',
      }
    }
    case 'covered': {
      const gaps = history.gap_count
      const parts = [sinceText(history)]
      if (gaps !== null && gaps !== undefined) parts.push(gapsCountText(gaps))
      if (history.updated_at) parts.push(`atualizado ${formatShortDateTime(history.updated_at, undefined, now)}`)
      return { text: parts.join(' · '), tone: gaps ? 'gap' : 'plain' }
    }
    case 'none':
      return { text: 'Sem histórico local', tone: 'plain' }
    default:
      return { text: ON_DEMAND_TEXT[asset.asset_class], tone: 'plain' }
  }
}

export function historyText(asset: CatalogAsset, now: Date = new Date()): string {
  return historySummary(asset, now).text
}

// --- Detalhe da cobertura por timeframe -----------------------------------------------

export interface CoverageRow {
  timeframe: string
  derived: boolean
  period: string
  gaps: string
  gapsTone: 'ok' | 'warn' | 'busy'
  updated: string
  origin: string
}

const NY_LABEL = 'horário de Nova York'

function hm(iso: string, timeZone: string): string {
  const p = dateParts(iso, timeZone)
  return p ? `${p.hour}:${p.minute}` : ''
}

/** Uma lacuna com data, hora e fuso na própria célula (design, decisão 16). */
export function gapLabel(gap: HistoryGap, timeframe: string, history: AssetHistory): string {
  const equity = !!history.calendar_timezone
  const zone = equity ? history.calendar_timezone! : browserTimeZone()
  const zoneText = equity ? NY_LABEL : 'horário local'
  const day = formatDate(gap.start, zone)
  if (timeframe === '1d') {
    const last = formatDate(gap.end, zone)
    return last === day ? `${day} (1 pregão sem candle)` : `${day} a ${last} (${gap.count} pregões sem candle)`
  }
  const from = hm(gap.start, zone)
  const to = hm(gap.inherited_from && gap.block_end ? gap.block_end : gap.end, zone)
  const range = from === to ? from : `${from}–${to}`
  return `${day}, ${range}, ${zoneText}`
}

function gapsCell(frame: HistoryTimeframe, history: AssetHistory): { text: string; tone: CoverageRow['gapsTone'] } {
  if (frame.state === 'collecting') return { text: 'em coleta', tone: 'busy' }
  const zone = sessionZone(history)
  if (frame.state === 'failed' || frame.incomplete) {
    return {
      text: `incompleto: faltam os candles antes de ${formatDate(frame.from, zone)}; a coleta continua do ponto em que parou no próximo pedido`,
      tone: 'warn',
    }
  }
  if (frame.insufficient) {
    return {
      text: `insuficiente para o último pedido (desde ${formatDate(frame.requested_since, zone)}): a Binance não tem candles antes de ${formatDate(frame.starts_at ?? frame.from, zone)}`,
      tone: 'warn',
    }
  }
  if (frame.origin === 'derived') {
    if (!frame.gaps.length) return { text: 'sem lacunas', tone: 'ok' }
    const shown = frame.gaps.slice(0, 3).map((g) => gapLabel(g, frame.timeframe, history))
    return {
      text: `herdada do ${frame.derived_from ?? '5m'}: ${shown.join('; ')} (bloco incompleto; não soma no resumo)`,
      tone: 'warn',
    }
  }
  const count = frame.gap_count
  if (count === null || count === undefined) return { text: 'lacunas ainda não calculadas', tone: 'ok' }
  if (count === 0) return { text: 'sem lacunas', tone: 'ok' }
  const shown = frame.gaps.slice(-3).map((g) => `${gapLabel(g, frame.timeframe, history)} (${g.count} ${g.count === 1 ? 'candle' : 'candles'} que a Binance não tem)`)
  const more = count > shown.length ? `; e mais ${count - shown.length}` : ''
  return { text: `${gapsCountText(count)}: ${shown.join('; ')}${more}`, tone: 'warn' }
}

export function coverageRows(history: AssetHistory, now: Date = new Date()): CoverageRow[] {
  const zone = sessionZone(history)
  return (history.timeframes ?? []).map((frame) => {
    const cell = gapsCell(frame, history)
    const derived = frame.origin === 'derived'
    const period =
      frame.state === 'collecting'
        ? `até agora: ${formatDate(frame.from, zone)} – ${formatDate(frame.to, zone)}`
        : `${formatDate(frame.from, zone)} – ${formatDate(frame.to, zone)}`
    return {
      timeframe: frame.timeframe,
      derived,
      period,
      gaps: cell.text,
      gapsTone: cell.tone,
      updated: frame.updated_at ? formatShortDateTime(frame.updated_at, undefined, now) : '—',
      origin: derived ? `montado do ${frame.derived_from ?? '5m'}` : 'nativo',
    }
  })
}

/** Linha de fonte, sessão e ajuste do detalhe da cobertura. */
export function coverageNote(history: AssetHistory): string {
  return `${history.note ?? ''}. Mercado fechado não conta como lacuna.`.replace(/^\. /, '')
}

/** O detalhe só existe quando há o que mostrar por timeframe. */
export function hasCoverageDetail(history: AssetHistory): boolean {
  return (history.timeframes ?? []).length > 0
}

/** Complemento exibido sob a linha de um ativo marcado. */
export function markedReasonText(asset: CatalogAsset, inSelection: boolean): string {
  const reason = (asset.state_reason || `${asset.state_label}.`).trim()
  return (
    `${reason} Não pode ser escolhido para análise nova; aparece para explicar resultados e favoritos antigos.` +
    (inSelection ? ' Está na seleção salva e fica de fora ao rodar.' : '')
  )
}

// --- Seleção ---------------------------------------------------------------------------

/** O que a seleção faz ao rodar: `runs` roda; os demais ficam de fora com motivo. */
export type EntryKind = 'runs' | 'class' | 'marked' | 'missing'

export interface SelectionEntry {
  symbol: string
  asset: CatalogAsset | null
  kind: EntryKind
}

/**
 * Classifica uma seleção concreta (símbolos) com o que o catálogo já conhece.
 * Símbolo desconhecido de uma classe sem lista válida segue como `runs`: a falha
 * da Binance não bloqueia por conta própria (o servidor decide).
 */
export function resolveSelection(
  symbols: string[],
  known: ReadonlyMap<string, CatalogAsset>,
  freshness: FreshnessMap | null,
  lookedUp?: ReadonlySet<string>,
): SelectionEntry[] {
  return symbols.map((raw) => {
    const symbol = normalizeSymbol(raw)
    const asset = known.get(symbol) ?? null
    if (asset) {
      if (isMarked(asset)) return { symbol, asset, kind: 'marked' as const }
      if (asset.asset_class !== 'crypto') return { symbol, asset, kind: 'class' as const }
      return { symbol, asset, kind: 'runs' as const }
    }
    const cls: AssetClass = symbolIsCrypto(symbol) ? 'crypto' : 'stock'
    // Sem consulta feita ou sem lista válida da classe, o símbolo segue neutro.
    const notAsked = lookedUp ? !lookedUp.has(symbol) : false
    const unverified = notAsked || !freshness || freshness[cls].status === 'unavailable'
    if (unverified) {
      return { symbol, asset: null, kind: symbolIsCrypto(symbol) ? ('runs' as const) : ('class' as const) }
    }
    return { symbol, asset: null, kind: 'missing' as const }
  })
}

export interface SelectionCounts {
  crypto: number
  stock: number
  etf: number
  equities: number
  marked: number
  missing: number
  out: number
  total: number
}

export function selectionCounts(entries: SelectionEntry[]): SelectionCounts {
  const counts: SelectionCounts = {
    crypto: 0,
    stock: 0,
    etf: 0,
    equities: 0,
    marked: 0,
    missing: 0,
    out: 0,
    total: 0,
  }
  for (const entry of entries) {
    if (entry.kind === 'marked') counts.marked += 1
    else if (entry.kind === 'missing') counts.missing += 1
    else if (entry.kind === 'runs') counts.crypto += 1
    else if (entry.asset?.asset_class === 'etf') counts.etf += 1
    else counts.stock += 1
  }
  counts.equities = counts.stock + counts.etf
  counts.out = counts.equities + counts.marked + counts.missing
  counts.total = counts.crypto + counts.out
  return counts
}

/** Marcados primeiro: nunca ficam escondidos no "+N". */
export function sortedForChips(entries: SelectionEntry[]): SelectionEntry[] {
  const rank = (e: SelectionEntry) => (e.kind === 'marked' ? 0 : e.kind === 'missing' ? 1 : 2)
  return entries
    .map((entry, index) => ({ entry, index }))
    .sort((a, b) => rank(a.entry) - rank(b.entry) || a.index - b.index)
    .map((item) => item.entry)
}

export function runnableSymbols(entries: SelectionEntry[]): string[] {
  return entries.filter((e) => e.kind === 'runs').map((e) => e.symbol)
}

export function outEntries(entries: SelectionEntry[]): SelectionEntry[] {
  return sortedForChips(entries).filter((e) => e.kind !== 'runs')
}

export function classLabelOf(entry: SelectionEntry): string {
  if (entry.asset) return CLASS_LABEL[entry.asset.asset_class]
  return symbolIsCrypto(entry.symbol) ? CLASS_LABEL.crypto : 'Ação ou ETF'
}

export function entryStateLabel(entry: SelectionEntry): string | null {
  if (entry.kind === 'marked' && entry.asset) return entry.asset.state_label
  if (entry.kind === 'missing') return 'Fora do catálogo'
  return null
}

export function outLabel(entry: SelectionEntry): string {
  const state = entryStateLabel(entry)
  return `${entry.symbol} (${classLabelOf(entry)}${state ? `, ${state}` : ''})`
}

export function outReason(entry: SelectionEntry): string {
  if (entry.kind === 'marked' && entry.asset) {
    const reason = (entry.asset.state_reason || entry.asset.state_label).replace(/\.$/, '')
    return `${reason}; não entra em análise nova`
  }
  if (entry.kind === 'missing') return MISSING_REASON
  return EQUITY_REASON
}

export function outNames(entries: SelectionEntry[], max = 3): string {
  const out = outEntries(entries)
  const shown = out.slice(0, max).map(outLabel)
  const rest = out.length - shown.length
  return shown.join(', ') + (rest > 0 ? ` e mais ${fmtInt(rest)}` : '')
}

export function outWhy(counts: SelectionCounts): string {
  const hasMarked = counts.marked > 0 || counts.missing > 0
  if (counts.equities && hasMarked) {
    return 'ações e ETFs ainda não têm análise, e ativos marcados pela Binance não entram em análise nova'
  }
  if (hasMarked) {
    return 'ativo marcado pela Binance (suspenso, fora de mercado, sem negociação, sem regras ou removido) não entra em análise nova'
  }
  return 'a análise ainda não está disponível para ações e ETFs'
}

export function selectionCountText(counts: SelectionCounts): string {
  const parts: string[] = []
  if (counts.crypto) parts.push(`${fmtInt(counts.crypto)} cripto`)
  if (counts.stock) parts.push(`${fmtInt(counts.stock)} ${counts.stock === 1 ? 'ação' : 'ações'}`)
  if (counts.etf) parts.push(`${fmtInt(counts.etf)} ${counts.etf === 1 ? 'ETF' : 'ETFs'}`)
  const marked = counts.marked + counts.missing
  if (marked) parts.push(`${fmtInt(marked)} ${marked === 1 ? 'marcado fica de fora' : 'marcados ficam de fora'}`)
  return (
    `${fmtInt(counts.total)} ${counts.total === 1 ? 'selecionado' : 'selecionados'}` +
    (parts.length ? ` · ${parts.join(' · ')}` : '')
  )
}

export function markedNoteText(entries: SelectionEntry[]): { title: string; body: string } | null {
  const marked = entries.filter((e) => e.kind === 'marked' || e.kind === 'missing')
  if (!marked.length) return null
  const names = sortedForChips(marked).slice(0, 3).map(outLabel).join(', ')
  const one = marked.length === 1
  return {
    title: one ? 'Ativo marcado na seleção salva' : 'Ativos marcados na seleção salva',
    body:
      `${names}: a Binance pausou ou retirou ${one ? 'esse ativo' : 'esses ativos'}. ` +
      `${one ? 'Ele aparece' : 'Eles aparecem'} para explicar resultados e favoritos antigos, mas ` +
      `${one ? 'fica' : 'ficam'} de fora de qualquer análise nova. Remova com ×.`,
  }
}

// --- Confirmação do "Todos do filtro" ---------------------------------------------------

const NOUN: Record<ClassFilter, [string, string]> = {
  all: ['ativo negociável', 'ativos negociáveis'],
  crypto: ['par cripto negociável', 'pares cripto negociáveis'],
  stock: ['ação negociável', 'ações negociáveis'],
  etf: ['ETF negociável', 'ETFs negociáveis'],
}

export interface ConfirmCopy {
  prefix: string
  count: string
  middle: string
  marked: string | null
  markedText: string
  suffix: string
}

export function confirmCopy(
  filter: ClassFilter,
  query: string,
  eligible: number,
  markedCount: number,
  newCount: number | null,
): ConfirmCopy {
  const noun = NOUN[filter][eligible === 1 ? 0 : 1]
  const q = query.trim()
  const scope = q
    ? ` que correspondem a “${q}”${filter === 'all' ? ' (todas as classes)' : ''}`
    : filter === 'all'
      ? ' de todas as classes'
      : ''
  const alreadyIn = newCount !== null && newCount < eligible
  return {
    prefix: 'Incluir ',
    count: alreadyIn ? `${fmtInt(eligible)} (${fmtInt(newCount as number)} ${newCount === 1 ? 'novo' : 'novos'})` : fmtInt(eligible),
    middle: ` ${noun}${scope} na seleção?`,
    marked: markedCount > 0 ? fmtInt(markedCount) : null,
    markedText:
      markedCount > 0
        ? ` ${markedCount === 1 ? 'ativo marcado fica' : 'ativos marcados ficam'} de fora: suspensos, fora de mercado, sem negociação, sem regras ou removidos não podem ser escolhidos para análise nova.`
        : '',
    suffix: ' O que já está selecionado continua.',
  }
}

// --- Frescor e falha por classe ----------------------------------------------------------

export interface CatalogBanner {
  kind: 'stale' | 'down'
  group: 'crypto' | 'equity'
  title: string
  body: string
  retry: boolean
}

function groupFreshness(freshness: FreshnessMap, group: 'crypto' | 'equity'): ClassFreshness {
  return group === 'crypto' ? freshness.crypto : freshness.stock
}

export function catalogBanners(freshness: FreshnessMap | null): CatalogBanner[] {
  if (!freshness) return []
  const banners: CatalogBanner[] = []
  for (const group of ['crypto', 'equity'] as const) {
    const info = groupFreshness(freshness, group)
    const name = group === 'crypto' ? 'Cripto' : 'Ações e ETFs'
    if (info.status === 'stale') {
      banners.push({
        kind: 'stale',
        group,
        title: group === 'crypto' ? 'Cripto desatualizado' : 'Ações e ETFs desatualizados',
        body:
          `A Binance não respondeu na atualização de ${formatDateTime(info.last_attempt_at)}. ` +
          `Mostrando a lista válida de ${formatDateTime(info.updated_at)}; pesquisa e escolha continuam.`,
        retry: false,
      })
    } else if (info.status === 'unavailable') {
      const other = group === 'crypto' ? 'Ações e ETFs continuam disponíveis' : 'Cripto continua disponível'
      banners.push({
        kind: 'down',
        group,
        title: group === 'crypto' ? 'Cripto indisponível' : 'Ações e ETFs indisponíveis',
        body: info.refreshing
          ? `Buscando a lista de ${name.toLowerCase()} na Binance. A seleção atual foi mantida.`
          : `A Binance não respondeu e ainda não há lista salva de ${name.toLowerCase()}. ${other}; a seleção atual foi mantida.`,
        retry: !info.refreshing,
      })
    }
  }
  // Um alerta vermelho só por vez: com cripto e ações fora, o de cripto manda.
  const down = banners.filter((b) => b.kind === 'down')
  if (down.length > 1) return [down[0], ...banners.filter((b) => b.kind !== 'down')]
  return banners
}

export function freshnessLine(freshness: FreshnessMap | null): string {
  if (!freshness) return 'Catálogo Binance · carregando…'
  const crypto = freshness.crypto
  const equity = freshness.stock
  const cText = (f: ClassFreshness) => (f.updated_at ? formatDateTime(f.updated_at) : '')
  if (crypto.status === 'unavailable' && equity.status === 'unavailable') return 'Catálogo Binance sem lista salva'
  if (crypto.status === 'unavailable') return `Cripto sem lista · Ações e ETFs atualizados ${cText(equity)}`
  if (equity.status === 'unavailable') return `Cripto atualizado ${cText(crypto)} · Ações e ETFs sem lista`
  if (crypto.status === 'stale' || equity.status === 'stale') {
    return `Cripto atualizado ${cText(crypto)} · Ações e ETFs de ${cText(equity)}`
  }
  return `Catálogo Binance · atualizado ${cText(crypto)}`
}

export function emptySearchMessage(
  query: string,
  filter: ClassFilter,
  freshness: FreshnessMap | null,
): string {
  const q = query.trim()
  const cryptoDown = freshness?.crypto.status === 'unavailable'
  const equityDown = freshness?.stock.status === 'unavailable'
  if (filter === 'crypto' && cryptoDown) {
    return 'Lista de cripto indisponível por falha da Binance. Use “Tentar de novo” no aviso acima; a seleção atual foi mantida.'
  }
  if (cryptoDown && (filter === 'all' || filter === 'crypto')) {
    return `Nenhuma ação ou ETF para “${q}”. Cripto está indisponível agora por falha da Binance, então pares cripto não aparecem na pesquisa até a lista voltar. A seleção atual foi mantida.`
  }
  if (equityDown && (filter === 'all' || filter === 'stock' || filter === 'etf')) {
    return `Nenhum par cripto para “${q}”. Ações e ETFs estão indisponíveis agora por falha da Binance, então não aparecem na pesquisa até a lista voltar. A seleção atual foi mantida.`
  }
  const where =
    filter === 'all' ? 'todas as classes' : filter === 'crypto' ? 'Cripto' : filter === 'stock' ? 'Ações' : 'ETFs'
  return `Nenhum ativo para “${q}” em ${where}. Confira o símbolo ou troque a classe. A seleção atual foi mantida.`
}

// --- Aviso antes e depois de rodar (Combo e Otimização) -----------------------------------

export type RunMode = 'none' | 'blocked' | 'single' | 'batch'

export interface RunPlan {
  mode: RunMode
  runnable: string[]
  counts: SelectionCounts
  outNames: string
  why: string
}

export function planRun(entries: SelectionEntry[]): RunPlan {
  const counts = selectionCounts(entries)
  const runnable = runnableSymbols(entries)
  let mode: RunMode
  if (counts.total === 0) mode = 'none'
  else if (runnable.length === 0) mode = 'blocked'
  else if (runnable.length === 1) mode = 'single'
  else mode = 'batch'
  return { mode, runnable, counts, outNames: outNames(entries, 3), why: outWhy(counts) }
}

export type RunPage = 'combo' | 'optimize'

/** Cópia que a tela mostra antes do clique. */
export function runCopy(plan: RunPlan, page: RunPage): { text: string; blocked: boolean } {
  const out = plan.counts.out ? ` Fora: ${plan.outNames} — ${plan.why}.` : ''
  if (plan.mode === 'none') {
    return { text: 'Nenhum ativo selecionado: escolha ao menos 1 par cripto em USDT.', blocked: false }
  }
  if (plan.mode === 'blocked') {
    return {
      text:
        page === 'combo'
          ? `Nada será executado nem salvo: ${plan.outNames} — ${plan.why}.`
          : `Nada será executado: ${plan.outNames} — ${plan.why}.`,
      blocked: true,
    }
  }
  if (plan.mode === 'single') {
    if (page === 'combo') {
      return {
        text: plan.counts.out
          ? `Roda 1 par cripto (${plan.runnable[0]}): otimiza, salva em favoritos e abre a página de favoritos.${out}`
          : '1 ativo selecionado: otimiza, salva em favoritos e abre a página de favoritos.',
        blocked: false,
      }
    }
    return {
      text: `${plan.counts.out ? `Roda 1 par cripto (${plan.runnable[0]}): ` : '1 ativo: '}otimiza e mostra o resultado ao lado.${out}`,
      blocked: false,
    }
  }
  const n = fmtInt(plan.runnable.length)
  if (page === 'combo') {
    return {
      text: `${n}${plan.counts.out ? ' pares cripto' : ' ativos'}: batch. Cada resultado é salvo em favoritos.${out}`,
      blocked: false,
    }
  }
  return {
    text: `${n}${plan.counts.out ? ' pares cripto' : ' ativos'}: lote, uma otimização por ativo com o mesmo template, timeframe e faixas. O melhor resultado de cada um é salvo em favoritos.${out}`,
    blocked: false,
  }
}

export interface RunNotice {
  tone: 'alert' | 'warn'
  title: string
  body: string
}

/** Aviso ao rodar quando nada roda (`blocked`) ou quando sobra parte fora (lote misto). */
export function blockedNotice(plan: RunPlan, page: RunPage): RunNotice {
  const { counts } = plan
  const title = !counts.marked && !counts.missing
    ? 'Análise ainda não disponível para ações e ETFs'
    : !counts.equities
      ? 'Ativo marcado pela Binance não entra em análise nova'
      : 'Nenhum ativo da seleção pode rodar agora'
  const what =
    page === 'combo'
      ? 'Backtest, combo e otimização rodam só com pares cripto negociáveis em USDT nesta etapa. Nada foi executado nem salvo.'
      : 'A otimização roda só com pares cripto negociáveis em USDT nesta etapa. Nada foi executado.'
  return {
    tone: 'alert',
    title,
    body: `${plan.outNames}: ${plan.why}. ${what} A seleção foi mantida.`,
  }
}

export function partialNotice(plan: RunPlan): RunNotice | null {
  if (!plan.counts.out) return null
  const single = plan.runnable.length === 1
  return {
    tone: 'warn',
    title: single ? 'Otimizando 1 par cripto' : `Lote iniciado com ${fmtInt(plan.runnable.length)} pares cripto`,
    body: `Fora${single ? '' : ' do lote'}: ${plan.outNames} — ${plan.why}.`,
  }
}

/** Mensagem da API (`detail.message`) em recusa estruturada; texto simples cai no fallback. */
export function refusalMessage(detail: unknown, fallback: string): string {
  if (typeof detail === 'string' && detail.trim()) return detail
  if (detail && typeof detail === 'object') {
    const message = (detail as Record<string, unknown>).message
    if (typeof message === 'string' && message.trim()) return message
    const nested = (detail as Record<string, unknown>).detail
    if (nested) return refusalMessage(nested, fallback)
  }
  return fallback
}

export function urlSymbolNotice(symbol: string): { title: string; body: string } {
  return {
    title: `${symbol} não está no catálogo da Binance`,
    body: 'O endereço trouxe esse símbolo, mas ele não foi marcado. Escolha os ativos na lista.',
  }
}

// --- Preflight da Descoberta -------------------------------------------------------------

export interface PreflightExcludedAsset {
  symbol: string
  asset_class: AssetClass | null
  state: AssetState | null
  kind: 'class' | 'marked' | 'missing'
  reason: string
  combinations: number
}

export function outOfSweepTitle(assets: PreflightExcludedAsset[]): string {
  const combos = assets.reduce((sum, a) => sum + a.combinations, 0)
  return (
    `Fora desta varredura: ${fmtInt(assets.length)} ${assets.length === 1 ? 'ativo' : 'ativos'} ` +
    `(${fmtInt(combos)} ${combos === 1 ? 'combinação' : 'combinações'})`
  )
}

export function preflightExcludedLabel(asset: PreflightExcludedAsset): string {
  const cls = asset.asset_class ? CLASS_LABEL[asset.asset_class] : 'Ação ou ETF'
  const state = asset.kind === 'marked' && asset.state ? STATE_NAMES[asset.state] : null
  return `${asset.symbol} (${cls}${state ? `, ${state}` : ''})`
}

const STATE_NAMES: Record<AssetState, string> = {
  tradable: 'Negociável',
  suspended: 'Suspenso',
  off_market: 'Fora de mercado',
  no_trading: 'Sem negociação',
  no_rules: 'Sem regras de negociação',
  removed: 'Removido',
}

export function preflightRestLine(assets: PreflightExcludedAsset[], shown: number): string | null {
  const rest = assets.length - shown
  if (rest <= 0) return null
  const hasMarked = assets.slice(shown).some((a) => a.kind !== 'class')
  return hasMarked
    ? `e mais ${fmtInt(rest)} ativos, pelos mesmos motivos.`
    : `e mais ${fmtInt(rest)} ações e ETFs, pelo mesmo motivo.`
}
