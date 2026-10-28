/* Card #1123 — comportamento do delta no protótipo (sem React, sem rede). Prefixo b23. */
(function () {
  'use strict';

  const dataEl = document.getElementById('b23-data');
  if (!dataEl) return;
  const DATA = JSON.parse(dataEl.textContent);
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  function td(value) {
    const cell = document.createElement('td');
    const text = value == null ? '' : String(value);
    cell.textContent = text;
    if (text === 'não registrado') cell.dataset.state = 'nao';
    else if (text.indexOf('(deduzido)') >= 0) cell.dataset.state = 'deduzido';
    return cell;
  }

  function fillSheet(table, header, rows) {
    table.textContent = '';
    const thead = document.createElement('thead');
    const tr = document.createElement('tr');
    header.forEach((h) => { const th = document.createElement('th'); th.scope = 'col'; th.textContent = h; tr.appendChild(th); });
    thead.appendChild(tr);
    const tbody = document.createElement('tbody');
    rows.forEach((row) => { const r = document.createElement('tr'); row.forEach((v) => r.appendChild(td(v))); tbody.appendChild(r); });
    table.appendChild(thead);
    table.appendChild(tbody);
  }

  function wireExport(button, file, detail) {
    const status = $('[data-b23-export-status]');
    if (!button || !status) return;
    button.addEventListener('click', () => {
      status.textContent = 'Planilha baixada: ' + file + ' · ' + detail();
    });
  }

  // ------------------------------------------------------------------ diálogo "Escolher referência" (resultado, favorito e Decidir)
  function wireDialog(opener, currentId, onUse) {
    const overlay = $('[data-b23-dialog]');
    if (!overlay || !opener) return;
    const dialog = $('[role="dialog"]', overlay);
    const q = $('[data-b23-q]', overlay);
    let filter = 'all';
    let lastFocus = null;

    function applyFilter() {
      const text = (q.value || '').trim().toLowerCase();
      let visible = 0;
      $$('.b23-opt', overlay).forEach((li) => {
        const ok = (filter === 'all' || li.dataset.b23Cls === filter) && (!text || li.dataset.b23Text.indexOf(text) >= 0);
        li.hidden = !ok;
        if (ok) visible += 1;
      });
      $('[data-b23-empty]', overlay).hidden = visible > 0;
    }

    function focusables() {
      const visible = (el) => !el.disabled && !el.closest('[hidden]');
      const radios = $$('input[name="b23-ref"]', dialog).filter(visible);
      const radio = radios.find((r) => r.checked) || radios[0];
      const items = $$('button, input[type="search"]', dialog).filter(visible);
      if (radio) items.push(radio);
      return items.sort((a, b) => (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1));
    }

    function openDialog(trigger) {
      lastFocus = trigger || opener;
      const checked = $('input[value="' + currentId() + '"]', overlay);
      if (checked) checked.checked = true;
      overlay.hidden = false;
      document.body.style.overflow = 'hidden';
      q.focus();
    }

    function closeDialog() {
      overlay.hidden = true;
      document.body.style.overflow = '';
      (lastFocus || opener).focus();
    }

    opener.addEventListener('click', () => openDialog(opener));
    $$('[data-b23-close]', overlay).forEach((b) => b.addEventListener('click', closeDialog));
    overlay.addEventListener('click', (e) => { if (e.target === overlay) closeDialog(); });
    q.addEventListener('input', applyFilter);
    $$('[data-b23-f]', overlay).forEach((b) => b.addEventListener('click', () => {
      filter = b.dataset.b23F;
      $$('[data-b23-f]', overlay).forEach((x) => x.setAttribute('aria-pressed', x === b ? 'true' : 'false'));
      applyFilter();
    }));
    document.addEventListener('keydown', (e) => {
      if (overlay.hidden) return;
      if (e.key === 'Escape') { e.preventDefault(); closeDialog(); return; }
      if (e.key === 'Tab') {
        const items = focusables();
        if (!items.length) return;
        const first = items[0];
        const last = items[items.length - 1];
        if (!dialog.contains(document.activeElement)) { e.preventDefault(); first.focus(); return; }
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    $('[data-b23-use]', overlay).addEventListener('click', () => {
      const picked = $('input[name="b23-ref"]:checked', overlay);
      closeDialog();
      if (picked) onUse(picked.value);
    });
  }

  // ------------------------------------------------------------------ resultado e favorito
  const block = $('[data-testid="benchmark-comparison"]');
  if (block) {
    const refs = DATA.refs;
    let current = refs.find((r) => r.id === DATA.initial);
    let recWhen = DATA.initialRec;
    let state = current.state;
    const set = (key, value) => { const el = $('[data-b23="' + key + '"]', block); if (el) el.textContent = value; };
    const show = (key, on) => { const el = $('[data-b23="' + key + '"]', block); if (el) el.hidden = !on; };

    function render() {
      block.dataset.b23State = state;
      block.dataset.b23Partial = current.partial ? 'true' : 'false';
      const label = current.own ? current.symbol + ' (próprio ativo)' : current.symbol;
      set('ref-name', state === 'unrecorded' ? 'Próprio ativo (' + DATA.strategy + ')' : label);
      set('ref-cls', current.cls);
      set('ref-cur', current.cur);
      set('r-label', current.symbol);
      show('insuf', state === 'insufficient');
      show('unrec', state === 'unrecorded');
      block.dataset.b23Reason = state === 'insufficient' ? (current.code || '') : '';
      if (state === 'insufficient') { set('insuf-reason', current.reason); set('insuf-help', current.help || ''); }
      if (state === 'valid') { // números só da comparação gravada; nada durante gravando/coletando
        set('s-ret', current.sRet); set('s-cagr', current.sCagr);
        set('r-ret', current.rRet); set('r-cagr', current.rCagr);
        set('d-cagr', current.dCagr);
        $('[data-b23="d-cagr"]', block).dataset.tone = current.dTone;
        $('[data-b23="r-ret"]', block).dataset.tone = current.rRet.charAt(0) === '+' ? 'up' : 'down';
        set('d-note', current.dTone === 'up' ? 'a favor da estratégia' : 'a favor da referência');
        set('common', current.common);
        set('left', current.left);
      } else {
        ['s-ret', 's-cagr', 'r-ret', 'r-cagr', 'd-cagr', 'common', 'left'].forEach((k) => set(k, ''));
      }
      show('price', !!current.price && state === 'valid');
      show('fx', !!current.fx && state === 'valid');
      set('fx-pair', DATA.strategy + ' em ' + DATA.stratCur + ', ' + current.symbol + ' em ' + current.cur);
      set('rec-when', recWhen);
      set('sample', current.sample);
      renderSheet();
    }

    function renderSheet() {
      const table = $('[data-b23-sheet]');
      if (!table || state === 'collecting') return; // a planilha só reflete a comparação gravada
      const valid = state === 'valid';
      const unrec = state === 'unrecorded';
      const ctx = DATA.ctx;
      const rows = Object.keys(ctx).map((k) => [k, ctx[k], 'registrado']);
      const nr = 'não registrado';
      const add = (k, v, st) => rows.push([k, v, st || 'registrado']);
      add('Referência', unrec ? 'Próprio ativo' : (current.own ? current.symbol + ' (próprio ativo)' : current.symbol + ' · ' + current.cls + ' · ' + current.cur));
      add('Tipo de retorno da referência', !valid ? '' : (current.price ? 'Retorno de preço, sem dividendos' : 'Retorno de preço'));
      add('Período comum', valid ? current.common : '');
      add('Fora do período comum', valid ? current.left : '');
      add('Retorno da estratégia no período comum', valid ? current.sRet : '');
      add('CAGR da estratégia no período comum', valid ? current.sCagr : '');
      add('Retorno da referência', valid ? current.rRet : '');
      add('CAGR da referência', valid ? current.rCagr : '');
      add('Diferença de CAGR (p.p.)', valid ? current.dCagr.replace(' p.p.', '') : '');
      add('Situação da comparação', unrec ? nr : (valid ? 'Válida' : 'Histórico insuficiente: ' + current.reason), unrec ? nr : 'registrado');
      add('Aviso de moeda', current.fx && valid ? 'USDT tratado como USD, sem conversão. A comparação é só em percentual.' : '');
      add('Versão da amostra da referência', unrec ? nr : current.sample, unrec ? nr : 'registrado');
      add('Comparação gravada em', unrec ? nr : recWhen.replace(/^.* em /, '').replace(/\.$/, ''), unrec ? nr : 'registrado');
      fillSheet(table, ['Campo', 'Valor', 'Estado'], rows);
    }

    // ---- diálogo (o mesmo do Decidir)
    const opener = $('[data-b23-open]', block);
    wireDialog(opener, () => current.id, (id) => { if (id !== current.id) choose(id); });

    function choose(id) {
      const next = refs.find((r) => r.id === id);
      if (!next) return;
      current = next;
      const live = $('[data-b23="live"]', block);
      const wait = next.collectMs || next.saveMs || 0;
      state = 'collecting';
      live.innerHTML = '<span class="b23-spin" aria-hidden="true"></span><span></span>';
      live.lastChild.textContent = next.collectMs
        ? 'Coletando histórico de ' + next.symbol + ' na Binance…'
        : 'Gravando a comparação com ' + next.symbol + '…';
      render();
      window.setTimeout(() => {
        state = next.state;
        recWhen = DATA.recNew;
        live.textContent = '';
        const msg = document.createElement('span');
        msg.textContent = next.state === 'valid'
          ? 'Referência trocada para ' + (next.own ? 'o próprio ativo' : next.symbol) + ' e gravada.'
          : 'Referência ' + next.symbol + ' gravada sem comparação: ' + (next.code === 'short_overlap' ? 'período comum curto.' : 'histórico insuficiente.');
        live.appendChild(msg);
        render();
      }, wait);
    }

    function failCollect(id) {
      const target = refs.find((r) => r.id === id);
      const before = current;
      const beforeState = state;
      const live = $('[data-b23="live"]', block);
      state = 'collecting';
      current = target;
      live.innerHTML = '<span class="b23-spin" aria-hidden="true"></span><span></span>';
      live.lastChild.textContent = 'Coletando histórico de ' + target.symbol + ' na Binance…';
      render();
      window.setTimeout(() => {
        current = before;
        state = beforeState;
        live.textContent = '';
        const box = document.createElement('div');
        box.className = 'b23-fail';
        box.setAttribute('role', 'alert');
        const msg = document.createElement('p');
        msg.textContent = 'Não foi possível coletar o histórico de ' + target.symbol + ' na Binance (tempo esgotado). Nada foi gravado: a referência continua ' + (before.own ? 'o próprio ativo' : before.symbol) + '.';
        const retry = document.createElement('button');
        retry.type = 'button';
        retry.className = 'b23-btn';
        retry.textContent = 'Tentar de novo';
        retry.setAttribute('data-testid', 'benchmark-retry');
        retry.addEventListener('click', () => choose(id));
        box.appendChild(msg);
        box.appendChild(retry);
        live.appendChild(box);
        render();
      }, 1200);
    }
    const demoShort = $('[data-b23-demo-short]');
    if (demoShort) demoShort.addEventListener('click', () => { block.scrollIntoView({ block: 'start' }); choose('PENGU'); });
    const demoFail = $('[data-b23-demo-fail]');
    if (demoFail) demoFail.addEventListener('click', () => { block.scrollIntoView({ block: 'start' }); failCollect('QQQ'); });

    const ownBtn = $('[data-b23-own]', block);
    if (ownBtn) ownBtn.addEventListener('click', () => choose('own'));

    const demoUnrec = $('[data-b23-demo-unrec]');
    if (demoUnrec) demoUnrec.addEventListener('click', () => {
      const on = demoUnrec.getAttribute('aria-pressed') !== 'true';
      demoUnrec.setAttribute('aria-pressed', on ? 'true' : 'false');
      demoUnrec.textContent = on ? 'Voltar ao favorito com SPY gravada' : 'Ver como favorito sem comparação registrada';
      current = refs.find((r) => r.id === (on ? 'own' : DATA.initial));
      state = on ? 'unrecorded' : current.state;
      recWhen = DATA.initialRec;
      $('[data-b23="live"]', block).textContent = '';
      render();
      block.scrollIntoView({ block: 'start' });
    });

    // ---- planilha de trades
    const tradesBtn = $$('button').find((b) => /Exportar para Excel/.test(b.textContent));
    if (tradesBtn) tradesBtn.setAttribute('data-testid', 'export-trades');
    wireExport(tradesBtn, DATA.file, () => 'abas Trades, Contexto e Legenda · referência ' +
      (state === 'unrecorded' ? 'não registrada' : (current.own ? 'próprio ativo' : current.symbol)));

    render();
  }

  // ------------------------------------------------------------------ Decidir: coluna extra com outra referência (a ordem não muda)
  if (DATA.page === 'discovery') {
    const strip = $('[data-testid="discovery-extra-ref"]');
    const opener = $('[data-b23-open]', strip);
    const live = $('[data-b23x="live"]', strip);
    const th = $('[data-b23-xcol]');
    const cellsEl = $$('[data-b23-xcell]');
    const refs = DATA.refs;
    const KEY = 'b23-disc-ref:' + DATA.sweep;
    let current = refs[0]; // gravada (ou nenhuma)
    let pending = null; // em coleta/cálculo
    let progress = 0;
    let recWhen = '';
    const x = (k) => $('[data-b23x="' + k + '"]', strip);
    const store = {
      get() { try { return window.sessionStorage.getItem(KEY); } catch (e) { return null; } },
      set(v) { try { if (v) window.sessionStorage.setItem(KEY, v); else window.sessionStorage.removeItem(KEY); } catch (e) { /* sem armazenamento */ } },
    };
    const ICON_WARN = '<svg class="b23-ic" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>';

    function el(tag, cls, text) {
      const e = document.createElement(tag);
      if (cls) e.className = cls;
      if (text != null) e.textContent = text;
      return e;
    }

    function fillCell(cell, ref, busy) {
      cell.textContent = '';
      const rid = cell.dataset.b23Xcell;
      const box = el('div', 'b23-xc');
      if (busy) {
        cell.dataset.b23Xstate = 'busy';
        box.appendChild(el('span', 'b23-xc-busy', 'Calculando…'));
        cell.appendChild(box);
        return;
      }
      const v = ref.cells[rid];
      cell.dataset.b23Xstate = v.state === 'valid' ? 'valid' : v.code;
      if (v.state === 'valid') {
        const b = el('b', null, v.d);
        b.dataset.tone = v.tone;
        box.appendChild(b);
        box.appendChild(el('span', null, ref.symbol + ' ' + v.rCagr + ' a.a.'));
        const per = el('span', 'b23-xc-dim');
        per.appendChild(el('span', 'sr-only', 'Período comum '));
        per.appendChild(document.createTextNode(v.common));
        box.appendChild(per);
        if (v.fx) {
          const w = el('span', 'b23-xc-warn');
          w.dataset.b23Fx = '';
          w.innerHTML = ICON_WARN;
          w.appendChild(el('span', null, 'USDT tratado como USD'));
          box.appendChild(w);
        }
      } else {
        box.classList.add('b23-xc-off');
        box.appendChild(el('strong', null, 'Sem comparação'));
        box.appendChild(el('span', null, v.reason));
      }
      cell.appendChild(box);
    }

    function render() {
      const shown = pending || current;
      const on = !shown.own;
      th.hidden = !on;
      $('[data-b23x="th"]', th).textContent = 'Contra ' + shown.symbol;
      th.setAttribute('aria-label', 'Contra ' + shown.symbol + ' (diferença de CAGR no período comum; não muda a ordem)');
      cellsEl.forEach((cell, i) => {
        cell.hidden = !on;
        cell.dataset.label = 'Contra ' + shown.symbol;
        if (on) fillCell(cell, shown, !!pending && i >= progress);
        else cell.textContent = '';
      });
      strip.dataset.b23Xstate = pending ? 'busy' : (on ? 'done' : 'none');
      x('name').textContent = on ? shown.symbol : 'Nenhuma';
      x('meta').hidden = !on;
      if (on) { x('cls').textContent = shown.cls; x('cur').textContent = shown.cur; }
      x('price').hidden = !(on && shown.price);
      x('btn').textContent = on ? 'Trocar referência' : 'Comparar com outra referência';
      x('text').textContent = on
        ? 'Diferença de CAGR de cada candidato contra ' + shown.symbol + ' no período comum. A coluna não muda a ordem, o rank global nem a elegibilidade.'
        : 'Compare cada candidato com outra referência, como SPY, numa coluna a mais. A ordem e o rank global não mudam.';
      const done = on && !pending;
      const sum = x('sum');
      sum.hidden = !done;
      x('fx').hidden = true;
      x('rec').hidden = !done;
      if (done) {
        const vals = DATA.cands.map((rid) => shown.cells[rid]);
        const ok = vals.filter((v) => v.state === 'valid').length;
        const shortN = vals.filter((v) => v.code === 'short_overlap').length;
        const noneN = vals.filter((v) => v.code === 'no_overlap').length;
        if (shown.none) sum.textContent = shown.none;
        else {
          const parts = [];
          if (shortN) parts.push(shortN + ' sem comparação (período comum curto)');
          if (noneN) parts.push(noneN + ' sem comparação (sem período comum)');
          sum.textContent = ok + ' de ' + vals.length + ' candidatos com comparação' + (parts.length ? '; ' + parts.join('; ') : '') + '.';
        }
        x('fx').hidden = !vals.some((v) => v.fx);
        x('rec-text').textContent = 'Gravada nesta varredura para você em ' + recWhen + '. Amostra da referência: ' + shown.sample + '. Abrir, recarregar ou exportar de novo não recalcula.';
      }
      renderSheet();
    }

    function renderSheet() {
      const table = $('[data-b23-sheet]');
      if (!table || pending) return;
      const base = Object.keys(DATA.rows[0]);
      const on = !current.own;
      const header = on ? base.concat(DATA.extra) : base;
      const rows = DATA.rows.map((r, i) => {
        const out = base.map((h) => r[h]);
        if (!on) return out;
        const v = current.cells[DATA.cands[i]];
        const ok = v.state === 'valid';
        return out.concat([
          current.symbol + ' · ' + current.cls + ' · ' + current.cur,
          ok ? (current.price ? 'Retorno de preço, sem dividendos' : 'Retorno de preço') : '',
          ok ? v.common : '', ok ? v.left : '', ok ? v.sRet : '', ok ? v.sCagr : '', ok ? v.rRet : '', ok ? v.rCagr : '',
          ok ? v.d.replace(' p.p.', '') : '',
          ok ? 'Válida' : 'Histórico insuficiente: ' + v.long,
          ok && v.fx ? 'USDT tratado como USD, sem conversão. A comparação é só em percentual.' : '',
          current.sample, recWhen,
        ]);
      });
      fillSheet(table, header, rows);
    }

    function say(text) {
      live.textContent = '';
      live.appendChild(el('span', null, text));
    }

    function busy(text) {
      live.innerHTML = '<span class="b23-spin" aria-hidden="true"></span><span></span>';
      live.lastChild.textContent = text;
    }

    function compute(next, after) {
      pending = next;
      progress = 0;
      const n = DATA.cands.length;
      const step = Math.max(120, Math.round((next.computeMs || 600) / n));
      busy('Calculando contra ' + next.symbol + ': 0 de ' + n + ' candidatos…');
      render();
      const tick = () => {
        progress += 1;
        if (progress < n) {
          busy('Calculando contra ' + next.symbol + ': ' + progress + ' de ' + n + ' candidatos…');
          render();
          window.setTimeout(tick, step);
          return;
        }
        pending = null;
        current = next;
        recWhen = DATA.recWhen;
        store.set(next.id);
        say('Coluna Contra ' + next.symbol + ' gravada nesta varredura. A ordem do ranking não mudou.');
        render();
        if (after) after();
      };
      window.setTimeout(tick, step);
    }

    function choose(id) {
      const next = refs.find((r) => r.id === id);
      if (!next || next.disabled) return;
      if (next.own) {
        current = next;
        pending = null;
        store.set(null);
        say('Coluna extra removida. O ranking segue igual.');
        render();
        return;
      }
      if (next.collectMs) {
        pending = next;
        progress = 0;
        busy('Coletando histórico de ' + next.symbol + ' na Binance…');
        render();
        window.setTimeout(() => compute(next), next.collectMs);
      } else compute(next);
    }

    function failCollect(id) {
      const target = refs.find((r) => r.id === id);
      const before = current;
      pending = target;
      progress = 0;
      busy('Coletando histórico de ' + target.symbol + ' na Binance…');
      render();
      window.setTimeout(() => {
        pending = null;
        current = before;
        live.textContent = '';
        const box = el('div', 'b23-fail');
        box.setAttribute('role', 'alert');
        box.appendChild(el('p', null, 'Não foi possível coletar o histórico de ' + target.symbol + ' na Binance (tempo esgotado). Nada foi gravado: ' +
          (before.own ? 'o ranking continua sem coluna extra.' : 'a coluna continua contra ' + before.symbol + '.')));
        const retry = el('button', 'b23-btn', 'Tentar de novo');
        retry.type = 'button';
        retry.setAttribute('data-testid', 'discovery-ref-retry');
        retry.addEventListener('click', () => choose(id));
        box.appendChild(retry);
        live.appendChild(box);
        render();
      }, 1200);
    }

    wireDialog(opener, () => (pending || current).id, (id) => { if (id !== (pending || current).id) choose(id); });
    const demoFail = $('[data-b23-demo-fail]');
    if (demoFail) demoFail.addEventListener('click', () => { strip.scrollIntoView({ block: 'start' }); failCollect('QQQ'); });

    const saved = store.get();
    const restored = saved && refs.find((r) => r.id === saved && !r.own && !r.disabled);
    if (restored) { current = restored; recWhen = DATA.recWhen; }
    render();

    const button = $('[data-b23-export]');
    wireExport(button, DATA.file, () => DATA.rows.length + ' candidatos do recorte, todas as páginas, na ordem do ranking · abas Ranking e Legenda' +
      (current.own ? '' : ' · colunas (extra) contra ' + current.symbol));
  }

  // ------------------------------------------------------------------ Favoritos: só planilha
  if (DATA.rows && DATA.page !== 'discovery') {
    const table = $('[data-b23-sheet]');
    const header = Object.keys(DATA.rows[0]);
    fillSheet(table, header, DATA.rows.map((r) => header.map((h) => r[h])));
    const button = DATA.page === 'favorites'
      ? $$('button.fav-secondary-action').find((b) => /Exportar/.test(b.textContent))
      : $('[data-b23-export]');
    if (button && DATA.page === 'favorites') button.setAttribute('data-testid', 'export-favorites');
    const n = DATA.rows.length;
    wireExport(button, DATA.file, () => DATA.page === 'favorites'
      ? n + ' favoritos da lista filtrada · colunas de hoje + contexto · abas Favoritos e Legenda'
      : n + ' candidatos do recorte, todas as páginas, na ordem do ranking · abas Ranking e Legenda');
  }
})();
