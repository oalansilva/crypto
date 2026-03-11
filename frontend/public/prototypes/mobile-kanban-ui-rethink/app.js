const pages = document.getElementById('pages');
const stageTabs = document.getElementById('stageTabs');

const detailSheet = document.getElementById('detailSheet');
const filtersSheet = document.getElementById('filtersSheet');
const menuDrawer = document.getElementById('menuDrawer');

const btnOpenFilters = document.getElementById('btnOpenFilters');
const btnMenu = document.getElementById('btnMenu');
const fab = document.getElementById('fab');

const detailId = document.getElementById('detailId');
const detailTitle = document.getElementById('detailTitle');
const detailType = document.getElementById('detailType');
const detailPriority = document.getElementById('detailPriority');
const detailStage = document.getElementById('detailStage');
const detailAssignees = document.getElementById('detailAssignees');
const detailLabels = document.getElementById('detailLabels');
const detailComments = document.getElementById('detailComments');
const detailCommentsCount = document.getElementById('detailCommentsCount');

const commentForm = document.getElementById('commentForm');
const commentInput = document.getElementById('commentInput');

function setOverlayOpen(el, open) {
  el.setAttribute('aria-hidden', open ? 'false' : 'true');
  document.documentElement.classList.toggle('no-scroll', open);
  document.body.classList.toggle('no-scroll', open);
}

function closeAllOverlays() {
  [detailSheet, filtersSheet, menuDrawer].forEach(el => setOverlayOpen(el, false));
}

function activeStageFromScroll() {
  const w = pages.clientWidth;
  const idx = Math.round(pages.scrollLeft / w);
  const stageEls = Array.from(pages.querySelectorAll('.page'));
  return stageEls[Math.max(0, Math.min(idx, stageEls.length - 1))]?.dataset.stage;
}

function setActiveTab(stage) {
  stageTabs.querySelectorAll('.tab').forEach(tab => {
    const active = tab.dataset.stage === stage;
    tab.classList.toggle('tab--active', active);
    tab.setAttribute('aria-selected', active ? 'true' : 'false');
  });

  const active = stageTabs.querySelector(`.tab[data-stage="${stage}"]`);
  if (active) active.scrollIntoView({ inline: 'center', block: 'nearest' });
}

function stageLabel(stage) {
  const map = { todo: 'To do', doing: 'Doing', review: 'Review', done: 'Done' };
  return map[stage] || stage;
}

function openDetailFromCard(card, stage) {
  detailId.textContent = card.dataset.id || '—';
  detailTitle.textContent = card.dataset.title || 'Untitled';
  detailType.textContent = card.dataset.type || 'TASK';
  detailPriority.textContent = card.dataset.priority || 'P3';
  detailStage.textContent = stageLabel(stage);

  detailAssignees.textContent = card.dataset.assignees || '—';

  // labels
  const labels = (card.dataset.labels || '').split(',').map(s => s.trim()).filter(Boolean);
  detailLabels.innerHTML = labels.length
    ? labels.map(l => `<span class="label">${escapeHtml(l)}</span>`).join('')
    : '<span class="muted">No labels</span>';

  // comments count (prototype-only)
  const n = Number(card.dataset.comments || '2');
  detailCommentsCount.textContent = String(n);

  setOverlayOpen(detailSheet, true);
  setTimeout(() => commentInput?.focus(), 120);
}

function escapeHtml(s) {
  return s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
}

// Tabs -> scroll
stageTabs.addEventListener('click', (e) => {
  const tab = e.target.closest('.tab');
  if (!tab) return;
  const stage = tab.dataset.stage;
  const page = pages.querySelector(`.page[data-stage="${stage}"]`);
  if (!page) return;
  pages.scrollTo({ left: page.offsetLeft, behavior: 'smooth' });
  setActiveTab(stage);
});

// Scroll -> tabs
let raf = null;
pages.addEventListener('scroll', () => {
  if (raf) cancelAnimationFrame(raf);
  raf = requestAnimationFrame(() => {
    const stage = activeStageFromScroll();
    if (stage) setActiveTab(stage);
  });
});

// Card -> detail
pages.querySelectorAll('.card').forEach(card => {
  card.addEventListener('click', () => {
    const stage = card.closest('.page')?.dataset.stage || activeStageFromScroll() || 'todo';
    openDetailFromCard(card, stage);
  });
});

// overlays close
[detailSheet, filtersSheet, menuDrawer].forEach(el => {
  el.addEventListener('click', (e) => {
    if (e.target.matches('[data-close]')) setOverlayOpen(el, false);
  });
});

// Filters open
btnOpenFilters?.addEventListener('click', () => {
  setOverlayOpen(filtersSheet, true);
});

// Menu open
btnMenu?.addEventListener('click', () => {
  setOverlayOpen(menuDrawer, true);
});

// FAB behavior (prototype)
fab?.addEventListener('click', () => {
  const stage = activeStageFromScroll() || 'todo';
  alert(`Prototype: create new item in stage "${stageLabel(stage)}" (FAB)`);
});

// comment composer (prototype)
commentForm?.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = commentInput.value.trim();
  if (!text) return;

  const li = document.createElement('li');
  li.className = 'comment';
  li.innerHTML = `
    <div class="comment__meta"><span class="who">@you</span><span class="when">just now</span></div>
    <div class="comment__body"></div>
  `;
  li.querySelector('.comment__body').textContent = text;
  detailComments.appendChild(li);
  commentInput.value = '';

  detailCommentsCount.textContent = String(detailComments.querySelectorAll('li').length);
  detailComments.parentElement?.scrollIntoView({ block: 'end', behavior: 'smooth' });
});

// Escape closes any overlay
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeAllOverlays();
});

// initial
setActiveTab(activeStageFromScroll() || 'todo');
