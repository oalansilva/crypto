## Context

Wallet is currently a dense table. Backend already:
- hides dust (< $0.02)
- computes USD value
- computes avg cost + PnL only for a limited number of top rows (time/limit guarded)

We want a screen that is **scan-first** and **mobile-friendly**, without expanding backend scope into full accounting.

## Goals / Non-Goals

**Goals**
- Make the page readable at a glance (summary + clear hierarchy).
- Let the user quickly filter and search.
- Keep interactions safe (read-only) and performant.

**Non-Goals**
- Any trading actions.
- Persisting wallet snapshots.
- Accurate realized PnL accounting.

## UX / IA (for DESIGN handoff)

### Page Structure
1. **Header**
   - Title: "Carteira" / "Wallet"
   - Subtitle: "Binance Spot — read-only"
   - `as_of` timestamp (server-provided)
   - Primary action: Refresh

2. **Summary strip (top KPIs)**
   - Total USD value (always)
   - Total locked USD (optional if derivable client-side)
   - Total PnL USD / % (only for rows with pnl; show caveat)

3. **Controls row**
   - Search input (asset symbol)
   - Filters:
     - Toggle: Locked only
     - Toggle: Show dust (or a "Min USD" selector)
   - Sort selector (Value, PnL, Asset)

4. **Content**
   - Desktop: table with sticky header, aligned numeric columns, consistent decimals
   - Mobile: card list (each asset is a card; expandable details)

### Data / Formatting
- Numeric formatting:
  - `value_usd`: 2 decimals
  - `price_usdt`, `avg_cost_usdt`: 4–6 decimals (adaptive)
  - quantities: show up to 8 decimals but trim trailing zeros
- PnL coloring: green for >= 0, red for < 0, neutral for missing

### Empty / Loading / Error states
- Loading: skeleton rows/cards
- Empty: explain "no balances" vs "all hidden by dust filter"
- Error: toast + inline callout (do not leak secrets)

## API Contract Decisions

- Add `as_of` (UTC timestamp) to the response for clarity.
- Add optional `min_usd` query param (default remains 0.02) so UI can change dust threshold safely.
- Keep the existing `lookback_days` behavior for avg cost; surface it in UI as an advanced option later.

## Risks / Trade-offs

- PnL is only computed for top N symbols due to time budget; UI must not imply completeness.
- More client-side sorting/filtering is fine for current data size; if it grows, consider server-side pagination.

## DESIGN Next Step

Use `skills/interface-design-codex/` to produce a concrete UI spec (layout, components, responsive breakpoints) based on the structure above.
