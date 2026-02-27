# home-page-refresh

## Status
- PO: blocked (needs Alan confirmation on KPIs)
- DESIGN: done
- Alan approval: approved
- DEV: not started
- QA: not started
- Alan homologation: not reviewed

## Decisions (draft)
- Goal: reformulate the Home page to improve clarity and daily usability.
- IA (proposed):
  - Top: short orientation (what the app is for) + “Where to start” suggestion.
  - Middle: **KPIs (at-a-glance)** row (compact cards).
  - Bottom: **Quick Actions** grid (shortcuts to core areas).
- KPIs to highlight (proposed for v1):
  - Total portfolio balance (base currency)
  - PnL 24h (portfolio)
  - Exposure / positions summary (e.g., # open positions or % allocated)
  - Active strategies (running count)
  - Last update timestamp (data freshness)
- Prototype: DESIGN will deliver a reusable HTML/CSS prototype under `frontend/public/prototypes/home-page-refresh/`.

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/home-page-refresh/proposal
- KPI decision memo (md): `openspec/changes/home-page-refresh/kpi-decision-memo.md`
- PT-BR review: http://72.60.150.140:5173/openspec/changes/home-page-refresh/review-ptbr
- Prototype (when ready): http://72.60.150.140:5173/prototypes/home-page-refresh/index.html

## Notes
- [DESIGN] v0 prototype created (layout skeleton): http://72.60.150.140:5173/prototypes/home-page-refresh/
- Reply to @PO mention: KPI decision memo drafted (see `openspec/changes/home-page-refresh/kpi-decision-memo.md`). Need Alan to confirm which KPIs matter most for “daily check-in”.
- Question for Alan (blocker): Which 3–5 KPIs should Home highlight first?
  - Option A (portfolio health): Total balance, PnL 24h, exposure/positions, active strategies, last update.
  - Option B (trading ops): active strategies, open orders, alerts/errors, PnL 24h, last update.

## Next actions
- [x] PO: Propose IA + KPI shortlist for Home.
- [x] PO: Draft a 1-page decision memo to help Alan pick the 3–5 KPIs (recommended default + rationale + any tradeoffs).
- [ ] Alan: Confirm IA + pick the 3–5 KPIs to highlight on Home (choose A vs B or customize).
- [ ] DESIGN: Iterate prototype after PO/Alan feedback.
- [ ] Alan: Approve scope + prototype.
- [ ] DEV: Implement Home using prototype.
- [ ] QA: Validate.
