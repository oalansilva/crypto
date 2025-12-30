# Proposal: Refine Results Layout

## Summary
Restructure the `ResultsPage.tsx` to prioritize high-level comparison and minimize information overload.

## Motivation
Current layout displays all charts and data for all strategies simultaneously, leading to performance issues and cognitive load. Users need to verify parameters and identify the best strategy quickly.

## Proposed Experience
1. **Summary Header**: Displays run context (dates, fees, initial capital).
2. **Comparison Grid**: Main view showing a sortable table/grid of all strategies. Highlights the best performer.
3. **Detail View**: Clicking a strategy opens a focused view with its specific charts and trades.

## Spec Deltas
- `modified-results-page`: Restructure main container.
- `added-run-summary-component`: New component for metadata.
- `added-comparison-grid-component`: New component for strategy ranking.
- `added-strategy-detail-view`: Extract chart/table logic into on-demand view.

## Risks
- **Navigation**: Ensuring back navigation from Detail to Grid is smooth.
- **State**: Persisting "seen" state or scroll position when returning to grid.
