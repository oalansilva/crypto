## Runtime reconciliation note (2026-03-12)

- Runtime/Kanban is the operational source of truth for this change.
- Current gate in runtime: **Homologation** (`QA=approved` after PASS at 2026-03-12 10:56 UTC). This OpenSpec artifact was reconciled to match the runtime/Kanban state.
- QA rerun note (2026-03-12 DEV): wallet shell/header and page hierarchy were adjusted to more closely match the approved prototype. New DEV evidence: `frontend/qa_artifacts/playwright/improve-wallet-screen/dev-check-{desktop,mobile}.png`. Runtime should remain in **QA** for visual revalidation.
- QA blocker recheck (2026-03-12): **cleared**. Both `/prototypes/improve-wallet-screen/` and `/prototypes/improve-wallet-screen/index.html` now return the prototype HTML on `127.0.0.1:5173` and `72.60.150.140:5173`.
- QA revalidation 2026-03-12: **failed for visual fidelity**. `/external/balances` still diverges materially from the approved prototype in shell/header, card hierarchy, labels/spacing, and overall composition (desktop + mobile).
- QA rerun 2026-03-12 08:58 UTC after DEV increment: shell/header got closer, but desktop still fails materially — the main wallet panel renders compressed/narrow on the left with large empty area on the right, so the approved composition is not matched. Mobile is closer but still denser/tighter than the prototype. Bug ativo: `7d692da9-8646-46e6-99d8-919870b785b3`.
- DEV follow-up 2026-03-12 09:10 UTC: desktop/mobile composition was tightened again to match the approved prototype more closely, focusing on the `Balances` panel/table/card proportions that QA flagged. The desktop table now uses the prototype-like 140px asset column and lighter row density instead of the wider/compressed layout; mobile cards were relaxed to the prototype spacing/token sizes. New DEV evidence: `frontend/qa_artifacts/playwright/improve-wallet-screen/devfix-desktop.png` and `frontend/qa_artifacts/playwright/improve-wallet-screen/devfix-mobile.png`.
- Runtime evidence was reconciled: old prototype-blank bug closed; active runtime bug is `7d692da9-8646-46e6-99d8-919870b785b3` (`QA: /external/balances diverge visualmente do protótipo aprovado`).
- QA rerun 2026-03-12 09:25 UTC: **failed novamente**. Mobile ficou mais próximo, mas o desktop ainda diverge materialmente do protótipo aprovado: o conteúdo principal segue comprimido no canto superior esquerdo, com grande área vazia abaixo/à direita, quebrando a composição esperada. Evidências: `frontend/qa_artifacts/playwright/improve-wallet-screen/rerun-2026-03-12-0925/{proto-desktop,impl-desktop,proto-mobile,impl-mobile}.png`. Runtime/Kanban reconciliado de volta para **DEV** com rejeição do gate DEV.
- DEV follow-up 2026-03-12 09:39 UTC: alinhei o shell/container desktop de `/external/balances` ao sizing do protótipo aprovado (`width: min(1120px, calc(100% - 28px))` no header + conteúdo), reforcei a largura total do app root/layout para evitar o aspecto encolhido à esquerda e adicionei altura mínima no painel desktop para reduzir o vazio abaixo quando houver poucas linhas reais. Build frontend ok (`npm run build`). Arquivos alterados: `frontend/src/index.css`, `frontend/src/components/Layout.tsx`, `frontend/src/components/AppNav.tsx`, `frontend/src/pages/ExternalBalancesPage.tsx`. Próximo passo operacional: **QA rerun desktop/mobile** focando a composição desktop vs `frontend/public/prototypes/improve-wallet-screen/`.
- QA rerun 2026-03-12 09:58 UTC: **failed novamente**. Executei a rerun visual desktop/mobile após o follow-up DEV de 09:39 UTC aguardando a hidratação real da página antes das capturas. O shell/header e a hierarquia geral melhoraram, mobile ficou próximo/aceitável nesta rodada, mas o desktop ainda diverge materialmente do protótipo aprovado: o container principal segue comprimido no canto superior esquerdo, com excesso de área vazia à direita/abaixo. Sem blocker novo; permanece ativo apenas o bug `7d692da9-8646-46e6-99d8-919870b785b3`. Evidências: `frontend/qa_artifacts/playwright/improve-wallet-screen/rerun-2026-03-12-0955/{proto-desktop.png,impl-desktop-loaded.png,proto-mobile.png,impl-mobile-loaded.png}`. Runtime/Kanban mantido em **DEV** com rejeição do gate QA.
- DEV follow-up 2026-03-12 10:10 UTC: corrigi o real motivo do desktop “encolhido” em `/external/balances`: os wrappers do header e do conteúdo estavam com `mx-auto` presente na marcação, mas sem margem automática computada, então o container de 1120px renderizava colado em `x=0` e parecia comprimido no canto superior esquerdo. Troquei esses wrappers para `style={{ width: 'min(1120px, calc(100% - 28px))', marginInline: 'auto' }}` em `frontend/src/components/AppNav.tsx` e `frontend/src/pages/ExternalBalancesPage.tsx`, e aumentei o `Balances` panel desktop para `lg:min-h-[642px]` para espelhar melhor a composição/altura do protótipo. Verificação local: header/content/panel agora centralizados em `x=160` no viewport 1440px e evidências DEV atualizadas em `frontend/qa_artifacts/playwright/improve-wallet-screen/devrerun-{desktop,mobile}.png`. Próximo passo operacional: **QA rerun desktop/mobile** focando fidelidade visual final do desktop.
- DEV validation 2026-03-12 10:40 UTC: runtime/Kanban reconciliado e confirmado de volta em **QA** (`DEV=approved`, `QA=pending`) antes de encerrar o turno. Revalidação local do layout computado em 1440×900 confirmou o fix do blocker desktop: header/content/panel renderizando em `x=160` com largura `1120px` e painel `Balances` com `height=642` em vez do estado anterior colado em `x=0`. Evidência complementar: `frontend/qa_artifacts/playwright/improve-wallet-screen/devturn-desktop-check.png`. Build frontend ok novamente (`npm run build`). Handoff: **QA rerun desktop/mobile** contra o protótipo aprovado.
- QA rerun 2026-03-12 10:56 UTC: **PASS**. Reexecutei a validação visual desktop/mobile de `/external/balances` contra `frontend/public/prototypes/improve-wallet-screen/` aguardando a hidratação completa antes das capturas. O blocker desktop `7d692da9-8646-46e6-99d8-919870b785b3` não reproduz mais: composição/header/content voltaram ao envelope aprovado (desktop com heading em `x=160`, painel `Balances` em `x=161`, sem overflow horizontal) e mobile permaneceu consistente com a hierarquia/layout aprovados. Sem blocker novo; bug runtime `7d692da9-8646-46e6-99d8-919870b785b3` encerrado. Evidências: `frontend/qa_artifacts/playwright/improve-wallet-screen/rerun-2026-03-12-1056/{proto-desktop.png,impl-desktop-loaded.png,proto-mobile.png,impl-mobile-loaded.png,summary.json}`. Runtime/Kanban reconciliado para **Homologation** com `QA=approved`.
- Reconciliation handoff 2026-03-12 11:55 UTC: OpenSpec tracking aligned with runtime/Kanban so the next operational gate is explicitly **Homologation**, not another QA rerun.
- Artifact note: the checklist below is legacy implementation scope, not the current operational blocker list. For execution/handoff, prefer workflow DB + Kanban comments.

## 1. Backend

- [x] 1.1 Add `as_of` (UTC ISO string or unix ms) to `GET /api/external/binance/spot/balances` response.
- [x] 1.2 Add query param `min_usd` (float, optional, default 0.02; clamp to sane range) to control dust filtering.
- [x] 1.3 Update backend tests to cover:
  - default dust behavior preserved
  - `min_usd=0` returns more rows
  - `as_of` present

## 2. Frontend (Wallet page: `/external/balances`)

- [x] 2.1 Add summary strip (Total USD + PnL caveat).
- [x] 2.2 Add search input (asset symbol) + "Locked only" filter.
- [x] 2.3 Add dust control:
  - default: respect backend default (0.02)
  - UI option to set `min_usd` (e.g., presets: 0, 0.02, 1, 10)
- [x] 2.4 Add sorting control (Value, PnL USD, PnL %, Asset). Keep Value desc as default.
- [x] 2.5 Responsive layout:
  - Desktop table
  - Mobile cards (no horizontal scroll)
- [x] 2.6 Improve numeric formatting and column alignment.

## 3. QA / E2E

- [x] 3.1 Update Playwright test for `/external/balances` to assert:
  - page loads
  - search works
  - toggling dust threshold changes visible rows (mocked API)
  - mobile viewport renders cards (or no horizontal scroll)

## 4. Docs / Spec

- [x] 4.1 Update `openspec/specs/external-balances/spec.md` with the new API requirements (`as_of`, `min_usd`) and UI requirements.
- [x] 4.2 Ensure this change has a clear review guide for Alan.
