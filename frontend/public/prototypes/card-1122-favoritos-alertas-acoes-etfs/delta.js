/* Card #1122, rodada d2 (rework r2): comportamento só do protótipo (nada é gravado). */
(function () {
  'use strict';

  var page = document.body.getAttribute('data-m22-page');

  function say(text) {
    var nodes = document.querySelectorAll('[data-m22-status]');
    for (var i = 0; i < nodes.length; i++) nodes[i].textContent = text;
  }

  function swapView(view) {
    var own = document.querySelector('[data-m22-view="own"]');
    var tpl = document.querySelector('template[data-m22-view-tpl="catalog"]');
    if (!own || !tpl) return;
    var cat = document.querySelector('[data-m22-view="catalog"]');
    if (!cat && view === 'own') return;
    if (!cat) {
      cat = document.createElement('div');
      cat.className = 'm22-view';
      cat.setAttribute('data-m22-view', 'catalog');
      cat.appendChild(tpl.content.cloneNode(true));
      own.parentNode.insertBefore(cat, own.nextSibling);
    }
    own.hidden = view !== 'own';
    cat.hidden = view !== 'catalog';
  }

  // ------------------------------------------------------------------ Monitor
  // Estado do interruptor por favorito (vale para todas as listas e detalhes, mesmo os fora da tela).
  var alerts = {};
  // Lista em tela: filtro (pf = "Em portfólio", all = "Todos") x estado da varredura do cenário.
  var filter = 'pf';
  var state = 'base';
  var lists = {};

  function setAlert(id, on) {
    alerts[id] = on;
    var all = document.querySelectorAll('[data-m22-alert="' + id + '"]');
    for (var i = 0; i < all.length; i++) {
      all[i].setAttribute('aria-checked', on ? 'true' : 'false');
      var st = all[i].querySelector('.m22-alert-state');
      if (st) st.textContent = on ? 'ligado' : 'desligado';
    }
  }

  function syncAlerts(root) {
    var sws = root.querySelectorAll('[data-m22-alert]');
    for (var i = 0; i < sws.length; i++) {
      var id = sws[i].getAttribute('data-m22-alert');
      if (Object.prototype.hasOwnProperty.call(alerts, id)) {
        var on = alerts[id];
        sws[i].setAttribute('aria-checked', on ? 'true' : 'false');
        var st = sws[i].querySelector('.m22-alert-state');
        if (st) st.textContent = on ? 'ligado' : 'desligado';
      }
    }
  }

  function listKey() {
    if (filter === 'pf') return state === 'exit' ? 'pf-exit' : 'pf-base';
    return 'all-' + state;
  }

  function showList() {
    var own = document.querySelector('[data-m22-view="own"]');
    if (!own) return;
    var cur = own.querySelector('[data-m22-list]');
    var key = listKey();
    if (cur && cur.getAttribute('data-m22-list') === key) return;
    var next = lists[key];
    if (!next) {
      var tpl = document.querySelector('template[data-m22-list-tpl="' + key + '"]');
      if (!tpl) return;
      next = tpl.content.querySelector('[data-m22-list]').cloneNode(true);
      lists[key] = next;
    }
    if (cur) {
      lists[cur.getAttribute('data-m22-list')] = cur;
      own.replaceChild(next, cur);
    } else {
      own.appendChild(next);
    }
    syncAlerts(next);
  }

  function setFilter(f) {
    filter = f;
    showList();
  }

  function toggleDetail(row) {
    var key = (row.getAttribute('data-testid') || '').replace('monitor-row-', '');
    var tpl = document.querySelector('template[data-m22-detail-tpl="' + key + '"][data-m22-state="' + state + '"]') ||
      document.querySelector('template[data-m22-detail-tpl="' + key + '"][data-m22-state="base"]');
    if (!tpl) return;
    var next = row.nextElementSibling;
    var open = next && next.classList.contains('detail-row');
    var btn = row.querySelector('.row-toggle');
    if (open) {
      next.parentNode.removeChild(next);
    } else {
      var frag = tpl.content.cloneNode(true);
      syncAlerts(frag);
      row.parentNode.insertBefore(frag, row.nextSibling);
    }
    row.setAttribute('aria-expanded', open ? 'false' : 'true');
    row.classList.toggle('expanded', !open);
    if (btn) {
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      btn.classList.toggle('open', !open);
    }
  }

  // Cenário → linha destacada, estado da varredura e se a linha está fora da carteira (troca para "Todos").
  var SCN = {
    entry: { key: 'nvda', state: 'base', outside: true },
    exit: { key: 'spy', state: 'exit', outside: false },
    reentry: { key: 'btc-usdt', state: 'base', outside: false },
    off: { key: 'eth-usdt', state: 'base', outside: true },
    delay: { key: 'nvda', state: 'delay', outside: true },
    delay15: { key: 'nvda', state: 'delay15', outside: true }
  };

  function setScenario(name) {
    document.body.setAttribute('data-scenario', name);
    var btns = document.querySelectorAll('[data-set-scenario]');
    for (var i = 0; i < btns.length; i++) {
      btns[i].setAttribute('aria-pressed', btns[i].getAttribute('data-set-scenario') === name ? 'true' : 'false');
    }
    var scns = document.querySelectorAll('[data-m22-scn]');
    for (var j = 0; j < scns.length; j++) scns[j].hidden = scns[j].getAttribute('data-m22-scn') !== (name || 'none');
    var cfg = SCN[name];
    state = cfg ? cfg.state : 'base';
    if (cfg && cfg.outside) filter = 'all';
    showList();
    var marked = document.querySelectorAll('[data-m22-focus]');
    for (var k = 0; k < marked.length; k++) marked[k].removeAttribute('data-m22-focus');
    if (cfg) {
      var row = document.querySelector('[data-m22-view="own"] tr[data-testid="monitor-row-' + cfg.key + '"]');
      if (row) row.setAttribute('data-m22-focus', '');
      var card = document.querySelector('[data-m22-view="own"] [data-testid="monitor-card-' + cfg.key + '"]');
      if (card && card.closest('.mobile-card')) card.closest('.mobile-card').setAttribute('data-m22-focus', '');
    }
    swapView(name === 'catalog' ? 'catalog' : 'own');
    if (name === 'catalog') say('');
    var ownOnly = document.querySelectorAll('[data-m22-own-only]');
    for (var o = 0; o < ownOnly.length; o++) ownOnly[o].hidden = name === 'catalog';
    syncDated();
  }

  function syncDated() {
    var box = document.querySelector('[data-m22-dated-toggle]');
    var on = !box || box.checked;
    var dated = document.querySelectorAll('[data-m22-dated]');
    for (var i = 0; i < dated.length; i++) dated[i].hidden = !on;
  }

  // ------------------------------------------------------------------ Favoritos
  var STAR_OFF = 'border-zinc-200 bg-zinc-50 text-zinc-400 hover:text-amber-500';
  var STAR_ON = 'border-amber-400 bg-amber-400/15 text-amber-500';

  function favName(el) {
    var row = el.closest('[data-favorite-id]');
    if (!row) return '';
    var sym = row.querySelector('.sym-cell strong, .fav-mobile-card-head strong');
    var tf = row.querySelector('.tf-pill');
    var tfText = tf ? tf.textContent.trim() : '';
    if (!tfText) {
      var mm = row.querySelector('.fav-mobile-metrics span');
      tfText = mm ? mm.textContent.replace('TF', '').trim() : '';
    }
    return (sym ? sym.textContent.trim() : '') + (tfText ? ' ' + tfText : '');
  }

  function paintStars(id, tier) {
    var holders = document.querySelectorAll('[data-m22-view="own"] [data-favorite-id="' + id + '"] [aria-label="Prioridade por estrelas"]');
    for (var h = 0; h < holders.length; h++) {
      var stars = holders[h].querySelectorAll('button');
      for (var s = 0; s < stars.length; s++) {
        var on = s < tier;
        var b = stars[s];
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
        b.className = b.className.replace(on ? STAR_OFF : STAR_ON, on ? STAR_ON : STAR_OFF);
        var svg = b.querySelector('svg');
        if (svg) svg.setAttribute('fill', on ? 'currentColor' : 'none');
      }
    }
    var legends = document.querySelectorAll('[data-m22-legend="' + id + '"]');
    for (var l = 0; l < legends.length; l++) {
      legends[l].setAttribute('data-on', tier > 0 ? 'true' : 'false');
      legends[l].textContent = tier > 0 ? 'No Monitor' : 'Fora do Monitor';
    }
  }

  function clickStar(btn) {
    var holder = btn.closest('[aria-label="Prioridade por estrelas"]');
    var row = btn.closest('[data-favorite-id]');
    if (!holder || !row || !row.closest('[data-m22-view="own"]')) return;
    var stars = Array.prototype.slice.call(holder.querySelectorAll('button'));
    var n = stars.indexOf(btn) + 1;
    var current = holder.querySelectorAll('button[aria-pressed="true"]').length;
    var tier = current === n ? 0 : n;
    var id = row.getAttribute('data-favorite-id');
    paintStars(id, tier);
    var name = favName(btn);
    if (current === 0 && tier > 0) {
      say(name + ' entrou no Monitor com o alerta ligado.');
      var lg = document.querySelectorAll('[data-m22-legend="' + id + '"]');
      for (var g = 0; g < lg.length; g++) lg[g].textContent = 'No Monitor · alerta ligado';
    }
    else if (current > 0 && tier === 0) say(name + ' saiu do Monitor e não manda mais alerta.');
    else say(name + ': ' + tier + (tier === 1 ? ' estrela' : ' estrelas') + '; o alerta no Monitor fica como estava.');
  }

  // ------------------------------------------------------------------ eventos
  document.addEventListener('click', function (ev) {
    var t = ev.target;
    var sw = t.closest && t.closest('[data-m22-alert]');
    if (sw) {
      ev.preventDefault();
      ev.stopPropagation();
      var on = sw.getAttribute('aria-checked') !== 'true';
      setAlert(sw.getAttribute('data-m22-alert'), on);
      var name = sw.getAttribute('data-m22-alert-name');
      say(on ? 'Alerta de ' + name + ' ligado: entrada e saída saem no Telegram.' : 'Alerta de ' + name + ' desligado: nada sai no Telegram para esta estratégia.');
      return;
    }
    var scn = t.closest && t.closest('[data-set-scenario]');
    if (scn) { setScenario(scn.getAttribute('data-set-scenario')); return; }
    var view = t.closest && t.closest('[data-set-view]');
    if (view) {
      var v = view.getAttribute('data-set-view');
      var vb = document.querySelectorAll('[data-set-view]');
      for (var i = 0; i < vb.length; i++) vb[i].setAttribute('aria-pressed', vb[i] === view ? 'true' : 'false');
      swapView(v);
      say('');
      return;
    }
    if (t.closest && t.closest('[data-m22-dated-toggle]')) { syncDated(); return; }
    if (page === 'favorites') {
      var star = t.closest && t.closest('[aria-label="Prioridade por estrelas"] button');
      if (star) { ev.preventDefault(); clickStar(star); }
      return;
    }
    if (page === 'monitor') {
      var fb = t.closest && t.closest('[data-testid="monitor-filter-in-portfolio"], [data-testid="monitor-filter-all"]');
      if (fb && fb.closest('[data-m22-view="own"]')) {
        ev.preventDefault();
        setFilter(fb.getAttribute('data-testid') === 'monitor-filter-all' ? 'all' : 'pf');
        return;
      }
      var row = t.closest && t.closest('tr.head-row');
      if (row && !t.closest('.actions-cell')) toggleDetail(row);
    }
  }, true);

  if (page === 'monitor') setScenario('');
})();
