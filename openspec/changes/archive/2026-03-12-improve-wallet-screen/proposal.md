## Why

The current Wallet page (`/external/balances`) works, but it is still **hard to scan quickly** and **not friendly on mobile**. Alan needs to reliably answer:

- What is my total USD exposure right now?
- What are my top positions?
- Which positions are locked?
- Where is the biggest PnL (when available)?

## What Changes

Improve the Wallet screen UX and the supporting API so the page is:

- **Fast to read** (summary + clear formatting)
- **Actionable** (search/filter/sort)
- **Responsive** (mobile-first layout)
- **Transparent** about limitations (dust filtering, PnL availability, lookback window)

## Capabilities

### New Capabilities
- `wallet-screen-improvements`: Better scanning + filtering + mobile UX for external balances.

### Modified Capabilities
- `external-balances`: Add optional query parameters + response metadata needed by the improved UI.

## Scope

In-scope:
- UI: summary header, search, filters, sortable columns, improved formatting, mobile layout.
- API: add safe query params for filtering (e.g., dust threshold) and add `as_of` timestamp.
- QA: update/add E2E coverage for key flows.

Out-of-scope (for this change):
- Multi-account aggregation (multiple exchanges).
- Real portfolio accounting (FIFO/LIFO), deposits/withdrawals ledger.
- Storing snapshots or historical charting.

## Success Criteria

- Alan can find any asset in <5 seconds.
- Mobile view is usable without horizontal scrolling.
- Defaults still hide dust, but the UI clearly states it and allows overriding.
- Page clearly indicates when PnL is missing (avg cost not available or not computed for all rows).
