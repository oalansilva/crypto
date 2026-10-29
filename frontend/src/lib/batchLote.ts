/**
 * Lote multiclasse (card #1120): tipos da API do lote e os textos do Confirmar e do painel por ativo.
 *
 * Lógica pura, sem DOM e sem rede, para ser testada com `tsx --test`. Os textos são os do protótipo
 * aprovado (`frontend/public/prototypes/card-1120-lote-multiclasse/`): os componentes só os desenham.
 */

import { CLASS_LABEL, fmtInt, formatDatePlain as formatDate, type AssetClass } from './assetSelection'

export type BatchItemState =
  | 'queued'
  | 'collecting'
  | 'optimizing'
  | 'success'
  | 'success_daily'
  | 'insufficient'
  | 'rejected'
  | 'failed'
  | 'skipped'
  | 'out'
  | 'not_run'

export interface BatchItemExecution {
  precision_requested?: string
  precision_effective?: string
  intraday_missing?: Array<{ from: string; to: string }>
  intraday_reason?: string | null
  window?: { covered?: { start?: string | null; end?: string | null; candles?: number } }
}

export interface BatchItem {
  position: number
  symbol: string
  asset_class: AssetClass | null
  currency: string | null
  state: BatchItemState
  reason: string | null
  progress: string | null
  favorite_id: number | null
  execution: BatchItemExecution | null
  snapshot_id: string | null
  started_at: string | null
  finished_at: string | null
  collect_kind?: 'none' | 'missing' | 'tail' | null
  needs_collection?: Array<{ series: string; role: string; kind: string }>
}

export interface BatchConfig {
  template_name?: string | null
  timeframe?: string
  start_date?: string | null
  end_date?: string | null
  page?: 'combo' | 'optimize' | null
  deep_backtest?: boolean
  direction?: string
}

export interface BatchJob {
  job_id: string
  status: string
  processed: number
  total: number
  succeeded: number
  failed: number
  skipped?: number
  errors: Array<{ symbol: string; error: string }>
  started_at: string | null
  elapsed_sec: number
  estimated_remaining_sec: number | null
  current_symbol?: string | null
  current_stage?: string | null
  pause_requested?: boolean
  cancel_requested?: boolean
  created_at?: string | null
  config?: BatchConfig | null
  items?: BatchItem[] | null
  totals?: Record<string, number> | null
}

export interface PreviewNeed {
  series: string
  role: string
  kind: string
}

export interface PreviewItem {
  symbol: string
  asset_id?: string | null
  asset_class: AssetClass | null
  currency: string | null
  plan: 'run' | 'out'
  reason: string | null
  out_kind?: string | null
  needs_collection: PreviewNeed[]
  collect_kind: 'none' | 'missing' | 'tail'
  covered_until?: string | null
  collect_note?: string | null
}

export interface BatchPreview {
  items: PreviewItem[]
  totals: {
    total: number
    run: number
    out: number
    by_class: Record<string, { run: number; out: number; currency: string | null }>
    collect: { count: number; of: number; missing: number; tail: number }
  }
  config: BatchConfig
}

export const FINAL_JOB_STATUSES = ['completed', 'failed', 'cancelled']
export const FINAL_ITEM_STATES: BatchItemState[] = [
  'success',
  'success_daily',
  'insufficient',
  'rejected',
  'failed',
  'skipped',
  'out',
  'not_run',
]
export const PAGE_STEP = 50

export const shortId = (jobId: string): string => String(jobId || '').slice(0, 8)

export function isJobFinal(job: BatchJob | null | undefined): boolean {
  return !!job && FINAL_JOB_STATUSES.includes(job.status)
}

export function isLegacyJob(job: BatchJob | null | undefined): boolean {
  return !!job && !Array.isArray(job.items)
}

/** "1m 30s" (sem horas, como o painel vivo antigo). */
export function formatDuration(sec: number): string {
  const total = Math.max(0, Math.floor(sec))
  return `${Math.floor(total / 60)}m ${total % 60}s`
}

/** "9h 40m" quando passa de uma hora. */
export function formatRemaining(sec: number): string {
  const total = Math.max(0, Math.ceil(sec))
  if (total >= 3600) return `${Math.floor(total / 3600)}h ${Math.floor((total % 3600) / 60)}m`
  return formatDuration(total)
}

// --- Estados por ativo -------------------------------------------------------------------------------------

export type StateIcon = 'ok' | 'warn' | 'fail' | 'ban' | 'skip' | 'out' | 'load' | 'wait' | 'stop'

export const STATE_META: Record<BatchItemState, { icon: StateIcon; label: string }> = {
  queued: { icon: 'wait', label: 'Na fila' },
  collecting: { icon: 'load', label: 'Coletando histórico' },
  optimizing: { icon: 'load', label: 'Otimizando' },
  success: { icon: 'ok', label: 'Sucesso' },
  success_daily: { icon: 'warn', label: 'Sucesso · precisão diária' },
  insufficient: { icon: 'warn', label: 'Insuficiente' },
  rejected: { icon: 'ban', label: 'Rejeitado' },
  failed: { icon: 'fail', label: 'Falha' },
  skipped: { icon: 'skip', label: 'Pulado' },
  out: { icon: 'out', label: 'Fora' },
  not_run: { icon: 'stop', label: 'Não rodou' },
}

/** Chave do filtro por estado: Em curso junta coletando e otimizando; o resto é o próprio estado. */
export type ChipKey =
  | 'all'
  | 'success'
  | 'daily'
  | 'insufficient'
  | 'rejected'
  | 'failed'
  | 'skipped'
  | 'out'
  | 'running'
  | 'queued'
  | 'notrun'

export const CHIPS: Array<[ChipKey, string]> = [
  ['all', 'Todos'],
  ['success', 'Sucesso'],
  ['daily', 'Precisão diária'],
  ['insufficient', 'Insuficiente'],
  ['rejected', 'Rejeitado'],
  ['failed', 'Falha'],
  ['skipped', 'Pulado'],
  ['out', 'Fora'],
  ['running', 'Em curso'],
  ['queued', 'Na fila'],
  ['notrun', 'Não rodou'],
]

export function chipOf(state: BatchItemState): ChipKey {
  if (state === 'collecting' || state === 'optimizing') return 'running'
  if (state === 'success_daily') return 'daily'
  if (state === 'not_run') return 'notrun'
  return state
}

export function chipCounts(items: BatchItem[]): Record<ChipKey, number> {
  const counts = Object.fromEntries(CHIPS.map(([key]) => [key, 0])) as Record<ChipKey, number>
  counts.all = items.length
  for (const item of items) counts[chipOf(item.state)] += 1
  return counts
}

/** Só os estados presentes viram botão (e "Todos"). */
export function visibleChips(counts: Record<ChipKey, number>): Array<[ChipKey, string]> {
  return CHIPS.filter(([key]) => key === 'all' || counts[key] > 0)
}

export function filterItems(items: BatchItem[], chip: ChipKey): BatchItem[] {
  return chip === 'all' ? items : items.filter((item) => chipOf(item.state) === chip)
}

// --- Selo, linha viva e resumo -----------------------------------------------------------------------------

export type JobView = 'running' | 'pausing' | 'cancelling' | 'paused' | 'cancelled' | 'completed' | 'failed'

export function jobView(job: BatchJob): JobView {
  if (job.status === 'paused') return 'paused'
  if (job.status === 'cancelled') return 'cancelled'
  if (job.status === 'completed') return 'completed'
  if (job.status === 'failed') return 'failed'
  if (job.cancel_requested) return 'cancelling'
  if (job.pause_requested) return 'pausing'
  return 'running'
}

export const PILL: Record<JobView, { tone: 'run' | 'warn' | 'ok' | 'stop'; label: string }> = {
  running: { tone: 'run', label: 'Rodando' },
  pausing: { tone: 'warn', label: 'Pausando' },
  cancelling: { tone: 'warn', label: 'Encerrando' },
  paused: { tone: 'warn', label: 'Pausado' },
  cancelled: { tone: 'stop', label: 'Encerrado' },
  completed: { tone: 'ok', label: 'Concluído' },
  failed: { tone: 'stop', label: 'Falhou' },
}

export function savedCount(job: BatchJob): number {
  return (job.items ?? []).filter((i) => i.state === 'success' || i.state === 'success_daily').length
}

function namesList(names: string[], max = 3): string {
  const shown = names.slice(0, max)
  const rest = names.length - shown.length
  return shown.join(', ') + (rest > 0 ? ` e mais ${fmtInt(rest)}` : '')
}

function currentItem(job: BatchJob): BatchItem | undefined {
  return (job.items ?? []).find((i) => i.state === 'collecting' || i.state === 'optimizing')
}

function stageName(item: BatchItem | undefined): string {
  return item?.state === 'collecting' ? 'coleta' : 'otimização'
}

/** Linha viva (`role=status`): só o ativo e a etapa em curso, nunca a lista inteira. */
export function liveLine(job: BatchJob): string {
  const view = jobView(job)
  const items = job.items ?? []
  const current = currentItem(job)
  const finished = job.processed
  const total = job.total
  const bad = items.filter((i) => ['insufficient', 'rejected', 'failed'].includes(i.state)).length
  const saved = savedCount(job)
  const daily = items.filter((i) => i.state === 'success_daily').length
  switch (view) {
    case 'running': {
      const symbol = current?.symbol ?? job.current_symbol
      if (!symbol) return 'Rodando.'
      return `${symbol}: ${current?.state === 'collecting' ? 'coletando histórico' : 'otimizando'}.`
    }
    case 'pausing':
      return `Pausa pedida: o lote para quando ${current?.symbol ?? job.current_symbol ?? 'o ativo em curso'} terminar a etapa em curso (${stageName(current)}).`
    case 'cancelling':
      return `Encerramento pedido: o lote para quando ${current?.symbol ?? job.current_symbol ?? 'o ativo em curso'} terminar a etapa em curso (${stageName(current)}).`
    case 'paused': {
      const waiting = items.filter((i) => i.state === 'queued').map((i) => i.symbol)
      const rest = waiting.length > 3 ? ` e mais ${fmtInt(waiting.length - 3)}` : ''
      return (
        `Pausado em ${fmtInt(finished)} de ${fmtInt(total)}. Os concluídos ficam; ` +
        `${waiting.slice(0, 3).join(', ')}${rest} ${waiting.length > 1 ? 'esperam' : 'espera'}. ` +
        'Retomar continua no mesmo lote; um lote novo só depois de retomar ou encerrar este.'
      )
    }
    case 'cancelled': {
      const notRun = items.filter((i) => i.state === 'not_run').map((i) => i.symbol)
      return (
        `Encerrado pelo usuário em ${fmtInt(finished)} de ${fmtInt(total)}. ` +
        `${saved} favorito(s) gravado(s) ficam; não rodaram: ${notRun.join(', ') || 'nenhum'}.`
      )
    }
    case 'failed':
      return `O lote parou por um erro no servidor em ${fmtInt(finished)} de ${fmtInt(total)}. Os favoritos já gravados ficam.`
    default:
      return (
        `Lote concluído: ${fmtInt(finished)} de ${fmtInt(total)} em ${formatDuration(job.elapsed_sec)} · ` +
        `${saved} favorito(s) gravado(s)${daily ? ` (${daily} com precisão diária)` : ''}` +
        `${bad ? ` · sem resultado válido: ${bad}` : ''}.`
      )
  }
}

export function metaLine(job: BatchJob): string {
  const view = jobView(job)
  const base = `${fmtInt(job.processed)} de ${fmtInt(job.total)} ativos · ${formatDuration(job.elapsed_sec)}`
  if ((view === 'running' || view === 'pausing' || view === 'cancelling') && job.estimated_remaining_sec != null) {
    return `${base} · resta ~${formatRemaining(job.estimated_remaining_sec)}`
  }
  return base
}

export function dailyNote(count: number): { title: string; body: string } | null {
  if (!count) return null
  return {
    title: `Precisão diária em ${count} ${count === 1 ? 'ativo' : 'ativos'}:`,
    body: ' o intradiário de 15m não cobre a janela, então o stop foi simulado no candle diário em toda a janela. O resultado é válido e a marca segue para Favoritos.',
  }
}

export function favoritesHref(job: BatchJob): string {
  return `/favorites?lote=${shortId(job.job_id)}`
}

export function favoritesLinkText(saved: number): string {
  return saved === 1 ? 'Ver o resultado do lote em Favoritos' : `Ver os ${saved} resultados do lote em Favoritos`
}

// --- Detalhe de cada ativo -----------------------------------------------------------------------------------

export function parseProgress(progress: string | null | undefined): { value: number; max: number } | null {
  const match = /página (\d+) de (\d+)/.exec(progress ?? '')
  return match ? { value: Number(match[1]), max: Number(match[2]) } : null
}

function capitalize(text: string): string {
  return text ? text[0].toUpperCase() + text.slice(1) : text
}

function collectSeries(item: BatchItem): string {
  const needs = item.needs_collection ?? []
  return needs
    .map((n) => (n.role === 'intraday' ? `${n.series} do intrabar` : n.series))
    .join(' e ')
}

/** Janela efetiva e precisão do favorito gravado ("17 ago. 2017 – 24 out. 2026 · intrabar 15m"). */
export function savedSummary(item: BatchItem): string {
  const zone = item.asset_class === 'crypto' ? 'UTC' : 'America/New_York'
  const covered = item.execution?.window?.covered
  const range =
    covered?.start && covered?.end
      ? `${formatDate(covered.start, zone)} – ${formatDate(covered.end, zone)}`
      : ''
  const execution = item.execution
  let precision: string
  if (execution?.precision_effective === 'intrabar_15m') precision = 'intrabar 15m'
  else if (execution?.precision_requested === 'daily') precision = 'precisão do candle (Deep Backtest desligado)'
  else {
    const stretch = (execution?.intraday_missing ?? [])
      .map((m) => `${formatDate(m.from, 'UTC')} a ${formatDate(m.to, 'UTC')}`)
      .join(' e ')
    precision = stretch ? `precisão diária: sem 15m de ${stretch}` : 'precisão diária'
  }
  return [range, precision].filter(Boolean).join(' · ')
}

export type DetailView =
  | { kind: 'text'; text: string }
  | { kind: 'saved'; summary: string; href: string }
  | { kind: 'progress'; text: string; progress: { value: number; max: number } | null }

export function itemDetail(item: BatchItem, job: BatchJob): DetailView {
  switch (item.state) {
    case 'out':
      return { kind: 'text', text: `${capitalize(item.reason ?? 'Ficou fora do plano')}. Ficou fora antes de começar.` }
    case 'queued': {
      if (item.progress) return { kind: 'text', text: item.progress }
      const series = collectSeries(item)
      return {
        kind: 'text',
        text: series
          ? `precisa de coleta: ${series}.`
          : 'histórico já guardado, sem lacunas e atualizado: nada a coletar.',
      }
    }
    case 'collecting':
      return { kind: 'progress', text: item.progress ?? 'coletando histórico…', progress: parseProgress(item.progress) }
    case 'optimizing':
      return {
        kind: 'progress',
        text:
          'otimizando · todas as tentativas leem a mesma amostra, guardada no começo' +
          (item.collect_kind === 'none' ? ' · histórico já guardado, nada a coletar' : ''),
        progress: null,
      }
    case 'success':
    case 'success_daily':
      // Combinações puladas por erro (#1120): "N combinações com erro: <motivo>" ao lado do resumo.
      return {
        kind: 'saved',
        summary: [savedSummary(item), item.reason].filter(Boolean).join(' · '),
        href: favoritesHref(job),
      }
    case 'not_run':
      return { kind: 'text', text: 'Não rodou: o lote foi encerrado antes deste ativo.' }
    default:
      return { kind: 'text', text: item.reason ?? STATE_META[item.state].label }
  }
}

// --- Confirmar lote ------------------------------------------------------------------------------------------

export interface ConfirmView {
  title: string
  run: { count: number; classes: string; names: string }
  collect: { headline: string; detail: string }
  out: Array<{ symbol: string; label: string }> | null
  outReason: string | null
  note: string | null
}

const CLASS_PLURAL: Record<string, [string, string]> = {
  crypto: ['cripto', 'cripto'],
  stock: ['ação', 'ações'],
  etf: ['ETF', 'ETFs'],
}

export function classBreakdown(items: Array<Pick<PreviewItem, 'asset_class' | 'currency'>>): string {
  const order: AssetClass[] = ['crypto', 'stock', 'etf']
  const parts: string[] = []
  for (const cls of order) {
    const group = items.filter((i) => i.asset_class === cls)
    if (!group.length) continue
    const [one, many] = CLASS_PLURAL[cls]
    parts.push(`${fmtInt(group.length)} ${group.length === 1 ? one : many} (${group[0].currency ?? ''})`)
  }
  return parts.join(', ')
}

const COLLECT_RULE = ' Conta só o que a Binance tem para a janela e ainda não está guardado.'
const COLLECT_TAIL = ' A coleta acontece dentro do lote, ativo por ativo, com progresso, e pode ser pausada ou encerrada.'

function itemOutLabel(item: PreviewItem): string {
  const cls = item.asset_class ? CLASS_LABEL[item.asset_class] : 'Ação ou ETF'
  return `${item.symbol} (${cls})`
}

/** O texto de "Ficam fora": os motivos distintos, na ordem em que aparecem. */
export function groupOutReason(out: PreviewItem[]): string {
  const reasons: string[] = []
  const seen = new Set<string>()
  const equityTimeframe = out.filter((i) => i.out_kind === 'timeframe')
  const coverage = out.filter((i) => i.out_kind === 'coverage')
  if (equityTimeframe.length) {
    const reason = equityTimeframe[0].reason ?? ''
    reasons.push(reason)
    seen.add(reason)
  }
  if (coverage.length) {
    const dates = new Set(coverage.map((i) => /começa em (.+?) e não cobre/.exec(i.reason ?? '')?.[1] ?? ''))
    const sample = coverage[0].reason ?? ''
    reasons.push(
      dates.size === 1
        ? sample.replace(/^o 5m de [^ ]+ começa/, 'o 5m deles começa')
        : sample,
    )
  }
  for (const item of out) {
    if (item.out_kind === 'timeframe' || item.out_kind === 'coverage') continue
    const reason = item.reason ?? ''
    if (!seen.has(reason)) {
      seen.add(reason)
      reasons.push(reason)
    }
  }
  return reasons.join('; ')
}

export function confirmView(preview: BatchPreview): ConfirmView {
  const run = preview.items.filter((i) => i.plan === 'run')
  const out = preview.items.filter((i) => i.plan === 'out')
  const need = run.filter((i) => i.collect_kind !== 'none')
  const ready = run.filter((i) => i.collect_kind === 'none')
  const { collect } = preview.totals
  const readyText = ready.length
    ? ready.length <= 3
      ? ` ${listAnd(ready.map((i) => i.symbol))} ${ready.length === 1 ? 'já está guardado, sem lacunas e atualizado' : 'já estão guardados, sem lacunas e atualizados'}.`
      : ` Os outros ${fmtInt(ready.length)} já estão guardados, sem lacunas e atualizados.`
    : ''
  const notes = need.map((i) => i.collect_note).filter((n): n is string => !!n)
  const note = notes.length ? ` ${notes.join(' ')}` : ''
  let detail: string
  if (!need.length) {
    detail = `—${readyText}${COLLECT_RULE}`
  } else if (need.length <= 3) {
    const list = need.map((i) => `${i.symbol} (${seriesText(i)})`).join(', ')
    detail = `— ${list}.${readyText}${note}${COLLECT_RULE}${COLLECT_TAIL}`
  } else {
    const missing = need.filter((i) => i.collect_kind === 'missing')
    const tail = need.filter((i) => i.collect_kind === 'tail')
    const bits: string[] = []
    if (missing.length) bits.push(`${fmtInt(missing.length)} sem histórico guardado (${seriesText(missing[0])})`)
    if (tail.length) bits.push(`${fmtInt(tail.length)} só com o trecho desde a última coleta`)
    detail = `— ${bits.join(' e ')}.${readyText}${note}${COLLECT_RULE}${COLLECT_TAIL}`
  }
  return {
    title: `Confirmar lote de ${fmtInt(preview.totals.total)} ativos`,
    run: {
      count: run.length,
      classes: classBreakdown(run),
      names: namesList(run.map((i) => i.symbol)),
    },
    collect: { headline: `${fmtInt(collect.count)} de ${fmtInt(collect.of)}`, detail },
    out: out.length ? out.map((i) => ({ symbol: i.symbol, label: itemOutLabel(i) })) : null,
    outReason: out.length ? groupOutReason(out) : null,
    note: null,
  }
}

function seriesText(item: PreviewItem): string {
  return item.needs_collection.map((n) => (n.role === 'intraday' ? `${n.series} do intrabar` : n.series)).join(' e ')
}

function listAnd(names: string[]): string {
  return names.length > 1 ? `${names.slice(0, -1).join(', ')} e ${names[names.length - 1]}` : (names[0] ?? '')
}

/** Frase de "Ficam fora": nomes com a classe, até 3 e "e mais N". */
export function outNamesText(out: Array<{ label: string }>, max = 3): string {
  return namesList(
    out.map((o) => o.label),
    max,
  )
}

export interface PausedBlockView {
  title: string
  body: string
  resume: string
  cancel: string
}

export function pausedBlockView(job: { job_id: string }, saved: number): PausedBlockView {
  const id = shortId(job.job_id)
  const kept = saved
    ? `Encerrar mantém ${saved === 1 ? 'o favorito já gravado' : `os ${saved} favoritos já gravados`} e marca o resto "Não rodou".`
    : 'Encerrar marca o resto "Não rodou".'
  return {
    title: 'Há um lote pausado',
    body: `Retome ou encerre o lote ${id} antes de começar outro. ${kept}`,
    resume: `Retomar o lote ${id}`,
    cancel: `Encerrar o lote ${id}`,
  }
}
