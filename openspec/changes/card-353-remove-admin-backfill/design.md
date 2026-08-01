## Context

Card #353 remove a superfície admin `/admin/backfill` (nav + página + API admin dedicada). O serviço `ohlcv_backfill_service` continua usado por `/market/candles?full_history` e pelo scheduler opcional.

**UI impact: affected** (remoção de item de navegação e rota admin).

**Base do sistema atual:** shell autenticado de `AppNav` + workspace Monitor (`frontend/src/components/AppNav.tsx`, tokens `frontend/src/index.css` / `DESIGN.md`). Em `origin/develop`, Admin ainda lista Backfill.

## Goals / Non-Goals

**Goals:**
- Remover Backfill da navegação admin e da rota SPA.
- Remover API `/api/admin/backfill/*` e schemas exclusivos.
- Preservar ingestão histórica programática.
- Atualizar E2E de menu admin.

**Non-Goals:**
- Remover `ohlcv_backfill_service` / store / writer canônico.
- Alterar flags `BACKFILL_SCHEDULER_*` em produção.
- Restaurar UI manual de backfill.

## Decisions

1. **Remoção cirúrgica da superfície admin, não do serviço.**
2. **Remover schemas `app/schemas/backfill.py` junto com o router.**
3. **Rota `/admin/backfill` deixa de existir** (sem página dedicada).
4. **Protótipo de fidelidade:** clona shell atual e mostra delta Antes/Depois no item Admin Backfill.
5. **Remoção visual robusta:** no modo Depois, usar `hidden` + classe `is-removed` com `display: none !important` para não ser sobrescrito por `.nav-link { display:flex }`.

## Risks / Trade-offs

- [Operadores perdem UI manual] → ops via serviço/scheduler/flags.
- [Bookmark quebra] → aceito; superfície descontinuada.
- [Confundir remoção de UI com remoção do serviço] → spec/tasks deixam preservação explícita.

## Migration Plan

1. Após `Pronto para Dev`: `/opsx:apply` na branch `change-353-remove-admin-backfill`.
2. Testes focados + QA.
3. Integrar em `develop`, `./restart`, confirmar nav sem Backfill.

## Prototype

- **URL HTTP navegável:** https://dev.criptofarol.com.br/prototypes/card-353-remove-admin-backfill/
- **Caminho versionado:** `frontend/public/prototypes/card-353-remove-admin-backfill/index.html`
- **Base:** shell atual Monitor (sidebar 224px, Painel, Ambiente DEV, seções Principal/Estratégias/Carteira/Admin, header Workspace, account chip, logo `/brand/cripto-farol-logo-v6-transparent.svg`)
- **Escopo:** desktop + mobile
- **Delta:** toggle Antes (Backfill visível) / Depois (Backfill ausente)
- **Tokens:** `--bg-primary`, `--bg-elevated`, `--accent-primary`, Inter, densidade AppNav

## Prototype Validation

- **URL servida:** https://dev.criptofarol.com.br/prototypes/card-353-remove-admin-backfill/
- **Ferramenta:** Playwright Chromium (`@playwright/test`)
- **Viewports:** desktop 1440×900, mobile 390×844
- **Ações:**
  1. Abrir URL (estado padrão = Depois)
  2. Assert Backfill desktop/mobile não visível (`display:none`)
  3. Clicar Antes → Backfill visível
  4. Clicar Depois → Backfill não visível
  5. Repetir Antes/Depois no mobile
- **Asserts:**
  - `defaultMode=depois`
  - `desktopVisibleDefault=false`, `desktopDisplayDefault=none`
  - `desktopVisibleAntes=true`, `desktopVisibleDepois2=false`
  - `mobileVisibleAntes=true`, `mobileVisibleDepois=false`
  - `errors=[]`
- **Screenshots:** `/tmp/proto-validation/353-desktop-depois.png`, `353-desktop-antes.png`, `353-mobile-depois.png`, `353-mobile-antes.png`
- **Resultado:** PASS

## Design Critique

### Fidelidade
- Shell espelha `AppNav` real (logo, seções, chip DEV, header Workspace).
- Achado anterior (`hidden` + `display:flex`) corrigido e revalidado no navegador.

### Produto
- Escopo correto: só superfície admin; serviço preservado.

### UX
- Toggle Antes/Depois deixa o delta óbvio.
- No Depois, Backfill realmente some do menu.

### Acessibilidade
- `aria-pressed` no toggle; item removido com `hidden` + `aria-hidden` + fora de tab.

### Responsividade
- Desktop sidebar + mobile header/Admin validados.

### Estados
- Admin autenticado; Antes vs Depois; sem erros de página.

**Design Agent verdict: PASS**

## Open Questions

Nenhuma bloqueante. Aguardando Alan em `Aprovação de Design`.
