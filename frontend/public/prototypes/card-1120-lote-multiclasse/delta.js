/* Card #1120 — DELTA do protótipo: lote multiclasse no Combo e na Otimização, lista única em Favoritos.
   Nada aqui vai para o produto além do comportamento descrito no design.md; números, datas e ids são amostra.
   Rework r1 (24/10/2026): lote pausado bloqueia lote novo, fora por cobertura na Otimização, contagem de coleta pelo que falta guardar. */
(function () {
  'use strict';
  var page = document.body.getAttribute('data-page');
  var LOTE = '7f3c2a91';

  var ICON = {
    ok: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="m9 12 2 2 4-4"></path></svg>',
    warn: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>',
    fail: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="m15 9-6 6"></path><path d="m9 9 6 6"></path></svg>',
    ban: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="m4.9 4.9 14.2 14.2"></path></svg>',
    skip: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 17 5-5-5-5"></path><path d="m13 17 5-5-5-5"></path></svg>',
    out: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 12h8"></path></svg>',
    load: '<svg class="b20-spin" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.22-8.56"></path></svg>',
    wait: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>',
    stop: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="5" width="14" height="14" rx="2"></rect></svg>',
    pause: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16" rx="1"></rect><rect x="14" y="4" width="4" height="16" rx="1"></rect></svg>',
    play: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4l14 8-14 8z"></path></svg>'
  };

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function fmt(n) { return Number(n).toLocaleString('pt-BR'); }
  var CLASS_LABEL = { crypto: 'Cripto', stock: 'Ação', etf: 'ETF' };
  function cls(c) { return '<span class="b20-cls" data-class="' + c + '">' + CLASS_LABEL[c] + '</span>'; }

  function press(group, btn) {
    $$('[data-demo="' + group + '"]').forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
  }

  /* ======================================================================================
     Favoritos (index.html): filtro Classe, faixa do lote, ordenação, lista e cartões.
     ====================================================================================== */
  if (page === 'favorites') {
    var classSel = $('#b20-class');
    var sortSel = $('#b20-sort');
    var lote = new URLSearchParams(location.search).get('lote');
    var banner = $('#b20-lote');

    function rowsOf(kind) { return $$(kind === 'card' ? '[data-b20-card]' : '[data-b20-row]'); }
    function key(el, by) {
      var r = parseFloat(el.getAttribute('data-ret')), t = parseFloat(el.getAttribute('data-trades')), s = parseFloat(el.getAttribute('data-sharpe'));
      if (by === 'return') return r; if (by === 'sharpe') return s; if (by === 'trades') return t; return r / Math.max(1, t);
    }
    function apply() {
      var c = classSel.value, by = sortSel.value, shown = 0;
      ['row', 'card'].forEach(function (kind) {
        var list = rowsOf(kind);
        if (!list.length) return;
        var parent = list[0].parentNode;
        list.sort(function (a, b) { return key(b, by) - key(a, by); });
        var anchor = parent.querySelector(kind === 'card' ? '.b20-empty-card' : '.b20-empty-row');
        var n = 0;
        list.forEach(function (el) {
          var ok = (c === 'all' || el.getAttribute('data-class') === c) && (!lote || el.getAttribute('data-lote') === lote);
          el.hidden = !ok;
          if (ok) n += 1;
          parent.insertBefore(el, anchor);
        });
        if (anchor) anchor.hidden = n !== 0;
        shown = n;
      });
      $$('[data-b20-count]').forEach(function (el) { el.textContent = shown + ' filtradas'; });
      $$('[data-b20-footer]').forEach(function (el) { el.textContent = shown + (shown === 1 ? ' estratégia carregada' : ' estratégias carregadas'); });
    }
    if (lote && banner) {
      banner.hidden = false;
      $('#b20-lote-id').textContent = lote;
    }
    $('#b20-lote-clear') && $('#b20-lote-clear').addEventListener('click', function () {
      lote = null; banner.hidden = true; history.replaceState(null, '', location.pathname); apply();
      classSel.focus();
    });
    // Estrelas, Telegram e Revalidar de ação/ETF: aria-disabled (focáveis, com o motivo em aria-describedby); o clique não faz nada.
    document.addEventListener('click', function (e) {
      var off = e.target.closest && e.target.closest('[data-b20-off]');
      if (off) { e.preventDefault(); e.stopPropagation(); }
    }, true);
    classSel.addEventListener('change', apply);
    sortSel.addEventListener('change', apply);
    $$('[data-demo="fav"]').forEach(function (b) {
      b.addEventListener('click', function () {
        var v = b.getAttribute('data-value');
        press('fav', b);
        if (v === 'lote') { lote = LOTE; history.replaceState(null, '', '?lote=' + LOTE); banner.hidden = false; $('#b20-lote-id').textContent = LOTE; }
        else { lote = null; history.replaceState(null, '', location.pathname); banner.hidden = true; }
        apply();
      });
    });
    apply();
    return;
  }

  /* ======================================================================================
     Combo (configure.html) e Otimização (optimize.html): confirmar lote e progresso por ativo.
     ====================================================================================== */
  var isOpt = page === 'optimize';
  var runBtn = $(isOpt ? '[data-testid="run-optimization"]' : '[data-testid="combo-run"]');
  var confirmBox = $('#b20-confirm');
  var batchBox = $('#b20-batch');
  var runCopy = $('#b20-runcopy');
  var tfSel = $('#b20-tf');
  var periodSel = $('#b20-period');
  // Otimização: com lote (Confirmar ou painel) a coluna larga mostra o lote no lugar de "Ready to Optimize".
  var wideCol = isOpt ? document.querySelector('.lg\\:col-span-2') : null;
  var readyPanel = wideCol ? wideCol.querySelector(':scope > .glass-strong') : null;

  // Amostra: o lote BTC/USDT + NVDA + SPY do card. "need" = o que a Binance tem para a janela e ainda não está guardado.
  var BASE = [
    { sym: 'BTC/USDT', c: 'crypto', cur: 'USDT' },
    { sym: 'NVDA', c: 'stock', cur: 'USD' },
    { sym: 'SPY', c: 'etf', cur: 'USD' }
  ];
  var EFF = isOpt
    ? { 'BTC/USDT': '1 a 31 jan. 2024 · intrabar 15m', NVDA: 'precisão diária: sem 15m de 1 a 31 jan. 2024 (o 5m de NVDA começa em 19 mai. 2026)', SPY: 'precisão diária: sem 15m de 1 a 31 jan. 2024 (o 5m de SPY começa em 19 mai. 2026)' }
    : { 'BTC/USDT': '17 ago. 2017 – 24 out. 2026 · intrabar 15m', NVDA: '11 nov. 2014 – 23 out. 2026 · precisão diária: sem 15m de 11 nov. 2014 a 18 mai. 2026', SPY: '2 jan. 2015 – 23 out. 2026 · precisão diária: sem 15m de 2 jan. 2015 a 18 mai. 2026' };

  var scen = 'mixed';        // mixed | big
  var tf = tfSel ? tfSel.value : '1d';
  var rows = [];             // estado por ativo
  var status = 'idle';       // idle | running | pausing | paused | cancelled | completed
  var step = 0;
  var elapsed = 48;
  var filter = 'all';
  var shownMax = 50;

  function periodText() {
    if (isOpt) return '1 a 31 jan. 2024 (fixo nesta tela)';
    var o = periodSel && periodSel.options[periodSel.selectedIndex];
    return o ? o.text.toLowerCase() : 'todo o histórico';
  }
  function config() {
    return isOpt ? 'Médias: tendência (multi_ma_crossover) · ' + tf + ' · ' + periodText() + ' · Long · intrabar 15m'
                 : 'Médias: tendência · ' + tf + ' · ' + periodText() + ' · Long · Deep Backtest (15m)';
  }
  // Por que ação e ETF ficam fora: 'tf' = tempo que não serve; 'cov' = Otimização em 15m/1h/4h com o 5m fora da janela fixa.
  function outMode() {
    if (scen === 'big') return null;
    if (tf === '1m' || tf === '5m' || (isOpt && tf === '30m')) return 'tf';
    if (isOpt && (tf === '15m' || tf === '1h' || tf === '4h')) return 'cov';
    return null;
  }
  function groupReason(mode) {
    if (mode === 'cov') return 'o 5m deles começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo, que tem período.';
    return 'ação e ETF não rodam em ' + tf + '; para incluí-los, ' + (isOpt ? 'use 1d aqui ou o Combo, que tem período.' : 'use 15m, 1h, 4h ou 1d.');
  }
  function itemReason(sym, mode) {
    if (mode === 'cov') return 'o 5m de ' + sym + ' começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo. Ficou fora antes de começar.';
    return 'não roda em ' + tf + ' (ação e ETF: ' + (isOpt ? 'use 1d aqui ou o Combo' : '15m, 1h, 4h ou 1d') + '); ficou fora antes de começar.';
  }
  function needOf(sym) {
    // BTC/USDT e NVDA: guardados, sem lacunas e atualizados (seletor). SPY: sob demanda.
    if (sym !== 'SPY') return null;
    if (isOpt) return '1d';
    return tf === '1d' ? '1d e 5m do intrabar' : '5m';
  }

  function selection() {
    if (scen === 'big') return null;
    var mode = outMode();
    return BASE.map(function (a) {
      return { sym: a.sym, c: a.c, cur: a.cur, need: needOf(a.sym), out: !!mode && a.c !== 'crypto' };
    });
  }

  function syncReady() {
    if (!readyPanel) return;
    readyPanel.style.display = (!confirmBox.hidden || !batchBox.hidden) ? 'none' : '';
  }

  function setRunCopy() {
    if (!runCopy) return;
    if (scen === 'big') {
      runCopy.innerHTML = '<b>Lote de 2.431 ativos</b> (2.431 ações): otimiza cada um com esta configuração e grava o melhor de cada em favoritos (nota "gerado em lote"). Antes de começar, você confirma o lote.';
      return;
    }
    var mode = outMode();
    if (mode) {
      runCopy.innerHTML = '<b>Lote de 3 ativos: roda 1</b> (BTC/USDT). <span class="b20-out">Fora antes de começar: NVDA (Ação), SPY (ETF) — ' + groupReason(mode) + '</span>';
      return;
    }
    runCopy.innerHTML = '<b>Lote de 3 ativos</b> (1 cripto, 1 ação, 1 ETF): otimiza cada um com esta configuração' + (isOpt ? ', no período fixo desta tela,' : '') + ' e grava o melhor de cada em favoritos (nota "gerado em lote"). Antes de começar, você confirma o lote.';
  }

  function setTimeframe(v) {
    tf = v;
    if (tfSel) tfSel.value = v;
  }

  var COLLECT_TAIL = ' A coleta acontece dentro do lote, ativo por ativo, com progresso, e pode ser pausada ou encerrada.';
  var COLLECT_RULE = ' Conta só o que a Binance tem para a janela e ainda não está guardado.';

  /* ---------- Confirmar lote ---------- */
  function openConfirm() {
    var sel = selection();
    var html;
    if (!sel) {
      html = '<h3 id="b20-confirm-title" tabindex="-1">Confirmar lote de 2.431 ativos</h3><dl>' +
        '<div><dt>Vão rodar</dt><dd><span class="b20-big">2.431</span> ações (USD)</dd></div>' +
        '<div class="b20-collect"><dt>Precisam de coleta de histórico</dt><dd><span class="b20-big">2.388 de 2.431</span> — 2.351 sem histórico guardado (1d e 5m do intrabar) e 37 só com o trecho desde a última coleta. Os outros 43 já estão guardados, sem lacunas e atualizados.' + COLLECT_RULE + COLLECT_TAIL + '</dd></div>' +
        '<div><dt>Ficam fora</dt><dd>nenhum</dd></div>' +
        '<div><dt>Configuração</dt><dd>' + config() + '</dd></div>' +
        '<div><dt>Favoritos</dt><dd>o melhor de cada ativo, com a nota "gerado em lote"; ativo que já tem favorito no mesmo período e direção é pulado.</dd></div></dl>';
    } else {
      var mode = outMode();
      var run = sel.filter(function (a) { return !a.out; });
      var out = sel.filter(function (a) { return a.out; });
      var need = run.filter(function (a) { return a.need; });
      var ready = run.filter(function (a) { return !a.need; });
      var classes = [];
      var cc = run.filter(function (a) { return a.c === 'crypto'; }).length, sc = run.filter(function (a) { return a.c === 'stock'; }).length, ec = run.filter(function (a) { return a.c === 'etf'; }).length;
      if (cc) classes.push(cc + ' cripto (USDT)');
      if (sc) classes.push(sc + (sc === 1 ? ' ação' : ' ações') + ' (USD)');
      if (ec) classes.push(ec + (ec === 1 ? ' ETF' : ' ETFs') + ' (USD)');
      var readyTxt = ready.length ? ' ' + ready.map(function (a) { return a.sym; }).join(' e ') + (ready.length === 1 ? ' já está guardado' : ' já estão guardados') + ', sem lacunas e atualizado' + (ready.length === 1 ? '' : 's') + '.' : '';
      var spyNote = isOpt && need.some(function (a) { return a.sym === 'SPY'; }) ? ' O 5m de SPY não entra: a Binance não tem 5m dele em jan. 2024.' : '';
      html = '<h3 id="b20-confirm-title" tabindex="-1">Confirmar lote de ' + sel.length + ' ativos</h3><dl>' +
        '<div><dt>Vão rodar</dt><dd><span class="b20-big">' + run.length + '</span> — ' + classes.join(', ') + ': ' + run.map(function (a) { return a.sym; }).join(', ') + '</dd></div>' +
        '<div class="b20-collect"><dt>Precisam de coleta de histórico</dt><dd><span class="b20-big" data-testid="batch-need-count">' + need.length + ' de ' + run.length + '</span>' +
        (need.length ? ' — ' + need.map(function (a) { return a.sym + ' (' + a.need + ')'; }).join(', ') + '.' + readyTxt + spyNote + COLLECT_RULE + COLLECT_TAIL : ' —' + readyTxt + COLLECT_RULE) + '</dd></div>' +
        '<div><dt>Ficam fora</dt><dd>' + (out.length ? '<span class="b20-out">' + out.map(function (a) { return a.sym + ' (' + CLASS_LABEL[a.c] + ')'; }).join(', ') + ' — ' + groupReason(mode) + '</span>' : 'nenhum') + '</dd></div>' +
        '<div><dt>Configuração</dt><dd data-testid="batch-config">' + config() + '</dd></div>' +
        '<div><dt>Favoritos</dt><dd>o melhor de cada ativo, com a nota "gerado em lote"; ativo que já tem favorito no mesmo período e direção é pulado.</dd></div></dl>';
    }
    html += '<div class="b20-actions"><button type="button" class="b20-btn primary" id="b20-go" data-testid="batch-confirm">' + ICON.play + 'Confirmar e rodar</button>' +
      '<button type="button" class="b20-btn" id="b20-back" data-testid="batch-back">Voltar</button></div>';
    confirmBox.innerHTML = html;
    confirmBox.hidden = false;
    batchBox.hidden = true;
    syncReady();
    $('#b20-confirm-title').focus();
    $('#b20-go').addEventListener('click', startBatch);
    $('#b20-back').addEventListener('click', closeConfirm);
  }

  function closeConfirm() { confirmBox.hidden = true; syncReady(); runBtn.focus(); }

  /* ---------- Lote pausado bloqueia um lote novo (decisão de Alan, 24/10/2026) ---------- */
  function openPausedBlock() {
    var saved = savedCount(counts(rows));
    confirmBox.innerHTML = '<h3 id="b20-confirm-title" tabindex="-1">Há um lote pausado</h3>' +
      '<p class="b20-block" data-testid="batch-paused-block">Retome ou encerre o lote ' + LOTE + ' antes de começar outro. ' +
      (saved ? 'Encerrar mantém ' + (saved === 1 ? 'o favorito já gravado' : 'os ' + saved + ' favoritos já gravados') + ' e marca o resto "Não rodou".' : 'Encerrar marca o resto "Não rodou".') + '</p>' +
      '<div class="b20-actions"><button type="button" class="b20-btn primary" id="b20-block-resume" data-testid="batch-block-resume">' + ICON.play + 'Retomar o lote ' + LOTE + '</button>' +
      '<button type="button" class="b20-btn danger" id="b20-block-cancel" data-testid="batch-block-cancel">' + ICON.stop + 'Encerrar o lote ' + LOTE + '</button>' +
      '<button type="button" class="b20-btn" id="b20-back" data-testid="batch-back">Voltar</button></div>';
    confirmBox.hidden = false;
    syncReady();
    $('#b20-confirm-title').focus();
    $('#b20-block-resume').addEventListener('click', function () { confirmBox.hidden = true; doResume(); });
    $('#b20-block-cancel').addEventListener('click', function () { confirmBox.hidden = true; doCancel(); });
    $('#b20-back').addEventListener('click', closeConfirm);
  }

  /* ---------- Estado por ativo ---------- */
  var STATE = {
    queued: ['wait', 'Na fila'],
    collecting: ['load', 'Coletando histórico'],
    optimizing: ['load', 'Otimizando'],
    success: ['ok', 'Sucesso'],
    daily: ['warn', 'Sucesso · precisão diária'],
    insufficient: ['warn', 'Insuficiente'],
    rejected: ['ban', 'Rejeitado'],
    failed: ['fail', 'Falha'],
    skipped: ['skip', 'Pulado'],
    out: ['out', 'Fora'],
    notrun: ['stop', 'Não rodou']
  };
  var CHIP = [['all', 'Todos'], ['success', 'Sucesso'], ['daily', 'Precisão diária'], ['insufficient', 'Insuficiente'], ['rejected', 'Rejeitado'], ['failed', 'Falha'], ['skipped', 'Pulado'], ['out', 'Fora'], ['running', 'Em curso'], ['queued', 'Na fila'], ['notrun', 'Não rodou']];
  function chipOf(s) { return (s === 'collecting' || s === 'optimizing') ? 'running' : s; }

  function favLink() { return ' · <a href="index.html?lote=' + LOTE + '">abrir em Favoritos</a>'; }

  function maxStep() { return outMode() ? 1 : 3; }

  function stepRows() {
    var mode = outMode();
    var r = selection().map(function (a) {
      return { sym: a.sym, c: a.c, cur: a.cur, state: a.out ? 'out' : 'queued',
        detail: a.out ? itemReason(a.sym, mode) : (a.need ? 'precisa de coleta: ' + a.need + '.' : 'histórico já guardado, sem lacunas e atualizado: nada a coletar.') };
    });
    var btc = r[0], nv = r[1], sp = r[2];
    function done(x, daily) {
      x.state = daily ? 'daily' : 'success';
      x.detail = '<b>Favorito gravado</b> · ' + EFF[x.sym] + favLink();
    }
    if (mode) {
      if (step === 0) { btc.state = 'optimizing'; btc.detail = 'tentativa 38 de 60 · todas na mesma amostra, guardada no começo.'; }
      else done(btc, false);
      return r;
    }
    done(btc, false);
    if (step === 0) { nv.state = 'optimizing'; nv.detail = 'tentativa 22 de 60 · todas na mesma amostra, guardada no começo · histórico já guardado, nada a coletar.'; }
    if (step >= 1) done(nv, true);
    if (step === 1) {
      sp.state = 'collecting';
      sp.detail = isOpt ? '1d · página 1 de 2<progress max="2" value="1" aria-label="Coleta de SPY: página 1 de 2"></progress>'
                        : '5m do intrabar · página 7 de 20<progress max="20" value="7" aria-label="Coleta de SPY: página 7 de 20"></progress>';
    }
    if (step === 2) { sp.state = 'optimizing'; sp.detail = 'tentativa 51 de 60 · todas na mesma amostra, guardada no começo.'; }
    if (step >= 3) done(sp, true);
    return r;
  }

  function bigRows() {
    var names = ['AAPL', 'ABBV', 'ABNB', 'ABT', 'ACN', 'ADBE', 'ADI', 'ADP', 'AMAT', 'AMD', 'AMGN', 'AMZN'];
    var out = [];
    for (var i = 0; i < 2431; i++) {
      var sym = i < names.length ? names[i] : 'AÇÃO ' + (i + 1);
      var st = i < 3 ? 'daily' : i === 3 ? 'collecting' : 'queued';
      var det = st === 'daily' ? '<b>Favorito gravado</b> · precisão diária: sem 15m antes de 19 mai. 2026' : st === 'collecting' ? '1d · página 1 de 3<progress max="3" value="1" aria-label="Coleta de ' + sym + ': página 1 de 3"></progress>' : 'precisa de coleta: 1d e 5m do intrabar.';
      out.push({ sym: sym, c: 'stock', cur: 'USD', state: st, detail: det });
    }
    return out;
  }

  function problemRows() {
    return [
      { sym: 'BTC/USDT', c: 'crypto', cur: 'USDT', state: 'success', detail: '<b>Favorito gravado</b> · ' + EFF['BTC/USDT'] + favLink() },
      { sym: 'NVDA', c: 'stock', cur: 'USD', state: 'daily', detail: '<b>Favorito gravado</b> · ' + EFF.NVDA + favLink() },
      { sym: 'AAPL', c: 'stock', cur: 'USD', state: 'insufficient', detail: 'Dados insuficientes: a janela coberta tem 120 candles de 1d e a estratégia precisa de pelo menos 201 (média de 200). Nenhum favorito gravado.' },
      { sym: 'QQQ', c: 'etf', cur: 'USD', state: 'rejected', detail: 'Reprovado no walk-forward (NO-GO no holdout): retorno do holdout −8,2%. Nenhum favorito gravado.' },
      { sym: 'SPY', c: 'etf', cur: 'USD', state: 'failed', detail: 'Histórico de SPY indisponível agora: limite de requisições da Binance. Nenhum favorito gravado; rode de novo mais tarde.' },
      { sym: 'ETH/USDT', c: 'crypto', cur: 'USDT', state: 'skipped', detail: 'Já está nos favoritos com o mesmo período e direção.' },
      { sym: 'SOL/USDT', c: 'crypto', cur: 'USDT', state: 'out', detail: 'Suspenso pela Binance; não entra em análise nova. Ficou fora antes de começar.' }
    ];
  }

  function counts(list) {
    var c = { all: list.length };
    list.forEach(function (r) { var k = chipOf(r.state); c[k] = (c[k] || 0) + 1; });
    return c;
  }
  function savedCount(c) { return (c.success || 0) + (c.daily || 0); }

  function render() {
    var list = rows;
    var c = counts(list);
    var total = list.filter(function (r) { return r.state !== 'out'; }).length;
    var finished = list.filter(function (r) { return ['success', 'daily', 'insufficient', 'rejected', 'failed', 'skipped', 'notrun'].indexOf(r.state) >= 0; }).length;
    var current = list.filter(function (r) { return r.state === 'collecting' || r.state === 'optimizing'; })[0];
    var pill = { running: ['run', 'Rodando'], pausing: ['warn', 'Pausando'], paused: ['warn', 'Pausado'], cancelled: ['stop', 'Encerrado'], completed: ['ok', 'Concluído'] }[status];
    var fmtTime = Math.floor(elapsed / 60) + 'm ' + (elapsed % 60) + 's';
    var saved = savedCount(c);
    var live;
    if (status === 'running') live = current ? current.sym + ': ' + (current.state === 'collecting' ? 'coletando histórico' : 'otimizando') + '.' : 'Rodando.';
    else if (status === 'pausing') live = 'Pausa pedida: o lote para quando ' + (current ? current.sym : 'o ativo em curso') + ' terminar a etapa em curso (' + (current && current.state === 'collecting' ? 'coleta' : 'otimização') + ').';
    else if (status === 'paused') live = 'Pausado em ' + finished + ' de ' + total + '. Os concluídos ficam; ' + list.filter(function (r) { return r.state === 'queued'; }).map(function (r) { return r.sym; }).slice(0, 3).join(', ') + (c.queued > 3 ? ' e mais ' + fmt(c.queued - 3) : '') + ((c.queued || 0) > 1 ? ' esperam' : ' espera') + '. Retomar continua no mesmo lote; um lote novo só depois de retomar ou encerrar este.';
    else if (status === 'cancelled') live = 'Encerrado pelo usuário em ' + finished + ' de ' + total + '. ' + saved + ' favorito(s) gravado(s) ficam; não rodaram: ' + list.filter(function (r) { return r.state === 'notrun'; }).map(function (r) { return r.sym; }).join(', ') + '.';
    else live = 'Lote concluído: ' + finished + ' de ' + total + ' em ' + fmtTime + ' · ' + saved + ' favorito(s) gravado(s)' + (c.daily ? ' (' + c.daily + ' com precisão diária)' : '') + (c.insufficient || c.rejected || c.failed ? ' · sem resultado válido: ' + ((c.insufficient || 0) + (c.rejected || 0) + (c.failed || 0)) : '') + '.';

    var head = '<div class="b20-bhead"><h3 id="b20-batch-title" tabindex="-1">Lote ' + LOTE + ' <span class="b20-pill" data-tone="' + pill[0] + '" data-testid="batch-status">' + pill[1] + '</span></h3>' +
      '<p class="b20-bmeta">' + fmt(finished) + ' de ' + fmt(total) + ' ativos · ' + fmtTime + (status === 'running' ? ' · resta ~' + (scen === 'big' ? '9h 40m' : '1m 30s') : '') + '</p></div>';
    var pct = total ? Math.round((finished / total) * 100) : 0;
    var body = '<div class="b20-bbody"><p class="b20-live" role="status" aria-live="polite" data-testid="batch-live">' + live + '</p>' +
      '<div class="b20-bar" role="progressbar" aria-label="Ativos concluídos" aria-valuemin="0" aria-valuemax="' + total + '" aria-valuenow="' + finished + '"><span style="width:' + pct + '%"></span></div>';
    if (c.daily) body += '<p class="b20-note" data-testid="batch-daily-note"><b>Precisão diária em ' + c.daily + (c.daily === 1 ? ' ativo' : ' ativos') + ':</b> o intradiário de 15m não cobre a janela, então o stop foi simulado no candle diário em toda a janela. O resultado é válido e a marca segue para Favoritos.</p>';
    var chips = CHIP.filter(function (k) { return k[0] === 'all' || c[k[0]]; }).map(function (k) {
      return '<button type="button" class="b20-chip" data-chip="' + k[0] + '" aria-pressed="' + (filter === k[0]) + '">' + k[1] + ' <b>' + fmt(c[k[0]] || 0) + '</b></button>';
    }).join('');
    body += '<div class="b20-chips" role="group" aria-label="Filtrar por estado">' + chips + '</div>';
    var visible = list.filter(function (r) { return filter === 'all' || chipOf(r.state) === filter; });
    var slice = visible.slice(0, shownMax);
    body += '<div class="b20-listhead" aria-hidden="true"><span>Ativo</span><span>Estado</span><span>Detalhe</span></div>';
    body += '<ol class="b20-list" aria-labelledby="b20-batch-title" data-testid="batch-items">' + slice.map(function (r) {
      var st = STATE[r.state];
      return '<li class="b20-row" data-state="' + r.state + '" data-asset="' + esc(r.sym) + '"><div class="b20-asset"><b>' + esc(r.sym) + '</b><span>' + cls(r.c) + ' · <span class="b20-cur">' + r.cur + '</span></span></div>' +
        '<div class="b20-state">' + ICON[st[0]] + '<span>' + st[1] + '</span></div><div class="b20-detail">' + r.detail + '</div></li>';
    }).join('') + '</ol>';
    if (visible.length > shownMax) body += '<button type="button" class="b20-more" id="b20-more">Mostrar mais 50 · ' + fmt(shownMax) + ' de ' + fmt(visible.length) + '</button>';
    var actions = '';
    if (status === 'running' || status === 'pausing') {
      // Durante "Pausando…" os botões ficam aria-disabled (focáveis), para o foco não cair no <body>.
      var dis = status === 'pausing' ? ' aria-disabled="true"' : '';
      actions = '<div class="b20-actions"><button type="button" class="b20-btn warn" id="b20-pause" data-testid="batch-pause"' + dis + '>' + ICON.pause + (status === 'pausing' ? 'Pausando…' : 'Pausar') + '</button>' +
        '<button type="button" class="b20-btn danger" id="b20-cancel" data-testid="batch-cancel"' + dis + '>' + ICON.stop + 'Encerrar</button></div>';
    } else if (status === 'paused') {
      actions = '<div class="b20-actions"><button type="button" class="b20-btn primary" id="b20-resume" data-testid="batch-resume">' + ICON.play + 'Retomar</button>' +
        '<button type="button" class="b20-btn danger" id="b20-cancel" data-testid="batch-cancel">' + ICON.stop + 'Encerrar</button></div>';
    }
    body += actions;
    if (status === 'completed' || status === 'cancelled' || status === 'paused') {
      body += '<div class="b20-links" data-testid="batch-links">' + (saved ? '<a href="index.html?lote=' + LOTE + '" data-testid="batch-open-favorites">' + (saved === 1 ? 'Ver o resultado do lote em Favoritos' : 'Ver os ' + saved + ' resultados do lote em Favoritos') + '</a>' : '') +
        (isOpt ? '' : '<a href="#" data-testid="batch-discovery">Descoberta sistemática (varredura)</a>') + '</div>';
    }
    body += '</div>';
    batchBox.innerHTML = head + body;
    batchBox.hidden = false;
    syncReady();
    bind();
  }

  function isOff(el) { return el && el.getAttribute('aria-disabled') === 'true'; }

  function doResume() {
    status = 'running';
    if (scen === 'big') { rows[4].state = 'collecting'; rows[4].detail = '1d · página 1 de 3<progress max="3" value="1" aria-label="Coleta: página 1 de 3"></progress>'; }
    else { rows = stepRows(); }
    render(); var p = $('#b20-pause'); p && p.focus();
  }

  function doCancel() {
    status = 'cancelled';
    rows.forEach(function (r) {
      if (r.state === 'queued' || r.state === 'collecting' || r.state === 'optimizing') { r.state = 'notrun'; r.detail = 'Não rodou: o lote foi encerrado antes deste ativo.'; }
    });
    render(); $('#b20-batch-title').focus();
  }

  function bind() {
    $$('.b20-chip', batchBox).forEach(function (b) {
      b.addEventListener('click', function () { filter = b.getAttribute('data-chip'); shownMax = 50; render(); var again = $('.b20-chip[data-chip="' + filter + '"]', batchBox); again && again.focus(); });
    });
    var more = $('#b20-more');
    more && more.addEventListener('click', function () { shownMax += 50; render(); var m = $('#b20-more'); (m || $('#b20-batch-title')).focus(); });
    var pause = $('#b20-pause');
    pause && pause.addEventListener('click', function () {
      if (isOff(pause)) return;
      status = 'pausing'; render(); $('#b20-pause').focus();
      setTimeout(function () {
        if (status !== 'pausing') return;
        var hadFocus = document.activeElement && document.activeElement.id === 'b20-pause';
        // A etapa em curso termina e o lote para antes da próxima.
        if (scen === 'big') {
          rows[3].state = 'daily'; rows[3].detail = '<b>Favorito gravado</b> · precisão diária: sem 15m antes de 19 mai. 2026';
          status = 'paused';
        } else {
          step += 1;
          if (step >= maxStep()) { step = maxStep(); rows = stepRows(); status = 'completed'; }
          else {
            rows = stepRows();
            rows.forEach(function (r) {
              if (r.state === 'optimizing') { r.state = 'queued'; r.detail = 'histórico coletado; otimiza ao retomar, na mesma amostra.'; }
              if (r.state === 'collecting') { r.state = 'queued'; r.detail = 'precisa de coleta: ' + (needOf(r.sym) || 'nada') + '.'; }
            });
            status = 'paused';
          }
        }
        render();
        if (hadFocus || document.activeElement === document.body) { var r = $('#b20-resume') || $('#b20-batch-title'); r.focus(); }
      }, 900);
    });
    var resume = $('#b20-resume');
    resume && resume.addEventListener('click', doResume);
    var cancel = $('#b20-cancel');
    cancel && cancel.addEventListener('click', function () { if (isOff(cancel)) return; doCancel(); });
  }

  function startBatch() {
    confirmBox.hidden = true;
    status = 'running'; step = 0; elapsed = 48; filter = 'all'; shownMax = 50;
    rows = scen === 'big' ? bigRows() : stepRows();
    render();
    $('#b20-batch-title').focus();
  }

  function advance() {
    if (status !== 'running') return;
    if (scen === 'big') { return; }
    step += 1; elapsed += 37;
    rows = stepRows();
    if (step >= maxStep()) status = 'completed';
    render();
  }

  runBtn.addEventListener('click', function (e) {
    e.preventDefault();
    if (status === 'paused') { openPausedBlock(); return; }
    if (status === 'running' || status === 'pausing') return;
    openConfirm();
  });

  // Demonstração (só no protótipo).
  var DEMO_TF = { mixed: '1d', mixed5m: '5m', mixed1h: '1h', big: '1d' };
  function pressFor(v) {
    var key = v === '1d' ? 'mixed' : v === '5m' ? 'mixed5m' : v === '1h' ? 'mixed1h' : null;
    $$('[data-demo="sel"]').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-value') === key ? 'true' : 'false'); });
  }
  $$('[data-demo="sel"]').forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.getAttribute('data-value');
      press('sel', b);
      scen = v === 'big' ? 'big' : 'mixed';
      setTimeframe(DEMO_TF[v]);
      status = 'idle'; confirmBox.hidden = true; batchBox.hidden = true; syncReady();
      setRunCopy();
    });
  });
  var adv = $('#demo-advance');
  adv && adv.addEventListener('click', advance);
  var prob = $('#demo-problems');
  prob && prob.addEventListener('click', function () {
    scen = 'mixed'; confirmBox.hidden = true; status = 'completed'; filter = 'all'; elapsed = 312; rows = problemRows(); render();
  });
  if (tfSel) tfSel.addEventListener('change', function () {
    scen = 'mixed';
    tf = tfSel.value;
    pressFor(tf);
    setRunCopy();
  });
  setRunCopy();
})();
