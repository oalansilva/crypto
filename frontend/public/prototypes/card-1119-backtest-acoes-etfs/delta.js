/* Card #1119 — DELTA do protótipo (rework r1): recusa de favoritar ação/ETF, "Dados e execução" recolhido no celular,
   estados de Combo e Otimização e painel de demonstração. Nada aqui vai para o produto além do comportamento descrito no design.md. */
(function () {
  'use strict';

  var FAV_REASON = 'Ações e ETFs ainda não podem ser favoritados: atualização diária e alertas dessas classes ainda não existem.';
  var EQUITY_OUT = 'ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois';

  // Favoritar recusado: o botão continua focável (aria-disabled), não abre o modal e anuncia o motivo.
  var fav = document.querySelector('[data-testid="favorite-refused"]');
  if (fav) {
    var btn = fav.querySelector('button');
    var status = fav.querySelector('[role="status"]');
    btn.addEventListener('click', function (event) {
      event.preventDefault();
      status.textContent = '';
      window.setTimeout(function () { status.textContent = 'Não salvo. ' + FAV_REASON; }, 30);
      fav.setAttribute('data-flash', '1');
      window.setTimeout(function () { fav.removeAttribute('data-flash'); }, 1600);
    });
  }

  // "Dados e execução": no celular o resumo (precisão e avisos) fica visível e o resto abre com um toque.
  // O botão só aparece abaixo de 768px (CSS); no desktop e no tablet o conteúdo fica sempre aberto.
  var toggle = document.querySelector('[data-testid="result-data-toggle"]');
  var more = document.getElementById('r19-more');
  if (toggle && more) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      more.setAttribute('data-open', open ? 'true' : 'false');
    });
  }

  function press(group, button) {
    document.querySelectorAll('[data-demo="' + group + '"]').forEach(function (b) {
      b.setAttribute('aria-pressed', b === button ? 'true' : 'false');
    });
  }

  var ICON_WARN = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>';
  var ICON_INFO = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>';

  // Título e fato da precisão seguem o tempo gráfico: "diária" só no 1d; no 4h é "do candle de 4h".
  var PRECISION = {
    missing: { tone: 'warn', title: 'Precisão diária', fact: 'Diária<span>Pedida: intrabar 15m</span>',
      text: 'O intradiário de 15m faltou de <time datetime="2014-11-11">11 nov. 2014</time> a <time datetime="2026-05-18">18 mai. 2026</time>. Você pediu precisão intrabar; como ele não cobre a janela, o stop foi simulado no candle diário em toda a janela.' },
    error: { tone: 'warn', title: 'Precisão diária', fact: 'Diária<span>Pedida: intrabar 15m</span>',
      text: 'Não foi possível ler o intradiário de 15m desta janela (falha ao ler o histórico guardado). O stop foi simulado no candle diário em toda a janela.' },
    off: { tone: 'info', title: 'Precisão diária, escolhida', fact: 'Diária<span>Deep Backtest desligado</span>',
      text: 'O Deep Backtest estava desligado: stops e saídas foram simulados no candle diário.' },
    covered: { tone: 'info', title: 'Precisão intrabar 15m', fact: 'Intrabar 15m',
      text: 'O 15m cobre a janela inteira: stops e saídas foram simulados candle a candle de 15m.' },
    'crypto-missing': { tone: 'warn', title: 'Precisão do candle de 4h', fact: 'Candle de 4h<span>Pedida: intrabar 15m</span>',
      text: 'O intradiário de 15m faltou de <time datetime="2026-03-18">18 mar. 2026</time> a <time datetime="2026-03-24">24 mar. 2026</time>. Você pediu precisão intrabar; como ele não cobre a janela, o stop foi simulado no candle de 4h em toda a janela.' }
  };

  function factRow(label) {
    var found = null;
    document.querySelectorAll('[data-testid="result-facts"] > div').forEach(function (row) {
      if (row.querySelector('dt').textContent === label) found = row.querySelector('dd');
    });
    return found;
  }

  function convItem(label) {
    var found = null;
    document.querySelectorAll('[data-testid="result-conventions"] li').forEach(function (li) {
      var b = li.querySelector('b');
      if (b && b.textContent === label + '.') found = li;
    });
    return found;
  }

  function setPrecision(key) {
    var p = PRECISION[key];
    var box = document.querySelector('[data-testid="result-precision"]');
    if (!p || !box) return;
    box.setAttribute('data-tone', p.tone);
    box.querySelector('svg').outerHTML = p.tone === 'warn' ? ICON_WARN : ICON_INFO;
    document.getElementById('r19-precision-title').textContent = p.title;
    document.getElementById('r19-precision-text').innerHTML = p.text;
    var dd = factRow('Precisão');
    if (dd) dd.innerHTML = p.fact;
  }

  // Resultado de NVDA: a coleta parou no meio com parte gravada (roda no trecho guardado e diz isso).
  var alertsText = document.getElementById('r19-alerts-text');
  var alertsBase = alertsText ? alertsText.textContent : '';
  var coveredDd = factRow('Janela coberta');
  var coveredBase = coveredDd ? coveredDd.innerHTML : '';
  function setCoverage(key) {
    var note = document.querySelector('[data-testid="result-coverage"]');
    if (!note) return;
    if (key === 'partial') {
      document.getElementById('r19-coverage-text').innerHTML = 'A coleta do 1d de NVDA parou depois de guardar até <time datetime="2026-10-02">2 out. 2026</time> (limite de requisições da Binance). O backtest rodou no trecho guardado, de <time datetime="2014-11-11">11 nov. 2014</time> a <time datetime="2026-10-02">2 out. 2026</time>; de 5 a 22 out. 2026 ficou fora. Rode de novo mais tarde para completar.';
      note.hidden = false;
      if (coveredDd) coveredDd.innerHTML = '<time datetime="2014-11-11">11 nov. 2014</time> – <time datetime="2026-10-02">2 out. 2026</time><span>Coleta parou em 2 out.; pedida até 22 out. 2026</span>';
      if (alertsText) alertsText.textContent = 'janela coberta menor que a pedida · ' + alertsBase;
    } else {
      note.hidden = true;
      if (coveredDd) coveredDd.innerHTML = coveredBase;
      if (alertsText) alertsText.textContent = alertsBase;
    }
  }

  // SPY: textos do tempo gráfico de ação/ETF em 1h, 4h e 15m (fato, custo e anualização).
  var TF = {
    '1h': { fact: '1h montado do 5m<span>09:30, 10:30 … 15:30–16:00; nenhum candle atravessa o fechamento</span>', slip: '0,03% por lado no 1h', ann: '252 pregões × 7 candles de 1h por ano' },
    '4h': { fact: '4h montado do 5m<span>09:30–13:30 e 13:30–16:00 (meio-pregão: 09:30–13:00); nenhum candle atravessa o fechamento</span>', slip: '0,02% por lado no 4h', ann: '252 pregões × 2 candles de 4h por ano' },
    '15m': { fact: '15m montado do 5m<span>09:30, 09:45 … 15:45–16:00; nenhum candle atravessa o fechamento</span>', slip: '0,05% por lado no 15m', ann: '252 pregões × 26 candles de 15m por ano' }
  };
  function setTf(key) {
    var t = TF[key];
    var dd = factRow('Tempo gráfico');
    if (!t || !dd) return;
    dd.innerHTML = t.fact;
    var cost = convItem('Custos');
    if (cost) cost.innerHTML = '<b>Custos.</b> Taxa de 0,075% por lado, assumida: a taxa da Binance Ações ainda não foi confirmada. Slippage de ' + t.slip + '.';
    var ann = convItem('Anualização');
    if (ann) ann.innerHTML = '<b>Anualização.</b> Anos pelo calendário (dias corridos ÷ 365). Risco por período em ' + t.ann + '.';
  }

  // --- Combo e Otimização: seleção, tempo gráfico e devolução da execução ---------------------------
  var page = document.body.getAttribute('data-page');
  var runCopy = document.querySelector('[data-testid="combo-run-copy"], [data-testid="opt-run-copy"]');
  var slot = document.getElementById('r19-run-notice');
  var chips = document.querySelector('[data-testid="asset-chips"]');
  var chipsHtml = chips ? chips.innerHTML : '';
  var marketBox = document.querySelector('[data-testid="combo-market-data"]');
  var tfSelect = null;
  document.querySelectorAll('select').forEach(function (s) {
    if (!tfSelect && s.querySelector('option[value="5m"]')) tfSelect = s;
  });
  var CRYPTO_ONLY = page === 'optimize' ? ['1m', '5m', '30m'] : ['1m', '5m'];
  var sel = 'one';

  function chip(sym, cls) {
    return '<span class="ap-chip" data-asset="' + sym + '"><span><b>' + sym + '</b> · ' + cls + '</span><button type="button" aria-label="Remover ' + sym + ' da seleção">×</button></span>';
  }

  function notice(kind, role, title, body) {
    if (!slot) return;
    slot.innerHTML = '';
    if (!kind) return;
    var div = document.createElement('div');
    div.className = kind === 'collect' ? 'r19-collect' : kind;
    div.setAttribute('role', role);
    div.setAttribute('data-testid', kind === 'collect' ? 'run-collecting' : 'run-warning');
    div.innerHTML = title ? '<strong>' + title + '</strong>' + body : body;
    slot.appendChild(div);
  }

  function setCopy(text, blocked) {
    if (!runCopy) return;
    runCopy.textContent = text;
    runCopy.classList.toggle('text-amber-300', !!blocked);
    runCopy.classList.toggle('text-zinc-400', !blocked);
  }

  var ONE = page === 'optimize'
    ? '1 ação (NVDA): otimiza em 1d, de 1 a 31 jan. 2024, e mostra o resultado ao lado.'
    : '1 ação (NVDA): otimiza e abre o resultado, sem salvar em favoritos: ações e ETFs ainda não podem ser favoritados.';
  var MIXED = page === 'optimize'
    ? 'Roda 1 par cripto (BTC/USDT): otimiza e mostra o resultado ao lado. Fora: NVDA (Ação) — ' + EQUITY_OUT + '.'
    : 'Roda 1 par cripto (BTC/USDT): otimiza, salva em favoritos e abre a página de favoritos. Fora: NVDA (Ação) — ' + EQUITY_OUT + '.';
  var EQUITIES = (page === 'optimize' ? 'Nada será executado: ' : 'Nada será executado nem salvo: ') + 'NVDA, SPY — ' + EQUITY_OUT + '.';

  function tfValue() { return tfSelect ? tfSelect.value : ''; }
  function equityRuns() { return sel === 'one' || sel === 'fail'; }
  function badTf() {
    if (!equityRuns()) return null;
    var v = tfValue();
    if (CRYPTO_ONLY.indexOf(v) >= 0) return 'crypto-only';
    if (page === 'optimize' && ['15m', '1h', '4h'].indexOf(v) >= 0) return 'no-5m';
    return null;
  }

  // Aviso que aparece antes de rodar, assim que o estado inválido nasce (não só depois do clique).
  function evaluate() {
    var bad = badTf();
    if (bad === 'crypto-only') {
      setCopy('Nada será executado: NVDA (Ação) não roda em ' + tfValue() + '. Escolha 15m, 1h, 4h ou 1d.', true);
      notice('ap-warn', 'status', 'Escolha 15m, 1h, 4h ou 1d', 'Ação e ETF não rodam em 1m nem 5m. Nada foi executado; a seleção foi mantida.');
      return;
    }
    if (bad === 'no-5m') {
      setCopy('Nada será executado: o 5m de NVDA começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela. Use 1d aqui ou o Combo, que tem período.', true);
      notice('', '', '', '');
      return;
    }
    notice('', '', '', '');
    if (sel === 'mixed') setCopy(MIXED, false);
    else if (sel === 'equities') setCopy(EQUITIES, true);
    else setCopy(ONE, false);
  }

  function setSel(key) {
    sel = key;
    if (chips) {
      chips.innerHTML = chipsHtml + (key === 'mixed' ? chip('BTC/USDT', 'Cripto') : key === 'equities' ? chip('SPY', 'ETF') : '');
    }
    if (marketBox) marketBox.textContent = key === 'mixed' ? 'CCXT (crypto exchange data)' : 'Binance Ações · pregão regular de Nova York · ajustado por split';
    if (tfSelect) {
      // Na seleção mista só a cripto roda: 1m/5m (e 30m na Otimização) voltam a ficar disponíveis.
      CRYPTO_ONLY.forEach(function (v) {
        var o = tfSelect.querySelector('option[value="' + v + '"]');
        if (o) o.disabled = key !== 'mixed';
      });
    }
    evaluate();
  }

  if (chips) {
    chips.addEventListener('click', function (event) {
      var b = event.target.closest('button');
      if (!b) return;
      var c = b.closest('.ap-chip');
      if (c && c.getAttribute('data-asset') !== 'NVDA') {
        var first = document.querySelector('[data-demo="sel"][data-value="one"], [data-demo="osel"][data-value="one"]');
        if (first) press(first.getAttribute('data-demo'), first);
        setSel('one');
      }
    });
  }
  if (tfSelect && (page === 'configure' || page === 'optimize')) tfSelect.addEventListener('change', evaluate);

  var COLLECT = page === 'optimize'
    ? 'Coletando histórico de NVDA (1d de 1 a 31 jan. 2024) antes de otimizar… Na primeira execução de um ativo isso pode levar alguns segundos.'
    : 'Coletando histórico de NVDA para a janela pedida (1h e o 5m do intrabar) antes de otimizar… Na primeira execução de um ativo isso pode levar alguns segundos.';

  var run = document.querySelector('[data-testid="combo-run"], [data-testid="run-optimization"]');
  if (run && (page === 'configure' || page === 'optimize')) {
    run.addEventListener('click', function () {
      var bad = badTf();
      if (bad === 'crypto-only') { evaluate(); return; }
      if (bad === 'no-5m') {
        notice('ap-warn', 'status', 'NVDA não roda em ' + tfValue() + ' nesta tela', 'O 5m de NVDA começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo da Otimização. Nada foi executado. Use 1d aqui ou o Combo, que tem período.');
        return;
      }
      if (sel === 'mixed') { notice('ap-warn', 'status', 'Otimizando 1 par cripto', 'Fora: NVDA (Ação) — ' + EQUITY_OUT + '.'); return; }
      if (sel === 'equities') {
        notice('ap-alert', 'alert', 'Ação e ETF rodam só com 1 ativo por enquanto', 'NVDA, SPY: ' + EQUITY_OUT + '. Nada foi executado' + (page === 'optimize' ? '' : ' nem salvo') + '. A seleção foi mantida.');
        return;
      }
      notice('collect', 'status', '', COLLECT);
      if (sel === 'fail') {
        window.setTimeout(function () {
          notice('ap-alert', 'alert', 'Histórico de NVDA indisponível agora', 'Limite de requisições da Binance e nada de NVDA guardado para esta janela. Nada foi executado. Tente de novo em alguns minutos.');
        }, 900);
        return;
      }
      window.setTimeout(function () {
        if (page === 'configure') { window.location.href = 'index.html'; return; }
        notice('', '', '', '');
      }, 1200);
    });
  }

  document.querySelectorAll('[data-demo]').forEach(function (b) {
    b.addEventListener('click', function () {
      var group = b.getAttribute('data-demo');
      var value = b.getAttribute('data-value');
      press(group, b);
      if (group === 'precision') setPrecision(value);
      if (group === 'coverage') setCoverage(value);
      if (group === 'tf') setTf(value);
      if (group === 'sel' || group === 'osel') setSel(value);
    });
  });
})();
