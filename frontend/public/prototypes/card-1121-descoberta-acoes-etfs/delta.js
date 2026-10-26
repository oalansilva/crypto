/* Card #1121 — DELTA do protótipo: Descoberta com cripto, ação e ETF na mesma varredura.
   Nada aqui vai para o produto além do comportamento descrito no design.md; números, datas e ids são amostra.
   O DOM COPIED é o vivo; este script só troca estados (modo, progresso, filtro, promoção) como o React faria. */
(function () {
  'use strict';
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var SWEEP = 'c1121mix';

  var ICON = {
    ok: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="m9 12 2 2 4-4"></path></svg>',
    warn: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>',
    info: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>',
    fail: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="m15 9-6 6"></path><path d="m9 9 6 6"></path></svg>',
    clock: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>',
    load: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"></path><path d="m16.2 7.8 2.9-2.9"></path><path d="M18 12h4"></path><path d="m16.2 16.2 2.9 2.9"></path><path d="M12 18v4"></path><path d="m4.9 19.1 2.9-2.9"></path><path d="M2 12h4"></path><path d="m4.9 4.9 2.9 2.9"></path></svg>',
    check: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check h-3.5 w-3.5" aria-hidden="true"><path d="M20 6 9 17l-5-5"></path></svg>',
    pause: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-pause h-4 w-4" aria-hidden="true"><rect x="14" y="3" width="5" height="18" rx="1"></rect><rect x="5" y="3" width="5" height="18" rx="1"></rect></svg>',
    play: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-play h-4 w-4" aria-hidden="true"><path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"></path></svg>'
  };
  var CLS = { crypto: 'Cripto', stock: 'Ação', etf: 'ETF' };
  var CLS_PLURAL = { crypto: 'cripto', stock: 'ação', etf: 'ETF' };
  var CUR = { crypto: 'USDT', stock: 'USD', etf: 'USD' };
  var CONV = { crypto: 'Binance Spot · 24/7 · 365 dias/ano', stock: 'Binance Ações · NY · split · 252/ano', etf: 'Binance Ações · NY · split · 252/ano' };
  var ASSETS = [
    { symbol: 'BTC/USDT', cls: 'crypto', rid: 'RS-BTC1121A1' },
    { symbol: 'NVDA', cls: 'stock', rid: 'RS-NVDA1121B2' },
    { symbol: 'SPY', cls: 'etf', rid: 'RS-SPY1121C3' }
  ];
  function assetBy(sym) { return ASSETS.filter(function (a) { return a.symbol === sym; })[0] || null; }
  var NO_5M = 'o 5m da Binance começa em 2 jan. 2026';
  var ASSET_PAGE = 50;

  // Identidade de execução por ativo, tempo e cenário (amostra).
  function rowInfo(sym, past) {
    var a = assetBy(sym);
    if (a.cls === 'crypto') {
      return { cls: a.cls, tone: 'info', prec: 'Precisão intrabar (15m)', short: 'Precisão intrabar (15m)', eff: past ? '1 jan. 2019 – 31 dez. 2020' : '17 ago. 2017 – 25 out. 2026' };
    }
    return past
      ? { cls: a.cls, tone: 'warn', prec: 'Precisão diária · sem 15m de 2 jan. 2019 a 31 dez. 2020', short: 'Precisão diária (2019–2020)', eff: '2 jan. 2019 – 31 dez. 2020' }
      : { cls: a.cls, tone: 'warn', prec: 'Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025', short: 'Precisão diária (2003–2025)', eff: '2 jan. 2003 – 23 out. 2026' };
  }
  function chipHTML(cls) { return '<span class="d21-cls" data-class="' + cls + '">' + CLS[cls] + '</span> <span class="d21-cur">' + CUR[cls] + '</span>'; }

  // Bloco do candidato em 2 linhas lógicas (decisão 11): identidade + precisão; convenções + período efetivo.
  function rowHTML(sym, tf, withSym, past) {
    var r = rowInfo(sym, past);
    var chip = '<span class="d21-g">' + chipHTML(r.cls) + '</span>';
    var lead = withSym ? '<span class="d21-g"><b>' + sym + '</b> · ' + tf + ' · Long</span> ' + chip : chip;
    var txt = r.short === r.prec ? '<span>' + r.prec + '</span>' : '<span aria-hidden="true">' + r.short + '</span><span class="sr-only">' + r.prec + '</span>';
    return '<span class="d21-l1">' + lead + ' <span class="d21-g d21-prec" data-tone="' + r.tone + '" data-testid="d21-precision" title="' + r.prec + '">' + (r.tone === 'warn' ? ICON.warn : ICON.info) + txt + '</span></span>' +
      '<span class="d21-l2"><span class="d21-conv">' + CONV[r.cls].replace(/ · /g, ' ·&nbsp;') + '</span> ' +
      '<span class="d21-g"><span class="sr-only">Período efetivo </span><span title="Período efetivo">' + r.eff + '</span></span></span>';
  }
  function insufficientHTML(a, tf) {
    return '<span class="d21-l1"><span class="d21-g"><b>' + a.symbol + '</b> · ' + tf + ' · Long</span> <span class="d21-g">' + chipHTML(a.cls) + '</span> <span class="d21-prec" data-tone="warn">' + ICON.warn + '<span>Sem candles de ' + tf + ' de ' + a.symbol + ' nessa janela (' + NO_5M + ')</span></span></span>' +
      '<span class="d21-l2"><span class="d21-conv">' + CONV[a.cls].replace(/ · /g, ' ·&nbsp;') + '</span> <span class="d21-g">Período efetivo: nenhum candle</span></span>';
  }

  // Linha do tempo por cenário: cada etapa diz o estado de cada ativo.
  // st: queued | collecting | running | done | done_daily | failed ; [estado, detalhe, combinações feitas, extra]
  function timeline(scenario, failSpy) {
    if (scenario === 'past') {
      return [
        { 'BTC/USDT': ['running', '1d'], NVDA: ['queued'], SPY: ['queued'] },
        { 'BTC/USDT': ['running', '4h', 1], NVDA: ['queued'], SPY: ['queued'] },
        { 'BTC/USDT': ['done', null, 2], NVDA: ['collecting', '1d · página 2 de 2'], SPY: ['queued'] },
        { 'BTC/USDT': ['done', null, 2], NVDA: ['running', '1d'], SPY: ['queued'] },
        { 'BTC/USDT': ['done', null, 2], NVDA: ['done_daily', null, 2, 'insufficient4h'], SPY: ['collecting', '1d · página 1 de 2'] },
        { 'BTC/USDT': ['done', null, 2], NVDA: ['done_daily', null, 2, 'insufficient4h'], SPY: ['running', '1d'] },
        { 'BTC/USDT': ['done', null, 2], NVDA: ['done_daily', null, 2, 'insufficient4h'], SPY: ['done_daily', null, 2, 'insufficient4h'] }
      ];
    }
    var steps = [
      { 'BTC/USDT': ['running', '1d'], NVDA: ['queued'], SPY: ['queued'] },
      { 'BTC/USDT': ['done', null, 1], NVDA: ['collecting', '1d · página 3 de 6'], SPY: ['queued'] },
      { 'BTC/USDT': ['done', null, 1], NVDA: ['running', '1d'], SPY: ['queued'] },
      { 'BTC/USDT': ['done', null, 1], NVDA: ['done_daily', null, 1], SPY: ['collecting', '1d · página 2 de 6'] }
    ];
    if (failSpy) {
      steps.push({ 'BTC/USDT': ['done', null, 1], NVDA: ['done_daily', null, 1], SPY: ['collecting', '1d · tentativa 2 de 3 · a Binance não respondeu'] });
      steps.push({ 'BTC/USDT': ['done', null, 1], NVDA: ['done_daily', null, 1], SPY: ['failed', null, 1] });
    } else {
      steps.push({ 'BTC/USDT': ['done', null, 1], NVDA: ['done_daily', null, 1], SPY: ['collecting', '5m do intrabar · página 7 de 16'] });
      steps.push({ 'BTC/USDT': ['done', null, 1], NVDA: ['done_daily', null, 1], SPY: ['running', '1d'] });
      steps.push({ 'BTC/USDT': ['done', null, 1], NVDA: ['done_daily', null, 1], SPY: ['done_daily', null, 1] });
    }
    return steps;
  }

  var state = { scenario: 'mixed', started: false, step: 0, steps: timeline('mixed'), paused: false, cancelled: false, failSpy: false, mode: 'montar', promoted: {}, cls: 'all', assetLimit: ASSET_PAGE };

  // ------------------------------------------------------------------ modos (abas vivas)
  var TAB_ON = ['bg-[rgba(252,213,53,0.12)]', 'text-[var(--accent-primary)]', 'shadow-[inset_0_-2px_0_var(--accent-primary)]'];
  var TAB_OFF = ['bg-[var(--bg-elevated)]', 'text-[var(--text-tertiary)]'];
  function setMode(mode, focus) {
    state.mode = mode;
    $$('[data-d21-panel]').forEach(function (p) { p.hidden = p.getAttribute('data-d21-panel') !== mode; });
    $$('[role="tab"][data-mode-tab]').forEach(function (t) {
      var on = t.getAttribute('data-mode-tab') === mode;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      TAB_ON.forEach(function (c) { t.classList.toggle(c, on); });
      TAB_OFF.forEach(function (c) { t.classList.toggle(c, !on); });
    });
    var target = { acomp: '#progress-heading', decidir: '#leaderboard-title', assets: '#d21-assets-title' }[focus];
    if (target) setTimeout(function () { var h = $(target); if (h) h.focus(); }, 0);
  }
  function enableTabs() {
    var ac = $('#tab-acomp'), de = $('#tab-decidir');
    if (ac) { ac.disabled = false; ac.textContent = 'Acompanhando #' + SWEEP; }
    if (de) de.disabled = false;
  }
  $$('[role="tab"][data-mode-tab]').forEach(function (t) {
    t.addEventListener('click', function () { if (!t.disabled) setMode(t.getAttribute('data-mode-tab')); });
  });
  var tablist = $('[role="tablist"][data-testid="discovery-modes"]');
  if (tablist) tablist.addEventListener('keydown', function (e) {
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    e.preventDefault();
    var tabs = $$('[role="tab"]', tablist).filter(function (t) { return !t.disabled; });
    var i = tabs.indexOf(document.activeElement);
    var next = tabs[(i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length];
    if (next) { setMode(next.getAttribute('data-mode-tab')); next.focus(); }
  });

  // ------------------------------------------------------------------ Montar: cenários do Preflight
  function setText(sel, text) { var el = $(sel); if (el) el.textContent = text; }
  function setHTML(sel, html) { var el = $(sel); if (el) el.innerHTML = html; }
  var TF_ON = ['border-[rgba(252,213,53,0.5)]', 'bg-[rgba(252,213,53,0.1)]', 'text-[var(--accent-primary)]'];
  var TF_OFF = ['border-[var(--border-default)]', 'bg-[var(--bg-secondary)]', 'text-[var(--text-tertiary)]'];
  function setTimeframe(id, on) {
    var label = $('[data-testid="timeframe-' + id + '"]');
    if (!label) return;
    var input = $('input', label), span = $('span', label);
    if (input) input.checked = on;
    TF_ON.forEach(function (c) { span.classList.toggle(c, on); });
    TF_OFF.forEach(function (c) { span.classList.toggle(c, !on); });
  }
  var START_ON = ['border-[var(--accent-primary)]', 'bg-[var(--accent-primary)]', 'text-[#181a20]', 'hover:bg-[var(--accent-primary-hover)]'];
  var START_OFF = ['cursor-not-allowed', 'border-[var(--accent-primary-disabled)]', 'bg-[var(--accent-primary-disabled)]', 'text-[var(--text-muted)]'];
  function setStartEnabled(on) {
    var b = $('[data-testid="start-sweep"]');
    if (!b) return;
    b.disabled = !on;
    START_ON.forEach(function (c) { b.classList.toggle(c, on); });
    START_OFF.forEach(function (c) { b.classList.toggle(c, !on); });
  }

  function applyScenario() {
    var s = state.scenario;
    var period = $('[data-testid="sel-period"]');
    var dates = $('[data-d21="custom-dates"]');
    var limit = $('[data-d21="pf-limit"]');
    var collect = $('[data-d21="pf-collect"]');
    var prec = $('[data-d21="pf-precision"]');
    setTimeframe('4h', s === 'past');
    if (period) period.value = s === 'past' ? 'custom' : 'all';
    if (dates) dates.hidden = s !== 'past';
    if (limit) limit.hidden = s !== 'limit';
    if (collect) collect.hidden = s === 'limit';
    if (prec) prec.hidden = s === 'limit';
    setStartEnabled(s !== 'limit');
    if (s === 'mixed') {
      setText('[data-d21="pf-state"]', 'Pronto para iniciar');
      setText('[data-d21="pf-total"]', '3');
      setHTML('[data-d21="pf-3line"]', '<b>3 combinações</b> · ~6min estimado · Todo o histórico');
      setHTML('[data-d21="pf-run"]', '<b>Vão rodar 3 ativos:</b> 1 cripto (USDT) · 1 ação · 1 ETF (USD). Cada um com a sua fonte, sessão, ajuste e moeda.');
      setHTML('[data-d21="pf-collect"]', '<b>Precisam de coleta de histórico: 1 de 3</b> — SPY (1d e 5m do intrabar). BTC/USDT e NVDA já estão guardados. A coleta acontece no começo do ativo e entra no tempo da varredura.');
      setHTML('[data-d21="pf-precision"] span', '<b>Precisão diária prevista em 1d:</b> NVDA — o 15m dele começa em 2 jan. 2026, então 2 jan. 2003 a 31 dez. 2025 roda no candle diário. SPY: sem histórico guardado; a precisão aparece depois da coleta. O resultado sempre marca o trecho.');
      setText('[data-d21="pf-surv-window"]', ', e a janela começa em 2 jan. 2003');
      setText('[data-d21="pf-formula"]', '1 × 3 × 1 × 1');
      setText('[data-d21="pf-breakdown"]', ' · 0 excluídas · 3 válidas · limite 1000');
      setText('[data-d21="pf-estimate"]', '~6min');
      setText('[data-d21="pf-start"]', 'Iniciar varredura — 3, ~6min');
      setText('[data-testid="pf-period"]', 'Todo o histórico');
      setText('[data-testid="asset-count"]', '3 selecionados · 1 cripto · 1 ação · 1 ETF');
    } else if (s === 'past') {
      setText('[data-d21="pf-state"]', 'Pronto para iniciar');
      setText('[data-d21="pf-total"]', '6');
      setHTML('[data-d21="pf-3line"]', '<b>6 combinações</b> · ~12min estimado · Personalizado [1 jan. 2019, 31 dez. 2020)');
      setHTML('[data-d21="pf-run"]', '<b>Vão rodar 3 ativos em 1d e 4h:</b> 1 cripto (USDT) · 1 ação · 1 ETF (USD). Cada um com a sua fonte, sessão, ajuste e moeda.');
      setHTML('[data-d21="pf-collect"]', '<b>Precisam de coleta de histórico: 1 de 3</b> — SPY (1d). BTC/USDT e NVDA já estão guardados. O 5m de NVDA e SPY não entra: a Binance não tem 5m nessa janela.');
      setHTML('[data-d21="pf-precision"] span', '<b>Sem candles prováveis em 4h: NVDA e SPY</b> — ' + NO_5M + ', então essas 2 combinações devem terminar como amostra insuficiente, sem resultado. Em 1d, NVDA e SPY rodam em precisão diária na janela inteira.');
      setText('[data-d21="pf-surv-window"]', ', e a janela é 1 jan. 2019 – 31 dez. 2020');
      setText('[data-d21="pf-formula"]', '1 × 3 × 2 × 1');
      setText('[data-d21="pf-breakdown"]', ' · 0 excluídas · 6 válidas · limite 1000');
      setText('[data-d21="pf-estimate"]', '~12min');
      setText('[data-d21="pf-start"]', 'Iniciar varredura — 6, ~12min');
      setText('[data-testid="pf-period"]', '1 jan. 2019 – 31 dez. 2020');
      setText('[data-testid="asset-count"]', '3 selecionados · 1 cripto · 1 ação · 1 ETF');
    } else {
      setText('[data-d21="pf-state"]', 'Bloqueado — veja o que falta');
      setText('[data-d21="pf-total"]', '2.433');
      setHTML('[data-d21="pf-3line"]', '<b>2.433 combinações</b> · acima do limite de 1.000 · Todo o histórico');
      setHTML('[data-d21="pf-run"]', '<b>2.433 ativos selecionados:</b> 1 cripto (USDT) · 2.431 ações · 1 ETF (USD).');
      setText('[data-d21="pf-surv-window"]', ', e a janela começa em 2 jan. 2003');
      setText('[data-d21="pf-formula"]', '1 × 2.433 × 1 × 1');
      setText('[data-d21="pf-breakdown"]', ' · 0 excluídas · 2.433 válidas · limite 1000');
      setText('[data-d21="pf-estimate"]', '~81h');
      setText('[data-d21="pf-start"]', 'Iniciar varredura — 2.433, ~81h');
      setText('[data-testid="pf-period"]', 'Todo o histórico');
      setText('[data-testid="asset-count"]', '2.433 selecionados · 1 cripto · 2.431 ações · 1 ETF');
    }
  }

  // ------------------------------------------------------------------ Acompanhando: progresso e por ativo
  function combosOf() { return state.scenario === 'past' ? 2 : 1; }
  function totalCombos() { return ASSETS.length * combosOf(); }
  function stepState() { return state.steps[Math.min(state.step, state.steps.length - 1)]; }
  function isTerminal() { return state.cancelled || state.step >= state.steps.length - 1; }
  function inFlight(s) { return s === 'queued' || s === 'collecting' || s === 'running'; }

  // Desfechos por ativo: contagem de cada um (decisão 7: desfecho misto mostra as duas contagens).
  function outcomes(x) {
    var s = x[0], done = x[2] || 0;
    if (s === 'failed') return { failed: combosOf(), ok: 0, insufficient: 0 };
    if (x[3] === 'insufficient4h') return { failed: 0, ok: done - 1, insufficient: 1 };
    return { failed: 0, ok: done, insufficient: 0 };
  }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }

  function assetLine(a, st) {
    var s = st[0], detail = st[1], done = st[2] || 0, extra = st[3];
    var per = combosOf();
    var countText = done + ' de ' + per + (per === 1 ? ' combinação' : ' combinações');
    var label, icon, det = '', key = s;
    var past = state.scenario === 'past';
    var r = rowInfo(a.symbol, past);
    if (state.cancelled && inFlight(s)) { s = 'not_run'; key = 'queued'; }
    if (state.paused && (s === 'collecting' || s === 'running')) { key = 'paused'; }
    switch (s) {
      case 'queued': label = 'Na fila'; icon = ICON.clock; break;
      case 'collecting': label = 'Coletando histórico · ' + detail; icon = ICON.load; break;
      case 'running': label = 'Rodando · ' + detail; icon = ICON.load; break;
      case 'done': label = 'Concluído'; icon = ICON.ok; det = r.prec + ' · período efetivo ' + r.eff; break;
      case 'done_daily': label = 'Concluído · precisão diária'; icon = ICON.warn;
        det = r.prec.replace('Precisão diária · s', 'S') + ' · período efetivo ' + r.eff; break;
      case 'failed': label = 'Falha: a Binance não respondeu ao histórico de ' + a.symbol + ' nas 3 tentativas'; icon = ICON.fail; det = 'Nenhum resultado; a combinação não entra no ranking nem vira amostra suficiente.'; break;
      case 'not_run': label = 'Não rodou · varredura cancelada'; icon = ICON.clock; det = 'Combinações pendentes viraram ignoradas; os resultados concluídos ficam.'; break;
    }
    if (state.paused && key === 'paused') label = (s === 'collecting' ? 'Pausado na coleta · ' : 'Pausado · ') + detail + ' · retoma daqui';
    if (extra === 'insufficient4h') {
      var o = outcomes(st);
      label = plural(o.ok, 'concluída', 'concluídas') + ' · ' + plural(o.insufficient, 'amostra insuficiente', 'amostras insuficientes');
      key = 'insufficient'; icon = ICON.warn;
      det = '1d: ' + r.prec + ' · período efetivo ' + r.eff + ' · 4h: Amostra insuficiente — sem candles de 4h de ' + a.symbol + ' nessa janela (' + NO_5M + ')';
    }
    return '<li data-asset="' + a.symbol + '"><span class="d21-asset"><b>' + a.symbol + '</b><span class="d21-g">' + chipHTML(a.cls) + '</span></span>' +
      '<span class="d21-count"><span class="sr-only">Combinações: </span>' + countText + '</span>' +
      '<span class="d21-state" data-state="' + key + '">' + icon + '<span><span class="sr-only">Estado: </span>' + label + '</span></span>' +
      '<span class="d21-detail">' + (det ? '<span class="sr-only">Detalhe: </span>' + det : '') + '</span></li>';
  }

  // Ordem do quadro (decisão 7): ativo em curso, falhas e amostras insuficientes no topo; o resto na ordem da varredura.
  function assetPriority(x) {
    var s = x[0];
    if (!state.cancelled && (s === 'collecting' || s === 'running')) return 0;
    if (s === 'failed') return 1;
    if (x[3] === 'insufficient4h') return 2;
    return 3;
  }

  function counts() {
    var st = stepState(), c = { succeeded: 0, failed: 0, skipped: 0, insufficient: 0 };
    ASSETS.forEach(function (a) {
      var x = st[a.symbol], o = outcomes(x);
      c.succeeded += o.ok; c.failed += o.failed; c.insufficient += o.insufficient;
      if (state.cancelled && inFlight(x[0])) c.skipped += combosOf() - (x[2] || 0);
    });
    c.processed = c.succeeded + c.failed + c.skipped + c.insufficient;
    return c;
  }

  function renderAssets() {
    var list = $('#d21-asset-list');
    if (!list) return;
    var st = stepState();
    var ordered = ASSETS.map(function (a, i) { return { a: a, i: i, p: assetPriority(st[a.symbol]) }; })
      .sort(function (x, y) { return x.p - y.p || x.i - y.i; });
    var shown = ordered.slice(0, state.assetLimit);
    list.innerHTML = shown.map(function (o) { return assetLine(o.a, st[o.a.symbol]); }).join('');
    var more = $('[data-d21="assets-more"]');
    var rest = ordered.length - shown.length;
    if (more) {
      more.hidden = rest <= 0;
      var btn = $('#d21-more', more);
      if (btn) btn.textContent = 'Mostrar mais ' + Math.min(ASSET_PAGE, rest);
      setText('[data-d21="assets-more-count"]', 'Mostrando ' + shown.length + ' de ' + ordered.length + ' ativos');
    }
  }
  var moreBtn = $('#d21-more');
  if (moreBtn) moreBtn.addEventListener('click', function () { state.assetLimit += ASSET_PAGE; renderAssets(); moreBtn.focus(); });

  function renderAcomp(announce) {
    if (!$('#d21-asset-list')) return;
    var st = stepState();
    renderAssets();
    var c = counts(), total = totalCombos();
    var terminal = isTerminal();
    setText('[data-testid="progress-count"]', c.processed + ' de ' + total);
    var bar = $('[role="progressbar"][aria-label="Progresso da varredura ativa"]');
    if (bar) { bar.setAttribute('aria-valuemax', String(total)); bar.setAttribute('aria-valuenow', String(c.processed)); }
    var fill = $('.progress-fill');
    if (fill) fill.style.width = Math.round((c.processed / total) * 100) + '%';
    setText('[data-testid="counter-invariant"]', c.processed + ' processadas = ' + c.succeeded + ' sucesso + ' + c.failed + ' falha + ' + c.skipped + ' ignoradas + ' + c.insufficient + ' amostra insuficiente');
    var heading = state.cancelled ? 'Varredura cancelada' : terminal ? (c.failed ? 'Varredura concluída com falhas' : 'Varredura concluída') : state.paused ? 'Varredura pausada' : 'Varredura em execução';
    setText('#progress-heading', heading);
    setText('[data-testid="active-state-chip"]', state.cancelled ? 'CANCELLED' : terminal ? (c.failed ? 'PARTIAL_FAILURE' : 'COMPLETED') : state.paused ? 'PAUSED' : 'EM CURSO');
    var dot = $('.status-dot');
    if (dot) { dot.classList.toggle('paused', state.paused && !terminal); dot.classList.toggle('cancelled', terminal); }
    var pause = $('[data-testid="pause-sweep"]'), cancel = $('[data-testid="cancel-sweep"]');
    if (pause) {
      pause.hidden = terminal; pause.innerHTML = (state.paused ? ICON.play : ICON.pause) + (state.paused ? 'Retomar' : 'Pausar');
      ['border-[rgba(252,213,53,0.45)]', 'bg-[rgba(252,213,53,0.08)]', 'text-[var(--accent-primary)]'].forEach(function (k) { pause.classList.toggle(k, state.paused); });
      ['border-[rgba(245,158,11,0.42)]', 'bg-[rgba(245,158,11,0.08)]', 'text-[#fbbf24]'].forEach(function (k) { pause.classList.toggle(k, !state.paused); });
    }
    if (cancel) cancel.hidden = terminal;
    // Parciais: só os ativos com resultado (amostra insuficiente e falha não entram)
    $$('[data-testid="partials-table"] tbody tr.result-row').forEach(function (tr) {
      var a = rowAsset(tr);
      var x = a && st[a.symbol];
      tr.hidden = !(x && (x[0] === 'done' || x[0] === 'done_daily'));
    });
    if (announce) {
      var live = $('#d21-live');
      var cur = ASSETS.filter(function (a) { var s = st[a.symbol][0]; return s === 'collecting' || s === 'running'; })[0];
      if (live) live.textContent = terminal ? heading + '.' : state.paused ? 'Varredura pausada.' : cur ? cur.symbol + ': ' + (st[cur.symbol][0] === 'collecting' ? 'coletando histórico · ' : 'rodando · ') + st[cur.symbol][1] : '';
    }
    renderDecidir();
    if (terminal && announce && state.mode === 'acomp') setTimeout(function () { setMode('decidir', 'decidir'); }, 400);
  }

  // O ativo de cada linha vem do bloco DELTA (data-asset), não do id do resultado.
  function rowAsset(tr) {
    var rd = $('.d21-rowdata[data-asset]', tr);
    return rd ? assetBy(rd.getAttribute('data-asset')) : null;
  }

  var pauseBtn = $('[data-testid="pause-sweep"]');
  if (pauseBtn) pauseBtn.addEventListener('click', function () { state.paused = !state.paused; renderAcomp(true); pauseBtn.focus(); });
  var cancelBtn = $('[data-testid="cancel-sweep"]');
  var confirmBox = null;
  if (cancelBtn) cancelBtn.addEventListener('click', function () {
    if (confirmBox) return;
    cancelBtn.setAttribute('aria-expanded', 'true');
    confirmBox = document.createElement('div');
    confirmBox.className = 'mt-3 flex items-center justify-between gap-3.5 rounded-lg border border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.06)] p-3';
    confirmBox.setAttribute('role', 'alertdialog'); confirmBox.setAttribute('aria-modal', 'false'); confirmBox.setAttribute('aria-labelledby', 'cancel-title');
    confirmBox.innerHTML = '<p id="cancel-title" class="text-xs text-[var(--text-secondary)]">Cancelar após as leases ativas? Resultados concluídos ficam; pendentes viram ignorados.</p><div class="flex shrink-0 gap-2"><button type="button" data-d21="keep" class="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 text-xs font-semibold text-[var(--text-secondary)]">Continuar</button><button type="button" data-testid="confirm-cancel" class="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 text-xs font-semibold text-[var(--text-secondary)]">Confirmar cancelamento</button></div>';
    var host = $('[data-testid="counter-invariant"]').parentNode.parentNode;
    host.appendChild(confirmBox);
    $('[data-d21="keep"]', confirmBox).addEventListener('click', function () { closeConfirm(true); });
    $('[data-testid="confirm-cancel"]', confirmBox).addEventListener('click', function () {
      closeConfirm(false);
      state.cancelled = true;
      renderAcomp(true);
      // Cancelar some com a varredura terminada: o foco vai ao título do progresso (não cai no body).
      var h = $('#progress-heading'); if (h) h.focus();
    });
    $('[data-testid="confirm-cancel"]', confirmBox).focus();
  });
  function closeConfirm(refocus) {
    if (confirmBox) { confirmBox.remove(); confirmBox = null; }
    if (cancelBtn) { cancelBtn.setAttribute('aria-expanded', 'false'); if (refocus) cancelBtn.focus(); }
  }

  // ------------------------------------------------------------------ Decidir: linhas, filtro Classe, sem resultado
  function decidirTable() { return $('[data-testid="decidir-table"]'); }
  var PRISTINE = {};
  (function () {
    var t = decidirTable();
    if (!t) return;
    ASSETS.forEach(function (a) {
      var b = $('[data-testid="promote-' + a.rid + '"]', t);
      if (b) PRISTINE[a.symbol] = b.closest('tr').cloneNode(true);
    });
  })();
  function retarget(tr, oldRid, newRid) {
    $$('[data-testid]', tr).forEach(function (n) { n.setAttribute('data-testid', n.getAttribute('data-testid').replace(oldRid, newRid)); });
    $$('[aria-label]', tr).forEach(function (n) { n.setAttribute('aria-label', n.getAttribute('aria-label').replace(oldRid, newRid)); });
    var meta = $('.candidate-meta', tr);
    if (meta && meta.firstChild && meta.firstChild.nodeType === 3) meta.firstChild.nodeValue = meta.firstChild.nodeValue.replace(oldRid, newRid);
    tr.setAttribute('data-d21-rid', newRid);
    tr.setAttribute('data-d21-generated', '');
  }
  // Período passado: BTC/USDT 4h tem resultado (NO-GO), então entra no ranking e as contagens batem (6 = 4 + 2).
  var BTC4H = 'RS-BTC1121G7';
  function btc4hRow() {
    var tr = PRISTINE['BTC/USDT'].cloneNode(true);
    retarget(tr, 'RS-BTC1121A1', BTC4H);
    $('.rank-cell-value', tr).textContent = '4';
    tr.setAttribute('data-verdict', 'NO-GO');
    var seal = $('.verdict', tr); if (seal) { seal.className = 'verdict verdict-nogo'; seal.setAttribute('data-testid', 'seal-nogo'); seal.textContent = 'NO-GO'; }
    var cells = $$('td.number', tr);
    var vals = ['0,58', null, '44%', '+86%', '−24%', '0,41', '9,8%'];
    cells.forEach(function (td, i) {
      if (i === 1) { if (td.firstChild && td.firstChild.nodeType === 3) td.firstChild.nodeValue = '52'; return; }
      if (vals[i] !== undefined && vals[i] !== null) td.textContent = vals[i];
    });
    var rd = $('.d21-rowdata', tr); rd.setAttribute('data-tf', '4h');
    return tr;
  }
  var INSUFF_ID = { 'RS-NVDA1121B2': 'RS-NVDA1121E5', 'RS-SPY1121C3': 'RS-SPY1121F6' };
  function insufficientRow(a) {
    var tr = PRISTINE[a.symbol].cloneNode(true);
    var nid = INSUFF_ID[a.rid];
    retarget(tr, a.rid, nid);
    tr.setAttribute('data-eligibility', 'insufficient_sample');
    tr.removeAttribute('data-verdict');
    tr.setAttribute('data-testid', 'row-insufficient');
    $('.rank-cell-value', tr).textContent = '—';
    var meta = $('.candidate-meta', tr);
    meta.textContent = nid + ' · cobertura N/A · fast 21 · slow 89';
    var rd = $('.d21-rowdata', tr);
    rd.setAttribute('data-tf', '4h'); rd.setAttribute('data-insufficient', '');
    rd.innerHTML = insufficientHTML(a, '4h');
    var seal = $('.verdict', tr); if (seal) seal.outerHTML = '<span class="sample-badge" data-testid="seal-insufficient">Amostra insuficiente</span>';
    $$('td.number', tr).forEach(function (td) { td.textContent = 'N/A'; td.className = 'number na'; });
    var prom = $('[data-testid^="promote-"]', tr); if (prom) prom.remove();
    var exp = $('[data-testid^="expand-"]', tr); if (exp) exp.remove();
    return tr;
  }
  function ensureRow(tbody, rid, make) {
    if ($('tr[data-d21-rid="' + rid + '"]', tbody)) return;
    tbody.appendChild(make());
  }

  function namesList(list) { return list.length < 2 ? list.join('') : list.slice(0, -1).join(', ') + ' e ' + list[list.length - 1]; }

  function renderDecidir() {
    var table = decidirTable();
    if (!table) return;
    var st = stepState();
    var past = state.scenario === 'past';
    var terminal = isTerminal();
    var tbody = $('tbody', table);
    if (!past) {
      $$('tr[data-d21-generated]', table).forEach(function (tr) { tr.remove(); });
    } else {
      if ((st['BTC/USDT'][2] || 0) >= 2) ensureRow(tbody, BTC4H, btc4hRow);
      ASSETS.forEach(function (a) { if (a.cls !== 'crypto' && st[a.symbol][3] === 'insufficient4h') ensureRow(tbody, INSUFF_ID[a.rid], function () { return insufficientRow(a); }); });
    }
    // bloco do candidato (Decidir e Parciais) segue o cenário
    $$('.d21-rowdata[data-tf]:not([data-insufficient])').forEach(function (el) {
      el.innerHTML = rowHTML(el.getAttribute('data-asset'), el.getAttribute('data-tf'), el.getAttribute('data-sym') !== '0', past);
    });
    var empty = $('tr[data-d21-empty]', tbody); if (empty) empty.remove();
    var rows = $$('tbody tr.result-row', table), shown = 0, available = 0;
    var cc = { crypto: 0, stock: 0, etf: 0 };
    rows.forEach(function (tr) {
      var a = rowAsset(tr);
      var x = a && st[a.symbol];
      var exists = tr.hasAttribute('data-d21-generated') || (x && (x[0] === 'done' || x[0] === 'done_daily'));
      if (exists) { available += 1; cc[a.cls] += 1; }
      var match = state.cls === 'all' || (a && a.cls === state.cls);
      tr.hidden = !(exists && match);
      if (!tr.hidden) shown += 1;
    });
    var sel = $('#d21-class-filter');
    if (sel) {
      sel.options[0].textContent = 'Todas (' + available + ')';
      [['crypto', 1, 'Cripto'], ['stock', 2, 'Ações'], ['etf', 3, 'ETFs']].forEach(function (o) {
        var opt = sel.options[o[1]];
        opt.textContent = o[2] + ' (' + cc[o[0]] + ')';
        // Opção com 0 fica desabilitada (spec "Class filter in Decidir"), salvo se já estiver escolhida.
        opt.disabled = cc[o[0]] === 0 && sel.value !== o[0];
      });
    }
    if (shown === 0 && state.cls !== 'all') {
      var cols = $$('thead th', table).length || 11;
      var tr = document.createElement('tr');
      tr.setAttribute('data-d21-empty', ''); tr.className = 'd21-empty';
      tr.innerHTML = '<td colspan="' + cols + '">Nenhum candidato de ' + CLS_PLURAL[state.cls] + ' nesta varredura. <button type="button" class="d21-linkbtn" data-d21="empty-clear">Limpar filtros</button></td>';
      tbody.appendChild(tr);
    }
    setText('[data-testid="result-count"]', shown + ' de ' + available + ' candidatos · página 1 de 1');
    // Cabeçalho segue o estado real da varredura (STATE_LABEL vivo), nunca "em execução" depois do fim.
    var failedAny = ASSETS.some(function (a) { return st[a.symbol][0] === 'failed'; });
    setText('[data-d21="lb-state"]', state.cancelled ? 'cancelada' : terminal ? (failedAny ? 'falha parcial' : 'concluída') : state.paused ? 'pausada' : 'em execução');
    // Nota "Sem resultado": falha, não rodou e amostra insuficiente não somem do Decidir.
    var failed = ASSETS.filter(function (a) { return st[a.symbol][0] === 'failed'; }).map(function (a) { return a.symbol; });
    var notRun = state.cancelled ? ASSETS.filter(function (a) { return inFlight(st[a.symbol][0]); }).map(function (a) { return a.symbol; }) : [];
    var insuff = ASSETS.filter(function (a) { return st[a.symbol][3] === 'insufficient4h'; }).map(function (a) { return a.symbol + ' 4h'; });
    var parts = [], kind = '';
    if (failed.length) { parts.push('<b>Sem resultado:</b> ' + namesList(failed) + ' — Falha: a Binance não respondeu ao histórico nas 3 tentativas.'); kind = 'failed'; }
    if (notRun.length) { parts.push('<b>Sem resultado:</b> ' + namesList(notRun) + ' — Não rodou · varredura cancelada.'); kind = kind || 'cancelled'; }
    if (insuff.length) { parts.push('<b>Amostra insuficiente:</b> ' + namesList(insuff) + ' — sem candles nessa janela; as linhas ficam sem rank e sem Promover.'); kind = kind || 'insufficient'; }
    var note = $('[data-testid="no-result-decidir"]');
    if (note) {
      note.hidden = !(terminal && parts.length);
      note.setAttribute('data-kind', kind);
      setHTML('[data-d21="no-result-text"]', parts.join(' '));
      setHTML('[data-d21="no-result-icon"]', kind === 'failed' ? ICON.fail : kind === 'cancelled' ? ICON.clock : ICON.warn);
    }
    var surv = $('[data-testid="survivorship-decidir"] > span');
    if (surv) surv.innerHTML = '<b>Viés de sobrevivência:</b> esta varredura usou só os ativos do catálogo de hoje (janela ' + (past ? '1 jan. 2019 – 31 dez. 2020' : 'desde 2 jan. 2003') + '). Ativos que saíram da Binance antes de hoje não estão no ranking.';
  }
  var classSel = $('#d21-class-filter');
  function clearFilters() { state.cls = 'all'; if (classSel) classSel.value = 'all'; renderDecidir(); }
  if (classSel) classSel.addEventListener('change', function () { state.cls = classSel.value; renderDecidir(); });
  var clear = $('[data-testid="clear-filters"]');
  if (clear) clear.addEventListener('click', clearFilters);
  document.addEventListener('click', function (e) {
    if (!e.target.closest) return;
    if (e.target.closest('[data-d21="empty-clear"]')) { clearFilters(); if (classSel) classSel.focus(); }
    if (e.target.closest('[data-d21="see-assets"]')) setMode('acomp', 'assets');
  });

  // ------------------------------------------------------------------ Promover: modal vivo + identidade da execução
  var modalWrap = $('[data-d21-modal]');
  var dialog = $('#promotion-modal');
  var trigger = null, target = null;
  var DATA = {
    'RS-BTC1121A1': { cagr: '45%', dd: '−21%', trades: '48', cov: '97% · 17 de ago. de 2017 – 25 de out. de 2026', past: '97% · 1 de jan. de 2019 – 31 de dez. de 2020', sample: '3f9a0c21' },
    'RS-BTC1121G7': { cagr: '9,8%', dd: '−24%', trades: '52', cov: '97% · 1 de jan. de 2019 – 31 de dez. de 2020', past: '97% · 1 de jan. de 2019 – 31 de dez. de 2020', sample: '5d2e8b40' },
    'RS-NVDA1121B2': { cagr: '18,3%', dd: '−17%', trades: '61', cov: '100% · 2 de jan. de 2003 – 23 de out. de 2026', past: '100% · 2 de jan. de 2019 – 31 de dez. de 2020', sample: '8b41d7e2' },
    'RS-SPY1121C3': { cagr: '4,6%', dd: '−14%', trades: '37', cov: '100% · 2 de jan. de 2003 – 23 de out. de 2026', past: '100% · 2 de jan. de 2019 – 31 de dez. de 2020', sample: 'c07e5a19' }
  };
  function openModal(btn) {
    var rid = btn.getAttribute('data-testid').replace('promote-', '');
    var tr = btn.closest('tr');
    var rd = tr && $('.d21-rowdata[data-asset]', tr);
    var a = rd && assetBy(rd.getAttribute('data-asset'));
    var d = DATA[rid];
    if (!a || !d || !modalWrap) return;
    var tf = rd.getAttribute('data-tf') || '1d';
    trigger = btn; target = { a: a, rid: rid };
    var equity = a.cls !== 'crypto';
    var past = state.scenario === 'past';
    var r = rowInfo(a.symbol, past);
    setText('#modal-title', equity ? 'Promover a favorito' : 'Promover a favorito tier 3');
    setText('[data-testid="modal-candidate"]', rid + ' · multi_ma_crossover');
    setText('[data-testid="modal-market"]', a.symbol + ' · ' + tf + ' · Long');
    setText('[data-testid="modal-risk-cagr"]', d.cagr);
    setText('[data-testid="modal-risk-dd"]', d.dd);
    setText('[data-testid="modal-risk-trades"]', d.trades);
    setText('[data-testid="modal-risk-cov"]', past ? d.past : d.cov);
    setText('[data-testid="modal-result"]', rid);
    // No modal a identidade vem por extenso (trecho exato da precisão).
    setHTML('[data-d21="modal-id"]', '<span class="d21-symline">' + chipHTML(a.cls) + '</span>' +
      '<span class="d21-prec" data-tone="' + r.tone + '">' + (r.tone === 'warn' ? ICON.warn : ICON.info) + '<span>' + r.prec + '</span></span>' +
      '<span class="d21-conv">' + CONV[a.cls] + '</span><span class="d21-conv">Período efetivo ' + r.eff + '</span>' +
      '<span class="d21-conv">Amostra ' + d.sample + ' · guardada enquanto o favorito existir · Direção Long</span>');
    var liveDest = $('[data-d21="dest-equity"]') && $('[data-d21="dest-equity"]').previousElementSibling;
    if (liveDest) liveDest.hidden = equity;
    var eqDest = $('[data-d21="dest-equity"]'); if (eqDest) eqDest.hidden = !equity;
    var confirm = $('[data-testid="confirm-promotion"]');
    if (confirm) {
      var svg = $('svg', confirm);
      confirm.textContent = '';
      if (svg) confirm.appendChild(svg);
      confirm.appendChild(document.createTextNode(equity ? 'Promover a favorito' : 'Promover como tier 3'));
    }
    $$('[aria-controls="promotion-modal"]').forEach(function (b) { b.setAttribute('aria-expanded', b === btn ? 'true' : 'false'); });
    modalWrap.hidden = false;
    setTimeout(function () { if (confirm) confirm.focus(); }, 0);
  }
  function closeModal() {
    if (!modalWrap || modalWrap.hidden) return;
    modalWrap.hidden = true;
    $$('[aria-controls="promotion-modal"]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    if (trigger && document.body.contains(trigger)) trigger.focus();
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('[data-testid^="promote-RS-"]');
    if (btn && !btn.disabled) { openModal(btn); return; }
    if (modalWrap && !modalWrap.hidden) {
      if (e.target.closest('[data-testid="close-modal"]')) closeModal();
      else if (e.target === modalWrap.firstElementChild) closeModal();
      else if (e.target.closest('#promotion-modal button') && e.target.closest('button').textContent.trim() === 'Voltar') closeModal();
    }
  });
  document.addEventListener('keydown', function (e) {
    if (!modalWrap || modalWrap.hidden) return;
    if (e.key === 'Escape') { e.preventDefault(); closeModal(); return; }
    if (e.key === 'Tab') {
      var f = $$('button, a[href], select, input', dialog).filter(function (n) { return !n.disabled && n.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  var confirmBtn = $('[data-testid="confirm-promotion"]');
  if (confirmBtn) confirmBtn.addEventListener('click', function () {
    if (!target) return;
    var a = target.a, rid = target.rid, equity = a.cls !== 'crypto';
    state.promoted[rid] = true;
    modalWrap.hidden = true;
    $$('[data-testid="promote-' + rid + '"]').forEach(function (b) {
      var cell = b.closest('td.action-cell');
      var html = '<span class="promoted-state" tabindex="-1" data-promoted-result="' + rid + '">' + ICON.check + (equity ? 'Favorito · sem estrela' : 'Favorito tier 3') + '</span>';
      if (equity) html = '<span class="d21-promoted">' + html + '<a href="/favorites" data-testid="see-favorite-' + rid + '">Ver em Favoritos</a></span>';
      cell.innerHTML = html;
    });
    var focusEl = $('.action-cell [data-promoted-result="' + rid + '"]', decidirTable()) || $('[data-promoted-result="' + rid + '"]');
    if (focusEl) focusEl.focus();
    toast('Candidato promovido.', equity ? a.symbol + ' entrou em Favoritos sem nível de estrela, com classe, moeda, precisão, convenções, janela e amostra desta execução.' : a.symbol + ' entrou em Favoritos como tier 3.');
  });
  function toast(title, copy) {
    var old = $('[data-d21-toast]'); if (old) old.remove();
    var t = document.createElement('div');
    t.setAttribute('data-d21-toast', '');
    t.setAttribute('role', 'status');
    t.className = 'fixed bottom-6 right-6 z-[70] flex max-w-[min(420px,calc(100vw-32px))] items-start gap-2.5 rounded-lg border border-[rgba(252,213,53,0.35)] bg-[var(--bg-elevated)] px-3.5 py-3 text-sm text-[var(--text-secondary)] shadow-2xl';
    t.innerHTML = ICON.check.replace('h-3.5 w-3.5', 'mt-0.5 h-4 w-4 shrink-0 text-[var(--accent-primary)]') + '<div><strong class="block">' + title + '</strong><div class="text-xs text-[var(--text-tertiary)]">' + copy + '</div></div>';
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 6000);
  }

  // ------------------------------------------------------------------ Iniciar e demonstração
  var start = $('[data-testid="start-sweep"]');
  if (start) start.addEventListener('click', function () {
    if (start.disabled) return;
    state.started = true; state.step = 0; state.paused = false; state.cancelled = false; state.assetLimit = ASSET_PAGE;
    enableTabs();
    setMode('acomp', 'acomp');
    renderAcomp(true);
  });
  function reset(scenario) {
    state.scenario = scenario; state.started = false; state.step = 0; state.paused = false; state.cancelled = false; state.failSpy = false; state.cls = 'all'; state.assetLimit = ASSET_PAGE;
    state.steps = timeline(scenario, false);
    if (classSel) classSel.value = 'all';
    var ac = $('#tab-acomp'), de = $('#tab-decidir');
    if (ac) { ac.disabled = true; ac.textContent = 'Acompanhando #—'; }
    if (de) de.disabled = true;
    $$('tr[data-d21-generated]').forEach(function (tr) { tr.remove(); });
    applyScenario();
    renderAcomp(false);
    setMode('montar');
  }
  $$('[data-demo="scenario"]').forEach(function (b) {
    b.addEventListener('click', function () {
      $$('[data-demo="scenario"]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      reset(b.getAttribute('data-value'));
    });
  });
  var adv = $('#demo-advance');
  if (adv) adv.addEventListener('click', function () {
    if (state.scenario === 'limit') return;
    if (!state.started) { start.click(); return; }
    if (state.paused || state.cancelled) return;
    if (state.step < state.steps.length - 1) state.step += 1;
    if (state.mode !== 'acomp') setMode('acomp');
    renderAcomp(true);
  });
  var fail = $('#demo-fail');
  if (fail) fail.addEventListener('click', function () {
    if (state.scenario !== 'mixed') { $$('[data-demo="scenario"]')[0].click(); }
    state.failSpy = true; state.steps = timeline('mixed', true);
    if (!state.started) { start.click(); }
    state.step = 3;
    setMode('acomp');
    renderAcomp(true);
  });

  applyScenario();
  renderAcomp(false);
})();
