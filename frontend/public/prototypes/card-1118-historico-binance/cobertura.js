/* Card #1118 — DELTA do protótipo: linhas do seletor com cobertura do histórico,
   detalhe por timeframe, estado da amostra no Decidir e painel de demonstração.
   O resto da página é clone da página viva (COPIED). Só protótipo; não vai para o produto. */
(function () {
  'use strict'

  var page = document.body.getAttribute('data-page') || 'discovery'
  var CLASS_LABEL = { crypto: 'Cripto', stock: 'Ação', etf: 'ETF' }
  var TOTALS = { all: [8685, 8393], crypto: [725, 511], stock: [4832, 4770], etf: [3128, 3112] }
  var PAGE_SIZE = 6
  var CRYPTO_NOTE = 'Binance Spot · 24/7 · ajuste não se aplica'
  var EQUITY_NOTE = 'Binance Ações · pregão regular de Nova York · ajustado'

  function tf(name, period, gaps, updated, origin) {
    return { name: name, period: period, gaps: gaps, updated: updated, origin: origin }
  }

  // Coberturas de demonstração (22 out. 2026). Atualização no horário de Brasília (fuso do navegador);
  // lacunas de ação e ETF no horário de Nova York, rotuladas na própria célula.
  var COVERED_QQQ = {
    kind: 'covered',
    since: '11 nov. 2014',
    gapsCount: 0,
    updated: '22 out., 18:07',
    tfs: [tf('1d', '11 nov. 2014 – 22 out. 2026', 'sem lacunas', '22 out., 18:07', 'nativo')],
    note: EQUITY_NOTE,
  }
  var COLLECTING_QQQ = {
    kind: 'collecting',
    text: 'Coletando histórico · 1d, página 2 · pedido às 18:06',
    note: EQUITY_NOTE,
    tfs: [tf('1d', 'até agora: 05 jan. 2023 – 22 out. 2026', 'em coleta', '22 out., 18:06', 'nativo')],
  }
  var FAILED_QQQ = {
    kind: 'failed',
    text: 'Coleta falhou 22 out., 18:06 · limite de requisições da Binance · já coletado: 1d desde 05 jan. 2023',
    note: EQUITY_NOTE,
    tfs: [
      tf('1d', '05 jan. 2023 – 22 out. 2026', 'incompleto: faltam os candles antes de 05 jan. 2023; a coleta continua do ponto em que parou no próximo pedido', '22 out., 18:06', 'nativo'),
    ],
  }

  var ASSETS = [
    {
      symbol: 'BTC/USDT', name: 'Bitcoin', cls: 'crypto',
      cov: {
        kind: 'covered', since: '17 ago. 2017', gapsCount: 0, updated: '22 out., 18:00', note: CRYPTO_NOTE,
        tfs: [
          tf('1d', '17 ago. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('4h', '17 ago. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('1h', '17 ago. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('15m', '17 ago. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
        ],
      },
    },
    {
      symbol: 'ETH/USDT', name: 'Ethereum', cls: 'crypto',
      cov: {
        kind: 'covered', since: '17 ago. 2017', gapsCount: 0, updated: '22 out., 18:00', note: CRYPTO_NOTE,
        tfs: [
          tf('1d', '17 ago. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('4h', '17 ago. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('1h', '17 ago. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('15m', '17 ago. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
        ],
      },
    },
    {
      symbol: 'NVDA', name: 'NVIDIA Corporation Common Stock', cls: 'stock',
      cov: {
        kind: 'covered', since: '11 nov. 2014', gapsCount: 0, updated: '22 out., 17:12', note: EQUITY_NOTE,
        tfs: [
          tf('1d', '11 nov. 2014 – 22 out. 2026', 'sem lacunas', '22 out., 17:12', 'nativo'),
          tf('5m', '19 mai. 2026 – 22 out. 2026', 'sem lacunas', '22 out., 17:12', 'nativo'),
          tf('15m', '19 mai. 2026 – 22 out. 2026', 'sem lacunas', '22 out., 17:12', 'montado do 5m'),
        ],
      },
    },
    {
      symbol: 'SPY', name: 'State Street SPDR S&P 500 ETF Trust', cls: 'etf',
      cov: {
        // Só lacunas de séries nativas somam no resumo: o 15m derivado repete a do 5m.
        kind: 'covered', since: '11 nov. 2014', gapsCount: 1, updated: '22 out., 17:12', note: EQUITY_NOTE,
        tfs: [
          tf('1d', '11 nov. 2014 – 22 out. 2026', 'sem lacunas', '22 out., 17:12', 'nativo'),
          tf('5m', '01 jul. 2026 – 22 out. 2026', '1 lacuna: 14 out. 2026, 10:05–10:40, horário de Nova York (8 candles que a Binance não tem)', '22 out., 17:12', 'nativo'),
          tf('15m', '01 jul. 2026 – 22 out. 2026', 'herdada do 5m: 14 out. 2026, 10:00–10:45, horário de Nova York (bloco incompleto; não soma no resumo)', '22 out., 17:12', 'montado do 5m'),
        ],
      },
    },
    { symbol: 'QQQ', name: 'Invesco QQQ Trust, Series 1', cls: 'etf', cov: COLLECTING_QQQ },
    { symbol: 'AAPL', name: 'Apple Inc. Common Stock', cls: 'stock', cov: { kind: 'on_demand' } },
    {
      symbol: 'SOL/USDT', name: 'Solana', cls: 'crypto',
      cov: {
        kind: 'covered', since: '11 ago. 2020', gapsCount: 0, updated: '22 out., 18:00', note: CRYPTO_NOTE,
        tfs: [
          tf('1d', '11 ago. 2020 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('4h', '11 ago. 2020 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('1h', '11 ago. 2020 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('15m', '11 ago. 2020 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
        ],
      },
    },
    {
      symbol: 'IBIT', name: 'iShares Bitcoin Trust ETF', cls: 'etf',
      cov: {
        kind: 'partial', text: 'Parcial: pedido desde 22 out. 2021; a Binance tem desde 11 jan. 2024 · atualizado 21 out., 10:30',
        note: EQUITY_NOTE,
        tfs: [tf('1d', '11 jan. 2024 – 21 out. 2026', 'insuficiente para o último pedido (desde 22 out. 2021): a Binance não tem candles antes de 11 jan. 2024', '21 out., 10:30', 'nativo')],
      },
    },
    { symbol: 'MSFT', name: 'Microsoft Corporation Common Stock', cls: 'stock', cov: { kind: 'on_demand' } },
    { symbol: 'TSLA', name: 'Tesla, Inc. Common Stock', cls: 'stock', cov: { kind: 'on_demand' } },
    {
      symbol: 'BNB/USDT', name: 'BNB', cls: 'crypto',
      cov: {
        kind: 'covered', since: '06 nov. 2017', gapsCount: 0, updated: '22 out., 18:00', note: CRYPTO_NOTE,
        tfs: [
          tf('1d', '06 nov. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('4h', '06 nov. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('1h', '06 nov. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
          tf('15m', '06 nov. 2017 – 22 out. 2026', 'sem lacunas', '22 out., 18:00', 'nativo'),
        ],
      },
    },
    {
      symbol: 'WAVES/USDT', name: 'Waves', cls: 'crypto', marked: true, stateLabel: 'Suspenso',
      reason: 'Negociação pausada pela Binance (status BREAK). Não pode ser escolhido para análise nova; aparece para explicar resultados e favoritos antigos.',
      cov: {
        kind: 'frozen', text: 'Histórico 01 jan. 2018 – 31 mai. 2024 · sem atualização: ativo suspenso', note: CRYPTO_NOTE,
        tfs: [tf('1d', '01 jan. 2018 – 31 mai. 2024', 'sem lacunas', '31 mai. 2024, 21:00', 'nativo')],
      },
    },
  ]

  var state = {
    q: '',
    filter: 'all',
    page: 1,
    selected: page === 'discovery' ? [] : ['BTC/USDT'],
    open: {},
    sampleExpired: false,
    btcFavorite: false,
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    })
  }
  function fmtInt(n) { return n.toLocaleString('pt-BR') }
  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '') }
  function byId(id) { return document.getElementById(id) }
  function find(symbol) { return ASSETS.filter(function (a) { return a.symbol === symbol })[0] }
  function slug(symbol) { return symbol.replace(/[^A-Za-z0-9]/g, '-') }

  // Até o #1119 só a consulta coleta ação e ETF (decisão de Alan, 23/10/2026): o texto não promete gatilho na tela.
  var ON_DEMAND = {
    crypto: 'Histórico sob demanda · coletado quando uma análise pedir',
    stock: 'Histórico sob demanda · a coleta começa quando as análises aceitarem ações',
    etf: 'Histórico sob demanda · a coleta começa quando as análises aceitarem ETFs',
  }

  // "desde" diz de qual timeframe é: início comum, ou um início por grupo de timeframes.
  function sinceText(c) {
    var groups = []
    c.tfs.forEach(function (t) {
      var start = t.period.split(' – ')[0]
      var g = groups.filter(function (x) { return x.start === start })[0]
      if (g) g.names.push(t.name)
      else groups.push({ start: start, names: [t.name] })
    })
    var n = c.tfs.length
    if (groups.length === 1) return 'Histórico desde ' + groups[0].start + ' · ' + n + (n === 1 ? ' timeframe' : ' timeframes')
    return groups.map(function (g) {
      var names = g.names.length > 1 ? g.names.slice(0, -1).join(', ') + ' e ' + g.names[g.names.length - 1] : g.names[0]
      return names + ' desde ' + g.start
    }).join(' · ')
  }

  function histFact(a) {
    var c = a.cov
    if (c.kind === 'on_demand') {
      return '<span class="ap-fact hist">' + ON_DEMAND[a.cls] + '</span>'
    }
    if (c.kind === 'collecting') {
      return '<span class="ap-fact hist cov-busy" role="status">' + esc(c.text) + '</span>'
    }
    if (c.kind === 'failed') {
      return '<span class="ap-fact hist cov-fail">' + esc(c.text) + '</span>'
    }
    if (c.kind === 'partial') {
      return '<span class="ap-fact hist cov-gap">' + esc(c.text) + '</span>'
    }
    if (c.kind === 'frozen') {
      return '<span class="ap-fact hist">' + esc(c.text) + '</span>'
    }
    var gaps = c.gapsCount === 0 ? 'sem lacunas' : c.gapsCount === 1 ? '1 lacuna' : c.gapsCount + ' lacunas'
    return (
      '<span class="ap-fact hist' + (c.gapsCount ? ' cov-gap' : '') + '">' + esc(sinceText(c)) +
      ' · ' + gaps + ' · atualizado ' + esc(c.updated) + '</span>'
    )
  }

  function covButton(a) {
    if (!a.cov.tfs) return ''
    var id = 'cov-' + slug(a.symbol)
    var open = !!state.open[a.symbol]
    return (
      '<button type="button" class="ap-cov-btn" data-cov="' + esc(a.symbol) + '" aria-expanded="' + open +
      '" aria-controls="' + id + '">Cobertura<span class="sr-only"> de ' + esc(a.symbol) + '</span></button>'
    )
  }

  function covPanel(a) {
    if (!a.cov.tfs || !state.open[a.symbol]) return ''
    var rows = a.cov.tfs.map(function (t) {
      var derived = t.origin !== 'nativo'
      var gapCls = /^sem lacunas/.test(t.gaps) ? '' : /lacuna|herdada|incompleto|insuficiente/.test(t.gaps) ? ' warn' : /coleta/.test(t.gaps) ? ' busy' : ''
      return (
        '<li class="ap-cov-tf">' +
        '<span class="tf"><b>' + esc(t.name) + '</b>' + (derived ? ' <span class="ap-cov-derived">derivado</span>' : '') + '</span>' +
        '<span class="cell"><span class="lbl">Período coberto</span>' + esc(t.period) + '</span>' +
        '<span class="cell' + gapCls + '"><span class="lbl">Lacunas</span>' + esc(t.gaps) + '</span>' +
        '<span class="cell"><span class="lbl">Atualizado (Brasília)</span>' + esc(t.updated) + '</span>' +
        '<span class="cell"><span class="lbl">Origem</span>' + esc(t.origin) + '</span>' +
        '</li>'
      )
    })
    return (
      '<div class="ap-cov" id="cov-' + slug(a.symbol) + '" role="region" aria-label="Cobertura do histórico de ' + esc(a.symbol) + '">' +
      '<p class="ap-cov-note">' + esc(a.cov.note) + '. Mercado fechado não conta como lacuna.</p>' +
      '<ul>' + rows.join('') + '</ul></div>'
    )
  }

  function rowHtml(a) {
    var cls = CLASS_LABEL[a.cls]
    var inSel = state.selected.indexOf(a.symbol) >= 0
    var pickId = 'pick-' + slug(a.symbol) + '-' + page
    var name = '<strong>' + esc(a.symbol) + '</strong><span>' +
      esc(a.cls === 'crypto' ? a.name + ' · Spot, cotação USDT' : a.name) + '</span>'
    // Linha selecionável = <div> com <label for> no nome: o botão "Cobertura" fica fora do <label> (HTML válido).
    var identity = a.marked
      ? '<span class="ap-id">' + name + '</span>'
      : '<label class="ap-id" for="' + pickId + '">' + name + '</label>'
    var facts =
      '<span class="ap-facts"><span class="ap-fact cls-' + a.cls + '">' + cls + '</span>' +
      '<span class="ap-fact ' + (a.marked ? 'st-marked' : 'st-ok') + '">' + (a.marked ? esc(a.stateLabel) : 'Negociável') + '</span>' +
      histFact(a) + covButton(a) + '</span>'
    var head
    if (a.marked) {
      head =
        '<div class="ap-row marked" data-asset="' + esc(a.symbol) + '"><input type="checkbox" disabled aria-label="' +
        esc(a.symbol) + ' — ' + cls + ', ' + esc(a.stateLabel) + ': não pode ser escolhido">' + identity + facts +
        '<p class="ap-reason">' + esc(a.reason) + '</p></div>'
    } else {
      head =
        '<div class="ap-row" data-asset="' + esc(a.symbol) + '" data-row-pick="' + esc(a.symbol) + '"><input type="checkbox" id="' + pickId +
        '" data-pick="' + esc(a.symbol) + '"' + (inSel ? ' checked' : '') + ' aria-label="' + esc(a.symbol) + ' — ' + cls + '">' +
        identity + facts + '</div>'
    }
    return '<div class="ap-item">' + head + covPanel(a) + '</div>'
  }

  function filtered() {
    var n = norm(state.q.trim())
    return ASSETS.filter(function (a) {
      if (state.filter !== 'all' && a.cls !== state.filter) return false
      return !n || norm(a.symbol + '\n' + a.name).indexOf(n) >= 0
    })
  }

  function renderList() {
    var list = document.querySelector('[data-testid="asset-results"]')
    if (!list) return
    var rows = filtered()
    var pages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE))
    if (state.page > pages) state.page = pages
    var slice = rows.slice((state.page - 1) * PAGE_SIZE, state.page * PAGE_SIZE)
    list.innerHTML = slice.length
      ? slice.map(rowHtml).join('')
      : '<p class="ap-empty" data-testid="asset-empty">Nenhum ativo da amostra com “' + esc(state.q.trim()) + '”. Confira o símbolo ou o nome.</p>'

    var range = document.querySelector('[data-testid="asset-range"]')
    var pager = range ? range.parentElement : null
    var searching = !!state.q.trim()
    var total = searching ? rows.length : TOTALS[state.filter][0]
    if (range) {
      var start = (state.page - 1) * PAGE_SIZE
      range.textContent = slice.length
        ? fmtInt(start + 1) + '–' + fmtInt(start + slice.length) + ' de ' + fmtInt(total)
        : '0 de 0'
    }
    if (pager) {
      var btns = pager.querySelectorAll('button')
      btns[0].disabled = state.page <= 1
      btns[1].disabled = state.page >= pages
    }
    var all = document.querySelector('[data-testid="asset-select-all"]')
    if (all) {
      var eligible = searching ? rows.filter(function (a) { return !a.marked }).length : TOTALS[state.filter][1]
      all.textContent = 'Todos do filtro (' + fmtInt(eligible) + ')'
      all.disabled = eligible === 0
    }
  }

  function renderSelection() {
    var counts = { crypto: 0, stock: 0, etf: 0 }
    state.selected.forEach(function (s) { var a = find(s); if (a) counts[a.cls] += 1 })
    var total = state.selected.length
    var parts = []
    if (counts.crypto) parts.push(counts.crypto + ' cripto')
    if (counts.stock) parts.push(counts.stock + (counts.stock === 1 ? ' ação' : ' ações'))
    if (counts.etf) parts.push(counts.etf + (counts.etf === 1 ? ' ETF' : ' ETFs'))
    var countEl = document.querySelector('[data-testid="asset-count"]')
    if (countEl) countEl.textContent = total + (total === 1 ? ' selecionado' : ' selecionados') + (parts.length ? ' · ' + parts.join(' · ') : '')
    var chips = document.querySelector('[data-testid="asset-chips"]')
    if (chips) {
      chips.innerHTML = total
        ? state.selected.map(function (s) {
            var a = find(s)
            return '<span class="ap-chip" data-asset="' + esc(s) + '"><span><b>' + esc(s) + '</b> · ' + CLASS_LABEL[a.cls] +
              '</span><button type="button" data-unpick="' + esc(s) + '" aria-label="Remover ' + esc(s) + ' da seleção">×</button></span>'
          }).join('')
        : '<span class="ap-none">Nenhum ativo selecionado.</span>'
    }
    var note = document.querySelector('[data-testid="asset-class-note"]')
    if (note) note.hidden = !(counts.stock + counts.etf)
  }

  function render() {
    renderList()
    renderSelection()
  }

  // --- Decidir (só na Descoberta) -----------------------------------------------------
  function renderSample() {
    var evid = byId('sample-evidence')
    if (evid) {
      // Favorito guarda a amostra do último refresh diário (decisão de Alan, 23/10/2026), não a da varredura.
      evid.innerHTML = state.sampleExpired
        ? ' · <span class="sample-state cov-fail-text">amostra expirada em 21 nov. 2026: não reproduzível exatamente</span>' +
          (state.btcFavorite ? ' · favoritos guardam a amostra do último refresh' : '')
        : ' · amostra guardada até 21 nov. 2026; favoritos guardam a amostra do último refresh'
    }
    Array.prototype.forEach.call(document.querySelectorAll('[data-sample-row]'), function (el) {
      var fav = el.getAttribute('data-sample-row') === 'BTC/USDT' && state.btcFavorite
      var own = state.sampleExpired
        ? ' · <span class="sample-state cov-fail-text">não reproduzível exatamente</span>'
        : ' · amostra até 21 nov. 2026'
      el.innerHTML = own + (fav ? ' · <span class="sample-state cov-ok-text">favorito: Favoritos guarda a amostra do último refresh</span>' : '')
    })
  }

  function setTab(name) {
    var act = document.body.getAttribute('data-tab-active')
    var idle = document.body.getAttribute('data-tab-idle')
    ;['montar', 'decidir'].forEach(function (key) {
      var tab = byId('tab-' + key)
      var panel = byId('panel-' + key)
      if (!tab || !panel) return
      var on = key === name
      tab.className = on ? act : idle
      tab.setAttribute('aria-selected', on ? 'true' : 'false')
      tab.setAttribute('tabindex', on ? '0' : '-1')
      panel.hidden = !on
    })
  }

  function setPressed(id, on) {
    var el = byId(id)
    if (el) el.setAttribute('aria-pressed', on ? 'true' : 'false')
  }

  function demo(action) {
    var qqq = find('QQQ')
    if (action === 'qqq-done') qqq.cov = COVERED_QQQ
    if (action === 'qqq-fail') qqq.cov = FAILED_QQQ
    if (action === 'qqq-busy') qqq.cov = COLLECTING_QQQ
    if (action === 'sample-kept') state.sampleExpired = false
    if (action === 'sample-expired') state.sampleExpired = true
    if (action === 'btc-fav') state.btcFavorite = !state.btcFavorite
    setPressed('demo-qqq-busy', qqq.cov === COLLECTING_QQQ)
    setPressed('demo-qqq-done', qqq.cov === COVERED_QQQ)
    setPressed('demo-qqq-fail', qqq.cov === FAILED_QQQ)
    setPressed('demo-sample-kept', !state.sampleExpired)
    setPressed('demo-sample-expired', state.sampleExpired)
    setPressed('demo-btc-fav', state.btcFavorite)
    render()
    renderSample()
  }

  // Abrir/fechar a cobertura nunca marca o ativo; o foco volta ao botão depois do re-render.
  function toggleCov(sym, open) {
    state.open[sym] = open
    renderList()
    var again = document.querySelector('[data-cov="' + sym + '"]')
    if (again) again.focus()
  }

  document.addEventListener('click', function (ev) {
    var t = ev.target.closest('button, input, label')
    if (!t) {
      // A linha inteira continua clicável como no vivo (lá ela é um <label>).
      var row = ev.target.closest('[data-row-pick]')
      var box = row && row.querySelector('[data-pick]')
      if (box && !box.disabled) box.click()
      return
    }
    if (t.tagName === 'LABEL') return
    if (t.matches('[data-cov]')) {
      toggleCov(t.getAttribute('data-cov'), !state.open[t.getAttribute('data-cov')])
      return
    }
    if (t.matches('[data-unpick]')) {
      var s = t.getAttribute('data-unpick')
      state.selected = state.selected.filter(function (x) { return x !== s })
      render()
      var search = document.querySelector('[data-testid="asset-search"]')
      if (search) search.focus()
      return
    }
    if (t.matches('.ap-class')) {
      state.filter = t.getAttribute('data-cls')
      state.page = 1
      Array.prototype.forEach.call(document.querySelectorAll('.ap-class'), function (b) {
        b.setAttribute('aria-pressed', b === t ? 'true' : 'false')
      })
      renderList()
      return
    }
    if (t.matches('[data-testid="asset-clear"]')) {
      state.selected = page === 'configure' ? ['BTC/USDT'] : []
      render()
      return
    }
    if (t.matches('[data-mode-tab]')) {
      var key = t.getAttribute('data-mode-tab')
      if (key === 'montar' || key === 'decidir') setTab(key)
      return
    }
    if (t.matches('[data-demo]')) {
      demo(t.getAttribute('data-demo'))
      return
    }
    var pager = t.closest('.ap-pager')
    if (pager && t.tagName === 'BUTTON') {
      var btns = pager.querySelectorAll('button')
      state.page += t === btns[0] ? -1 : 1
      renderList()
    }
  })

  document.addEventListener('change', function (ev) {
    var t = ev.target
    if (t.matches && t.matches('[data-pick]')) {
      var s = t.getAttribute('data-pick')
      if (t.checked) { if (state.selected.indexOf(s) < 0) state.selected.push(s) }
      else state.selected = state.selected.filter(function (x) { return x !== s })
      renderSelection()
    }
  })

  document.addEventListener('input', function (ev) {
    var t = ev.target
    if (t.matches && t.matches('[data-testid="asset-search"]')) {
      state.q = t.value
      state.page = 1
      renderList()
    }
  })

  // Esc fecha a tabela de Cobertura (com o foco no botão ou dentro dela) e devolve o foco ao botão.
  document.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Escape') return
    var t = ev.target
    var btn = t.closest && t.closest('[data-cov]')
    var region = !btn && t.closest && t.closest('.ap-cov')
    var sym = btn ? btn.getAttribute('data-cov') : null
    if (region) {
      var owner = document.querySelector('[aria-controls="' + region.id + '"]')
      sym = owner ? owner.getAttribute('data-cov') : null
    }
    if (!sym || !state.open[sym]) return
    ev.preventDefault()
    toggleCov(sym, false)
  })

  // Tablist: setas como no vivo (Montar ↔ Decidir; Acompanhando desabilitado).
  document.addEventListener('keydown', function (ev) {
    var t = ev.target
    if (!t.matches || !t.matches('[data-mode-tab]')) return
    if (ev.key !== 'ArrowLeft' && ev.key !== 'ArrowRight') return
    var next = t.getAttribute('data-mode-tab') === 'montar' ? 'decidir' : 'montar'
    setTab(next)
    byId('tab-' + next).focus()
    ev.preventDefault()
  })

  render()
  renderSample()
  if (byId('panel-decidir')) setTab('montar')
})()
