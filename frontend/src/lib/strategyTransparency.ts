export type StrategyIndicatorPanel = 'price' | 'volume' | 'oscillator' | 'macd' | 'atr' | string

export interface StrategyIndicatorPoint {
    timestamp_utc: string
    value: number
}

export interface StrategyIndicatorReference {
    value: number
    label: string
    color?: string
}

export interface StrategyTransparencyIndicator {
    key: string
    label: string
    parameters: Record<string, unknown>
    type: string
    panel: StrategyIndicatorPanel
    scale: string
    color: string
    function: string
    participation: string[]
    references: StrategyIndicatorReference[]
    series: StrategyIndicatorPoint[]
    availability: string
    unavailable_reason: string
}

export interface StrategyTransparency {
    status: string
    timeframe: string
    display_name: string
    description: string
    effective_parameters: Record<string, unknown>
    indicators: StrategyTransparencyIndicator[]
    logic_blocks: string[]
    unavailable_reason: string
}

const DEFAULT_COLORS = ['#fcd535', '#2dbdb6', '#3b82f6', '#0ecb81', '#f6465d', '#929aa5']

const asRecord = (value: unknown): Record<string, unknown> => (
    value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {}
)

const asText = (value: unknown, fallback = ''): string => {
    const text = typeof value === 'string' ? value.trim() : ''
    return text || fallback
}

const normalizeAvailability = (value: unknown, hasPoints: boolean): string => {
    if (value === true) return 'available'
    if (value === false) return 'unavailable'
    const record = asRecord(value)
    const raw = asText(record.status ?? record.state ?? value).toLowerCase()
    if (['available', 'ready', 'ok', 'disponivel', 'disponível'].includes(raw)) return 'available'
    if (raw) return raw
    return hasPoints ? 'available' : 'unavailable'
}

const normalizeReferences = (value: unknown): StrategyIndicatorReference[] => {
    if (!Array.isArray(value)) return []
    return value.flatMap((item) => {
        const record = asRecord(item)
        const numericValue = Number(record.value ?? record.level)
        if (!Number.isFinite(numericValue)) return []
        return [{
            value: numericValue,
            label: asText(record.label ?? record.name, String(numericValue)),
            color: asText(record.color) || undefined,
        }]
    })
}

const normalizePoints = (value: unknown): StrategyIndicatorPoint[] => {
    if (!Array.isArray(value)) return []
    const byTimestamp = new Map<number, StrategyIndicatorPoint>()
    value.forEach((item) => {
        const record = asRecord(item)
        const rawTimestamp = record.timestamp_utc ?? record.timestamp ?? record.time
        const timestampMs = typeof rawTimestamp === 'number'
            ? rawTimestamp * (rawTimestamp > 10_000_000_000 ? 1 : 1000)
            : Date.parse(String(rawTimestamp ?? ''))
        const numericValue = Number(record.value)
        if (!Number.isFinite(timestampMs) || !Number.isFinite(numericValue)) return
        byTimestamp.set(timestampMs, {
            timestamp_utc: new Date(timestampMs).toISOString(),
            value: numericValue,
        })
    })
    return [...byTimestamp.entries()]
        .sort(([left], [right]) => left - right)
        .map(([, point]) => point)
}

const normalizeParticipation = (value: unknown): string[] => {
    if (Array.isArray(value)) return value.map((item) => String(item).trim()).filter(Boolean)
    const text = asText(value)
    return text ? [text] : []
}

const normalizeLogicBlocks = (value: unknown): string[] => {
    if (!Array.isArray(value)) return []
    return value.map((item) => {
        if (typeof item === 'string') return item.trim()
        const record = asRecord(item)
        const label = asText(record.label ?? record.title ?? record.name ?? record.participation)
        const description = asText(record.description ?? record.text ?? record.function)
        return [label, description].filter(Boolean).join(': ')
    }).filter(Boolean)
}

export function normalizeStrategyTransparency(value: unknown): StrategyTransparency | null {
    const record = asRecord(value)
    if (Object.keys(record).length === 0) return null

    const indicators = (Array.isArray(record.indicators) ? record.indicators : []).flatMap((item, index) => {
        const indicator = asRecord(item)
        const key = asText(indicator.key ?? indicator.id)
        if (!key) return []
        const series = normalizePoints(indicator.series ?? indicator.points)
        return [{
            key,
            label: asText(indicator.label ?? indicator.display_name, key),
            parameters: asRecord(indicator.parameters),
            type: asText(indicator.type, 'line').toLowerCase(),
            panel: asText(indicator.panel, 'price').toLowerCase(),
            scale: asText(indicator.scale, 'auto').toLowerCase(),
            color: asText(indicator.color, DEFAULT_COLORS[index % DEFAULT_COLORS.length]),
            function: asText(indicator.function ?? indicator.description),
            participation: normalizeParticipation(indicator.participation),
            references: normalizeReferences(indicator.references),
            series,
            availability: normalizeAvailability(indicator.series_status ?? indicator.availability, series.length > 0),
            unavailable_reason: asText(indicator.unavailable_reason),
        } satisfies StrategyTransparencyIndicator]
    })

    return {
        status: asText(record.status, indicators.length > 0 ? 'available' : 'unavailable').toLowerCase(),
        timeframe: asText(record.timeframe).toLowerCase(),
        display_name: asText(record.display_name ?? record.name),
        description: asText(record.description),
        effective_parameters: asRecord(record.parameters ?? record.effective_parameters),
        indicators,
        logic_blocks: normalizeLogicBlocks(record.logic_blocks),
        unavailable_reason: asText(record.unavailable_reason),
    }
}

export function transparencyMatchesTimeframe(
    transparency: StrategyTransparency | null,
    timeframe: string | undefined,
): boolean {
    if (!transparency || !timeframe || !transparency.timeframe) return true
    return transparency.timeframe.toLowerCase() === timeframe.trim().toLowerCase()
}

export function hasAvailableIndicatorSeries(
    value: unknown,
    timeframe: string | undefined,
): boolean {
    const transparency = normalizeStrategyTransparency(value)
    if (!transparency || !transparencyMatchesTimeframe(transparency, timeframe)) return false

    return transparency.indicators.some((indicator) => (
        indicator.availability === 'available' && indicator.series.length > 0
    ))
}

export function indicatorValueAtTimestamp(
    indicator: StrategyTransparencyIndicator,
    timestampSeconds: number,
): number | null {
    const point = indicator.series.find((item) => Math.floor(Date.parse(item.timestamp_utc) / 1000) === timestampSeconds)
    return point?.value ?? null
}

export function buildIndicatorValueIndex(
    indicators: StrategyTransparencyIndicator[],
): Map<string, Map<number, number>> {
    return new Map(indicators.map((indicator) => [
        indicator.key,
        new Map(indicator.series.map((point) => [
            Math.floor(Date.parse(point.timestamp_utc) / 1000),
            point.value,
        ])),
    ]))
}
