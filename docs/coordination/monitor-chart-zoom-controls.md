# monitor-chart-zoom-controls

## Status
- PO: done
- DESIGN: skipped
- Alan approval: approved
- DEV: done
- QA: done
- Homologation: approved

## Decisions (locked)
- Scope limited to the expanded Monitor strategy chart in `ChartModal`.
- Zoom uses visible logical range mutation instead of refetching candles.
- Main price panel and RSI panel remain synchronized during zoom.
- Added explicit toolbar controls plus wheel zoom fallback for discoverability and usability.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/monitor-chart-zoom-controls/proposal
- Design: http://72.60.150.140:5173/openspec/changes/monitor-chart-zoom-controls/design
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/monitor-chart-zoom-controls/review-ptbr

## Notes
- PO packaged the change artifacts and locked the scope to Monitor chart zoom controls.
- DEV implemented the zoom toolbar, reset action, visible-bar feedback, and mouse wheel zoom support.
- QA validated the change with frontend build, targeted Playwright coverage, and manual monitor verification.

## Next actions
- [x] Alan: approved the change for implementation and archive.
- [x] DEV: implementation completed.
- [x] QA: validation completed.
- [x] Archive: ready to archive with OpenSpec + workflow reconciliation.

## Closed

- Homologated by Alan and archived from the published `feature/zoon` branch because `main` is protected and requires PR checks.
