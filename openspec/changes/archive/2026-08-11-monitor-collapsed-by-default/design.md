## Context

`MonitorStatusTab` tracks expanded rows in `expandedRows`. Current rendering uses `expandedRows[rowKey] ?? true`, so any row not explicitly toggled starts expanded.

## Decisions

1. Change default expansion to collapsed.

   Use `expandedRows[rowKey] ?? false`, preserving existing toggle behavior and row click behavior.

2. Keep table rows visible.

   Only the `detail-row` containing `OpportunityCard` is hidden by default. The head row remains visible and clickable.

3. Update tests to expand rows before detail assertions.

   Tests that check `monitor-card-*`, portfolio detail toggles, or card-mode controls need to click the row/chevron first.

## Validation

- OpenSpec validation.
- Frontend build.
- Affected Monitor E2E suite.
