/**
 * Card #1123: textos e estados da comparação com referência (lógica pura, testada com `tsx --test`).
 *
 * Os números vêm só da comparação gravada no servidor (`benchmark_comparisons`): nada aqui calcula
 * retorno ou CAGR. Formato da seção do resultado igual ao "Retorno total" vivo (`+6352.66%`); na célula
 * do Decidir, pt-BR como o resto do Decidir (`+66,8 p.p.`, `+15,25% a.a.`, `2 jan. 2019`).
 */

import { formatDate, formatDatePlain, type AssetClass, type CatalogAsset } from './assetSelection'

export const MIN_COMMON_DAYS = 30
export const CURRENCY_NOTE_TITLE = 'USDT tratado como USD, sem conversão.'
export const CURRENCY_NOTE_TEXT = 'USDT tratado como USD, sem conversão. A comparação é só em percentual.'
export const PRICE_RETURN_TEXT = 'Retorno de preço, sem dividendos'
export const SECTION_SUBTITLE =
    'Buy-and-hold da referência · fechamentos diários no período comum · CAGR com dias corridos ÷ 365,25'

export const CLASS_LABEL: Record<string, string> = { crypto: 'Cripto', stock: 'Ação', etf: 'ETF' }

export type ReasonCode =
    | 'no_history'
    | 'no_overlap'
    | 'short_overlap'
    | 'sample_expired'
    | 'sample_unavailable'
    | 'regeneration_failed'

export interface ComparisonReference {
    kind: 'own' | 'catalog'
    symbol: string
    asset_id?: string | null
    asset_class?: string | null
    currency?: string | null
    name?: string | null
    return_kind?: 'price' | 'price_no_dividends'
    long_only?: boolean
}

export interface LeftOutPart {
    start: string
    end: string
    trades: number
    note?: 'no_session' | 'no_reference' | 'edge'
}

export interface BenchmarkComparison {
    id: string
    created_at: string
    trigger: 'run' | 'choice' | 'favorite_refresh'
    owner: { kind: 'result' | 'favorite' | 'discovery_result'; favorite_id?: number | null }
    reference: ComparisonReference
    strategy: {
        symbol: string
        asset_class?: string | null
        currency?: string | null
        direction?: string
        window?: { start?: string | null; end?: string | null; state?: string }
        return: number | null
        cagr: number | null
        trades_in: number | null
        trades_out: number | null
    }
    reference_result: { return: number; cagr: number; first_close: { date: string; price: number }; last_close: { date: string; price: number } } | null
    common_window: { start: string; end: string; days: number } | null
    left_out: LeftOutPart[]
    delta: { cagr_pp: number | null } | null
    currency_note: string | null
    status: 'valid' | 'insufficient'
    reason: { code: ReasonCode; text: string; short?: string; expired_at?: string | null } | null
    history?: { first: string | null; last: string | null }
    samples?: { reference?: { snapshot_id?: string | null; version_label?: string | null } | null } | null
    collected?: boolean
}

export interface ComparisonSummary {
    id: string
    status: string
    created_at: string
    trigger?: string
    owner_kind?: string
    reference: { kind: string; symbol: string; asset_class?: string | null; currency?: string | null }
}

// --------------------------------------------------------------------------- formatos

const MINUS = '−'

/** `+6352.66%` (mesmo formato do "Retorno total" da tela). */
export function pctDot(ratio: number | null | undefined, decimals = 2): string {
    if (ratio === null || ratio === undefined || !Number.isFinite(ratio)) return ''
    const points = ratio * 100
    const text = Math.abs(points).toFixed(decimals)
    return `${points < 0 ? MINUS : '+'}${text}%`
}

/** `+29.7 p.p.` */
export function ppDot(points: number | null | undefined): string {
    if (points === null || points === undefined || !Number.isFinite(points)) return ''
    return `${points < 0 ? MINUS : '+'}${Math.abs(points).toFixed(1)} p.p.`
}

function brNumber(value: number, decimals: number): string {
    return value.toLocaleString('pt-BR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

/** `+66,8 p.p.` (Decidir, pt-BR). */
export function ppBr(points: number | null | undefined): string {
    if (points === null || points === undefined || !Number.isFinite(points)) return ''
    return `${points < 0 ? MINUS : '+'}${brNumber(Math.abs(points), 1)} p.p.`
}

/** `+15,25% a.a.` (Decidir, pt-BR). */
export function annualBr(ratio: number | null | undefined): string {
    if (ratio === null || ratio === undefined || !Number.isFinite(ratio)) return ''
    const points = ratio * 100
    return `${points < 0 ? MINUS : '+'}${brNumber(Math.abs(points), 2)}% a.a.`
}

export function toneOf(value: number | null | undefined): 'up' | 'down' | 'flat' {
    if (value === null || value === undefined || !Number.isFinite(value) || value === 0) return 'flat'
    return value > 0 ? 'up' : 'down'
}

/** Datas do período comum são dias de calendário (ISO sem hora): formatadas em UTC. */
export function day(iso: string | null | undefined): string {
    return formatDate(iso ? `${iso.slice(0, 10)}T12:00:00Z` : null, 'UTC')
}

export function dayPlain(iso: string | null | undefined): string {
    return formatDatePlain(iso ? `${iso.slice(0, 10)}T12:00:00Z` : null, 'UTC')
}

export function brDate(iso: string | null | undefined): string {
    if (!iso) return ''
    const [y, m, d] = iso.slice(0, 10).split('-')
    return `${d}/${m}/${y}`
}

const thousands = (n: number) => n.toLocaleString('pt-BR')

/** `27/10/2026, 14:30` no fuso de São Paulo. */
export function stamp(iso: string | null | undefined, timeZone = 'America/Sao_Paulo'): string {
    if (!iso) return ''
    const date = new Date(iso)
    if (Number.isNaN(date.getTime())) return ''
    const parts = new Intl.DateTimeFormat('en-GB', {
        timeZone,
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
    }).formatToParts(date)
    const get = (t: string) => parts.find((p) => p.type === t)?.value ?? ''
    return `${get('day')}/${get('month')}/${get('year')}, ${get('hour')}:${get('minute')}`
}

/** `27/10` (tag de Favoritos). */
export function shortDay(iso: string | null | undefined, timeZone = 'America/Sao_Paulo'): string {
    return stamp(iso, timeZone).slice(0, 5)
}

// --------------------------------------------------------------------------- seção do resultado

export function referenceName(ref: ComparisonReference | null | undefined, strategySymbol: string): string {
    if (!ref || ref.kind === 'own') return `${ref?.symbol || strategySymbol} (próprio ativo)`
    return ref.symbol
}

export function holdLabel(direction: string | null | undefined): string {
    return String(direction || '').toLowerCase() === 'short' ? 'buy-and-hold long-only' : 'buy-and-hold'
}

export function isPriceNoDividends(ref: ComparisonReference | null | undefined): boolean {
    if (!ref) return false
    if (ref.return_kind) return ref.return_kind === 'price_no_dividends'
    return ref.asset_class === 'stock' || ref.asset_class === 'etf'
}

export function commonText(common: BenchmarkComparison['common_window']): string {
    if (!common) return ''
    return `${day(common.start)} – ${day(common.end)} · ${thousands(common.days)} dias`
}

export function leftOutText(payload: Pick<BenchmarkComparison, 'left_out' | 'strategy'>): string {
    const parts = payload.left_out || []
    if (parts.length === 0) return 'Nada: a referência cobre o período inteiro da estratégia.'
    return parts
        .map((part) => {
            const span = part.start === part.end ? day(part.start) : `${day(part.start)} – ${day(part.end)}`
            const n = Number(part.trades || 0)
            if (part.note === 'no_session') return `${span} (sem pregão em Nova York) · ${n} ${n === 1 ? 'trade' : 'trades'}`
            return `${span} da estratégia · ${n} ${n === 1 ? 'trade fora' : 'trades fora'}`
        })
        .join('; ')
}

export function hasTradesOut(payload: Pick<BenchmarkComparison, 'left_out'>): boolean {
    return (payload.left_out || []).some((p) => Number(p.trades || 0) > 0 || p.note === 'no_reference')
}

export function insufficientHelp(code: string | null | undefined): string {
    if (code === 'short_overlap') {
        return 'Com poucos dias, anualizar exagera o CAGR. Escolha uma referência com mais histórico dentro do período da estratégia.'
    }
    if (code === 'no_history') return 'A Binance não tem fechamento diário guardado deste ativo. Escolha outra referência.'
    return 'Escolha outra referência com histórico no período da estratégia.'
}

export function fxPair(strategySymbol: string, strategyCurrency: string, ref: ComparisonReference): string {
    return `${strategySymbol} em ${strategyCurrency}, ${ref.symbol} em ${ref.currency || (ref.asset_class === 'crypto' ? 'USDT' : 'USD')}`
}

export function sampleText(payload: BenchmarkComparison, owner: 'result' | 'favorite'): string {
    const sample = payload.samples?.reference
    const version = sample?.version_label
    const parts = [`${payload.reference.symbol}${version ? ` versão ${version}` : ''}`]
    if (payload.collected) parts.push('coletada agora')
    if (owner === 'favorite' && sample?.snapshot_id) parts.push('fixada pelo favorito')
    return parts.length > 1 ? `${parts[0]} (${parts.slice(1).join(', ')})` : parts[0]
}

export interface RecordingContext {
    owner: 'result' | 'favorite'
    favoriteName?: string | null
}

/** Primeira frase da linha de gravação: quando e onde foi gravada. */
export function recordedWhen(payload: BenchmarkComparison, ctx: RecordingContext): string {
    const when = stamp(payload.created_at)
    if (ctx.owner === 'favorite') {
        if (payload.trigger === 'favorite_refresh') {
            return `Refeita na atualização do backtest do favorito${ctx.favoriteName ? ` ${ctx.favoriteName}` : ''} em ${when}.`
        }
        if (payload.owner?.kind === 'result') {
            return `Gravada no resultado em ${when} e herdada pelo favorito${ctx.favoriteName ? ` ${ctx.favoriteName}` : ''} ao salvar.`
        }
        if (payload.owner?.kind === 'discovery_result') {
            return `Gravada na coluna extra da Descoberta em ${when} e herdada pelo favorito ao promover.`
        }
        return `Gravada no favorito${ctx.favoriteName ? ` ${ctx.favoriteName}` : ''} em ${when}.`
    }
    if (payload.trigger === 'run') return `Gravada ao rodar, em ${when}.`
    return `Gravada neste resultado em ${when}.`
}

export function recordedTail(ctx: RecordingContext): string {
    return ctx.owner === 'favorite'
        ? 'Refeita só quando o backtest do favorito é atualizado, com a mesma referência.'
        : 'Ao salvar nos Favoritos, a referência vai junto.'
}

export interface SectionNumbers {
    sRet: string
    sCagr: string
    rRet: string
    rCagr: string
    delta: string
    deltaTone: 'up' | 'down' | 'flat'
    deltaNote: string
    sTone: 'up' | 'down' | 'flat'
    rTone: 'up' | 'down' | 'flat'
}

export function sectionNumbers(payload: BenchmarkComparison): SectionNumbers | null {
    if (payload.status !== 'valid' || !payload.reference_result) return null
    const delta = payload.delta?.cagr_pp ?? null
    return {
        sRet: pctDot(payload.strategy.return),
        sCagr: pctDot(payload.strategy.cagr),
        rRet: pctDot(payload.reference_result.return),
        rCagr: pctDot(payload.reference_result.cagr),
        delta: ppDot(delta),
        deltaTone: toneOf(delta),
        deltaNote: delta === null ? '' : delta >= 0 ? 'a favor da estratégia' : 'a favor da referência',
        sTone: toneOf(payload.strategy.return),
        rTone: toneOf(payload.reference_result.return),
    }
}

// --------------------------------------------------------------------------- seletor (aviso antes da escolha)

export interface WindowLike {
    start?: string | null
    end?: string | null
}

/** Primeiro e último dia do histórico guardado de um ativo (1d quando há). */
export function storedSpan(asset: Pick<CatalogAsset, 'history'> | null | undefined): { from: string | null; to: string | null } {
    const history = asset?.history
    if (!history) return { from: null, to: null }
    const daily = (history.timeframes || []).find((t) => t.timeframe === '1d' && t.from)
    const from = daily?.from ?? history.from ?? null
    const to = daily?.to ?? history.to ?? null
    return { from: from ? from.slice(0, 10) : null, to: to ? to.slice(0, 10) : null }
}

const dayMs = 86400000
const toUtc = (iso: string) => Date.parse(`${iso.slice(0, 10)}T00:00:00Z`)

/** Dias de interseção entre o histórico guardado e a janela (`null` quando falta um dos lados). */
export function overlapDays(span: { from: string | null; to: string | null }, window: WindowLike): number | null {
    if (!span.from || !window.start || !window.end) return null
    const lo = Math.max(toUtc(span.from), toUtc(window.start))
    const hi = Math.min(toUtc(span.to || window.end), toUtc(window.end))
    if (hi < lo) return -1
    return Math.round((hi - lo) / dayMs)
}

export interface ChoiceHint {
    tone: 'warn' | 'note'
    text: string
}

/** Aviso na linha do seletor do resultado, sem coletar e sem bloquear. */
export function resultChoiceHint(asset: Pick<CatalogAsset, 'history'>, window: WindowLike, minDays = MIN_COMMON_DAYS): ChoiceHint | null {
    const days = overlapDays(storedSpan(asset), window)
    if (days === null) return null
    if (days < 0) return { tone: 'warn', text: 'Sem período comum com esta estratégia' }
    if (days < minDays) return { tone: 'warn', text: `Só ${days} ${days === 1 ? 'dia' : 'dias'} em comum com esta estratégia` }
    return null
}

export interface CandidateWindow {
    result_id: string
    symbol: string
    start: string | null
    end: string | null
    /**
     * `kept | pinned | expired` (amostra guardada) ou, para o candidato que nunca guardou amostra
     * (cripto da Descoberta sem o histórico novo), `legacy` (refeito pelas velas do cache e conferido
     * no cálculo pelas métricas gravadas na varredura) e `unavailable` (não dá para refazer: sem a
     * janela da varredura ou sem o cache).
     */
    sample?: string
    retain_until?: string | null
}

/** Aviso contado sobre os candidatos da varredura (Decidir), sem coletar. */
export function columnChoiceHints(
    asset: Pick<CatalogAsset, 'history'>,
    candidates: CandidateWindow[],
    minDays = MIN_COMMON_DAYS,
): ChoiceHint[] {
    const out: ChoiceHint[] = []
    const expired = candidates.filter((c) => c.sample === 'expired')
    // Cripto que nunca guardou amostra e não dá para refazer pelo caminho antigo: não é "vencida".
    const unavailable = candidates.filter((c) => c.sample === 'unavailable')
    if (candidates.length > 0 && expired.length === candidates.length) {
        out.push({ tone: 'warn', text: `Todos os ${candidates.length} candidatos com amostra vencida: rode a varredura de novo para comparar` })
        return out
    }
    if (candidates.length > 0 && unavailable.length === candidates.length) {
        out.push({ tone: 'warn', text: `Todos os ${candidates.length} candidatos sem as velas da varredura: rode a varredura de novo para comparar` })
        return out
    }
    if (candidates.length > 0 && expired.length + unavailable.length === candidates.length) {
        out.push({
            tone: 'warn',
            text: `Nenhum dos ${candidates.length} candidatos tem amostra ou velas da varredura para refazer os trades: rode a varredura de novo para comparar`,
        })
        return out
    }
    const span = storedSpan(asset)
    if (span.from) {
        const days = candidates.map((c) => overlapDays(span, c))
        const known = days.filter((d): d is number => d !== null)
        if (known.length > 0 && known.every((d) => d < 0)) {
            out.push({ tone: 'warn', text: 'Sem período comum com nenhum candidato desta varredura' })
        } else {
            const short = candidates.filter((_, i) => days[i] !== null && (days[i] as number) >= 0 && (days[i] as number) < minDays)
            if (short.length > 0) {
                const names = short.slice(0, 3).map((c) => c.symbol).join(', ')
                out.push({
                    tone: 'note',
                    text: `${short.length} ${short.length === 1 ? 'candidato' : 'candidatos'} com período comum curto (${names}${short.length > 3 ? '…' : ''})`,
                })
            }
        }
    }
    if (expired.length > 0) {
        out.push({ tone: 'note', text: `${expired.length} ${expired.length === 1 ? 'candidato' : 'candidatos'} com amostra vencida` })
    }
    if (unavailable.length > 0) {
        out.push({ tone: 'note', text: `${unavailable.length} ${unavailable.length === 1 ? 'candidato' : 'candidatos'} sem as velas da varredura` })
    }
    return out
}

export function historyLine(asset: CatalogAsset): string {
    const span = storedSpan(asset)
    if (asset.state === 'removed' && span.to) return `Histórico local até ${day(span.to)}`
    if (span.from) return `Histórico desde ${day(span.from)}`
    return 'Sem histórico guardado: coleta ao escolher'
}

export function classLabel(cls: AssetClass | string | null | undefined): string {
    return CLASS_LABEL[String(cls || '')] || ''
}

// --------------------------------------------------------------------------- Favoritos

export function favoriteRefTag(summary: ComparisonSummary | null | undefined): string | null {
    if (!summary || summary.reference?.kind === 'own' || !summary.reference?.symbol) return null
    return `Ref.: ${summary.reference.symbol} · comparação gravada ${shortDay(summary.created_at)}`
}

// --------------------------------------------------------------------------- Decidir: coluna extra

export interface CellSummary {
    state: 'valid' | 'insufficient' | 'pending' | 'no_sample'
    id?: string
    delta_cagr_pp?: number | null
    reference_cagr?: number | null
    common_window?: { start: string; end: string; days: number } | null
    currency_note?: string | null
    reason_code?: string | null
    reason?: string | null
    expired_at?: string | null
}

export type CellView =
    | { kind: 'busy'; text: string }
    | { kind: 'no_sample'; text: string }
    | { kind: 'off'; title: string; reason: string; code: string }
    | { kind: 'valid'; delta: string; tone: 'up' | 'down' | 'flat'; refLine: string; period: string; fx: boolean }

export function cellView(cell: CellSummary | null | undefined, refSymbol: string, computing: boolean): CellView {
    if (!cell || cell.state === 'pending') {
        // "Calculando…" só enquanto a coluna calcula; fora disso a célula não gravada fecha sem número.
        return computing ? { kind: 'busy', text: 'Calculando…' } : { kind: 'no_sample', text: 'Não calculada' }
    }
    if (cell.state === 'no_sample') return { kind: 'no_sample', text: 'Sem amostra' }
    if (cell.state === 'insufficient') {
        return { kind: 'off', title: 'Sem comparação', reason: cell.reason || '', code: cell.reason_code || '' }
    }
    const period = cell.common_window ? `${dayPlain(cell.common_window.start)} – ${dayPlain(cell.common_window.end)}` : ''
    return {
        kind: 'valid',
        delta: ppBr(cell.delta_cagr_pp ?? null),
        tone: toneOf(cell.delta_cagr_pp ?? null),
        refLine: `${refSymbol} ${annualBr(cell.reference_cagr ?? null)}`,
        period,
        fx: Boolean(cell.currency_note),
    }
}

export interface ColumnCounts {
    valid: number
    short_overlap?: number
    no_overlap?: number
    no_history?: number
    sample_expired?: number
    sample_unavailable?: number
    regeneration_failed?: number
    computed: number
    total: number
    currency_note?: boolean
}

/** Resumo da faixa: conta a varredura inteira (todas as páginas), não o recorte filtrado. */
export function stripSummary(counts: ColumnCounts | null | undefined, refSymbol: string): string {
    if (!counts) return ''
    const total = counts.total
    if (total > 0 && (counts.no_overlap ?? 0) === total) {
        return `Nenhum candidato desta varredura tem período comum com ${refSymbol}: o histórico guardado dele não cruza as janelas dos candidatos.`
    }
    const parts: string[] = []
    const add = (n: number | undefined, label: string) => {
        if (n && n > 0) parts.push(`${n} sem comparação (${label})`)
    }
    add(counts.short_overlap, 'período comum curto')
    add(counts.no_overlap, 'sem período comum')
    add(counts.sample_expired, 'amostra vencida')
    // Velas fora do cache, janela não registrada ou trades refeitos que não batem com a varredura.
    add(counts.sample_unavailable, 'sem os trades da varredura')
    add(counts.no_history, 'sem histórico')
    add(counts.regeneration_failed, 'trades não refeitos')
    return `${counts.valid} de ${total} candidatos desta varredura com comparação${parts.length ? `; ${parts.join('; ')}` : ''}.`
}

export function columnHeader(refSymbol: string | null | undefined): string {
    return refSymbol ? `Contra ${refSymbol}` : 'Contra —'
}

export const COLUMN_HINT = 'Δ CAGR · período comum · não ordena'

/**
 * A promoção herda a célula gravada de qualquer coluna ativa (não só da concluída): com a coluna
 * concluída a nota sempre aparece; antes disso, só quando a célula da linha já é válida.
 */
export function showPromotionReferenceNote(status: string | null | undefined, cell: CellSummary | null | undefined): boolean {
    if (!status) return false
    if (status === 'done') return true
    return cell?.state === 'valid'
}

export function promotionReferenceNote(cell: CellSummary | null | undefined, refSymbol: string | null | undefined): string | null {
    if (!refSymbol || !cell) return null
    if (cell.state === 'valid') return `Leva a comparação com ${refSymbol} gravada (mesma referência e mesma amostra, sem recálculo).`
    return `Sem comparação com ${refSymbol}: o favorito vai com a referência padrão (próprio ativo).`
}
