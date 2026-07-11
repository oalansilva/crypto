import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

import {
    buildIndicatorValueIndex,
    hasAvailableIndicatorSeries,
    indicatorValueAtTimestamp,
    normalizeStrategyTransparency,
    transparencyMatchesTimeframe,
} from '../src/lib/strategyTransparency.ts'

test('normaliza séries exclusivamente por timestamp e preserva gaps', () => {
    const transparency = normalizeStrategyTransparency({
        status: 'available',
        timeframe: '1d',
        display_name: 'EMA + RSI',
        parameters: { ema_period: 20 },
        indicators: [{
            key: 'rsi',
            label: 'RSI (14)',
            type: 'line',
            panel: 'oscillator',
            scale: '0-100',
            color: '#fcd535',
            series_status: 'available',
            series: [
                { timestamp_utc: '2026-07-03T00:00:00Z', value: 55 },
                { timestamp_utc: '2026-07-01T00:00:00Z', value: 45 },
                { timestamp_utc: 'inválido', value: 99 },
            ],
        }],
        logic_blocks: [{ title: 'Entrada', description: 'EMA confirma tendência.' }],
    })

    assert.ok(transparency)
    assert.deepEqual(transparency.effective_parameters, { ema_period: 20 })
    assert.deepEqual(
        transparency.indicators[0].series.map((point) => point.value),
        [45, 55],
    )
    assert.equal(
        indicatorValueAtTimestamp(transparency.indicators[0], Date.parse('2026-07-02T00:00:00Z') / 1000),
        null,
        'não deve alinhar o ponto anterior por índice',
    )
    assert.equal(
        indicatorValueAtTimestamp(transparency.indicators[0], Date.parse('2026-07-03T00:00:00Z') / 1000),
        55,
    )
    assert.deepEqual(transparency.logic_blocks, ['Entrada: EMA confirma tendência.'])
})

test('bloqueia séries quando timeframe do manifesto diverge', () => {
    const transparency = normalizeStrategyTransparency({ status: 'available', timeframe: '4h' })
    assert.equal(transparencyMatchesTimeframe(transparency, '4H'), true)
    assert.equal(transparencyMatchesTimeframe(transparency, '1d'), false)
})

test('normaliza cores semânticas de médias legadas sem alterar outros indicadores', () => {
    const transparency = normalizeStrategyTransparency({
        status: 'available',
        timeframe: '1d',
        indicators: [
            { key: 'short', type: 'ema', color: '#fcd535' },
            { key: 'sma_medium', type: 'sma', color: '#74b9ff' },
            { key: 'long', alias: 'slow', type: 'sma', color: '#0ecb81' },
            { key: 'media_20', type: 'sma', color: '#74b9ff' },
            { key: 'rsi_14', type: 'rsi', color: '#a970ff' },
        ],
    })

    assert.ok(transparency)
    assert.deepEqual(
        transparency.indicators.map((indicator) => indicator.color),
        ['#f6465d', '#ff9f43', '#3b82f6', '#74b9ff', '#a970ff'],
    )
})

test('só libera cache com série disponível, pontos válidos e timeframe compatível', () => {
    const baseManifest = {
        status: 'available',
        timeframe: '1d',
        indicators: [{
            key: 'short',
            type: 'ema',
            panel: 'price',
            series_status: 'available',
            series: [{ timestamp_utc: '2026-07-01T00:00:00Z', value: 101 }],
        }],
    }

    assert.equal(hasAvailableIndicatorSeries(baseManifest, '1d'), true)
    assert.equal(hasAvailableIndicatorSeries(baseManifest, '4h'), false)
    assert.equal(hasAvailableIndicatorSeries({
        ...baseManifest,
        indicators: [{ ...baseManifest.indicators[0], series_status: 'unavailable' }],
    }, '1d'), false)
    assert.equal(hasAvailableIndicatorSeries({
        ...baseManifest,
        indicators: [{ ...baseManifest.indicators[0], series: [] }],
    }, '1d'), false)
    assert.equal(hasAvailableIndicatorSeries({
        ...baseManifest,
        indicators: [{
            ...baseManifest.indicators[0],
            series: [{ timestamp_utc: 'inválido', value: 101 }],
        }],
    }, '1d'), false)
})

test('indexa séries uma vez para lookup constante por timestamp', () => {
    const indicator = {
        key: 'ema',
        series: Array.from({ length: 10_000 }, (_, index) => ({
            timestamp_utc: new Date(Date.UTC(2026, 0, 1, 0, index)).toISOString(),
            value: index,
        })),
    }
    const index = buildIndicatorValueIndex([indicator])
    const lastTimestamp = Math.floor(Date.parse(indicator.series.at(-1).timestamp_utc) / 1000)

    assert.equal(index.get('ema').size, 10_000)
    assert.equal(index.get('ema').get(lastTimestamp), 9_999)
})

test('gráfico mantém contrato acessível e integra as três superfícies', () => {
    const chartSource = readFileSync(new URL('../src/components/charts/StrategyChartSurface.tsx', import.meta.url), 'utf8')
    const comboSource = readFileSync(new URL('../src/pages/ComboResultsPage.tsx', import.meta.url), 'utf8')
    const favoritesSource = readFileSync(new URL('../src/pages/FavoritesDashboard.tsx', import.meta.url), 'utf8')
    const monitorSource = readFileSync(new URL('../src/components/monitor/ChartModal.tsx', import.meta.url), 'utf8')

    assert.match(chartSource, /aria-label="Legenda dos indicadores da estratégia"/)
    assert.match(chartSource, /Indicadores indisponíveis/)
    assert.match(chartSource, /buildIndicatorValueIndex/)
    assert.match(chartSource, /data-last-candle-timestamp/)
    assert.match(chartSource, /data-series-last-timestamp/)
    assert.match(chartSource, /h-11/)
    assert.match(comboSource, /strategyTransparency=\{strategyTransparency\}/)
    assert.match(favoritesSource, /strategy_transparency: recovered\.strategyTransparency/)
    assert.match(monitorSource, /strategyTransparency=\{activeStrategyTransparency\}/)
})
