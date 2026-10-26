/* Card #1122 — interações do protótipo (só o delta; o clone vivo não tem React aqui). */
(function () {
  'use strict';
  var page = document.body.getAttribute('data-m22-page');
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  // ------------------------------------------------------------------ mensagens do Telegram (uma mensagem por alerta)
  var DISCLAIMER = '\n\nAviso: ferramenta educacional de apoio à decisão. Não constitui recomendação financeira nem ordem de compra/venda.';
  var NO_ORDER = 'Este alerta não envia ordem: é só o sinal da estratégia.';
  var MSG = {
    entry: '<b>Cripto Farol - Alerta Monitor</b>\n\nAtivo: NVDA (Ação · USD)\nEstratégia: Médias Móveis: Tendência em Virada\nConfiguração: Binance Ações · pregão regular de NY · ajustado por split\nTimeFrame: 1d\nLeitura anterior: Venda\nLeitura atual: Compra\nCandle: sex., 23 out. 2026 (pregão fechou às 17:00 BRT)\nValor Entrada: 182,40 USD\nStop: 173,28 USD\n' + NO_ORDER + DISCLAIMER,
    delay: '<b>Cripto Farol - Dados atrasados</b>\n\nAtivo: NVDA (Ação · USD) · Binance Ações\nÚltimo candle recebido: sex., 23 out. 2026 (1d)\nEsperado: seg., 26 out. 2026 (o pregão já fechou)\nOs sinais deste ativo ficam em espera até o dado normalizar. Você não recebe outro aviso enquanto o atraso durar.',
    cdelay: '<b>Cripto Farol - Dados atrasados</b>\n\nAtivo: BTC/USDT (Cripto · USDT) · Binance Spot\nÚltimo candle recebido: sex., 23 out. 2026 (1d)\nEsperado: sáb., 24 out. 2026 (fechou às 21:00 BRT)\nOs sinais deste ativo ficam em espera até o dado normalizar. Você não recebe outro aviso enquanto o atraso durar.',
    exit: '<b>Cripto Farol - Alerta Monitor</b>\n\nAtivo: NVDA (Ação · USD)\nEstratégia: Médias Móveis: Tendência em Virada\nConfiguração: Binance Ações · pregão regular de NY · ajustado por split\nTimeFrame: 1d\nLeitura anterior: Compra\nLeitura atual: Venda\nCandle: ter., 27 out. 2026 (pregão fechou às 17:00 BRT)\nValor Entrada: 182,40 USD\nStop: 173,28 USD\n' + NO_ORDER + DISCLAIMER,
    transition: '<b>Cripto Farol - Mudança nos alertas</b>\n\nA partir de hoje, os alertas do Telegram vêm dos seus favoritos marcados "Alertar", em cripto, ações e ETFs. Até agora você recebia os alertas do catálogo do Cripto Farol (BTC/USDT, ETH/USDT e SOL/USDT). Para continuar recebendo, salve nos seus Favoritos as estratégias que quer acompanhar e marque "Alertar". Esta mensagem não se repete.'
  };

  // estado do mercado: [tom, texto completo (cartão e title), texto curto (linha da tabela)]
  var OPEN = ['open', 'Pregão aberto · fecha 17:00 (16:00 em NY)', 'Aberto · fecha 17:00 (16:00 NY)'];
  var WEEKEND = ['closed', 'Mercado fechado · fim de semana · abre seg., 26 out., 10:30 (09:30 em NY)', 'Fechado · fim de semana · abre seg. 10:30 (09:30 NY)'];
  var HOLIDAY = ['closed', 'Mercado fechado · feriado em Nova York · abre sex., 27 nov., 11:30 (09:30 em NY)', 'Fechado · feriado em NY · abre sex. 11:30 (09:30 NY)'];
  var AFTER = ['closed', 'Mercado fechado · fora do pregão · abre hoje, 10:30 (09:30 em NY)', 'Fechado · abre hoje 10:30 (09:30 NY)'];
  var NVDA_STALE = ['stale', 'Dados atrasados · último candle sex., 23 out.; esperado seg., 26 out.', 'Dados atrasados · falta seg. 26/10'];
  var BTC_STALE = ['stale', 'Dados atrasados · último candle sex., 23 out.; esperado sáb., 24 out.', 'Dados atrasados · falta sáb. 24/10'];
  var QQQ_INSUF = ['insufficient', 'Dados insuficientes · 40 de 200 candles', 'Dados insuficientes · 40 de 200 candles'];
  var NONE = ['none', '', ''];
  function eq(a, b, c) { return { 'nvda-b': a, spy: b || a, 'nvda-s': c || b || a, qqq: NONE, 'btc-usdt': NONE }; }

  var SCEN = {
    open: {
      now: 'Leitura: seg., 26 out. 2026, 15:00 (BRT) · pregão de Nova York aberto.',
      mkt: eq(OPEN), tg: [],
      note: 'Varredura de hoje, 08:05: nenhuma mensagem. Nenhum candle de ação ou ETF fechou desde sex., 23 out. O fim de semana não conta como atraso.'
    },
    weekend: {
      now: 'Leitura: sáb., 24 out. 2026, 11:05 (BRT) · fim de semana.',
      mkt: eq(WEEKEND), tg: ['entry'],
      note: 'Varredura de sáb., 08:05: lê o pregão de sex., 23 out., já fechado. NVDA da Binance Ações mudou de Venda para Compra e gerou um alerta. NVDA da fonte antiga não mudou, então não gerou alerta. Mercado fechado não manda mensagem. Cada alerta é uma mensagem própria, e a varredura não tem limite por hora: se seis favoritos mudarem no mesmo dia, saem seis mensagens.'
    },
    'crypto-stale': {
      now: 'Leitura: dom., 25 out. 2026, 08:05 (BRT) · fim de semana; a cripto negocia 24/7.',
      mkt: (function () { var m = eq(WEEKEND); m['btc-usdt'] = BTC_STALE; return m; })(),
      tg: ['cdelay'], crypto: true,
      note: 'Varredura de dom., 08:05: falta o candle 1d de sáb., 24 out. de BTC/USDT na Binance Spot, que fechou às 21:00 BRT de sábado. Sai um aviso só, e o sinal de BTC/USDT fica em espera. Na linha de BTC/USDT, "Dados atrasados" substitui o "Sem candle válido/atual" de hoje: os dois nunca aparecem juntos. Ações e ETFs estão no fim de semana, sem atraso.'
    },
    holiday: {
      now: 'Leitura: qui., 26 nov. 2026, 11:05 (BRT) · feriado em Nova York (Ação de Graças).',
      mkt: eq(HOLIDAY), tg: [],
      note: 'Varredura de hoje, 08:05: nenhuma mensagem. Ela leu o pregão de qua., 25 nov. O feriado não conta como atraso.'
    },
    stale: {
      now: 'Leitura: ter., 27 out. 2026, 08:05 (BRT) · antes da abertura de NY.',
      mkt: eq(NVDA_STALE, AFTER, AFTER), tg: ['delay'],
      note: 'Varredura de hoje, 08:05: falta o candle de seg., 26 out. de NVDA na Binance Ações, e o calendário diz que esse pregão já fechou. Isso é atraso real, mesmo com o mercado fechado agora. Sai um aviso só. SPY e NVDA da fonte antiga leram segunda normalmente. Se o atraso continuar amanhã, nenhum aviso novo sai.'
    },
    recovery: {
      now: 'Leitura: qua., 28 out. 2026, 08:05 (BRT) · dado de NVDA normalizado.',
      mkt: eq(AFTER), tg: ['exit'], move: true,
      note: 'Os candles de segunda e terça de NVDA chegaram. O atraso fecha sem mensagem. A leitura mudou para Venda no candle de ter., 27 out., e NVDA está na carteira, então sai o alerta de saída. Nenhuma ordem é enviada.'
    },
    insufficient: {
      now: 'Leitura: seg., 26 out. 2026, 15:00 (BRT) · QQQ (ETF) com 40 pregões na Binance Ações; a estratégia usa média de 200.',
      mkt: (function () { var m = eq(OPEN); m.qqq = QQQ_INSUF; return m; })(),
      tg: [], only: 'insufficient',
      note: 'Nenhuma mensagem. QQQ entrou pelo lote com 1 estrela e sem "Alertar". Dado insuficiente não é atraso nem falha: o Monitor mostra a contagem e "Sem leitura", e nada sai no Telegram. Quando a série tiver 200 candles, a primeira leitura vira base, sem alerta.'
    },
    transition: {
      now: 'Leitura: seg., 26 out. 2026, 15:00 (BRT) · pessoa que recebia alertas do catálogo e não marcou nenhum favorito.',
      mkt: eq(OPEN), tg: ['transition'], banner: 'dated',
      note: 'Decisão de Alan: um aviso único no Telegram no dia da troca e a faixa no Monitor até a pessoa marcar um favorito, sem período de transição. Só quem recebia pelo catálogo vê a frase com a data. Depois disso, quem não marcou nada não recebe alerta de sinal.'
    },
    newuser: {
      now: 'Leitura: seg., 26 out. 2026, 15:00 (BRT) · pessoa com Telegram ligado que nunca recebeu alerta do catálogo.',
      mkt: eq(OPEN), tg: [], banner: 'plain',
      note: 'Nenhuma mensagem: o aviso da troca vai só para quem recebia pelo catálogo. A faixa aparece sem a frase com data até a pessoa marcar um favorito.'
    }
  };

  function setMkt(key, spec) {
    var tone = spec[0];
    $$('[data-m22-mkt="' + key + '"], [data-m22-mkt="' + key + '-m"]').forEach(function (el) {
      var short = el.getAttribute('data-m22-short') === '1';
      el.setAttribute('data-tone', tone);
      el.hidden = tone === 'none';
      el.setAttribute('title', spec[1]);
      $('.m22-mkt-text', el).textContent = short ? spec[2] : spec[1];
    });
    $$('[data-m22-hold="' + key + '"], [data-m22-hold="' + key + '-m"]').forEach(function (el) {
      var inRow = Boolean(el.closest('table.signals'));
      el.hidden = tone !== 'stale' && tone !== 'insufficient';
      el.setAttribute('data-tone', tone);
      if (tone === 'insufficient') el.textContent = inRow ? 'Sem sinal' : 'Sem sinal até completar o histórico';
      else el.textContent = inRow ? 'Sinal em espera' : 'Sinal em espera até o dado normalizar';
    });
  }

  var home = {};
  var reapplyFilters = null;
  function moveNvda(toExit) {
    var row = $('tr[data-m22-row="nvda-b"]');
    var detail = $('tr[data-m22-detail="nvda-b"]');
    var card = $('article[data-m22-card="nvda-b"]');
    if (!row) return;
    if (!home.row) {
      home.row = row.parentNode; home.card = card.parentNode;
      home.rowNext = detail ? detail.nextSibling : row.nextSibling; home.cardNext = card.nextSibling;
    }
    if (!toExit && row.parentNode === home.row) return;
    var exitSection = $('[data-testid="monitor-section-exit"]');
    if (toExit) {
      var tb = $('table.signals tbody', exitSection);
      tb.insertBefore(row, $('tr[data-m22-row="qqq"]', tb));
      if (detail) tb.insertBefore(detail, $('tr[data-m22-row="qqq"]', tb));
      var cards = $('.mobile-cards', exitSection);
      cards.insertBefore(card, $('article[data-m22-card="qqq"]', cards));
    } else {
      home.row.insertBefore(row, home.rowNext);
      if (detail) home.row.insertBefore(detail, home.rowNext);
      home.card.insertBefore(card, home.cardNext);
    }
    $$('.status-pill', row).concat($$('.status-pill', card)).forEach(function (pill) {
      pill.classList.toggle('hold', !toExit); pill.classList.toggle('exit', toExit);
      pill.textContent = toExit ? 'Saída / cobertura' : 'Em posição';
    });
  }

  function visible(el) { return !el.hidden && el.style.display !== 'none'; }
  function recount() {
    var hold = $$('[data-testid="monitor-section-hold"] table.signals tbody tr.head-row').filter(visible).length;
    var exit = $$('[data-testid="monitor-section-exit"] table.signals tbody tr.head-row').filter(visible).length;
    var h = $('[data-m22-meta="hold"]'); if (h) h.textContent = '(' + hold + ')';
    var e = $('[data-m22-meta="exit"]'); if (e) e.textContent = '(' + exit + ')';
    var c = $('[data-m22-count]'); if (c) c.textContent = (hold + exit) + ' resultados';
    var t = $('[data-m22-total]'); if (t) t.textContent = String(hold + exit);
    var kp = $$('.kpis .kpi .kpi-val');
    if (kp.length >= 2) { kp[0].textContent = String(hold); kp[1].textContent = String(exit); }
    // Em carteira: ativos distintos marcados (as duas NVDA contam uma vez)
    var assets = {};
    $$('table.signals tr.head-row').forEach(function (row) {
      if (row.getAttribute('data-m22-only') && row.getAttribute('data-m22-only') !== currentOnly) return;
      if (!/●/.test(($('.tag.portfolio', row) || {}).textContent || '')) return;
      var sym = row.getAttribute('data-symbol') || (($('.pair-name', row) || {}).firstChild || {}).textContent;
      assets[(sym || '').trim()] = true;
    });
    var pf = $('[data-m22-pf-count]'); if (pf) pf.textContent = String(Object.keys(assets).length);
  }

  var currentOnly = '';
  function setScenario(name) {
    var s = SCEN[name]; if (!s) return;
    document.body.setAttribute('data-scenario', name);
    currentOnly = s.only || '';
    Object.keys(s.mkt).forEach(function (k) { setMkt(k, s.mkt[k]); });
    $$('[data-m22-crypto-meta]').forEach(function (el) { el.hidden = !s.crypto; });
    $$('[data-m22-crypto-reason]').forEach(function (el) { el.hidden = !s.crypto; });
    moveNvda(Boolean(s.move));
    var banner = $('[data-m22-banner]');
    if (banner) {
      banner.hidden = !s.banner;
      var dated = $('[data-m22-banner-dated]', banner); if (dated) dated.hidden = s.banner !== 'dated';
    }
    var now = $('[data-m22-now]'); if (now) now.textContent = s.now;
    var note = $('[data-m22-tg-note]'); if (note) note.textContent = s.note;
    var box = $('[data-m22-tg]');
    if (box) {
      box.innerHTML = '';
      s.tg.forEach(function (k) {
        var pre = document.createElement('pre');
        pre.className = 'm22-tg-msg';
        pre.setAttribute('aria-label', 'Mensagem do Telegram');
        pre.innerHTML = MSG[k];
        box.appendChild(pre);
      });
    }
    $$('[data-set-scenario]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-set-scenario') === name)); });
    if (typeof reapplyFilters === 'function') reapplyFilters(); else recount();
  }

  // ------------------------------------------------------------------ Monitor
  function initMonitor() {
    $$('[data-set-scenario]').forEach(function (b) {
      b.addEventListener('click', function () { setScenario(b.getAttribute('data-set-scenario')); });
    });
    // abrir/fechar linha: ação/ETF (delta) e BTC (detalhe copiado da captura com a linha aberta)
    $$('table.signals tr.head-row').forEach(function (row) {
      var toggle = $('.row-toggle', row);
      var key = row.getAttribute('data-m22-row');
      var tid = row.getAttribute('data-testid') || '';
      var tpl = !key && tid === 'monitor-row-btc-usdt' ? $('template[data-m22-detail-tpl="btc-usdt"]') : null;
      if (!key && !tpl) return;
      var open = function () {
        var detail = key ? $('tr[data-m22-detail="' + key + '"]') : row.nextElementSibling && row.nextElementSibling.classList.contains('detail-row') ? row.nextElementSibling : null;
        if (!detail && tpl) {
          detail = tpl.content.firstElementChild.cloneNode(true);
          detail.hidden = true;
          row.parentNode.insertBefore(detail, row.nextSibling);
          bindPortfolio(detail);
          bindOff(detail);
        }
        if (!detail) return;
        var willOpen = detail.hidden;
        detail.hidden = !willOpen;
        detail.setAttribute('aria-hidden', String(!willOpen));
        row.classList.toggle('expanded', willOpen);
        row.setAttribute('aria-expanded', String(willOpen));
        toggle.classList.toggle('open', willOpen);
        toggle.setAttribute('aria-expanded', String(willOpen));
      };
      toggle.addEventListener('click', function (ev) { ev.stopPropagation(); open(); });
      row.addEventListener('click', function (ev) { if (!ev.target.closest('button')) open(); });
    });
    bindPortfolio(document);
    var segIn = $('[data-testid="monitor-filter-in-portfolio"]');
    var segAll = $('[data-testid="monitor-filter-all"]');
    var listFilter = 'in';
    function applyFilters() {
      var tf = ($('[data-testid="monitor-filter-timeframe"]') || {}).value || 'all';
      $$('table.signals tr.head-row').forEach(function (row) {
        var rowTf = row.getAttribute('data-tf') || ($('.pair-tf', row) || {}).textContent;
        var inPf = /●/.test(($('.tag.portfolio', row) || {}).textContent || '');
        var only = row.getAttribute('data-m22-only');
        var show = (listFilter === 'all' || inPf) && (tf === 'all' || rowTf === tf) && (!only || only === currentOnly);
        row.style.display = show ? '' : 'none';
        var d = row.nextElementSibling;
        if (d && d.classList.contains('detail-row') && !show) d.hidden = true;
        var card = $('article[data-m22-card="' + row.getAttribute('data-m22-row') + '"]');
        if (card) card.style.display = show ? '' : 'none';
      });
      recount();
    }
    [segIn, segAll].forEach(function (b) {
      if (!b) return;
      b.addEventListener('click', function () {
        listFilter = b === segAll ? 'all' : 'in';
        segIn.classList.toggle('on', listFilter === 'in');
        segAll.classList.toggle('on', listFilter === 'all');
        applyFilters();
      });
    });
    var tfSel = $('[data-testid="monitor-filter-timeframe"]');
    if (tfSel) tfSel.addEventListener('change', applyFilters);
    reapplyFilters = applyFilters;
    bindOff(document);
    setScenario('open');
  }

  // botões indisponíveis da fonte antiga: focáveis, sem ação; o motivo está em texto visível
  function bindOff(root) {
    $$('[data-m22-off]', root).forEach(function (b) {
      if (b.__m22off) return; b.__m22off = true;
      b.addEventListener('click', function (ev) { ev.preventDefault(); ev.stopPropagation(); });
    });
  }

  function bindPortfolio(root) {
    $$('[data-testid^="portfolio-toggle-"]', root).forEach(function (btn) {
      if (btn.__m22) return; btn.__m22 = true;
      var key = btn.getAttribute('data-testid').replace('portfolio-toggle-', '');
      btn.addEventListener('click', function (ev) {
        ev.stopPropagation();
        var on = btn.getAttribute('aria-pressed') !== 'true';
        var sym = key === 'nvda-b' || key === 'nvda-s' ? ['nvda-b', 'nvda-s'] : [key];
        sym.forEach(function (k) {
          $$('[data-testid="portfolio-toggle-' + k + '"]').forEach(function (b) {
            b.setAttribute('aria-pressed', String(on));
            b.textContent = on ? 'No portfólio' : 'Fora do portfólio';
          });
          var row = $('tr[data-m22-row="' + k + '"]') || $('[data-testid="monitor-row-' + k + '"]');
          var tag = row && $('.tag.portfolio', row);
          if (tag) tag.textContent = on ? '● Carteira' : '○ Carteira';
        });
        if (typeof reapplyFilters === 'function') reapplyFilters();
      });
    });
  }

  // ------------------------------------------------------------------ Favoritos
  var TG_ON = ['border-emerald-400', 'bg-emerald-400/15', 'text-emerald-600'];
  var TG_OFF = ['border-zinc-200', 'bg-zinc-50', 'text-zinc-400', 'hover:text-emerald-600'];
  var ST_ON = ['border-amber-400', 'bg-amber-400/15', 'text-amber-500'];
  var ST_OFF = ['border-zinc-200', 'bg-zinc-50', 'text-zinc-400', 'hover:text-amber-500'];
  function swap(el, on, onCls, offCls) {
    // tira primeiro as classes do outro estado, para nunca juntar cinza e cor no mesmo botão
    (on ? offCls : onCls).forEach(function (c) { el.classList.remove(c); });
    (on ? onCls : offCls).forEach(function (c) { el.classList.add(c); });
  }
  function favId(el) {
    var host = el.closest('[data-favorite-id]');
    return host ? host.getAttribute('data-favorite-id') : '';
  }
  function favSym(id) {
    var host = $('[data-favorite-id="' + id + '"] strong');
    return host ? host.textContent : '';
  }
  var outOfPortfolio = {};
  function syncPfWarn() {
    $$('[data-m22-pfwarn]').forEach(function (w) {
      var id = w.getAttribute('data-m22-pfwarn');
      var t = $('[data-favorite-id="' + id + '"] .telegram-toggle');
      var on = Boolean(t) && t.getAttribute('aria-pressed') === 'true';
      w.hidden = !(outOfPortfolio[id] && on);
    });
  }
  function initFavorites() {
    var live = $('[data-m22-live]');
    // "Alertar" do dono: coluna (≥ 1280 px), célula Ações (1024–1279 px) e cartão do celular, sincronizados
    $$('.telegram-toggle, .m22-act-alertar').forEach(function (b) {
      b.addEventListener('click', function (ev) {
        ev.stopPropagation();
        var id = favId(b);
        var on = b.getAttribute('aria-pressed') !== 'true';
        var label = 'Alertar no Telegram: ' + (on ? 'ligado' : 'desligado');
        $$('[data-favorite-id="' + id + '"] .telegram-toggle, [data-favorite-id="' + id + '"] .m22-act-alertar').forEach(function (x) {
          x.setAttribute('aria-pressed', String(on));
          x.setAttribute('title', label);
          x.setAttribute('aria-label', label);
          if (x.classList.contains('telegram-toggle')) swap(x, on, TG_ON, TG_OFF);
          var svg = $('svg', x);
          if (svg) svg.setAttribute('fill', on ? 'currentColor' : 'none');
          var txt = $('.m22-tg-text', x);
          if (txt) txt.textContent = x.classList.contains('m22-tg-mob') ? 'Alertar: ' + (on ? 'on' : 'off') : (on ? 'On' : 'Off');
        });
        syncPfWarn();
        if (live) live.textContent = 'Alertar no Telegram ' + (on ? 'ligado' : 'desligado') + ' para ' + favSym(id) + '.';
      });
    });
    $$('.stars-cell button, .fav-mobile-stars [aria-label="Prioridade por estrelas"] button').forEach(function (b) {
      b.addEventListener('click', function (ev) {
        ev.stopPropagation();
        var id = favId(b);
        var n = parseInt(b.getAttribute('title'), 10);
        var group = $$('[data-favorite-id="' + id + '"] [aria-label="Prioridade por estrelas"] button');
        var current = group.filter(function (s) { return s.getAttribute('aria-pressed') === 'true'; }).length / Math.max(1, group.length / 3);
        var target = current === n ? 0 : n;
        group.forEach(function (s) {
          var k = parseInt(s.getAttribute('title'), 10);
          s.setAttribute('aria-pressed', String(k <= target));
          swap(s, k <= target, ST_ON, ST_OFF);
        });
        if (live) live.textContent = favSym(id) + ': ' + (target ? target + (target > 1 ? ' estrelas' : ' estrela') : 'sem estrela') + '.';
      });
    });
    var NOW = {
      owner: 'Vendo como Alan, dono dos favoritos: "Alertar" em cada linha, inclusive de ação e ETF.',
      nopf: 'SPY saiu da carteira no Monitor. O "Alertar" de SPY continua ligado, mas a linha avisa que, fora da carteira, ação e ETF não recebem alerta.',
      catalog: 'Vendo como uma pessoa sem favorito próprio: a lista é a vitrine do catálogo, sem "Alertar".'
    };
    $$('[data-set-view]').forEach(function (b) {
      b.addEventListener('click', function () {
        var v = b.getAttribute('data-set-view');
        document.body.setAttribute('data-view', v);
        $$('[data-set-view]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        var banner = $('[data-m22-fav-banner]'); if (banner) banner.hidden = v !== 'catalog';
        $$('.m22-cat-none').forEach(function (s) { s.hidden = v !== 'catalog'; });
        outOfPortfolio = v === 'nopf' ? { '105': true } : {};
        syncPfWarn();
        var now = $('[data-m22-now]'); if (now) now.textContent = NOW[v];
      });
    });
  }

  // ------------------------------------------------------------------ Resultado: Salvar nos Favoritos (ação/ETF)
  function initResults() {
    var modal = $('[data-m22-modal]');
    var opener = $('[data-testid="save-favorite-button"]');
    if (!modal || !opener) return;
    var dup = $('[data-m22-dup]', modal);
    var ok = $('[data-m22-ok]', modal);
    var save = $('[data-m22-save]', modal);
    function focusables() {
      return $$('a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), summary, [tabindex]:not([tabindex="-1"])', modal)
        .filter(function (el) { return el.offsetParent !== null; });
    }
    function close() {
      if (modal.hidden) return;
      modal.hidden = true;
      opener.focus();
    }
    opener.addEventListener('click', function () {
      dup.hidden = true; ok.hidden = true; save.disabled = false;
      modal.hidden = false;
      var input = $('input', modal); if (input) input.focus();
    });
    $('[data-m22-close]', modal).addEventListener('click', close);
    // Esc fecha sempre (o foco pode estar em qualquer lugar); Tab fica preso no modal
    document.addEventListener('keydown', function (ev) {
      if (modal.hidden) return;
      if (ev.key === 'Escape') { ev.preventDefault(); close(); return; }
      if (ev.key !== 'Tab') return;
      var f = focusables(); if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      var inside = modal.contains(document.activeElement);
      if (ev.shiftKey && (document.activeElement === first || !inside)) { ev.preventDefault(); last.focus(); }
      else if (!ev.shiftKey && (document.activeElement === last || !inside)) { ev.preventDefault(); first.focus(); }
    });
    save.addEventListener('click', function () {
      var isDup = document.body.getAttribute('data-dup') === 'yes';
      dup.hidden = !isDup; ok.hidden = isDup;
      if (!isDup) {
        // o foco vai para "Ver em Favoritos" antes de o Salvar ficar indisponível
        $('[data-m22-ok-link]', modal).focus();
        save.disabled = true;
      }
    });
    $$('[data-set-dup]').forEach(function (b) {
      b.addEventListener('click', function () {
        document.body.setAttribute('data-dup', b.getAttribute('data-set-dup'));
        $$('[data-set-dup]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      });
    });
  }

  if (page === 'monitor') initMonitor();
  if (page === 'favorites') initFavorites();
  if (page === 'results') initResults();
})();
