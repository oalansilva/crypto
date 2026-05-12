## 1. Monitor labels

- [x] 1.1 Add public Compra/Venda labels to the Monitor signal resolver without changing raw statuses.
- [x] 1.2 Update Monitor list, KPI, card, chart modal, and signal history visible copy.
- [x] 1.3 Keep technical raw states, CSS class keys, API payload names, and internal fixture statuses unchanged.

## 2. Public copy

- [x] 2.1 Update product docs that describe public Monitor signal language.
- [x] 2.2 Update public landing/onboarding prototype copy where HOLD/EXIT is still visible.

## 3. Validation

- [x] 3.1 Update affected Monitor E2E expectations to Compra/Venda.
- [x] 3.2 Run OpenSpec validation, frontend build, and focused Monitor E2E tests.

Validation note 2026-05-12:
- `openspec validate card-180-buy-sell-language --type change` passed.
- `npm --prefix frontend run build` passed.
- Focused label E2E passed: `issue-70-monitor-standardized-states`, `monitor-card-mode-and-portfolio` label case, and two `monitor-mobile-cards-timeframe` chart/label cases.
- Full touched E2E set had 21/26 passing; remaining mobile failures were reproduced on baseline `develop` for representative cases (`monitor mobile uses single cards view...`, `monitor renders exited strategies separately...`, `monitor resolves current exit signal consistently...`) and are unrelated stale expectations around hidden cards/crypto-only filtering.

Note: use `$crypto-frontend` for frontend changes and OpenSpec skills for this change flow.
