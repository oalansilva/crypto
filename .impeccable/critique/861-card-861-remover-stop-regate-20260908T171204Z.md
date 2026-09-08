# Re-gate — Card 861 remover stop (new bytes, Status Design)

- Card/change: `card-861-remover-stop`
- Prototype URL: https://dev.criptofarol.com.br/prototypes/card-861-remover-stop/
- Prototype file: `frontend/public/prototypes/card-861-remover-stop/index.html`
- Design: `openspec/changes/card-861-remover-stop/design.md`
- Gate: UI impact: affected / live_route: `/monitor` / surface: existing
- Re-gated at (UTC): 2026-09-08T17:12:04Z
- Scope of re-gate: gate-compliance additions only since the A/B PASS — COPIED comment
  markers, signals table with class `table.signals` + texts `7d` and `Par / Estratégia`,
  gate token lines in design.md. Product interactions untouched. This is a re-gate, not a
  new critique round.
- Tooling note: `playwright-cli` / `playwright-cli-headed` binaries are not installed in
  this environment, so the browser pass ran on the equivalent engine (Python Playwright
  1.62 + cached Chromium 1243, `--no-sandbox`, fresh contexts per viewport, real HTTPS
  URL). No repo files outside this snapshot were written; scratch (fetched HTML, check
  script) stayed in `/tmp`.

## Verdict: PASS

The new bytes render and behave per the prior PASS: the `table.signals` landmark with all
eight header texts is present on both viewports; both remove confirmations (chart +
sell-flow) move focus on open and return it to the trigger on close with explicit origin
labels (app-created BTC + exchange-only SOL); remover-nunca-vende holds; post-remove
requires a new preview; nothing is offered without HOLD/stop; 0 console / 0 page errors
on both viewports. No P0/P1. One P3 (clone-inherited, accepted — same as A/B).

## Digests (disk vs HTTPS, new bytes)

- Disk: sha256 `a208a0f544442104930fd17aea71dc722f62c344fd05e6bb716fac39632e4e77`, 63683 bytes
- HTTPS `GET /prototypes/card-861-remover-stop/` → HTTP 200, 63683 bytes,
  sha256 `a208a0f544442104930fd17aea71dc722f62c344fd05e6bb716fac39632e4e77`
- **Digest match disk-vs-HTTPS: IDENTICAL** (`cmp` clean)
- Gate lines verified in `design.md`: `UI impact: affected` (l50), `live_route: /monitor`
  (l51), `surface: existing` (l53)
- Static markers in served bytes: `COPIED:start/end` present (2 hits), `table.signals`
  (`table class="monitor-table signals"`) present, `Par / Estratégia` present

## Viewport table

| Viewport | Landmarks (table.signals + 8 headers) | Chart remove+confirm (focus in/back, origins) | Sell-flow blocked+confirm (focus, never-sells, repreview) | No-offer states | Errors |
|---|---|---|---|---|---|
| Desktop 1280×800 | PASS | PASS | PASS | PASS ETH HOLD-no-stop, ADA EXIT, ETH sell-direct | 0 console / 0 page |
| Mobile 390×844 | PASS | PASS | PASS (blocked→confirm→removed) | n/a (same DOM) | 0 console / 0 page |

## Asserts (37 checks, all PASS)

Method note: `inner_text` returns the *rendered* header text, and `.monitor-table th`
carries `text-transform: uppercase` (l98), so the eight headers read back as
`STATUS / PREÇO / DISTÂNCIA / 7D / RISCO ATÉ STOP / TAGS / PAR / ESTRATÉGIA / OPERAR`;
DOM source keeps the specified casing (`Status … Par / Estratégia`, l318). All eight
match case-insensitively on both viewports.

Desktop (24):
1. PASS `table.signals` present (count=1).
2.–9. PASS headers `Status`, `Preço`, `Distância`, `7d`, `Risco até stop`, `Tags`,
   `Operar`, `Par / Estratégia` (case-insensitive vs rendered uppercase).
10. PASS chart confirm `spot-protect-confirm` visible on open; text identifies
    qty/stop/limit: "Remover a stop 0.085 BTC (stop $99,560.00, limit $99,460.44),
    criada no app (Farol), via Farol? O saldo destrava, mas nada será vendido."
11. PASS app origin label "criada no app (Farol)" in chart confirm text.
12. PASS focus moves into confirmation (`spot-protect-confirm-yes`) on open.
13. PASS Cancelar hides confirmation, focus returns to `spot-protect-remove`.
14. PASS Confirmar remoção → done status "Stop removida via Farol. Saldo destravado — …",
    focus → done status.
15. PASS remover-nunca-vende: trade overlay NOT opened by chart removal.
16. PASS chart SOL exchange-only note `spot-protect-external-note` visible.
17. PASS chart SOL confirm carries "…, criada só na exchange, via Farol? …".
18. PASS chart SOL focus in (`spot-protect-confirm-yes`) / cancel → focus back to trigger.
19. PASS ETH HOLD without stop: `spot-protect-remove` hidden,
    "Sem ordem protetiva. Remover stop não é oferecido (sem stop aberta)."
20. PASS ADA EXIT: protect panel `display:none`.
21. PASS sell blocked state after Continuar:
    "Saldo livre insuficiente: 0.085 BTC travados pela stop aberta (stop $99,560.00,
    criada no app (Farol)). Remova a stop para vender como operação — remover não vende."
22. PASS sell confirm visible with app origin; focus → `spot-sell-stop-confirm-yes`.
23. PASS Voltar hides sell confirmation, focus returns to `spot-sell-stop-remove`,
    still blocked, nothing submitted.
24. PASS Confirmar → `spot-sell-stop-removed` visible ("Stop removida via Farol. Nenhuma
    venda foi enviada. Para vender como operação, gere uma nova prévia — …"); review AND
    result both hidden (post-remove requires new preview; remove never sells); focus →
    `spot-repreview-order`.
25. PASS "Gerar nova prévia" → review visible; submit disabled until ack (gated).
26. PASS sell SOL blocked+confirm both carry "criada só na exchange".
27. PASS ETH sell (no stop): Continuar goes straight to review; blocked block hidden.

Mobile (13): table.signals + all 8 headers PASS; chart confirm + app-origin text +
focus in/back PASS; chart removal → done + focus + no trade overlay PASS; SOL external
note + label + focus round-trip PASS; sell blocked → confirm (focus) → removed with
review hidden PASS.

Errors: 0 console / 0 page on desktop run; 0 console / 0 page on mobile run.

## Findings

### P0 — none
### P1 — none

### P3 (accepted, solved in Apply, never reopened)

- P3-1 Mobile horizontal overflow (same clone-inherited note as assessments A/B): source
  is the CLONE monitor table, not the delta — no `d861-*` / protect / trade element
  exceeds the viewport, and chart + trade dialogs open and operate on mobile. Live
  `/monitor` parity question belongs to Apply; the card delta is responsive. (Not
  re-measured pixel-wise in this re-gate; no delta element changed layout — gate
  additions are comment markers + existing table structure.)

## Scope/contract notes (no new issues)

- Offer rule visible and unchanged: BTC HOLD + stop → remover offered (chart +
  sell-flow); ETH HOLD without stop and EXIT rows explicitly state remover is NOT
  offered — matches "sem Posicionado / sem stop aberta, remover não é oferecido".
- Non-goals intact: no rule-of-stop, withdraw/futures/margin, or buy changes; buy tab
  marked out of scope; no new endpoint (simulated DELETE noted in code comments).
- Prior snapshots untouched:
  `.impeccable/critique/861-card-861-remover-stop-assessment-A-20260908T170632Z.md`,
  `.impeccable/critique/861-card-861-remover-stop-assessment-B-20260908T170407Z.md`.
