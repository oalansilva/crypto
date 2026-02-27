# home-page-refresh

## Status
- PO: done
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
- KPI candidates (for v1):
  - Total portfolio balance (base currency)
  - PnL 24h (portfolio)
  - Exposure / positions summary (e.g., % allocated or # open positions)
  - Active strategies (running count)
  - Last update timestamp (data freshness)
- Prototype: DESIGN will deliver a reusable HTML/CSS prototype under `frontend/public/prototypes/home-page-refresh/`.

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/home-page-refresh/proposal
- KPI decision memo (md): `openspec/changes/home-page-refresh/kpi-decision-memo.md`
- PT-BR review: http://72.60.150.140:5173/openspec/changes/home-page-refresh/review-ptbr
- Prototype (when ready): http://72.60.150.140:5173/prototypes/home-page-refresh/index.html

## Notes
- [DESIGN] v0 prototype created (layout skeleton): http://72.60.150.140:5173/prototypes/home-page-refresh/index.html
- [PO] KPI decision memo updated to be short + answerable (3 quick questions). Awaiting Alan confirmation.

## Next actions
- [x] PO: Propose IA + KPI shortlist for Home.
- [x] PO: Draft/maintain KPI decision memo (recommended default + 1 alternative + 3 quick questions).
- [x] PO: Add an explicit “Pick A or B” + 3 quick choices at the top of the KPI memo (so Alan can answer in 30s).
- [x] Alan: Chose Option A (simple Home) and approved scope/prototype direction.
- [ ] DESIGN: Optional small iteration of prototype based on Option A (if needed).
- [ ] DEV: Implement Home using prototype.
- [ ] QA: Validate.
