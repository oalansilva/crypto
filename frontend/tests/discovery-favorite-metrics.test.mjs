import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import {
  currentCandlesTradesLabel,
  discoveryTrainWindowLabel,
  favoriteGridMetrics,
} from '../src/lib/discoveryFavoriteMetrics.ts'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const favoritesPath = path.resolve(__dirname, '../src/pages/FavoritesDashboard.tsx')
const resultsPath = path.resolve(__dirname, '../src/pages/ComboResultsPage.tsx')

test('discovery helper flattens #193 snapshot and formats window labels', () => {
  const nested = {
    origin_type: 'discovery_sweep',
    result_id: 'RS-B109ED2C80',
    metrics_snapshot: {
      sharpe_ratio: 0.31,
      win_rate: 0.467,
      total_return: 169.51,
      total_return_pct: 16951,
      max_drawdown: 0.165,
      total_trades: 30,
    },
  }
  const grid = favoriteGridMetrics(nested)
  assert.equal(grid.sharpe_ratio, 0.31)
  assert.equal(grid.total_trades, 30)
  assert.equal(grid.win_rate, 0.467)
  assert.equal(grid.total_return_pct, 16951)
  assert.equal(grid.max_drawdown, 0.165)
  assert.equal(
    discoveryTrainWindowLabel('2020-10-10', '2024-02-01'),
    'Resumo · janela de treino da Descoberta · 10/10/2020 → 01/02/2024',
  )
  assert.equal(
    currentCandlesTradesLabel(12),
    'Lista de operações · velas atuais · 12 negócios — não é a janela da Descoberta',
  )
  const combo = { sharpe_ratio: 0.5, total_trades: 72 }
  assert.equal(favoriteGridMetrics(combo), combo)
})

test('favorites grid keeps discovery snapshot trades off the regenerated list', async () => {
  const source = await readFile(favoritesPath, 'utf8')
  assert.match(source, /favoriteGridMetrics/)
  assert.match(source, /isDiscoveryOrigin\(fav\.metrics\)/)
  assert.match(source, /data-testid=\{`favorite-\$\{fav\.id\}`\}/)
  assert.match(source, /table className="fav-strategies"/)
})

test('combo results summary uses snapshot for discovery and labels current-candle trades', async () => {
  const source = await readFile(resultsPath, 'utf8')
  assert.match(source, /isDiscovery/)
  assert.match(source, /derivedMetrics \? \{ \.\.\.baseMetrics, \.\.\.derivedMetrics \}/)
  assert.match(source, /discoveryTrainWindowLabel/)
  assert.match(source, /currentCandlesTradesLabel/)
  assert.match(source, /data-testid=\{summaryWindowLabel \? 'summary-window-label' : 'combo-result-title'\}/)
  assert.match(source, /data-testid="trades-window-label"/)
})
