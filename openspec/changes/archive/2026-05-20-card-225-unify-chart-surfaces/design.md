## Context

Card #218 improved only the Monitor modal, but Alan clarified that both graph screens must be unified and Favorites should be the base because it carries more complete result data. The prototype in `crypto.3.zip` reinforces a dense operational chart layout with context panels, but the implemented colors and spacing must follow `DESIGN.md`.

## Goals / Non-Goals

**Goals:**
- Share the chart rendering, zoom, wheel handling, candle tooltip data, marker normalization and volume rendering across Favorites and Monitor.
- Preserve Favorites data behavior from `/combo/results`: no extra fetches and no loss of result markers/candles.
- Preserve Monitor-specific behavior: timeframe selector, live candle fetching, signal history markers, fallback current marker, entry/stop price lines and signal context side panel.
- Preserve existing `data-testid` contracts used by Playwright.
- Use `DESIGN.md` tokens: `#0b0e11`, `#1e2329`, `#2b3139`, `#fcd535`, `#f0b90b`, `#0ecb81`, `#f6465d`, `#eaecef`, `#929aa5`, `#707a8a`.

**Non-Goals:**
- Merge Favorites and Monitor routes into one page.
- Change strategy calculations, signal resolution, API contracts or cache format.
- Archive OpenSpec or release to `main`; this card ends in `develop` after technical validation.

## Decisions

- Create `StrategyChartSurface` as the shared rendering component. It owns the `lightweight-charts` setup, zoom controls, wheel zoom, candle/volume data mapping, marker normalization, visible bar count and optional price lines.
- Keep `MonitorAlignedCandlestickChart` as a compatibility wrapper for Favorites so existing imports and test IDs continue working.
- Refactor `ChartModal` to remove duplicated chart setup and pass Monitor-only context into the shared surface through props for toolbar, summary, side content, footer and price lines.
- Keep the prototype influence at the layout level: chart-first surface, compact header metrics, right-side context panel and footer legend. `DESIGN.md` remains the visual authority.

## Risks / Trade-offs

- Shared component props become broader than a single-screen component. This is acceptable because the alternative is maintaining two independent chart engines with duplicated bugs.
- Monitor has more modal-specific content than Favorites. The shared surface therefore supports custom side content instead of forcing Favorites to adopt Monitor-only fields.
- Tests depend on existing selectors. The implementation keeps those selectors stable and adds no route-level contract change.
