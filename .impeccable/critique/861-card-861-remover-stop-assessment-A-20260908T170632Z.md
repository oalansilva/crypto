# Assessment A — Card 861 remover stop (isolated, same model, no parent transcript)

- Card/change: `card-861-remover-stop`
- Prototype URL: https://dev.criptofarol.com.br/prototypes/card-861-remover-stop/
- Prototype file: `frontend/public/prototypes/card-861-remover-stop/index.html`
- Design: `openspec/changes/card-861-remover-stop/design.md`
- Specs: `openspec/changes/card-861-remover-stop/specs/monitor-spot-stop-limit/spec.md`, `.../specs/monitor-direct-spot-trading/spec.md`
- Tasks: `openspec/changes/card-861-remover-stop/tasks.md`
- Gate: UI impact: affected / live_route: `/monitor` / surface: chart-stop-panel + sell-flow-stop-block (cloned regions)
- Assessed at (UTC): 2026-09-08T17:06:32Z
- Tooling note: `playwright-cli-headed` is not installed in this environment (and the
  `playwright-cli` npm name is a deprecated stub), so the real CLI (`@playwright/cli`
  0.1.19, installed to `/tmp`) drove cached Chromium headed under `xvfb-run` with
  `PLAYWRIGHT_MCP_SANDBOX=false` (same flags as the missing wrapper). Sessions only
  persist inside a single X server, so each pass ran as one wrapped invocation
  (open → resize → run-code → close). No repo files outside this snapshot were written;
  scratch (npm pack, fetched HTML, scripts, screenshots) stayed in `/tmp`.

## Verdict: PASS

HOLD BTC Spot USDT witness behaves per design/specs on both viewports: remove-with-confirmation
works in the chart AND in the sell flow when the sale is blocked by the stop; the two gestures
are separate and confirmed; remove never sells; app-created and exchange-only stops are both
covered with explicit origin labels; nothing is offered without HOLD/stop. 0 console / 0 page
errors everywhere. No P0/P1. Two P3 notes (accepted, Apply-owned).

## Digests (disk vs HTTPS)

- Disk: sha256 `d849df59762c17582ea562b9b2317e0444c80295e7dca5cc827cb9c1f3652a9b`, 62419 bytes
- HTTPS `GET /prototypes/card-861-remover-stop/` → HTTP 200, 62419 bytes,
  sha256 `d849df59762c17582ea562b9b2317e0444c80295e7dca5cc827cb9c1f3652a9b`
- **Digest match disk-vs-HTTPS: IDENTICAL** (`cmp` clean)

## Viewport table

| Viewport | Chart remove+confirm | Sell-flow blocked+confirm | Origin labels | No-offer states | Errors |
|---|---|---|---|---|---|
| Desktop 1280×800 | PASS (open→confirm→cancel→confirm→done) | PASS (blocked→confirm→Voltar→confirm→removed→repreview→review→sold) | PASS app (BTC) + external (SOL), both gestures | PASS ETH HOLD-no-stop, ADA EXIT | 0 console / 0 page |
| Mobile 390×844 | PASS (confirm + app label + focus in/back) | PASS (blocked→confirm→removed) | PASS app (chart+sell); external verified desktop | n/a (same DOM) | 0 console / 0 page |

## Asserts (34 checks, all PASS)

Chart gesture, BTC app-created stop (desktop):
1. PASS `spot-protect-remove` visible with HOLD + open stop.
2. PASS confirm `spot-protect-confirm` visible on open; text identifies qty/stop/limit:
   "Remover a stop 0.085 BTC (stop $99,560.00, limit $99,460.44), criada no app (Farol),
   via Farol? O saldo destrava, mas nada será vendido."
3. PASS focus moves into confirmation (`spot-protect-confirm-yes`).
4. PASS accessible signal: trigger `aria-expanded=true` + `aria-controls=d861-protect-confirm`,
   confirm `role=group` + `aria-label="Confirmar remoção da stop"`.
5. PASS Cancelar hides confirmation, focus returns to `spot-protect-remove`, stop intact
   (summary still "Ativa: qty 0.085 BTC · stop $99,560.00 · limit $99,460.44" — cancel cancels nothing).
6. PASS Confirmar remoção → done status "Stop removida via Farol. Saldo destravado — …",
   focus → done status, trigger gone, trade overlay NOT opened (remove never sells).

Chart gesture, SOL exchange-only stop (desktop):
7. PASS external note `spot-protect-external-note` visible.
8. PASS confirm text carries "…, criada só na exchange, via Farol? O saldo destrava, mas nada será vendido."
9. PASS focus in (`spot-protect-confirm-yes`) / cancel → focus back to trigger.

No-offer states (desktop):
10. PASS ETH HOLD without stop: panel shown, `spot-protect-remove` hidden,
    "Sem ordem protetiva. Remover stop não é oferecido (sem stop aberta)."
11. PASS ADA EXIT: protect panel `display:none`.

Sell-flow gesture, BTC app-created stop (desktop):
12. PASS Continuar with locked balance → `spot-sell-stop-blocked` visible:
    "Saldo livre insuficiente: 0.085 BTC travados pela stop aberta (stop $99,560.00,
    criada no app (Farol)). Remova a stop para vender como operação — remover não vende."
13. PASS own confirmation visible; text "Remover a stop 0.085 BTC (stop $99,560.00,
    limit $99,460.44, criada no app (Farol)) via Farol? Nada será vendido agora.";
    focus → `spot-sell-stop-confirm-yes`.
14. PASS Voltar hides confirmation, focus returns to `spot-sell-stop-remove`, still blocked, nothing submitted.
15. PASS Confirmar → `spot-sell-stop-removed` visible ("Stop removida via Farol. Nenhuma venda
    foi enviada. Para vender como operação, gere uma nova prévia — …"); review AND result
    both hidden at this point (post-remove requires new preview; remove never sells).
16. PASS "Gerar nova prévia" → review visible; submit disabled until ack, enabled after ack;
    "Confirmar venda total" → result "Venda de 100% de BTC executada a mercado. …".

Sell-flow gesture, SOL exchange-only stop (desktop):
17. PASS blocked visible; blocked text + confirm text both carry "criada só na exchange".

Non-stop path (desktop):
18. PASS ETH sell (no stop): Continuar goes straight to review; blocked block hidden (no removal offered).

Mobile 390×844:
19. PASS viewport 390×844; chart confirm visible with full app-origin text; focus in/out correct.
20. PASS sell flow blocked → confirm (focus correct) → removed; all visible and operable.
21. PASS 0 console / 0 page errors on both viewports (desktop run + mobile run + SOL run).

## Findings

### P0 — none
### P1 — none

### P3 (accepted, solved in Apply, never reopened)

- P3-1 Mobile horizontal overflow (doc 793 px at 390 px viewport): source is the CLONE
  monitor table (`table` ≈ 773 px with rows `monitor-row-btc-usdt`, `detail-row`, …), not the
  delta — overflow-element scan lists only clone table parts; no `d861-*` / protect / trade
  element exceeds the viewport, and chart + trade dialogs open and operate on mobile.
  Clone-inherited, Apply-owned (live `/monitor` parity question, not this card's delta).
- P3-2 Chart confirmation bottom edge sits ~7 px below the fold on mobile (top=642/bottom=851
  at 844 px height) inside the scrollable chart modal; confirmation is visible and focus moves
  correctly. Dialog-scroll behavior, implementation detail, Apply-owned.

## Scope/contract notes (no new issues)

- Offer rule matches spec: BTC HOLD + stop → remover in chart + sell flow; ETH HOLD-no-stop and
  ADA EXIT offer nothing.
- Non-goals intact: no stop-rule, withdraw/futures/margin, or buy changes visible; buy tab marked
  out of scope in the prototype; no new endpoint (simulated `DELETE /monitor/spot-stop-order`
  noted in code comments).
