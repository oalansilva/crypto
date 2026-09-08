# Assessment B — Card 861 remover stop (isolated, same model, no parent transcript)

- Card/change: `card-861-remover-stop`
- Prototype URL: https://dev.criptofarol.com.br/prototypes/card-861-remover-stop/
- Prototype file: `frontend/public/prototypes/card-861-remover-stop/index.html`
- Design: `openspec/changes/card-861-remover-stop/design.md`
- Specs: `openspec/changes/card-861-remover-stop/specs/monitor-spot-stop-limit/spec.md`, `.../specs/monitor-direct-spot-trading/spec.md`
- Tasks: `openspec/changes/card-861-remover-stop/tasks.md`
- Gate: UI impact: affected / live_route: `/monitor` / surface: chart-stop-panel + sell-flow-stop-block (cloned regions)
- Assessed at (UTC): 2026-09-08T17:04:07Z
- Tooling note: `playwright-cli` / `playwright-cli-headed` binaries are not installed in this
  environment, so the browser pass was executed with the equivalent engine (Python Playwright +
  cached Chromium 1243, `--no-sandbox`, fresh contexts). No repo files outside this snapshot
  were written; scratch (fetched HTML, screenshots) stayed in `/tmp`.

## Verdict: PASS

The page is a faithful clone of live `/monitor` with ONLY the card delta, both inline
confirmations behave per spec, origin labels are explicit in both cases, and there are
0 console / 0 page errors on both viewports. No P0/P1. One P3 (clone-inherited, accepted).

## Digests (disk vs HTTPS)

- Disk: sha256 `d849df59762c17582ea562b9b2317e0444c80295e7dca5cc827cb9c1f3652a9b`, 62419 bytes
- HTTPS `GET /prototypes/card-861-remover-stop/` → HTTP 200, 62419 bytes,
  sha256 `d849df59762c17582ea562b9b2317e0444c80295e7dca5cc827cb9c1f3652a9b`
- **Digest match disk-vs-HTTPS: IDENTICAL** (`cmp` clean)

## Viewport table

| Viewport | Clone fidelity | Only delta | Focus open→close ×2 gestures | Origin labels | Errors | Overflow |
|---|---|---|---|---|---|---|
| Desktop 1280×800 | PASS (sidebar, MonitorStatusTab, ChartModal, SpotMarketTradePanel, gate tokens) | PASS | PASS chart + PASS sell-flow | PASS app + external, both gestures | 0 console / 0 page | 0 px |
| Mobile 390×844 | PASS (same markers; `@media ≤900px` collapses shell: sidebar hidden, margins 0, kpis 2-col) | PASS | n/a (smoke: chart + trade open) | n/a (labels verified on desktop; same DOM) | 0 console / 0 page | doc 793 px — source is CLONE table (see P3) |

## Asserts (42 checks: 41 PASS / 1 FAIL triaged to P3)

Desktop (27): sidebar / monitor-status-tab / chart-modal / trade-dialog / protect-panel /
gate-tokens present; gate tokens exact (`UI impact: affected`, `live_route: /monitor`,
`surface: chart-stop-panel + sell-flow-stop-block (cloned regions)`); state-card-grid absent;
BEFORE-AFTER-as-page absent; 861-CLONE + 861-DELTA + 861-LEGEND present; no h-overflow;
chart confirm visible on open; focus → `spot-protect-confirm-yes` on open; app label
"criada no app (Farol)" in chart confirm text; `aria-expanded=true` + `role=group` signal;
cancel hides + focus returns to `spot-protect-remove`; external label "criada só na exchange"
(SOL); sell blocked state shown after Continuar; sell confirm visible + focus →
`spot-sell-stop-confirm-yes`; app label in sell confirm; Voltar hides + focus returns to
`spot-sell-stop-remove`; external label in sell confirm (SOL); after confirm-removal →
`removed` state, NOT auto-review/sale (remover-nunca-vende holds); 0 console / 0 page errors.
Mobile (15): all presence/gate/anti-pattern/marker checks PASS; chart opens; trade opens;
0 console / 0 page errors. Single FAIL: h-overflow 403 px — triaged below as P3.

Verified confirm texts:
- Chart/app: "Remover a stop 0.085 BTC (stop $99,560.00, limit $99,460.44), criada no app (Farol), via Farol? O saldo destrava, mas nada será vendido."
- Chart/external: "Remover a stop 12.4 SOL (stop $68.28, limit $68.21), criada só na exchange, via Farol? …"
- Sell/app: "… (stop $99,560.00, limit $99,460.44, criada no app (Farol)) via Farol? Nada será vendido agora."
- Sell/external: "… criada só na exchange …"

## Findings

### P0 — none
### P1 — none

### P3 (accepted, solved in Apply, never reopened)

- P3-1 Mobile horizontal overflow (~403 px at 390 px): source is the CLONE monitor table
  (`table.monitor-table` ≈ 773 px wide, inside 861-CLONE regions), not the delta — no `d861-*`
  element exceeds 390 px, and the clone shell itself collapses correctly at ≤900 px
  (sidebar hidden, margins 0). Live `/monitor` parity question for the real table belongs to
  Apply; the prototype delta is responsive (chart + trade dialogs open and fit on mobile).
- P3-2 (static-noted, consistent with design.md Apply-details): `data-trade-remove-no` carries
  no `testid`; post-removal state naming (`removed` vs `entry`); danger-button contrast —
  implementation detail, Apply-owned.

## Scope/contract notes (no new issues)

- Offer rule visible in clone: BTC HOLD + stop → remover offered (chart + sell-flow); ETH HOLD
  without stop and EXIT rows (ADA/LINK) explicitly state remover is NOT offered — matches
  "sem Posicionado / sem stop aberta, remover não é oferecido".
- Non-goals intact on the page: no rule-of-stop, withdraw/futures/margin, or buy changes;
  buy tab explicitly marked out of scope; no new endpoint (simulated DELETE noted in code).
