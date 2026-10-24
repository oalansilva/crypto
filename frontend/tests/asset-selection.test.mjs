import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import {
  blockedNotice,
  catalogBanners,
  confirmCopy,
  emptySearchMessage,
  formatDate,
  formatDateTime,
  freshnessLine,
  historyText,
  historySummary,
  ON_DEMAND_TEXT_BACKTEST,
  markedNoteText,
  markedReasonText,
  mergeSymbols,
  outEntries,
  outLabel,
  outNames,
  outOfSweepTitle,
  outReason,
  outWhy,
  partialNotice,
  planRun,
  preflightExcludedLabel,
  preflightRestLine,
  refusalMessage,
  resolveSelection,
  runCopy,
  selectionCountText,
  selectionCounts,
  sortedForChips,
  urlSymbolNotice,
} from '../src/lib/assetSelection.ts'

const asset = (symbol, asset_class, state = 'tradable', extra = {}) => ({
  asset_id: `${asset_class === 'crypto' ? 'binance:spot:' : 'binance:equity:EQ_'}${symbol}`,
  asset_class,
  symbol,
  name: symbol,
  state,
  state_label:
    { tradable: 'Negociável', suspended: 'Suspenso', off_market: 'Fora de mercado', removed: 'Removido' }[state] ?? state,
  state_reason: state === 'suspended' ? 'Negociação pausada pela Binance (status BREAK).' : null,
  selectable: state === 'tradable',
  analysis_available: asset_class === 'crypto',
  history: { status: 'on_demand', from: null, to: null, timeframes: [], gap_count: 0 },
  ...extra,
})

const KNOWN = new Map(
  [
    asset('BTC/USDT', 'crypto'),
    asset('ETH/USDT', 'crypto'),
    asset('WAVES/USDT', 'crypto', 'suspended'),
    asset('AGLD/USDT', 'crypto', 'removed', { state_reason: 'Saiu da lista spot da Binance em 12 set. 2026.' }),
    asset('NVDA', 'stock'),
    asset('AVB', 'stock', 'off_market', { state_reason: 'A Binance marcou a ação como fora de mercado.' }),
    asset('SPY', 'etf'),
    asset('QQQ', 'etf'),
  ].map((a) => [a.symbol, a]),
)

const ok = { status: 'ok', updated_at: '2026-10-20T09:00:00Z', last_attempt_at: '2026-10-20T09:00:00Z', reason: null, code: null, refreshing: false }
const FRESH_OK = { crypto: ok, stock: ok, etf: ok }

const entries = (symbols, fresh = FRESH_OK) => resolveSelection(symbols, KNOWN, fresh)

test('exemplos de verificação: BTC/USDT roda; NVDA, SPY e QQQ ficam na seleção mas fora da análise', () => {
  const sel = entries(['BTC/USDT', 'NVDA', 'SPY', 'QQQ'])
  assert.deepEqual(sel.map((e) => e.kind), ['runs', 'class', 'class', 'class'])
  const counts = selectionCounts(sel)
  assert.deepEqual(
    { crypto: counts.crypto, stock: counts.stock, etf: counts.etf, out: counts.out, total: counts.total },
    { crypto: 1, stock: 1, etf: 2, out: 3, total: 4 },
  )
  assert.equal(selectionCountText(counts), '4 selecionados · 1 cripto · 1 ação · 2 ETFs')
})

test('ativo marcado nunca roda: aparece como "fica de fora", antes do +N, com o estado', () => {
  const sel = entries(['BTC/USDT', 'ETH/USDT', 'WAVES/USDT', 'AGLD/USDT', 'AVB'])
  assert.deepEqual(sel.map((e) => e.kind), ['runs', 'runs', 'marked', 'marked', 'marked'])
  const chips = sortedForChips(sel).map((e) => e.symbol)
  assert.deepEqual(chips.slice(0, 3), ['WAVES/USDT', 'AGLD/USDT', 'AVB'])
  const counts = selectionCounts(sel)
  assert.equal(counts.marked, 3)
  assert.equal(counts.crypto, 2)
  assert.equal(selectionCountText(counts), '5 selecionados · 2 cripto · 3 marcados ficam de fora')
  assert.equal(outLabel(sel[2]), 'WAVES/USDT (Cripto, Suspenso)')
  assert.equal(
    outReason(sel[2]),
    'Negociação pausada pela Binance (status BREAK); não entra em análise nova',
  )
  const note = markedNoteText(sel)
  assert.match(note.title, /Ativos marcados na seleção salva/)
  assert.match(note.body, /a Binance pausou ou retirou esses ativos/)
  assert.match(note.body, /Remova com ×/)
})

test('seleção antiga com um marcado reidrata como está e a nota fala no singular', () => {
  const sel = entries(['BTC/USDT', 'WAVES/USDT'])
  assert.match(markedNoteText(sel).title, /^Ativo marcado/)
  assert.match(markedNoteText(sel).body, /Ele aparece .* fica de fora/)
  assert.equal(outNames(sel), 'WAVES/USDT (Cripto, Suspenso)')
})

test('símbolo desconhecido: "fora do catálogo" só com lista válida; sem lista fica neutro', () => {
  assert.equal(entries(['XYZ/USDT'])[0].kind, 'missing')
  const cryptoDown = { ...FRESH_OK, crypto: { ...ok, status: 'unavailable' } }
  assert.equal(entries(['XYZ/USDT'], cryptoDown)[0].kind, 'runs')
  assert.equal(resolveSelection(['XYZ/USDT'], KNOWN, FRESH_OK, new Set())[0].kind, 'runs') // ainda não consultado
})

test('plano de rodar: nada, bloqueado, 1 par (caminho de 1 ativo) ou lote', () => {
  assert.equal(planRun(entries([])).mode, 'none')
  // Card #1119: 1 ação/ETF sozinha roda (backtest de 1 ativo); mais de uma, ou com cripto, não.
  const oneEquity = planRun(entries(['NVDA']))
  assert.equal(oneEquity.mode, 'single')
  assert.deepEqual(oneEquity.runnable, ['NVDA'])
  assert.equal(oneEquity.equityRun.symbol, 'NVDA')
  assert.equal(planRun(entries(['NVDA', 'SPY'])).mode, 'blocked')
  assert.equal(planRun(entries(['NVDA', 'SPY'])).equityRun, null)
  assert.equal(planRun(entries(['WAVES/USDT'])).mode, 'blocked')
  const equityAndMarked = planRun(entries(['SPY', 'WAVES/USDT']))
  assert.equal(equityAndMarked.mode, 'single')
  assert.deepEqual(equityAndMarked.runnable, ['SPY'])
  assert.equal(equityAndMarked.counts.out, 1) // só o marcado fica de fora
  const single = planRun(entries(['BTC/USDT', 'NVDA', 'WAVES/USDT']))
  assert.equal(single.mode, 'single')
  assert.deepEqual(single.runnable, ['BTC/USDT'])
  const batch = planRun(entries(['BTC/USDT', 'ETH/USDT', 'QQQ']))
  assert.equal(batch.mode, 'batch')
  assert.deepEqual(batch.runnable, ['BTC/USDT', 'ETH/USDT'])
})

test('Combo: cópia antes do clique diz o que roda e o que fica fora', () => {
  assert.equal(runCopy(planRun(entries(['BTC/USDT'])), 'combo').text, '1 ativo selecionado: otimiza, salva em favoritos e abre a página de favoritos.')
  const one = runCopy(planRun(entries(['NVDA'])), 'combo')
  assert.equal(one.blocked, false)
  assert.equal(one.text, '1 ação (NVDA): otimiza e abre o resultado, sem salvar em favoritos: ações e ETFs ainda não podem ser favoritados.')
  assert.equal(runCopy(planRun(entries(['SPY'])), 'combo').text.slice(0, 15), '1 ETF (SPY): ot')
  const only = runCopy(planRun(entries(['NVDA', 'SPY'])), 'combo')
  assert.equal(only.blocked, true)
  assert.equal(only.text, 'Nada será executado nem salvo: NVDA (Ação), SPY (ETF) — ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois.')
  assert.doesNotMatch(only.text, /favoritos/)
  const mixedSingle = runCopy(planRun(entries(['BTC/USDT', 'NVDA'])), 'combo').text
  assert.equal(mixedSingle, 'Roda 1 par cripto (BTC/USDT): otimiza, salva em favoritos e abre a página de favoritos. Fora: NVDA (Ação) — ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois.')
  const mixed = runCopy(planRun(entries(['BTC/USDT', 'ETH/USDT', 'NVDA', 'SPY'])), 'combo').text
  assert.equal(mixed, '2 pares cripto: batch. Cada resultado é salvo em favoritos. Fora: NVDA (Ação), SPY (ETF) — ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois.')
  const old = runCopy(planRun(entries(['BTC/USDT', 'WAVES/USDT'])), 'combo').text
  assert.match(old, /^Roda 1 par cripto \(BTC\/USDT\): otimiza, salva em favoritos e abre a página de favoritos\. Fora: WAVES\/USDT \(Cripto, Suspenso\)/)
  assert.match(old, /não entra em análise nova\.$/)
})

test('Otimização: cópia de 1 ativo, de lote e de nada roda', () => {
  assert.equal(runCopy(planRun(entries(['BTC/USDT'])), 'optimize').text, '1 ativo: otimiza e mostra o resultado ao lado.')
  assert.match(
    runCopy(planRun(entries(['BTC/USDT', 'ETH/USDT'])), 'optimize').text,
    /^2 ativos: lote, uma otimização por ativo com o mesmo template, timeframe e faixas\. O melhor resultado de cada um é salvo em favoritos\.$/,
  )
  const lote = runCopy(planRun(entries(['BTC/USDT', 'ETH/USDT', 'QQQ'])), 'optimize').text
  assert.match(lote, /^2 pares cripto: lote/)
  assert.match(lote, /Fora: QQQ \(ETF\)/)
  const none = runCopy(planRun(entries(['QQQ', 'SPY'])), 'optimize')
  assert.equal(none.blocked, true)
  assert.equal(none.text, 'Nada será executado: QQQ (ETF), SPY (ETF) — ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois.')
  assert.equal(
    runCopy(planRun(entries(['NVDA'])), 'optimize', { timeframe: '1d' }).text,
    '1 ação (NVDA): otimiza em 1d, de 1 a 31 jan. 2024, e mostra o resultado ao lado.',
  )
  assert.equal(runCopy(planRun(entries([])), 'optimize').text, 'Nenhum ativo selecionado: escolha ao menos 1 par cripto em USDT.')
})

test('aviso ao rodar: só ação ou ETF, só marcado e lote misto', () => {
  const eq = blockedNotice(planRun(entries(['NVDA', 'SPY'])), 'combo')
  assert.equal(eq.title, 'Ação e ETF rodam só com 1 ativo por enquanto')
  assert.equal(eq.body, 'NVDA (Ação), SPY (ETF): ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois. Nada foi executado nem salvo. A seleção foi mantida.')
  const marked = blockedNotice(planRun(entries(['WAVES/USDT'])), 'optimize')
  assert.equal(marked.title, 'Ativo marcado pela Binance não entra em análise nova')
  assert.match(marked.body, /Nada foi executado\. A seleção foi mantida\.$/)
  const both = blockedNotice(planRun(entries(['WAVES/USDT', 'SPY', 'QQQ'])), 'optimize')
  assert.equal(both.title, 'Nenhum ativo da seleção pode rodar agora')
  assert.ok(both.body.includes('ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois, e ativos marcados pela Binance não entram em análise nova'))

  const lot = partialNotice(planRun(entries(['BTC/USDT', 'ETH/USDT', 'NVDA', 'SPY'])))
  assert.equal(lot.title, 'Lote iniciado com 2 pares cripto')
  assert.match(lot.body, /^Fora do lote: NVDA \(Ação\), SPY \(ETF\) — /)
  assert.equal(partialNotice(planRun(entries(['BTC/USDT', 'WAVES/USDT']))).title, 'Otimizando 1 par cripto')
  assert.equal(partialNotice(planRun(entries(['BTC/USDT', 'ETH/USDT']))), null)
})

test('"Todos do filtro": confirmação mostra incluídos e marcados de fora, e os novos quando já há seleção', () => {
  const full = confirmCopy('etf', '', 3112, 16, null)
  assert.equal(full.prefix + full.count + full.middle, 'Incluir 3.112 ETFs negociáveis na seleção?')
  assert.equal(full.marked, '16')
  assert.match(full.markedText, /ativos marcados ficam de fora: suspensos, fora de mercado, sem negociação, sem regras ou removidos não podem ser escolhidos para análise nova\./)
  assert.equal(full.suffix, ' O que já está selecionado continua.')

  const search = confirmCopy('all', 'nvidia', 3, 0, 1)
  assert.equal(search.count, '3 (1 novo)')
  assert.match(search.middle, /ativos negociáveis que correspondem a “nvidia” \(todas as classes\) na seleção\?/)
  assert.equal(search.marked, null)
  assert.equal(confirmCopy('crypto', '', 1, 1, 1).middle, ' par cripto negociável na seleção?')
  assert.equal(confirmCopy('all', '', 5, 0, 2).count, '5 (2 novos)')
})

test('falha por classe: lista anterior com aviso e data; sem lista, um erro com Tentar de novo', () => {
  const stale = {
    ...FRESH_OK,
    stock: { ...ok, status: 'stale', updated_at: '2026-10-19T21:00:00Z', last_attempt_at: '2026-10-20T09:00:00Z', reason: 'timeout' },
    etf: { ...ok, status: 'stale', updated_at: '2026-10-19T21:00:00Z' },
  }
  const [banner] = catalogBanners(stale)
  assert.equal(banner.kind, 'stale')
  assert.equal(banner.title, 'Ações e ETFs desatualizados')
  assert.match(banner.body, /A Binance não respondeu na atualização de 20 out\. 2026, 06:00\. Mostrando a lista válida de 19 out\. 2026, 18:00; pesquisa e escolha continuam\./)
  assert.equal(banner.retry, false)
  assert.equal(freshnessLine(stale), 'Cripto atualizado 20 out. 2026, 06:00 · Ações e ETFs de 19 out. 2026, 18:00')

  const down = { ...FRESH_OK, crypto: { ...ok, status: 'unavailable', updated_at: null } }
  const banners = catalogBanners(down)
  assert.equal(banners.length, 1)
  assert.equal(banners[0].kind, 'down')
  assert.equal(banners[0].title, 'Cripto indisponível')
  assert.equal(banners[0].retry, true)
  assert.match(banners[0].body, /não há lista salva de cripto\. Ações e ETFs continuam disponíveis/)
  assert.equal(freshnessLine(down), 'Cripto sem lista · Ações e ETFs atualizados 20 out. 2026, 06:00')

  const both = { ...down, stock: { ...ok, status: 'unavailable' }, etf: { ...ok, status: 'unavailable' } }
  assert.equal(catalogBanners(both).filter((b) => b.kind === 'down').length, 1)
  assert.deepEqual(catalogBanners(FRESH_OK), [])
  assert.equal(freshnessLine(FRESH_OK), 'Catálogo Binance · atualizado 20 out. 2026, 06:00')
})

test('pesquisa vazia durante a falha culpa a Binance, não o símbolo', () => {
  const down = { ...FRESH_OK, crypto: { ...ok, status: 'unavailable' } }
  const msg = emptySearchMessage('btc', 'all', down)
  assert.match(msg, /^Nenhuma ação ou ETF para “btc”\. Cripto está indisponível agora por falha da Binance/)
  assert.doesNotMatch(msg, /Confira o símbolo/)
  assert.match(emptySearchMessage('', 'crypto', down), /^Lista de cripto indisponível por falha da Binance\./)
  assert.match(emptySearchMessage('zzzz', 'all', FRESH_OK), /^Nenhum ativo para “zzzz” em todas as classes\. Confira o símbolo ou troque a classe\./)
  assert.match(emptySearchMessage('zzzz', 'etf', FRESH_OK), /em ETFs\./)
})

test('linhas do seletor: classe, negociação e histórico separados, e motivo do marcado', () => {
  const frame = (timeframe, from, to) => ({ timeframe, from, to, gap_count: 0, gaps: [], updated_at: '2026-10-22T21:00:00Z', origin: 'native' })
  const covered = (frames, extra = {}) => ({ status: 'covered', from: frames[0].from, to: frames[0].to, updated_at: '2026-10-22T21:00:00Z', gap_count: 0, timeframes: frames, ...extra })
  assert.match(
    historyText(asset('BTC/USDT', 'crypto', 'tradable', { history: covered(['1d', '4h', '1h', '15m'].map((tf) => frame(tf, '2017-08-17T00:00:00Z', '2026-10-22T18:00:00Z'))) })),
    /^Histórico desde 17 ago\. 2017 · 4 timeframes · sem lacunas · atualizado 22 out\.(?: 2026)?, \d{2}:\d{2}$/,
  )
  assert.equal(historyText(asset('ETH/USDT', 'crypto')), 'Histórico sob demanda · coletado quando uma análise pedir')
  assert.equal(historyText(asset('NVDA', 'stock')), 'Histórico sob demanda · a coleta começa quando as análises aceitarem ações')
  // Combo e Otimização (card #1119): a coleta acontece ao rodar o backtest de 1 ativo; a Descoberta mantém o texto acima.
  assert.equal(historySummary(asset('NVDA', 'stock'), new Date(), ON_DEMAND_TEXT_BACKTEST).text, 'Histórico sob demanda · coletado ao rodar o backtest de 1 ativo')
  assert.equal(historySummary(asset('ETH/USDT', 'crypto'), new Date(), ON_DEMAND_TEXT_BACKTEST).text, 'Histórico sob demanda · coletado quando uma análise pedir')
  assert.equal(historyText(asset('SPY', 'etf')), 'Histórico sob demanda · a coleta começa quando as análises aceitarem ETFs')
  for (const symbol of ['ETH/USDT', 'NVDA', 'SPY']) assert.doesNotMatch(historyText(asset(symbol, symbol.includes('/') ? 'crypto' : 'stock')), /não coletado/)
  assert.equal(
    historyText(asset('WAVES/USDT', 'crypto', 'suspended', { history: covered([frame('1d', '2018-01-01T00:00:00Z', '2024-05-31T00:00:00Z')], { status: 'frozen', from: '2018-01-01T00:00:00Z', to: '2024-05-31T00:00:00Z' }) })),
    'Histórico 01 jan. 2018 – 31 mai. 2024 · sem atualização: ativo suspenso',
  )
  assert.equal(historyText(asset('X/USDT', 'crypto', 'removed', { history: { status: 'none', from: null, to: null } })), 'Sem histórico local')
  const reason = markedReasonText(KNOWN.get('WAVES/USDT'), true)
  assert.match(reason, /Negociação pausada pela Binance \(status BREAK\)\. Não pode ser escolhido para análise nova; aparece para explicar resultados e favoritos antigos\. Está na seleção salva e fica de fora ao rodar\.$/)
  assert.doesNotMatch(markedReasonText(KNOWN.get('WAVES/USDT'), false), /Está na seleção salva/)
})

test('datas em pt-BR no fuso de São Paulo', () => {
  assert.equal(formatDate('2017-08-17T12:00:00Z'), '17 ago. 2017')
  assert.equal(formatDateTime('2026-10-20T09:00:00Z'), '20 out. 2026, 06:00')
  assert.equal(formatDate(null), '')
  assert.equal(formatDateTime('lixo'), '')
})

test('mergeSymbols soma sem repetir e preserva a ordem', () => {
  assert.deepEqual(mergeSymbols(['BTC/USDT'], ['eth/usdt', 'BTC/USDT', ' nvda ', '']), ['BTC/USDT', 'ETH/USDT', 'NVDA'])
})

test('Preflight da Descoberta: bloco "Fora desta varredura" com os 3 primeiros e o resto', () => {
  const assets = [
    { symbol: 'NVDA', asset_class: 'stock', state: 'tradable', kind: 'class', reason: 'análise ainda não disponível para ações e ETFs', combinations: 2 },
    { symbol: 'SPY', asset_class: 'etf', state: 'tradable', kind: 'class', reason: 'análise ainda não disponível para ações e ETFs', combinations: 2 },
    { symbol: 'QQQ', asset_class: 'etf', state: 'tradable', kind: 'class', reason: 'análise ainda não disponível para ações e ETFs', combinations: 2 },
    { symbol: 'VOO', asset_class: 'etf', state: 'tradable', kind: 'class', reason: 'análise ainda não disponível para ações e ETFs', combinations: 2 },
  ]
  assert.equal(outOfSweepTitle(assets), 'Fora desta varredura: 4 ativos (8 combinações)')
  assert.equal(outOfSweepTitle(assets.slice(0, 1)), 'Fora desta varredura: 1 ativo (2 combinações)')
  assert.equal(preflightExcludedLabel(assets[1]), 'SPY (ETF)')
  assert.equal(preflightRestLine(assets, 3), 'e mais 1 ações e ETFs, pelo mesmo motivo.')
  assert.equal(preflightRestLine(assets.slice(0, 3), 3), null)
  const marked = { symbol: 'WAVES/USDT', asset_class: 'crypto', state: 'suspended', kind: 'marked', reason: 'x', combinations: 1 }
  assert.equal(preflightExcludedLabel(marked), 'WAVES/USDT (Cripto, Suspenso)')
  assert.equal(preflightRestLine([...assets.slice(0, 3), marked], 3), 'e mais 1 ativos, pelos mesmos motivos.')
})

test('recusa estruturada da API vira a mensagem em português; texto antigo segue como estava', () => {
  assert.equal(refusalMessage({ code: 'asset_class_not_supported', message: 'Análise ainda não disponível para ações e ETFs.' }, 'x'), 'Análise ainda não disponível para ações e ETFs.')
  assert.equal(refusalMessage('Batch queue is unavailable', 'x'), 'Batch queue is unavailable')
  assert.equal(refusalMessage(undefined, 'Falha na otimização'), 'Falha na otimização')
  assert.equal(urlSymbolNotice('XYZ/USDT').title, 'XYZ/USDT não está no catálogo da Binance')
})

test('o texto de por que fica fora muda com a mistura', () => {
  assert.equal(outWhy(selectionCounts(entries(['NVDA']))), 'ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois')
  assert.match(outWhy(selectionCounts(entries(['WAVES/USDT']))), /^ativo marcado pela Binance \(suspenso, fora de mercado/)
  assert.ok(outWhy(selectionCounts(entries(['WAVES/USDT', 'NVDA']))).startsWith('ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois, e ativos marcados'))
  assert.equal(outEntries(entries(['BTC/USDT', 'NVDA'])).length, 1)
})

// --- Contrato das telas (texto-fonte): sem texto livre, sem "Edição avançada" de símbolos ------------

test('Descoberta: eixo Ativos com o seletor, sem Edição avançada de símbolos nem catálogo antigo', async () => {
  const source = await readFile(new URL('../src/pages/DiscoveryPage.tsx', import.meta.url), 'utf8')
  assert.match(source, /<AssetPicker/)
  assert.match(source, /title="Ativos"/)
  assert.doesNotMatch(source, /data-testid="edit-symbols"/)
  assert.doesNotMatch(source, /\/exchanges\/binance\/symbols/)
  assert.doesNotMatch(source, /inline-symbols-search/)
  assert.match(source, /data-testid="edit-templates"/)
  assert.match(source, /data-testid="preflight-class-out"/)
})

test('Combo: seletor no lugar do rádio Todos/Seleciona e da lista dupla, com Top 10 e Limpar (1 ativo)', async () => {
  const source = await readFile(new URL('../src/pages/ComboConfigurePage.tsx', import.meta.url), 'utf8')
  assert.match(source, /<AssetPicker/)
  assert.match(source, /clearLabel="Limpar \(1 ativo\)"/)
  assert.match(source, /data-testid="combo-top10"/)
  assert.doesNotMatch(source, /name="scope"/)
  assert.doesNotMatch(source, /Seleciona<\/span>/)
  assert.doesNotMatch(source, /\/exchanges\/binance\/symbols/)
})

test('Otimização: sem texto livre, com o seletor, authFetch e o lote do Combo', async () => {
  const source = await readFile(new URL('../src/pages/ComboOptimizePage.tsx', import.meta.url), 'utf8')
  assert.match(source, /<AssetPicker/)
  assert.doesNotMatch(source, /type="text"/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/backtest\/batch`/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/optimize`/)
  assert.doesNotMatch(source, /[^h]fetch\(`\$\{API_BASE_URL\}/)
  assert.match(source, /urlSymbolNotice/)
})
